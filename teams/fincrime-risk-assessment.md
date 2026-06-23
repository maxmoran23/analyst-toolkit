# Financial-Crime Risk Assessment — team hub

> This financial-crime team builds and maintains the enterprise risk picture — the inventory of financial-crime risks, the controls that offset them, and the residual exposure that remains.

## In one minute

This team answers the question every examiner, auditor, and board risk committee eventually asks: what financial-crime risks does the institution carry, what is being done about them, and how much exposure is left over after controls. The work has two halves that lock together — a risk register that scores each risk on inherent likelihood-times-impact, applies the offset from key controls, and lands on a residual rating against risk appetite; and a control inventory that documents every preventive and detective control across customer due diligence, transaction monitoring, sanctions screening, regulatory reporting, governance, and technology. "Good" looks like complete coverage with no silent gaps, ratings that a reviewer can trace back to evidence, and a clear line from each residual risk to the control that holds it down. AI is genuinely useful here for the heavy structuring work — drafting the register, laying out the control matrix, flagging coverage gaps, and rendering the workbook — which is most of the manual effort. AI cannot decide the institution's risk appetite, validate that a control actually operates as described, or sign the assessment; those remain human judgments backed by evidence.

> **In plain terms:** the tools draft the risk-and-controls picture in minutes so a human spends their time on judgment and evidence, not on building spreadsheets.

## What this team owns

- Compliance risk register — moving each risk from inherent exposure to residual exposure after controls
- AML/CFT control inventory and coverage across the six examiner domains
- Inherent and residual risk scoring, with comparison against the institution's stated risk appetite

## The toolkit for this team

| Need | Tool | Type | Where |
|---|---|---|---|
| Build a risk register with heat maps | risk-register-builder | prompt | [../prompts/controls/risk-register-builder.md](../prompts/controls/risk-register-builder.md) |
| Build an AML/CFT control matrix | control-matrix-builder | prompt | [../prompts/controls/control-matrix-builder.md](../prompts/controls/control-matrix-builder.md) |
| One-file control matrix (no setup) | control-matrix-builder (standalone) | standalone | [../standalone/control-matrix-builder.md](../standalone/control-matrix-builder.md) |
| Risk-register workbook spec | risk-register | template | [../output-templates/compliance-docs/risk-register.md](../output-templates/compliance-docs/risk-register.md) |
| Control-matrix workbook spec | control-matrix | template | [../output-templates/compliance-docs/control-matrix.md](../output-templates/compliance-docs/control-matrix.md) |
| See a finished control matrix | control-matrix-sample | sample | [../samples/compliance/control-matrix-sample.md](../samples/compliance/control-matrix-sample.md) |

## How the pieces fit

The two builder prompts are the working tools — paste one into an AI assistant, fill in the scope, and it drafts the register or the control inventory on demand. The standalone version is the same control-matrix builder packaged as a single self-contained file when there is no time to set anything up. The two templates define the exact workbook structure each builder targets (tabs, columns, scoring scales), and the sample shows what a finished control matrix actually reads like before you commit to running one. A typical pass runs: pick scope -> run builder prompt -> draft register/matrix against the template -> review the sample for the look of "done" -> render the workbook deliverable.

## Capabilities & limitations

**What these tools DO**

- Draft a full risk register (inherent L×I, key controls, residual rating, appetite comparison, dual heat maps) and a full control inventory across the six FFIEC/FATF-aligned domains
- Score and route — surface coverage gaps, tag severity, and propose remediation owners and dates for a human to confirm
- Produce structured, examiner-ready workbook deliverables in a consistent, traceable format

**What they deliberately do NOT do**

- They are reference implementations and drafting aids, not production controls or a system of record
- They score and route, but a human decides — the tools do not set risk appetite, validate control operation, or finalize ratings
- They never act on their own — no auto-blocking, no filing, no sign-off; every output is a draft pending human review against evidence

## Start here

1. Open the [control-matrix-sample](../samples/compliance/control-matrix-sample.md) to see what a finished deliverable looks like — this orients you on structure and depth in two minutes.
2. Run the [control-matrix-builder](../prompts/controls/control-matrix-builder.md) (or the [standalone](../standalone/control-matrix-builder.md) version if you want zero setup) on a small, well-understood scope to feel how the drafting works.
3. Once the control inventory is in hand, run the [risk-register-builder](../prompts/controls/risk-register-builder.md) so residual risk ratings reference the controls you just documented.

> **Coverage note.** The risk register and control matrix are fully covered by this toolkit. Enterprise-wide risk assessment (EWRA) aggregation — rolling individual registers up into a single institution-level view — is on the roadmap and not yet available here.
