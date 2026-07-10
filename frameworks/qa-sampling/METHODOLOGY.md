# Methodology — QA / Independent-Testing Attribute-Sampling Engine

The regulator-facing specification of the sampling logic. Every input,
threshold, and named rule below exists as a named construct in
[`engine.py`](engine.py) and [`../_lib/sampling.py`](../_lib/sampling.py); those
files are its executable form. Evidence:
[`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md).
Shared governance: [`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** A tester cannot check all 40,000 wire callbacks, so they
> check a sample and reason from it. Getting that reasoning right takes three
> exact answers: how many items make the sample big enough (plan), how to pick
> them so nobody chose them (select), and what the deviations found prove about
> the whole population (evaluate). Each answer here is a probability statement
> computed exactly — not read off a printed table — and the final conclusion is
> handed to the tester with the math shown. One rule is absolute: if the sample
> found more deviations than the plan allows, no arithmetic can call the
> control effective.

---

## 1. What this framework does, and why it is different

The other frameworks score alerts and tune rules. This one equips the function
that CHECKS them — independent testing and quality assurance — with exact
statistical machinery for tests of controls. It is a thin, domain-framed layer
over [`../_lib/sampling.py`](../_lib/sampling.py): exact binomial and
hypergeometric tail probabilities, an exact attribute-sample-size solver, and
the exact one-sided upper deviation limit (UDL), replacing the lookup tables
this work is traditionally done from. Three stages: PLAN, SELECT, EVALUATE.

## 2. Inputs

A `ControlTest`: the control identifier and description, plus three stated
policy parameters — `confidence` (1 − the acceptable risk of over-reliance),
`tolerable_rate` (the maximum population deviation rate consistent with
reliance on the control), `expected_rate` (the anticipated population deviation
rate) — and optionally the finite `population` size. For evaluation, the
observed deviation count from the tested sample. The engine consumes no labels
and no scores — only these stated parameters and the count the tester found.

## 3. Stage 1 — PLAN (exact sample-size solver)

The plan is the smallest pair (n, c) — sample size and acceptance number —
such that:

1. **Risk condition:** a population deviating at the tolerable rate is accepted
   (observed deviations <= c) with probability at most 1 − confidence. Exact
   binomial tail by default; exact hypergeometric when the population is
   finite, testing the count K = ceil(N x tolerable) — the smallest population
   deviation count still at the rate, i.e. the hardest such population to
   detect. No normal approximation, no table interpolation.
2. **Feasibility condition:** c >= n x expected_rate — the acceptance number
   absorbs the deviations the tester already anticipates, so an expected-clean
   sample does not auto-fail.

The solver iterates c upward and finds the minimal n for each by exact tail
inversion. It emits the `achieved_risk` — the exact acceptance probability at
the tolerable rate — which is always at or below the design risk (verified in
validation). If expected_rate >= tolerable_rate it raises: no sample size can
separate them, and pretending otherwise is how bad plans are born.

## 4. Stage 2 — SELECT (seeded, reproducible)

Simple random or stratified selection over the population, driven by a stated
seed: same seed, same selection, verifiable by anyone re-running. Stratified
selection allocates proportionally by largest remainder with a minimum of one
item per stratum, then samples within each stratum. The selected items ARE the
selection log (committed in evidence as `selection-log.csv`) — the answer to
the examiner's "show me how these items were chosen" is a seed and a script,
not a memo.

## 5. Stage 3 — EVALUATE (exact UDL + named rules, in firing order)

The UDL is the largest population deviation rate the sample does not reject at
the stated confidence: the exact Clopper-Pearson upper bound (binomial
inversion by bisection), or exact hypergeometric inversion over the integer
count of population deviations when the population is finite — a census
collapses to exactly k/N. The conclusion rules fire in order:

| # | Rule | Condition | Conclusion | Rationale |
|---|---|---|---|---|
| R1 | `OVER_ACCEPTANCE` | deviations > acceptance number | CONTROL_INEFFECTIVE | The sample exceeded what the plan tolerates. Fires FIRST: past this line no arithmetic can conclude effectiveness — structural, not scored. |
| R2 | `UDL_WITHIN_TOLERABLE` | UDL <= tolerable rate | CONTROL_EFFECTIVE | The worst population rate consistent with the sample is still acceptable — the only provable cause for a supports-reliance conclusion. |
| R3 | `UDL_EXCEEDS_TOLERABLE` | otherwise | INCONCLUSIVE | Deviations within acceptance but the sample (typically short-tested) cannot bound the rate under the tolerable line. The engine re-solves the plan at the observed rate and emits exact expand-sample guidance, or states that expansion cannot conclude. |

Every conclusion carries the exact statistical statement ("with 95% confidence
the population deviation rate does not exceed X ...") and routes to the tester.
**The engine never certifies a control, closes a test, or files a result** —
CONTROL_EFFECTIVE is a statement the sample supports, not an auto-pass; the
tester owns the judgment and the workpaper.

## 6. Why the safety posture is structural

R1 precedes R2, so an over-acceptance sample can never be concluded effective —
by construction, not by tuning. The validation harness independently re-checks
every evaluation (main run and replicate draws) for that property, plants a
fully-deviant stratum sized so stratified allocation must catch more than the
acceptance number, measures false-assurance on populations deviating at 2-3x
the tolerable rate against the design risk, and recomputes every UDL through an
independent brute-force exact path (direct `math.comb` summation; exact
integer/Fraction arithmetic). All four are build gates: a breach exits non-zero.

## 7. Tunable constants

The three consequential dials — `confidence`, `tolerable_rate`,
`expected_rate` — are INPUTS stated per test, owned by policy, not engine
constants (see [`tuning.md`](tuning.md)). `engine.Config` holds only
`max_acceptance` (1000), the solver's search bound on the acceptance number.
The generator's design constants (design confidence 0.95, tolerable-rate menu,
scenario bands) shape the validation population, not the engine.

## 8. Governance and boundaries

Mapped to public guidance per [`../GOVERNANCE.md`](../GOVERNANCE.md) — SR 11-7 /
OCC 2011-12 (this framework serves the independent-testing leg of model risk
management: exact, reproducible outcomes analysis for control testing), and the
FFIEC BSA/AML Examination Manual expectation that independent testing be
risk-based, documented, and defensible in its sampling approach. Limitations,
stated plainly: the engine quantifies **sampling risk only** — non-sampling
risk (the tester misreading an item) is unaffected by sample size and is
managed by review; deviations in real populations cluster, so stratify on the
clustering dimension and scope any cluster found as a finding; and the
parameters are policy choices the institution must set and own. A reference
implementation for auditability — a real deployment recalibrates the parameters
to its own testing standards, and this scoring contract is what travels.
