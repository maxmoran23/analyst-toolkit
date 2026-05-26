# Standalone Prompts — single-file copy/paste

Every file in this directory is a **complete, self-contained instruction set**. Copy one whole file into any AI assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT, or anything comparable), reply with your inputs when asked, and the assistant performs the analysis to a defensible standard. **No other file from this repo is needed** — no references, no companion docs, no zip downloads.

These are the right files to reach for when you want a **single markdown reference** you can keep on a work machine, paste into a Copilot agent's custom instructions, drop into a Claude Project, or share as one block.

---

## What makes these different from `../prompts/`

| | `prompts/` | `standalone/` |
|---|---|---|
| **Shape** | Human-facing wrapper + an isolated ```text``` prompt block + tuning sections | Tiny header for the human, then the whole file *is* the prompt |
| **Cross-references** | Yes — links to `samples/`, `reference/`, paired prompts | None — every reference inlined or removed |
| **Preflight clarification** | Buried in the Rules section at the bottom of the prompt block | A named **Preflight** step before Method — assistant explicitly stops and asks if any required input is missing |
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

### Domain templates (financial crime / intelligence)
| File | What it produces |
|------|------------------|
| [entity-risk-assessment.md](entity-risk-assessment.md) | 8-domain weighted risk assessment of an entity — 0-100 composite, 5-tier rating, red flags, disposition |
| [breaking-news-scan.md](breaking-news-scan.md) | Terse severity-tagged headline feed across your domains; filters hard, returns "quiet scan" rather than padding |
| [alert-triage.md](alert-triage.md) | Transaction-monitoring alert worked to a defensible disposition with for/against factors and an audit-ready memo |

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
```

The **Preflight** step is the most important difference from naive prompting. Without it, assistants tend to best-effort guess with whatever the user provided and bury the gaps in a footer. With it, the assistant stops, asks a numbered list of clarifications, and waits — producing nothing partial.

---

## How to use these on a work machine

Three ways, in order of how often you do the task:

**Occasional** — copy the file, paste it into the assistant's chat, supply your inputs when it asks.

**Recurring** — save the file *once* as the assistant's custom instructions:
- **GitHub Copilot** — paste into `.github/copilot-instructions.md` in a working repo, or save as a reusable prompt file in VS Code.
- **Microsoft 365 Copilot** — create a Copilot agent, paste the file into the agent's instructions, name it ("Document Summarizer", "Decision Memo", etc.), and run it from Copilot Chat.
- **Claude** — create a Project, paste the file into the Project's custom instructions.
- **ChatGPT** — create a custom GPT with the file as its instructions.

Then you only supply your inputs each time.

**For sharing** — send the whole file to a teammate. It runs identically in their assistant of choice.

---

## When to use `../prompts/` instead

If you want to browse the broader library (29 prompts across 7 categories) and see how each one connects to reference material, samples, and other prompts, start at [`../prompts/`](../prompts/) and the [main README](../README.md). The standalone files here are a curated subset, shaped for single-file portability.
