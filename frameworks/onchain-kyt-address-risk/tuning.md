# Tuning — recalibrating the operating point

The thresholds in `scorer.Config`, the category severities, and the propagation
`hop_decay` are a conservative posture validated on synthetic data — a starting
point, not a production calibration. Recalibrate against labelled cases from your own
chain-analytics feed, and record every change.

> **In plain terms:** The dials below decide how close, how much, and how serious an
> exposure has to be before a flag is kept versus cleared. Set them by testing
> against addresses your investigators have already dispositioned — find the setting
> that clears the most non-actionable flags while still catching every genuinely
> risky address — and write down why.

## The dials

| Constant | Default | Raise it → |
|---|---|---|
| `escalate_floor` | 0.30 | fewer escalations (need stronger exposure) |
| `dilution_floor` | 0.04 | more flags cleared as too-remote (riskier) |
| `max_actionable_hops` | 4 | fewer flags cleared on distance (more conservative) |
| `deminimis_fraction` | 0.02 | more flags cleared as immaterial (riskier) |
| `review_high` / `review_medium` | 0.12 / 0.05 | shift analyst priority bands |

**Deeper surface:** the `CATEGORY_SEVERITY` table in `scorer.py` (which on-chain
categories are how serious) and the `hop_decay` in `_lib/graph.py` (how fast taint
attenuates per hop). These should reflect your risk appetite and your analytics
vendor's attribution semantics.

## The vendor dependency

This engine consumes exposure features that, in production, come from a
chain-analytics vendor (Chainalysis / TRM / Elliptic). That vendor's **cluster
attribution** — which address belongs to which entity/category — has its own error
rate. A mis-labeled cluster (e.g., a benign service labeled as a mixer, or vice
versa) propagates directly into this engine's disposition. **Validate the vendor
feed** as part of the model: sample its attributions, track its confidence, and
consider routing low-confidence attributions to ANALYST_REVIEW regardless of the
computed exposure.

## Procedure

1. Assemble a labelled sample of historical address dispositions (analyst outcome +
   the exposure features at the time). This is the ground truth.
2. Run the scorer and read the threshold sweep. Find where recall on genuinely
   high-risk addresses first drops below 1.0 — the hard ceiling.
3. Pick the operating point holding recall at the floor while maximising the
   named-cause clear rate. Keep the mid-severity ambiguous band open.
4. Set `CATEGORY_SEVERITY` and `hop_decay` from your taxonomy and policy; review the
   sanctioned/mixer/darknet severities against current designations.
5. Re-run the false-negative gate after any change; a change dropping recall below
   the floor is rejected.
6. Record the change, old/new values, the labelled-sample result, and the rationale.

## What not to do

- Do not raise `dilution_floor` or `deminimis_fraction` to cut volume without
  re-running the gate — that is how proximate, material exposure gets wrongly cleared.
- Do not auto-clear on the risk score alone; closure requires a named cause.
- Do not trust the vendor's category labels blindly — a mis-attribution there becomes
  a false negative here.
