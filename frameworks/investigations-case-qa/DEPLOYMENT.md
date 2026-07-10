# Deployment — mapping to Microsoft Copilot Studio / Power Platform

This framework follows the shared pattern in [`../DEPLOYMENT-PATTERN.md`](../DEPLOYMENT-PATTERN.md).
Nothing here assumes a tenant or licence today; it describes the target
architecture so a future deployment is a wiring exercise, not a rebuild.

> **In plain terms:** When the bank turns on its Microsoft AI tooling, the QA
> engine becomes a tool an agent calls on every completed case file before
> closure; the methodology becomes the agent's instructions and its explanation
> of exactly why a file passed or came back; and the synthetic case files become
> the test pack that proves it behaves before go-live.

## The three-asset mapping

| This framework | Copilot Studio / Power Platform target | Becomes |
|---|---|---|
| `review_case` — deterministic, case record in → QA review out | A **Power Platform custom connector** or **Azure Function**, called as a **Copilot Studio action/tool** from the case-management workflow at closure | The QA grading logic, run server-side; the agent receives the disposition, quality score, dimension breakdown, and named deficiencies — and never re-implements grading. |
| `METHODOLOGY.md` — checks, severities, gate, posture | The **agent instructions** + knowledge grounding | The agent's behavioural contract (a critical deficiency can never pass; the engine grades files, humans decide cases) and its explainability script — it states *which check* fired and *why* because the engine returns it. |
| `generate_synthetic_data.py` + `evidence/` | **Test cases** + pre-deployment validation pack | The seeded case files — including the adversarial plants — become the regression set; the validation report (deficiency recall, zero critical passes, clean-file pass rate) is the model-validation artifact for governance review. |

## Properties that make this clean

- **Determinism is the integration contract** — same case record in, same QA
  review out, so the engine slots behind a connector with a documented schema
  (the `CaseFile` fields in `scorer.py`).
- **The human-in-the-loop boundary survives deployment** — the tool returns a
  graded review with named deficiencies; reopening a case, changing an
  investigative disposition, and any filing decision stay with people. A
  REWORK_AND_ESCALATE routes to the investigations supervisor as a notification
  in the flow, never as an automated case action.
- **The safety gate travels with the logic** — the no-pass rule for critical
  deficiencies is a property of the engine, so it holds wherever the engine
  runs; the evidence pack demonstrates it to reviewers before go-live.

Real Microsoft surfaces only — Copilot Studio actions/tools, Power Platform
custom connectors, Power Automate flows, Azure Functions, Dataverse for the
case record. No integration is claimed built; confirm current terminology
against Microsoft Learn before implementation.
