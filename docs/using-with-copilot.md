# Using this toolkit with Copilot (and any AI assistant)

This toolkit is built for one motion: **find a template, copy it, paste it into an assistant, get a structured result.** Nothing to install, no account tied to anything. It works the same in GitHub Copilot, Claude, ChatGPT, or any capable assistant.

This guide covers the workflow end to end.

---

## The two kinds of "codes"

Every reusable block in this repo is one of two kinds. Knowing which you have tells you how to use it.

| Kind | Lives in | What you do with it |
|------|----------|---------------------|
| **A prompt** | [`prompts/`](../prompts/) | Paste it in, fill the `{{PLACEHOLDERS}}`, and the assistant *performs an analysis* — it becomes an entity risk reviewer, a sanctions screener, a regulatory monitor, a researcher. |
| **An output template** | [`output-templates/`](../output-templates/) | Paste it in alongside your content and ask the assistant to *populate the format* — a dashboard, a PDF report, a control matrix. |

The two compose: run a prompt to produce the analysis, then hand the result plus an output template to the assistant to render a finished deliverable.

---

## The core loop — prompts

1. **Find the prompt.** Browse [`prompts/`](../prompts/) or the catalog in the [main README](../README.md). Each file's summary table tells you when to use it and what it produces.
2. **Copy the prompt block.** Every prompt file has exactly one fenced block under `## The prompt`. Copy the whole block.
3. **Fill the placeholders.** Replace every `{{PLACEHOLDER}}` with your input. Do not leave any — an unfilled placeholder produces a vague answer. The `## How to use it` section flags which placeholders matter most.
4. **Paste and run.** Drop it into Copilot Chat (or your assistant of choice) and send.
5. **Check it against the spec.** The prompt file's `## Output structure` section tells you what a complete result looks like. If the assistant skipped a section or a source, ask it to complete that part.

### Working in Copilot

**GitHub Copilot Chat** (VS Code, JetBrains, or github.com) — open the chat panel, paste the filled prompt block, send. To produce a deliverable, open a new file, run the prompt in chat, and paste the result in.

**Microsoft 365 Copilot** — paste a prompt into Copilot Chat, then take the result into the app that fits the deliverable:

| Output | App | How |
|--------|-----|-----|
| Prose — an entity risk assessment, an investigation narrative, a regulatory writeup | **Word** | Run the prompt in Copilot Chat, paste the output into a document, ask Word's Copilot to apply formatting |
| Tables — a control matrix, a risk register, an obligation register | **Excel** | Ask Copilot to render the output as a table, then paste it into a sheet |
| Messages — the communication templates | **Outlook** | Paste an email template plus your content and let Copilot draft the message |

In any Copilot, give the assistant something to work from: paste source material, attach files, or — if your Copilot has web access — tell it to research. A prompt with no inputs and no web access produces a structured *template* of an answer, not a researched one.

---

## Getting output into clean files

The prompts emit Markdown. To turn a result into a saved artifact:

1. Open a new file — `assessment.md`, `brief.md`, whatever fits.
2. Paste the assistant's output.
3. Skim for placeholders the assistant left unfilled (`[like this]`) and the health/confidence line at the end — those tell you where the analysis was thin.
4. Save. For a Word or PDF version, see [`output-templates/document-generation/`](../output-templates/document-generation/).

For a **formatted visual deliverable** — an interactive dashboard or a multi-page PDF report — do not hand-build it. Open the matching file in [`output-templates/`](../output-templates/), paste the template plus your analysis into the assistant, and ask it to populate the template. See the [`samples/`](../samples/) directory for what that produces.

---

## Patterns that make the toolkit stronger

**Run prompts on a cadence with the delta pattern.** Many prompts (regulatory scans, briefs, monitors) accept an optional `PRIOR OUTPUT` placeholder. Paste last run's result in, and the assistant deprioritizes stale items and reports only what changed. The tracked-matters tables become running ledgers.

**Chain prompts.** Output from one is input to another. A `frontier-scan` finding worth a deep look goes into `deep-research-storm`. Several finished assessments feed `cross-source-synthesis`. The severity vocabulary (CRITICAL / HIGH / MEDIUM / LOW) and confidence ratings are consistent across the library so results compose cleanly.

**Adapt the prompt — it is a starting point.** Tighten the scope, change the weighting, add a constraint. Each prompt's `## Tuning & variants` section lists the safe knobs. If you change a scoring weight, have the assistant state the change in its output — that keeps the result audit-defensible.

**Hold the output to the standard.** [`methodology/`](../methodology/) defines the voice, the quality bar, and the analytical patterns. If a result reads like marketing, blends fact with speculation, or makes uncited claims, point the assistant at the relevant rule and ask for a revision.

---

## Quick reference

| You want to... | Go to |
|----------------|-------|
| Assess an entity's risk | [`prompts/compliance/entity-risk-assessment.md`](../prompts/compliance/entity-risk-assessment.md) |
| Screen against sanctions lists | [`prompts/compliance/sanctions-watchlist-screen.md`](../prompts/compliance/sanctions-watchlist-screen.md) |
| Trace blockchain fund flows | [`prompts/blockchain/fund-flow-tracing.md`](../prompts/blockchain/fund-flow-tracing.md) |
| Track a regulatory area | [`prompts/regulatory/regulatory-intelligence-scan.md`](../prompts/regulatory/regulatory-intelligence-scan.md) |
| Research a topic deeply | [`prompts/research/deep-research-storm.md`](../prompts/research/deep-research-storm.md) |
| Produce a recurring brief | [`prompts/briefs/intelligence-brief.md`](../prompts/briefs/intelligence-brief.md) |
| Build an interactive dashboard | [`output-templates/dashboards/`](../output-templates/dashboards/) |
| Build a multi-page PDF report | [`output-templates/pdf-reports/`](../output-templates/pdf-reports/) |
| Produce a compliance document | [`output-templates/compliance-docs/`](../output-templates/compliance-docs/) |
| See what any of it produces | [`samples/`](../samples/) |
