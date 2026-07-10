# Prompts

68 paste-ready analytical prompt templates across 13 categories. Each one turns an AI assistant into a specific kind of analyst — an entity risk reviewer, a sanctions or PEP screener, a transaction-monitoring analyst, a fraud investigator, a surveillance reviewer, a control tester, a data-governance analyst, a new-product risk assessor, a blockchain investigator, a regulatory monitor, a deep researcher — with a defined method, a scoring rubric, and a structured output format.

**The two-file rule.** Every prompt block here is fully self-contained as pasted — no other file is required at run time. The only companion that ever adds anything is [`../BASE.md`](../BASE.md) (the audit-defensible voice, the quality floor, and the Word / Excel / PDF / HTML renderer in one document). One prompt + `BASE.md` is the entire quality system; there is never a third file, and CI enforces it. Links inside these files are browse-time navigation only — each file states this in its **Run-time needs** row and its run-time contract footer.

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
| **`## Try it now`** | A second fenced block: the prompt above with every input already filled with fictional demo data — paste it with zero edits to see the full output before you supply any material of your own |

**The `{{PLACEHOLDER}}` convention.** Inside every prompt block, `{{LIKE THIS}}` marks something you replace before sending. Replace all of them — an unfilled placeholder produces a vague result.

**Two blocks per file, two jobs.** `## The prompt` is the reusable tool — you fill its placeholders with your material. `## Try it now` is the same prompt with fictional inputs already in place, so anyone can paste it into any assistant and judge the depth, method, and output shape with nothing to fill in and no data of their own. The demo is *generated* from the prompt block, so it always matches the method exactly; CI re-derives it on every change.

These are written for interactive use — paste into GitHub Copilot, Microsoft 365 Copilot, Claude, or ChatGPT and run. See [`../docs/using-with-copilot.md`](../docs/using-with-copilot.md) for the full workflow.

## Catalog

### [`compliance/`](compliance/) — financial crime & compliance
The financial-crime files cover a full analytical lifecycle: **detect** → **monitor** → **investigate** → **decide** → **quality-check** → **report**.
- **[entity-risk-assessment](compliance/entity-risk-assessment.md)** — 8-domain weighted risk assessment of an entity; 0-100 composite, 5-tier rating, disposition recommendation
- **[sanctions-watchlist-screen](compliance/sanctions-watchlist-screen.md)** — screen a name, entity, or address against OFAC + EU/UN/UK lists with hit disposition
- **[pep-screening-disposition](compliance/pep-screening-disposition.md)** — disposition a politically-exposed-person alert on two axes: right party, and materially in-scope status (prominence tier, step-down, jurisdiction)
- **[typology-detection-mapping](compliance/typology-detection-mapping.md)** — decompose an AML typology into red-flag indicators and transaction-monitoring rule logic
- **[alert-triage](compliance/alert-triage.md)** — work a transaction-monitoring alert to a documented close / escalate / refer disposition
- **[investigation-narrative](compliance/investigation-narrative.md)** — draft a chronological, evidence-sourced narrative of investigated activity
- **[sar-decisioning](compliance/sar-decisioning.md)** — work a completed investigation through the elements-of-suspicion checklist to a documented file / no-file decision memo, with deadline arithmetic; the filing decision itself stays human
- **[case-qa-review](compliance/case-qa-review.md)** — second-line QA of a completed case file: six named critical checks, five weighted dimensions, severity-coded deficiency register, PASS / REMEDIATE / REWORK disposition
- **[ubo-beneficial-ownership](compliance/ubo-beneficial-ownership.md)** — unwind an ownership chain layer by layer: effective-ownership math, control-prong analysis, opacity red flags, gap register
- **[network-link-analysis](compliance/network-link-analysis.md)** — map entity-relationship data into shared-attribute clusters, hubs, and flow-through patterns; ring hypotheses stated as observed vs inferred
- **[periodic-review-triggers](compliance/periodic-review-triggers.md)** — triage a periodic-review backlog: event-driven vs calendar-driven triggers, weighted prioritization, risk-based scheduling
- **[customer-file-review](compliance/customer-file-review.md)** — review a customer risk file for completeness and risk-rating defensibility; deficiencies by severity, remediation actions

### [`fraud/`](fraud/) — fraud detection & response
- **[app-fraud-triage](fraud/app-fraud-triage.md)** — classify an authorized-push-payment scam, weigh social-engineering and mule indicators, disposition with liability framing
- **[wire-fraud-disposition](fraud/wire-fraud-disposition.md)** — disposition a flagged wire: hold, release, recall, or escalate, with the specific verification step needed
- **[check-fraud-analysis](fraud/check-fraud-analysis.md)** — classify a flagged check or deposit case, derive red flags, estimate loss exposure against the funds-availability clock
- **[mule-account-review](fraud/mule-account-review.md)** — assess one account for money-mule indicators; tiered mule-likelihood disposition plus a network-expansion list
- **[fraud-typology-mapping](fraud/fraud-typology-mapping.md)** — translate a named fraud scheme into detection-rule logic, data requirements, and control mappings

### [`surveillance/`](surveillance/) — trade & communications surveillance
- **[trade-surveillance-review](surveillance/trade-surveillance-review.md)** — triage a trade-surveillance alert: manipulation pattern, intent vs legitimate-strategy alternatives, close-or-escalate
- **[comms-surveillance-review](surveillance/comms-surveillance-review.md)** — read a flagged e-comms item in context and classify the market-integrity or conduct risk
- **[market-abuse-case](surveillance/market-abuse-case.md)** — build a sourced, element-by-element case narrative for suspected insider dealing or manipulation

### [`third-party/`](third-party/) — ABC, vendors & correspondent banking
- **[vendor-due-diligence](third-party/vendor-due-diligence.md)** — onboarding or periodic vendor due diligence: domain scorecard, residual-risk tier, required mitigations
- **[abc-risk-assessment](third-party/abc-risk-assessment.md)** — anti-bribery & corruption exposure assessment for a relationship, transaction, or intermediary
- **[correspondent-nested-risk](third-party/correspondent-nested-risk.md)** — score a respondent relationship and its downstream / nested access risk
- **[tbml-redflag-analysis](third-party/tbml-redflag-analysis.md)** — screen a trade-finance transaction or relationship for TBML red flags; tiered disposition memo

### [`blockchain/`](blockchain/) — blockchain intelligence
- **[onchain-sanctions-monitor](blockchain/onchain-sanctions-monitor.md)** — screen blockchain addresses for sanctions, mixer, and AML-typology exposure
- **[fund-flow-tracing](blockchain/fund-flow-tracing.md)** — trace funds hop by hop across a chain; counterparties, mixers, exchanges, attribution confidence
- **[block-explorer-osint](blockchain/block-explorer-osint.md)** — convert public block-explorer data into a provenance-stamped evidence annex: source and retrieval date on every fact, reconciliation tie-out, observation-vs-attribution firewall
- **[defi-protocol-risk](blockchain/defi-protocol-risk.md)** — score a DeFi protocol on TVL, yield, contract, governance, and bridge risk
- **[token-compliance-screen](blockchain/token-compliance-screen.md)** — screen a digital asset on both thesis quality and AML red flags

### [`regulatory/`](regulatory/) — regulatory landscape & obligations
- **[regulatory-intelligence-scan](regulatory/regulatory-intelligence-scan.md)** — severity-rated briefing on what changed in a regulatory landscape
- **[geopolitical-risk-monitor](regulatory/geopolitical-risk-monitor.md)** — per-jurisdiction sanctions, conflict, and regulatory-risk scoring
- **[obligation-extraction](regulatory/obligation-extraction.md)** — turn a regulation or filing into a structured register of obligations and deadlines
- **[policy-gap-analysis](regulatory/policy-gap-analysis.md)** — clause-level gap analysis of an internal policy against a regulation; requirement register, coverage map, traceability matrix
- **[exam-response-pack](regulatory/exam-response-pack.md)** — parse an examination or information request into a response pack: request register, evidence mapping, drafting guidance, QC checklist

### [`controls/`](controls/) — controls, testing & governance
The assurance side of a compliance program: document the control environment, register and score risk, test independently, quality-check analyst work, track findings to closure, and govern the models, tools, and data the program runs on.
- **[control-matrix-builder](controls/control-matrix-builder.md)** — build a six-domain AML/CFT control inventory from a program scope; 27-control reference framework, gap register, remediation view
- **[risk-register-builder](controls/risk-register-builder.md)** — build a compliance risk register with inherent L×I scoring, control offset, residual ratings, appetite comparison, dual heat maps
- **[ewra-builder](controls/ewra-builder.md)** — build the enterprise-wide financial-crime risk assessment: per-business-line inherent factors, control-effectiveness overlay, residual grid, year-over-year movement, board summary
- **[independent-testing-workpaper](controls/independent-testing-workpaper.md)** — design and document a control test to audit standard: sample methodology, attribute results, exceptions with root cause, effectiveness conclusion
- **[qa-review-scorecard](controls/qa-review-scorecard.md)** — score completed work items against a weighted QA rubric; per-item scorecards, pass rate, error taxonomy, coaching themes
- **[issue-remediation-tracker](controls/issue-remediation-tracker.md)** — normalize findings into an issue register, quality-check action plans, design sustainability tests, enforce closure-evidence standards, roll up for governance
- **[model-governance-review](controls/model-governance-review.md)** — assess a model, rule set, or AI-assisted tool against model-risk-management expectations; eight-dimension scorecard, governance recommendation
- **[model-validation-workpaper](controls/model-validation-workpaper.md)** — independent validation workpaper for a financial-crime model along the conceptual-soundness / ongoing-monitoring / outcomes-analysis pillars; findings register, effective-challenge documentation, fitness conclusion
- **[data-quality-review](controls/data-quality-review.md)** — assess a dataset or feed across six quality dimensions, map source-to-use lineage with handoff controls, defect log and remediation register

### [`data-governance/`](data-governance/) — data governance for financial-crime systems
Screening, monitoring, and reporting are only as good as the data feeding them. These prompts are the data team's side of the program.
- **[cde-inventory](data-governance/cde-inventory.md)** — build a critical-data-element inventory from consuming-process criticality; per-CDE record with owner, source of truth, thresholds, consuming controls
- **[data-lineage-mapping](data-governance/data-lineage-mapping.md)** — map one CDE from origin to every consuming process: hop-by-hop table, transformation inventory, controlled vs uncontrolled hops, break-risk register
- **[dq-rule-authoring](data-governance/dq-rule-authoring.md)** — translate a CDE quality requirement into named, testable rules across the five quality dimensions, with thresholds, criticality, and a rulebook table
- **[data-incident-triage](data-governance/data-incident-triage.md)** — triage a data break that hits financial-crime systems: blast radius, lookback scoping, notification considerations, interim compensating controls

### [`npa/`](npa/) — new-product approval & review
The product-risk committee workflow, end to end: assess before launch, verify readiness at launch, review after launch.
- **[npa-risk-assessment](npa/npa-risk-assessment.md)** — nine-factor financial-crime risk assessment of a proposed product; tier with raise-only floors, mandatory pre-launch conditions, approval routing
- **[product-launch-readiness](npa/product-launch-readiness.md)** — verify every approval condition against actual evidence; GO / GO-WITH-CONDITIONS / NO-GO with launch-blocking classification
- **[post-implementation-review](npa/post-implementation-review.md)** — projected-vs-observed comparison at the committed review date; condition compliance, new risks since launch, close / extend / remediate / escalate

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
- **[committee-reporting-pack](briefs/committee-reporting-pack.md)** — assemble a governance-committee reporting pack: KPI/KRI dashboard, escalations, prior-action tracker, forward calendar

### [`specialty/`](specialty/) — focused quantitative methods
- **[expected-value-analysis](specialty/expected-value-analysis.md)** — compute edge and expected value, size with the Kelly criterion, with risk-of-ruin context
- **[local-market-analytics](specialty/local-market-analytics.md)** — local real-estate market analytics: tracking, transformation signals, multi-scenario projection

## Chaining prompts

Output from one prompt is often input to another. Within financial crime, the categories chain into a workflow: `typology-detection-mapping` defines what to look for, `alert-triage`, `pep-screening-disposition`, and `onchain-sanctions-monitor` catch it, `fund-flow-tracing` and `network-link-analysis` follow it, `ubo-beneficial-ownership` and `entity-risk-assessment` size the counterparty, `investigation-narrative` writes it up, `sar-decisioning` works the outcome to a documented decision, and `case-qa-review` checks the finished file. The assurance prompts chain the same way: `ewra-builder` and `risk-register-builder` say where the risk is, `control-matrix-builder` documents what mitigates it, `independent-testing-workpaper` proves whether the controls work, `qa-review-scorecard` checks the analysts working them, `issue-remediation-tracker` carries what testing finds through to verified closure, and `committee-reporting-pack` reports the whole picture upward. `policy-gap-analysis` and `exam-response-pack` close the loop with regulators. The data prompts feed everything upstream: `cde-inventory` names what matters, `data-lineage-mapping` shows where it flows, `dq-rule-authoring` makes quality testable, and `data-incident-triage` handles the breaks. The `npa/` prompts run the same discipline forward in time — assess, verify, review — before a product ever generates its first alert. Across categories: a `frontier-scan` finding worth a deep look feeds `deep-research-storm`; several finished assessments feed `cross-source-synthesis`; a regulatory finding feeds an `intelligence-brief`. The shared severity vocabulary (CRITICAL / HIGH / MEDIUM / LOW) and confidence ratings (HIGH / MODERATE / LOW) are deliberately consistent across the library so outputs compose.
