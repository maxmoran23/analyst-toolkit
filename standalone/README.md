# Standalone Prompts — single-file copy/paste

Every file in this directory is a **complete, self-contained instruction set**. Copy one whole file into any AI assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT, or anything comparable), reply with your inputs when asked, and the assistant performs the analysis to a defensible standard. Most need no repository companion. The two artifact-preservation workflows are explicit exceptions: `data-to-dashboard.md` may use one supplied HTML shell, and `material-to-deck.md` pairs the semantic plan with a supplied branded deck and the placeholder-only injector.

Each file now also embeds a **multi-format renderer**: after the analysis runs, ask for a Word doc, an Excel workbook, a PDF narrative report, or an interactive HTML dashboard, and the same single file tells the assistant how to produce it — to the same visual quality bar as the dedicated templates in `../output-templates/`, but without needing any of those files. The renderer ships working Python skeletons (`python-docx`, `openpyxl`, `reportlab`) plus a self-contained HTML+Chart.js dashboard template.

These are the right files to reach for when you want a **single markdown reference** you can keep on a work machine, paste into a Copilot agent's custom instructions, drop into a Claude Project, or share as one block.

---

## What makes these different from `../prompts/`

| | `prompts/` | `standalone/` |
|---|---|---|
| **Shape** | Human-facing wrapper + an isolated ```text``` prompt block + tuning sections | Tiny header for the human, then the whole file *is* the prompt |
| **Cross-references** | Yes — links to `samples/`, `reference/`, paired prompts | None — every reference inlined or removed |
| **Preflight clarification** | Buried in the Rules section at the bottom of the prompt block | A named **Preflight** step before Method — assistant explicitly stops and asks if any required input is missing |
| **Multi-format output** | Linked to `output-templates/` files | Embedded inline — Word, Excel, PDF, and interactive HTML rendering in every file |
| **Designed for** | Browsing the library, copying just the prompt block | Single-file copy/paste; saved as a Copilot agent / Claude Project; sharing one file with a teammate |

The two directories cover the same kinds of work; pick the shape that matches how you use it.

---

## What's in here

### Universal analyst templates (work in any field)
| File | What it produces |
|------|------------------|
| [document-summarizer.md](document-summarizer.md) | Structured executive summary of any document — severity-tagged key points, deadlines/numbers/parties pulled out, obligations and open questions |
| [comparison-matrix.md](comparison-matrix.md) | Scored, weighted comparison of N options with recommendation and the conditions that would flip it |
| [meeting-prep.md](meeting-prep.md) | Pre-meeting brief — attendees, what each likely wants, focused agenda, questions to be ready for, the single non-negotiable |
| [decision-memo.md](decision-memo.md) | One-page decision memo with recommendation, trade-offs, risks + mitigations, mandatory dissenting view, flip conditions |
| [weekly-comms-digest.md](weekly-comms-digest.md) | A week of emails / Slack / notes turned into a structured digest organized by your priorities, with commitments, decisions, and overdue items surfaced |
| [action-items-extractor.md](action-items-extractor.md) | Clean accountable action-item list from any conversational source — meeting notes, email thread, transcript — with owner / action / due / dependency / source |
| [data-to-dashboard.md](data-to-dashboard.md) | Arbitrary CSV, JSON, tables, lists, or numeric prose turned into a domain-neutral, single-file interactive dashboard with a layout inferred from the data |
| [material-to-deck.md](material-to-deck.md) | Arbitrary source material mapped into an existing branded PowerPoint template while preserving its theme, masters, layouts, fonts, colors, and logo |

### Domain templates (financial crime / intelligence)
| File | What it produces |
|------|------------------|
| [entity-risk-assessment.md](entity-risk-assessment.md) | 8-domain weighted risk assessment of an entity — 0-100 composite, 5-tier rating, red flags, disposition |
| [breaking-news-scan.md](breaking-news-scan.md) | Terse severity-tagged headline feed across your domains; filters hard, returns "quiet scan" rather than padding |
| [alert-triage.md](alert-triage.md) | Transaction-monitoring alert worked to a defensible disposition with for/against factors and an audit-ready memo |
| [control-matrix-builder.md](control-matrix-builder.md) | Structured, testable AML/CFT control inventory across six domains — nine-attribute matrix, domain coverage summary, severity-tagged gap register |
| [committee-reporting-pack.md](committee-reporting-pack.md) | Committee-ready reporting pack — decisions sought vs. items for noting, threshold-coded KPI/KRI dashboard, severity-rated escalations, action tracker, forward calendar |

---

## The pattern every file follows

All standalone files share the same shape. Once you've used one, the rest are familiar.

```
# Title

[one paragraph to the human: "paste this whole file into your assistant"]

---

You are a [role]. [what you do.]

## Inputs the user will provide
[the placeholders — what required vs. optional means here]

## Preflight — do this first
[explicit STOP-and-ASK rule for missing inputs, before any output]

## Method
[step-by-step]

## Output format
[the exact shape of the output]

## Rules
[the quality bar — sourcing, hedging, "no fabrication", etc.]

---

## Render as a formatted deliverable (Word, Excel, PDF, or interactive HTML)
[universal renderer — color palette, typography, accent table]
### Mode A — Word document (.docx)         [python-docx skeleton]
### Mode B — Excel workbook (.xlsx)        [openpyxl skeleton]
### Mode C — PDF narrative report (.pdf)   [HTML+CSS template OR reportlab skeleton]
### Mode D — Interactive HTML dashboard    [single-file HTML + Chart.js template]
### Common rules for all four modes

## Per-analysis customization
[file-specific notes: which format suits this analysis, which sections/tabs/page-types/dashboard-sections to use]
```

The **Preflight** step is the most important difference from naive prompting. Without it, assistants tend to best-effort guess with whatever the user provided and bury the gaps in a footer. With it, the assistant stops, asks a numbered list of clarifications, and waits — producing nothing partial.

The **Render as a formatted deliverable** appendix means the same file produces both the analysis *and* the artifact. After the analysis runs, the user says "render as Word doc" / "give me the Excel version" / "build the HTML dashboard" / "all formats" and the assistant produces the artifact directly (if the environment supports file output) or generates a self-contained Python script the user runs locally. Style is consistent across all four formats — dark theme, severity color system, accent-by-topic, audit-defensible voice.

---

## How to use these on a work machine

Three ways, in order of how often you do the task:

**Occasional** — copy the file, paste it into the assistant's chat, supply your inputs when it asks. To get a formatted artifact, ask: "render as Word doc" / "give me the Excel" / "produce a PDF" / "build the HTML dashboard" / "all formats".

**Recurring** — save the file *once* as the assistant's custom instructions:
- **GitHub Copilot** — paste into `.github/copilot-instructions.md` in a working repo, or save as a reusable prompt file in VS Code.
- **Microsoft 365 Copilot** — create a Copilot agent, paste the file into the agent's instructions, name it ("Document Summarizer", "Decision Memo", etc.), and run it from Copilot Chat. M365 Copilot can produce the Word / Excel / PowerPoint deliverable directly from the spec without running any local code.
- **Claude** — create a Project, paste the file into the Project's custom instructions.
- **ChatGPT** — create a custom GPT with the file as its instructions.

Then you only supply your inputs each time, and request whichever output format the situation calls for.

**For sharing** — send the whole file to a teammate. It runs identically in their assistant of choice.

## Optional Python libraries (for code-based artifact generation)

The renderer is set up so the assistant produces a self-contained Python script when its environment can't generate the artifact directly. To run those scripts the user only needs:

```bash
pip install python-docx openpyxl reportlab
```

For Mode C (PDF), `reportlab` covers Path C2 (pure-Python). Path C1 (HTML to PDF) needs only a browser — the assistant generates HTML, the user prints to PDF. For Mode D (HTML dashboard), no install is needed — the assistant emits a single self-contained `.html` file the user opens in any browser; Chart.js is loaded from a CDN.

---

## When to use `../prompts/` instead

If you want to browse the broader library (29 prompts across 7 categories) and see how each one connects to reference material, samples, and other prompts, start at [`../prompts/`](../prompts/) and the [main README](../README.md). The standalone files here are a curated subset, shaped for single-file portability.
