# analyst-toolkit

[![validate](https://github.com/maxmoran23/analyst-toolkit/actions/workflows/validate.yml/badge.svg)](https://github.com/maxmoran23/analyst-toolkit/actions/workflows/validate.yml)

**A copy/paste library of prompts, runnable scoring engines, and output templates for AI-assisted analytical work at financial institutions — covering every function of a financial-crime organization, plus the regulatory, research, market, and quantitative work around it.**

---

## If you have five minutes

**Who this is for.** People who work financial crime for a living — sanctions and
screening, transaction monitoring, fraud, surveillance, investigations, KYC, crypto,
controls and testing, model risk, data governance, new-product approval, regulatory
affairs. It assumes you know your domain. It does not assume you write code.

**What it gives you.** Two things, and they are different in kind:

- **87 prompts.** A page of written instructions you copy and paste into an AI assistant
  you already have — Microsoft 365 Copilot, GitHub Copilot, Claude, ChatGPT. Nothing to
  install. Each one turns the assistant into a specific analyst with a defined method, a
  scoring rubric, and a fixed output shape, so two people running it get comparable work.
- **15 runnable engines.** Small, transparent calculators for the problems that are
  really about volume — triaging 50,000 sanctions alerts, tuning a monitoring threshold,
  deciding whether a customer extract is fit to screen against.

**Why you should believe any of it.** Because you do not have to. Every accuracy figure
in this repository is produced by a script, not typed by a person, and an automated check
re-derives all of them from scratch on every change — on a machine nobody here controls.
You can run the same check yourself in about twenty seconds:

```bash
python3 _tooling/verify_evidence.py
```

And when an engine reports "no missed true matches," it also reports the bound that
claim actually supports. Zero misses across 997 planted true matches does not mean the
miss rate is zero — it means it is **below 0.30% at 95% confidence**, exactly as an
attribute sample returning zero exceptions bounds a deviation rate rather than proving it
is nil. Every such bound is published in **[`frameworks/EVIDENCE.md`](frameworks/EVIDENCE.md)**.

**What none of it does.** Nothing here connects to a bank system, blocks a payment,
files a report, or off-boards a customer. It drafts, it scores, and it documents. A
qualified person decides. All test data is synthetic and every entity is fictional.

### Where to go

| If you are… | Start here |
|---|---|
| On a team, and want what applies to your work | **[Your team hub](teams/)** — 15 pages, one per function |
| A senior reviewer asking "can I trust this?" | **[How the system works](docs/how-the-system-works.md)**, then **[EVIDENCE.md](frameworks/EVIDENCE.md)** |
| Validating models, or preparing for an exam | **[EVIDENCE.md](frameworks/EVIDENCE.md)** and **[RIGOR-CONTRACT.md](frameworks/RIGOR-CONTRACT.md)** |
| Just here for a tool | **[Browse the prompt catalog](prompts/)** or **[the engines](frameworks/)** |
| An AI agent working on this repo | **[AGENTS.md](AGENTS.md)** — not this page |

Every folder in this repository is written to be read on its own. If someone sends you a
link to one engine or one prompt category, that page will tell you who it is for, what it
refuses to do, and how to check its numbers — without sending you anywhere else.

---

## What this is

A library of reusable, paste-ready **prompt templates**, runnable **scoring engines**, and **document templates** for analytical work. Every prompt is a self-contained block you drop into an AI assistant — GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT — to get a rigorous, structured, audit-defensible result: an entity risk assessment, a sanctions or PEP screen, a transaction-alert disposition, a SAR file/no-file memo, a control-testing workpaper, a data-lineage map, a new-product risk assessment, a policy gap analysis, a committee reporting pack, a regulatory intelligence scan, a fund-flow trace, a deep research report, a populated dashboard.

The library is written for **every team inside a financial-crime organization** — sanctions and screening, transaction monitoring, fraud, trade and communications surveillance, investigations and SAR, crypto/blockchain intelligence, KYC/CDD onboarding, third-party and correspondent banking, risk assessment, controls and independent testing, model risk and governance, data governance, new-product approval, and regulatory affairs — as well as the research, market, and quantitative work that sits alongside them, and for any analyst outside one doing comparable work. Fifteen [team hubs](teams/) index it by function. Nothing here assumes a specific firm, vendor, or toolchain.

It is **not a system to deploy**. There is nothing to install, no runtime, no scheduler, and nothing you must connect it to. You browse, copy, paste, fill in the `{{PLACEHOLDERS}}`, and run. The work product is the prompt itself — the analytical method, the scoring rubric, the output structure, and the quality bar baked into each one. The one exception is [`frameworks/`](frameworks/): fifteen small, pure-standard-library scoring engines for the problems that are genuinely about volume, each shipping reproducible evidence of how accurately it performs. Those you run offline from a fixed seed; everything else you paste. (Two of the fifteen offer an *optional* live-ingest path to a public list or block explorer — opt-in, isolated, and never exercised by a validation run. See [`frameworks/README.md`](frameworks/README.md#on-network-access).)

Each template was extracted and generalized from a production autonomous-agent fleet, then stripped to its portable core — the part that travels to any assistant, any account, any machine.

> Looking for the architecture to *run* agents like these autonomously on a schedule — state, self-repair, budget management? That is the companion repo: **[Claude-Agent-Fleet](https://github.com/maxmoran23/Claude-Agent-Fleet)**. This repo is the content; that repo is the runtime.

---

## The two-file rule

Every feature in this library replicates with **at most two files** — and it is enforced in CI, not just promised:

| You attach | You get |
|------------|---------|
| **1 file** — any [`standalone/`](standalone/) file, or any prompt block from [`prompts/`](prompts/) | The full analysis: method, scoring rubric, structured output. Standalone files also include the multi-format renderer. |
| **2 files** — any prompt + [`BASE.md`](BASE.md) | Everything above **plus** the full quality system: audit-defensible voice, analytical discipline, per-deliverable quality floor, and the Word / Excel / PDF / interactive-HTML renderer. |

There is never a third file. [`BASE.md`](BASE.md) is the entire 4-file methodology consolidated into one attachable document — built for environments with no file system, no memory, and no repo access: a locked-down work machine, a Copilot chat, a one-shot share with a teammate. Every prompt block is fully self-contained as pasted; links inside prompt files are browse-time navigation, never run-time dependencies. A CI job ([`validate.yml`](.github/workflows/validate.yml)) fails the build if any prompt leaks a file reference into its paste payload, names a companion other than `BASE.md`, or exceeds the two-file budget.

![Entity risk assessment dashboard — illustrative sample](samples/previews/entity-risk-preview.png)

<table>
  <tr>
    <td width="50%"><img src="samples/previews/regulatory-landscape-preview.png" alt="Regulatory landscape dashboard — illustrative sample"></td>
    <td width="50%"><img src="output-templates/dashboards/previews/deep-dive-dashboard-preview.png" alt="Deep-dive dashboard template"></td>
  </tr>
  <tr>
    <td width="50%"><img src="samples/previews/control-matrix-preview.png" alt="AML/CFT control matrix dashboard — illustrative sample"></td>
    <td width="50%"><img src="samples/previews/committee-pack-preview.png" alt="Governance committee reporting pack — illustrative sample"></td>
  </tr>
</table>

*Above: outputs and templates from the toolkit — a sample entity risk assessment (one prompt plus one template), a regulatory-landscape view, the lightweight deep-dive dashboard template, and rendered samples from the controls category (27-control AML/CFT matrix, quarterly committee reporting pack). [See all samples](samples/) · [dashboard templates](output-templates/dashboards/).*

---

## What's inside

| Directory | What's in it |
|-----------|--------------|
| **[`BASE.md`](BASE.md)** | **The one companion file** — the entire methodology framework (voice + method + quality bar + renderer) consolidated into a single attachable document. Any prompt + `BASE.md` = full toolkit quality. Generated from `methodology/`; CI keeps it in sync. |
| **[`methodology/`](methodology/)** | **The 4-file framework base** — analytical patterns, audit-defensible writing voice, quality standards per output type, and the multi-format report-templates renderer. Load all four as Copilot agent / Claude Project / ChatGPT custom GPT instructions once; every task becomes a thin prompt after that. Prefer one file? Use [`BASE.md`](BASE.md). |
| **[`standalone/`](standalone/)** | **Single-file copy/paste prompts** — each one a complete instruction set, no cross-references, no other files needed; embeds the same renderer as `methodology/report-templates.md`. Best for one-off use or sharing one file with a teammate |
| **[`prompts/`](prompts/)** | 87 paste-ready analytical prompt templates across 15 categories — the broader library; each file pairs a prompt block with how-to and tuning sections |
| **[`output-templates/`](output-templates/)** | Document scaffolds — interactive dashboards, PDF reports, compliance documents, communications |
| **[`samples/`](samples/)** | Rendered example outputs with previews — what the prompts and templates actually produce |
| **[`reference/`](reference/)** | Domain cheat-sheets — AML typologies, blockchain entity typologies, compliance, audit, regulatory, financial analysis |
| **[`quant/`](quant/)** | A dependency-free Python quant library — VaR, Sharpe, Kelly, Monte Carlo, DCF, drawdown |
| **[`quant-jvm/`](quant-jvm/)** | Kotlin/JVM port of `quant/` — same math, same JSON I/O contract, verified by cross-language parity tests |
| **[`frameworks/`](frameworks/)** | **15 runnable scoring engines with validation evidence** — pure-stdlib reference engines for measurable scoring, triage, matching, threshold, fraud, and control-testing problems, each with a seeded synthetic-data generator and a harness that emits reproducible evidence and fails the build on its named safety invariant. A different artifact class from the paste-prompts; runnable, multi-file. |
| **[`teams/`](teams/)** | **Start here by your function** — 15 hub pages, one per team across the financial-crime organization (sanctions/screening, transaction monitoring, fraud, surveillance, crypto, KYC, investigations & SAR, third-party & correspondent, risk assessment, controls/testing, model governance, data governance, new-product approval, regulatory affairs, adverse media), each bundling the relevant prompts, frameworks, references, and templates in one place, in plain English. Pure navigation over the by-type folders. |
| **[`docs/`](docs/)** | Usage guides — the Copilot copy/paste workflow, running on any assistant, and **[how-the-system-works.md](docs/how-the-system-works.md)**: a plain-English walkthrough of the whole library for non-technical senior reviewers. |

---

## Three ways in

The toolkit supports three workflows. Pick the one that matches how you use AI assistants day to day.

### 1. Methodology base + thin prompts (set up once)

**Best for:** a work machine where you'll do many varied analytical tasks, and want every output to come out at the same quality bar without re-pasting a long prompt each time.

Load **[`BASE.md`](BASE.md)** (the four methodology files in one document) — or the four files from **[`methodology/`](methodology/)** individually — as your assistant's base instructions: Copilot agent custom instructions, Claude Project custom instructions, ChatGPT custom GPT instructions, or `.github/copilot-instructions.md` in a working repo. The four files cover **how to think** ([`analytical-patterns.md`](methodology/analytical-patterns.md)), **how to write it down** ([`audit-defensible-writing.md`](methodology/audit-defensible-writing.md)), **when it's done** ([`output-quality-standards.md`](methodology/output-quality-standards.md)), and **how to render it as Word / Excel / PDF / HTML** ([`report-templates.md`](methodology/report-templates.md)).

Then every task is a thin prompt that scopes the work; the four files supply the framework:

> *"Do an 8-domain entity risk assessment on [ENTITY]. Render as a Word doc."*
>
> *"Compare these three vendors on [criteria]. Render as an Excel workbook."*
>
> *"Triage this transaction alert. [profile + transactions]. Render as both Word and PDF."*

The methodology files apply the voice, the analytical discipline, the quality floor, and the rendering form. See [`methodology/report-templates.md`](methodology/report-templates.md) for more thin-prompt patterns.

### 2. Single-file standalone (no setup, copy/paste once per task)

**Best for:** one-off use, sharing one file with a teammate who has no setup, or demoing the "look at the quality difference" pattern.

Use a file from **[`standalone/`](standalone/)**. Every file there is fully self-contained: the whole file *is* the prompt, no markdown links to other files in the repo, each one starts with a Preflight step (assistant explicitly checks your inputs and asks for clarification before producing anything partial), and each one embeds the same multi-format renderer as `methodology/report-templates.md`. Paste one file, supply your inputs, optionally ask for a Word / Excel / PDF / HTML deliverable — all from that single paste. Covers universal analyst work (document summary, comparison matrix, meeting prep, decision memo, weekly digest, action items), the flagship financial-crime / intelligence prompts, and the assurance templates (control matrix builder, committee reporting pack).

### 3. Browse the catalog (find a prompt, copy the block)

**Best for:** discovering what the library covers, picking the right template for a new task, or seeing how prompts pair with samples and reference material.

Use **[`prompts/`](prompts/)** (catalog below). Each file has:

1. A summary table — when to use it and what it produces.
2. A single fenced ```text``` block under `## The prompt` — copy that, fill the `{{PLACEHOLDERS}}`, paste into any assistant.
3. How-to-use, output-structure, and tuning sections for the human reader.

Need a formatted deliverable from this workflow? Attach **[`BASE.md`](BASE.md)** alongside the prompt — its Part 4 is the Word / Excel / PDF / HTML renderer. Two files, never more. (Browsing for document scaffolds directly? They live in [`output-templates/`](output-templates/).)

Full workflow, including the Copilot copy/paste loop and getting output into clean files: **[docs/using-with-copilot.md](docs/using-with-copilot.md)**.

---

## Prompt catalog

87 prompts across 15 categories. The complete, per-prompt index — each file with a worked example and a paste-ready demo — lives in **[`prompts/`](prompts/)**; this is the category map.

The financial-crime categories run a full analytical lifecycle — **detect** → **monitor** → **investigate** → **decide** → **quality-check** → **report** — and the controls, data, and regulatory categories run the assurance lifecycle around it. The `npa/` category runs the same discipline forward in time, before a product generates its first alert. The shared severity vocabulary (CRITICAL / HIGH / MEDIUM / LOW) and confidence ratings (HIGH / MODERATE / LOW) are deliberately consistent across the library, so outputs compose.

| Category | Prompts | What it covers |
|---|---|---|
| **[`compliance/`](prompts/compliance/)** | 15 | Financial crime & compliance — screening, alert triage, investigation, SAR decisioning, UBO, case QA, identity resolution |
| **[`fraud/`](prompts/fraud/)** | 5 | Fraud detection & response — APP scams, wire and check fraud, mule accounts, typology mapping |
| **[`surveillance/`](prompts/surveillance/)** | 3 | Trade & communications surveillance — manipulation patterns, e-comms conduct, market-abuse cases |
| **[`third-party/`](prompts/third-party/)** | 4 | ABC, vendors & correspondent banking — vendor diligence, bribery risk, nested access, TBML |
| **[`blockchain/`](prompts/blockchain/)** | 15 | Blockchain intelligence — on-chain screening and tracing, tokens, stablecoins, tokenized assets, prediction markets, wallet attribution |
| **[`regulatory/`](prompts/regulatory/)** | 5 | Regulatory landscape & obligations — intelligence scans, obligation extraction, policy-gap analysis, exam response |
| **[`controls/`](prompts/controls/)** | 9 | Controls, testing & governance — control matrix, risk register, EWRA, independent testing, model validation, data quality |
| **[`data-governance/`](prompts/data-governance/)** | 4 | Data governance for financial-crime systems — CDE inventory, lineage, DQ-rule authoring, incident triage |
| **[`npa/`](prompts/npa/)** | 3 | New-product approval & review — pre-launch risk, launch readiness, post-implementation review |
| **[`research/`](prompts/research/)** | 7 | Deep research & idea work — STORM research, cross-source synthesis, calibration debate, frontier/futures |
| **[`market/`](prompts/market/)** | 5 | Market & economic analysis — sentiment, macro regime, prediction-market signal, portfolio simulation |
| **[`briefs/`](prompts/briefs/)** | 4 | Recurring intelligence briefings — daily briefs, weekly roundups, breaking-news scans, committee packs |
| **[`specialty/`](prompts/specialty/)** | 2 | Focused quantitative methods — expected-value / Kelly sizing, local-market analytics |
| **[`automation/`](prompts/automation/)** | 4 | Communications automation & maintained artifacts — thread extraction, report refresh, chat indexing, pipeline specs |
| **[`workspace/`](prompts/workspace/)** | 2 | Configure & automate your AI workspace — custom-instructions writer, Outlook/Copilot automation |

For the full list of prompts in each category and how they chain into workflows, see **[`prompts/README.md`](prompts/README.md)**.

## Design principles

Every prompt in this library follows the same discipline — documented in full under [`methodology/`](methodology/):

- **Audit-defensible.** Every claim carries a source. Observed fact, allegation, and projection are never blended.
- **Evidence, not assertion.** Every number in every `evidence/` pack is emitted by a harness, and CI **re-derives all fifteen packs from seed on every commit** and fails if one differs. Safety claims carry an exact confidence bound, not just "recall 1.0". Check it yourself in twenty seconds: `python3 _tooling/verify_evidence.py`. See [`frameworks/EVIDENCE.md`](frameworks/EVIDENCE.md).
- **Two-file ceiling, machine-enforced.** Any feature replicates with at most one prompt + [`BASE.md`](BASE.md). CI fails if a paste payload references another file or any prompt names a different companion.
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
