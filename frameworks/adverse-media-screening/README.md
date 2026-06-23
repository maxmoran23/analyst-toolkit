# Adverse-Media Screening Framework

A runnable, deterministic engine that dispositions negative-news screening hits on
two axes — is it the right party, and is it materially adverse — clearing the
provable false positives while never auto-clearing a confirmed adverse match or an
unresolvable common-name hit.

> **In plain terms:** Negative-news screening floods analysts with articles that
> merely share a name with a customer. This engine clears the ones it can prove are
> noise — a different person (the article names someone with a different date of
> birth), an article that isn't actually negative, one where the customer is the
> victim, or ancient minor history — and escalates confirmed matches on serious
> recent wrongdoing. Crucially, a bare "John Smith" match with no identifying detail
> is **not** cleared: it might be your customer, so it goes to a person. On a
> 50,000-hit test it cut the queue ~76% while missing zero genuine adverse matches.

---

## What it produces

Per hit, a disposition (AUTO_CLEAR / ANALYST_REVIEW / ESCALATE) with an
`entity_strength` (confidence it's the right party), a `relevance` (how materially
adverse), a `combined` ranking score, and a named reason.

## Validation result (seed 42, 50,000 hits — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| Recall on genuine adverse matches (FN-safety) | **1.0000 — 0 false negatives** |
| False-positive reduction | **79.9%** |
| Human review-volume cut | **76.0%** (50,000 → 12,018 to a human) |
| Analyst queue precision lift | **4.9% → 20.5%** (~4.2×) |
| Stability | recall 1.0 across 6 seeds; FP-reduction 79.7–80.2% |
| Scale | 200,000 hits in ~6s |

Per-category clear rate: wrong_entity 100% · not_adverse 100% · low_role 100% ·
stale_immaterial 100% · common_name_ambiguous 0% (the irreducible band — common-name
matches with no identifier, left open by design). FP reduction is bounded by that
residual rather than inflated past it.

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --subjects 8000 --hits 50000
python3 run_validation.py          --seed 42 --subjects 8000 --hits 50000
```

`run_validation.py` regenerates the population in-memory, scores it, writes the
evidence pack, and **exits non-zero if any genuine adverse match is auto-cleared**.
Optional: `--trials 5`, `--hits 200000`.

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — entity resolution, relevance, disposition logic, governance. |
| [`scorer.py`](scorer.py) | The deterministic engine (reuses `../_lib/match` + `../_lib/relevance`). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded subjects + labelled media hits. |
| [`run_validation.py`](run_validation.py) | Validation harness + evidence; FN-safety gate. |
| [`tuning.md`](tuning.md) | Recalibration for a real environment. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Copilot Studio / Power Platform mapping. |
| [`evidence/`](evidence/) | Committed real-run output. |

## Standing caveat

A transparent **reference implementation** for auditability, not a production
control. `category` and `role` are taken as given here; in production they come from
an upstream media classifier whose own accuracy must be validated alongside this
engine. The category severities, role weights, and recency half-life are illustrative
and configurable. All data synthetic; nothing here screens a real person.
