# Tuning — recalibrating the operating point

The thresholds in `scorer.Config` and the category/role/recency tables in
`_lib/relevance.py` are a conservative posture validated on synthetic data — a
starting point, not a production calibration. Recalibrate against a labelled sample
of your own screening hits, and record every change.

> **In plain terms:** The dials below decide how readily a hit is cleared versus
> sent to a person, and what counts as "serious" or "stale." Set them by testing
> against hits your analysts have already dispositioned, find the setting that
> clears the most while still catching every genuine match, and write down why.

## The dials

**Config (the operating point):**

| Constant | Default | Raise it → |
|---|---|---|
| `match_floor` | 0.55 | fewer escalations (need stronger entity confidence) |
| `escalate_relevance` | 0.50 | fewer escalations (need more material content) |
| `stale_days` | 1825 | fewer stale clears (only older news clears) |
| `immaterial_max_severity` | 0.45 | more categories eligible for stale clear (riskier) |
| `near_exact_name` | 0.95 | a weak-id discriminator can clear stronger name matches |
| `generic_max_share` | 0.005 | more name tokens treated as common |
| `review_high` / `review_medium` | 0.40 / 0.18 | shift analyst priority bands |

**Relevance tables (`_lib/relevance.py`) — the deeper surface:** the adverse-category
severities, the role weights, and the recency half-life. These should match your
media-classification taxonomy and risk appetite.

## The classifier dependency

This engine takes `category` and `role` as inputs. In production they come from an
upstream media classifier (NLP). That classifier has its own error rate, which
compounds with this engine's — a mis-classified "non_adverse" that is actually
adverse would be auto-cleared here. **Validate the upstream classifier as part of
the model**, and consider treating low-confidence classifications as ANALYST_REVIEW
regardless of the category they were assigned.

## Procedure

1. Assemble a labelled sample of historical hits (analyst disposition + reason, and
   ideally the true category/role). This is the ground truth.
2. Run the scorer and read the threshold sweep. Find where recall on genuine adverse
   matches first drops below 1.0 — the hard ceiling.
3. Pick the operating point holding recall at the floor while maximising the
   named-cause clear rate. Expect a residual common-name-ambiguous band that stays
   open — do not tune it away.
4. Set the relevance tables from your taxonomy; review category severities and the
   recency half-life against policy.
5. Re-run the false-negative gate after any change; a change dropping recall below
   the floor is rejected.
6. Record the change, old/new values, the labelled-sample result, and the rationale.

## What not to do

- Do not clear common-name matches with no identifier to cut volume — that is
  exactly the move that clears a real adverse hit on a common-named customer.
- Do not auto-clear on the combined score alone; closure requires a named cause.
- Do not trust the upstream `category`/`role` blindly — a classifier error there
  becomes a false negative here.
