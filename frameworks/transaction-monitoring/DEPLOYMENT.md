# Deployment — mapping to Microsoft Copilot Studio / Power Platform

This framework follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target architecture
so a future deployment is a wiring exercise, not a rebuild.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, the scoring
> engine becomes a "tool" an agent calls, the methodology becomes the agent's
> instructions and explainability script, and the synthetic alerts become the test
> pack that proves it behaves before go-live.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `scorer.py` — deterministic, alert features in → disposition out | A **Power Platform custom connector** or **Azure Function**, called as a **Copilot Studio action/tool** | The TM scoring logic, run server-side; the agent receives the disposition (decision, priority, named reason, fired rules, typology hits) and never re-implements scoring. |
| `METHODOLOGY.md` — rules, thresholds, posture | The **agent instructions** + knowledge grounding | The agent's behavioural contract (never auto-close a typology, never file a SAR) and its explainability script — it states *which rule* and *why* because the engine returns it. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** + pre-deployment validation pack | Seeded synthetic alerts become the regression set; the validation report is the model-validation artifact for governance review. |

## Properties that make this clean

- **Determinism is the integration contract** — same alert features in, same
  disposition out, so the engine slots behind a connector with a documented schema.
- **The human-in-the-loop boundary survives deployment** — the tool returns
  dispositions and assembled evidence; the SAR decision stays with an investigator.
  Auto-file is never in the automated path.
- **Plug-and-play, not pre-wired** — the connector schema, the agent instructions,
  and the test pack already exist.

Real Microsoft surfaces only — Copilot Studio actions/tools, Power Platform custom
connectors, Power Automate flows, Azure Functions. No integration is claimed built;
confirm current terminology against Microsoft Learn before implementation.
