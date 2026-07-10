"""
Validation harness for the transaction-monitoring framework.

Runs the deterministic scorer over the full seeded synthetic population, computes
the asymmetric-error metrics (recall on genuinely suspicious activity must hold at
1.0; false-positive reduction is the operational value), and writes the evidence
pack under evidence/. Numbers are emitted here, not hand-written.

Enforces false-negative safety as a BUILD GATE: if the engine ever auto-closes a
genuinely suspicious alert, or recall falls below the floor, it exits non-zero.

Usage:
    python3 run_validation.py
    python3 run_validation.py --alerts 200000        # scale
    python3 run_validation.py --trials 5             # multi-seed stability
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
SWEEP_THRESHOLDS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
FP_CATEGORIES = ["within_profile", "below_typology", "documented_context", "ambiguous_residual"]


def generate(customers_n, alerts_n, seed):
    import random
    rng = random.Random(seed)
    cust_rows = G.make_customers(customers_n, rng)
    alert_rows = G.make_alerts(alerts_n, cust_rows, rng)
    profiles = {
        r["customer_id"]: S.CustomerProfile(
            customer_id=r["customer_id"], segment=r["segment"], risk_rating=r["risk_rating"],
            expected_amount=float(r["expected_amount"]), expected_count=float(r["expected_count"]),
            home_country=r["home_country"], business_type=r["business_type"])
        for r in cust_rows
    }
    return profiles, alert_rows


def score_population(alert_rows, profiles, config):
    records = []
    for a in alert_rows:
        prof = profiles[a["customer_id"]]
        alert = S.Alert(
            alert_id=a["alert_id"], customer_id=a["customer_id"], window_days=int(a["window_days"]),
            total_in=float(a["total_in"]), total_out=float(a["total_out"]),
            txn_count=int(a["txn_count"]), near_threshold_count=int(a["near_threshold_count"]),
            distinct_in_cp=int(a["distinct_in_cp"]), distinct_out_cp=int(a["distinct_out_cp"]),
            passthrough_ratio=float(a["passthrough_ratio"]), same_day=bool(int(a["same_day"])),
            high_risk_geo_fraction=float(a["high_risk_geo_fraction"]))
        d = S.score_alert(alert, prof, config)
        records.append({"label": int(a["label"]), "category": a["category"],
                        "decision": d.decision, "priority": d.priority,
                        "score": d.suspicion_score, "reason": d.reason})
    return records


def operating_point(records):
    y_true = [r["label"] for r in records]
    y_pred = [0 if r["decision"] == "AUTO_CLOSE" else 1 for r in records]
    conf = metrics.confusion(y_true, y_pred)

    funnel = {"AUTO_CLOSE": 0, "ANALYST_REVIEW": 0, "ESCALATE": 0}
    priorities = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in records:
        funnel[r["decision"]] += 1
        if r["decision"] == "ANALYST_REVIEW":
            priorities[r["priority"]] += 1

    cats = {}
    for r in records:
        if r["label"] == 1:
            continue
        c = cats.setdefault(r["category"], {"total": 0, "auto_closed": 0})
        c["total"] += 1
        if r["decision"] == "AUTO_CLOSE":
            c["auto_closed"] += 1
    for c in cats.values():
        c["close_rate"] = round(c["auto_closed"] / c["total"], 4) if c["total"] else 0.0

    leaked = [r for r in records if r["label"] == 1 and r["decision"] == "AUTO_CLOSE"]
    total = len(records)
    reviewed = funnel["ANALYST_REVIEW"] + funnel["ESCALATE"]
    return {
        "confusion": conf.as_dict(), "funnel": funnel, "review_priorities": priorities,
        "per_category_close_rate": cats, "fn_count": conf.fn,
        "fn_leaked_examples": [r["reason"] for r in leaked[:5]],
        "volume": {"total_alerts": total, "auto_closed": funnel["AUTO_CLOSE"],
                   "human_reviewed": reviewed,
                   "human_workload_reduction": round(1 - reviewed / total, 4) if total else 0.0},
    }


def threshold_sweep(records):
    n_true = sum(r["label"] for r in records)
    n_fp = len(records) - n_true
    rows = []
    for t in SWEEP_THRESHOLDS:
        fp_cleared = sum(1 for r in records if r["label"] == 0 and r["score"] <= t)
        fn_leaked = sum(1 for r in records if r["label"] == 1 and r["score"] <= t)
        rows.append({"threshold": t, "fp_closed": fp_cleared,
                     "fp_close_rate": round(fp_cleared / n_fp, 4) if n_fp else 0.0,
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
    c = op["confusion"]; v = op["volume"]; f = op["funnel"]; cats = op["per_category_close_rate"]
    cat_rows = [{"category": k, "count": cats[k]["total"], "auto_closed": cats[k]["auto_closed"],
                 "close_rate": cats[k]["close_rate"]} for k in FP_CATEGORIES if k in cats]
    cat_tbl = metrics.markdown_table(cat_rows, ["category", "count", "auto_closed", "close_rate"])
    sweep_tbl = metrics.markdown_table(sweep, ["threshold", "fp_closed", "fp_close_rate", "fn_leaked", "recall"])

    L = []; A = L.append
    A("# Validation Report — Transaction-Monitoring Alert-Scoring Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Every figure is produced by running the reference "
      "scorer over a seeded, fully synthetic population. No real customer or "
      "transaction is represented. Numbers are emitted by `run_validation.py`, not "
      "authored; re-run it to reproduce them.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['customers']:,} customers · "
      f"{manifest['alerts']:,} alerts · git `{manifest['git_sha']}` · {manifest['generated_utc']}")
    A("")
    A(f"**Headline:** recall on suspicious activity **{c['recall']:.4f}** "
      f"(false negatives: **{op['fn_count']}**), false-positive reduction "
      f"**{c['specificity']:.1%}**, human review volume cut by "
      f"**{v['human_workload_reduction']:.1%}** "
      f"({v['total_alerts']:,} alerts → {v['human_reviewed']:,} to a human).")
    A("")
    A("## 1. Methodology summary")
    A("The engine dispositions each TM alert (a customer plus a window of aggregated "
      "transaction features) as AUTO_CLOSE, ANALYST_REVIEW, or ESCALATE. It "
      "auto-closes only on a named benign cause (within-profile, documented-context, "
      "or below-typology-threshold) and only when NO laundering typology has fired; "
      "it never auto-files a SAR. Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['alerts']:,} alerts across {manifest['customers']:,} customers; "
      "~4% genuinely suspicious. Each false positive carries a category; suspicious "
      "alerts come in clear-typology and emerging flavours, both of which fire a "
      "typology rule (so neither can be auto-closed) — the emerging flavour is the "
      "adversarial band that sits at the edge of the escalation threshold.")
    A("")
    A("## 3. Operating-point results")
    A(f"- **Recall (suspicious retained): {c['recall']:.4f}** — "
      f"**false negatives: {op['fn_count']}**")
    A(f"- False-positive reduction (specificity): {c['specificity']:.4f}")
    A(f"- Precision of the retained queue: {c['precision']:.4f}")
    A(f"- Confusion — TP {c['tp']:,} · FP {c['fp']:,} · TN {c['tn']:,} · FN {c['fn']:,}")
    A("")
    A("| Disposition | Count | Share |")
    A("| --- | --- | --- |")
    for k in ("AUTO_CLOSE", "ANALYST_REVIEW", "ESCALATE"):
        A(f"| {k} | {f[k]:,} | {f[k]/v['total_alerts']:.1%} |")
    A(f"\nAnalyst-review priority — HIGH {op['review_priorities']['HIGH']:,} · "
      f"MEDIUM {op['review_priorities']['MEDIUM']:,} · LOW {op['review_priorities']['LOW']:,}.")
    A("")
    A("## 4. Per-category false-positive close rate")
    A("Did the engine close each false-positive type for the right named reason? The "
      "`ambiguous_residual` band — unexplained deviation with no typology — is "
      "deliberately NOT auto-closed; it is the irreducible queue a human must work.")
    A("")
    A(cat_tbl)
    A("")
    A("## 5. Threshold-sensitivity analysis")
    A("A naive policy that auto-closed on `suspicion_score <= T` alone, for "
      "comparison. The deployed policy does not close on score — it closes only on a "
      "named benign cause and never when a typology has fired — so recall stays at "
      "1.0 by construction while a bare threshold leaks suspicious activity as it "
      "rises.")
    A("")
    A(sweep_tbl)
    A("")
    A("## 6. False-negative safety argument")
    A(attest.bound_sentence(c["tp"], c["fn"], unit="truly suspicious alerts"))
    A("")
    A(f"1. Of {manifest['suspicious']:,} planted suspicious alerts, "
      f"**{op['fn_count']} were auto-closed** — recall {c['recall']:.4f}.")
    A("2. Safety is structural: a genuinely suspicious alert fires a typology rule "
      "(structuring / funnel / pass-through), and the auto-close branches are reached "
      "only when NO typology has fired. A suspicious case therefore cannot be "
      "auto-closed regardless of its score.")
    A("3. Enforced as a build gate — `run_validation.py` exits non-zero if any "
      "suspicious alert is auto-closed.")
    A("")
    A("## 7. Volume / funnel impact")
    A(f"{v['total_alerts']:,} alerts → {v['auto_closed']:,} auto-closed "
      f"({v['auto_closed']/v['total_alerts']:.1%}) → {v['human_reviewed']:,} to a "
      f"human ({v['human_reviewed']/v['total_alerts']:.1%}), with recall held at 1.0.")
    A("")
    A("## 8. Limitations")
    A("- Synthetic data models the shape of monitoring alerts (structuring, funnel, "
      "pass-through, velocity, geography) against a customer baseline, not the full "
      "richness of real transaction histories. Calibrate against a labelled sample of "
      "your own alerts before reliance (`tuning.md`).")
    A("- The engine scores and routes; it does not file SARs or close alerts of "
      "record. A typology hit is a human investigation decision.")
    A("- This is a transparent reference implementation, not a production control.")
    A("")
    A("## 9. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} "
      f"--customers {manifest['customers']} --alerts {manifest['alerts']}")
    A("```")
    A("Same seed → identical population → identical metrics.")
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
        w.writerow(["", "predicted_suspicious", "predicted_closed"])
        w.writerow(["actual_suspicious", c["tp"], c["fn"]])
        w.writerow(["actual_benign", c["fp"], c["tn"]])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


def run_once(customers_n, alerts_n, seed, config):
    profiles, alert_rows = generate(customers_n, alerts_n, seed)
    records = score_population(alert_rows, profiles, config)
    return operating_point(records), threshold_sweep(records), records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=5000)
    ap.add_argument("--alerts", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = S.Config()
    op, sweep, records = run_once(args.customers, args.alerts, args.seed, config)
    n_sus = sum(r["label"] for r in records)
    c = op["confusion"]
    print(f"\n=== operating point (seed {args.seed}, {args.alerts:,} alerts) ===")
    print(f"recall {c['recall']:.4f}  FN {op['fn_count']}  FP-reduction {c['specificity']:.4f}  "
          f"review-cut {op['volume']['human_workload_reduction']:.4f}")
    print("funnel:", op["funnel"])
    print("per-category close:", {k: v["close_rate"] for k, v in op["per_category_close_rate"].items()})

    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            o, _, _ = run_once(args.customers, args.alerts, s, config)
            print(f"  trial seed {s}: recall {o['confusion']['recall']:.4f} FN {o['fn_count']} "
                  f"FP-red {o['confusion']['specificity']:.4f}")

    if op["fn_count"] > 0 or c["recall"] < FN_RECALL_FLOOR:
        print(f"\nFN-SAFETY GATE FAILED: recall {c['recall']:.4f} < {FN_RECALL_FLOOR} "
              f"({op['fn_count']} suspicious alerts auto-closed)")
        for ex in op["fn_leaked_examples"]:
            print("   leaked:", ex)
        return 1

    manifest = {"framework": "transaction-monitoring", "seed": args.seed,
                "customers": args.customers, "alerts": args.alerts, "suspicious": n_sus,
                "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "fn_recall_floor": FN_RECALL_FLOOR}

    manifest = attest.enrich_manifest(manifest, _T0)
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, op, sweep, manifest, render_report(op, sweep, manifest))
        print(f"\nevidence written -> {args.out}/  (FN-safety gate PASSED)")
    else:
        print("\nFN-safety gate PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
