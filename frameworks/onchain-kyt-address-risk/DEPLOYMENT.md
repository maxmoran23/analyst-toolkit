# Deployment — mapping to Microsoft Copilot Studio / Power Platform

Follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target architecture.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, the
> disposition engine becomes a tool an agent calls on each KYT flag; the methodology
> becomes the agent's instructions and its explanation of *why* an address was
> cleared or escalated; and the synthetic addresses become the test pack that proves
> it behaves before go-live.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `score_address` — deterministic, exposure features in → disposition out | A **Power Platform custom connector** or **Azure Function**, called as a **Copilot Studio action/tool** | The disposition logic, run server-side; the agent receives decision, risk, and the named reason, and never re-implements scoring. |
| `METHODOLOGY.md` — exposure model + posture | The **agent instructions** + grounding | The agent's contract (clear only on a named cause; never clear material proximate exposure; never freeze/file) and its explainability script. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** + pre-deployment validation pack | The synthetic addresses become the regression set; the validation report is the model-validation artifact for governance. |

## The chain-analytics dependency

This engine sits *downstream* of a chain-analytics layer (the `_lib/graph` taint
propagation in this repo, a vendor like Chainalysis / TRM / Elliptic in production)
that computes the exposure features. In a Copilot Studio deployment that vendor is a
separate connector/tool the agent calls first; the agent passes its output to this
disposition engine. The vendor's attribution is validated in its own right — the
disposition engine's evidence assumes its inputs.

## Properties that make this clean

- **Determinism is the integration contract** — same exposure features in, same
  disposition out.
- **The human boundary survives deployment** — the tool dispositions; the freeze /
  SAR / off-boarding decision stays with a person.
- **Reuse travels** — the `_lib/graph` propagation and the `_lib` matching/metrics
  primitives are shared across the pillar.

Real Microsoft surfaces only — Copilot Studio actions/tools, Power Platform custom
connectors, Power Automate, Azure Functions. No integration is claimed built; confirm
current terminology against Microsoft Learn before implementation.
