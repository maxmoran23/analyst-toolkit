# Methodology — Customer Risk-Rating Engine

The regulator-facing specification of the rating logic. Every factor, weight, band,
and floor below exists as a named construct in [`scorer.py`](scorer.py); that file is
the executable form of this document. The evidence that the rating discriminates,
is monotonic, and never under-rates a hard-risk customer is in
[`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md). Shared
model-governance framing: [`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** Every customer gets a risk rating — LOW, MEDIUM, or HIGH —
> that decides how much due diligence and monitoring they get. This engine builds
> that rating from eight documented factors (where they're based, what business
> they're in, what products they use, how they were onboarded, and whether there
> are red flags like PEP status or prior suspicious activity), each weighted by how
> much it matters. Two guarantees hold no matter what: more risk never produces a
> lower rating, and a customer with a serious red flag can never be rated LOW. The
> engine rates; a person still makes the onboarding decision.

---

## 1. What a risk rating is, and how it is validated

A customer risk rating drives the intensity of due diligence and ongoing
monitoring. Unlike a sanctions match or a suspicious-activity finding, a rating has
no objective "true" value — it is a calibrated judgement. So this model is validated
on the properties that matter for a rating model rather than on accuracy against a
fabricated truth:

- **Discrimination** — scores rise with designed risk.
- **Monotonicity** — raising any single factor never lowers the score.
- **Floor safety** — a known-high-risk customer is never rated LOW (the analogue of
  false-negative safety).
- **Distribution sanity and stability** — a sensible, seed-stable tier mix.

---

## 2. Inputs (eight factors)

`customer_type`, `domicile_country`, `operating_countries`, `products`, `channel`
(face-to-face vs remote), `pep`, `adverse_media` (confirmed negative news),
`prior_sar`, `ownership_opacity` (0 transparent … 1 nominee/opaque), and
`expected_activity_intensity` (0 … 1 vs stated purpose).

## 3. Factor sub-scores (each 0-100)

| Factor | How scored |
|---|---|
| geography | max country-risk over domicile + operating countries; buckets HIGH 100 / ELEVATED 78 / STANDARD 25 / LOW 10 |
| products | max product risk; correspondent 92, crypto 85, cash 72, private_banking 70, trade_finance 65, wire 50, lending 25, retail_deposit 15 |
| customer_type | SHELL 90, MSB 80, NBFI 68, TRUST 60, SMB 35, CORPORATE 30, INDIVIDUAL 20 |
| negative_history | prior SAR 100, else confirmed adverse media 80, else 0 |
| pep | 100 if PEP else 0 |
| channel | REMOTE 60, FACE_TO_FACE 15 |
| ownership_opacity | opacity × 100 |
| expected_activity | intensity × 100 |

> The country buckets, product/type scores, and weights are **illustrative and
> configurable**. A deployment sources country risk from its own methodology and
> the current FATF lists (which move), and recalibrates weights against its book.

## 4. Composite and bands

```
score = Σ (factor_sub_score × weight) / Σ weights        # 0-100
```

Documented weights (relative importance): geography 0.22, products 0.18,
customer_type 0.15, negative_history 0.13, pep 0.12, channel 0.08,
ownership_opacity 0.07, expected_activity 0.05.

Bands: `score < 34` → **LOW**; `34 ≤ score < 55` → **MEDIUM**; `score ≥ 55` →
**HIGH**. The bands are asymmetric because the scale is not used uniformly — benign
customers score very low (a typical retail individual ≈ 15), so HIGH begins at 55.

## 5. Mandatory floors (raise-only)

A floor can only raise the tier, never lower it:

- **PEP** → at least **MEDIUM**.
- **High-risk-jurisdiction nexus** (domicile or operating country in the HIGH
  bucket) → at least **HIGH**.
- **Prior SAR** → at least **HIGH**.
- **Confirmed adverse media** → at least **HIGH**.
- **Opaque shell** (SHELL customer type with ownership_opacity ≥ 0.6) → at least
  **HIGH**.

### Why under-rating safety is structural

Every hard risk attribute maps to a floor — PEP to MEDIUM, all others to HIGH — so a
customer carrying any hard attribute cannot be rated LOW regardless of its composite
score. The validation harness enforces this as a build gate (count of hard-attribute
customers rated LOW must be 0). This is the rating model's equivalent of the
false-negative safety the screening and monitoring frameworks enforce.

### Why the model is monotonic

The composite is a non-negative weighted sum of sub-scores, each of which is
non-decreasing in its underlying input; floors only raise the tier. Therefore
raising any single factor never lowers the score or the tier. The harness verifies
this by perturbation over hundreds of random base vectors across all eight factors.

---

## 6. Tunable constants

`scorer.Config`: `low_band` (34), `high_band` (55), `pep_floor` (MEDIUM),
`high_risk_floor` (HIGH). The factor weights and reference tables are the deeper
calibration surface. Recalibration procedure in [`tuning.md`](tuning.md).

## 7. Governance and boundaries

Mapped to public guidance — SR 11-7 / OCC 2011-12, the FFIEC BSA/AML Examination
Manual, FATF customer-risk guidance, and Wolfsberg — per the shared
[`../GOVERNANCE.md`](../GOVERNANCE.md). The engine produces a rating that drives due
diligence and monitoring intensity; it does not make the onboarding or exit
decision, and any analyst override of the model rating is a documented human action
(an override-rate analysis is the natural outcomes-monitoring metric in production).
