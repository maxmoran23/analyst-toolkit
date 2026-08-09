# Sanctions Ownership Aggregation

A deterministic, standard-library-only Python 3.12 engine for identifying candidate entities whose aggregate direct and indirect ownership by sanctioned parties reaches 50%. It applies path-product ownership math per sanctioned seed, aggregates across all sanctioned owners, preserves every material contributing path, and returns:

- `BLOCKED_BY_OWNERSHIP`: aggregate sanctioned effective ownership is at least 50%, individually or collectively.
- `REVIEW`: aggregate ownership is 25%–50%, near 50%, any relevant path is unresolved/opaque/incomplete/nominee-linked, convergence or evidence is incomplete, or a sanctioned control prong exists without qualifying ownership.
- `NOT_BLOCKED_BY_OWNERSHIP`: the only auto-clear, available solely below 25% on a fully resolved and converged graph with complete path evidence and no sanctioned control.

The engine resolves and documents. It never blocks, freezes, rejects, files, or off-boards.

## Safety invariants

- Sanctioned interests are aggregated across owners; a 30% + 25% structure cannot be cleared because neither owner individually reaches 50%.
- Each sanctioned owner’s effective ownership reuses the vendored `_lib/ownership.py` path-product, multi-path, and circular-series calculation.
- Blocked results include per-owner effective ownership and complete material ownership-path chains under the convergence policy.
- Any unresolved path to the candidate blocks auto-clearance.
- Sanctioned control is not treated as the 50% ownership rule; it routes to `REVIEW`.
- Production asserts that every `NOT_BLOCKED_BY_OWNERSHIP` result satisfies the auto-clear invariant.

## Quick start

```bash
python3 scorer.py --input reference-data/sample-input.json --output data/sample-output.json
python3 run_validation.py --seed 42 --true-blocked 160 --below 240 --unresolved 80 --trials 6
```

CI-style re-derivation:

```bash
python3 run_validation.py --seed 42 --true-blocked 160 --below 240 --unresolved 80 --trials 6 --out data/rederived
```

The `--out DIR` form writes `metrics.json`, `VALIDATION-REPORT.md`, `run-manifest.json`, and the CSV evidence files into `DIR`. No installation or network connection is required.

## Core files

- `_lib/ownership.py`: vendored shared ownership math
- `_lib/sanctions_ownership.py`: sanctioned-owner aggregation, path evidence, control review, and dispositions
- `generate_synthetic_data.py`: seeded labelled adversarial graphs; `--out DIR` writes `sample-input.json`
- `run_validation.py`: unit tests, stability trials, evidence emission, and dual safety gates
- `negative_control_scorer.py`: deliberately unsafe single-owner-only test double
- `METHODOLOGY.md`: complete rules, formulas, thresholds, assumptions, and limitations

## Scope

The threshold and aggregation logic are modeled on public OFAC 50 Percent Rule guidance for analytical illustration. This is not legal advice, an official designation determination, or a replacement for current authoritative guidance and counsel.
