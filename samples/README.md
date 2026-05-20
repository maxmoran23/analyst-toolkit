# Samples

Rendered example outputs — what the toolkit's prompts and templates actually produce.

> Every sample here is **illustrative**: synthetic data, and where an entity is assessed it is **fictional**. "Meridian Digital Exchange" is invented. These exist to show output format and quality, not to assess any real company.

---

## Interactive dashboards

### Entity Risk Assessment dashboard
[`dashboards/entity-risk-sample.html`](dashboards/entity-risk-sample.html) — the output of [`prompts/compliance/entity-risk-assessment.md`](../prompts/compliance/entity-risk-assessment.md) rendered into the [Dashboard BIG](../output-templates/dashboards/) template. An 8-domain risk assessment of a fictional digital-asset exchange: weighted 0-100 composite, scorecard, radar and bar charts, per-domain narrative, red flags, disposition.

![Entity risk assessment dashboard preview](previews/entity-risk-preview.png)

### Regulatory intelligence dashboard
[`dashboards/regulatory-landscape-sample.html`](dashboards/regulatory-landscape-sample.html) — a regulatory-landscape view rendered into the [3-tab deep-dive](../output-templates/dashboards/) template. Severity-tagged developments, a tracked-matters ledger, and upcoming deadlines for the digital-asset regulatory landscape.

![Regulatory dashboard preview](previews/regulatory-landscape-preview.png)

> Both files are self-contained HTML — download and open in any browser; the only external dependency is the Chart.js CDN.

---

## Reports

| Sample | Produced by | What it shows |
|--------|-------------|---------------|
| [`reports/entity-risk-sample.md`](reports/entity-risk-sample.md) | [entity-risk-assessment](../prompts/compliance/entity-risk-assessment.md) | The same entity risk assessment as a markdown report — the prose form of the dashboard above |
| [`reports/deep-research-sample.md`](reports/deep-research-sample.md) | [deep-research-storm](../prompts/research/deep-research-storm.md) | A cited, multi-section research article — *The Evolution of Stablecoin Regulation, 2022-2026* |
| [`reports/intelligence-brief-sample.md`](reports/intelligence-brief-sample.md) | [intelligence-brief](../prompts/briefs/intelligence-brief.md) | A morning anchor brief — prioritized, scannable, sourced |
| [`reports/obligation-extraction-sample.md`](reports/obligation-extraction-sample.md) | [obligation-extraction](../prompts/regulatory/obligation-extraction.md) | A structured obligation register — the public FATF "Travel Rule" for virtual-asset transfers, parsed into citable obligations, deadlines, and open questions |

## Compliance artifacts

| Sample | Produced by | What it shows |
|--------|-------------|---------------|
| [`compliance/control-matrix-sample.md`](compliance/control-matrix-sample.md) | [control-matrix](../output-templates/compliance-docs/control-matrix.md) | A populated AML/CFT control matrix — 10 controls across CDD, monitoring, sanctions, SAR, governance, with test results |
| [`compliance/alert-triage-sample.md`](compliance/alert-triage-sample.md) | [alert-triage](../prompts/compliance/alert-triage.md) | A transaction-monitoring alert worked to a documented ESCALATE disposition — round-value international wires off a fictional small-business profile, with for-and-against factors and an audit-ready memo |
| [`compliance/investigation-narrative-sample.md`](compliance/investigation-narrative-sample.md) | [investigation-narrative](../prompts/compliance/investigation-narrative.md) | A complete investigation narrative — chronological layering of funds through a fictional customer's linked accounts, every figure sourced and reconciled |
| [`compliance/fund-flow-tracing-sample.md`](compliance/fund-flow-tracing-sample.md) | [fund-flow-tracing](../prompts/blockchain/fund-flow-tracing.md) | An on-chain fund-flow trace — a fictional Ethereum address traced six hops through a mixer and into a centralized-exchange deposit, with attribution-confidence ratings |

---

## How to read these

Each sample is the *result*; the linked prompt or template is the *input*. To reproduce: open the linked prompt, copy its prompt block, fill the placeholders, and run it in any capable AI assistant. The sample shows you the quality bar to expect — and the structure to hold the output to.
