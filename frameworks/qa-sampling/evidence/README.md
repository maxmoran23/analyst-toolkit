# Evidence — qa-sampling

**Every file in this folder was written by a script, not by a person.** No figure here
was typed in. They are the output of one run of the validation harness over a seeded,
fully synthetic population with known ground truth.

The claim here is exactness, not accuracy: the sample size and the upper deviation limit are **computed from exact binomial and hypergeometric tail probabilities**, not read off a lookup table, and each is cross-checked against an independent brute-force computation on every run.

## Reproduce all of it

```bash
cd frameworks/qa-sampling
python3 run_validation.py --seed 42 --controls 12 --population 40000
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
| [`control-conclusions.csv`](control-conclusions.csv) | Per-control sample plan, deviations found, and the exact statistical conclusion. |
| [`metrics.json`](metrics.json) | Every figure in the report, machine-readable, plus the run manifest. This is what the automated check compares against. |
| [`run-manifest.json`](run-manifest.json) | The reproduction fingerprint: seed, population sizes, git commit, whether the source tree was clean, the interpreter and platform, and the wall-clock runtime. |
| [`sample-size-sweep.csv`](sample-size-sweep.csv) | Required sample size across confidence levels and tolerable deviation rates. |
| [`selection-log.csv`](selection-log.csv) | The reproducible sample selection — which items were drawn, from which seed. |
| [`udl-crosscheck.csv`](udl-crosscheck.csv) | The upper-deviation-limit computed two independent ways, per case. Values sit at the 1e-12 level and are round-off diagnostics; the committed claim is that they agree within a 1e-9 tolerance. |

## Provenance of this run

| | |
|---|---|
| Seed | `42` |
| Generated at commit | `531971e` |
| Generated (UTC) | 2026-07-10 05:15 UTC |
| Wall-clock runtime | 0.47s |
| Interpreter | CPython 3.14.5 |
| Results digest | `ffe79786d6a40587` |

---

*Synthetic data throughout; every entity is fictional. These figures describe a reference
implementation on a constructed population — they are not a claim about live performance,
and this engine is not a production control. The limitations section of
[`VALIDATION-REPORT.md`](VALIDATION-REPORT.md) states what the evidence does not
establish.*
