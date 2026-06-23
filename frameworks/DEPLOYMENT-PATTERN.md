# Deployment pattern — frameworks → Microsoft Copilot Studio / Power Platform

The reusable version of the per-framework `DEPLOYMENT.md`. Every framework in this
pillar is factored so that a future Microsoft Copilot Studio / Power Platform
deployment is a wiring exercise, not a rebuild. Nothing here assumes a tenant or
licence today; this describes the target architecture so the build is short when
licensing is switched on.

> **In plain terms:** Each framework is already split into the three things a
> Microsoft AI agent needs — the calculator, the instructions, and the test pack —
> so the bank can stand one up quickly once its Microsoft AI tooling is enabled,
> without rebuilding the logic.

## The three-asset mapping (applies to every framework)

| Framework asset | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `scorer.py` / engine — deterministic, JSON in → disposition out | A **Power Platform custom connector** or **Azure Function**, called as a **Copilot Studio action/tool** | The regulated decision logic, run server-side and returned to the agent. The LLM orchestrates and narrates; it never re-implements scoring. |
| `METHODOLOGY.md` — spec + posture | The **agent instructions** and knowledge grounding | The agent's behavioural contract and explainability script — it can state *why* a disposition was reached because the named reason is in the engine output. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** and the **pre-deployment validation pack** | The seeded cases become the agent's regression set; the validation report is the governance artifact that accompanies the agent into review. |

## Why the architecture is governance-defensible

- **Determinism is the integration contract.** A "same inputs → same disposition"
  engine slots cleanly behind a connector with a documented schema. The
  non-deterministic LLM stays out of the regulated decision; it handles language
  and workflow.
- **The human-in-the-loop boundary survives deployment.** The tool returns
  dispositions and assembled evidence; a person decides. Auto-block and filing stay
  out of the automated path — the posture the engine enforces in code is the posture
  the agent inherits.
- **Plug-and-play, not pre-wired.** The connector schema (the disposition shape),
  the agent instructions, and the test pack already exist in each package.

## Vendor accuracy

Real Microsoft surfaces only — Copilot Studio **actions/tools**, Power Platform
**custom connectors**, **Power Automate** flows, **Azure Functions** for compute.
No integration is claimed to be built. Confirm current terminology against Microsoft
Learn before implementation.
