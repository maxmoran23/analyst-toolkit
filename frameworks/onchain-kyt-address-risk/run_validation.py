"""
Validation harness for the on-chain KYT address-risk framework.

Runs the deterministic scorer over the full seeded synthetic population (whose
exposure features are derived by the real `_lib/graph` taint propagation), computes
the asymmetric-error metrics, and writes the evidence pack. Numbers are emitted
here, not hand-written.

Enforces false-negative safety as a BUILD GATE: if the engine ever auto-clears a
genuinely high-risk address, or recall falls below the floor, it exits non-zero.

Usage:
    python3 run_validation.py
    python3 run_validation.py --addresses 200000
    python3 run_validation.py --trials 5
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import subprocess
import time
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from _lib import attest, metrics  # noqa: E402
import scorer as S  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

_T0 = time.time()   # wall-clock provenance for the evidence manifest

FN_RECALL_FLOOR = 1.0
SWEEP_THRESHOLDS = [0.0, 0.02, 0.04, 0.06, 0.10, 0.15, 0.20, 0.30, 0.40, 0.60]
FP_CATEGORIES = ["benign_category", "broken_intermediary", "de_minimis",
                 "diluted_distant", "ambiguous_residual"]


def _hops(v):
    return None if v in ("", None) else int(v)


def generate(n, seed):
    import random
    return G.make_addresses(n, random.Random(seed))


def score_population(rows, config):
    records = []
    for r in rows:
        a = S.AddressAlert(address=r["address_id"], top_category=r["top_category"],
                           exposure=float(r["exposure"]), hops=_hops(r["hops"]),
                           amount_fraction=float(r["amount_fraction"]),
                           via_breaker=bool(int(r["via_breaker"])), direction=r["direction"])
        d = S.score_address(a, config)
        records.append({"label": int(r["label"]), "fp_category": r["fp_category"],
                        "decision": d.decision, "priority": d.priority,
                        "risk": d.risk, "reason": d.reason})
    return records


def operating_point(records):
    y_true = [r["label"] for r in records]
    y_pred = [0 if r["decision"] == "AUTO_CLEAR" else 1 for r in records]
    conf = metrics.confusion(y_true, y_pred)
    funnel = {"AUTO_CLEAR": 0, "ANALYST_REVIEW": 0, "ESCALATE": 0}
    priorities = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in records:
        funnel[r["decision"]] += 1
        if r["decision"] == "ANALYST_REVIEW":
            priorities[r["priority"]] += 1
    cats = {}
    for r in records:
        if r["label"] == 1:
            continue
        c = cats.setdefault(r["fp_category"], {"total": 0, "auto_cleared": 0})
        c["total"] += 1
        if r["decision"] == "AUTO_CLEAR":
            c["auto_cleared"] += 1
    for c in cats.values():
        c["clear_rate"] = round(c["auto_cleared"] / c["total"], 4) if c["total"] else 0.0
    leaked = [r for r in records if r["label"] == 1 and r["decision"] == "AUTO_CLEAR"]
    total = len(records)
    reviewed = funnel["ANALYST_REVIEW"] + funnel["ESCALATE"]
    return {"confusion": conf.as_dict(), "funnel": funnel, "review_priorities": priorities,
            "per_category_clear_rate": cats, "fn_count": conf.fn,
            "fn_leaked_examples": [r["reason"] for r in leaked[:5]],
            "volume": {"total_addresses": total, "auto_cleared": funnel["AUTO_CLEAR"],
                       "human_reviewed": reviewed,
                       "human_workload_reduction": round(1 - reviewed / total, 4) if total else 0.0}}


def threshold_sweep(records):
    n_true = sum(r["label"] for r in records)
    n_fp = len(records) - n_true
    rows = []
    for t in SWEEP_THRESHOLDS:
        fp_cleared = sum(1 for r in records if r["label"] == 0 and r["risk"] <= t)
        fn_leaked = sum(1 for r in records if r["label"] == 1 and r["risk"] <= t)
        rows.append({"threshold": t, "fp_cleared": fp_cleared,
                     "fp_clear_rate": round(fp_cleared / n_fp, 4) if n_fp else 0.0,
                     "fn_leaked": fn_leaked,
                     "recall": round(1 - fn_leaked / n_true, 4) if n_true else 1.0})
    return rows


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def render_report(op, sweep, manifest):
    c = op["confusion"]; v = op["volume"]; f = op["funnel"]; cats = op["per_category_clear_rate"]
    cat_rows = [{"fp_category": k, "count": cats[k]["total"], "auto_cleared": cats[k]["auto_cleared"],
                 "clear_rate": cats[k]["clear_rate"]} for k in FP_CATEGORIES if k in cats]
    cat_tbl = metrics.markdown_table(cat_rows, ["fp_category", "count", "auto_cleared", "clear_rate"])
    sweep_tbl = metrics.markdown_table(sweep, ["threshold", "fp_cleared", "fp_clear_rate", "fn_leaked", "recall"])
    L = []; A = L.append
    A("# Validation Report — On-Chain KYT Address-Risk Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the reference "
      "scorer over a seeded, fully synthetic population whose exposure features are "
      "derived by the real `_lib/graph` taint propagation. No real address is "
      "represented. Numbers are emitted by `run_validation.py`, not authored.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['addresses']:,} addresses · "
      f"git `{manifest['git_sha']}` · {manifest['generated_utc']}")
    A("")
    A(f"**Headline:** recall on high-risk addresses **{c['recall']:.4f}** "
      f"(false negatives: **{op['fn_count']}**), false-positive reduction "
      f"**{c['specificity']:.1%}**, human review volume cut by "
      f"**{v['human_workload_reduction']:.1%}** "
      f"({v['total_addresses']:,} addresses → {v['human_reviewed']:,} to a human).")
    A("")
    A("## 1. Methodology summary")
    A("Each flagged address is dispositioned AUTO_CLEAR / ANALYST_REVIEW / ESCALATE "
      "from its strongest tainted-path exposure to an illicit entity (severity, hop "
      "distance with decay, traceable value share, and whether a commingling "
      "intermediary breaks the trail). Auto-clears only on a named cause; never "
      "auto-clears material, proximate, unbroken exposure to a serious category. "
      "Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['addresses']:,} addresses; ~6% genuinely high-risk. Each address's "
      "exposure features are computed by `_lib/graph` over a constructed subgraph "
      "(seed, optional commingling breaker, intermediates). False positives span "
      "benign-category, broken-intermediary, de-minimis, diluted-distant, and a "
      "mid-severity ambiguous residual that is left open by design.")
    A("")
    A("## 3. Operating-point results")
    A(f"- **Recall (high-risk retained): {c['recall']:.4f}** — "
      f"**false negatives: {op['fn_count']}**")
    A(f"- False-positive reduction (specificity): {c['specificity']:.4f}")
    A(f"- Precision of the retained queue: {c['precision']:.4f}")
    A(f"- Confusion — TP {c['tp']:,} · FP {c['fp']:,} · TN {c['tn']:,} · FN {c['fn']:,}")
    A("")
    A("| Disposition | Count | Share |")
    A("| --- | --- | --- |")
    for k in ("AUTO_CLEAR", "ANALYST_REVIEW", "ESCALATE"):
        A(f"| {k} | {f[k]:,} | {f[k]/v['total_addresses']:.1%} |")
    A(f"\nAnalyst-review priority — HIGH {op['review_priorities']['HIGH']:,} · "
      f"MEDIUM {op['review_priorities']['MEDIUM']:,} · LOW {op['review_priorities']['LOW']:,}.")
    A("")
    A("## 4. Per-category false-positive clear rate")
    A("The `ambiguous_residual` band (mid-severity, moderate exposure) is deliberately "
      "NOT auto-cleared — it goes to a human. The other categories clear on a named, "
      "provable cause.")
    A("")
    A(cat_tbl)
    A("")
    A("## 5. Threshold-sensitivity analysis")
    A("A naive policy auto-clearing on the risk score `<= T`, for comparison. The "
      "deployed policy clears only on a named cause, holding recall at 1.0 while a "
      "bare threshold leaks high-risk addresses as it rises.")
    A("")
    A(sweep_tbl)
    A("")
    A("## 6. False-negative safety argument")
    A(attest.bound_sentence(c["tp"], c["fn"], unit="truly tainted addresses"))
    A("")
    A(f"1. Of {manifest['true_risk']:,} genuinely high-risk addresses, "
      f"**{op['fn_count']} were auto-cleared** — recall {c['recall']:.4f}.")
    A("2. Safety is structural: material, proximate, unbroken exposure to a serious "
      "category cannot satisfy any clear cause — it is not benign, not broken by an "
      "intermediary, not de-minimis, and not diluted/distant.")
    A("3. Enforced as a build gate — `run_validation.py` exits non-zero if any "
      "high-risk address is auto-cleared.")
    A("")
    A("## 7. Volume / funnel impact")
    A(f"{v['total_addresses']:,} addresses → {v['auto_cleared']:,} auto-cleared "
      f"({v['auto_cleared']/v['total_addresses']:.1%}) → {v['human_reviewed']:,} to a "
      f"human ({v['human_reviewed']/v['total_addresses']:.1%}), recall held at 1.0.")
    A("")
    A("## 8. Limitations")
    A("- Synthetic subgraphs model the exposure shape (severity, hops, decay, "
      "commingling breaks, value share), not the full complexity of a real chain "
      "graph or the attribution quality of a real analytics vendor. In production "
      "the exposure features come from that vendor, whose attribution accuracy must "
      "be validated alongside this engine. Calibrate against labelled cases (`tuning.md`).")
    A("- The engine dispositions; the freeze / SAR / off-boarding decision is a "
      "documented human action.")
    A("- A transparent reference implementation, not a production control.")
    A("")
    A("## 9. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} --addresses {manifest['addresses']}")
    A("```")
    A("")
    return "\n".join(L)


def write_evidence(out_dir, op, sweep, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    json.dump({"operating_point": op, "manifest": manifest},
              open(os.path.join(out_dir, "metrics.json"), "w"), indent=2)
    with open(os.path.join(out_dir, "threshold-sweep.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sweep[0].keys())); w.writeheader(); w.writerows(sweep)
    c = op["confusion"]
    with open(os.path.join(out_dir, "confusion-matrix.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["", "predicted_high_risk", "predicted_cleared"])
        w.writerow(["actual_high_risk", c["tp"], c["fn"]])
        w.writerow(["actual_low_risk", c["fp"], c["tn"]])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


def run_once(n, seed, config):
    rows = generate(n, seed)
    records = score_population(rows, config)
    return operating_point(records), threshold_sweep(records), records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--addresses", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = S.Config()
    op, sweep, records = run_once(args.addresses, args.seed, config)
    n_true = sum(r["label"] for r in records)
    c = op["confusion"]
    print(f"\n=== on-chain KYT (seed {args.seed}, {args.addresses:,} addresses) ===")
    print(f"recall {c['recall']:.4f}  FN {op['fn_count']}  FP-reduction {c['specificity']:.4f}  "
          f"review-cut {op['volume']['human_workload_reduction']:.4f}")
    print("funnel:", op["funnel"])
    print("per-category clear:", {k: v["clear_rate"] for k, v in op["per_category_clear_rate"].items()})

    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            o, _, _ = run_once(args.addresses, s, config)
            print(f"  trial seed {s}: recall {o['confusion']['recall']:.4f} FN {o['fn_count']} "
                  f"FP-red {o['confusion']['specificity']:.4f}")

    if op["fn_count"] > 0 or c["recall"] < FN_RECALL_FLOOR:
        print(f"\nFN-SAFETY GATE FAILED: recall {c['recall']:.4f} < {FN_RECALL_FLOOR} "
              f"({op['fn_count']} high-risk addresses auto-cleared)")
        for ex in op["fn_leaked_examples"]:
            print("   leaked:", ex)
        return 1

    manifest = {"framework": "onchain-kyt-address-risk", "seed": args.seed,
                "addresses": args.addresses, "true_risk": n_true, "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

    manifest = attest.enrich_manifest(manifest, _T0)
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, op, sweep, manifest, render_report(op, sweep, manifest))
        print(f"\nevidence written -> {args.out}/  (FN-safety gate PASSED)")
    else:
        print("\nFN-safety gate PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
