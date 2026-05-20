# Prompts

29 paste-ready analytical prompt templates. Each one turns an AI assistant into a specific kind of analyst — an entity risk reviewer, a sanctions screener, a transaction-monitoring analyst, a blockchain investigator, a regulatory monitor, a deep researcher — with a defined method, a scoring rubric, and a structured output format.

## How each file is built

Every prompt file has the same anatomy:

| Section | What it gives you |
|---------|-------------------|
| Description + summary table | What the prompt does, when to use it, what it produces, what it pairs with |
| **`## The prompt`** | A single fenced block — copy the whole thing into your assistant |
| `## How to use it` | How to fill placeholders and adapt the prompt |
| `## Output structure` | The exact shape of the result, so you know what good looks like |
| `## Tuning & variants` | Knobs — severity bands, weighting, scope variants, cadence |
| `## Worked example` | A concrete scenario |

**The `{{PLACEHOLDER}}` convention.** Inside every prompt block, `{{LIKE THIS}}` marks something you replace before sending. Replace all of them — an unfilled placeholder produces a vague result.

These are written for interactive use — paste into GitHub Copilot, Microsoft 365 Copilot, Claude, or ChatGPT and run. See [`../docs/using-with-copilot.md`](../docs/using-with-copilot.md) for the full workflow.

## Catalog

### [`compliance/`](compliance/) — financial crime & compliance
The financial-crime files cover a full analytical lifecycle: **detect** → **monitor** → **investigate** → **assess** → **report**.
- **[entity-risk-assessment](compliance/entity-risk-assessment.md)** — 8-domain weighted risk assessment of an entity; 0-100 composite, 5-tier rating, disposition recommendation
- **[sanctions-watchlist-screen](compliance/sanctions-watchlist-screen.md)** — screen a name, entity, or address against OFAC + EU/UN/UK lists with hit disposition
- **[typology-detection-mapping](compliance/typology-detection-mapping.md)** — decompose an AML typology into red-flag indicators and transaction-monitoring rule logic
- **[alert-triage](compliance/alert-triage.md)** — work a transaction-monitoring alert to a documented close / escalate / refer disposition
- **[investigation-narrative](compliance/investigation-narrative.md)** — draft a chronological, evidence-sourced narrative of investigated activity

### [`blockchain/`](blockchain/) — blockchain intelligence
- **[onchain-sanctions-monitor](blockchain/onchain-sanctions-monitor.md)** — screen blockchain addresses for sanctions, mixer, and AML-typology exposure
- **[fund-flow-tracing](blockchain/fund-flow-tracing.md)** — trace funds hop by hop across a chain; counterparties, mixers, exchanges, attribution confidence
- **[defi-protocol-risk](blockchain/defi-protocol-risk.md)** — score a DeFi protocol on TVL, yield, contract, governance, and bridge risk
- **[token-compliance-screen](blockchain/token-compliance-screen.md)** — screen a digital asset on both thesis quality and AML red flags

### [`regulatory/`](regulatory/) — regulatory landscape & obligations
- **[regulatory-intelligence-scan](regulatory/regulatory-intelligence-scan.md)** — severity-rated briefing on what changed in a regulatory landscape
- **[geopolitical-risk-monitor](regulatory/geopolitical-risk-monitor.md)** — per-jurisdiction sanctions, conflict, and regulatory-risk scoring
- **[obligation-extraction](regulatory/obligation-extraction.md)** — turn a regulation or filing into a structured register of obligations and deadlines

### [`research/`](research/) — deep research and idea work
- **[deep-research-storm](research/deep-research-storm.md)** — multi-perspective deep research into a cited long-form article
- **[cross-source-synthesis](research/cross-source-synthesis.md)** — meta-analysis across many sources: themes, contradictions, blind spots
- **[idea-generation](research/idea-generation.md)** — cross-domain idea generation, scored on an opportunity rubric
- **[calibration-debate](research/calibration-debate.md)** — steelman both sides of a thesis, then score its defensibility
- **[research-translation-scan](research/research-translation-scan.md)** — filter a research stream for signal, translate to practical implications
- **[frontier-scan](research/frontier-scan.md)** — track speculative research with strict evidence-tiering and forced counter-arguments
- **[futures-projection](research/futures-projection.md)** — year-by-year multi-metric scenario forecast with confidence bands

### [`market/`](market/) — market and economic analysis
- **[market-sentiment-tracker](market/market-sentiment-tracker.md)** — synthesize price, sentiment, and news into a market-narrative read
- **[macro-regime-monitor](market/macro-regime-monitor.md)** — classify the current macro regime from growth/inflation/liquidity indicators
- **[prediction-market-signal](market/prediction-market-signal.md)** — mine prediction markets for implied probabilities and flag divergences
- **[simulated-portfolio-manager](market/simulated-portfolio-manager.md)** — a hypothetical portfolio-simulation exercise with risk rules and attribution
- **[intelligence-dashboard-aggregator](market/intelligence-dashboard-aggregator.md)** — consolidate multiple feeds into one structured dashboard view

### [`briefs/`](briefs/) — recurring intelligence briefings
- **[intelligence-brief](briefs/intelligence-brief.md)** — a prioritized, scannable briefing; morning / midday / afternoon / evening variants
- **[weekly-roundup](briefs/weekly-roundup.md)** — a weekly review with a multi-dimension performance scorecard
- **[breaking-news-scan](briefs/breaking-news-scan.md)** — a terse, relevance-filtered breaking-news headline scan

### [`specialty/`](specialty/) — focused quantitative methods
- **[expected-value-analysis](specialty/expected-value-analysis.md)** — compute edge and expected value, size with the Kelly criterion, with risk-of-ruin context
- **[local-market-analytics](specialty/local-market-analytics.md)** — local real-estate market analytics: tracking, transformation signals, multi-scenario projection

## Chaining prompts

Output from one prompt is often input to another. Within financial crime, the categories chain into a workflow: `typology-detection-mapping` defines what to look for, `alert-triage` and `onchain-sanctions-monitor` catch it, `fund-flow-tracing` follows it, `entity-risk-assessment` sizes the counterparty, and `investigation-narrative` writes it up. Across categories: a `frontier-scan` finding worth a deep look feeds `deep-research-storm`; several finished assessments feed `cross-source-synthesis`; a regulatory finding feeds an `intelligence-brief`. The shared severity vocabulary (CRITICAL / HIGH / MEDIUM / LOW) and confidence ratings (HIGH / MODERATE / LOW) are deliberately consistent across the library so outputs compose.
