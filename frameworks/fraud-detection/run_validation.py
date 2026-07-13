"""Validation harness and dual safety build gate for fraud-detection.

The primary run is deterministic. ``--trials K`` means the primary seed plus K
additional independent seeds. Throughput is intentionally printed only to stdout;
it is excluded from every deterministic evidence file.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from dataclasses import asdict, fields
from pathlib import Path

HERE = Path(__file__).resolve().parent
FRAMEWORKS = HERE.parent
sys.path.insert(0, str(FRAMEWORKS))

from _lib import attest, metrics  # noqa: E402
import generate_synthetic_data as G  # noqa: E402
import scorer as S  # noqa: E402


CONFIDENCE = 0.95
MAX_FAILURE_RATE = 0.001
THRESHOLDS = (0.25, 0.40, 0.55, 0.70, 0.80, 0.88, 0.94)
HARD_DISPOSITIONS = {
    S.Disposition.DECLINE_PENDING_REVIEW.value,
    S.Disposition.REFER_FOR_BLOCK_CONFIRMATION.value,
}
DEFAULT_EVIDENCE = HERE / "evidence"


def _construct_event(row: dict) -> S.FraudEvent:
    names = {field.name for field in fields(S.FraudEvent)}
    return S.FraudEvent(**{name: row[name] for name in names})


def run_once(transactions: int, seed: int, config: S.Config) -> tuple[list[dict], float]:
    started = time.perf_counter()
    baseline_rows, event_rows = G.make_population(transactions, random.Random(seed))
    records = []
    for row in event_rows:
        baseline = S.CustomerBaseline(**baseline_rows[row["customer_id"]])
        decision = S.score_event(_construct_event(row), baseline, config)
        records.append(
            {
                "event_id": row["event_id"],
                "label": int(row["label"]),
                "typology": row["typology"],
                "category": row["category"],
                "boundary_case": bool(row["boundary_case"]),
                "disposition": decision.disposition.value,
                "score": decision.score,
                "named_cause": decision.named_cause,
                "risk_floor": decision.risk_floor.value,
                "fired_rules": [result.name for result in decision.fired_rules],
                "corroborating_causes": list(decision.corroborating_causes),
            }
        )
    return records, time.perf_counter() - started


def inject_gate_failure(records: list[dict], mode: str | None) -> None:
    """Plant one explicit harness-level failure without weakening the scorer."""
    if not mode:
        return
    if mode == "fraud-miss":
        target = next(record for record in records if record["label"] == 1)
        target["disposition"] = S.Disposition.APPROVE.value
        target["named_cause"] = "injected_fraud_miss"
    elif mode == "false-decline":
        target = next(record for record in records if record["label"] == 0)
        target["disposition"] = S.Disposition.DECLINE_PENDING_REVIEW.value
        target["named_cause"] = "injected_false_decline"


def operating_point(records: list[dict]) -> dict:
    fraud_records = [record for record in records if record["label"] == 1]
    legitimate_records = [record for record in records if record["label"] == 0]
    fraud_misses = [
        record for record in fraud_records
        if record["disposition"] == S.Disposition.APPROVE.value
    ]
    false_declines = [
        record for record in legitimate_records if record["disposition"] in HARD_DISPOSITIONS
    ]
    unauthorized_approvals = [
        record for record in records
        if record["disposition"] == S.Disposition.APPROVE.value
        and (
            record["named_cause"] != "trusted_session_continuity"
            or bool(record["fired_rules"])
        )
    ]
    hard_without_corroboration = [
        record for record in records
        if record["disposition"] in HARD_DISPOSITIONS
        and (
            not record["named_cause"].startswith("corroborated_")
            or len(record["corroborating_causes"]) < 2
            or not record["fired_rules"]
        )
    ]
    rank = {disposition.value: index for index, disposition in enumerate(S.Disposition)}
    floor_violations = [
        record for record in records
        if rank[record["disposition"]] < rank[record["risk_floor"]]
    ]
    intervened = [
        record for record in records if record["disposition"] != S.Disposition.APPROVE.value
    ]
    intervention_fraud = sum(record["label"] for record in intervened)
    prevalence = len(fraud_records) / len(records)
    intervention_precision = intervention_fraud / len(intervened) if intervened else 1.0

    funnel = {disposition.value: 0 for disposition in S.Disposition}
    for record in records:
        funnel[record["disposition"]] += 1

    typologies = {}
    for name in G.TYPOLOGIES:
        subset = [record for record in fraud_records if record["typology"] == name]
        misses = sum(record["disposition"] == S.Disposition.APPROVE.value for record in subset)
        dispositions = {key: 0 for key in funnel}
        for record in subset:
            dispositions[record["disposition"]] += 1
        typologies[name] = {
            "total": len(subset),
            "boundary_cases": sum(record["boundary_case"] for record in subset),
            "detected": len(subset) - misses,
            "recall": (len(subset) - misses) / len(subset) if subset else 1.0,
            "dispositions": dispositions,
        }

    legitimate_categories = {}
    for category in G.LEGITIMATE_CATEGORIES:
        subset = [record for record in legitimate_records if record["category"] == category]
        legitimate_categories[category] = {
            "total": len(subset),
            "boundary_cases": sum(record["boundary_case"] for record in subset),
            "approved": sum(
                record["disposition"] == S.Disposition.APPROVE.value for record in subset
            ),
            "step_up": sum(
                record["disposition"] == S.Disposition.STEP_UP_AUTH.value for record in subset
            ),
            "hard_declines": sum(record["disposition"] in HARD_DISPOSITIONS for record in subset),
        }

    fraud_bound = attest.failure_rate_bound(len(fraud_records), len(fraud_misses), CONFIDENCE)
    false_decline_bound = attest.failure_rate_bound(
        len(legitimate_records), len(false_declines), CONFIDENCE
    )
    return {
        "population": {
            "transactions": len(records),
            "confirmed_fraud": len(fraud_records),
            "legitimate": len(legitimate_records),
            "fraud_prevalence": prevalence,
        },
        "dual_safety": {
            "fraud_miss": {
                "count": len(fraud_misses),
                "rate": len(fraud_misses) / len(fraud_records),
                "fraud_recall": 1.0 - len(fraud_misses) / len(fraud_records),
                "exact_bound": fraud_bound,
                "offending_event_ids": [record["event_id"] for record in fraud_misses],
            },
            "false_decline": {
                "count": len(false_declines),
                "rate": len(false_declines) / len(legitimate_records),
                "legitimate_accept_or_step_up_rate": 1.0 - len(false_declines) / len(legitimate_records),
                "exact_bound": false_decline_bound,
                "offending_event_ids": [record["event_id"] for record in false_declines],
            },
            "required_observed_count": 0,
            "maximum_95pct_upper_bound": MAX_FAILURE_RATE,
        },
        "structural_invariants": {
            "approve_without_trusted_session_continuity": len(unauthorized_approvals),
            "hard_disposition_without_named_corroboration": len(hard_without_corroboration),
            "risk_floor_violations": len(floor_violations),
            "offending_event_ids": sorted(
                {
                    record["event_id"]
                    for record in (
                        unauthorized_approvals
                        + hard_without_corroboration
                        + floor_violations
                    )
                }
            ),
            "missing_typologies": [
                name for name in G.TYPOLOGIES if typologies[name]["total"] == 0
            ],
            "missing_legitimate_categories": [
                name
                for name in G.LEGITIMATE_CATEGORIES
                if legitimate_categories[name]["total"] == 0
            ],
        },
        "intervention": {
            "count": len(intervened),
            "fraud_count": intervention_fraud,
            "precision": intervention_precision,
            "lift_over_prevalence": intervention_precision / prevalence if prevalence else 0.0,
        },
        "disposition_funnel": funnel,
        "per_typology": typologies,
        "per_legitimate_category": legitimate_categories,
    }


def gate_failures(result: dict) -> list[str]:
    safety = result["dual_safety"]
    failures = []
    for key, label in (("fraud_miss", "FRAUD-MISS"), ("false_decline", "FALSE-DECLINE")):
        metric = safety[key]
        if metric["count"] != safety["required_observed_count"]:
            failures.append(
                f"{label}: observed {metric['count']} failures; required exactly zero"
            )
        upper = metric["exact_bound"]["upper_bound"]
        if upper > safety["maximum_95pct_upper_bound"]:
            failures.append(
                f"{label}: exact 95% upper bound {upper:.6%} exceeds 0.100000%"
            )
    structural = result["structural_invariants"]
    for key in (
        "approve_without_trusted_session_continuity",
        "hard_disposition_without_named_corroboration",
        "risk_floor_violations",
    ):
        if structural[key]:
            failures.append(f"STRUCTURAL: {key}={structural[key]}; required zero")
    if structural["missing_typologies"]:
        failures.append(
            "STRUCTURAL: missing typology labels " + ", ".join(structural["missing_typologies"])
        )
    if structural["missing_legitimate_categories"]:
        failures.append(
            "STRUCTURAL: missing legitimate categories "
            + ", ".join(structural["missing_legitimate_categories"])
        )
    return failures


def threshold_sweep(records: list[dict]) -> list[dict]:
    fraud_count = sum(record["label"] for record in records)
    legitimate_count = len(records) - fraud_count
    rows = []
    for threshold in THRESHOLDS:
        fraud_missed = sum(
            record["label"] == 1 and record["score"] < threshold for record in records
        )
        legitimate_hard_declined = sum(
            record["label"] == 0 and record["score"] >= threshold for record in records
        )
        rows.append(
            {
                "score_threshold": threshold,
                "fraud_recall_if_score_only": round(1 - fraud_missed / fraud_count, 6),
                "fraud_misses_if_score_only": fraud_missed,
                "legitimate_false_decline_rate_if_score_only": round(
                    legitimate_hard_declined / legitimate_count, 6
                ),
                "legitimate_hard_declines_if_score_only": legitimate_hard_declined,
            }
        )
    return rows


def _trial_summary(seed: int, result: dict) -> dict:
    return {
        "seed": seed,
        "transactions": result["population"]["transactions"],
        "fraud_recall": result["dual_safety"]["fraud_miss"]["fraud_recall"],
        "fraud_misses": result["dual_safety"]["fraud_miss"]["count"],
        "fraud_miss_upper_bound": result["dual_safety"]["fraud_miss"]["exact_bound"]["upper_bound"],
        "false_decline_rate": result["dual_safety"]["false_decline"]["rate"],
        "false_declines": result["dual_safety"]["false_decline"]["count"],
        "false_decline_upper_bound": result["dual_safety"]["false_decline"]["exact_bound"]["upper_bound"],
        "intervention_precision": result["intervention"]["precision"],
        "intervention_lift": result["intervention"]["lift_over_prevalence"],
    }


def _source_hashes() -> dict[str, str]:
    used_library_modules = (
        "__init__.py",
        "aggregations.py",
        "attest.py",
        "metrics.py",
        "rules.py",
        "sampling.py",
    )
    source_paths = [
        HERE / "scorer.py",
        HERE / "generate_synthetic_data.py",
        HERE / "run_validation.py",
        *(FRAMEWORKS / "_lib" / name for name in used_library_modules),
    ]
    return attest.file_hashes(source_paths, FRAMEWORKS)


def _report(result: dict, sweep: list[dict], trials: list[dict], manifest: dict) -> str:
    population = result["population"]
    safety = result["dual_safety"]
    intervention = result["intervention"]
    funnel = result["disposition_funnel"]
    typology_rows = []
    for name, item in result["per_typology"].items():
        typology_rows.append(
            {
                "typology": name,
                "confirmed": item["total"],
                "boundary_cases": item["boundary_cases"],
                "detected": item["detected"],
                "recall": f"{item['recall']:.4f}",
            }
        )
    trial_rows = [
        {
            "seed": trial["seed"],
            "fraud_recall": f"{trial['fraud_recall']:.4f}",
            "fraud_misses": trial["fraud_misses"],
            "false_declines": trial["false_declines"],
            "intervention_precision": f"{trial['intervention_precision']:.4f}",
        }
        for trial in trials
    ]
    lines = [
        "# Validation Report — Fraud-Detection Triage Engine",
        "",
        "> ILLUSTRATIVE / SYNTHETIC. Every figure below was rendered by `run_validation.py` from a seeded, labelled population. No real person, account, or transaction is represented.",
        "",
        "> **In plain terms:** The engine caught every planted confirmed-fraud event and hard-declined none of the legitimate events. Both zero counts are paired with exact statistical bounds; they are finite-sample evidence, not a guarantee about live activity.",
        "",
        f"**Run:** seed `{manifest['seed']}`; {population['transactions']:,} transactions; {population['confirmed_fraud']:,} confirmed fraud ({population['fraud_prevalence']:.2%}); results digest `{manifest['results_sha256']}`.",
        "",
        "## Dual safety invariant",
        "",
        f"- Fraud miss: **{safety['fraud_miss']['count']}** confirmed-fraud events received `APPROVE`; recall **{safety['fraud_miss']['fraud_recall']:.4f}**. Exact one-sided 95% upper miss-rate bound: **{safety['fraud_miss']['exact_bound']['upper_bound']:.4%}**.",
        f"- False decline: **{safety['false_decline']['count']}** legitimate events received a hard disposition; rate **{safety['false_decline']['rate']:.4%}**. Exact one-sided 95% upper false-decline-rate bound: **{safety['false_decline']['exact_bound']['upper_bound']:.4%}**.",
        f"- Gate requirement: each observed count is zero and each bound is no greater than **{MAX_FAILURE_RATE:.1%}**. Both branches passed.",
        "",
        "The false-decline definition includes `DECLINE_PENDING_REVIEW` and `REFER_FOR_BLOCK_CONFIRMATION`; `STEP_UP_AUTH` is excluded. `APPROVE` is available only for `trusted_session_continuity` and no fired fraud rule. Risk floors are raise-only.",
        "",
        "## Operating point",
        "",
        f"Interventions (step-up or harder): {intervention['count']:,}; precision **{intervention['precision']:.4f}**; lift **{intervention['lift_over_prevalence']:.2f}x** over the {population['fraud_prevalence']:.2%} fraud prevalence.",
        "",
        "| Disposition | Count | Share |",
        "| --- | ---: | ---: |",
    ]
    for disposition in (item.value for item in S.Disposition):
        lines.append(
            f"| {disposition} | {funnel[disposition]:,} | {funnel[disposition] / population['transactions']:.2%} |"
        )
    lines.extend(
        [
            "",
            "## Per-typology performance",
            "",
            metrics.markdown_table(typology_rows),
            "",
            "## Multi-seed stability",
            "",
            f"`--trials {len(trials) - 1}` means the primary seed plus {len(trials) - 1} additional seeds.",
            "",
            metrics.markdown_table(trial_rows),
            "",
            "## Counterfactual score-only threshold sweep",
            "",
            "This table demonstrates why the deployed engine does not use a bare score for a hard decision. The actual disposition contract requires a named rule and corroborating causes.",
            "",
            metrics.markdown_table(sweep),
            "",
            "## Limitations",
            "",
            "- Labels are constructed and features are stylized. Live prevalence, drift, upstream authentication quality, merchant intelligence, and identity resolution must be independently validated.",
            "- Exact bounds describe these independent seeded synthetic populations; they are not production guarantees.",
            "- The engine recommends routing. It does not execute a decline, block, filing, freeze, or customer action.",
            "",
            "## Reproduction",
            "",
            "```bash",
            f"python3 run_validation.py --seed {manifest['seed']} --transactions {manifest['transactions']} --trials {manifest['additional_trials']}",
            "```",
            "",
            "**Confidence rating: HIGH —** the deterministic evidence re-runs byte-for-byte and both planted gate branches fail as designed; production transfer remains unvalidated.",
            "",
        ]
    )
    return "\n".join(lines)


def _evidence_readme(result: dict, manifest: dict) -> str:
    safety = result["dual_safety"]
    return "\n".join(
        [
            "# Fraud-Detection Evidence Pack",
            "",
            "Generated, not authored, by `../run_validation.py` from the configuration and seed in `run-manifest.json`.",
            "",
            f"- Fraud recall: **{safety['fraud_miss']['fraud_recall']:.4f}**; misses: **{safety['fraud_miss']['count']}**; 95% upper miss-rate bound: **{safety['fraud_miss']['exact_bound']['upper_bound']:.4%}**.",
            f"- Legitimate false-decline rate: **{safety['false_decline']['rate']:.4%}**; false declines: **{safety['false_decline']['count']}**; 95% upper bound: **{safety['false_decline']['exact_bound']['upper_bound']:.4%}**.",
            f"- Results digest: `{manifest['results_sha256']}`.",
            "",
            "`VALIDATION-REPORT.md` explains the contract and limitations; the JSON and CSV files are machine-readable evidence.",
            "",
            "**Confidence rating: HIGH —** the pack is deterministic and directly derived from labelled synthetic cases.",
            "",
        ]
    )


def _readme_metrics(result: dict, trials: list[dict], manifest: dict) -> str:
    safety = result["dual_safety"]
    intervention = result["intervention"]
    return "\n".join(
        [
            "<!-- GENERATED-METRICS:START -->",
            f"Validated at seed {manifest['seed']} on {manifest['transactions']:,} synthetic transactions ({manifest['confirmed_fraud']:,} confirmed fraud):",
            "",
            f"- Fraud recall **{safety['fraud_miss']['fraud_recall']:.4f}**; {safety['fraud_miss']['count']} misses; exact one-sided 95% upper miss-rate bound **{safety['fraud_miss']['exact_bound']['upper_bound']:.4%}**.",
            f"- Legitimate false-decline rate **{safety['false_decline']['rate']:.4%}**; {safety['false_decline']['count']} hard declines; exact one-sided 95% upper bound **{safety['false_decline']['exact_bound']['upper_bound']:.4%}**.",
            f"- Intervention precision **{intervention['precision']:.4f}**, a **{intervention['lift_over_prevalence']:.2f}x** lift over prevalence.",
            f"- Stability: both gates passed on the primary seed plus {len(trials) - 1} additional seeds.",
            "<!-- GENERATED-METRICS:END -->",
        ]
    )


def write_evidence(
    out_dir: Path,
    result: dict,
    sweep: list[dict],
    trials: list[dict],
    manifest: dict,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"operating_point": result, "stability": trials}
    for filename, value in (("metrics.json", payload), ("run-manifest.json", manifest)):
        with (out_dir / filename).open("w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
    with (out_dir / "confusion-matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        intervention = result["intervention"]
        fraud = result["population"]["confirmed_fraud"]
        legitimate = result["population"]["legitimate"]
        writer.writerow(["", "intervention", "approve"])
        writer.writerow(["confirmed_fraud", intervention["fraud_count"], fraud - intervention["fraud_count"]])
        writer.writerow(["legitimate", intervention["count"] - intervention["fraud_count"], legitimate - (intervention["count"] - intervention["fraud_count"])])
    with (out_dir / "threshold-sweep.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sweep[0]))
        writer.writeheader()
        writer.writerows(sweep)
    (out_dir / "VALIDATION-REPORT.md").write_text(
        _report(result, sweep, trials, manifest), encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        _evidence_readme(result, manifest), encoding="utf-8"
    )

    if out_dir.resolve() == DEFAULT_EVIDENCE.resolve():
        readme_path = HERE / "README.md"
        readme = readme_path.read_text(encoding="utf-8")
        start = "<!-- GENERATED-METRICS:START -->"
        end = "<!-- GENERATED-METRICS:END -->"
        before, remainder = readme.split(start, 1)
        _, after = remainder.split(end, 1)
        readme_path.write_text(
            before + _readme_metrics(result, trials, manifest) + after,
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--transactions", type=int, default=50000)
    parser.add_argument("--trials", type=int, default=0)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--out", default=str(DEFAULT_EVIDENCE))
    parser.add_argument(
        "--inject-gate-failure", choices=("fraud-miss", "false-decline")
    )
    args = parser.parse_args()
    if args.trials < 0:
        parser.error("--trials must be non-negative")

    config = S.Config()
    primary_records, elapsed = run_once(args.transactions, args.seed, config)
    inject_gate_failure(primary_records, args.inject_gate_failure)
    primary = operating_point(primary_records)
    failures = gate_failures(primary)

    print(f"=== fraud-detection seed {args.seed}; {args.transactions:,} transactions ===")
    print(
        f"fraud recall {primary['dual_safety']['fraud_miss']['fraud_recall']:.6f}; "
        f"misses {primary['dual_safety']['fraud_miss']['count']}; "
        f"95% upper {primary['dual_safety']['fraud_miss']['exact_bound']['upper_bound']:.6%}"
    )
    print(
        f"legitimate false-decline rate {primary['dual_safety']['false_decline']['rate']:.6%}; "
        f"false declines {primary['dual_safety']['false_decline']['count']}; "
        f"95% upper {primary['dual_safety']['false_decline']['exact_bound']['upper_bound']:.6%}"
    )
    print(
        f"intervention precision {primary['intervention']['precision']:.6f}; "
        f"lift {primary['intervention']['lift_over_prevalence']:.3f}x"
    )
    print(f"funnel {primary['disposition_funnel']}")
    print(f"throughput {args.transactions / elapsed:,.0f} events/second ({elapsed:.3f}s; volatile)")

    if failures:
        print("\nDUAL SAFETY GATE FAILED")
        for failure in failures:
            print(f"- {failure}")
        for metric_name in ("fraud_miss", "false_decline"):
            for event_id in primary["dual_safety"][metric_name]["offending_event_ids"][:20]:
                print(f"  offending transaction ID [{metric_name}]: {event_id}")
        print("Evidence was not written.")
        return 1

    trials = [_trial_summary(args.seed, primary)]
    for offset in range(1, args.trials + 1):
        seed = args.seed + offset
        records, trial_elapsed = run_once(args.transactions, seed, config)
        result = operating_point(records)
        trial_failures = gate_failures(result)
        trials.append(_trial_summary(seed, result))
        print(
            f"trial seed {seed}: recall {result['dual_safety']['fraud_miss']['fraud_recall']:.6f}; "
            f"fraud misses {result['dual_safety']['fraud_miss']['count']}; "
            f"false declines {result['dual_safety']['false_decline']['count']}; "
            f"throughput {args.transactions / trial_elapsed:,.0f}/s (volatile)"
        )
        if trial_failures:
            print("\nDUAL SAFETY GATE FAILED ON STABILITY TRIAL")
            for failure in trial_failures:
                print(f"- seed {seed}: {failure}")
            return 1

    sweep = threshold_sweep(primary_records)
    core_results = {"operating_point": primary, "stability": trials, "threshold_sweep": sweep}
    manifest = attest.deterministic_manifest(
        {
            "schema_version": 1,
            "framework": "fraud-detection",
            "seed": args.seed,
            "transactions": args.transactions,
            "confirmed_fraud": primary["population"]["confirmed_fraud"],
            "legitimate": primary["population"]["legitimate"],
            "additional_trials": args.trials,
            "trial_seeds": [trial["seed"] for trial in trials],
            "confidence": CONFIDENCE,
            "maximum_failure_rate": MAX_FAILURE_RATE,
            "config": asdict(config),
        },
        _source_hashes(),
        core_results,
    )
    if not args.no_write:
        write_evidence(Path(args.out), primary, sweep, trials, manifest)
        print(f"evidence written -> {Path(args.out)}")
    else:
        print("evidence not written (--no-write)")
    print("DUAL SAFETY GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
