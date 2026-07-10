# Methodology — NPA Product-Risk Engine

The regulator-facing specification of the new-product / new-activity (NPA)
assessment logic. Every factor, weight, band, floor, prohibited attribute, route,
and condition below exists as a named construct in [`scorer.py`](scorer.py); that
file is the executable form of this document. The evidence that the score
discriminates, is monotonic, never under-tiers a floor-triggered proposal, and
never scores around a prohibited attribute is in
[`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md). Shared
model-governance framing: [`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** Before a bank launches a new product, a committee has to
> understand how risky it is — who it serves, where, settled in what, through
> which channel, how new it is to the firm, and how attractive it would be to a
> money launderer. This engine turns a proposal's attributes into a consistent
> 0-100 score, a LOW / MEDIUM / HIGH tier, and a named approval route with the
> conditions that must be met before launch — instead of every proposal arriving
> as an ad-hoc memo. Three guarantees hold no matter what: more risk never
> produces a lower score, a proposal with a serious hard attribute (a
> sanctions-exposed market, digital-asset custody the firm has never run) can
> never be tiered LOW, and anything on the prohibited list goes straight to a
> referral — the engine will not score its way around it. The engine routes; the
> committee decides.

---

## 1. What an NPA assessment is, and how it is validated

A pre-launch product-risk tier drives which approval route a proposal takes and
which controls must be confirmed before launch. Like a customer risk rating — and
unlike a sanctions match — it has no objective "true" value; it is a calibrated
judgement. So this model is validated on the properties that matter for a rating
model rather than on accuracy against a fabricated truth:

- **Discrimination** — scores rise with designed risk.
- **Monotonicity** — worsening any single factor never lowers the score.
- **Floor safety** — a proposal carrying a floor-triggering attribute is never
  tiered LOW (the analogue of false-negative safety).
- **Prohibited routing** — a proposal carrying a prohibited attribute always
  routes REFER_PROHIBITED; there is no score at which it passes a scoring route.
- **Distribution sanity and stability** — a sensible, seed-stable tier and
  routing mix.

## 2. Inputs

Per proposal: `client_segment`, `target_jurisdictions`, `delivery_channel`,
`asset_settlement_type`, `novelty_to_firm`, `third_party_dependency`,
`data_privacy_surface` (0 minimal … 1 broad), the three fincrime-exposure inputs
(`cash_intensity` 0…1, `anonymity_features` yes/no, `cross_border_reach` 0…1),
`model_ai_reliance`, and the structural flags: `involves_custody`,
`sanctions_exposed_asset`, `new_client_segment`, `new_geography`, and the two
prohibited-list flags (`anonymity_enhanced_instrument`,
`bearer_negotiable_feature`).

## 3. Factor sub-scores (nine factors, each 0-100)

| Factor | How scored |
|---|---|
| fincrime_exposure | documented mix of product-inherent inputs: 0.40 × cash_intensity + 0.35 × anonymity_features + 0.25 × cross_border_reach, × 100 |
| jurisdiction_footprint | max bucket score over target jurisdictions; PROHIBITED 100 / SANCTIONS_EXPOSED 95 / ELEVATED 72 / STANDARD 28 / LOW 12 |
| asset_settlement_type | digital_asset 85, physical 60, derivatives 55, securities 35, fiat 25 |
| client_segment | unregulated_entity 85, non_resident 70, HNW 55, institutional 30, retail 25 |
| novelty_to_firm | new_capability 80, adjacent 45, existing 10 |
| third_party_dependency | unregulated 80, regulated 40, none 5 |
| delivery_channel | API 75, intermediated 65, online 45, branch 15 |
| model_ai_reliance | autonomous_decisioning 85, assistive 40, none 5 |
| data_privacy_surface | surface × 100 |

> The jurisdiction buckets, reference tables, and weights are **illustrative and
> configurable**. A deployment sources jurisdiction risk from its own country-risk
> methodology, current sanctions programs, and the current FATF lists (all of
> which move), and recalibrates weights against its own approval history.

## 4. Composite and bands

```
score = Σ (factor_sub_score × weight) / Σ weights        # 0-100
```

Documented weights (relative importance): fincrime_exposure 0.18,
jurisdiction_footprint 0.16, asset_settlement_type 0.13, client_segment 0.12,
novelty_to_firm 0.12, third_party_dependency 0.09, delivery_channel 0.08,
model_ai_reliance 0.07, data_privacy_surface 0.05. Fincrime exposure and
jurisdiction lead because they are the two factors a financial-crime organization
cannot remediate with launch conditions; data-privacy trails because its
condition (a named pre-launch assessment) absorbs most of the risk.

Bands: `score < 35` → **LOW**; `35 ≤ score < 60` → **MEDIUM**; `score ≥ 60` →
**HIGH**. The bands are asymmetric because the scale is not used uniformly — a
routine extension of an existing product scores very low (a typical
domestic-retail proposal ≈ 15), so HIGH begins at 60.

## 5. The prohibited list (checked first; never scored around)

A documented prohibited list dominates the routing regardless of the composite.
Checked in firing order:

1. **Prohibited-jurisdiction target market** — any target jurisdiction in the
   PROHIBITED bucket (comprehensively sanctioned).
2. **Anonymity-enhanced instrument** — mixer-integrated or privacy-coin
   settlement design.
3. **Bearer-negotiable feature** — bearer-share / bearer-negotiable instrument
   design.

Any hit → routing **REFER_PROHIBITED** (tier recorded as HIGH), no conditions
issued, no launch path, no post-launch interval. The referral goes to the policy
owner as a human action; the engine cannot be configured to score around the
list. The illustration carries three entries; a real deployment carries its full
prohibited-product register.

## 6. Mandatory floors (raise-only)

Applied after banding, in documented firing order; a floor can only raise the
tier, never lower it:

1. **Sanctions-exposed jurisdiction** (any target jurisdiction in the
   SANCTIONS_EXPOSED or PROHIBITED bucket) → at least **HIGH**.
2. **Sanctions-exposed asset** (settlement asset with documented
   sanctions-evasion exposure) → at least **HIGH**.
3. **Digital-asset custody novelty** (digital-asset settlement + the firm holds
   the asset + new capability) → at least **HIGH**.
4. **New-segment plus new-geography combination** (`new_client_segment` and
   `new_geography` together) → at least **MEDIUM** — two unknowns compound even
   when each alone is manageable.

### Why under-tiering safety is structural

Every hard attribute maps to a raise-only floor — sanctions exposure and
digital-asset custody novelty to HIGH, the segment + geography combination to at
least MEDIUM — so a proposal carrying any of them cannot be tiered LOW regardless
of how benign the rest of the profile is. The validation harness enforces this as
a build gate (count of floor-triggered proposals tiered LOW must be 0), with the
adversarial population built exactly for it: otherwise-benign profiles carrying
one buried hard attribute, where the composite alone would land most of them in
the LOW band. This is the assessment model's equivalent of the false-negative
safety the screening and monitoring frameworks enforce.

### Why the model is monotonic

The composite is a non-negative weighted sum of sub-scores, each of which is
non-decreasing in its underlying input (including the fincrime mix, itself a
non-negative weighted sum); floors only raise the tier; the prohibited gate only
escalates the routing. Therefore worsening any single factor never lowers the
score, the tier, or the routing severity. The harness verifies this by
perturbation over hundreds of random base vectors across all nine factors.

## 7. Routing map and mandatory pre-launch conditions

After the prohibited gate, the tier names the route:

| Tier | Route | Meaning |
|---|---|---|
| LOW | **STANDARD_APPROVAL** | standard approval route; conditions attach if triggered |
| MEDIUM | **ENHANCED_REVIEW** | enhanced review with conditions; second-line signoff |
| HIGH | **FULL_COMMITTEE** | full new-product committee with mandatory conditions |
| (prohibited attribute) | **REFER_PROHIBITED** | referral to the policy owner; no launch path |

Named conditions, evaluated in firing order (each cites its trigger):

1. **Sanctions screening-coverage confirmation** — any target jurisdiction
   ELEVATED or above, a sanctions-exposed asset, or cross_border_reach ≥ 0.5.
2. **Monitoring-rule coverage check** — fincrime_exposure sub-score ≥ 40.
3. **Digital-asset control review** — digital-asset settlement (wallet/custody
   controls, on-chain monitoring coverage).
4. **Third-party due-diligence completion** — unregulated third-party dependency.
5. **Model-risk validation signoff** — autonomous model/AI decisioning.
6. **Data-privacy assessment** — data_privacy_surface ≥ 0.6.
7. **Post-launch review date** — always issued; interval by tier: HIGH 90 days,
   MEDIUM 180 days, LOW 365 days.

The engine issues the conditions; confirming them, waiving them, and the approval
itself are documented committee (human) actions. The engine never approves,
blocks, or files anything.

## 8. Tunable constants

`scorer.Config`: `low_band` (35), `high_band` (60), `hard_floor` (HIGH),
`combo_floor` (MEDIUM), `fincrime_condition_threshold` (40),
`privacy_condition_threshold` (0.6), `review_days` (90/180/365). The factor
weights, reference tables, and the prohibited list are the deeper calibration
surface. Recalibration procedure in [`tuning.md`](tuning.md).

## 9. Governance and boundaries

Mapped to public guidance — SR 11-7 / OCC 2011-12 (conceptual soundness: this
document plus a readable pure-stdlib engine; outcomes analysis: the reproducible
evidence pack; ongoing monitoring: the build-gated floors and multi-seed runs;
limitations: stated in every report), the FFIEC BSA/AML Examination Manual's
expectation that new products and services be risk-assessed before launch, and
FATF Recommendation 15 (new-technology risk assessment) — per the shared
[`../GOVERNANCE.md`](../GOVERNANCE.md). The engine produces a tier, route, and
condition set that structure the approval discussion; it does not make the
launch decision, and any override of the model tier or waiver of a condition is
a documented human action (override and waiver rates are the natural
outcomes-monitoring metrics in production).
