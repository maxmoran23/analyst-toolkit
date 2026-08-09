# Tuning Guide

Tune only with independently labelled, representative ownership graphs and a frozen adversarial safety set. Both gates must pass after every change.

## Parameters

`SanctionsConfig` exposes the blocked threshold (50%), internal review floor (25%), near-threshold margin (2 percentage points), convergence tolerance (`1e-12`), iteration cap (500), aggregate cap (100%), evidence-path cap (2,000), and active-state cap (20,000).

The 50% threshold and aggregation rule are policy constraints modeled on public OFAC guidance, not ordinary tuning parameters. The 25% review floor is an internal risk-control choice. `evidence/threshold-sweep.csv` varies that review floor while holding the 50% ground-truth standard fixed.

## Evaluation order

1. Freeze train, tuning, adversarial, and final holdout graphs.
2. Validate sanctioned seed provenance, edge directions/fractions, candidate selection, and completeness flags.
3. Run both gates before optimizing review volume or path limits.
4. Reconcile path-evidence totals to per-owner effective ownership.
5. Stratify by sanctioned-owner count, direct/indirect depth, cycle strength, path count, opacity, control, and source.
6. Examine every auto-clear and all analyst overrides.

## Adversarial hardening

Maintain planted cases for 30% + 25% and three-owner aggregation, N-shell slice concealment, long dilution chains, sanctioned parties behind apparently clean intermediaries, parallel paths, circular/cross ownership, overlapping sanctioned seeds, nominee layers, incomplete branches, control without equity, near-50 rounding, convergence limits, trace truncation, duplicate edges, and stale seed lists.

`negative_control_scorer.py` intentionally applies a single-owner-only 50% check and ignores graph resolution. The harness must exit non-zero, auto-clear the 30% + 25% true block, auto-clear an unresolved chain, and mark both gates `FAIL`. Never deploy it.

## Stop conditions

Do not deploy if either gate fails, evidence hashes are stale, the deterministic report does not reproduce, path totals do not reconcile, required completeness provenance is missing, current legal/policy review is absent, or REVIEW capacity is inadequate.
