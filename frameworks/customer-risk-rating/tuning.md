# Tuning — recalibrating the rating

The factor weights, reference tables (country buckets, product and customer-type
scores), and band thresholds are **illustrative**. A risk rating is a calibrated
judgement specific to an institution's risk appetite and customer base — recalibrate
before relying on the engine, and record every change.

> **In plain terms:** The settings below decide how much each factor counts and
> where the LOW/MEDIUM/HIGH lines fall. Tune them so the resulting distribution
> matches your risk appetite and the way your experts would rate a sample of real
> customers — and write down the rationale.

## The calibration surface

| Surface | Where | Effect |
|---|---|---|
| Factor weights | `WEIGHTS` in `scorer.py` | Relative importance of each factor; normalized, so read each as a share. |
| Country buckets | `COUNTRY_TIER` / `COUNTRY_BUCKET_SCORE` | Which jurisdictions are HIGH/ELEVATED/STANDARD/LOW. **Must track current FATF lists.** |
| Product / type scores | `PRODUCT_RISK` / `CUSTOMER_TYPE_RISK` | Inherent risk of each product and customer type. |
| Bands | `Config.low_band` / `high_band` | Where the tier lines fall on the 0-100 composite. |
| Floors | `_floors()` + `Config.pep_floor` / `high_risk_floor` | Which attributes force a minimum tier. |

## Procedure

1. **Assemble an expert-rated sample** — a few hundred real customers your team has
   rated, spanning the risk spectrum. This is the calibration target.
2. **Fit the bands** so the engine's tier distribution matches your risk appetite
   and the expert ratings (the model-vs-expert disagreement rate is your
   override-rate estimate). Keep benign customers scoring low and reserve HIGH for
   genuinely elevated profiles.
3. **Set the country buckets** from your country-risk methodology and the current
   FATF high-risk and increased-monitoring lists. This is the most time-sensitive
   table — review it on the FATF update cadence.
4. **Confirm the floors** match your policy (which attributes are auto-HIGH vs
   auto-MEDIUM). The floors are the safety net; keep them at least as conservative
   as policy requires.
5. **Re-run the validation gate** after any change: discrimination must still hold,
   monotonicity must still pass, and no hard-risk customer may be rated LOW.
6. **Record** the change, old/new values, the expert-sample result before and after,
   and the rationale — the model-change-management evidence.

## What not to do

- Do not weaken a floor to reduce the HIGH population — the floors are the
  under-rating protection.
- Do not let the country buckets go stale; an out-of-date FATF mapping is a common
  exam finding.
- Do not treat the illustrative weights as validated — they are a starting point,
  fit to a synthetic distribution, not your book.
- Keep weights non-negative and the per-factor sub-scores monotone in risk, or the
  monotonicity guarantee (and its gate) breaks.
