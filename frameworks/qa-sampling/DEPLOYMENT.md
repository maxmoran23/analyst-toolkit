# Deployment — mapping to Microsoft Copilot Studio / Power Platform

Follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target architecture.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, the
> sampling engine becomes a tool the testing team's agent calls three times per
> test — size the sample, draw it, evaluate it — with every number exact and
> reproducible; the methodology becomes the agent's instructions and its
> explanation of what the sample does and does not prove; and the synthetic
> controls become the test pack that proves the math before anyone relies on it.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `plan` / `select` / `evaluate` — deterministic, parameters in → plan, selection, conclusion out | A **Power Platform custom connector** or **Azure Function** exposing the three stages as **Copilot Studio actions/tools** (e.g. a Power Automate flow per test cycle: plan at scoping, select at fieldwork start, evaluate at completion) | The sampling mathematics, run server-side. The agent narrates and files the outputs; it never re-derives a sample size or a UDL. |
| `METHODOLOGY.md` — exact solver, UDL, named rules in firing order | The **agent instructions** + grounding | The agent's contract (state the parameters before selection; the seed is the selection audit trail; over-acceptance can never be narrated as effective) and its explainability script — it can state exactly why a conclusion was reached because the named rule and the statistical statement are in the engine output. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** + the pre-deployment validation pack | The designed-scenario controls (including the planted fully-deviant stratum) become the regression set; the validation report (UDL cross-check, structural gate, measured false-assurance, monotonicity) is the governance artifact that accompanies the agent into review. |

## A note specific to attribute sampling

The selection log is the deployment-critical artifact: in a Power Automate
flow, `select` returns the seeded item list, which the flow writes to the
workpaper store BEFORE fieldwork begins — selection is then provably prior to
results, which is the property examiners probe. Evaluation output routes to the
tester's queue; CONTROL_EFFECTIVE is a statement the sample supports, never an
automatic workpaper sign-off, and the expansion decision on INCONCLUSIVE
results remains a human scoping call informed by the emitted exact guidance.

## Properties that make this clean

- **Determinism is the integration contract** — same parameters and seed in,
  same plan, selection, and conclusion out.
- **The human boundary survives deployment** — the engine computes; concluding
  on the control, signing the workpaper, and raising findings stay with the
  tester.
- **Reuse travels** — the engine is a thin layer over the shared
  `_lib/sampling.py` exact-tail mathematics, so the same primitives back any
  future sampling surface (monetary-unit sampling, QA re-testing).

Real Microsoft surfaces only — Copilot Studio actions/tools, Power Platform
custom connectors, Power Automate, Azure Functions. No integration is claimed
built; confirm current terminology against Microsoft Learn before implementation.
