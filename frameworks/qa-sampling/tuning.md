# Tuning — configuring the sampler

This framework has almost no engine constants to tune — deliberately. The three
dials that decide every plan are policy inputs stated per test, and the point
of the exact solver is that once they are stated, the sample size stops being a
negotiation.

> **In plain terms:** The knobs here are not model settings — they are risk
> decisions: how sure you need to be, how much failure you could live with, and
> how much failure you expect. Decide those from policy, write them down, and
> let the math produce the sample size. The one thing this tool removes is the
> habit of working backwards from the sample size you wanted.

## The dials

| Parameter | Typical range | Effect |
|---|---|---|
| `confidence` | 0.90-0.99 | 1 − the acceptable risk of over-reliance. Higher = larger samples. Set from the criticality of the control and the reliance placed on it (key controls warrant 0.95+). **A policy choice — set and own it.** |
| `tolerable_rate` | 0.02-0.10 | The maximum population deviation rate still consistent with reliance. Tighter = larger samples. Set from the assertion the control supports, not from workload. |
| `expected_rate` | 0-0.5x tolerable | The anticipated deviation rate; drives the acceptance number. Set from prior-period results for the same control. Must be strictly below tolerable — the solver refuses otherwise. |
| `Config.max_acceptance` | 1000 | Solver search bound; only a guard against degenerate inputs. |

## Recalibration procedure

1. Set `confidence` and `tolerable_rate` per control from the testing standard
   (control criticality, reliance, regulatory expectation). Document them
   before selection — never after results are in.
2. Set `expected_rate` from the most recent prior test of the same control;
   for a first test, use a conservative low value (a zero acceptance number is
   the cheapest plan but fails on the first deviation found).
3. Run PLAN and record n, c, and the achieved risk in the workpaper — the plan
   is the reproducible artifact.
4. SELECT with a recorded seed. The seed plus the population snapshot is the
   full selection audit trail.
5. EVALUATE and act on the named rule: OVER_ACCEPTANCE and UDL_EXCEEDS
   conclusions route to findings and expansion decisions; the expand-sample
   guidance is a re-solved plan, not a rule of thumb.
6. Feed this period's observed rate back as next period's `expected_rate`.

## The definition dependency

Attribute sampling is only as good as the deviation definition. Decide before
testing what counts as a deviation (missing evidence? late? wrong approver?),
apply it uniformly, and record per-item results — the UDL is exact about the
count it is given, and silent definitional drift is non-sampling risk the
statistics cannot see.

## What not to do

- Do not tune `expected_rate` upward to buy a bigger acceptance number for a
  control you fear is failing — you are pre-purchasing tolerance for the
  failure you expect to find.
- Do not lower `confidence` or loosen `tolerable_rate` to hit a testing-budget
  number; change the reliance decision instead, and document it.
- Do not stop testing mid-sample when deviations reach the acceptance number
  and call it a day — the plan's risk statement assumes the full sample; an
  early stop routes through the INCONCLUSIVE path, not to a conclusion.
- Do not reuse a selection seed across periods "for comparability" — that is
  a predictable sample, and predictable samples get managed to.
