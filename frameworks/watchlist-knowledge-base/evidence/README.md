# Evidence — watchlist-knowledge-base

**Every file in this folder was written by a script, not by a person.** No figure here
was typed in. They are the output of one run of the validation harness over a seeded,
fully synthetic population with known ground truth.

The claim here is structural: **zero false merges**. Combining two genuinely different designated parties would erase a designation, so the run fails outright if it ever happens — it is a build gate, not a score.

## Reproduce all of it

```bash
cd frameworks/watchlist-knowledge-base
python3 run_validation.py --seed 42 --entities 3000
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
| [`resolved-sample.csv`](resolved-sample.csv) | A sample of the resolved, deduplicated watchlist entities. |
| [`run-manifest.json`](run-manifest.json) | The reproduction fingerprint: seed, population sizes, git commit, whether the source tree was clean, the interpreter and platform, and the wall-clock runtime. |

## Provenance of this run

| | |
|---|---|
| Seed | `42` |
| Generated at commit | `d2f4ef1` |
| Generated (UTC) | 2026-07-10 05:10 UTC |
| Wall-clock runtime | 0.31s |
| Interpreter | CPython 3.14.5 |
| Results digest | `a6357027fa3d0ea7` |

---

*Synthetic data throughout; every entity is fictional. These figures describe a reference
implementation on a constructed population — they are not a claim about live performance,
and this engine is not a production control. The limitations section of
[`VALIDATION-REPORT.md`](VALIDATION-REPORT.md) states what the evidence does not
establish.*
