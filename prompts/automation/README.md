# Communications automation prompts

These prompts build and **maintain** structured artifacts from raw communications —
persistent markdown archives, surgically refreshed reports, and reusable pipeline
specs. They are the repeatable-pipeline lane of the library: each one is designed to
be run again and again over the same growing body of material, extending what exists
instead of regenerating it.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | Any analyst or team running repeatable communications-driven workflows. |
| **The question it answers** | How do I turn raw email and chat material into structured, continuously-maintained files without redoing the work each run? |
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
| [email-thread-structured-extraction](email-thread-structured-extraction.md) | One thread or export in, rigorous structured record out: participants, deduplicated timeline, commitments, decisions, open questions, embedded tables re-emitted clean |
| [comms-driven-report-refresh](comms-driven-report-refresh.md) | Existing report + new communications in, surgical update out: changed-sections-only diff, dated update-log entry, refreshed report with untouched sections byte-preserved |
| [chat-history-index](chat-history-index.md) | Any chat/Teams-style export normalized into per-conversation markdown with speakers, timestamps, and explicit thread-reconstruction rules — plus an incremental mode that extends the archive |
| [recurring-review-pipeline-spec](recurring-review-pipeline-spec.md) | Meta-prompt: describe a recurring review process and get the full operating spec for an assistant-run pipeline — a configured instance of the tools above for your specific desk |

## When to use these — and when not

The library already has one-off summarization prompts: a weekly comms digest, an
action-items extractor, and the recurring-briefing prompts in the briefs category.
Those read a pile of material once and produce a **read-and-discard** output — a
digest you consume, an action list you copy into your tracker. Nothing persists to
the next run.

This category is for the **accumulate-and-maintain** case:

| You want... | Use |
|---|---|
| A five-minute read of the week, then move on | the digest / briefing prompts elsewhere in the library |
| A one-time action list from a meeting | the action-items extractor elsewhere in the library |
| A permanent, growing, greppable archive of your mail or chat | [chat-history-index](chat-history-index.md) (or the mailbox indexer in the standalone directory) |
| A living report that updates surgically as messages arrive | [comms-driven-report-refresh](comms-driven-report-refresh.md) |
| An auditable record of one thread — commitments, decisions, tables | [email-thread-structured-extraction](email-thread-structured-extraction.md) |
| Your own recurring process turned into a written, repeatable pipeline | [recurring-review-pipeline-spec](recurring-review-pipeline-spec.md) |

The distinguishing mechanics of this lane: **deterministic identifiers** (so re-runs
match), **incremental deltas** (later runs emit only what is new or changed),
**byte-preservation** (unchanged content is never reworded), and **unparsed-material
ledgers** (nothing supplied is silently dropped). If none of those matter for your
task, a one-off prompt is the lighter tool.

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
