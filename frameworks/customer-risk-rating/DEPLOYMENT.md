# Deployment — mapping to Microsoft Copilot Studio / Power Platform

Follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target architecture
so a future deployment is a wiring exercise, not a rebuild.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, the rating
> engine becomes a tool an agent calls at onboarding and periodic review; the
> methodology becomes the agent's instructions and its explanation of *why* a
> customer got their rating; and the synthetic customers become the test pack that
> proves it behaves before go-live.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `score_features` / `rate` — deterministic, customer attributes in → rating out | A **Power Platform custom connector** or **Azure Function**, called as a **Copilot Studio action/tool** (e.g. from a Dynamics 365 / onboarding flow) | The rating logic, run server-side; the agent receives the score, tier, factor breakdown, floors applied, and reason — and never re-implements scoring. |
| `METHODOLOGY.md` — factors, weights, floors | The **agent instructions** + knowledge grounding | The agent's behavioural contract (rate, don't decide; floors are mandatory) and its explainability script — it states the top drivers and any floor because the engine returns them. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** + pre-deployment validation pack | The designed-strata customers become the regression set; the validation report (discrimination, monotonicity, floor safety) is the model-validation artifact for governance review. |

## Properties that make this clean

- **Determinism is the integration contract** — same attributes in, same rating out.
- **The human boundary survives deployment** — the tool produces a rating; the
  onboarding/exit decision and any override stay with a person and are logged. An
  override-rate report is the natural ongoing-monitoring metric.
- **Monotonicity and floors travel with the logic** — they are properties of the
  engine, so they hold wherever the engine runs.

Real Microsoft surfaces only — Copilot Studio actions/tools, Power Platform custom
connectors, Power Automate, Azure Functions, Dataverse/Dynamics for the customer
record. No integration is claimed built; confirm current terminology against
Microsoft Learn before implementation.
