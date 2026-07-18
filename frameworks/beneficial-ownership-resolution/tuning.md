# Tuning Guide

Tune only on labelled, representative graphs with an independently frozen safety set. Every change must preserve both validation gates.

## Adjustable parameters

`OwnershipConfig` exposes the ownership threshold (default 25%), near-threshold review margin (2 percentage points), convergence tolerance (`1e-12`), iteration cap (500), and ownership cap (100%). The harness-generated `evidence/threshold-sweep.csv` varies the review margin while holding the labelled 25% standard constant.

Threshold and control-prong changes are legal-policy changes, not ordinary numerical tuning. Require documented jurisdiction/use-case authority and independent approval.

## Evaluation order

1. Freeze train, tuning, adversarial safety, and final holdout graphs.
2. Verify edge direction, fractions, target selection, and completeness provenance.
3. Run both gates before optimizing review volume.
4. Stratify by graph depth, number of paths, cycle strength, opacity, nominee status, control prong, source, and jurisdiction.
5. Inspect every auto-clear and every true-owner miss or review.
6. Record analyst overrides and upstream data corrections.

## Adversarial hardening

Maintain planted cases for N-shell concealed majorities, long dilution chains, duplicate and parallel paths, circular cross ownership, loops near non-convergence, nominee layers, opaque intermediaries, incomplete target branches, control without equity, sole versus non-sole signing authority, voting agreements, cap-triggering graphs, and threshold-boundary rounding. Add every discovered production failure mode to a frozen challenge set.

`negative_control_scorer.py` is intentionally unsafe. It checks only direct person-to-target ownership, ignores path aggregation, and disregards resolution eligibility. The dual-gate harness must exit non-zero and expose both concealed-majority false clearance and unresolved-chain auto-clearance. Never deploy or import it from a production pipeline.

## Stop conditions

Do not deploy when either gate fails, evidence hashes are stale, completeness declarations lack provenance, graph cycles do not converge within the documented policy, a segment lacks sufficient validation, or the REVIEW workload cannot be handled safely.
