# Tuning — recalibrating the operating point

The defaults in `scorer.Config` and the contracts in `scorer.py` (country
reference set, identifier check-digit format, DOB plausibility floor) are a
conservative posture validated on synthetic data — a **starting point, not a
production calibration**. Recalibrate against profiled extracts from your own
golden sources before relying on the engine, and record every change.

> **In plain terms:** The settings below control how broken a file has to be
> before it is blocked, how similar two names must be to count as the same
> person, and how old a record can get before it is stale. Set them by
> profiling your own customer files: measure what "normal" defect rates look
> like, put the block line where screening quality genuinely degrades, and
> write down why.

## The two layers of dials

**Config (the operating point):**

| Constant | Default | Raise it → |
|---|---|---|
| `crit_ceiling` | 0.005 | more broken screening-critical data tolerated before BLOCK — the move that risks silent screening degradation |
| `dup_ceiling` | 0.004 | more duplicated parties tolerated before BLOCK |
| `warn_fraction` | 0.50 | warn band starts later → fewer INVESTIGATE dispositions |
| `supporting_ceiling` | 0.02 | supporting-field problems escalate later |
| `staleness_ceiling` | 0.10 | staler feeds tolerated |
| `composite_floor` | 0.98 | harder to FEED_PASS (this one tightens as it rises) |
| `staleness_horizon_days` | 365 | records stay "fresh" longer |
| `near_dup_name_sim` | 0.85 | fewer near-duplicate flags — the move that lets transliterated re-onboards through |

**Contracts (what counts as valid — the most consequential):** the country
reference set (`COUNTRY_REF`), the identifier format and check-digit rule
(`ID_RE` / `id_check`), the extract date format (`DATE_RE`), the DOB floor
(`DOB_FLOOR`), and the account-prefix format. These are stand-ins for your
institution's documented data standards — substitute the real ones verbatim.
A reference set that is too wide waves drift through; a format contract that
is too narrow floods the queue with false structure defects.

## Calibrate against your own extracts

The single most important production step: profile a representative sample of
each real feed and set ceilings relative to observed baselines and downstream
tolerance. The synthetic defect rates here (0.5-2% per class) are illustrative;
real feeds differ by an order of magnitude in either direction. Two rules of
thumb survive contact with production:

1. **Set the ceiling where screening measurably degrades, not where the data
   team is comfortable.** A 0.5% blank-name rate on an active book is 500
   unscreenable customers per 100,000 — quantify that exposure, then decide.
2. **Tune `near_dup_name_sim` on a labelled duplicate sample.** Run the
   threshold sweep (`evidence/threshold-sweep.csv` shows the shape): find
   where recall on known duplicate pairs first drops below 1.0 — that is your
   hard ceiling. Keep the phonetic and single-edit fallbacks on; the sweep
   demonstrates that similarity-only detection leaks transliterated pairs
   (0.88 recall at the default 0.85 threshold on the synthetic population).

## Procedure

1. Assemble labelled samples: profiled extracts with known defects, a labelled
   duplicate-pair set, and the feed owner's remediation history. This is your
   ground truth.
2. Run the engine over each sample; read the per-CDE scorecard and the sweep.
3. Pick ceilings that hold the two safety properties — every known critical
   defect detected, no materially-degraded feed passing — while keeping the
   INVESTIGATE volume workable.
4. Re-run the harness gates after any change; a change that lets a planted
   critical defect through, or a breached feed pass, is rejected.
5. Record the constant changed, old/new values, the labelled-sample result
   before and after, and the rationale — the model-change-management evidence.

## What not to do

- Do not raise `crit_ceiling` to make a chronically bad feed pass — that
  converts a data-remediation problem into a silent screening gap. Fix the
  feed or formally accept the risk in writing; the engine's job is to make
  that choice visible.
- Do not pass a feed on the composite score alone. FEED_PASS requires every
  named threshold met; a pass justified only by a high average does not
  survive an exam — the whole point of the hard gate is that averages cannot
  offset broken critical fields.
- Do not disable the phonetic/single-edit fallbacks to cut duplicate flags;
  raise the block threshold consciously instead, and re-run the gate on your
  labelled pairs.
- Do not treat the synthetic contracts (reference set, check digit, horizon)
  as production standards — substitute your documented ones.
