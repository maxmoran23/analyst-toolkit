# Tuning — recalibrating the operating point

The defaults in `scorer.Config` are a deliberately conservative posture, validated
on synthetic data. They are a **starting point, not a production calibration**.
Before relying on this engine in a real environment, recalibrate it against a
labelled sample of your own alerts and record the change and its justification.

> **In plain terms:** The dials below control how aggressively the engine clears
> alerts versus how much it sends to people. Turning them up clears more but risks
> missing a real match; the safe way to set them is to test against a batch of
> alerts a human has already decided, find the setting that clears the most while
> still catching every real match, and write down why you chose it.

## The dials

| Constant | Default | Raise it → | Lower it → |
|---|---|---|---|
| `generic_max_share` | 0.005 | more tokens treated as generic → more aggressive auto-clear, higher false-negative risk | fewer tokens generic → more conservative, larger review queue |
| `escalate_name_floor` | 0.60 | fewer escalations (need a stronger name) | more escalations |
| `near_exact_name` | 0.95 | a discriminator can clear even strong name matches → higher FN risk | discriminator clears only weak name matches → safer |
| `review_high` | 0.50 | fewer HIGH-priority items | more HIGH-priority items |
| `review_medium` | 0.25 | more LOW-priority items | more MEDIUM-priority items |

The two that move the false-negative/false-positive trade-off are
`generic_max_share` and `near_exact_name`. Treat them with the most care.

## Calibrate genericness against your population, not the watchlist

The single most important production change: build the token-rarity model
(`TokenStats`) from a representative sample of the **names you actually screen**
(your customer and payment-party population), not only the watchlist. A token's
false-positive risk is a function of how common it is among *your* parties.
`generate_synthetic_data.py` builds `TokenStats` from the watchlist because that is
all a generic, public framework has; a deployment has its own name population and
should use it. Recompute `df`-shares on that corpus and re-confirm the generic band
(the genuinely common tokens should land above `generic_max_share`, distinctive
tokens well below).

## Procedure

1. **Assemble a labelled sample.** A few thousand historical alerts a qualified
   analyst has dispositioned (true match / false positive, and for false positives,
   ideally the reason). This is your ground truth.
2. **Run the sweep.** Score the sample and read the threshold-sensitivity table
   (`run_validation.py` produces this shape). Find where recall on true matches
   first drops below 1.0 — that is your hard ceiling.
3. **Pick the operating point** that holds recall at your required floor (1.0 for
   sanctions) while minimizing the residual review queue. Stay on the plateau, not
   the cliff edge.
4. **Re-run the false-negative gate** after any change. If recall on your labelled
   sample is below the floor, the change is rejected.
5. **Record it.** Document the constant changed, the old and new values, the
   labelled-sample result before and after, and the rationale. This is the
   model-change-management evidence an examiner expects.

## What not to do

- Do not raise `generic_max_share` to clear more volume without re-running the gate
  on a labelled sample — that is exactly the move that introduces false negatives.
- Do not auto-clear on `match_likelihood` alone. The named-reason requirement is
  the explainability property; a clearance justified only by "the score was low"
  does not survive an exam.
- Do not treat the synthetic-data operating point as production-ready. It is
  calibrated to a synthetic distribution; yours differs.
