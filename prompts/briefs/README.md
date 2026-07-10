# Recurring intelligence briefings prompts

These prompts produce recurring, scannable intelligence output — prioritized briefings, weekly reviews, and relevance-filtered news scans.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | Anyone producing a recurring intelligence briefing or a governance-committee reporting pack. |
| **The question it answers** | How do I turn a pile of updates into something a busy reader — or a committee — can act on? |
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
| [intelligence-brief](intelligence-brief.md) | A prioritized, scannable briefing; morning / midday / afternoon / evening variants |
| [weekly-roundup](weekly-roundup.md) | A weekly review with a multi-dimension performance scorecard |
| [breaking-news-scan](breaking-news-scan.md) | A terse, relevance-filtered breaking-news headline scan |
| [committee-reporting-pack](committee-reporting-pack.md) | Assemble a governance-committee reporting pack: KPI/KRI dashboard, escalations, prior-action tracker, forward calendar |

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
