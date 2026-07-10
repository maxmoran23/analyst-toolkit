# Evidence — onchain-osint-evidence

**Every file in this folder was written by a script, not by a person.** No figure here
was typed in. They are the output of one run of the validation harness over a seeded,
fully synthetic population with known ground truth.

The claim here is evidentiary, not statistical: **every captured fact carries its source, retrieval time, and a hash of the exact bytes**; the totals reconcile to the captures with nothing dropped or double-counted; and the same captures re-render byte-for-byte identically months later.

## Reproduce all of it

```bash
cd frameworks/onchain-osint-evidence
python3 run_validation.py --seed 42 --addresses 400 --transactions 50000
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
| [`annex-sample.md`](annex-sample.md) | A rendered sample of the provenance-stamped evidence annex the engine produces. |
| [`metrics.json`](metrics.json) | Every figure in the report, machine-readable, plus the run manifest. This is what the automated check compares against. |
| [`reconciliation.csv`](reconciliation.csv) | Tie-out of every captured fact to its source, proving nothing was dropped or double-counted. |
| [`run-manifest.json`](run-manifest.json) | The reproduction fingerprint: seed, population sizes, git commit, whether the source tree was clean, the interpreter and platform, and the wall-clock runtime. |

## Provenance of this run

| | |
|---|---|
| Seed | `42` |
| Generated at commit | `d2f4ef1` |
| Generated (UTC) | 2026-07-10 05:09 UTC |
| Wall-clock runtime | 3.46s |
| Interpreter | CPython 3.14.5 |
| Results digest | `23f2f8c77e1c3737` |

---

*Synthetic data throughout; every entity is fictional. These figures describe a reference
implementation on a constructed population — they are not a claim about live performance,
and this engine is not a production control. The limitations section of
[`VALIDATION-REPORT.md`](VALIDATION-REPORT.md) states what the evidence does not
establish.*
