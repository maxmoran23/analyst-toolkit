# New-product approval & new-activity review prompts

These prompts cover the product-risk committee workflow end to end — the lifecycle a new
product, service, channel, or activity moves through at a financial institution: **assess**
before approval → **verify readiness** before launch → **review** at the committed
post-launch date. Each turns an AI assistant into a specific committee-support role with a
defined method, decision criteria, and a structured output the forum can act on, and the
outputs chain: the assessment's condition list feeds the readiness check, and both feed the
post-implementation review.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** Everything you need to use these
> prompts is in this folder. Links out are optional background, never a prerequisite.

|  |  |
|---|---|
| **Who this is for** | New-product approval committees and the financial-crime advisors who brief them. |
| **The question it answers** | Before this product launches, what is its financial-crime risk and what must be true first? |
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
| [npa-risk-assessment](npa-risk-assessment.md) | Assess a proposed new product across nine risk factors: weighted composite, LOW / MEDIUM / HIGH tier with raise-only floor rules (sanctions nexus and digital-asset custody novelty force HIGH), mandatory pre-launch conditions, approval-routing recommendation |
| [product-launch-readiness](product-launch-readiness.md) | Verify approval conditions against actual evidence before go-live: condition-by-condition verification, launch-blocking vs post-launch-trackable classification, GO / GO-WITH-CONDITIONS / NO-GO disposition with unmet conditions named |
| [post-implementation-review](post-implementation-review.md) | Review a launched product at its committed review date: projected-vs-observed comparison, condition compliance, new-risk identification, disposition (close / extend / remediate / escalate back to committee) as a review memo |

**Who this is for:** analysts and second-line reviewers who prepare new-product /
new-activity submissions, sit on or support a product-risk approval forum, or own the
pre-launch and post-launch checkpoints an approval creates. The three prompts enforce the
disciplines committees are examined on: hard attributes cannot be scored around, assertions
are not evidence, and an absence of alerts is a coverage question before it is comfort.

For systematic, validated scoring of the assessment stage at scale — with monotonicity,
floor-safety, and prohibited-routing guarantees — see the runnable
[NPA product-risk framework](../../frameworks/npa-product-risk/README.md); the
[npa-risk-assessment](npa-risk-assessment.md) prompt is the analyst-judgment version of the
same method.

Every prompt is a standalone copy/paste tool — see the [prompt catalog](../README.md) for how the files are built and the [repository overview](../../README.md) for the full toolkit.
