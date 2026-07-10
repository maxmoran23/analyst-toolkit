"""
Validation harness for the PEP-screening framework.

Runs the deterministic scorer over the full seeded synthetic population, computes
the asymmetric-error metrics (recall on genuine in-scope PEP matches must hold at
1.0; false-positive reduction is the operational value), and writes the evidence
pack under evidence/. Numbers are emitted here, never hand-written, so an
independent reviewer reproduces them by re-running.

Enforces false-negative safety as a BUILD GATE: if the engine ever auto-clears a
genuine in-scope PEP match, or recall falls below the floor, it exits non-zero.

Usage:
    python3 run_validation.py                       # default 50k run, writes evidence/
    python3 run_validation.py --alerts 200000       # scale run
    python3 run_validation.py --trials 6 --no-write # multi-seed stability
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # frameworks/ on path for _lib

from _lib import metrics  # noqa: E402
from _lib.text_normalize import TokenStats  # noqa: E402
import scorer as S  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

FN_RECALL_FLOOR = 1.0  # auto-clear must never lose an in-scope match — METHODOLOGY.md
SWEEP_THRESHOLDS = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
FP_CATEGORIES = ["wrong_party_common_name", "wrong_party_translit", "generic_token",
                 "out_of_scope_former", "common_name_ambiguous"]


def generate(peps_n, alerts_n, seed):
    """Regenerate the exact population the committed CSVs come from: ONE seeded
    RNG draws the PEP list, then continues into the alerts — identical to
    generate_synthetic_data.main(). Returns (entry dict, alerts, TokenStats)."""
    import random
    rng = random.Random(seed)
    pep_rows = G.make_peps(peps_n, rng)
    alerts = G.make_alerts(alerts_n, pep_rows, rng)
    entries = {
        r["pep_id"]: S.PepEntry(
            pep_id=r["pep_id"], name=r["name"], tier=r["tier"],
            position=r["position"], country=r["country"],
            jurisdiction_risk=r["jurisdiction_risk"], status=r["status"],
            years_since_left=float(r["years_since_left"]),
            principal_tier=r["principal_tier"],
            adverse_flag=bool(int(r["adverse_flag"])), dob=r["dob"],
            aliases=[a for a in r["aliases"].split("|") if a])
        for r in pep_rows
    }
    corpus = [e.name for e in entries.values()]
    corpus += [a for e in entries.values() for a in e.aliases]
    return entries, alerts, TokenStats.from_names(corpus)


def score_population(alerts, entries, stats, config):
    records = []
    for a in alerts:
        entry = entries[a["pep_id"]]
        cust = S.Customer(name=a["customer_name"], dob=a["customer_dob"],
                          nationality=a["customer_nationality"])
        d = S.score_alert(cust, entry, stats, config)
        records.append({"label": int(a["label"]), "neg_category": a["neg_category"],
                        "decision": d.decision, "priority": d.priority,
                        "combined": d.combined, "reason": d.reason})
    return records


def operating_point(records):
    """The deployed (named-reason) policy: kept-open = decision != AUTO_CLEAR.
    Positive class = genuine in-scope PEP match. Recall = fraction of true
    matches NOT auto-cleared (the FN-safety metric); specificity = fraction of
    false positives auto-cleared (the FP-reduction metric)."""
    y_true = [r["label"] for r in records]
    y_pred = [0 if r["decision"] == "AUTO_CLEAR" else 1 for r in records]
    conf = metrics.confusion(y_true, y_pred)

    funnel = {"AUTO_CLEAR": 0, "ANALYST_REVIEW": 0, "ESCALATE_ENHANCED_REVIEW": 0}
    priorities = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in records:
        funnel[r["decision"]] += 1
        if r["decision"] == "ANALYST_REVIEW":
            priorities[r["priority"]] += 1

    cats = {}
    for r in records:
        if r["label"] == 1:
            continue
        c = cats.setdefault(r["neg_category"], {"total": 0, "auto_cleared": 0})
        c["total"] += 1
        if r["decision"] == "AUTO_CLEAR":
            c["auto_cleared"] += 1
    for c in cats.values():
        c["clear_rate"] = round(c["auto_cleared"] / c["total"], 4) if c["total"] else 0.0

    leaked = [r for r in records if r["label"] == 1 and r["decision"] == "AUTO_CLEAR"]
    total = len(records)
    reviewed = funnel["ANALYST_REVIEW"] + funnel["ESCALATE_ENHANCED_REVIEW"]
    return {
        "confusion": conf.as_dict(),
        "funnel": funnel,
        "review_priorities": priorities,
        "per_category_clear_rate": cats,
        "fn_count": conf.fn,
        "fn_leaked_examples": [r["reason"] for r in leaked[:5]],
        "volume": {"total_alerts": total, "auto_cleared": funnel["AUTO_CLEAR"],
                   "human_reviewed": reviewed,
                   "human_workload_reduction": round(1 - reviewed / total, 4) if total else 0.0},
    }


def threshold_sweep(records):
    """Compare a NAIVE single-threshold auto-clear policy (clear if combined
    <= T) against the named-reason policy. The low-scoring true matches — the
    formerly senior officials whose materiality has decayed but never reaches
    zero — are exactly the band a bare threshold clears first."""
    n_true = sum(r["label"] for r in records)
    n_fp = len(records) - n_true
    rows = []
    for t in SWEEP_THRESHOLDS:
        fp_cleared = sum(1 for r in records if r["label"] == 0 and r["combined"] <= t)
        fn_leaked = sum(1 for r in records if r["label"] == 1 and r["combined"] <= t)
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


def render_report(op, sweep, manifest, stability=None):
    c = op["confusion"]; v = op["volume"]; f = op["funnel"]
    cats = op["per_category_clear_rate"]
    cat_rows = [{"neg_category": k, "count": cats[k]["total"],
                 "auto_cleared": cats[k]["auto_cleared"], "clear_rate": cats[k]["clear_rate"]}
                for k in FP_CATEGORIES if k in cats]
    cat_tbl = metrics.markdown_table(cat_rows, ["neg_category", "count", "auto_cleared", "clear_rate"])
    sweep_tbl = metrics.markdown_table(sweep, ["threshold", "fp_cleared", "fp_clear_rate",
                                               "fn_leaked", "recall"])
    L = []; A = L.append
    A("# Validation Report — PEP-Screening Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Every figure below is produced by running the "
      "reference scorer over a seeded, fully synthetic population. All officials, "
      "countries, and offices are fictional; no real person is represented. "
      "Numbers are emitted by `run_validation.py`, not authored; re-run it to "
      "reproduce them.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['peps']:,} PEP-list entries · "
      f"{manifest['alerts']:,} alerts · git `{manifest['git_sha']}` · "
      f"{manifest['generated_utc']}")
    A("")
    A(f"**Headline:** recall on genuine in-scope PEP matches **{c['recall']:.4f}** "
      f"(false negatives: **{op['fn_count']}**), false-positive reduction "
      f"**{c['specificity']:.1%}**, human review volume cut by "
      f"**{v['human_workload_reduction']:.1%}** "
      f"({v['total_alerts']:,} alerts → {v['human_reviewed']:,} to a human).")
    A("")
    A("## 1. Methodology summary")
    A("Each alert (a customer an upstream filter matched to a PEP-list entry) is "
      "dispositioned AUTO_CLEAR / ANALYST_REVIEW / ESCALATE_ENHANCED_REVIEW on two "
      "axes — is it the right party (IDF-weighted name matching plus DOB/nationality "
      "corroboration), and does the entry carry material PEP risk (prominence tier "
      "x status decay x jurisdiction bucket). Auto-clears only on a named cause "
      "(wrong_party, generic_token_only, out_of_scope_status); never clears any "
      "current PEP match, any TIER_1/TIER_2 match, or any corroborated match. "
      "Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['alerts']:,} alerts against {manifest['peps']:,} fictional PEP-list "
      "entries (invented officials of invented countries). True in-scope matches are "
      "~4% of volume. Every false positive carries a category; adversarial plants "
      "include transliteration-noisy current TIER_1 matches, common-name true PEPs, "
      "RCAs under different surnames, former officials still inside the step-down "
      "horizon, and adverse-flagged entries past it — the cases designed to defeat "
      "the clearing rules.")
    A("")
    A("## 3. Operating-point results (deployed named-reason policy)")
    A(f"- **Recall (in-scope match retention): {c['recall']:.4f}** — "
      f"**false negatives: {op['fn_count']}**")
    A(f"- False-positive reduction (specificity): {c['specificity']:.4f}")
    A(f"- Precision of the retained queue: {c['precision']:.4f}")
    A(f"- Confusion — TP {c['tp']:,} · FP {c['fp']:,} · TN {c['tn']:,} · FN {c['fn']:,}")
    A("")
    A("| Disposition | Count | Share |")
    A("| --- | --- | --- |")
    for k in ("AUTO_CLEAR", "ANALYST_REVIEW", "ESCALATE_ENHANCED_REVIEW"):
        A(f"| {k} | {f[k]:,} | {f[k]/v['total_alerts']:.1%} |")
    A(f"\nAnalyst-review priority split — HIGH {op['review_priorities']['HIGH']:,} · "
      f"MEDIUM {op['review_priorities']['MEDIUM']:,} · "
      f"LOW {op['review_priorities']['LOW']:,}.")
    A("")
    A("## 4. Per-category false-positive clear rate")
    A("Did the engine clear each false-positive type for the right named reason? "
      "The `common_name_ambiguous` band — a common-name match with no identifier "
      "either way — is deliberately NOT auto-cleared: it cannot be resolved without "
      "more information. The `out_of_scope_former` clear rate is below 1.0 by "
      "design: the minority of those alerts whose nationality corroborates the "
      "entry are routed to a human, because a corroborated identity match on a "
      "list entry is never auto-cleared.")
    A("")
    A(cat_tbl)
    A("")
    A("## 5. Threshold-sensitivity analysis")
    A("A naive policy that auto-cleared on `combined <= T` alone, for comparison. "
      "The first true matches a bare threshold clears are exactly the ones the "
      "step-down design protects: formerly senior officials whose materiality has "
      "decayed to a low — but deliberately non-zero — value. The named-reason "
      "policy holds recall at 1.0 by construction; every clearance it makes "
      "carries an individual, auditable cause.")
    A("")
    A(sweep_tbl)
    A("")
    A("## 6. False-negative safety argument")
    A(f"1. Of {manifest['true_matches']:,} genuine in-scope PEP matches, "
      f"**{op['fn_count']} were auto-cleared** — recall {c['recall']:.4f}.")
    A("2. Safety is structural: a genuine in-scope match cannot exhibit any clearing "
      "cause. Its identifiers corroborate or are absent — never doubly contradict — "
      "so `wrong_party` cannot fire; its distinctive token aligns (transliteration "
      "noise is vowel-only, preserving the phonetic key), and a fully common-named "
      "entry has no unmatched distinctive token, so `generic_token_only` cannot "
      "fire; and it is in scope — current, TIER_1/TIER_2 (no horizon exists), "
      "within the horizon, or adverse-flagged — so `out_of_scope_status` cannot fire.")
    A("3. The sweep (Section 5) shows what the deployed policy refuses to do: a bare "
      "threshold starts leaking decayed-but-in-scope senior matches almost "
      "immediately, because \"low combined score\" and \"safe to clear\" are not "
      "the same claim.")
    A("4. Enforced as a build gate — `run_validation.py` exits non-zero if any "
      "in-scope match is auto-cleared.")
    A("")
    A("## 7. Volume / funnel impact")
    A(f"{v['total_alerts']:,} alerts → {v['auto_cleared']:,} auto-cleared "
      f"({v['auto_cleared']/v['total_alerts']:.1%}) → {v['human_reviewed']:,} to a "
      f"human ({v['human_reviewed']/v['total_alerts']:.1%}), with recall held at "
      "1.0. FP reduction is bounded by the common-name-ambiguous residual and the "
      "corroborated out-of-scope band, both left open by design — the honest "
      "outcome for matches that cannot be proven false.")
    if stability:
        A("")
        A("## 7a. Stability across seeds")
        A(f"{stability['trials']} independent seeds. Recall "
          f"min **{stability['recall_min']:.4f}**, FP-reduction mean "
          f"**{stability['spec_mean']:.4f}** (range {stability['spec_min']:.4f}–"
          f"{stability['spec_max']:.4f}). The result is not an artifact of one seed.")
    A("")
    A("## 8. Limitations")
    A("- Synthetic data models the shape of PEP screening (name collisions, "
      "transliteration, tier/status/jurisdiction structure), not the messiness of "
      "real list vendors' data. Tier assignments, step-down horizons, and "
      "jurisdiction buckets here are ILLUSTRATIVE; a deployment sets them from its "
      "own policy and recalibrates on labelled alerts (`tuning.md`).")
    A("- The engine dispositions screening alerts; the onboarding, enhanced-review, "
      "or exit decision is a documented human action. It never approves or blocks "
      "a relationship.")
    A("- Tier, status, and adverse flags are taken as given from the list; a real "
      "deployment validates the upstream list vendor's accuracy alongside this engine.")
    A("- A transparent reference implementation chosen for auditability, not a "
      "production control.")
    A("")
    A("## 9. Reproduction")
    A("```bash")
    A(f"python3 generate_synthetic_data.py --seed {manifest['seed']} "
      f"--peps {manifest['peps']} --alerts {manifest['alerts']}")
    A(f"python3 run_validation.py --seed {manifest['seed']} "
      f"--peps {manifest['peps']} --alerts {manifest['alerts']}")
    A("```")
    A("Same seed → identical population → identical metrics. Fingerprint in "
      "`evidence/run-manifest.json`.")
    A("")
    return "\n".join(L)


def write_evidence(out_dir, op, sweep, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "metrics.json"), "w") as fh:
        json.dump({"operating_point": op, "manifest": manifest}, fh, indent=2)
    with open(os.path.join(out_dir, "threshold-sweep.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sweep[0].keys()))
        w.writeheader()
        w.writerows(sweep)
    c = op["confusion"]
    with open(os.path.join(out_dir, "confusion-matrix.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["", "predicted_in_scope_match", "predicted_cleared"])
        w.writerow(["actual_in_scope_match", c["tp"], c["fn"]])
        w.writerow(["actual_false_positive", c["fp"], c["tn"]])
    with open(os.path.join(out_dir, "run-manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    with open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w") as fh:
        fh.write(report)


def run_once(peps_n, alerts_n, seed, config):
    entries, alerts, stats = generate(peps_n, alerts_n, seed)
    records = score_population(alerts, entries, stats, config)
    return operating_point(records), threshold_sweep(records), records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--peps", type=int, default=8000)
    ap.add_argument("--alerts", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0,
                    help="re-run across N seeds for stability (no evidence written)")
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = S.Config()
    op, sweep, records = run_once(args.peps, args.alerts, args.seed, config)
    n_true = sum(r["label"] for r in records)
    c = op["confusion"]
    print(f"\n=== PEP screening (seed {args.seed}, {args.alerts:,} alerts) ===")
    print(f"recall {c['recall']:.4f}  FN {op['fn_count']}  "
          f"FP-reduction {c['specificity']:.4f}  "
          f"human-review-cut {op['volume']['human_workload_reduction']:.4f}")
    print("funnel:", op["funnel"])
    print("per-category clear:", {k: v["clear_rate"]
                                  for k, v in op["per_category_clear_rate"].items()})

    stability = None
    if args.trials:
        recalls, specs = [], []
        for t in range(args.trials):
            s = args.seed + 1 + t
            o, _, _ = run_once(args.peps, args.alerts, s, config)
            recalls.append(o["confusion"]["recall"])
            specs.append(o["confusion"]["specificity"])
            print(f"  trial seed {s}: recall {o['confusion']['recall']:.4f} "
                  f"FN {o['fn_count']} FP-red {o['confusion']['specificity']:.4f}")
        stability = {"trials": args.trials, "recall_min": min(recalls),
                     "spec_mean": round(sum(specs) / len(specs), 4),
                     "spec_min": min(specs), "spec_max": max(specs)}
        if min(recalls) < FN_RECALL_FLOOR:
            print(f"\nFN-SAFETY GATE FAILED across trials: recall min "
                  f"{min(recalls):.4f} < {FN_RECALL_FLOOR}")
            return 1

    # ---- FN-safety BUILD GATE ----
    if op["fn_count"] > 0 or c["recall"] < FN_RECALL_FLOOR:
        print(f"\nFN-SAFETY GATE FAILED: recall {c['recall']:.4f} < "
              f"{FN_RECALL_FLOOR} ({op['fn_count']} in-scope matches auto-cleared)")
        for ex in op["fn_leaked_examples"]:
            print("   leaked:", ex)
        return 1

    manifest = {
        "framework": "pep-screening",
        "seed": args.seed, "peps": args.peps, "alerts": args.alerts,
        "true_matches": n_true, "git_sha": _git_sha(),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                         .strftime("%Y-%m-%d %H:%M UTC"),
        "fn_recall_floor": FN_RECALL_FLOOR,
    }
    if not args.no_write and args.trials == 0:
        report = render_report(op, sweep, manifest, stability)
        write_evidence(args.out, op, sweep, manifest, report)
        print(f"\nevidence written -> {args.out}/  (FN-safety gate PASSED)")
    else:
        print("\nFN-safety gate PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
