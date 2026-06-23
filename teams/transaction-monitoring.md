# Transaction Monitoring — team hub

> This team detects, investigates, and dispositions suspicious transaction activity, and keeps the monitoring rules calibrated so the right alerts fire and the wrong ones do not.

## In one minute

This team watches transaction activity for signs of money laundering and other financial crime, decides which alerts are worth a closer look, works each one to a defensible close-or-escalate outcome, and tunes the underlying detection rules so the alert volume stays both complete and manageable. "Good" looks like every genuinely suspicious pattern getting caught (high recall), analysts not drowning in false positives, every disposition backed by a clear written rationale, and every threshold change supported by evidence rather than gut feel. AI in this toolkit can read an alert and draft a structured first-pass narrative, score and rank a large alert backlog so the riskiest items surface first, translate a money-laundering typology into concrete detection logic, and produce the above/below-the-line evidence needed to justify a rule change. What AI cannot do here is make the final call: it does not block accounts, file regulatory reports, or change a production rule on its own — it prepares the work and a qualified human decides.

> **In plain terms:** these tools read, score, and explain the alerts and rules so analysts spend their time deciding, not sorting.

## What this team owns

- Alert triage — working each transaction-monitoring alert through to a close or escalate disposition with a documented rationale.
- Typology-to-rule decomposition — turning a known laundering pattern into the specific detection logic that would catch it.
- Behavioral alert scoring at scale — ranking large volumes of alerts so the highest-risk activity is reviewed first.
- Threshold tuning and ATL/BTL testing — adjusting rule thresholds and proving, with above-the-line and below-the-line samples, that the change is sound.

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Score & triage TM alerts at scale | transaction-monitoring | framework (runnable, recall 1.0, 85% FP-cut) | [../frameworks/transaction-monitoring/](../frameworks/transaction-monitoring/) |
| Tune a rule threshold with ATL/BTL evidence | tm-threshold-tuning | framework (runnable, model-validation) | [../frameworks/tm-threshold-tuning/](../frameworks/tm-threshold-tuning/) |
| Work a single alert to a disposition ad hoc | alert-triage | prompt | [../prompts/compliance/alert-triage.md](../prompts/compliance/alert-triage.md) |
| Turn a typology into detection-rule logic | typology-detection-mapping | prompt | [../prompts/compliance/typology-detection-mapping.md](../prompts/compliance/typology-detection-mapping.md) |
| One-file alert triage (no setup) | alert-triage (standalone) | standalone | [../standalone/alert-triage.md](../standalone/alert-triage.md) |
| Look up laundering typologies | aml-typologies | reference | [../reference/aml-typologies.md](../reference/aml-typologies.md) |
| See a finished alert disposition | alert-triage-sample | sample | [../samples/compliance/alert-triage-sample.md](../samples/compliance/alert-triage-sample.md) |

## How the pieces fit

The two prompts are for ad-hoc, one-at-a-time work: the alert-triage prompt walks a single alert to a disposition, and the typology-detection-mapping prompt converts a laundering pattern into rule logic, both leaning on the aml-typologies reference for the underlying patterns. The two frameworks are the at-scale engines: the transaction-monitoring framework scores and ranks a whole alert backlog, while the tm-threshold-tuning framework produces the ATL/BTL evidence behind a rule change. The standalone file is a zero-setup version of triage for a quick one-off, and the sample shows what a finished disposition reads like.

Typical chain: aml-typologies -> typology-detection-mapping (define the rule) -> transaction-monitoring (score the resulting alerts at scale) -> alert-triage (work the surfaced alerts to disposition) -> tm-threshold-tuning (test and recalibrate the rule).

## Capabilities & limitations

**What these tools DO**

- Score and rank alerts so the highest-risk items are reviewed first, and draft a structured disposition rationale for each.
- Decompose a typology into concrete, testable detection-rule logic.
- Generate above- and below-the-line samples and the supporting evidence needed to justify a threshold change.
- Give analysts a consistent, repeatable triage format and a worked example to anchor quality.

**What they deliberately do NOT do**

- They do not auto-close, auto-escalate, auto-block, or file a SAR — a qualified analyst makes every final decision.
- They do not change production monitoring rules; they produce the evidence so a human can approve and implement a change through the normal model-governance path.
- The frameworks are reference implementations for analysis and validation, not production monitoring controls.
- They do not connect to live customer or transaction systems on their own, and use only generic, illustrative data — no real institution or non-public information.

## Start here

1. Read the [alert-triage-sample](../samples/compliance/alert-triage-sample.md) to see what a finished, defensible disposition looks like.
2. Take one real-shaped (illustrative) alert and run it through the [alert-triage](../prompts/compliance/alert-triage.md) prompt — or the [standalone version](../standalone/alert-triage.md) if you want zero setup.
3. When you are ready to work at volume, point the [transaction-monitoring framework](../frameworks/transaction-monitoring/) at a batch of alerts to score and rank them, then review the top of the list first.
