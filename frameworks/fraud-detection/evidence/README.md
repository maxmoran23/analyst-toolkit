# Evidence — fraud-detection

**Every file in this folder was written by a script, not by a person.** No figure here
was typed in. They are the output of one run of the validation harness over a seeded,
fully synthetic population with known ground truth.

The symmetric claim has two gates: zero confirmed-fraud events may receive APPROVE, and zero legitimate events may receive a hard disposition. Each zero count must also place its exact one-sided 95% upper failure-rate bound at or below 0.1%.

## Reproduce all of it

```bash
cd frameworks/fraud-detection
python3 run_validation.py --seed 42 --transactions 50000 --trials 6
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
| Seed | `—` |
| Generated at commit | `—` |
| Generated (UTC) | — |
| Wall-clock runtime | —s |
| Interpreter | —  |
| Results digest | `5d6be29f53f6b9a5` |

---

*Synthetic data throughout; every entity is fictional. These figures describe a reference
implementation on a constructed population — they are not a claim about live performance,
and this engine is not a production control. The limitations section of
[`VALIDATION-REPORT.md`](VALIDATION-REPORT.md) states what the evidence does not
establish.*
