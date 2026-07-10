# Customer Risk-Rating Framework

A runnable, deterministic engine that rates a customer LOW / MEDIUM / HIGH from a
documented weighted composite of eight risk factors, with mandatory floors that stop
a known-high-risk customer being rated low — validated for discrimination,
monotonicity, and floor safety.

> **In plain terms:** Every customer needs a risk rating that sets how closely
> they're watched. This engine produces one from where they operate, what they do,
> what products they use, and any red flags — and guarantees two things a regulator
> asks about: a higher-risk customer never scores lower than a lower-risk one, and a
> customer with a serious red flag (a politically exposed person, a sanctions-country
> link, a prior suspicious-activity report) can never be rated low. It produces the
> rating; a person still decides whether to take the customer on.

---

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | KYC / CDD / onboarding teams and the periodic-review function. |
| **The question it answers** | What risk rating does this customer get, and can I defend how it was reached? |
| **What it is** | A small, transparent, runnable scoring engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never onboards, exits, or off-boards a customer. A customer carrying a hard risk factor can never be rated LOW, whatever the composite score says. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/customer-risk-rating
python3 run_validation.py --seed 42 --customers 50000
```

Pure Python standard library: nothing to install, no network access, well under a second. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read the result on this page

The claim here is structural, not a hit rate: **no customer carrying a hard risk factor was rated LOW**, and worsening any single factor never lowers the score (the model is monotonic). Both are tested on every run, and the run fails if either breaks.

<!-- /STANDALONE-BRIEF -->

## What it produces

Per customer, a `Rating`: a 0-100 `score`, a `tier` (LOW / MEDIUM / HIGH), the
per-factor sub-scores, the floors applied, and a reason naming the top risk drivers
and any floor that raised the tier.

## Validation result (seed 42, 50,000 customers — see [`evidence/`](evidence/))

| Property | Result |
|---|---|
| Floor safety (hard-risk customers rated LOW) | **0 — none** (the under-rating gate) |
| Discrimination (mean score by designed stratum) | **PASS** — low 14.5 < medium 35.8 < high 55.8 |
| Monotonicity (raising any factor never lowers the score) | **PASS** — 300 random vectors × 8 factors |
| Tier distribution | LOW 66.7% · MEDIUM 18.9% · HIGH 14.5% (seed-stable) |
| Scale | 200,000 customers in ~2s |

Per designed stratum: designed_low → 100% LOW; designed_medium → LOW/MEDIUM mix;
designed_high (strong soft factors, no hard attribute) → ~66% HIGH / 34% MEDIUM;
hard_high (carries a hard attribute) → 0% LOW, floored to MEDIUM (PEP) or HIGH.

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --customers 50000
python3 run_validation.py          --seed 42 --customers 50000
```

`run_validation.py` regenerates the population in-memory, rates it, writes the
evidence pack, and **exits non-zero if any hard-risk customer is rated LOW, or
discrimination ordering fails, or monotonicity fails**. Optional: `--trials 5`,
`--customers 200000`.

Ad-hoc: `python3 scorer.py` rates four example customers.

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — factors, weights, bands, floors, governance. |
| [`scorer.py`](scorer.py) | The deterministic rating engine (pure stdlib + `../_lib/`). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded customers in designed-risk strata. |
| [`run_validation.py`](run_validation.py) | Discrimination / monotonicity / floor-safety harness + evidence. |
| [`tuning.md`](tuning.md) | Recalibration for a real environment. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Copilot Studio / Power Platform mapping. |
| [`evidence/`](evidence/) | Committed real-run output. |

## Standing caveat

A transparent **reference implementation** for auditability, not a production
control. The factor weights, country buckets, and band thresholds are illustrative —
calibrate them against your own methodology and customer base (the country buckets
must track current FATF lists). The engine rates; the onboarding/exit decision and
any override are documented human actions. All data synthetic; nothing here rates a
real customer.
