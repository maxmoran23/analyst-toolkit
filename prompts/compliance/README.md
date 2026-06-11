# Financial crime & compliance prompts

These prompts cover a full financial-crime analytical lifecycle: detect, monitor, investigate, assess, and report. Each turns an AI assistant into a specific compliance analyst role with a defined method, scoring rubric, and structured output.

| Prompt | What it does |
|--------|--------------|
| [entity-risk-assessment](entity-risk-assessment.md) | 8-domain weighted risk assessment of an entity; 0-100 composite, 5-tier rating, disposition recommendation |
| [sanctions-watchlist-screen](sanctions-watchlist-screen.md) | Screen a name, entity, or address against OFAC + EU/UN/UK lists with hit disposition |
| [typology-detection-mapping](typology-detection-mapping.md) | Decompose an AML typology into red-flag indicators and transaction-monitoring rule logic |
| [alert-triage](alert-triage.md) | Work a transaction-monitoring alert to a documented close / escalate / refer disposition |
| [investigation-narrative](investigation-narrative.md) | Draft a chronological, evidence-sourced narrative of investigated activity |
| [customer-file-review](customer-file-review.md) | Review a customer risk file for completeness and risk-rating defensibility; deficiencies by severity, remediation actions |

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
