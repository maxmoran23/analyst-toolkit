# Third-party, ABC & correspondent-banking prompts

These prompts cover counterparty and relationship risk beyond the direct customer —
vendors and intermediaries, bribery and corruption exposure, correspondent-banking and
nested access, and trade-based money laundering. Each turns an AI assistant into a
specific risk-analyst role with a defined method, red-flag set, and structured
recommendation.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | Third-party risk, anti-bribery and corruption, and correspondent-banking teams. |
| **The question it answers** | What risk does this vendor, intermediary, or respondent relationship carry, and what must we put in place? |
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
| [vendor-due-diligence](vendor-due-diligence.md) | Third-party / vendor due diligence (onboarding & periodic): risk tiering, multi-domain scorecard, required mitigations, recommendation |
| [abc-risk-assessment](abc-risk-assessment.md) | Anti-bribery & corruption risk assessment (FCPA / UK Bribery Act framing): red flags, risk rating, recommended controls |
| [correspondent-nested-risk](correspondent-nested-risk.md) | Correspondent-banking & nested-account risk (Wolfsberg CBDDQ-style): respondent risk, downstream/PTA exposure, controls, recommendation |
| [tbml-redflag-analysis](tbml-redflag-analysis.md) | Trade-based money laundering red-flag analysis: invoicing/shipment anomalies, price-reasonableness check, disposition |

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
