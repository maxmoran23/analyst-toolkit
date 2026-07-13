# Fraud — team hub

> This financial-crime team detects, investigates, and dispositions fraud committed against the institution's customers and against the institution itself.

## In one minute

This team handles fraud — distinct from money laundering, though they overlap. Its
daily work is scams where a customer is tricked into paying a fraudster, payment fraud
where an account or instruction is compromised, check and deposit fraud, and the
detection of money-mule accounts that move the proceeds. "Good" looks like fast, fair
dispositions that recover funds where a window still exists, protect vulnerable victims,
and feed detection learnings back into the rules — all documented well enough to defend.
AI in this toolkit can classify a scam, score the fraud and mule indicators, draft the
disposition and the reimbursement view, and turn a fraud pattern into detection logic.
What it cannot do is decide: it never holds, recalls, reimburses, or files on its own —
it prepares the case and a human acts.

> **In plain terms:** the tools read a fraud case, say what kind it is and how strong
> the signals are, and draft the call — a person makes it.

## What this team owns

- Authorized-push-payment (APP) / scam triage and the reimbursement-vs-liability view
- Wire and payment fraud disposition (business email compromise, account takeover, unauthorized)
- Check and deposit fraud analysis (counterfeit, altered, forged, kiting, double-presentment)
- Money-mule account detection and network review
- Translating fraud typologies into detection-rule logic and controls

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Triage an APP / scam case | app-fraud-triage | prompt | [../prompts/fraud/app-fraud-triage.md](../prompts/fraud/app-fraud-triage.md) |
| Disposition a flagged wire/payment for fraud | wire-fraud-disposition | prompt | [../prompts/fraud/wire-fraud-disposition.md](../prompts/fraud/wire-fraud-disposition.md) |
| Analyze a check / deposit fraud case | check-fraud-analysis | prompt | [../prompts/fraud/check-fraud-analysis.md](../prompts/fraud/check-fraud-analysis.md) |
| Assess an account for money-mule indicators | mule-account-review | prompt | [../prompts/fraud/mule-account-review.md](../prompts/fraud/mule-account-review.md) |
| Turn a fraud typology into detection logic | fraud-typology-mapping | prompt | [../prompts/fraud/fraud-typology-mapping.md](../prompts/fraud/fraud-typology-mapping.md) |
| Triage transaction/session fraud at volume | fraud-detection | framework | [../frameworks/fraud-detection/](../frameworks/fraud-detection/) |
| Trace where mule funds went on-chain | fund-flow-tracing | prompt | [../prompts/blockchain/fund-flow-tracing.md](../prompts/blockchain/fund-flow-tracing.md) |
| Render any output as Word/Excel/PDF/HTML | BASE.md | companion | [../BASE.md](../BASE.md) |

## How the pieces fit

A reported scam starts at app-fraud-triage; a system-flagged payment starts at
wire-fraud-disposition; a returned or suspect item at check-fraud-analysis. Any of these
can surface a receiving account worth a closer look, which routes to mule-account-review
(and, for crypto, fund-flow-tracing). Patterns that recur feed fraud-typology-mapping,
which turns them into detection rules so the next case is caught earlier. Flow:
report/flag -> triage & disposition -> mule/network review -> typology -> detection rule.

## Capabilities & limitations

**What these tools DO**

- Classify the fraud, score the indicators, and draft a defensible disposition and action set
- Frame a reimbursement / liability view as a recommendation for human adjudication
- Surface mule and network links to expand an investigation
- Convert observed fraud patterns into implementable detection logic

**What they deliberately do NOT do**

- They analyze and recommend; a human makes every hold, recall, reimbursement, or filing decision
- The reimbursement view is a generic framework, not legal advice — local rules and policy govern
- They work from the case facts provided; they do not connect to payment systems or move money

## Start here

1. Pick the entry point that matches the case — [app-fraud-triage](../prompts/fraud/app-fraud-triage.md) for a reported scam, [wire-fraud-disposition](../prompts/fraud/wire-fraud-disposition.md) for a flagged payment.
2. If a receiving account looks suspect, run [mule-account-review](../prompts/fraud/mule-account-review.md) on it.
3. When a pattern repeats, capture it once with [fraud-typology-mapping](../prompts/fraud/fraud-typology-mapping.md) so detection improves — and render the case record with [BASE.md](../BASE.md).
