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
