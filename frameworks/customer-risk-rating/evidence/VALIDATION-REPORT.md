# Validation Report — Customer Risk-Rating Framework

> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the reference engine over a seeded, fully synthetic customer population. No real customer is represented. Numbers are emitted by `run_validation.py`, not authored.

**Run:** seed `42` · 50,000 customers · git `d2f4ef1` · 2026-07-10 05:09 UTC

**Headline:** discrimination PASS (mean score rises across designed strata), floor safety **0 hard-risk customers rated LOW**, monotonicity PASS.

## 1. Methodology summary
The engine rates each customer LOW / MEDIUM / HIGH from a documented weighted composite of eight risk factors, with mandatory floors (a PEP can never be LOW; a sanctions/high-risk-jurisdiction nexus, a prior SAR, confirmed adverse media, or an opaque shell force at least HIGH). It rates; it does not make the onboarding decision. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
50,000 customers across four designed-risk strata. The stratum is assigned from attribute presence and is independent of the engine's weighted formula, so agreement is a real test, not a tautology. The hard_high stratum carries a hard risk attribute and is the safety population.

## 3. Rating distribution
| Tier | Count | Share |
| --- | --- | --- |
| LOW | 33,329 | 66.7% |
| MEDIUM | 9,448 | 18.9% |
| HIGH | 7,223 | 14.4% |

## 4. Discrimination by designed stratum
Mean score must rise across designed_low → designed_medium → designed_high, and the hard_high stratum must concentrate in MEDIUM/HIGH (never LOW).

| stratum | count | mean_score | LOW | MEDIUM | HIGH |
| --- | --- | --- | --- | --- | --- |
| designed_low | 27649 | 14.52 | 27649 | 0 | 0 |
| designed_medium | 12427 | 35.77 | 5680 | 6747 | 0 |
| designed_high | 5956 | 55.84 | 0 | 2017 | 3939 |
| hard_high | 3968 | 46.9 | 0 | 684 | 3284 |

Discrimination ordering: **PASS**.

## 5. Floor-rule safety (the under-rating gate)
Customers carrying a hard risk attribute rated LOW: **0** (must be 0). This is the rating analogue of false-negative safety, enforced structurally by the floor rules and as a build gate — a PEP floors to MEDIUM, every other hard attribute floors to HIGH, so no hard-risk customer can be rated LOW regardless of its other factors.

designed_high (soft factors only) rated LOW: 0 (expected ~0 from the composite alone).

## 6. Monotonicity property test
Raising any single factor sub-score never lowers the composite — tested over 300 random base vectors across all 8 factors: **PASS**. Monotonicity is a structural property of the non-negative weighted sum and the raise-only floors.

## 7. Limitations
- A risk rating is a judgement; there is no objective true tier, so this validates discrimination, safety, and monotonicity rather than tier accuracy against a fabricated truth.
- The factor weights, country buckets, and band thresholds are ILLUSTRATIVE. Calibrate them against your own methodology and customer base (`tuning.md`); the country buckets in particular must track current FATF lists.
- The engine rates; the onboarding / exit decision and any override are human, documented actions.

## 8. Reproduction
```bash
python3 run_validation.py --seed 42 --customers 50000
```
