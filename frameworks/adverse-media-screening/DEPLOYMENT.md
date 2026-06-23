# Deployment — mapping to Microsoft Copilot Studio / Power Platform

Follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target architecture.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, the
> disposition engine becomes a tool an agent calls on each media hit; the
> methodology becomes the agent's instructions and its explanation of *why* a hit
> was cleared or escalated; and the synthetic hits become the test pack that proves
> it behaves before go-live.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `score_hit` — deterministic, subject + hit in → disposition out | A **Power Platform custom connector** or **Azure Function**, called as a **Copilot Studio action/tool** | The disposition logic, run server-side; the agent receives decision, entity_strength, relevance, and the named reason, and never re-implements scoring. |
| `METHODOLOGY.md` — entity + relevance logic, posture | The **agent instructions** + grounding | The agent's contract (clear only on a named cause; never clear an unidentifiable common-name match) and its explainability script. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** + pre-deployment validation pack | The labelled synthetic hits become the regression set; the validation report is the model-validation artifact for governance. |

## A note specific to adverse media

This engine sits *downstream* of a media-classification model (which produces
`category` and `role`) and *reuses* the sanctions entity-resolution logic. In a
Copilot Studio deployment, the classifier and the matcher are separate tools the
agent orchestrates; the agent assembles their outputs and calls this disposition
engine. Each upstream model is validated in its own right — the disposition engine's
evidence assumes its inputs, and the deployment's governance package must cover the
classifier too.

## Properties that make this clean

- **Determinism is the integration contract** — same subject + hit in, same
  disposition out.
- **The human boundary survives deployment** — the tool dispositions; the
  enhanced-review / exit / SAR decision stays with a person.
- **Reuse travels** — the entity-resolution tool is shared with sanctions screening,
  so one connector serves both.

Real Microsoft surfaces only — Copilot Studio actions/tools, Power Platform custom
connectors, Power Automate, Azure Functions. No integration is claimed built; confirm
current terminology against Microsoft Learn before implementation.
