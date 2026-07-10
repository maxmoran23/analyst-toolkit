# Deployment — mapping to Microsoft Copilot Studio / Power Platform

This framework follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target
architecture so a future deployment is a wiring exercise, not a rebuild.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, the
> data-quality engine becomes a "tool" an agent calls on each inbound customer
> file, the methodology becomes the agent's instructions and explainability
> script, and the synthetic extracts become the test pack that proves it
> behaves before go-live. The agent narrates the scorecard and routes the
> verdict; it never re-derives the verdict itself.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `scorer.py` — deterministic, extract in → scorecard + disposition out | A **Power Platform custom connector** or **Azure Function**, called as a **Copilot Studio action/tool** (triggered per batch by a **Power Automate** flow when a feed lands) | The feed-acceptance logic, run server-side; the agent receives the per-CDE scorecard, the record-level defect list, and the disposition with its named reason, and never re-implements the rules. |
| `METHODOLOGY.md` — CDE inventory, rules, thresholds, posture | The **agent instructions** + knowledge grounding | The agent's behavioural contract (a screening-critical breach is always BLOCK; never drop or repair a record; FEED_PASS only on the named provable cause) and its explainability script — it states *which CDE*, *which rule*, and *why* because the engine returns them. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** + pre-deployment validation pack | The seeded extracts (including the adversarial plants and the five disposition scenarios) become the regression set; the validation report is the model-validation artifact for governance review. |

## Properties that make this clean

- **Determinism is the integration contract** — same extract in, same
  scorecard and disposition out, so the engine slots behind a connector with a
  documented schema (feed id + rows in; disposition, reason, per-CDE rates,
  defect list out).
- **The human-in-the-loop boundary survives deployment** — the tool returns
  the disposition and the assembled defect evidence; the data-governance owner
  decides whether to hold, remediate, or formally accept. Auto-repair,
  auto-drop, and autonomous feed acceptance are never in the automated path.
- **The defect list is the workflow payload** — each entry already carries the
  named rule, CDE, severity, and detail string, which maps directly onto a
  Power Automate remediation-queue item or Dataverse row.
- **Plug-and-play, not pre-wired** — the connector schema, the agent
  instructions, and the test pack already exist in this package.

Real Microsoft surfaces only — Copilot Studio actions/tools, Power Platform
custom connectors, Power Automate flows, Azure Functions. No integration is
claimed built; confirm current terminology against Microsoft Learn before
implementation.
