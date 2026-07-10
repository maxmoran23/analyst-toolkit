# Deep research & idea work prompts

These prompts handle deep research, cross-source synthesis, and idea work — multi-perspective investigation, evidence-tiered frontier tracking, and scenario forecasting.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | Anyone who needs a rigorous, sourced deep-dive rather than a search-engine summary. |
| **The question it answers** | What does the evidence actually say, what contradicts it, and how confident should I be? |
| **What these are** | Paste-ready prompt templates. Each file contains one fenced block that *is* the tool: copy it, replace the `{{PLACEHOLDERS}}`, paste it into whatever assistant you already have — Microsoft 365 Copilot, GitHub Copilot, Claude, ChatGPT. |
| **Setup required** | None. Nothing to install, no account, no integration, no repository access. A prompt works when pasted into a locked-down work machine with no file system. |
| **What you get** | A structured, sourced result with a defined method, a scoring rubric, and a fixed output shape — so two analysts running the same prompt produce comparable work. |
| **What they never do** | They draft, score, and structure. They do not decide. Every clear, escalate, block, reimburse, or file decision stays with a person, and an unverifiable claim is labelled or omitted rather than invented. |

### Using one, in about a minute

1. Open any prompt file in this folder and copy the single fenced block under `## The prompt`.
2. Replace every `{{PLACEHOLDER}}` — an unfilled one produces a vague answer.
3. Paste it into your assistant along with the case facts, document, or data.

Want a finished Word / Excel / PDF / dashboard deliverable out of it? Attach one more
file — [`BASE.md`](../../BASE.md) — which carries the writing voice, the quality floor,
and the renderer. **One prompt plus `BASE.md` is the entire system; there is never a
third file**, and a CI job fails the build if any prompt breaks that rule.

<!-- /STANDALONE-BRIEF -->

| Prompt | What it does |
|--------|--------------|
| [deep-research-storm](deep-research-storm.md) | Multi-perspective deep research into a cited long-form article |
| [cross-source-synthesis](cross-source-synthesis.md) | Meta-analysis across many sources: themes, contradictions, blind spots |
| [idea-generation](idea-generation.md) | Cross-domain idea generation, scored on an opportunity rubric |
| [calibration-debate](calibration-debate.md) | Steelman both sides of a thesis, then score its defensibility |
| [research-translation-scan](research-translation-scan.md) | Filter a research stream for signal, translate to practical implications |
| [frontier-scan](frontier-scan.md) | Track speculative research with strict evidence-tiering and forced counter-arguments |
| [futures-projection](futures-projection.md) | Year-by-year multi-metric scenario forecast with confidence bands |

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
