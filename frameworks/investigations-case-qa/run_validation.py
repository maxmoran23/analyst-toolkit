"""
Validation harness for the investigations case-file QA framework.

Runs the deterministic QA engine over the full seeded synthetic case population,
computes the asymmetric-error metrics (every planted critical deficiency must be
detected and no critical-deficient file may pass QA; the false-flag burden on
clean files is the operational cost), and writes the evidence pack under
evidence/. Numbers are emitted here, not hand-written.

Enforces critical-deficiency safety as a BUILD GATE: if any planted critical
deficiency goes undetected (deficiency recall < 1.0), or any critical-deficient
case receives QA_PASS, it prints the leaked cases and exits non-zero.

Usage:
    python3 run_validation.py
    python3 run_validation.py --cases 200000        # scale
    python3 run_validation.py --trials 6 --no-write # multi-seed stability
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import statistics
import subprocess
import time
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from _lib import attest, metrics  # noqa: E402
import scorer as S  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

_T0 = time.time()   # wall-clock provenance for the evidence manifest

DEFICIENCY_RECALL_FLOOR = 1.0   # every planted critical deficiency detected
CRITICAL_PASS_CEILING = 0       # critical-deficient cases receiving QA_PASS
SWEEP_THRESHOLDS = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
DISPOSITIONS = ["QA_PASS", "REMEDIATE", "REWORK_AND_ESCALATE"]


def generate(cases_n, seed):
    import random
    rng = random.Random(seed)
    return G.make_cases(cases_n, rng)


def _to_case(r):
    return S.CaseFile(
        case_id=r["case_id"], case_type=r["case_type"],
        subject_identified=bool(int(r["subject_identified"])),
        account_scope_documented=bool(int(r["account_scope_documented"])),
        lookback_days=int(r["lookback_days"]),
        scope_elements_total=int(r["scope_elements_total"]),
        scope_elements_reviewed=int(r["scope_elements_reviewed"]),
        evidence_item_count=int(r["evidence_item_count"]),
        evidence_source_types=[t for t in str(r["evidence_source_types"]).split("|") if t],
        corroborated_typology=bool(int(r["corroborated_typology"])),
        disposition=r["disposition"],
        rationale_claim_count=int(r["rationale_claim_count"]),
        rationale_cited_count=int(r["rationale_cited_count"]),
        escalation_trigger_count=int(r["escalation_trigger_count"]),
        escalation_flag=bool(int(r["escalation_flag"])),
        alert_to_open_days=int(r["alert_to_open_days"]),
        open_to_complete_days=int(r["open_to_complete_days"]),
        chronology_present=bool(int(r["chronology_present"])),
        missing_5w=[w for w in str(r["missing_5w"]).split("|") if w],
        empty_narrative_fields=[f for f in str(r["empty_narrative_fields"]).split("|") if f])


def score_population(rows, config):
    records = []
    for r in rows:
        qa = S.review_case(_to_case(r), config)
        records.append({
            "case_id": r["case_id"], "label": int(r["label"]), "category": r["category"],
            "expected_check": r["expected_check"], "disposition": qa.disposition,
            "score": qa.quality_score,
            "fired": {d["check"] for d in qa.deficiencies}, "reason": qa.reason})
    return records


def operating_point(records):
    total = len(records)
    planted = [r for r in records if r["label"] == 1]
    detected = [r for r in planted if r["expected_check"] in r["fired"]]
    missed = [r for r in planted if r["expected_check"] not in r["fired"]]
    critical_passed = [r for r in planted if r["disposition"] == "QA_PASS"]

    # confusion: positive = critical-deficient; predicted positive = REWORK_AND_ESCALATE
    y_true = [r["label"] for r in records]
    y_pred = [1 if r["disposition"] == "REWORK_AND_ESCALATE" else 0 for r in records]
    conf = metrics.confusion(y_true, y_pred)

    funnel = {d: 0 for d in DISPOSITIONS}
    for r in records:
        funnel[r["disposition"]] += 1

    cats = {}
    for r in records:
        c = cats.setdefault(r["category"], {"count": 0, "QA_PASS": 0, "REMEDIATE": 0,
                                            "REWORK_AND_ESCALATE": 0, "scores": []})
        c["count"] += 1
        c[r["disposition"]] += 1
        c["scores"].append(r["score"])
    per_category = {}
    for k, c in cats.items():
        per_category[k] = {
            "count": c["count"], "QA_PASS": c["QA_PASS"], "REMEDIATE": c["REMEDIATE"],
            "REWORK_AND_ESCALATE": c["REWORK_AND_ESCALATE"],
            "mean_score": round(statistics.mean(c["scores"]), 2)}

    clean = per_category.get("clean", {"count": 0, "QA_PASS": 0})
    clean_pass_rate = clean["QA_PASS"] / clean["count"] if clean["count"] else 0.0
    noncrit_reworked = sum(1 for r in records
                           if r["label"] == 0 and r["disposition"] == "REWORK_AND_ESCALATE")
    return {
        "confusion": conf.as_dict(), "funnel": funnel, "per_category": per_category,
        "deficiency_recall": round(len(detected) / len(planted), 4) if planted else 1.0,
        "planted_critical": len(planted), "detected_critical": len(detected),
        "missed_examples": [f"{r['case_id']} [{r['category']}] expected {r['expected_check']}"
                            for r in missed[:5]],
        "critical_passed": len(critical_passed),
        "critical_passed_examples": [f"{r['case_id']} [{r['category']}] score {r['score']:.1f}"
                                     for r in critical_passed[:5]],
        "clean_pass_rate": round(clean_pass_rate, 4),
        "noncritical_sent_to_rework": noncrit_reworked,
        "volume": {"total_cases": total, "qa_pass": funnel["QA_PASS"],
                   "remediate": funnel["REMEDIATE"],
                   "rework_and_escalate": funnel["REWORK_AND_ESCALATE"],
                   "released_share": round(funnel["QA_PASS"] / total, 4) if total else 0.0},
    }


def threshold_sweep(records):
    """A naive policy that granted QA_PASS on `quality_score >= T` alone, for
    comparison against the deployed named-check policy."""
    rows = []
    n_clean_minor = sum(1 for r in records if r["category"] in ("clean", "minor_findings"))
    for t in SWEEP_THRESHOLDS:
        passed = [r for r in records if r["score"] >= t]
        rows.append({
            "threshold": t,
            "naive_pass_count": len(passed),
            "critical_deficient_passed": sum(1 for r in passed if r["label"] == 1),
            "major_deficient_passed": sum(1 for r in passed
                                          if r["category"] == "major_findings"),
            "clean_or_minor_failed": sum(1 for r in records
                                         if r["category"] in ("clean", "minor_findings")
                                         and r["score"] < t),
            "clean_or_minor_failed_rate": round(
                sum(1 for r in records if r["category"] in ("clean", "minor_findings")
                    and r["score"] < t) / n_clean_minor, 4) if n_clean_minor else 0.0,
        })
    return rows


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def render_report(op, sweep, manifest):
    c = op["confusion"]; v = op["volume"]; pc = op["per_category"]
    cat_rows = [{"category": k, "count": pc[k]["count"], "mean_score": pc[k]["mean_score"],
                 "QA_PASS": pc[k]["QA_PASS"], "REMEDIATE": pc[k]["REMEDIATE"],
                 "REWORK_AND_ESCALATE": pc[k]["REWORK_AND_ESCALATE"]}
                for k in G.CATEGORIES if k in pc]
    cat_tbl = metrics.markdown_table(
        cat_rows, ["category", "count", "mean_score", "QA_PASS", "REMEDIATE", "REWORK_AND_ESCALATE"])
    sweep_tbl = metrics.markdown_table(
        sweep, ["threshold", "naive_pass_count", "critical_deficient_passed",
                "major_deficient_passed", "clean_or_minor_failed", "clean_or_minor_failed_rate"])

    L = []; A = L.append
    A("# Validation Report — Investigations Case-File QA Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Every figure is produced by running the reference "
      "QA engine over a seeded, fully synthetic population of investigation case "
      "files. No real case, customer, or institution is represented. Numbers are "
      "emitted by `run_validation.py`, not authored; re-run it to reproduce them.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['cases']:,} case files · "
      f"git `{manifest['git_sha']}` · {manifest['generated_utc']}")
    A("")
    A(f"**Headline:** critical-deficiency recall **{op['deficiency_recall']:.4f}** "
      f"({op['detected_critical']:,} of {op['planted_critical']:,} planted critical "
      f"deficiencies detected), critical-deficient cases passed QA: "
      f"**{op['critical_passed']}**, clean-case pass rate "
      f"**{op['clean_pass_rate']:.1%}** (false-flag burden on clean files: "
      f"{1 - op['clean_pass_rate']:.1%}).")
    A("")
    A("## 1. Methodology summary")
    A("The engine grades each completed investigation case file against 13 named QA "
      "checks across five dimensions (completeness, evidence support, consistency, "
      "timeliness, narrative quality), producing a weighted 0-100 quality score and "
      "a QA disposition: QA_PASS, REMEDIATE, or REWORK_AND_ESCALATE. ANY critical "
      "deficiency — an unsupported disposition, a disposition contradicting the "
      "evidence, a missed escalation trigger, a missing mandatory element, or a "
      "no-finding closure over unreviewed scope — makes QA_PASS structurally "
      "unreachable regardless of score. The engine grades the file and routes it; "
      "it never reopens or re-decides the investigation. Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['cases']:,} completed case files: ~55% clean, ~15% minor-issue, "
      "~12% major-issue, and ~18% adversarial critical plants across five types. "
      "Each plant is an otherwise-pristine, well-scored file hiding exactly one "
      "critical defect (a fully-cited-looking file whose rationale cites no "
      "evidence, a corroborated typology closed as no-finding, escalation-trigger "
      "facts closed as normal, a missing mandatory element, a clearance over "
      "unreviewed scope) — the cases designed to defeat a score-only policy. "
      "Labels and categories are assigned by construction, never by the engine.")
    A("")
    A("## 3. Operating-point results")
    A(f"- **Critical-deficiency recall (planted defects detected): "
      f"{op['deficiency_recall']:.4f}** — missed: "
      f"{op['planted_critical'] - op['detected_critical']}")
    A(f"- **Critical-deficient cases receiving QA_PASS: {op['critical_passed']}** "
      f"(ceiling: {manifest['critical_pass_ceiling']})")
    A(f"- Confusion (positive = critical-deficient, predicted = REWORK_AND_ESCALATE) — "
      f"TP {c['tp']:,} · FP {c['fp']:,} · TN {c['tn']:,} · FN {c['fn']:,} · "
      f"recall {c['recall']:.4f} · precision {c['precision']:.4f}")
    A(f"- Non-critical cases over-escalated to REWORK_AND_ESCALATE: "
      f"{op['noncritical_sent_to_rework']}")
    A("")
    A("| QA disposition | Count | Share |")
    A("| --- | --- | --- |")
    for k in DISPOSITIONS:
        A(f"| {k} | {op['funnel'][k]:,} | {op['funnel'][k] / v['total_cases']:.1%} |")
    A("")
    A("## 4. Per-category outcomes")
    A("Did each construction category land where designed? Clean files should pass; "
      "minor-issue files pass with advisory notes; major-issue files are remediated "
      "(never reworked as critical); every plant type is reworked. Note the plants' "
      "mean scores — they are well-scored files, which is exactly why the no-pass "
      "gate is a named check, not a score threshold.")
    A("")
    A(cat_tbl)
    A("")
    A("## 5. Threshold-sensitivity analysis")
    A("A naive policy that granted QA_PASS on `quality_score >= T` alone, for "
      "comparison. No threshold separates the population: every T at or below the "
      "plants' scores leaks critical-deficient files, and every T above them still "
      "passes major-deficient files or starts failing clean/minor files. The "
      "deployed policy does not pass on score — QA_PASS requires every critical and "
      "major check provably clean — so critical leakage is 0 by construction.")
    A("")
    A(sweep_tbl)
    A("")
    A("## 6. Critical-deficiency safety argument")
    A(attest.bound_sentence(c["tp"], c["fn"], unit="critical deficiencies"))
    A("")
    A(f"1. Of {op['planted_critical']:,} planted critical deficiencies, "
      f"**{op['detected_critical']:,} were detected** by their named check "
      f"(recall {op['deficiency_recall']:.4f}) and **{op['critical_passed']} "
      f"critical-deficient cases received QA_PASS**.")
    A("2. Safety is structural: the QA_PASS branch of the disposition logic is "
      "reachable only when zero critical checks have fired. A case with an "
      "unsupported disposition, a contradiction, a missed escalation trigger, a "
      "missing mandatory element, or a no-finding closure over unreviewed scope "
      "therefore cannot pass QA regardless of its quality score.")
    A("3. Enforced as a build gate — `run_validation.py` exits non-zero if any "
      "planted critical deficiency goes undetected or any critical-deficient case "
      "passes QA.")
    A("")
    A("## 7. Volume / QA-burden impact")
    A(f"{v['total_cases']:,} case files → {v['qa_pass']:,} released with a named "
      f"pass basis ({v['released_share']:.1%}) → {v['remediate']:,} returned for "
      f"targeted remediation → {v['rework_and_escalate']:,} reworked and escalated "
      f"to the investigations supervisor. Clean-file pass rate "
      f"{op['clean_pass_rate']:.1%} — the QA queue's human effort concentrates on "
      f"genuinely deficient files.")
    A("")
    A("## 8. Limitations")
    A("- The case record is structured metadata about the file (presence, counts, "
      "citations, flags, milestones), not the prose itself. The narrative checks "
      "are structural (chronology present, 5W field coverage, no empty mandatory "
      "fields); judging the analytical quality of the written narrative remains a "
      "human QA skill this engine routes to, not one it replaces.")
    A("- The policy tables (SLAs, minimum lookbacks, mandatory elements) are "
      "illustrative. A deployment substitutes its own procedures manual and "
      "recalibrates the dimension weights and deductions against a labelled sample "
      "of its own QA outcomes (`tuning.md`).")
    A("- The engine grades files and routes them; reopening a case, changing its "
      "disposition, or any filing decision is a documented human action.")
    A("- This is a transparent reference implementation, not a production control.")
    A("")
    A("## 9. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} --cases {manifest['cases']}")
    A("```")
    A("Same seed → identical population → identical metrics.")
    A("")
    return "\n".join(L)


def write_evidence(out_dir, op, sweep, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    op_json = dict(op)
    json.dump({"operating_point": op_json, "manifest": manifest},
              open(os.path.join(out_dir, "metrics.json"), "w"), indent=2)
    with open(os.path.join(out_dir, "threshold-sweep.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sweep[0].keys())); w.writeheader(); w.writerows(sweep)
    c = op["confusion"]
    with open(os.path.join(out_dir, "confusion-matrix.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["", "predicted_rework_and_escalate", "predicted_pass_or_remediate"])
        w.writerow(["actual_critical_deficient", c["tp"], c["fn"]])
        w.writerow(["actual_noncritical", c["fp"], c["tn"]])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


def run_once(cases_n, seed, config):
    rows = generate(cases_n, seed)
    records = score_population(rows, config)
    return operating_point(records), threshold_sweep(records), records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cases", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = S.Config()
    op, sweep, records = run_once(args.cases, args.seed, config)
    print(f"\n=== operating point (seed {args.seed}, {args.cases:,} case files) ===")
    print(f"deficiency recall {op['deficiency_recall']:.4f}  "
          f"critical passed QA {op['critical_passed']}  "
          f"clean pass rate {op['clean_pass_rate']:.4f}  "
          f"non-critical over-escalated {op['noncritical_sent_to_rework']}")
    print("funnel:", op["funnel"])
    print("per-category QA_PASS:", {k: v["QA_PASS"] for k, v in sorted(op["per_category"].items())})

    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            o, _, _ = run_once(args.cases, s, config)
            print(f"  trial seed {s}: recall {o['deficiency_recall']:.4f} "
                  f"critical-passed {o['critical_passed']} "
                  f"clean-pass {o['clean_pass_rate']:.4f}")

    if op["deficiency_recall"] < DEFICIENCY_RECALL_FLOOR or \
            op["critical_passed"] > CRITICAL_PASS_CEILING:
        print(f"\nCRITICAL-DEFICIENCY SAFETY GATE FAILED: "
              f"recall {op['deficiency_recall']:.4f} < {DEFICIENCY_RECALL_FLOOR} "
              f"or {op['critical_passed']} critical-deficient case(s) passed QA")
        for ex in op["missed_examples"]:
            print("   undetected:", ex)
        for ex in op["critical_passed_examples"]:
            print("   passed QA:", ex)
        return 1

    manifest = {"framework": "investigations-case-qa", "seed": args.seed,
                "cases": args.cases, "critical_deficient": op["planted_critical"],
                "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "deficiency_recall_floor": DEFICIENCY_RECALL_FLOOR,
                "critical_pass_ceiling": CRITICAL_PASS_CEILING}

    manifest = attest.enrich_manifest(manifest, _T0)
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, op, sweep, manifest, render_report(op, sweep, manifest))
        print(f"\nevidence written -> {args.out}/  (critical-deficiency safety gate PASSED)")
    else:
        print("\ncritical-deficiency safety gate PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
