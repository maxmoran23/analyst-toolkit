"""
Validation harness for the data-quality rules framework.

Runs the deterministic engine over the full seeded synthetic extract plus a
grid of feed-disposition scenarios, computes the asymmetric-error metrics
(recall on planted critical defects must hold at 1.0; the false-flag rate on
clean records is the operational cost), and writes the evidence pack under
evidence/. Numbers are emitted here, not hand-written.

Enforces safety as a BUILD GATE — exits non-zero if:
  1. any planted critical defect is NOT detected at critical severity
     (recall < 1.0 — the leaked records are printed), or
  2. any feed whose planted screening-critical defect rate breaches its
     documented ceiling receives FEED_PASS, or
  3. the disposition scenario grid deviates from its expected outcomes
     (including that a fully conformant feed DOES pass — the engine must not
     be trivially blocking everything).

Usage:
    python3 run_validation.py
    python3 run_validation.py --records 200000       # scale
    python3 run_validation.py --trials 6 --no-write  # multi-seed stability
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import random
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from _lib import metrics           # noqa: E402
import scorer as S                 # noqa: E402
import generate_synthetic_data as G  # noqa: E402

CRIT_RECALL_FLOOR = 1.0
SWEEP_THRESHOLDS = [0.70, 0.75, 0.80, 0.85, 0.88, 0.90, 0.92, 0.95, 0.98]
# planted critical class -> the screening-critical CDE it degrades
CLASS_CDE = {
    "null_name_active": "full_name",
    "missing_dob": "dob", "malformed_dob": "dob",
    "impossible_dob_sequence": "dob",
    "country_drift": "country",
    "invalid_id_checksum": "national_id",
    "exact_dup": "record_uniqueness", "near_dup_shared_id": "record_uniqueness",
}
# scenario feed -> expected disposition (deterministic: class counts are
# planted exactly, so the expected outcome is stable across seeds)
SCENARIOS = [
    ("clean", "FEED_PASS"),
    ("minor_degraded", "INVESTIGATE"),
    ("warn_band", "INVESTIGATE"),
    ("critical_breach", "BLOCK_FEED_TO_SCREENING"),
    ("dup_contaminated", "BLOCK_FEED_TO_SCREENING"),
]
MINOR_CLASSES = ("null_name_inactive", "missing_supporting",
                 "prefix_country_mismatch", "entity_dob_conflict",
                 "stale_refresh")


def to_records(rows):
    return [S.Record(record_id=r["record_id"], customer_id=r["customer_id"],
                     full_name=r["full_name"], entity_type=r["entity_type"],
                     dob=r["dob"], country=r["country"],
                     national_id=r["national_id"],
                     account_prefix=r["account_prefix"],
                     onboarding_date=r["onboarding_date"], status=r["status"],
                     last_refresh=r["last_refresh"]) for r in rows]


def planted_critical_rates(rows):
    """Ground-truth screening-critical defect rate per CDE, from the labels."""
    n = len(rows)
    counts = Counter(CLASS_CDE[r["category"]] for r in rows
                     if r["category"] in CLASS_CDE)
    return {cde: counts.get(cde, 0) / n for cde in S.SCREENING_CRITICAL}


def gate_no_breach_pass(rows, fa, config, feed_name):
    """Gate 2: a feed whose PLANTED screening-critical rate breaches its
    ceiling must never be FEED_PASS. Returns a failure string or None."""
    for cde, rate in planted_critical_rates(rows).items():
        ceiling = config.dup_ceiling if cde == "record_uniqueness" else config.crit_ceiling
        if rate > ceiling and fa.disposition == "FEED_PASS":
            return (f"feed '{feed_name}': planted {cde} rate {rate:.4f} breaches "
                    f"ceiling {ceiling:.4f} but disposition is FEED_PASS")
    return None


def assess_main(rows, config):
    recs = to_records(rows)
    fa = S.assess_feed(recs, config, feed_id="MAIN")
    by_rid = {}
    for d in fa.defects:
        by_rid.setdefault(d["record_id"], []).append(d)

    per_class = {}
    leaked = []
    y_true, y_pred = [], []
    clean_total = clean_flagged = 0
    for r in rows:
        ds = by_rid.get(r["record_id"], [])
        crit_hit = any(d["severity"] == S.CRITICAL for d in ds)
        any_hit = bool(ds)
        cat = r["category"]
        y_true.append(r["label"])
        y_pred.append(1 if crit_hit else 0)
        if cat in ("clean", "clean_edge"):
            clean_total += 1
            if any_hit:
                clean_flagged += 1
        c = per_class.setdefault(cat, {"planted": 0, "detected": 0,
                                       "rules": Counter()})
        c["planted"] += 1
        detected = crit_hit if cat in G.CRITICAL_CLASSES else any_hit
        if detected:
            c["detected"] += 1
            for d in ds:
                c["rules"][d["rule"]] += 1
        if r["label"] == 1 and not crit_hit:
            leaked.append({"record_id": r["record_id"], "category": cat,
                           "full_name": r["full_name"], "dob": r["dob"],
                           "country": r["country"],
                           "national_id": r["national_id"]})

    for cat, c in per_class.items():
        c["detection_rate"] = round(c["detected"] / c["planted"], 4) if c["planted"] else 0.0
        c["detected_by"] = ", ".join(k for k, _ in c["rules"].most_common(2))
        del c["rules"]

    conf = metrics.confusion(y_true, y_pred)
    n = len(rows)
    defective = len(by_rid)
    critical_records = sum(1 for p in y_pred if p)
    volume = {
        "total_records": n,
        "clean_passthrough": n - defective,
        "records_with_defects": defective,
        "critical_records": critical_records,
        "minor_only_records": defective - critical_records,
        "remediation_share": round(defective / n, 4) if n else 0.0,
    }
    op = {
        "confusion": conf.as_dict(),
        "critical_planted": sum(y_true),
        "critical_detected": conf.tp,
        "critical_missed": len(leaked),
        "false_flag_rate_clean": round(clean_flagged / clean_total, 6) if clean_total else 0.0,
        "clean_records": clean_total,
        "clean_flagged": clean_flagged,
        "per_class_detection": per_class,
        "per_cde": fa.per_cde,
        "per_dimension": fa.per_dimension,
        "composite_score": round(fa.composite_score, 4),
        "feed": fa.as_row(),
        "volume": volume,
    }
    return op, fa, recs, leaked


def threshold_sweep(recs, rows, config):
    """Sensitivity of NAME-SIMILARITY-ONLY near-duplicate detection (phonetic
    and single-edit fallbacks disabled) to the Jaro-Winkler threshold — the
    naive-alternative comparison. The deployed detector keeps the fallbacks,
    which is what holds transliterated pairs at recall 1.0 (gate 1)."""
    near_ids = [r["record_id"] for r in rows if r["category"] == "near_dup_shared_id"]
    exact_ids = [r["record_id"] for r in rows if r["category"] == "exact_dup"]
    non_dup = {r["record_id"] for r in rows if r["category"] not in G.DUP_CLASSES}
    out = []
    for t in SWEEP_THRESHOLDS:
        flags = S.find_duplicates(recs, config, sim=t, use_fallback=False)
        near_det = sum(1 for rid in near_ids if rid in flags)
        exact_det = sum(1 for rid in exact_ids if rid in flags)
        false_pairs = sum(1 for rid in flags if rid in non_dup)
        out.append({
            "threshold": t,
            "near_dup_detected": near_det,
            "near_dup_recall": round(near_det / len(near_ids), 4) if near_ids else 1.0,
            "exact_dup_recall": round(exact_det / len(exact_ids), 4) if exact_ids else 1.0,
            "false_pair_records": false_pairs,
        })
    return out


def run_scenarios(seed, scn_n, config):
    grid, failures = [], []
    for i, (name, expected) in enumerate(SCENARIOS):
        rows = G.make_records(scn_n, random.Random(seed * 1000 + i + 1),
                              G.PROFILES[name])
        fa = S.assess_feed(to_records(rows), config, feed_id=name.upper())
        breach_fail = gate_no_breach_pass(rows, fa, config, name)
        if breach_fail:
            failures.append(breach_fail)
        if fa.disposition != expected:
            failures.append(f"scenario '{name}': expected {expected}, "
                            f"got {fa.disposition}")
        grid.append({"feed": name, "records": len(rows),
                     "expected": expected, "disposition": fa.disposition,
                     "composite": round(fa.composite_score, 4),
                     "outcome": "OK" if fa.disposition == expected else "MISMATCH"})
    return grid, failures


def run_all(records_n, scn_n, seed, config):
    rows = G.make_records(records_n, random.Random(seed), G.PROFILES["standard"])
    op, fa, recs, leaked = assess_main(rows, config)
    sweep = threshold_sweep(recs, rows, config)
    grid, failures = run_scenarios(seed, scn_n, config)
    main_breach_fail = gate_no_breach_pass(rows, fa, config, "MAIN")
    if main_breach_fail:
        failures.append(main_breach_fail)
    op["scenario_grid"] = grid
    return op, sweep, leaked, failures


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def render_report(op, sweep, manifest):
    c = op["confusion"]
    v = op["volume"]
    pc = op["per_class_detection"]
    cde = op["per_cde"]

    crit_rows = [{"class": k, "planted": pc[k]["planted"],
                  "detected": pc[k]["detected"],
                  "detection_rate": pc[k]["detection_rate"],
                  "detected_by": pc[k]["detected_by"]}
                 for k in G.CRITICAL_CLASSES if k in pc]
    minor_rows = [{"class": k, "planted": pc[k]["planted"],
                   "detected": pc[k]["detected"],
                   "detection_rate": pc[k]["detection_rate"],
                   "detected_by": pc[k]["detected_by"]}
                  for k in MINOR_CLASSES if k in pc]
    cde_rows = [{"cde": k,
                 "screening_critical": "yes" if cde[k]["screening_critical"] else "no",
                 "weight": cde[k]["weight"],
                 "defect_rate": cde[k]["defect_rate"],
                 "critical_rate": cde[k]["critical_rate"],
                 "pass_rate": cde[k]["pass_rate"],
                 "ceiling": cde[k]["ceiling"], "status": cde[k]["status"]}
                for k in S.CDE_WEIGHTS]
    dim_rows = [{"dimension": k, "pass_rate": op["per_dimension"][k]}
                for k in op["per_dimension"]]
    grid_rows = op["scenario_grid"]

    L = []
    A = L.append
    A("# Validation Report — Data-Quality Rules Framework (CDE fitness for screening)")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Every figure is produced by running the reference "
      "engine over a seeded, fully synthetic Harborview Financial Group customer "
      "extract. No real customer or record is represented. Numbers are emitted by "
      "`run_validation.py`, not authored; re-run it to reproduce them.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['records']:,} records · "
      f"{len(grid_rows)} scenario feeds x {manifest['scenario_records']:,} · "
      f"git `{manifest['git_sha']}` · {manifest['generated_utc']}")
    A("")
    A(f"**Headline:** recall on planted critical defects **{c['recall']:.4f}** "
      f"(missed: **{op['critical_missed']}** of {op['critical_planted']:,}), "
      f"false-flag rate on clean records **{op['false_flag_rate_clean']:.4%}** "
      f"({op['clean_flagged']} of {op['clean_records']:,}, including the "
      f"adversarial-benign edge cases), and no critical-breach feed passed — the "
      f"contaminated main feed was correctly dispositioned "
      f"**{op['feed']['disposition']}** while the conformant scenario feed passed.")
    A("")
    A("## 1. Methodology summary")
    A("The engine evaluates named data-quality rules across five dimensions "
      "(COMPLETENESS, VALIDITY, CONSISTENCY, UNIQUENESS, TIMELINESS), each rule "
      "bound to a critical data element with a documented criticality weight. It "
      "produces a per-CDE scorecard, a record-level defect list with named rule "
      "and severity, and a feed disposition: FEED_PASS only on the provable named "
      "cause that every documented threshold is met; INVESTIGATE on named warn-band "
      "or supporting-CDE causes; BLOCK_FEED_TO_SCREENING whenever any "
      "screening-critical CDE breaches its ceiling — a hard gate no weighted score "
      "can override. The engine never drops or repairs a record. Full spec: "
      "`METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['records']:,} extract records with deterministic per-class plant "
      f"counts: {op['critical_planted']:,} critical defects across "
      f"{len(crit_rows)} classes, {sum(r['planted'] for r in minor_rows):,} minor "
      f"defects, and {op['clean_records']:,} clean records — of which "
      f"{pc.get('clean_edge', {}).get('planted', 0):,} are adversarial-BENIGN edge "
      "cases (accented/hyphenated names, leap-day and boundary DOBs, "
      "refresh just inside the horizon) that must NOT be flagged. Adversarial "
      "plants include format-valid-calendar-false DOBs, DOBs valid in format but "
      "impossible in sequence, ISO-adjacent-but-wrong country codes, and "
      "transliterated near-duplicate pairs sharing an identifier.")
    A("")
    A("## 3. Operating-point results")
    A(f"- **Recall on planted critical defects: {c['recall']:.4f}** — "
      f"**missed: {op['critical_missed']}**")
    A(f"- False-flag rate on clean records: {op['false_flag_rate_clean']:.4%} "
      f"({op['clean_flagged']} of {op['clean_records']:,})")
    A(f"- Precision of the critical flag: {c['precision']:.4f} · specificity "
      f"{c['specificity']:.4f}")
    A(f"- Confusion (critical flag) — TP {c['tp']:,} · FP {c['fp']:,} · "
      f"TN {c['tn']:,} · FN {c['fn']:,}")
    A(f"- Weighted composite DQ score of the main feed: "
      f"{op['composite_score']:.4f} · disposition **{op['feed']['disposition']}**")
    A("")
    A("Field-level scorecard (per CDE):")
    A("")
    A(metrics.markdown_table(cde_rows, ["cde", "screening_critical", "weight",
                                        "defect_rate", "critical_rate",
                                        "pass_rate", "ceiling", "status"]))
    A("")
    A("Per-dimension pass rates:")
    A("")
    A(metrics.markdown_table(dim_rows, ["dimension", "pass_rate"]))
    A("")
    A("## 4. Per-category detection")
    A("Critical classes — every planted defect must be caught at critical "
      "severity (this is the gate):")
    A("")
    A(metrics.markdown_table(crit_rows, ["class", "planted", "detected",
                                         "detection_rate", "detected_by"]))
    A("")
    A("Minor classes — flagged at minor severity for the remediation queue; "
      "deliberately NOT part of the hard gate:")
    A("")
    A(metrics.markdown_table(minor_rows, ["class", "planted", "detected",
                                          "detection_rate", "detected_by"]))
    A("")
    A("## 5. Threshold-sensitivity analysis (near-duplicate name similarity)")
    A("A NAME-SIMILARITY-ONLY near-duplicate detector (phonetic and "
      "single-edit fallbacks disabled), for comparison. The deployed detector "
      "pairs the Jaro-Winkler threshold with a per-token Soundex fallback "
      "(holds MOHAMMED/MUHAMMAD) and a single-edit tolerance (holds OMAR/UMAR, "
      "which defeats both Jaro-Winkler and Soundex), keeping recall at 1.0 at "
      f"the default threshold ({manifest['near_dup_name_sim']}). "
      "Similarity-only leaks transliterated pairs as the threshold rises; "
      "false pairs stay at zero throughout because duplicate detection is "
      "blocked on a shared identifier.")
    A("")
    A(metrics.markdown_table(sweep, ["threshold", "near_dup_detected",
                                     "near_dup_recall", "exact_dup_recall",
                                     "false_pair_records"]))
    A("")
    A("## 6. False-negative safety argument")
    A(f"1. Of {op['critical_planted']:,} planted critical defects, "
      f"**{op['critical_missed']} were missed** — recall {c['recall']:.4f}. Every "
      "class is caught by a deterministic parser or rule, not a statistical "
      "guess: blank-name and blank-DOB checks, a strict ISO/calendar date parse, "
      "the approved country reference set, the identifier check-digit contract, "
      "the DOB/onboarding ordering test, and identifier-blocked duplicate "
      "detection with phonetic and single-edit fallbacks.")
    A("2. The feed-level gate is structural: the BLOCK branch is evaluated "
      "before any pass logic, so a screening-critical breach can never be "
      "outweighed by a high composite score. FEED_PASS is only reachable when "
      "every screening-critical CDE is at or below its warn threshold.")
    A("3. Both are enforced as build gates — `run_validation.py` exits non-zero "
      "if any planted critical defect goes undetected, if any feed with a "
      "planted screening-critical breach receives FEED_PASS, or if the scenario "
      "grid below deviates from its expected outcomes.")
    A("")
    A("Feed-disposition scenario grid (deterministic plant counts, so expected "
      "outcomes are stable across seeds):")
    A("")
    A(metrics.markdown_table(grid_rows, ["feed", "records", "expected",
                                         "disposition", "composite", "outcome"]))
    A("")
    A("## 7. Volume / remediation impact")
    A(f"{v['total_records']:,} records → {v['clean_passthrough']:,} clean "
      f"pass-through ({1 - v['remediation_share']:.1%}) → "
      f"{v['records_with_defects']:,} routed to the remediation queue "
      f"({v['remediation_share']:.1%}: {v['critical_records']:,} with a critical "
      f"defect, {v['minor_only_records']:,} minor-only), each with a named rule "
      "and detail string. The feed disposition routes the FEED; the defect list "
      "routes the RECORDS. Nothing is dropped or silently repaired.")
    A("")
    A("## 8. Limitations")
    A("- Synthetic data models the failure shapes of a customer extract "
      "(nulls, format drift, impossible sequences, re-onboarded duplicates), not "
      "the full richness of a production golden source. Recalibrate ceilings and "
      "the similarity threshold on your own profiled extracts (`tuning.md`).")
    A("- Duplicate detection is blocked on a shared national identifier; "
      "same-party pairs holding DIFFERENT identifiers, and identifier collisions "
      "across dissimilar names, are separate controls outside this engine's "
      "scope and are not claimed.")
    A("- The reference set, identifier contract, and policy horizon are "
      "illustrative stand-ins for the institution's documented standards.")
    A("- The engine assesses and routes; it never blocks records, repairs "
      "values, or approves a feed autonomously — FEED_PASS is a named, "
      "evidence-backed recommendation to the data-governance owner.")
    A("- This is a transparent reference implementation, not a production "
      "control.")
    A("")
    A("## 9. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} "
      f"--records {manifest['records']}")
    A("```")
    A("Same seed → identical extract → identical numbers.")
    A("")
    return "\n".join(L)


def write_evidence(out_dir, op, sweep, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    json.dump({"operating_point": op, "manifest": manifest},
              open(os.path.join(out_dir, "metrics.json"), "w"), indent=2)
    with open(os.path.join(out_dir, "threshold-sweep.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sweep[0].keys()))
        w.writeheader()
        w.writerows(sweep)
    c = op["confusion"]
    with open(os.path.join(out_dir, "confusion-matrix.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["", "flagged_critical", "not_flagged_critical"])
        w.writerow(["actual_critical_defect", c["tp"], c["fn"]])
        w.writerow(["actual_no_critical_defect", c["fp"], c["tn"]])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"),
              indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--records", type=int, default=50000)
    ap.add_argument("--scenario-records", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = S.Config()
    op, sweep, leaked, failures = run_all(args.records, args.scenario_records,
                                          args.seed, config)
    c = op["confusion"]
    print(f"\n=== operating point (seed {args.seed}, {args.records:,} records) ===")
    print(f"critical recall {c['recall']:.4f}  missed {op['critical_missed']}  "
          f"false-flag(clean) {op['false_flag_rate_clean']:.4%}  "
          f"composite {op['composite_score']:.4f}  "
          f"main feed {op['feed']['disposition']}")
    print("scenarios:", {g["feed"]: g["disposition"] for g in op["scenario_grid"]})
    print("per-dimension pass:", op["per_dimension"])

    gate_failed = bool(leaked) or c["recall"] < CRIT_RECALL_FLOOR or failures

    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            o, _, lk, fl = run_all(args.records, args.scenario_records, s, config)
            oc = o["confusion"]
            ok = "OK" if not (lk or fl) else "FAIL"
            print(f"  trial seed {s}: recall {oc['recall']:.4f} missed "
                  f"{o['critical_missed']} false-flag {o['false_flag_rate_clean']:.4%} "
                  f"main {o['feed']['disposition']} scenarios "
                  f"{'/'.join(g['disposition'][:4] for g in o['scenario_grid'])} "
                  f"[{ok}]")
            if lk or fl:
                gate_failed = True
                failures.extend(fl + [f"seed {s}: {len(lk)} critical defects leaked"])

    if gate_failed:
        print(f"\nSAFETY GATE FAILED (floor {CRIT_RECALL_FLOOR}):")
        for r in leaked[:10]:
            print("   leaked critical defect:", r)
        for f in failures:
            print("   gate failure:", f)
        return 1

    manifest = {"framework": "data-quality-rules", "seed": args.seed,
                "records": args.records,
                "scenario_records": args.scenario_records,
                "critical_planted": op["critical_planted"],
                "near_dup_name_sim": config.near_dup_name_sim,
                "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                .strftime("%Y-%m-%d %H:%M UTC"),
                "critical_recall_floor": CRIT_RECALL_FLOOR}
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, op, sweep, manifest,
                       render_report(op, sweep, manifest))
        print(f"\nevidence written -> {args.out}/  (safety gates PASSED)")
    else:
        print("\nsafety gates PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
