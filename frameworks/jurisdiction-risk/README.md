# Jurisdiction-Risk Framework

A runnable, deterministic engine that rates a country or territory's inherent
financial-crime risk on a 0-100 scale and a LOW / MEDIUM / HIGH / CRITICAL tier, by
compositing seven recognized public-index dimensions under a documented weighting —
and applying hard-risk overrides that a flattering index can never talk down.

> **In plain terms:** Geographic risk is one of the most-used inputs in AML — it sets
> EDD scope, correspondent risk, and the country layer of an enterprise risk
> assessment — and it is usually done by eyeballing a couple of lists. This engine
> composites the recognized public indices (FATF status, Basel AML Index, corruption,
> governance, secrecy, organized crime, terrorism, instability) into one score with the
> weighting written out, then applies floors: a comprehensively-sanctioned or
> FATF-black-listed jurisdiction is CRITICAL no matter what the other indices say, and a
> FATF-grey / EU-high-risk / INCSR-primary jurisdiction is at least HIGH. On a 40,000
> synthetic-jurisdiction test the score separates cleanly by designed risk, and **no
> hard-designated jurisdiction was ever rated below its mandated floor.**

---

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | Financial-crime risk teams setting geographic risk ratings, and the correspondent-banking, EDD, and enterprise-risk-assessment functions that consume them. |
| **The question it answers** | How much inherent financial-crime risk does this jurisdiction carry, and can I show how the score was reached? |
| **What it is** | A small, transparent, runnable scoring engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never decides whether to enter, exit, bank, or de-risk a market, and it is not a political judgement about a country. It composites public indices into a documented, floored rating and hands the reasoning to a human. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/jurisdiction-risk
python3 run_validation.py --seed 42 --jurisdictions 40000
```

Pure Python standard library: nothing to install, no network access, well under a second. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read the result on this page

The claim here is structural, not a hit rate: **no jurisdiction carrying a hard-risk designation was ever rated below its mandated floor** — a comprehensive sanctions program or a FATF black listing forces CRITICAL, and a FATF grey listing, an EU high-risk designation, or an INCSR primary-concern listing forces at least HIGH — the score discriminates cleanly across the designed-risk strata, and raising any dimension never lowers the score (the model is monotonic). All three are tested on every run, and the run fails if any breaks.

<!-- /STANDALONE-BRIEF -->

## What it produces

Per jurisdiction, a 0-100 composite `score`, a `tier` (LOW / MEDIUM / HIGH / CRITICAL),
the per-dimension sub-scores, the `floors_applied` (which categorical designations
raised the tier), the count of dimensions the score rests on, and a named `reason`.

## Validation result (seed 42, 40,000 jurisdictions — see [`evidence/`](evidence/))

| Property | Result |
|---|---|
| Discrimination (mean score rises across designed strata) | **PASS** — designed_low 18.9 < designed_medium 45.4 < designed_high 72.6 |
| Floor safety — sanctioned / FATF-black rated below CRITICAL | **0** (must be 0) |
| Floor safety — FATF-grey / EU-high-risk / INCSR-primary rated below HIGH | **0** (must be 0) |
| Monotonicity (raising any dimension never lowers the score) | **PASS** — 300 random base vectors × 7 dimensions |
| Determinism | identical results digest across repeated runs |

The exact figures, the per-stratum table, and the tier distribution are emitted to
[`evidence/`](evidence/); this page never hand-authors a number the harness computes.

## Run it

```bash
cd frameworks/jurisdiction-risk
python3 run_validation.py --seed 42 --jurisdictions 40000
```

Pure Python standard library — nothing to install, no network access, about a second.
It prints the discrimination, floor-safety, and monotonicity results and writes the
evidence pack. It exits non-zero — failing the build — if any hard-designated
jurisdiction is rated below its floor, discrimination ordering breaks, or monotonicity
breaks.

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The spec — the seven dimensions, their normalization from raw indices, the weighting, the tier bands, the hard-risk floors, and governance. |
| [`SOURCE-LIBRARY.md`](SOURCE-LIBRARY.md) | Where each dimension is drawn from: the tiered public-index whitelist, editions and cadence, and retrieval discipline. |
| [`scorer.py`](scorer.py) | The deterministic engine (reuses `../_lib/scoring`). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded fictional jurisdictions across five designed-risk strata. |
| [`run_validation.py`](run_validation.py) | Validation harness + evidence; the discrimination, floor-safety, and monotonicity gates. |
| [`tuning.md`](tuning.md) | Recalibration for a real methodology — weights, bands, and dimension set. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Copilot Studio / Power Platform mapping. |
| [`evidence/`](evidence/) | Committed real-run output. |

## Standing caveat

The engine rates **inherent geographic risk** — it does not decide whether to enter,
exit, bank, or de-risk a market, and it is not a political judgement about a country or
its people. Every jurisdiction in the test population is fictional. The dimension
weights and band thresholds are illustrative and must be calibrated to a firm's own
methodology; the categorical designations move over time and must be refreshed against
the authoritative source at time of use. A qualified human owns any action taken on a
rating. The paste-in analyst sibling of this engine is
[`../../prompts/compliance/jurisdiction-risk-osint.md`](../../prompts/compliance/jurisdiction-risk-osint.md).
