# Sanctions Ownership Aggregation

A deterministic, standard-library-only Python 3.12 engine for identifying candidate entities whose aggregate direct and indirect ownership by sanctioned parties reaches 50%. It applies path-product ownership math per sanctioned seed, aggregates across all sanctioned owners, preserves every material contributing path, and returns:

- `BLOCKED_BY_OWNERSHIP`: aggregate sanctioned effective ownership is at least 50%, individually or collectively.
- `REVIEW`: aggregate ownership is 25%–50%, near 50%, any relevant path is unresolved/opaque/incomplete/nominee-linked, convergence or evidence is incomplete, or a sanctioned control prong exists without qualifying ownership.
- `NOT_BLOCKED_BY_OWNERSHIP`: the only auto-clear, available solely below 25% on a fully resolved and converged graph with complete path evidence and no sanctioned control.

The engine resolves and documents. It never blocks, freezes, rejects, files, or off-boards.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | Sanctions screening and list-management teams applying the ownership rule, and their independent validators. |
| **The question it answers** | Is this entity blocked by ownership — owned 50% or more, individually or in the aggregate, directly or indirectly, by sanctioned parties — even though no list names it? |
| **What it is** | A small, transparent, runnable ownership-aggregation engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never blocks, freezes, or rejects. It never auto-clears a candidate while any path from a sanctioned party is unresolved, and sanctioned control without qualifying equity routes to review, never to a clear. Thresholds are modeled on public guidance and are not legal advice. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/sanctions-ownership-aggregation
python3 run_validation.py --seed 42 --true-blocked 160 --below 240 --unresolved 80 --trials 6
```

Pure Python standard library: nothing to install, no network access, a few seconds. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read the result on this page



<!-- /STANDALONE-BRIEF -->

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
