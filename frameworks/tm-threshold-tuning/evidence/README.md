# Evidence — tm-threshold-tuning

**Every file in this folder was written by a script, not by a person.** No figure here
was typed in. They are the output of one run of the validation harness over a seeded,
fully synthetic population with known ground truth.

The claim here is a floor, not an accuracy figure: **every recommended threshold still detects at least 95% of the suspicious activity**, and the run fails if any recommendation would push a rule below that line. Rules that currently leak suspicious activity below the line are recommended *down*, never up.

## Reproduce all of it

```bash
cd frameworks/tm-threshold-tuning
python3 run_validation.py --seed 42 --rules 12 --population 40000
```

Pure Python standard library — nothing to install, no network. The harness rebuilds the
population from the seed, re-scores it, recomputes every figure, and **exits non-zero if
the engine ever breaches its safety invariant**. It will overwrite this folder with
identical content.

You do not have to take that on trust either: a continuous-integration job re-derives
this pack on every change to the repository and fails the build if a single metric moves.
See [`../../../.github/workflows/validate.yml`](../../../.github/workflows/validate.yml)
and the pillar-wide index [`../../EVIDENCE.md`](../../EVIDENCE.md).

## What each file is

| File | What it contains |
|---|---|
| [`VALIDATION-REPORT.md`](VALIDATION-REPORT.md) | The report. Methodology, how the test population was built, results at the operating point, per-category performance, threshold sensitivity, the safety argument with its confidence bound, limitations, and the exact command to reproduce it. |
| [`example-atl-btl-sweep.csv`](example-atl-btl-sweep.csv) | One rule's full above/below-the-line sweep, as a worked example. |
| [`metrics.json`](metrics.json) | Every figure in the report, machine-readable, plus the run manifest. This is what the automated check compares against. |
| [`rule-recommendations.csv`](rule-recommendations.csv) | The per-rule action (raise / lower / keep), the current and recommended thresholds, and the reason. |
| [`run-manifest.json`](run-manifest.json) | The reproduction fingerprint: seed, population sizes, git commit, whether the source tree was clean, the interpreter and platform, and the wall-clock runtime. |

## Provenance of this run

| | |
|---|---|
| Seed | `42` |
| Generated at commit | `d2f4ef1` |
| Generated (UTC) | 2026-07-10 05:10 UTC |
| Wall-clock runtime | 1.27s |
| Interpreter | CPython 3.14.5 |
| Results digest | `288b273adb50c058` |

---

*Synthetic data throughout; every entity is fictional. These figures describe a reference
implementation on a constructed population — they are not a claim about live performance,
and this engine is not a production control. The limitations section of
[`VALIDATION-REPORT.md`](VALIDATION-REPORT.md) states what the evidence does not
establish.*
