# Tuning — recalibrating the operating point

The defaults in `scorer.Config` and the rule thresholds in `scorer.py` are a
conservative posture validated on synthetic data — a **starting point, not a
production calibration**. Recalibrate against a labelled sample of your own alerts
before relying on the engine, and record every change.

> **In plain terms:** The settings below control how aggressively alerts are closed
> versus sent to people, and what counts as each laundering pattern. Set them by
> testing against alerts your investigators have already dispositioned: find the
> setting that closes the most while still catching every suspicious case, and
> write down why.

## The two layers of dials

**Config (the operating point):**

| Constant | Default | Raise it → |
|---|---|---|
| `escalate_severity` | 0.60 | fewer escalations, more typology hits routed to review instead |
| `within_tol` | 1.50 | more alerts treated as on-profile → more aggressive closing |
| `context_tol` | 3.00 | documented-business explanations tolerate larger deviations |
| `soft_severity_floor` | 0.30 | minor signals ignored more readily |
| `review_high` / `review_medium` | 0.50 / 0.25 | shift the analyst priority bands |

**Rule thresholds (what counts as a typology — the most consequential):**
the structuring count (≥3 near-threshold deposits), the funnel fan-in (≥5 inbound),
the pass-through ratio (≥80%), the $10,000 reporting threshold, the $50,000
materiality floor, and the velocity/geo cutoffs. Lowering a typology threshold
catches more real patterns (raises recall headroom) but routes more alerts to
review; raising it does the reverse and is the move that risks false negatives.

## Calibrate against your own alert history

The single most important production step: tune the rule thresholds and the
customer baselines against a labelled sample of your **own** alerts and customer
segments. The synthetic baselines here (per-segment expected amounts and counts)
stand in for what a real deployment computes from each customer's transaction
history. Genericness of "expected" behaviour is customer- and segment-specific;
compute it from your data.

## Procedure

1. Assemble a labelled sample of historical alerts (analyst disposition + reason,
   ideally the typology where one applied). This is your ground truth.
2. Run the scorer over it and read the threshold-sensitivity sweep. Find where
   recall on suspicious alerts first drops below 1.0 — your hard ceiling.
3. Pick the operating point that holds recall at the floor while maximising the
   named-cause auto-close rate. The `ambiguous_residual` band should stay open.
4. Re-run the false-negative gate after any change; a change that drops recall
   below the floor on your labelled sample is rejected.
5. Record the constant changed, old/new values, the labelled-sample result before
   and after, and the rationale — the model-change-management evidence.

## What not to do

- Do not raise a typology threshold to cut volume without re-running the gate on a
  labelled sample — that is the move that introduces false negatives.
- Do not auto-close on `suspicion_score` alone. Closure requires a named benign
  cause and the absence of any typology; a closure justified only by a low score
  does not survive an exam.
- Do not treat the per-segment synthetic baselines as production baselines — derive
  them from real customer history.
