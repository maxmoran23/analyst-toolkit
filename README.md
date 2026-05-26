# analyst-toolkit

**A copy/paste library of prompts and output templates for AI-assisted analytical work — built around a financial-crime, compliance, and blockchain-intelligence core, and extending into regulatory, research, market, and quantitative analysis.**

---

## What this is

A library of reusable, paste-ready **prompt templates** and **document templates** for analytical work. Every prompt is a self-contained block you drop into an AI assistant — GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT — to get a rigorous, structured, audit-defensible result: an entity risk assessment, a sanctions screen, a transaction-alert disposition, a regulatory intelligence scan, a fund-flow trace, a deep research report, a populated dashboard.

It is **not a framework to run**. There is nothing to install, no runtime, no scheduler. You browse, copy, paste, fill in the `{{PLACEHOLDERS}}`, and run. The work product is the prompt itself — the analytical method, the scoring rubric, the output structure, and the quality bar baked into each one.

Each template was extracted and generalized from a production autonomous-agent fleet, then stripped to its portable core — the part that travels to any assistant, any account, any machine.

> Looking for the architecture to *run* agents like these autonomously on a schedule — state, self-repair, budget management? That is the companion repo: **[Claude-Agent-Fleet](https://github.com/maxmoran23/Claude-Agent-Fleet)**. This repo is the content; that repo is the runtime.

![Entity risk assessment dashboard — illustrative sample](samples/previews/entity-risk-preview.png)

<table>
  <tr>
    <td width="50%"><img src="samples/previews/regulatory-landscape-preview.png" alt="Regulatory landscape dashboard — illustrative sample"></td>
    <td width="50%"><img src="output-templates/dashboards/previews/deep-dive-dashboard-preview.png" alt="Deep-dive dashboard template"></td>
  </tr>
</table>

*Above: outputs and templates from the toolkit — a sample entity risk assessment (one prompt plus one template), a regulatory-landscape view, and the lightweight deep-dive dashboard template. [See all samples](samples/) · [dashboard templates](output-templates/dashboards/).*

---

## What's inside

| Directory | What's in it |
|-----------|--------------|
| **[`standalone/`](standalone/)** | **Single-file copy/paste prompts** — each one a complete instruction set, no cross-references, no other files needed. Best for saving as a Copilot agent / Claude Project, or sharing one file with a teammate |
| **[`prompts/`](prompts/)** | 29 paste-ready analytical prompt templates across 7 categories — the broader library; each file pairs a prompt block with how-to and tuning sections |
| **[`output-templates/`](output-templates/)** | Document scaffolds — interactive dashboards, PDF reports, compliance documents, communications |
| **[`samples/`](samples/)** | Rendered example outputs with previews — what the prompts and templates actually produce |
| **[`methodology/`](methodology/)** | The writing voice, quality standards, and analytical patterns that keep outputs consistent |
| **[`reference/`](reference/)** | Domain cheat-sheets — AML typologies, blockchain entity typologies, compliance, audit, regulatory, financial analysis |
| **[`quant/`](quant/)** | A dependency-free Python quant library — VaR, Sharpe, Kelly, Monte Carlo, DCF, drawdown |
| **[`docs/`](docs/)** | How to use the toolkit — the Copilot copy/paste workflow, and how the prompts run on any assistant |

---

## Two ways in

**Want one file you can paste whole into an assistant — or save as a Copilot agent / Claude Project?** Use **[`standalone/`](standalone/)**. Every file there is self-contained: the whole file *is* the prompt, no markdown links to other files in the repo, and each one starts with a Preflight step where the assistant explicitly checks your inputs and asks for clarification before producing anything partial. Covers universal analyst work (document summary, comparison matrix, meeting prep, decision memo, weekly digest, action items) and the flagship financial-crime / intelligence prompts.

**Want to browse the full library — see how prompts connect to samples, reference material, and other prompts?** Use **[`prompts/`](prompts/)** (catalog below). Each file has:

1. A summary table — when to use it and what it produces.
2. A single fenced ```text``` block under `## The prompt` — copy that, fill the `{{PLACEHOLDERS}}`, paste into any assistant.
3. How-to-use, output-structure, and tuning sections for the human reader.

Need a formatted deliverable from either workflow? Pair the result with an **[`output-templates/`](output-templates/)** scaffold.

Full workflow, including the Copilot copy/paste loop and getting output into clean files: **[docs/using-with-copilot.md](docs/using-with-copilot.md)**.

---

## Prompt catalog

The financial-crime categories cover a full analytical lifecycle — **detect** (typology mapping) → **monitor** (alert triage, on-chain screening) → **investigate** (fund-flow tracing) → **assess** (entity and token risk) → **report** (investigation narrative).

### Financial crime & compliance — [`prompts/compliance/`](prompts/compliance/)
| Prompt | What it does |
|--------|--------------|
| [entity-risk-assessment](prompts/compliance/entity-risk-assessment.md) | 8-domain weighted risk assessment of an entity — 0-100 composite, 5-tier rating, disposition |
| [sanctions-watchlist-screen](prompts/compliance/sanctions-watchlist-screen.md) | Screen a name, entity, or address against OFAC + EU/UN/UK lists with hit disposition |
| [typology-detection-mapping](prompts/compliance/typology-detection-mapping.md) | Decompose an AML typology into red-flag indicators and transaction-monitoring rule logic |
| [alert-triage](prompts/compliance/alert-triage.md) | Work a transaction-monitoring alert to a documented close / escalate / refer disposition |
| [investigation-narrative](prompts/compliance/investigation-narrative.md) | Draft a chronological, evidence-sourced narrative of investigated activity |

### Blockchain intelligence — [`prompts/blockchain/`](prompts/blockchain/)
| Prompt | What it does |
|--------|--------------|
| [onchain-sanctions-monitor](prompts/blockchain/onchain-sanctions-monitor.md) | Screen blockchain addresses for sanctions, mixer, and AML-typology exposure |
| [fund-flow-tracing](prompts/blockchain/fund-flow-tracing.md) | Trace funds hop by hop across a chain — counterparties, mixers, exchanges, attribution |
| [defi-protocol-risk](prompts/blockchain/defi-protocol-risk.md) | Score a DeFi protocol on TVL, yield, contract, governance, and bridge risk |
| [token-compliance-screen](prompts/blockchain/token-compliance-screen.md) | Screen a digital asset on both thesis quality and AML red flags |

### Regulatory — [`prompts/regulatory/`](prompts/regulatory/)
| Prompt | What it does |
|--------|--------------|
| [regulatory-intelligence-scan](prompts/regulatory/regulatory-intelligence-scan.md) | Severity-rated briefing on what changed in a regulatory landscape |
| [geopolitical-risk-monitor](prompts/regulatory/geopolitical-risk-monitor.md) | Per-jurisdiction sanctions, conflict, and regulatory-risk scoring |
| [obligation-extraction](prompts/regulatory/obligation-extraction.md) | Turn a regulation or filing into a structured register of obligations and deadlines |

### Research — [`prompts/research/`](prompts/research/)
| Prompt | What it does |
|--------|--------------|
| [deep-research-storm](prompts/research/deep-research-storm.md) | Multi-perspective deep research into a cited long-form article |
| [cross-source-synthesis](prompts/research/cross-source-synthesis.md) | Meta-analysis across many sources — themes, contradictions, blind spots |
| [idea-generation](prompts/research/idea-generation.md) | Cross-domain idea generation, scored on an opportunity rubric |
| [calibration-debate](prompts/research/calibration-debate.md) | Steelman both sides of a thesis, then score its defensibility |
| [research-translation-scan](prompts/research/research-translation-scan.md) | Filter a research stream for signal, translate to practical implications |
| [frontier-scan](prompts/research/frontier-scan.md) | Track speculative research with strict evidence-tiering and forced counter-arguments |
| [futures-projection](prompts/research/futures-projection.md) | Year-by-year multi-metric scenario forecast with confidence bands |

### Market & economic — [`prompts/market/`](prompts/market/)
| Prompt | What it does |
|--------|--------------|
| [market-sentiment-tracker](prompts/market/market-sentiment-tracker.md) | Synthesize price, sentiment, and news into a market-narrative read |
| [macro-regime-monitor](prompts/market/macro-regime-monitor.md) | Classify the current macro regime from growth/inflation/liquidity indicators |
| [prediction-market-signal](prompts/market/prediction-market-signal.md) | Mine prediction markets for implied probabilities and flag divergences |
| [simulated-portfolio-manager](prompts/market/simulated-portfolio-manager.md) | A hypothetical portfolio-simulation exercise with risk rules and attribution |
| [intelligence-dashboard-aggregator](prompts/market/intelligence-dashboard-aggregator.md) | Consolidate multiple feeds into one structured dashboard view |

### Intelligence briefs — [`prompts/briefs/`](prompts/briefs/)
| Prompt | What it does |
|--------|--------------|
| [intelligence-brief](prompts/briefs/intelligence-brief.md) | A prioritized, scannable briefing — morning / midday / afternoon / evening variants |
| [weekly-roundup](prompts/briefs/weekly-roundup.md) | A weekly review with a multi-dimension performance scorecard |
| [breaking-news-scan](prompts/briefs/breaking-news-scan.md) | A terse, relevance-filtered breaking-news headline scan |

### Specialty — [`prompts/specialty/`](prompts/specialty/)
| Prompt | What it does |
|--------|--------------|
| [expected-value-analysis](prompts/specialty/expected-value-analysis.md) | Compute edge and expected value, size with the Kelly criterion, with risk-of-ruin context |
| [local-market-analytics](prompts/specialty/local-market-analytics.md) | Local real-estate market analytics — tracking, transformation signals, multi-scenario projection |

---

## Design principles

Every prompt in this library follows the same discipline — documented in full under [`methodology/`](methodology/):

- **Audit-defensible.** Every claim carries a source. Observed fact, allegation, and projection are never blended.
- **Runs anywhere.** Every prompt is self-contained and assistant-agnostic — no tool, integration, memory, or specific product required. If a capability is missing it degrades gracefully and asks for what it needs. See [running on any assistant](docs/running-on-any-assistant.md).
- **Structured output.** Each prompt specifies an exact output format — scorecards, severity tiers, confidence ratings — so results are comparable and reusable.
- **Honest about gaps.** "No adverse findings" and "quiet period" are valid results. Thin evidence lowers the confidence rating; it does not get filled with inference.
- **Vendor-skeptical.** Self-reported metrics and vendor claims are treated as unverified until corroborated.
- **No fabrication.** An unverifiable claim is labeled or omitted — never invented.

---

## About

This toolkit was generalized from a production autonomous-agent fleet operated at the intersection of crypto/AML compliance work and hands-on AI system design. That compliance background is why the templates lean toward structured severity frameworks, audit-defensible documentation, and systematic evidence-based analysis — those are the default operating principles here, not decoration.

Everything in this repository is generic and reusable. There is no proprietary, employer-specific, or non-public content — only method, structure, and quality bar.

## License

MIT — see [LICENSE](LICENSE). Use these freely; adapt them to your work.
