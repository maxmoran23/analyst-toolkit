# Methodology as a base — set up once, use with thin prompts

The four files in [`../methodology/`](../methodology/) form a self-contained analytical framework. Loaded **once** as your assistant's base instructions, they turn every subsequent task into a thin prompt — you describe what you want and in what format, and the four files supply the voice, the analytical discipline, the quality floor, and the rendering form.

This guide shows the setup for each major assistant, then the thin-prompt patterns that work once the base is in place.

---

## The four files (what you're loading)

| File | What it gives the assistant |
|------|------------------------------|
| [`methodology/analytical-patterns.md`](../methodology/analytical-patterns.md) | Severity tiers (CRITICAL / HIGH / MEDIUM / LOW), source hierarchy, fallback chains, observed vs. alleged vs. projected, quality self-rating |
| [`methodology/audit-defensible-writing.md`](../methodology/audit-defensible-writing.md) | Voice (direct, dense, sourced), banned phrases, hedging discipline, citation style |
| [`methodology/output-quality-standards.md`](../methodology/output-quality-standards.md) | The floor each deliverable type must clear before it ships (memo, research, dashboard, PDF, DOCX, Excel, email, code) |
| [`methodology/report-templates.md`](../methodology/report-templates.md) | Rendering — color palette, accent-by-topic, typography, layout, and working code skeletons for `.docx`, `.xlsx`, `.pdf`, and self-contained `.html` dashboard |

Combined size: ~1,800 lines. They fit comfortably within the custom-instruction budgets of every major assistant.

---

## Setup per assistant

### GitHub Copilot — repo-level instructions

In a working repository, create `.github/copilot-instructions.md` and paste the contents of all four methodology files in this order (the order does not affect the behavior, but this order matches how the files are read across the toolkit):

```
1. analytical-patterns.md
2. audit-defensible-writing.md
3. output-quality-standards.md
4. report-templates.md
```

Copilot Chat in VS Code / JetBrains / github.com automatically uses these as context for that repo. Verify by asking a thin prompt (see below) and confirming the response applies the framework.

Alternatively: keep the four files as VS Code reusable prompt files (`File → Save Prompt`) and reference them by name from Copilot Chat.

### Microsoft 365 Copilot — Copilot agent

Create a new Copilot agent (Copilot Studio or Copilot Chat → Create Agent). Paste the four files into the agent's **Instructions** field, in the order above. Name the agent something memorable ("Analytical Framework", "Audit-Defensible Analyst", etc.). Save.

Then run the agent from Copilot Chat in Word, Excel, Outlook, Teams, or the standalone Copilot Chat app. The agent's first-class access to Word / Excel / PowerPoint means it can produce the artifacts directly without any local code.

### Claude — Project

Create a new Project in claude.ai. In the Project's **Custom instructions** field, paste the four files in order. Save.

Every conversation started inside the Project inherits the framework. Use Claude's Artifacts feature for the HTML dashboard (Mode D) and for any code-generated artifacts.

### ChatGPT — custom GPT

Create a new custom GPT (GPT Builder → Configure). In the **Instructions** field, paste the four files in order. Save and publish (private to you is fine).

Use Code Interpreter / Advanced Data Analysis for the Python-script outputs (Mode A Word, Mode B Excel, Mode C PDF via reportlab). The HTML dashboard (Mode D) renders directly in the assistant's response.

### Any other assistant

If the assistant accepts custom instructions or a system prompt, paste the four files there. If not, paste them at the top of each conversation as a one-time framing message — clunky but works.

---

## Thin-prompt patterns

Once the base is loaded, the prompt itself can be very short. The framework is already in place; the prompt's only job is to scope the task and name the format.

### Pattern 1 — "Do X. Render as Y."

The most common pattern. Name the analysis type and the format.

> "Do an entity risk assessment on Coinbase. Render as a Word doc."
>
> "Compare Chainalysis vs Elliptic vs TRM on detection coverage, integration cost, false-positive rate, sanctions screening, and support quality. Render as an Excel workbook with a comparison-matrix tab and an option-detail tab per vendor."
>
> "Summarize this regulation for a compliance team deciding whether it changes our program. Render as a one-page PDF."
>
> "Build a one-page decision memo on whether to migrate the data warehouse to BigQuery this quarter or defer to next year. Options: migrate now, phase over 6 months, defer. Render as a Word doc."

### Pattern 2 — "Analyze first, then render"

When you want to read the analysis in chat first and decide whether to render.

> "Triage this transaction-monitoring alert. Show me the disposition recommendation in chat first; if I confirm, render the audit-ready memo as both Word and PDF."

### Pattern 3 — "Here's the data, produce X in [format]"

When you have source material to paste.

> "Here are the transactions [paste]. Customer profile: salaried teacher, $4K monthly income, 18-month account, no prior alerts. Alert details: structuring rule, 6 cash deposits under $10K in 8 days. Triage and render as a Word doc."
>
> "Here is the regulation text [paste]. Reader: compliance team deciding whether it changes our program. Summarize and render as a PDF."
>
> "Here are last week's emails and Slack threads [paste]. My role: compliance analyst. Priorities this quarter: stablecoin rule comment, vendor selection, quarterly metrics. Build the weekly digest. Render as HTML dashboard."

### Pattern 4 — "Recurring digest"

When the prompt will run on a schedule and the methodology base is stable.

> "Weekly comms digest for week of 2026-05-26. Priorities: stablecoin rule, vendor selection, metrics package. Source material below. Render as HTML dashboard."
>
> "Breaking news scan. Domains: crypto markets, financial regulation, AI. As of 2026-05-26 9:00 AM ET. Render as HTML dashboard."

### Pattern 5 — "All formats"

When you want the deliverable in every format (e.g., a critical analysis that will be sent in email as PDF, shared in a working channel as Excel, and archived as Word).

> "Do an entity risk assessment on [ENTITY]. Render in all formats — Word, Excel, PDF, and the HTML dashboard."

---

## What makes thin prompts work

Three things have to be true:

1. **The four methodology files are loaded as base instructions.** Without that, the prompt has nothing to inherit from and the output reverts to assistant-generic quality.
2. **The thin prompt names the analysis type specifically enough.** "Do a risk assessment" is too vague; "do an 8-domain entity risk assessment" or "do enhanced due diligence on a digital-asset service provider" gives the assistant a recognizable structure to apply. The methodology base encodes the *framework*, not the specific shape of every possible analysis.
3. **The thin prompt names the format.** If it does not, the assistant gives prose in chat — which is fine when prose is what you wanted, and a problem when you needed a workbook.

When the analysis type does not map to a structure the assistant can derive from the base, fall back to a [`../standalone/`](../standalone/) file (one-file copy/paste) or one of the [`../prompts/`](../prompts/) catalog templates (specifies the structure explicitly).

---

## When to use this workflow vs. the standalone files

| Use methodology-as-base when... | Use a standalone file when... |
|---|---|
| You're doing many different kinds of analyses in the same environment | You're doing one specific kind of analysis |
| You want to keep prompts short and reusable | You're sharing the work with someone who has no setup |
| You're in a Copilot agent / Claude Project / custom GPT you control | You're pasting into a fresh chat with no context |
| The analysis type is one the methodology base can structure on its own | The analysis has a specific structure (8 domains, 5-step typology test, etc.) that needs to be spelled out |
| You want to evolve the framework once and have every task pick it up | You want to grab one file and run |

The two workflows produce equivalent output for any analysis that fits both — they both apply the same methodology. The choice is about how you want to manage the *setup cost*: pay it once and get thin prompts forever, or pay it per-task and get zero setup.

---

## Verifying the base is working

After loading the four files, run a quick verification prompt to confirm the assistant is applying them:

> "Without producing the analysis itself, briefly tell me: what severity tiers will you use for findings in your next analytical task, and what color does each map to in a rendered HTML dashboard? What's the floor for a DOCX deliverable?"

The expected response cites CRITICAL/HIGH/MEDIUM/LOW, names the colors (`#ef4444`, `#f59e0b`, `#22d3ee`, `#6e6e73`), and lists the DOCX floor (cover page, sourced findings, methodology section, sources list, classification footer). If the assistant gives a generic answer or makes things up, the base is not loaded — recheck the custom-instructions configuration in your assistant.
