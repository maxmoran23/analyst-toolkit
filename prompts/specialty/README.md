# Focused quantitative methods prompts

These prompts apply focused quantitative methods — expected-value and Kelly sizing, and local real-estate market analytics.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | Analysts doing focused quantitative work: expected value, position sizing, local-market analytics. |
| **The question it answers** | What is the edge, and how much should be staked on it? |
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
| [expected-value-analysis](expected-value-analysis.md) | Compute edge and expected value, size with the Kelly criterion, with risk-of-ruin context |
| [local-market-analytics](local-market-analytics.md) | Local real-estate market analytics: tracking, transformation signals, multi-scenario projection |

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
