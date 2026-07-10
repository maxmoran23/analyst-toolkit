# Trade & communications surveillance prompts

These prompts cover market-integrity and conduct surveillance — reviewing trade and
communications alerts for market abuse and misconduct, and building the investigation
case when one is warranted. Each turns an AI assistant into a specific surveillance
analyst role with a defined method, false-positive discipline, and structured disposition.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | Trade-surveillance and communications-surveillance teams, and the market-abuse investigators they escalate to. |
| **The question it answers** | Is this alert or message market abuse, or is there a legitimate explanation I have to rule out first? |
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
| [trade-surveillance-review](trade-surveillance-review.md) | Review a trade-surveillance alert for market abuse (spoofing, layering, wash trading, marking-the-close, front-running, insider dealing): pattern signature, intent assessment, disposition |
| [comms-surveillance-review](comms-surveillance-review.md) | Review a communications-surveillance alert (e-comms / voice) for conduct and market-integrity risk, in context, with strict false-positive discipline |
| [market-abuse-case](market-abuse-case.md) | Build a market-abuse investigation case narrative (insider dealing or manipulation) for a compliance/legal file or a regulator referral |

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
