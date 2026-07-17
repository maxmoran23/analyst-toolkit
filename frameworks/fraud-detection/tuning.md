# Tuning — Fraud-Detection Operating Point

> **In plain terms:** Tune hard rules only against representative labelled fraud
> and legitimate activity. A change is rejected if it introduces one fraud approval,
> one legitimate hard decline, or leaves either exact 95% upper bound above 0.1%.

## Change classes

- Rule thresholds change what constitutes a named typology. Raising a threshold can
  create fraud misses; lowering one can create legitimate hard declines.
- `refer_severity` changes whether corroborated fraud routes to decline review or
  block confirmation. It cannot create `APPROVE`, but it changes customer-impact and
  operational routing.
- Score formula changes affect ranking and the counterfactual sweep only. They must
  never become a bare-score hard-decision path.
- Trusted-session conditions change approval eligibility. Loosening them requires
  direct challenge against confirmed fraud and account-takeover edge cases.

## Recalibration procedure

1. Freeze an independently labelled, time-split development and validation set with
   all five typologies, segment labels, overrides, and legitimate mimic categories.
2. Record the existing configuration, data lineage, observation window, prevalence,
   and both exact bounds.
3. Change one named constant at a time. Re-run both safety gates and review
   per-typology and per-legitimate-category outcomes.
4. Reject any configuration with a nonzero observed failure count or a 95% upper
   bound above 0.1%. A small sample that cannot establish the bound fails; zero
   observed errors alone is insufficient.
5. Challenge protected and operationally sensitive segments separately. Aggregate
   passing results do not excuse a segment-level failure.
6. Obtain documented fraud-strategy, customer-treatment, legal/compliance, model
   risk, and operations approval before deployment. Preserve before/after evidence.

## Monitoring

Track confirmed-fraud approvals, legitimate hard declines, step-up completion,
human override rates, typology mix, input missingness, score/disposition drift,
review latency, and downstream confirmed loss. Recompute exact bounds on a rolling,
independently labelled sample. Treat an observed safety failure as a control event,
not as routine variance.

Do not tune to synthetic headline metrics, copy the default 8% prevalence into a
business case, or use intervention precision as a substitute for the two safety
gates.

## Adversarial hardening (roadmap, not built)

The current harness plants two known failure branches and proves the dual gate
catches both. The stronger form is property-based adversarial generation around
every named rule boundary: for each rule, synthesize populations that sit just
inside and just outside its threshold, include correlated legitimate mimics
(customers whose lawful behavior imitates a typology), and drift the behavioral
baselines over the observation window. A gate that survives generated boundary
cases — rather than two hand-planted ones — is materially harder to pass by
accident, and the generation itself documents where the rule boundaries are
sensitive.

**Confidence rating: MODERATE —** the procedure protects the explicit invariant,
but its effectiveness depends on label quality, representativeness, and governance.

