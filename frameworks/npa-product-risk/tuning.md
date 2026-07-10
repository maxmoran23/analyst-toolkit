# Tuning — recalibrating the assessment

The factor weights, reference tables (jurisdiction buckets, segment / channel /
asset / novelty / third-party / model-reliance scores), band thresholds, condition
triggers, and the prohibited list are **illustrative**. A pre-launch product-risk
tier is a calibrated judgement specific to an institution's risk appetite,
product strategy, and approval history — recalibrate before relying on the
engine, and record every change.

> **In plain terms:** The settings below decide how much each factor counts,
> where the LOW/MEDIUM/HIGH lines fall, and which attributes force a floor or a
> referral. Tune them so the resulting routing mix matches your risk appetite and
> the way your committee actually disposed of a sample of past proposals — and
> write down the rationale.

## The calibration surface

| Surface | Where | Effect |
|---|---|---|
| Factor weights | `WEIGHTS` in `scorer.py` | Relative importance of each factor; normalized, so read each as a share. |
| Jurisdiction buckets | `JURISDICTION_BUCKET` / `JURISDICTION_BUCKET_SCORE` | Which jurisdictions are PROHIBITED / SANCTIONS_EXPOSED / ELEVATED / STANDARD / LOW. **Must track current sanctions programs and FATF lists.** |
| Reference tables | `CLIENT_SEGMENT_RISK`, `ASSET_SETTLEMENT_RISK`, `DELIVERY_CHANNEL_RISK`, `NOVELTY_RISK`, `THIRD_PARTY_RISK`, `MODEL_AI_RISK`, `FINCRIME_MIX` | Inherent risk of each attribute value; the fincrime mix weights its three inputs. |
| Bands | `Config.low_band` / `high_band` | Where the tier lines fall on the 0-100 composite. |
| Floors | `_floors()` + `Config.hard_floor` / `combo_floor` | Which attributes force a minimum tier. |
| Prohibited list | `prohibited_attributes()` | Which attributes bypass scoring entirely. Extend to your full prohibited-product register. |
| Condition triggers | `_conditions()` + `Config.fincrime_condition_threshold` / `privacy_condition_threshold` / `review_days` | Which pre-launch conditions attach, and the post-launch review cadence. |

## Procedure

1. **Assemble a committee-disposed sample** — a few dozen to a few hundred past
   proposals with their actual routes, conditions, and outcomes. This is the
   calibration target.
2. **Fit the bands** so the engine's routing mix matches your risk appetite and
   the historical committee dispositions (the model-vs-committee disagreement
   rate is your override-rate estimate). Keep routine extensions scoring low and
   reserve FULL_COMMITTEE for genuinely elevated proposals.
3. **Set the jurisdiction buckets** from your country-risk methodology, current
   sanctions programs, and the current FATF high-risk and increased-monitoring
   lists. This is the most time-sensitive table — review it on the sanctions /
   FATF update cadence.
4. **Confirm the floors and the prohibited list** match your policy — which
   attributes are auto-HIGH vs auto-MEDIUM, and which are never launchable at
   all. The floors and the list are the safety net; keep them at least as
   conservative as policy requires.
5. **Set the condition triggers and review intervals** to your control catalog —
   each named condition should map to a real pre-launch control confirmation
   your organization can actually perform and evidence.
6. **Re-run the validation gate** after any change: discrimination must still
   hold, monotonicity must still pass, no floor-triggered proposal may be tiered
   LOW, and no prohibited proposal may route past REFER_PROHIBITED.
7. **Record** the change, old/new values, the committee-sample result before and
   after, and the rationale — the model-change-management evidence.

## What not to do

- Do not weaken a floor or shorten the prohibited list to reduce the
  FULL_COMMITTEE population — they are the under-tiering protection.
- Do not let the jurisdiction buckets go stale; an out-of-date sanctions / FATF
  mapping is a common exam finding.
- Do not treat the illustrative weights as validated — they are a starting
  point, fit to a synthetic distribution, not your approval history.
- Do not add a condition the organization cannot evidence — an unverifiable
  condition is worse than routing the proposal up a tier.
- Keep weights non-negative and the per-factor sub-scores monotone in risk, or
  the monotonicity guarantee (and its gate) breaks.
