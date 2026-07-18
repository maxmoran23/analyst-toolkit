# Tuning Guide

Tune only with labelled, representative holdout data. Preserve a frozen safety set and rerun `run_validation.py` after every change.

## Adjustable settings

`ResolutionConfig` exposes the decisive moderate-contradiction threshold (`1.00`), minimum raw name context (`0.50`), address similarity (`0.92`), and place-of-birth similarity (`0.90`). The threshold sweep in `evidence/threshold-sweep.csv` is generated from the seeded primary trial.

Do not tune the structural SAME invariant. Adding a new strong field requires evidence that the field is unique, stable, source-authenticated, normalized without collision risk, and governed for jurisdiction and lifecycle changes.

## Evaluation sequence

1. Freeze labelled train, tuning, safety, and final holdout sets.
2. Tune REVIEW volume only after both safety gates pass.
3. Stratify outcomes by source, jurisdiction, script/romanization, identifier missingness, and common-name segment.
4. Examine every `SAME` and `DIFFERENT` error, not only aggregate rates.
5. Document overrides and require independent approval for production threshold changes.

## Adversarial hardening

Maintain planted cases for transliteration drift, name-order swaps, recycled or renewed document numbers, OCR substitutions, adjacent-digit DOB transpositions, partial DOBs, alias-only records, common-name collisions, conflicting strong IDs, and poisoned records containing one copied identifier. Expand the corpus when production reviewers find a new failure mode.

`negative_control_scorer.py` is intentionally unsafe: it treats romanization differences as clearance evidence and exact common names as merge evidence. The harness must exit non-zero and print leaked case IDs when run with `--engine negative-control`. Never import or deploy that file as a production scorer.

## Stop conditions

Do not deploy a change if either gate fails, evidence files are stale relative to `_lib/identity.py`, the holdout provenance is incomplete, a segment has insufficient coverage, or the review queue cannot support the resulting workload.
