# Deployment — mapping to Microsoft Copilot Studio / Power Platform

This framework is already factored into the three assets a future Microsoft
Copilot Studio / Power Platform deployment needs, so switching licensing on is a
wiring exercise, not a rebuild. Nothing here assumes a tenant or licence today; it
describes the target architecture. The reusable version of this mapping is in
[`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).

> **In plain terms:** When the bank turns on its Microsoft AI tooling, this engine
> does not have to be rebuilt. The scoring code becomes a "tool" the AI assistant
> calls; the methodology becomes the assistant's instructions for how to explain
> itself; and the synthetic test cases become the test pack that proves the
> assistant behaves before it goes live.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `scorer.py` — deterministic logic, JSON in → disposition out | A **Power Platform custom connector** or **Azure Function**, invoked as a **Copilot Studio action/tool** | The agent calls the scoring logic as a tool. The disposition (decision, priority, named reason, components) is computed by the deterministic engine server-side and returned. The LLM never re-implements scoring. |
| `METHODOLOGY.md` — scoring spec + disposition posture | The **Copilot Studio agent instructions** and knowledge grounding | The agent's instructions encode the posture (route to a human, auto-clear only with a named reason, never auto-block) and its explainability script — it can state *why* a disposition was reached because the named reason is in the engine output. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases / Power Automate test data** and the pre-deployment validation pack | The seeded synthetic cases become the agent's regression set; `evidence/VALIDATION-REPORT.md` becomes the model-validation artifact that accompanies the agent into a governance review. |

## Architecture properties that make this clean

- **Determinism is the integration contract.** Because `scorer.py` is "same inputs
  → same disposition", it slots behind a custom connector with a documented schema.
  The non-deterministic LLM handles language and orchestration; the regulated
  decision logic stays in the deterministic tool — itself a governance-defensible
  design (the LLM does not make the screening call).
- **The human-in-the-loop boundary is preserved.** The tool returns dispositions;
  the agent presents them and assembles evidence for a person. Auto-block and
  filing stay out of the automated path — the same posture the engine enforces in
  code is the posture the agent inherits.
- **Plug-and-play, not pre-wired.** When licensing is switched on, the connector
  schema (the `Disposition` shape), the agent instructions (`METHODOLOGY.md`), and
  the test pack (`evidence/`) already exist.

## Surfaces named

Real Microsoft surfaces: Copilot Studio **actions/tools**, Power Platform **custom
connectors**, **Power Automate** flows, **Azure Functions** for the compute. This
document does not claim any integration is built — it describes how the pieces map
so the build is short when the time comes. Confirm current Copilot Studio action and
custom-connector terminology against Microsoft Learn before implementation.
