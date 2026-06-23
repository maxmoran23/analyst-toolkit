# Fraud detection & investigation prompts

These prompts cover the fraud lifecycle — distinct from money laundering: scams,
payment fraud, account misuse, and the detection logic behind them. Each turns an AI
assistant into a specific fraud-analyst role with a defined method, indicator set, and
structured disposition.

| Prompt | What it does |
|--------|--------------|
| [app-fraud-triage](app-fraud-triage.md) | Triage an authorized-push-payment (APP) / scam case: scam-type classification, beneficiary and victim indicators, reimbursement/liability view, recommended actions |
| [wire-fraud-disposition](wire-fraud-disposition.md) | Disposition a flagged wire/payment for fraud (BEC, account takeover, unauthorized): indicators, hold / release / recall decision with the verification step needed |
| [check-fraud-analysis](check-fraud-analysis.md) | Analyze a check/deposit fraud case (counterfeit, altered, forged, kiting, double-presentment): fraud type, loss exposure, disposition |
| [mule-account-review](mule-account-review.md) | Assess an account for money-mule indicators: pass-through, network links, a mule-likelihood tier, and next actions |
| [fraud-typology-mapping](fraud-typology-mapping.md) | Translate a fraud typology into red-flag indicators, detection-rule logic, and control mapping |

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
