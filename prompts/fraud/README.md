# Fraud detection & investigation prompts

These prompts cover the fraud lifecycle — distinct from money laundering: scams,
payment fraud, account misuse, and the detection logic behind them. Each turns an AI
assistant into a specific fraud-analyst role with a defined method, indicator set, and
structured disposition.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | Fraud detection, investigations, and disputes teams. |
| **The question it answers** | What kind of fraud is this, how strong are the indicators, and what should happen to the payment? |
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
| [app-fraud-triage](app-fraud-triage.md) | Triage an authorized-push-payment (APP) / scam case: scam-type classification, beneficiary and victim indicators, reimbursement/liability view, recommended actions |
| [wire-fraud-disposition](wire-fraud-disposition.md) | Disposition a flagged wire/payment for fraud (BEC, account takeover, unauthorized): indicators, hold / release / recall decision with the verification step needed |
| [check-fraud-analysis](check-fraud-analysis.md) | Analyze a check/deposit fraud case (counterfeit, altered, forged, kiting, double-presentment): fraud type, loss exposure, disposition |
| [mule-account-review](mule-account-review.md) | Assess an account for money-mule indicators: pass-through, network links, a mule-likelihood tier, and next actions |
| [fraud-typology-mapping](fraud-typology-mapping.md) | Translate a fraud typology into red-flag indicators, detection-rule logic, and control mapping |

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
