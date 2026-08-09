# Methodology

## Intended use and regulatory framing

The engine determines whether known sanctioned ownership of a candidate entity reaches 50% in the aggregate, even when the candidate is not itself present in a sanctions seed set. The threshold and aggregation rules are modeled on public OFAC 50 Percent Rule guidance. The implementation is illustrative, not legal advice, and does not represent an official designation, blocking, licensing, reporting, or enforcement determination.

This is an SR 11-7-style model-risk frame: transparent calculations; documented intended use and limits; seeded, repeatable validation; adversarial effective challenge; emitted outcomes; provenance; and mandatory revalidation after code, threshold, source, completeness, or control-policy changes.

## Ownership calculation

For sanctioned party `s` and candidate entity `c`:

`EO(s,c) = min(1, Σ_path(s→c) Π_edge fraction(edge))`

The engine imports this calculation from the vendored `_lib/ownership.py`, identical to the module prepared for the shared repo library. Products capture indirect dilution; sums capture parallel paths. Circular and cross ownership are evaluated as a numeric series until residual path mass is at most `1e-12` or 500 iterations are exhausted.

Aggregate sanctioned ownership is:

`SAO(c) = min(1, Σ_sanctioned EO(s,c))`

The sum is evaluated across the supplied sanctioned seed set. The 100% cap is a reporting guard, not a repair for overlapping or duplicative source records. Nested sanctioned seeds can double count economic interests; inputs require source governance and de-duplication appropriate to the use case.

## Ownership-path evidence

For every sanctioned owner, the output contains effective and raw ownership, convergence diagnostics, and every numerically material path contribution through the configured convergence tolerance. Each path records ordered node IDs, edge fractions, and the resulting product. Circular paths may repeat nodes and are emitted term-by-term until convergence. The trace total must reconcile to the shared ownership calculation within the greater of `1e-12` or relative `1e-10`; otherwise evidence is incomplete and a below-threshold result routes to `REVIEW`.

Default safeguards cap evidence at 2,000 completed paths and 20,000 active path states. Truncation is explicit and prevents auto-clearance.

## Graph resolution

For each candidate, `_lib/ownership.py` identifies every node capable of reaching that candidate. The graph is unresolved if any relevant node has:

- `resolved: false`
- `opaque: true`
- `nominee: true`
- entity `ownership_complete: false`

Any unresolved sanctioned path prevents `NOT_BLOCKED_BY_OWNERSHIP`, even when visible ownership appears small. Known aggregate ownership at or above 50% remains surfaced as blocked by ownership despite other opacity.

## Thresholds and disposition order

| Parameter | Default | Purpose |
|---|---:|---|
| Blocked threshold | 0.50 | Individual or aggregate sanctioned ownership at/above 50% |
| Review floor | 0.25 | Internal conservative triage band; not the OFAC blocking threshold |
| Near-threshold margin | 0.02 | Flags aggregate ownership from 48% to below 50% |
| Convergence tolerance | 1e-12 | Maximum residual path mass |
| Maximum iterations | 500 | Numeric series limit |
| Aggregate cap | 1.00 | Reporting cap |

Rules are applied in order:

1. Aggregate sanctioned ownership at least 50% → `BLOCKED_BY_OWNERSHIP`. The reason distinguishes an individual 50% owner from aggregate-only blocking.
2. Any unresolved, opaque, incomplete, or nominee-linked relevant path → `REVIEW`.
3. Non-convergence, path-evidence mismatch/truncation, or per-owner cap → `REVIEW` below 50%.
4. Qualifying sanctioned control without 50% ownership → `REVIEW`.
5. Aggregate ownership from 25% to below 50% → `REVIEW`; 48%–50% also carries `near_threshold: true`.
6. Aggregate ownership below 25%, complete/converged evidence, and no sanctioned control → `NOT_BLOCKED_BY_OWNERSHIP`.

The 25% review floor is an engine risk-control choice, not a statement of the OFAC ownership threshold.

## Sanctioned-control review prongs

Control is not added to ownership and cannot produce `BLOCKED_BY_OWNERSHIP`. A qualifying relationship from a sanctioned person to the candidate—or to an intermediary that reaches it—routes to review:

| Prong | Qualification |
|---|---|
| `sole_director` | Always |
| `senior_managing_official` | Always |
| `signatory` / `authorized_signatory` | `sole_authority: true` or `decisive: true` |
| `voting_agreement` | `voting_fraction >= 0.50` or `decisive: true` |
| `director` | `sole_director: true` or `decisive: true` |
| `power_of_attorney` | `decisive: true` |
| Other | `decisive: true` |

## Validation design

The seeded generator labels graphs before scoring and varies category boundaries across seeds. TRUE-blocked plants include 30% + 25% aggregation, three sub-threshold sanctioned owners totaling 51%, three shell slices totaling 54%, a convergent circular structure exceeding 50%, a sanctioned party behind a clean-looking intermediary, and indirect multi-owner aggregation. Negative/unresolved plants cover fully resolved low ownership, 25%–50% review cases, 49% near-threshold ownership, sanctioned control without equity, and opaque/incomplete/nominee paths.

The harness enforces:

- False-negative gate: no labelled TRUE blocked-by-ownership candidate may be auto-cleared.
- Resolution-integrity gate: no ineligible auto-clear and no unresolved planted candidate may be auto-cleared.

The one-sided 95% Clopper-Pearson upper bound is exact and calculated from observed false clearances and labelled TRUE-blocked sample size. Every numeric false-negative statement explains that the bound is a property of sample size, not proof of a zero population rate.

`VALIDATION-REPORT.md` is deterministic. Interpreter, platform, timestamps, wall-clock time, command, and code hashes appear only in `run-manifest.json`.

## Limitations

The engine trusts sanctioned seeds, edge fractions, node identity resolution, completeness flags, and control attributes. It does not retrieve or update lists, resolve aliases, interpret licenses, apply temporal ownership, distinguish share classes, eliminate overlapping sanctioned interests, or make legal/action decisions. Validate against current authoritative guidance and representative, lawfully obtained records; monitor source, jurisdiction, depth, cycles, path counts, opacity, list changes, and analyst overrides.
