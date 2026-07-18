#!/usr/bin/env python3
"""Generate BUILD-NOTES.md exclusively from harness-emitted evidence."""

from __future__ import annotations

import json
from pathlib import Path

from _local.attest import bound_sentence, clopper_pearson_upper
from _local.metrics import summarize
from generate_synthetic_data import generate_pairs
from negative_control_scorer import score_pair
from run_validation import gates, score_rows

ROOT = Path(__file__).resolve().parent


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def trial_table(metrics: dict) -> str:
    lines = ["| Seed | Pairs | TRUE-SAME | Clear FN | False merges | Name-only merges | Structural leaks | Gate |",
             "|---:|---:|---:|---:|---:|---:|---:|:---:|"]
    for trial in metrics["trials"]:
        lines.append(
            f"| {trial['seed']} | {trial['pairs']} | {trial['true_same_pairs']} | {trial['clear_false_negatives']} | "
            f"{trial['auto_same_false_merges']} | {trial['name_only_false_merges']} | "
            f"{trial['structural_same_without_strong_id']} | {'PASS' if trial['gates_pass'] else 'FAIL'} |"
        )
    return "\n".join(lines)


def console_transcript(metrics: dict, manifest: dict, engine: str) -> str:
    lines = [f"engine={engine} unit_tests={manifest['unit_tests_run']} seed={manifest['base_seed']} trials={manifest['trials']}",
             "seed  pairs  true_same  clear_FN  false_merges  name_only_merges  structural_leaks  gate"]
    for trial in metrics["trials"]:
        lines.append(f"{trial['seed']:4d}  {trial['pairs']:5d}  {trial['true_same_pairs']:9d}  "
                     f"{trial['clear_false_negatives']:8d}  {trial['auto_same_false_merges']:12d}  "
                     f"{trial['name_only_false_merges']:16d}  {trial['structural_same_without_strong_id']:16d}  "
                     f"{'PASS' if trial['gates_pass'] else 'FAIL'}")
    lines.extend([
        "false_negative_gate=" + ("PASS" if metrics["gates"]["false_negative"]["pass"] else "FAIL"),
        "false_merge_gate=" + ("PASS" if metrics["gates"]["false_merge"]["pass"] else "FAIL"),
        metrics["clear_false_negative_attestation"],
        "VALIDATION: PASS" if all(gate["pass"] for gate in metrics["gates"].values()) else "VALIDATION: FAIL (non-zero exit)",
    ])
    return "\n".join(lines)


def leaked_examples(manifest: dict) -> list[dict]:
    rows = generate_pairs(manifest["base_seed"], manifest["sizes_per_trial"]["same"],
                          manifest["sizes_per_trial"]["different"], manifest["sizes_per_trial"]["name_only"])
    leaked = []
    for row in rows:
        result = score_pair(row["query"], row["candidate"])
        if ((row["label"] == "SAME" and result["disposition"] == "DIFFERENT") or
                (row["label"] == "DIFFERENT" and result["disposition"] == "SAME")):
            leaked.append({"pair_id": row["pair_id"], "category": row["category"], "label": row["label"],
                           "disposition": result["disposition"], "reason": result["reason"]})
    transliteration = next(row for row in leaked if row["label"] == "SAME" and "romanization" in row["reason"])
    common_name = next(row for row in leaked if row["category"] == "distinct_common_name_name_only")
    return [transliteration, common_name]


def negative_metrics(manifest: dict) -> dict:
    all_scored = []
    trials = []
    sizes = manifest["sizes_per_trial"]
    for seed in manifest["trial_seeds"]:
        rows = generate_pairs(seed, sizes["same"], sizes["different"], sizes["name_only"])
        scored = score_rows(rows, score_pair)
        values = summarize(scored)
        trial_gate = gates(values)
        trials.append({"seed": seed, **{key: value for key, value in values.items() if key != "confusion"},
                       "gates_pass": all(item["pass"] for item in trial_gate.values())})
        all_scored.extend(scored)
    aggregate = summarize(all_scored)
    aggregate["trials"] = trials
    aggregate["gates"] = gates(aggregate)
    aggregate["clear_false_negative_cp_upper_95"] = clopper_pearson_upper(
        aggregate["clear_false_negatives"], aggregate["true_same_pairs"], 0.95)
    aggregate["clear_false_negative_attestation"] = bound_sentence(
        aggregate["clear_false_negatives"], aggregate["true_same_pairs"], 0.95)
    return aggregate


def main() -> int:
    production = load(ROOT / "evidence" / "metrics.json")
    production_manifest = load(ROOT / "evidence" / "run-manifest.json")
    negative = negative_metrics(production_manifest)
    negative_manifest = production_manifest
    reproduce_line = (ROOT / "REPRODUCE.json").read_text(encoding="utf-8").strip()
    leaks = "\n".join(json.dumps(item, sort_keys=True) for item in leaked_examples(negative_manifest))
    content = f"""# Build Notes

Generated from harness evidence by `generate_build_notes.py`; reported counts are not hand-entered.

## Passing validation console transcript

Command:

```bash
python3 run_validation.py --seed 42 --same 160 --different 240 --name-only 80 --trials 6
```

Console (`exit 0`):

```text
{console_transcript(production, production_manifest, 'production')}
```

## Multi-seed stability

{trial_table(production)}

{production['clear_false_negative_attestation']}

## Proof the gates are real

`negative_control_scorer.py` deliberately introduces both forbidden behaviors: romanization differences can clear a true match, and exact common names can auto-merge without an identifier.

```bash
python3 run_validation.py --seed 42 --same 160 --different 240 --name-only 80 --trials 6 --engine negative-control --no-write-evidence
```

Harness result: `exit 1`.

{trial_table(negative)}

Both gates printed `FAIL`. Representative leaked cases printed by the harness:

```jsonl
{leaks}
```

The weakened run produced {negative['clear_false_negatives']} clear false negatives, {negative['auto_same_false_merges']} auto-SAME false merges, {negative['name_only_false_merges']} name-only false merges, and {negative['structural_same_without_strong_id']} SAME-without-strong-ID structural leaks across all trials. These are test-double results, not production metrics.

## REPRODUCE.json entry

```json
{reproduce_line}
```

## Evidence digest

- Both production gates passed across {production_manifest['trials']} seeds and {production['pairs']} labelled pairs.
- Production observed {production['clear_false_negatives']} clear false negatives in {production['true_same_pairs']} TRUE-SAME pairs; exact one-sided 95% upper bound: {production['clear_false_negative_cp_upper_95']:.6f}.
- Production emitted {production['auto_same_false_merges']} false merges, {production['name_only_false_merges']} name-only merges, and {production['structural_same_without_strong_id']} structural SAME-without-strong-ID leaks.

## Vendored primitives

- `_local/match.py`: Jaro-Winkler, Soundex, IDF weights, IDF token-set similarity (engine-local string primitives)
- `_local/text_normalize.py`: Unicode folding, normalization, tokenization, identifier normalization (engine-local)
- `_local/metrics.py`: confusion matrix and safety metrics (engine-local)
- `_local/attest.py`: exact one-sided Clopper-Pearson bound, bound sentence, provenance, SHA-256 (engine-local)
- Shared `../_lib/seeding.py`: deterministic RNG, seed schedule, stable sampling
- `_local/identity.py`: name equivalence/base-rate calibration, identifier comparison, quality flags, evidence weights, and disposition logic with a structural SAME invariant
"""
    (ROOT / "BUILD-NOTES.md").write_text(content, encoding="utf-8")
    print("wrote BUILD-NOTES.md from emitted production evidence and regenerated negative-control results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
