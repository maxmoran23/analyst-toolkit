# Methodology

## Objective and model-risk framing

For each natural-person candidate and target entity, the engine calculates aggregate effective ownership, evaluates non-equity control, assesses graph resolvability, and returns a documented disposition. It uses symmetric safety controls: a true beneficial owner must never be auto-cleared, and an incomplete graph must never support auto-clearance.

This is an SR 11-7-style model-risk framework: intended use and limits are documented; calculations are transparent; validation is independent and repeatable; adversarial controls provide effective challenge; provenance and outcomes are emitted; and any code, threshold, prong, or completeness change requires revalidation. This framing is not a representation that the engine has received regulatory validation.

## Effective ownership

For natural person `p` and target `t`, effective ownership is:

`EO(p,t) = min(1, Σ_path Π_edge fraction(edge))`

The sum includes every directed ownership path from the person to the target. Products capture dilution through intermediary layers; summation captures split holdings and concealed-majority structures. Fractions must be numeric values from 0 through 1. Duplicate edges are additive and therefore must reflect the source data intentionally.

## Circular and cross ownership

The engine evaluates cycles as a convergent series rather than enumerating only simple paths. Starting with mass 1 at the source, each iteration propagates mass across ownership edges. Mass arriving at the target is accumulated and not propagated further. Remaining non-target mass is iterated until its absolute sum is at most `1e-12` or 500 iterations are reached.

The reported result includes raw effective ownership, residual mass, iterations, convergence status, and whether the ownership cap was required. Final effective ownership is capped at 100%. A result that is below threshold but does not converge, or requires capping, is `REVIEW`; it cannot be auto-cleared. The default circular validation plant has a geometric loop product of 0.25 and converges to 26.6667% effective ownership.

## Resolution integrity

The engine computes all graph nodes that can reach the target. The target graph is not fully resolved if any relevant node has one of these declarations:

- `resolved: false`
- `opaque: true`
- `nominee: true`
- an entity with `ownership_complete: false`

Equivalent flags on the candidate also block auto-clearance. Resolution is global to the relevant target graph: an opaque target-ownership branch blocks clearance even when the candidate's own visible chain appears complete. The engine does not infer completeness from fractions summing to 100%; upstream systems must explicitly attest `ownership_complete` where needed.

## Thresholds and disposition rules

| Parameter | Default | Rule |
|---|---:|---|
| Beneficial-ownership threshold | 0.25 | Effective ownership at or above this value confirms the ownership prong |
| Near-threshold margin | 0.02 | Resolved ownership from 0.23 up to, but excluding, 0.25 returns REVIEW |
| Convergence tolerance | 1e-12 | Maximum residual path mass for convergence |
| Maximum iterations | 500 | Non-convergence by this point returns REVIEW below threshold |
| Ownership cap | 1.00 | Raw sums above 100% are capped and reviewed when otherwise below threshold |

Rules are applied in this order:

1. Effective ownership at least 25% or any qualifying control prong → `CONFIRMED_BENEFICIAL_OWNER`.
2. Unresolved, opaque, incomplete, or nominee graph/candidate → `REVIEW`.
3. Non-convergent or capped circular calculation → `REVIEW`.
4. Effective ownership within the 2 percentage-point review margin → `REVIEW`.
5. Fully resolved, converged ownership below 23% with no control prong → `RESOLVED_BELOW_THRESHOLD`.

Confirmed ownership/control is surfaced even when another portion of the graph is unresolved. Opacity never suppresses known threshold-crossing evidence.

## Control prongs

Only relationships applying directly to the target—or to an intermediary whose own effective ownership of the target is at least the ownership threshold—can qualify.

| Input prong | Qualification rule |
|---|---|
| `sole_director` | Always qualifying |
| `senior_managing_official` | Always qualifying |
| `signatory` / `authorized_signatory` | `sole_authority: true` or `decisive: true` |
| `voting_agreement` | `voting_fraction >= threshold` or `decisive: true` |
| `director` | `sole_director: true` or `decisive: true`; ordinary non-sole directorship is non-qualifying |
| `power_of_attorney` | `decisive: true` only |
| Other prong | `decisive: true` only |

This taxonomy is configurable only through code review; expanding it requires legal and data-source validation.

## Validation design

Ground truth is assigned by the seeded generator before scoring. TRUE-owner plants include three sub-threshold shell paths aggregating above 25%, a convergent circular cross-ownership loop, an opaque layer with a known 30% path, 0% equity plus sole-director control, direct threshold owners, and multi-path diluted interests. NOT-owner plants include resolved low interests, zero equity, non-sole directors, near-threshold records, opaque/incomplete/nominee intermediaries, and an opaque branch elsewhere in the target graph.

The harness runs unit tests, scores independent seeds, emits trial and aggregate metrics, sweeps the near-threshold margin, and enforces:

- False-negative gate: no labelled TRUE beneficial owner may be dispositioned `RESOLVED_BELOW_THRESHOLD`.
- Resolution-integrity gate: no ineligible auto-clear and no auto-clear on an unresolved planted graph.

The exact one-sided 95% Clopper-Pearson upper bound is computed by binomial-CDF inversion, with a closed form for zero observed events. Every numeric false-negative statement includes its event count, TRUE-owner sample size, exact upper bound, and the warning that the bound is a sample-size property.

## Limitations

The engine trusts edge fractions and completeness flags; it does not authenticate filings, infer missing owners, resolve identity aliases, time-bound ownership, model share classes, allocate joint ownership, or interpret jurisdiction-specific legal standards. Convergent path sums can overstate economic ownership when source edges encode non-independent or duplicative rights. Validate with representative, lawfully obtained data and monitor by jurisdiction, source, depth, cycle structure, opacity, control prong, and analyst override.
