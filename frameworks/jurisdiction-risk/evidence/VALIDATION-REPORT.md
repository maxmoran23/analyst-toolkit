# Validation Report — Jurisdiction-Risk Framework

> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the reference engine over a seeded, fully synthetic population of FICTIONAL jurisdictions. No real country is represented or rated. Numbers are emitted by `run_validation.py`, not authored.

**Run:** seed `42` · 40,000 jurisdictions · git `3312293` · 2026-07-10 21:08 UTC

**Headline:** discrimination PASS (mean score rises across designed strata), floor safety **0 below CRITICAL and 0 below HIGH** among hard-designated jurisdictions, monotonicity PASS.

## 1. Methodology summary
The engine rates each jurisdiction LOW / MEDIUM / HIGH / CRITICAL from a documented weighted composite of seven public-index dimensions (AML/CFT, corruption, governance, secrecy, organized crime, terrorism, instability), with mandatory floors driven by categorical designations: a comprehensive sanctions program or a FATF black list forces CRITICAL; a FATF grey list, an EU high-risk-third-country listing, or an INCSR primary-concern listing forces at least HIGH. It rates inherent geographic risk; it does not make the market or onboarding decision. Full spec: `METHODOLOGY.md`; sources: `SOURCE-LIBRARY.md`.

## 2. Synthetic-population construction
40,000 fictional jurisdictions across five designed strata. The stratum is assigned from the construction, independent of the engine's weighted formula, so agreement is a real test, not a tautology. The two hard strata carry a categorical designation with moderate soft dimensions, so the floor — not the composite — is what must lift the tier; they are the safety population.

## 3. Rating distribution
| Tier | Count | Share |
| --- | --- | --- |
| LOW | 12,041 | 30.1% |
| MEDIUM | 11,959 | 29.9% |
| HIGH | 12,765 | 31.9% |
| CRITICAL | 3,235 | 8.1% |

## 4. Discrimination by designed stratum
Mean score must rise across designed_low → designed_medium → designed_high. The hard strata are validated by the floor gate below, not by score ordering.

| stratum | count | mean_score | LOW | MEDIUM | HIGH | CRITICAL |
| --- | --- | --- | --- | --- | --- | --- |
| designed_low | 12000 | 18.85 | 12000 | 0 | 0 | 0 |
| designed_medium | 12000 | 45.39 | 41 | 11959 | 0 | 0 |
| designed_high | 8000 | 72.64 | 0 | 0 | 7965 | 35 |
| hard_high | 4800 | 41.02 | 0 | 0 | 4800 | 0 |
| hard_critical | 3200 | 49.26 | 0 | 0 | 0 | 3200 |

Discrimination ordering (soft strata): **PASS**.

## 5. Floor-rule safety (the under-rating gate)
Hard-designated jurisdictions rated below their mandated floor — the analogue of false-negative safety, enforced structurally and as a build gate:

- Comprehensively-sanctioned or FATF-black-listed rated below CRITICAL: **0** (must be 0).
- FATF-grey / EU-high-risk / INCSR-primary rated below HIGH: **0** (must be 0).

A flattering index can never talk a designated jurisdiction below its floor: the floor is applied as the worse of the weighted tier and the mandated minimum.

## 6. Monotonicity property test
Raising any single dimension sub-score never lowers the composite — tested over 300 random base vectors across all 7 dimensions: **PASS**. Monotonicity is a structural property of the non-negative weighted sum and the raise-only floors.

## 7. Limitations
- A risk rating is a judgement; there is no objective true tier, so this validates discrimination, floor safety, and monotonicity rather than tier accuracy against a fabricated truth.
- The dimension weights and band thresholds are ILLUSTRATIVE. Calibrate them against your own geographic-risk methodology (`tuning.md`).
- The categorical designations (FATF, EU, INCSR, sanctions) move over time. A deployment must refresh them against the authoritative source at time of use (`SOURCE-LIBRARY.md`); the engine applies whatever it is given.
- The engine rates inherent geographic risk; the market/onboarding decision and any override are human, documented actions. It is not a judgement about a country or its people.

## 8. Reproduction
```bash
python3 run_validation.py --seed 42 --jurisdictions 40000
```
