# New-product approval & new-activity review prompts

These prompts cover the product-risk committee workflow end to end — the lifecycle a new
product, service, channel, or activity moves through at a financial institution: **assess**
before approval → **verify readiness** before launch → **review** at the committed
post-launch date. Each turns an AI assistant into a specific committee-support role with a
defined method, decision criteria, and a structured output the forum can act on, and the
outputs chain: the assessment's condition list feeds the readiness check, and both feed the
post-implementation review.

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
