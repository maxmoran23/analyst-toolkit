# Methodology

The *how to do the work* half of the toolkit. The prompts produce the analysis; these four documents define the standard the analysis is held to — the writing voice, the analytical discipline, the quality bar, and the rendering form that make every output consistent and audit-defensible.

Read these four together. The prompts assume them.

Loaded as a **base** into any assistant (Copilot agent custom instructions, Claude Project, ChatGPT custom GPT, GitHub Copilot repo-level instructions), these four files become the framework that turns a thin task prompt into a structured, sourced, properly rendered deliverable. See `report-templates.md` for the thin-prompt patterns this enables.

---

## The four documents

| Document | What it defines |
|----------|-----------------|
| [`analytical-patterns.md`](analytical-patterns.md) | **The discipline.** Five reusable patterns: severity rubrics, the source hierarchy, fallback chains, quality self-rating, and the observed/alleged/projected split. The mechanics that make outputs comparable and honest. |
| [`audit-defensible-writing.md`](audit-defensible-writing.md) | **The voice.** How analytical prose should read — direct, dense, sourced, vendor-skeptical, free of marketing filler. Includes banned phrases, a hedging test, citation style, and before/after rewrites. |
| [`output-quality-standards.md`](output-quality-standards.md) | **The quality bar.** The floor for each deliverable type — memo, research synthesis, dashboard, PDF, DOCX, Excel, email, code. The line below which work is a draft, not a deliverable. |
| [`report-templates.md`](report-templates.md) | **The form.** Style spec, color palette, typography, layout, and working code skeletons for rendering an analysis as Word (`.docx`), Excel (`.xlsx`), PDF, or interactive HTML dashboard. The renderer the standalone files in [`../standalone/`](../standalone/) all share. |

---

## How they fit together

The four documents answer four different questions, and they reinforce each other:

```
analytical-patterns.md       →  How do I think?              (severity, sourcing, confidence)
audit-defensible-writing.md  →  How do I write it down?      (voice, hedging, citations)
output-quality-standards.md  →  Is the deliverable done?     (floor per output type)
report-templates.md          →  How do I render it?          (Word / Excel / PDF / HTML)
```

A worked example, end to end:

1. You run a prompt — say, an entity risk assessment — and ask for a Word doc as the deliverable.
2. **`analytical-patterns.md`** governs the analysis: you rank sources by the hierarchy, tag each finding with a severity tier, keep observed facts separate from allegations, and rate the output's quality.
3. **`audit-defensible-writing.md`** governs the prose: you lead with the answer, cut every marketing phrase, source every number, and hedge only where the data is genuinely uncertain — saying *why*.
4. **`output-quality-standards.md`** governs the finish — for a DOCX deliverable: cover page, sourced findings, methodology section, sources list, classification footer. Below that floor it is a draft, not a deliverable.
5. **`report-templates.md`** governs the form: the cover page uses the accent bar in the topic color, the scorecard table uses the severity color system, the heading hierarchy follows the Heading 1/2/3 pattern, the footer carries classification + date + page number. A working `python-docx` skeleton sits in the file ready to populate.

The result: an output a skeptical reader can trust because every claim is traceable, every uncertainty is labeled, the document is honest about what it does not know — and it *looks* like part of a coherent family of deliverables, regardless of which assistant produced it.

---

## Two ways to use these

### As a methodology base (set up once)

Load all four files as base instructions in your assistant of choice. Then every task is a thin prompt that scopes the work; the four files supply the framework. See `report-templates.md` for example thin-prompt patterns. This is the highest-leverage way to use the toolkit on a work machine.

### As reference (look up when you need them)

Read once, refer back when an output reads off — a piece of prose that sounds like marketing, a deliverable that's missing a section, a Word doc that uses the wrong typography. Each file is short enough to skim against the specific output you're checking.

---

## The core principle

Everything here serves one idea: **analytical work should survive scrutiny.**

A reviewer, a regulator, a colleague, or a future version of you should be able to pick up any output, trace every claim to a source, see exactly where the analysis is certain and where it is not, and find no filler hiding the gaps. That is what "audit-defensible" means, and it is the bar the entire toolkit is built to clear.

The patterns are not bureaucracy. They are what separates analysis from assertion.
