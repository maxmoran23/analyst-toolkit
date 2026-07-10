# Validation Report — NPA Product-Risk Framework

> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the reference engine over a seeded, fully synthetic population of product proposals at the fictional Harborview Financial Group. No real product or institution is represented. Numbers are emitted by `run_validation.py`, not authored.

**Run:** seed `42` · 50,000 product proposals · git `d2f4ef1` · 2026-07-10 05:09 UTC

**Headline:** discrimination PASS (mean score rises across designed strata), floor safety **0 floor-triggered products tiered LOW**, prohibited routing **0 of 3,046 prohibited proposals routed past REFER_PROHIBITED**, monotonicity PASS.

## 1. Methodology summary
The engine scores each product / activity proposal 0-100 from a documented weighted composite of nine risk factors, tiers it LOW / MEDIUM / HIGH, and routes it to a named approval route with named mandatory pre-launch conditions and a post-launch review interval. Mandatory floors are raise-only (a sanctions-exposed jurisdiction or asset, or digital-asset custody the firm has never operated, force at least HIGH; a new client segment combined with a new geography forces at least MEDIUM), and a documented prohibited list is never scored around (REFER_PROHIBITED). The engine routes; the approval decision is the committee's. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
50,000 proposals across five designed-risk strata. The stratum is assigned from attribute presence and is independent of the engine's weighted formula, so agreement is a real test, not a tautology. The hard_high stratum is the adversarial safety population: an otherwise-benign profile carrying ONE buried floor-triggering attribute, so the composite alone would tier most of them LOW — the floor has to catch every one. The prohibited stratum carries a documented prohibited attribute and must always route REFER_PROHIBITED.

## 3. Tier and routing distribution
| Tier | Count | Share |
| --- | --- | --- |
| LOW | 24,615 | 49.2% |
| MEDIUM | 12,761 | 25.5% |
| HIGH | 12,624 | 25.2% |

| Routing | Count | Share |
| --- | --- | --- |
| STANDARD_APPROVAL | 24,615 | 49.2% |
| ENHANCED_REVIEW | 12,761 | 25.5% |
| FULL_COMMITTEE | 9,578 | 19.2% |
| REFER_PROHIBITED | 3,046 | 6.1% |

## 4. Discrimination by designed stratum
Mean score must rise across designed_low → designed_medium → designed_high. hard_high is deliberately benign apart from its buried hard attribute, so its mean score sits low — it is judged by the floor gate (never LOW), not by score ordering; prohibited is judged by the routing gate.

| stratum | count | mean_score | LOW | MEDIUM | HIGH |
| --- | --- | --- | --- | --- | --- |
| designed_low | 22367 | 17.33 | 22367 | 0 | 0 |
| designed_medium | 13556 | 39.82 | 2248 | 11308 | 0 |
| designed_high | 6062 | 68.58 | 0 | 232 | 5830 |
| hard_high | 4969 | 30.67 | 0 | 1221 | 3748 |
| prohibited | 3046 | 30.9 | 0 | 0 | 3046 |

Discrimination ordering: **PASS**.

## 5. Floor-rule safety (the under-rating gate)
Floor-triggered (hard_high) proposals tiered LOW: **0** (must be 0). Structural double-check over the whole population — proposals with any floor applied that still ended LOW: **0** (must be 0). This is the assessment analogue of false-negative safety: every hard attribute maps to a raise-only floor (sanctions exposure and digital-asset custody novelty to HIGH, the new-segment + new-geography combination to at least MEDIUM), so a proposal carrying one cannot be tiered LOW regardless of how benign the rest of the profile is.

## 6. Prohibited-attribute gate (never scored around)
Prohibited-stratum proposals: 3,046; routed anywhere other than REFER_PROHIBITED: **0** (must be 0). Engine-detected prohibited attributes misrouted: **0** (must be 0). A prohibited attribute dominates the routing regardless of the composite score — there is no score at which the engine will pass one through a scoring route.

## 7. Monotonicity property test
Raising any single factor sub-score never lowers the composite — tested over 300 random base vectors across all 9 factors: **PASS**. Monotonicity is a structural property of the non-negative weighted sum and the raise-only floors.

## 8. Limitations
- A pre-launch product-risk tier is a judgement; there is no objective true tier, so this validates discrimination, floor safety, prohibited routing, and monotonicity rather than tier accuracy against a fabricated truth.
- The factor weights, jurisdiction buckets, reference tables, and band thresholds are ILLUSTRATIVE. Calibrate them against your own product-approval methodology and history (`tuning.md`); the jurisdiction buckets in particular must track current sanctions programs and FATF lists.
- The engine tiers and routes; the approval decision, any conditions waiver, and any override are human, documented committee actions. It never approves, blocks, or files anything.
- The prohibited list here is a three-item illustration; a real deployment carries its institution's full prohibited-product register.

## 9. Reproduction
```bash
python3 run_validation.py --seed 42 --products 50000
```
