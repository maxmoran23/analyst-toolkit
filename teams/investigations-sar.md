# Investigations & SAR — team hub

> The team accountable for investigating escalated financial-crime cases, deciding whether the activity warrants a filing, and producing defensible suspicious-activity narratives that withstand regulatory and audit scrutiny.

## In one minute

This team takes the cases that other functions escalate — flagged alerts, referrals,
unusual activity — and works them to a conclusion: reconstructing what happened, tracing
how funds moved, unwinding who is actually behind the counterparty, and writing it down
in a clear, evidence-backed narrative. When the activity warrants it, that narrative
becomes the basis for a suspicious-activity report. "Good" here means a narrative a
regulator or examiner can read cold and follow the reasoning: every figure sourced, every
actor identified, every conclusion tied to evidence, with no gaps an auditor could
exploit — and a second-line reviewer who checks the finished file before it closes. AI
can do the heavy lifting on structure and first drafts: organizing a messy fact pattern
into the standard who/what/when/where/why/how form, reconciling figures, working an
investigation through the elements-of-suspicion checklist to a documented file / no-file
memo, and grading a finished case file against named QA checks. AI cannot decide whether
to file, cannot judge whether the activity is actually suspicious, and cannot sign
anything; those are human calls that stay with the investigator and the BSA officer.

> **In plain terms:** the tools help an investigator turn a pile of facts into a clean,
> defensible write-up faster, and check the finished file before it closes — but a person
> still decides what it means and whether to file.

## What this team owns

- Investigation and fund-flow case narratives — reconstructing escalated cases into a structured account of what happened
- The file / no-file decision and its documentation — the elements-of-suspicion analysis, the deadline arithmetic, and the memo that records either outcome
- Suspicious-activity report (SAR) narrative drafting — producing the defensible written narrative that supports a filing
- Beneficial-ownership unwinding — establishing who ultimately owns and controls the counterparty
- Entity network and link analysis — finding the shared attributes, hubs, and flow-through patterns that connect a case to others
- Periodic-review triage — prioritizing which customer files get re-examined, and why
- Second-line case QA — checking a finished file for completeness, evidence support, and internal consistency before closure
- Figure sourcing and reconciliation — making sure every dollar amount, date, and counterparty in the narrative ties back to a verifiable source

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| QA a finished case file before it closes | investigations-case-qa | framework (runnable, critical-deficiency recall 1.0, 0 deficient files passed) | [../frameworks/investigations-case-qa/](../frameworks/investigations-case-qa/) |
| Draft a defensible case / SAR narrative | investigation-narrative | prompt | [../prompts/compliance/investigation-narrative.md](../prompts/compliance/investigation-narrative.md) |
| Work an investigation to a documented file / no-file memo | sar-decisioning | prompt | [../prompts/compliance/sar-decisioning.md](../prompts/compliance/sar-decisioning.md) |
| Second-line QA review of one completed case file | case-qa-review | prompt | [../prompts/compliance/case-qa-review.md](../prompts/compliance/case-qa-review.md) |
| Unwind an ownership chain to the real owners | ubo-beneficial-ownership | prompt | [../prompts/compliance/ubo-beneficial-ownership.md](../prompts/compliance/ubo-beneficial-ownership.md) |
| Map shared attributes, hubs, and rings across entities | network-link-analysis | prompt | [../prompts/compliance/network-link-analysis.md](../prompts/compliance/network-link-analysis.md) |
| Triage and prioritize a periodic-review backlog | periodic-review-triggers | prompt | [../prompts/compliance/periodic-review-triggers.md](../prompts/compliance/periodic-review-triggers.md) |
| Trace where the funds actually went on-chain | fund-flow-tracing | prompt | [../prompts/blockchain/fund-flow-tracing.md](../prompts/blockchain/fund-flow-tracing.md) |
| See a finished investigation narrative | investigation-narrative-sample | sample | [../samples/compliance/investigation-narrative-sample.md](../samples/compliance/investigation-narrative-sample.md) |
| Render a narrative report (PDF) | narrative-report-guide | template | [../output-templates/pdf-reports/narrative-report-guide.md](../output-templates/pdf-reports/narrative-report-guide.md) |

## How the pieces fit

The pieces form a production line for a single case, then a gate at the end of it. A case
arrives; ubo-beneficial-ownership establishes who is really behind the counterparty and
network-link-analysis surfaces the entities it touches; fund-flow-tracing follows the
money where the case is on-chain. investigation-narrative turns the resulting fact pattern
into a structured, sourced first draft, and the sample is the reference standard you check
that draft against. sar-decisioning then works the completed investigation through the
elements-of-suspicion checklist to a documented file / no-file memo with the deadline
arithmetic laid out — the memo is the output, the filing decision stays with the BSA
officer. Before the file closes, case-qa-review gives it a second-line read, and the
investigations-case-qa framework does the structural half of that review at queue scale,
holding one unbreakable rule: a file with a critical defect — a conclusion no evidence
supports, an unescalated red flag, a missing required section — can never pass QA,
however polished the rest of it reads. periodic-review-triggers decides which customers
come back around. Flow: escalation -> ownership & network -> trace -> narrative ->
file/no-file memo -> QA gate -> render the PDF for the case file.

## Capabilities & limitations

**What these tools DO**

- Structure a messy fact pattern into the standard narrative form (who, what, when, where, why, how)
- Produce a defensible first draft fast, with placeholders that force figure sourcing rather than guessing
- Work an investigation through a named elements-of-suspicion checklist to a documented decision memo — for a no-file outcome as rigorously as for a filing
- Unwind effective ownership and control, and separate observed relationships from inferred ones in network analysis
- Grade a finished case file against named critical checks and weighted dimensions, and route it PASS / REMEDIATE / REWORK
- Give a concrete reference standard so drafts are measured against a known-good example, and render the approved narrative into a clean PDF

**What they deliberately do NOT do**

- Make the file / no-file decision — the toolkit builds the analysis and the memo; the BSA officer decides and signs
- Judge whether activity is genuinely suspicious, or substitute for the investigator's judgment on any element
- Pass a critically deficient case file — the QA engine has no override, and it grades structure, never the quality of an investigator's reasoning
- Pull or verify the underlying transaction data — the investigator sources and reconciles every figure
- Auto-file, auto-submit, or sign anything; and the framework, like every framework here, is a reference implementation rather than a production control

## Start here

1. Open the [investigation-narrative-sample](../samples/compliance/investigation-narrative-sample.md) and read it end to end — this is what "good" looks like and the standard everything is measured against.
2. Run the [investigation-narrative](../prompts/compliance/investigation-narrative.md) prompt on a real (genericized) case to produce a first-draft narrative, then take it through [sar-decisioning](../prompts/compliance/sar-decisioning.md) to see the file / no-file analysis written down properly.
3. Before you close the file, run [case-qa-review](../prompts/compliance/case-qa-review.md) on it — and read the [investigations-case-qa](../frameworks/investigations-case-qa/) framework to understand the critical checks that can never be scored around. Then render the final PDF with the [narrative-report-guide](../output-templates/pdf-reports/narrative-report-guide.md).
