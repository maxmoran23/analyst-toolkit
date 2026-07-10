# Evidence — jurisdiction-risk

**Every file in this folder was written by a script, not by a person.** No figure here
was typed in. They are the output of one run of the validation harness over a seeded,
fully synthetic population with known ground truth.

The claim here is structural, not a hit rate: **no jurisdiction carrying a hard-risk designation was ever rated below its mandated floor** — a comprehensive sanctions program or a FATF black listing forces CRITICAL, and a FATF grey listing, an EU high-risk designation, or an INCSR primary-concern listing forces at least HIGH — the score discriminates cleanly across the designed-risk strata, and raising any dimension never lowers the score (the model is monotonic). All three are tested on every run, and the run fails if any breaks.

## Reproduce all of it

```bash
cd frameworks/jurisdiction-risk
python3 run_validation.py --seed 42 --jurisdictions 40000
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
| [`metrics.json`](metrics.json) | Every figure in the report, machine-readable, plus the run manifest. This is what the automated check compares against. |
| [`run-manifest.json`](run-manifest.json) | The reproduction fingerprint: seed, population sizes, git commit, whether the source tree was clean, the interpreter and platform, and the wall-clock runtime. |
| [`stratum-scores.csv`](stratum-scores.csv) | Mean score by designed risk stratum — evidence the engine discriminates between low, medium, and high risk. |
| [`tier-distribution.csv`](tier-distribution.csv) | How the population distributes across the rating tiers. |

## Provenance of this run

| | |
|---|---|
| Seed | `42` |
| Generated at commit | `1afa8a7` |
| Generated (UTC) | 2026-07-10 21:18 UTC |
| Wall-clock runtime | 0.59s |
| Interpreter | CPython 3.14.5 |
| Results digest | `b309d40e9ecc163b` |

---

*Synthetic data throughout; every entity is fictional. These figures describe a reference
implementation on a constructed population — they are not a claim about live performance,
and this engine is not a production control. The limitations section of
[`VALIDATION-REPORT.md`](VALIDATION-REPORT.md) states what the evidence does not
establish.*
