# Investigations & SAR — team hub

> The team accountable for investigating escalated financial-crime cases and producing defensible suspicious-activity narratives that withstand regulatory and audit scrutiny.

## In one minute

This team takes the cases that other functions escalate — flagged alerts, referrals, unusual activity — and works them to a conclusion: reconstructing what happened, tracing how funds moved, and writing it down in a clear, evidence-backed narrative. When the activity warrants it, that narrative becomes the basis for a suspicious-activity report. "Good" here means a narrative a regulator or examiner can read cold and follow the reasoning: every figure sourced, every actor identified, every conclusion tied to evidence, with no gaps an auditor could exploit. AI can do the heavy lifting on structure and first drafts — organizing a messy fact pattern into the standard who/what/when/where/why/how form, reconciling figures, and surfacing what's missing. AI cannot decide whether to file, cannot judge whether the activity is actually suspicious, and cannot sign anything; those are human calls that stay with the investigator and the BSA officer.

> **In plain terms:** the tools help an investigator turn a pile of facts into a clean, defensible write-up faster — but a person still decides what it means and whether to file.

## What this team owns

- Investigation and fund-flow case narratives — reconstructing escalated cases into a structured account of what happened
- Suspicious-activity report (SAR) narrative drafting — producing the defensible written narrative that supports a filing
- Figure sourcing and reconciliation — making sure every dollar amount, date, and counterparty in the narrative ties back to a verifiable source

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Draft a defensible case / SAR narrative | investigation-narrative | prompt | [../prompts/compliance/investigation-narrative.md](../prompts/compliance/investigation-narrative.md) |
| See a finished investigation narrative | investigation-narrative-sample | sample | [../samples/compliance/investigation-narrative-sample.md](../samples/compliance/investigation-narrative-sample.md) |
| Render a narrative report (PDF) | narrative-report-guide | template | [../output-templates/pdf-reports/narrative-report-guide.md](../output-templates/pdf-reports/narrative-report-guide.md) |

## How the pieces fit

The three artifacts form a short production line for a single case. The investigation-narrative prompt is the working tool — you feed it the case facts and it produces a structured first-draft narrative; the sample is the reference standard you check that draft against, showing what a finished, defensible narrative actually reads like; and the narrative-report guide is how you turn the approved text into a polished PDF deliverable for the file or for hand-off. In practice: gather case facts -> draft with the prompt -> compare against the sample and tighten -> human review and figure reconciliation -> render the PDF.

## Capabilities & limitations

**What these tools DO**

- Structure a messy fact pattern into the standard narrative form (who, what, when, where, why, how)
- Produce a defensible first draft fast, with placeholders that force figure sourcing rather than guessing
- Give a concrete reference standard so drafts are measured against a known-good example
- Render the final approved narrative into a clean, consistent PDF deliverable

**What they deliberately do NOT do**

- Make the file / no-file decision — that is a human BSA judgment, currently outside the toolkit
- Orchestrate multi-alert case management across a queue — single-case drafting only (on the roadmap)
- Pull or verify the underlying transaction data — the investigator sources and reconciles every figure
- Auto-file, auto-submit, or sign anything — the tools draft and render; a human reviews, decides, and owns the output

## Start here

1. Open the [investigation-narrative-sample](../samples/compliance/investigation-narrative-sample.md) and read it end to end — this is what "good" looks like and the standard everything is measured against.
2. Run the [investigation-narrative](../prompts/compliance/investigation-narrative.md) prompt on a real (genericized) case to produce a first-draft narrative, then check it against the sample.
3. Once the draft is reviewed and the figures are reconciled, use the [narrative-report-guide](../output-templates/pdf-reports/narrative-report-guide.md) to render the final PDF for the case file.
