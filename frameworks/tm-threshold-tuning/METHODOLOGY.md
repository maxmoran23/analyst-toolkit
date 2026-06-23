# Methodology — Transaction-Monitoring Threshold-Tuning Engine

The regulator-facing specification of the tuning logic. Every input, threshold, and
rule below exists as a named construct in [`engine.py`](engine.py); that file is its
executable form. Evidence: [`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md).
Shared governance: [`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** Every monitoring rule has a dial — a threshold — that decides
> what gets alerted. Set it too low and analysts drown in junk alerts; set it too
> high and real suspicious activity slips by unnoticed. This engine tests each rule
> two ways: of the alerts it fires, how many are worth working (above-the-line), and
> of the activity it lets through, how much is actually suspicious (below-the-line).
> Then it recommends the highest threshold that still catches the required share of
> suspicious activity — cutting junk only where it's safe. The regulator's question,
> "is the line in the right place?", is exactly what it answers.

---

## 1. What this framework does, and why it is different

The other frameworks score alerts. This one validates and tunes the **rules** that
generate them — it is the model-validation framework, applied to a monitoring rule
set. It is a thin, domain-framed layer over [`../_lib/metrics.py`](../_lib/metrics.py)
`sweep`: the same confusion matrix the scoring frameworks use, read with a tuning
question.

A rule alerts when its metric is at or above a threshold. Over a population with a
ground-truth label of which activity is genuinely suspicious:

- **Above-the-line (ATL) productivity** = precision of the alerts (TP / alerts) —
  are the alerts worth an analyst's time? A low value means the threshold is too low.
- **Below-the-line (BTL) leakage** = false negatives (suspicious activity below the
  threshold, undetected). A non-trivial value means the threshold is too high. This
  is the regulator's central concern.
- **Detection rate** = recall (TP / all suspicious) = 1 − BTL leakage share.

## 2. Inputs

A `Rule` (name, metric description, `current_threshold`) and, for that rule, a
population of metric values with a binary suspicious label.

## 3. Tuning logic

For each rule the engine sweeps candidate thresholds across the metric range and, at
each, computes alert volume, ATL productivity, detection rate, and BTL-missed (via
`metrics.sweep`). It then applies the safety posture:

**Recommend the HIGHEST threshold whose detection rate is still at or above the
recall floor** (`recall_floor`, default 0.95). Raising a threshold past that point
trades alert volume for missed suspicious activity, which the engine never
recommends.

The recommended **action** follows:

- **LOWER** — the current threshold's detection is below the floor (the rule is
  leaking suspicious activity below the line). Recommend down to the threshold that
  restores detection.
- **RAISE** — detection holds at the floor well above the current threshold (the
  rule is over-alerting). Recommend up to cut unproductive alert volume safely.
- **KEEP** — the current threshold is already near the safe optimum (within
  `keep_tolerance`, default 5%); no safe volume reduction is available.

### Why below-the-line safety is structural

The recommended threshold is, by construction, the highest one whose detection still
meets the floor. So a recommendation can never detect below the floor — the engine
cannot trade required detection for volume reduction. A rule that currently leaks is
always recommended DOWN to recover detection. The validation harness enforces both
as a build gate: every recommendation must meet the floor, and every leaking rule
must be remediated.

## 4. Tunable constants

`engine.Config`: `recall_floor` (0.95 — the required detection of suspicious
activity; a policy choice set from risk appetite), `keep_tolerance` (0.05),
`n_candidates` (40, the sweep resolution). See [`tuning.md`](tuning.md).

## 5. Governance and boundaries

Mapped to public guidance per [`../GOVERNANCE.md`](../GOVERNANCE.md) — SR 11-7 /
OCC 2011-12 (this framework IS outcomes analysis and ongoing monitoring for a
monitoring model), the FFIEC BSA/AML Examination Manual, and the **Wolfsberg Group**
statements on monitoring-rule threshold testing, which name above- and
below-the-line testing explicitly. The engine recommends; a threshold change is a
governed model-change decision that a human approves and documents. The recall floor
itself is a policy choice, not a model output — it must be set and owned by the
institution.
