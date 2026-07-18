# Beneficial Ownership Resolution

A deterministic, standard-library-only Python 3.12 graph engine for resolving which natural persons ultimately own or control a target legal entity. It aggregates ownership across every path, handles convergent circular structures, detects non-equity control prongs, and dispositions each candidate as:

- `CONFIRMED_BENEFICIAL_OWNER`: aggregate effective ownership meets the threshold (default 25%) or a qualifying control prong is present.
- `REVIEW`: an ownership chain is unresolved, opaque, incomplete, nominee-linked, non-convergent, capped, or near threshold.
- `RESOLVED_BELOW_THRESHOLD`: the sole auto-clear, available only when the graph is fully resolved, aggregate effective ownership is below threshold and outside the review margin, and no qualifying control prong exists.

The engine documents resolution. It never files, freezes, rejects, off-boards, or takes external action.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | KYC / CDD onboarding teams, beneficial-ownership analysts, and independent validators. |
| **The question it answers** | Who ultimately owns or controls this entity, and can any candidate be cleared as below-threshold defensibly? |
| **What it is** | A small, transparent, runnable ownership-graph resolution engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never files, freezes, rejects, or off-boards. It never auto-clears a candidate while any part of the ownership graph is unresolved, and control without equity is surfaced, never cleared. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/beneficial-ownership-resolution
python3 run_validation.py --seed 42 --true-owners 160 --below 240 --unresolved 80 --trials 6
```

Pure Python standard library: nothing to install, no network access, a few seconds. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read the result on this page



<!-- /STANDALONE-BRIEF -->

## Safety invariants

- Multi-path interests are summed; no shell is evaluated in isolation.
- Circular paths are evaluated as a convergent path-product series, with explicit residual and iteration diagnostics.
- 0% equity plus qualifying control—such as sole directorship—is surfaced as confirmed.
- An unresolved, opaque, incomplete, or nominee element blocks every auto-clear in the relevant target graph.
- The production resolver asserts that every below-threshold auto-clear satisfies all eligibility conditions.
- `run_validation.py` exits non-zero if a true owner is auto-cleared or an ineligible/unresolved chain is auto-cleared.

## Quick start

```bash
python3 scorer.py --input reference-data/sample-input.json --output data/sample-output.json
python3 run_validation.py --seed 42 --true-owners 160 --below 240 --unresolved 80 --trials 6
```

No installation, dependency resolution, or network connection is required.

## Output

Each candidate result contains the disposition and reason; effective and raw ownership; threshold; ownership/control prong flags; control evidence; graph-resolution findings; convergence iterations, residual, and cap status; and the auditable `auto_clear_eligible` invariant.

## Core files

- `_lib/ownership.py`: path-product aggregation, cycle convergence, graph completeness, control prongs, and disposition logic
- `scorer.py`: production JSON CLI
- `generate_synthetic_data.py`: seeded labelled graph generator with adversarial plants
- `run_validation.py`: unit tests, multi-seed metrics, evidence emission, and fail-closed gates
- `negative_control_scorer.py`: deliberately unsafe direct-only test double
- `METHODOLOGY.md`: full formulas, thresholds, prongs, assumptions, and limitations
- `evidence/`: harness-emitted validation record

## Scope

This is a resolution aid, not a legal determination or substitute for authoritative corporate records. Thresholds and control tests vary by jurisdiction and use case. Validate configuration, data provenance, completeness declarations, and analyst procedures before deployment.
