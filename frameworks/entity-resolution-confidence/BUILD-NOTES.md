# Build Notes

Generated from harness evidence by `generate_build_notes.py`; reported counts are not hand-entered.

## Passing validation console transcript

Command:

```bash
python3 run_validation.py --seed 42 --same 160 --different 240 --name-only 80 --trials 6
```

Console (`exit 0`):

```text
engine=production unit_tests=11 seed=42 trials=6
seed  pairs  true_same  clear_FN  false_merges  name_only_merges  structural_leaks  gate
  42    480        160         0             0                 0                 0  PASS
  43    480        160         0             0                 0                 0  PASS
  44    480        160         0             0                 0                 0  PASS
  45    480        160         0             0                 0                 0  PASS
  46    480        160         0             0                 0                 0  PASS
  47    480        160         0             0                 0                 0  PASS
false_negative_gate=PASS
false_merge_gate=PASS
Observed 0 clear false negatives in 960 labelled TRUE-SAME pairs; the exact one-sided 95% Clopper-Pearson upper bound is 0.003116. This bound is a property of the validation sample size, not a claim of a zero population rate.
VALIDATION: PASS
```

## Multi-seed stability

| Seed | Pairs | TRUE-SAME | Clear FN | False merges | Name-only merges | Structural leaks | Gate |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 42 | 480 | 160 | 0 | 0 | 0 | 0 | PASS |
| 43 | 480 | 160 | 0 | 0 | 0 | 0 | PASS |
| 44 | 480 | 160 | 0 | 0 | 0 | 0 | PASS |
| 45 | 480 | 160 | 0 | 0 | 0 | 0 | PASS |
| 46 | 480 | 160 | 0 | 0 | 0 | 0 | PASS |
| 47 | 480 | 160 | 0 | 0 | 0 | 0 | PASS |

Observed 0 clear false negatives in 960 labelled TRUE-SAME pairs; the exact one-sided 95% Clopper-Pearson upper bound is 0.003116. This bound is a property of the validation sample size, not a claim of a zero population rate.

## Proof the gates are real

`negative_control_scorer.py` deliberately introduces both forbidden behaviors: romanization differences can clear a true match, and exact common names can auto-merge without an identifier.

```bash
python3 run_validation.py --seed 42 --same 160 --different 240 --name-only 80 --trials 6 --engine negative-control --no-write-evidence
```

Harness result: `exit 1`.

| Seed | Pairs | TRUE-SAME | Clear FN | False merges | Name-only merges | Structural leaks | Gate |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 42 | 480 | 160 | 59 | 51 | 27 | 83 | FAIL |
| 43 | 480 | 160 | 59 | 51 | 27 | 83 | FAIL |
| 44 | 480 | 160 | 59 | 51 | 27 | 83 | FAIL |
| 45 | 480 | 160 | 59 | 51 | 27 | 83 | FAIL |
| 46 | 480 | 160 | 59 | 51 | 27 | 83 | FAIL |
| 47 | 480 | 160 | 59 | 51 | 27 | 83 | FAIL |

Both gates printed `FAIL`. Representative leaked cases printed by the harness:

```jsonl
{"category": "different_romanization_shared_passport", "disposition": "DIFFERENT", "label": "SAME", "pair_id": "S-00092", "reason": "UNSAFE: romanization mismatch treated as identity contradiction"}
{"category": "distinct_common_name_name_only", "disposition": "SAME", "label": "DIFFERENT", "pair_id": "N-00026", "reason": "UNSAFE: exact common name auto-merged"}
```

The weakened run produced 354 clear false negatives, 306 auto-SAME false merges, 162 name-only false merges, and 498 SAME-without-strong-ID structural leaks across all trials. These are test-double results, not production metrics.

## REPRODUCE.json entry

```json
{"audience":"financial-crime analysts and independent validators","command":"python3 run_validation.py --seed 42 --same 160 --different 240 --name-only 80 --trials 6","kind":"offline synthetic dual-safety-gate validation","never":"treat name similarity or synthetic metrics as proof of identity","question":"Does the resolver avoid clear false negatives and structurally prevent name-only false merges across six deterministic seeds?"}
```

## Evidence digest

- Both production gates passed across 6 seeds and 2880 labelled pairs.
- Production observed 0 clear false negatives in 960 TRUE-SAME pairs; exact one-sided 95% upper bound: 0.003116.
- Production emitted 0 false merges, 0 name-only merges, and 0 structural SAME-without-strong-ID leaks.

## Vendored primitives

- `_local/match.py`: Jaro-Winkler, Soundex, IDF weights, IDF token-set similarity (engine-local string primitives)
- `_local/text_normalize.py`: Unicode folding, normalization, tokenization, identifier normalization (engine-local)
- `_local/metrics.py`: confusion matrix and safety metrics (engine-local)
- `_local/attest.py`: exact one-sided Clopper-Pearson bound, bound sentence, provenance, SHA-256 (engine-local)
- Shared `../_lib/seeding.py`: deterministic RNG, seed schedule, stable sampling
- `_local/identity.py`: name equivalence/base-rate calibration, identifier comparison, quality flags, evidence weights, and disposition logic with a structural SAME invariant
