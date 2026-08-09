# Validation Report

Generated deterministically by `run_validation.py`; all numeric results are emitted by the harness.

## Result

| Gate | Status | Observed |
|---|---:|---:|
| False-negative | PASS | 0 TRUE blocked → auto-clear |
| Resolution-integrity | PASS | 0 structural leaks; 0 unresolved-chain clears |

## Aggregate confusion matrix

| Ground truth | BLOCKED | NOT BLOCKED | REVIEW |
|---|---:|---:|---:|
| TRUE_BLOCKED | 960 | 0 | 0 |
| NOT_BLOCKED | 0 | 720 | 1200 |

Blocked-by-ownership recall: 1.000000. Review rate: 0.416667.

## Exact uncertainty statement

Observed 0 auto-clear false negatives in 960 labelled TRUE blocked-by-ownership candidates; the exact one-sided 95% Clopper-Pearson upper bound is 0.003116. This bound is a property of the validation sample size, not a claim of a zero population rate.

## Deterministic reproduction inputs

- Seed schedule: [42, 43, 44, 45, 46, 47]
- Per-trial sizes: {'true_blocked': 160, 'below': 240, 'unresolved': 80, 'total': 480}
- Blocked threshold: 0.50
- Review floor: 0.25
