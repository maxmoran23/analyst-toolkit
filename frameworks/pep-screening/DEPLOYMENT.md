# Deployment — mapping to Microsoft Copilot Studio / Power Platform

Follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target
architecture so the build is short when licensing is switched on.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, this
> engine does not have to be rebuilt. The scoring code becomes a tool the AI
> assistant calls on each PEP alert; the methodology becomes the assistant's
> instructions and its script for explaining *why* an alert was cleared or
> escalated; and the synthetic alerts become the test pack that proves the
> assistant behaves before go-live.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `score_alert` — deterministic, customer + entry in → disposition out | A **Power Platform custom connector** or **Azure Function**, called as a **Copilot Studio action/tool** | The disposition logic, run server-side; the agent receives decision, match_strength, materiality, and the named reason, and never re-implements scoring. |
| `METHODOLOGY.md` — two-axis logic, tier/decay/jurisdiction tables, posture | The **agent instructions** + knowledge grounding | The agent's behavioural contract (clear only on a named cause; never clear a current PEP, a TIER_1/TIER_2 entry, or a corroborated match) and its explainability script. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** + pre-deployment validation pack | The labelled synthetic alerts — including the adversarial plants — become the regression set; the validation report is the model-validation artifact for governance review. |

## Notes specific to PEP screening

- **The list vendor is part of the model.** Tier, status, years-since-left, and
  adverse flags arrive from the PEP-list provider. In a Copilot Studio
  deployment those fields flow through the connector as inputs; the deployment's
  governance package must cover the vendor's field accuracy, because a vendor
  error upstream becomes a disposition error downstream.
- **Axis B parameters are configuration, not code.** Step-down horizons,
  tier weights, and jurisdiction buckets should be surfaced as environment
  configuration (a Dataverse table or environment variables) with change
  control, so a policy update is a governed configuration change — not a code
  release.
- **Reuse travels.** The entity-resolution core (`_lib/match`) is shared with
  the sanctions and adverse-media frameworks, so one matching connector can
  serve all three screening agents.

## Properties that make this clean

- **Determinism is the integration contract** — same customer + entry in, same
  disposition out, behind a documented schema.
- **The human boundary survives deployment** — the tool dispositions and
  assembles evidence; the onboarding, enhanced-review, or exit decision stays
  with a person. The posture the engine enforces in code is the posture the
  agent inherits.
- **Plug-and-play, not pre-wired** — the connector schema (the `Disposition`
  shape), the agent instructions (`METHODOLOGY.md`), and the test pack
  (`evidence/`) already exist.

Real Microsoft surfaces only — Copilot Studio **actions/tools**, Power Platform
**custom connectors**, **Power Automate** flows, **Azure Functions** for
compute. No integration is claimed built; confirm current terminology against
Microsoft Learn before implementation.
