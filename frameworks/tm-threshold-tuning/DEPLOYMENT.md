# Deployment — mapping to Microsoft Copilot Studio / Power Platform

Follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target architecture.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, the tuning
> engine becomes a tool an agent runs on each monitoring rule on a schedule; the
> methodology becomes the agent's instructions and its explanation of *why* a
> threshold should move; and the synthetic rules become the test pack that proves it
> recommends safely before go-live.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `tune_rule` — deterministic, rule population in → recommendation out | A **Power Platform custom connector** or **Azure Function**, called as a **Copilot Studio action/tool** (e.g. on a Power Automate schedule per rule) | The ATL/BTL tuning logic, run server-side over the rule's labelled population; the agent receives the action, recommended threshold, and ATL/BTL evidence. |
| `METHODOLOGY.md` — ATL/BTL framing, safety posture | The **agent instructions** + grounding | The agent's contract (recommend the leanest threshold holding detection at the floor; never trade detection for volume; lower any leaking rule) and its explainability script. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** + the model-validation pack | The designed-scenario rules become the regression set; the validation report (safety, leak remediation, direction accuracy) is the model-validation artifact for the rule-tuning model itself. |

## A note specific to threshold tuning

This framework *is* the outcomes-analysis and ongoing-monitoring component of model
risk management for a monitoring rule set. In a deployment it would run on a cadence
(quarterly / semi-annually) and produce the ATL/BTL evidence pack that goes to a
governance committee. Its output is a model-change *proposal*, never an automatic
change — the human-in-the-loop boundary here is the model-change-control process
itself.

## Properties that make this clean

- **Determinism is the integration contract** — same population in, same
  recommendation out.
- **The human boundary survives deployment** — the engine recommends; approving and
  applying a threshold change is a governed, documented decision.
- **Reuse travels** — the engine is a thin layer over the shared `_lib/metrics`
  sweep, so it composes with the same metrics the scoring frameworks report.

Real Microsoft surfaces only — Copilot Studio actions/tools, Power Platform custom
connectors, Power Automate, Azure Functions. No integration is claimed built; confirm
current terminology against Microsoft Learn before implementation.
