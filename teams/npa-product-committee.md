# New-Product Approval & Product-Risk Committee — team hub

> This team assesses the financial-crime risk of a proposed product or activity before it launches, sets the conditions it must meet, and reviews what actually happened after it went live.

## In one minute

Every product a bank launches eventually generates alerts, and the cheapest place to fix
a financial-crime problem is before the first customer is onboarded. This team is that
checkpoint: it takes a proposal — who it serves, in which markets, settled in what, how
new the activity is to the firm, how attractive it would be to a launderer — and produces
a consistent risk picture, an approval route, the mandatory conditions attached to that
approval, and the date the committee will come back and check. "Good" looks like three
things a regulator asks about directly: a riskier proposal never scores lower than a safer
one, a proposal carrying a serious hard attribute can never be tiered LOW no matter how
benign the rest of it reads, and a prohibited activity is referred to the policy owner
rather than scored around. AI and the runnable engine here supply the consistency — the
same proposal assessed the same way regardless of who picks it up, with the top risk
drivers named — and draft the committee memo, the readiness verification, and the
post-implementation comparison. What they never do is approve anything. The engine routes;
the committee decides whether to launch.

> **In plain terms:** before a new product goes live, someone has to ask how a criminal
> would use it. These tools ask that question the same way every time, write down the
> answer, and hand the committee a decision to make — they never make it.

## What this team owns

- Pre-launch financial-crime risk assessment of a proposed product, service, market, or channel
- Approval routing — deciding which proposals clear at standard approval and which need enhanced review or the full committee
- Prohibited-activity screening — catching the proposals that policy forbids outright, before scoring
- Mandatory pre-launch conditions, and verifying each one is actually evidenced before go-live
- Post-implementation review at the committed date — what was projected against what was observed

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Score and route a proposal consistently (nine factors, floors, routing) | npa-product-risk | framework (runnable, 0 floor-triggered proposals tiered LOW, prohibited never scored around, monotonic) | [../frameworks/npa-product-risk/](../frameworks/npa-product-risk/) |
| Write the committee risk assessment for one proposal | npa-risk-assessment | prompt | [../prompts/npa/npa-risk-assessment.md](../prompts/npa/npa-risk-assessment.md) |
| Verify every approval condition before go-live | product-launch-readiness | prompt | [../prompts/npa/product-launch-readiness.md](../prompts/npa/product-launch-readiness.md) |
| Review the product against its projections after launch | post-implementation-review | prompt | [../prompts/npa/post-implementation-review.md](../prompts/npa/post-implementation-review.md) |
| Carry an open condition or finding through to verified closure | issue-remediation-tracker | prompt | [../prompts/controls/issue-remediation-tracker.md](../prompts/controls/issue-remediation-tracker.md) |
| Reason about the typologies a product would attract | aml-typologies | reference | [../reference/aml-typologies.md](../reference/aml-typologies.md) |
| Render any output as Word/Excel/PDF/HTML | BASE.md | companion | [../BASE.md](../BASE.md) |

## How the pieces fit

A proposal enters at the framework: it scores the nine documented factors, applies the
raise-only floors, and names a route — STANDARD_APPROVAL, ENHANCED_REVIEW, FULL_COMMITTEE,
or REFER_PROHIBITED for anything policy forbids. That routing decides how much writing
happens next. Proposals going to review or committee get the full memo from
npa-risk-assessment, which also fixes the mandatory pre-launch conditions and the
post-launch review interval. At go-live, product-launch-readiness tests each of those
conditions against actual evidence and returns GO, GO-WITH-CONDITIONS, or NO-GO, with
launch-blocking items called out by name. At the committed review date,
post-implementation-review compares what was projected against what the product actually
did, and anything still open becomes a tracked issue via issue-remediation-tracker. The
typology reference keeps the "how would a launderer use this?" question grounded in
observed patterns rather than imagination. Flow: proposal -> score & route -> committee
memo -> conditions -> readiness verification -> launch -> post-implementation review.
Whatever launches becomes the transaction-monitoring and sanctions teams' problem
afterwards, which is exactly why the conditions are set here.

## Capabilities & limitations

**What these tools DO**

- Produce a consistent 0-100 composite, a LOW / MEDIUM / HIGH tier, and a named approval route from the proposal's attributes
- Guarantee the properties a committee is asked to defend: worsening any factor never lowers the score, a floor-triggered proposal can never be tiered LOW, and a prohibited proposal is referred rather than scored
- Name the mandatory pre-launch conditions and the post-launch review interval, so approval is never open-ended
- Test each condition against evidence at go-live and classify what is genuinely launch-blocking
- Compare projected against observed after launch, and surface risks that only appeared once the product was live

**What they deliberately do NOT do**

- They never approve, condition, or launch anything — the engine routes and the memo drafts; the committee decides
- The framework is a reference implementation; the factor weights, floors, and prohibited list are illustrative and must be recalibrated to an institution's own policy
- They do not read the product's actual transaction data, and a readiness verification is only as good as the evidence supplied to it
- A GO-WITH-CONDITIONS is a recommendation to a human owner, not a control that prevents launch

## Start here

1. Open [../frameworks/npa-product-risk/](../frameworks/npa-product-risk/) and read the routing table and the floors — a proposal with digital-asset custody the firm has never operated cannot be tiered LOW, and that single rule explains the engine's design.
2. Take one real (genericized) proposal through [npa-risk-assessment](../prompts/npa/npa-risk-assessment.md) to produce the committee memo, with [aml-typologies](../reference/aml-typologies.md) open beside it.
3. When that product reaches go-live, run [product-launch-readiness](../prompts/npa/product-launch-readiness.md) against the conditions the memo set — and diarize [post-implementation-review](../prompts/npa/post-implementation-review.md) for the review date it committed to.
