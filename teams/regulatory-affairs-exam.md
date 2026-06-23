# Regulatory Affairs & Exam — team hub

> This financial-crime team is accountable for knowing what regulators expect, turning those expectations into tracked obligations, finding where policy falls short, and standing up clean, defensible responses when examiners ask.

## In one minute

This team watches the regulatory landscape, reads new and amended rules, and translates them into concrete obligations the institution can be measured against. It then checks those obligations against existing policies and procedures to surface gaps before an examiner does, and assembles the evidence and narrative when a regulator opens an examination or sends a request for information. "Good" looks like a current obligation register, gaps that are identified and owned before they become findings, and exam responses that are complete, consistent, and traceable to source. AI accelerates the reading-heavy front end of this work — scanning sources, drafting obligation registers, flagging likely policy gaps, and assembling a first-draft response pack — so analysts spend their time judging, not transcribing. What AI cannot do here is decide whether a gap is acceptable, sign an attestation, or speak for the institution to a regulator; every output is a draft a qualified person reviews, corrects, and owns.

> **In plain terms:** the tools read the rulebooks and draft the homework fast, but a human still checks it and turns it in.

## What this team owns

- Regulatory landscape and change monitoring across relevant jurisdictions and agencies
- Extracting discrete, trackable obligations from a regulation into an obligation register
- Comparing obligations against current policies and procedures to find gaps
- Coordinating examination and request-for-information (RFI) responses end to end
- Scoring jurisdiction and geopolitical risk to prioritize attention and coverage

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Scan the regulatory landscape | regulatory-intelligence-scan | prompt | [../prompts/regulatory/regulatory-intelligence-scan.md](../prompts/regulatory/regulatory-intelligence-scan.md) |
| Extract obligations from a regulation | obligation-extraction | prompt | [../prompts/regulatory/obligation-extraction.md](../prompts/regulatory/obligation-extraction.md) |
| Run a policy gap analysis | policy-gap-analysis | prompt | [../prompts/regulatory/policy-gap-analysis.md](../prompts/regulatory/policy-gap-analysis.md) |
| Build an exam / RFI response pack | exam-response-pack | prompt | [../prompts/regulatory/exam-response-pack.md](../prompts/regulatory/exam-response-pack.md) |
| Score jurisdiction / geopolitical risk | geopolitical-risk-monitor | prompt | [../prompts/regulatory/geopolitical-risk-monitor.md](../prompts/regulatory/geopolitical-risk-monitor.md) |
| Regulatory-intelligence reference | regulatory-intelligence | reference | [../reference/regulatory-intelligence.md](../reference/regulatory-intelligence.md) |
| See a finished obligation register | obligation-extraction-sample | sample | [../samples/reports/obligation-extraction-sample.md](../samples/reports/obligation-extraction-sample.md) |

## How the pieces fit

The prompts chain from broad to specific: a landscape scan finds what changed, obligation extraction turns a chosen regulation into a structured register, gap analysis tests that register against current policy, and the response pack packages findings and evidence for an examiner. The geopolitical-risk-monitor runs alongside to prioritize which jurisdictions and rules deserve attention first. The reference document grounds all of these in shared definitions and source expectations, while the sample shows the target shape of a finished obligation register before you start.

Typical flow: regulatory-intelligence-scan -> obligation-extraction -> policy-gap-analysis -> exam-response-pack (with geopolitical-risk-monitor steering priority, regulatory-intelligence as the reference, and the obligation-extraction-sample as the worked example).

## Capabilities & limitations

**What these tools DO**

- Scan, read, and summarize large volumes of regulatory text and turn rules into structured, trackable obligations
- Surface candidate policy gaps and assemble a first-draft, evidence-linked exam or RFI response
- Score and rank jurisdiction and geopolitical risk to focus the team's attention
- Produce consistent, source-referenced drafts a reviewer can verify and stand behind

**What they deliberately do NOT do**

- Decide whether a gap is acceptable, set risk appetite, or sign an attestation — a human owns the judgment
- Serve as production controls or a system of record; the prompts and references are reference implementations, not live monitoring
- Speak to a regulator, submit a response, or take any external action on the team's behalf
- Replace authoritative legal interpretation or counsel sign-off on what a rule requires

## Start here

1. Read the [regulatory-intelligence](../reference/regulatory-intelligence.md) reference to understand the shared vocabulary and what each output is expected to contain.
2. Open the [obligation-extraction-sample](../samples/reports/obligation-extraction-sample.md) to see what a finished obligation register looks like before producing your own.
3. Pick one recent regulation and run [obligation-extraction](../prompts/regulatory/obligation-extraction.md) on it, then take that register into [policy-gap-analysis](../prompts/regulatory/policy-gap-analysis.md) to see the chain end to end.

---

*Coverage note: this toolkit is mature for landscape monitoring, obligation extraction, gap analysis, exam response, and jurisdiction risk scoring. Dedicated horizon scanning of emerging (not-yet-final) rules is on the roadmap.*
