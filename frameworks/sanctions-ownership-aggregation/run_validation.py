#!/usr/bin/env python3
"""Reproducible dual-gate validation for sanctions ownership aggregation."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
import unittest
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from _local.attest import bound_sentence, clopper_pearson_upper, runtime_provenance, sha256_file, utc_now
from _local.metrics import DISPOSITIONS, summarize
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from _lib.seeding import trial_seeds
from _lib.sanctions_ownership import SanctionsConfig, resolve_candidate
from generate_synthetic_data import generate_cases, write_sample_pack

ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--true-blocked", type=int, default=160)
    parser.add_argument("--below", type=int, default=240)
    parser.add_argument("--unresolved", type=int, default=80)
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--engine", choices=("production", "negative-control"), default="production")
    parser.add_argument("--out", type=Path, help="write the re-derived evidence pack into DIR")
    parser.add_argument("--write-evidence", action=argparse.BooleanOptionalAction, default=None)
    return parser.parse_args()


def run_unit_tests() -> tuple[bool, int]:
    suite = unittest.defaultTestLoader.discover(str(ROOT), pattern="test_sanctions_ownership.py")
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    if not result.wasSuccessful():
        print(stream.getvalue(), file=sys.stderr)
    return result.wasSuccessful(), result.testsRun


def select_scorer(engine: str) -> Callable:
    if engine == "negative-control":
        from negative_control_scorer import score_candidate
        return score_candidate
    return resolve_candidate


def score_cases(cases: list[dict[str, Any]], scorer: Callable,
                config: SanctionsConfig | None = None) -> list[dict[str, Any]]:
    config = config or SanctionsConfig()
    scored = []
    for case in cases:
        result = scorer(case["graph"], case["candidate_id"], config)
        scored.append({
            "case_id": case["case_id"], "category": case["category"], "label": case["label"],
            "disposition": result["disposition"], "reason": result["reason"],
            "aggregate_sanctioned_ownership": result["aggregate_sanctioned_ownership"],
            "maximum_individual_ownership": max(
                (item["effective_ownership"] for item in result["sanctioned_owner_evidence"]), default=0.0),
            "sanctioned_control_prong": result["sanctioned_control_prong"],
            "graph_fully_resolved": result["graph_fully_resolved"],
            "all_converged": result["all_converged"],
            "all_path_evidence_complete": result["all_path_evidence_complete"],
            "auto_clear_eligible": result["auto_clear_eligible"],
        })
    return scored


def category_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    output: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        output[row["category"]][row["disposition"]] += 1
    return {category: dict(sorted(counts.items())) for category, counts in sorted(output.items())}


def gates(metrics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "false_negative": {
            "pass": metrics["clear_false_negatives"] == 0,
            "observed": metrics["clear_false_negatives"],
            "criterion": "no labelled TRUE blocked-by-ownership candidate may be auto-cleared",
        },
        "resolution_integrity": {
            "pass": metrics["resolution_integrity_leaks"] == 0 and metrics["unresolved_plant_clears"] == 0,
            "observed_structural_leaks": metrics["resolution_integrity_leaks"],
            "observed_unresolved_plant_clears": metrics["unresolved_plant_clears"],
            "criterion": "every auto-clear must be eligible and no unresolved sanctioned path may be auto-cleared",
        },
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_report(metrics: dict[str, Any], manifest: dict[str, Any]) -> str:
    gate = metrics["gates"]
    matrix = metrics["confusion"]
    return f"""# Validation Report

Generated deterministically by `run_validation.py`; all numeric results are emitted by the harness.

## Result

| Gate | Status | Observed |
|---|---:|---:|
| False-negative | {'PASS' if gate['false_negative']['pass'] else 'FAIL'} | {gate['false_negative']['observed']} TRUE blocked → auto-clear |
| Resolution-integrity | {'PASS' if gate['resolution_integrity']['pass'] else 'FAIL'} | {gate['resolution_integrity']['observed_structural_leaks']} structural leaks; {gate['resolution_integrity']['observed_unresolved_plant_clears']} unresolved-chain clears |

## Aggregate confusion matrix

| Ground truth | BLOCKED | NOT BLOCKED | REVIEW |
|---|---:|---:|---:|
| TRUE_BLOCKED | {matrix['TRUE_BLOCKED']['BLOCKED_BY_OWNERSHIP']} | {matrix['TRUE_BLOCKED']['NOT_BLOCKED_BY_OWNERSHIP']} | {matrix['TRUE_BLOCKED']['REVIEW']} |
| NOT_BLOCKED | {matrix['NOT_BLOCKED']['BLOCKED_BY_OWNERSHIP']} | {matrix['NOT_BLOCKED']['NOT_BLOCKED_BY_OWNERSHIP']} | {matrix['NOT_BLOCKED']['REVIEW']} |

Blocked-by-ownership recall: {metrics['blocked_recall']:.6f}. Review rate: {metrics['review_rate']:.6f}.

## Exact uncertainty statement

{metrics['clear_false_negative_attestation']}

## Deterministic reproduction inputs

- Seed schedule: {manifest['trial_seeds']}
- Per-trial sizes: {manifest['sizes_per_trial']}
- Blocked threshold: 0.50
- Review floor: 0.25
"""


def emit_evidence(out_dir: Path, primary_cases: list[dict[str, Any]], metrics: dict[str, Any],
                  manifest: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    matrix_rows = [{"ground_truth": label, "disposition": disposition,
                    "count": metrics["confusion"][label][disposition]}
                   for label in ("TRUE_BLOCKED", "NOT_BLOCKED") for disposition in DISPOSITIONS]
    write_csv(out_dir / "confusion-matrix.csv", ["ground_truth", "disposition", "count"], matrix_rows)
    sweep_rows = []
    for floor in (.10, .20, .25, .30, .40):
        scored = score_cases(primary_cases, resolve_candidate, SanctionsConfig(review_floor=floor))
        values = summarize(scored)
        sweep_rows.append({
            "blocked_threshold": "0.50", "review_floor": f"{floor:.2f}",
            "clear_false_negatives": values["clear_false_negatives"],
            "resolution_integrity_leaks": values["resolution_integrity_leaks"],
            "blocked_recall": f"{values['blocked_recall']:.6f}",
            "review_rate": f"{values['review_rate']:.6f}",
        })
    write_csv(out_dir / "threshold-sweep.csv",
              ["blocked_threshold", "review_floor", "clear_false_negatives",
               "resolution_integrity_leaks", "blocked_recall", "review_rate"], sweep_rows)
    (out_dir / "run-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "VALIDATION-REPORT.md").write_text(render_report(metrics, manifest), encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.trials < 1:
        print("error: --trials must be >= 1", file=sys.stderr)
        return 2
    started_utc = utc_now()
    started = time.perf_counter()
    unit_ok, tests_run = run_unit_tests()
    if not unit_ok:
        print("UNIT TESTS: FAIL", file=sys.stderr)
        return 2
    scorer = select_scorer(args.engine)
    seeds = trial_seeds(args.seed, args.trials)
    all_scored: list[dict[str, Any]] = []
    trial_metrics = []
    primary_cases: list[dict[str, Any]] = []
    print(f"engine={args.engine} unit_tests={tests_run} seed={args.seed} trials={args.trials}")
    print("seed  candidates  true_blocked  clear_FN  integrity_leaks  unresolved_clears  gate")
    for trial_seed in seeds:
        cases = generate_cases(trial_seed, args.true_blocked, args.below, args.unresolved)
        if not primary_cases:
            primary_cases = cases
        scored = score_cases(cases, scorer)
        values = summarize(scored)
        trial_gate = gates(values)
        passed = all(item["pass"] for item in trial_gate.values())
        trial_metrics.append({"seed": trial_seed, **{key: value for key, value in values.items() if key != "confusion"},
                              "gates_pass": passed})
        all_scored.extend(scored)
        print(f"{trial_seed:4d}  {values['candidates']:10d}  {values['true_blocked_candidates']:12d}  "
              f"{values['clear_false_negatives']:8d}  {values['resolution_integrity_leaks']:15d}  "
              f"{values['unresolved_plant_clears']:17d}  {'PASS' if passed else 'FAIL'}")
    aggregate = summarize(all_scored)
    aggregate["category_dispositions"] = category_summary(all_scored)
    aggregate["trials"] = trial_metrics
    aggregate["gates"] = gates(aggregate)
    aggregate["clear_false_negative_cp_upper_95"] = clopper_pearson_upper(
        aggregate["clear_false_negatives"], aggregate["true_blocked_candidates"], .95)
    aggregate["clear_false_negative_attestation"] = bound_sentence(
        aggregate["clear_false_negatives"], aggregate["true_blocked_candidates"], .95)
    aggregate_pass = all(item["pass"] for item in aggregate["gates"].values())
    elapsed = time.perf_counter() - started
    manifest = {
        "schema_version": "1.0", "engine": args.engine, "command": "python3 " + " ".join(sys.argv),
        "base_seed": args.seed, "trial_seeds": seeds, "trials": args.trials,
        "sizes_per_trial": {"true_blocked": args.true_blocked, "below": args.below,
                            "unresolved": args.unresolved,
                            "total": args.true_blocked + args.below + args.unresolved},
        "unit_tests_run": tests_run, "started_utc": started_utc, "completed_utc": utc_now(),
        "wall_clock_seconds": round(elapsed, 6), **runtime_provenance(),
        "generator_sha256": sha256_file(ROOT / "generate_synthetic_data.py"),
        "sanctions_engine_sha256": sha256_file(ROOT.parent / "_lib" / "sanctions_ownership.py"),
        "shared_ownership_sha256": sha256_file(ROOT.parent / "_lib" / "ownership.py"),
        "network_used": False,
    }
    write_evidence = (args.engine == "production") if args.write_evidence is None else args.write_evidence
    if args.out is not None:
        write_evidence = True
    if write_evidence:
        # reference-data/ is owned by _tooling/build_reference_data.py (CI-gated);
        # the harness writes evidence only.
        emit_evidence(args.out or (ROOT / "evidence"), primary_cases, aggregate, manifest)
    print("false_negative_gate=" + ("PASS" if aggregate["gates"]["false_negative"]["pass"] else "FAIL"))
    print("resolution_integrity_gate=" + ("PASS" if aggregate["gates"]["resolution_integrity"]["pass"] else "FAIL"))
    print(aggregate["clear_false_negative_attestation"])
    if not aggregate_pass:
        leaked = [row for row in all_scored if
                  (row["label"] == "TRUE_BLOCKED" and row["disposition"] == "NOT_BLOCKED_BY_OWNERSHIP") or
                  (row["disposition"] == "NOT_BLOCKED_BY_OWNERSHIP" and not row["auto_clear_eligible"])]
        print(f"LEAKED CASES ({len(leaked)} total; first 12):", file=sys.stderr)
        for row in leaked[:12]:
            print(json.dumps(row, sort_keys=True), file=sys.stderr)
        print("VALIDATION: FAIL (non-zero exit)", file=sys.stderr)
        return 1
    print("VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
