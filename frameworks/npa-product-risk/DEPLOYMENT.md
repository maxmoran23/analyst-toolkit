# Deployment — mapping to Microsoft Copilot Studio / Power Platform

Follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target architecture
so a future deployment is a wiring exercise, not a rebuild.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, the
> assessment engine becomes a tool an agent calls when a product proposal is
> submitted; the methodology becomes the agent's instructions and its explanation
> of *why* a proposal got its tier, route, and conditions; and the synthetic
> proposals become the test pack that proves it behaves before go-live.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `score_features` / `assess` — deterministic, proposal attributes in → assessment out | A **Power Platform custom connector** or **Azure Function**, called as a **Copilot Studio action/tool** (e.g. from a Power Apps proposal-intake form or a Power Automate approval flow) | The assessment logic, run server-side; the agent receives the score, tier, routing, factor breakdown, floors applied, prohibited attributes, conditions, and review interval — and never re-implements scoring. |
| `METHODOLOGY.md` — factors, weights, floors, prohibited list, routing map | The **agent instructions** + knowledge grounding | The agent's behavioural contract (route, don't approve; floors and the prohibited list are mandatory) and its explainability script — it states the top drivers, any floor, and every condition because the engine returns them. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** + pre-deployment validation pack | The designed-strata proposals become the regression set; the validation report (discrimination, monotonicity, floor safety, prohibited routing) is the model-validation artifact for governance review. |

## Properties that make this clean

- **Determinism is the integration contract** — same proposal attributes in,
  same assessment out.
- **The human boundary survives deployment** — the tool produces a tier, a
  route, and named conditions; the launch decision, condition confirmations,
  waivers, and any override stay with the committee and are logged. Override
  and waiver rates are the natural ongoing-monitoring metrics.
- **The prohibited gate travels with the logic** — REFER_PROHIBITED is a
  property of the engine, so no agent prompt or workflow branch can score
  around the list wherever the engine runs.
- **Conditions map to workflow** — each named condition is a natural Power
  Automate approval step (screening-coverage confirmation, monitoring-coverage
  check, third-party due-diligence completion), and the post-launch review
  interval is a scheduled follow-up task.

Real Microsoft surfaces only — Copilot Studio actions/tools, Power Platform
custom connectors, Power Automate, Azure Functions, Power Apps / Dataverse for
the proposal record. No integration is claimed built; confirm current
terminology against Microsoft Learn before implementation.
