# Evidence — adverse-media-screening

**Every file in this folder was written by a script, not by a person.** No figure here
was typed in. They are the output of one run of the validation harness over a seeded,
fully synthetic population with known ground truth.

The engine missed **0** of the **2,468** materially adverse true hits planted in the test population. As with an attribute sample returning zero exceptions, that bounds the miss rate rather than proving it is nil: **below 0.12% at 95% confidence**, on this synthetic population.

## Reproduce all of it

```bash
cd frameworks/adverse-media-screening
python3 run_validation.py --seed 42 --subjects 8000 --hits 50000
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
| [`confusion-matrix.csv`](confusion-matrix.csv) | True positives, false positives, true negatives, false negatives at the deployed operating point. |
| [`metrics.json`](metrics.json) | Every figure in the report, machine-readable, plus the run manifest. This is what the automated check compares against. |
| [`run-manifest.json`](run-manifest.json) | The reproduction fingerprint: seed, population sizes, git commit, whether the source tree was clean, the interpreter and platform, and the wall-clock runtime. |
| [`threshold-sweep.csv`](threshold-sweep.csv) | How recall, precision, and cleared volume move as the threshold is swept — evidence the operating point sits on a plateau rather than a cliff edge. |

## Provenance of this run

| | |
|---|---|
| Seed | `42` |
| Generated at commit | `d2f4ef1` |
| Generated (UTC) | 2026-07-10 05:09 UTC |
| Wall-clock runtime | 1.15s |
| Interpreter | CPython 3.14.5 |
| Results digest | `c8c6d4a94091abf7` |

---

*Synthetic data throughout; every entity is fictional. These figures describe a reference
implementation on a constructed population — they are not a claim about live performance,
and this engine is not a production control. The limitations section of
[`VALIDATION-REPORT.md`](VALIDATION-REPORT.md) states what the evidence does not
establish.*
