# KYC / CDD / Onboarding — team hub

> This financial-crime team is accountable for rating customer risk at onboarding and periodic review, and for assessing the risk of entities and counterparties the firm engages with.

## In one minute

This team decides how much money-laundering and sanctions risk each customer, entity, or counterparty presents, and records a defensible rating that drives downstream controls. The work happens at two moments: when a customer is first onboarded, and again at periodic review, with the same discipline applied to entities and counterparties as relationships form. "Good" looks like a rating that a regulator or auditor can follow line by line — every score tied to a stated factor, mandatory risk floors never silently overridden, and a complete file behind each decision. AI in this toolkit accelerates the mechanical parts: it scores a whole book consistently, drafts the narrative for a file review, and structures an eight-domain entity assessment so nothing is missed. What AI does not do is decide — it produces a recommendation and a rationale; a qualified analyst reviews it, and a human owns the final rating and any escalation.

> **In plain terms:** the tools rate and write up the risk consistently and fast, but a person still signs off on every rating.

## What this team owns

- Customer risk rating (LOW / MEDIUM / HIGH) with mandatory floors that cannot be scored away
- KYC file completeness and rating-defensibility review
- Entity and counterparty risk assessment across multiple risk domains

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Rate a customer / book at scale with floors | customer-risk-rating | framework (runnable, monotonic, floor-safe) | [../frameworks/customer-risk-rating/](../frameworks/customer-risk-rating/) |
| Resolve who ultimately owns or controls an entity — concealed-majority and control-prong aware | beneficial-ownership-resolution | framework (runnable, dual-gated: 0 true owners cleared, 0 unresolved-chain clears) | [../frameworks/beneficial-ownership-resolution/](../frameworks/beneficial-ownership-resolution/) |
| Decide whether two customer records are the same person (dedup, hit adjudication) | entity-resolution-confidence | framework (runnable, dual-gated: never a name-only merge) | [../frameworks/entity-resolution-confidence/](../frameworks/entity-resolution-confidence/) |
| Review a KYC file for completeness & defensibility | customer-file-review | prompt | [../prompts/compliance/customer-file-review.md](../prompts/compliance/customer-file-review.md) |
| Assess an entity / counterparty (8-domain) | entity-risk-assessment | prompt | [../prompts/compliance/entity-risk-assessment.md](../prompts/compliance/entity-risk-assessment.md) |
| One-file entity risk assessment (no setup) | entity-risk-assessment (standalone) | standalone | [../standalone/entity-risk-assessment.md](../standalone/entity-risk-assessment.md) |
| See a finished entity assessment (report) | entity-risk-sample | sample | [../samples/reports/entity-risk-sample.md](../samples/reports/entity-risk-sample.md) |
| See it as a dashboard | entity-risk dashboard | sample | [../samples/dashboards/entity-risk-sample.html](../samples/dashboards/entity-risk-sample.html) |

## How the pieces fit

The framework is the engine for scale — point it at a customer or a whole book and it produces consistent LOW/MEDIUM/HIGH ratings that respect mandatory floors. The two prompts handle the ad-hoc, judgment-heavy work: one reviews a single KYC file for gaps and rating defensibility, the other walks an entity or counterparty through an eight-domain assessment. The standalone version of the entity assessment runs the same logic with no setup, and the samples show what a finished assessment looks like as a written report and as a dashboard. A typical path: rate the book (framework) -> review the weak files (file-review prompt) -> assess any entity or counterparty in scope (entity prompt or standalone) -> render the finished assessment as a report or dashboard for the reviewer.

## Capabilities & limitations

**What these tools DO**

- Score customers and books consistently, with mandatory risk floors that hold (monotonic, floor-safe scoring)
- Surface KYC file gaps and test whether a rating is defensible on its stated factors
- Structure an eight-domain entity / counterparty assessment and produce a written report or a dashboard view
- Give an analyst a fast, repeatable starting point with a clear, auditable rationale

**What they deliberately do NOT do**

- They are reference implementations and methodology aids, not production controls or systems of record
- They score and route; they do not decide — a qualified human reviews and owns the final rating
- They never auto-approve, auto-block, or auto-escalate a customer or counterparty on their own
- They do not unwind beneficial ownership (UBO) — that capability is on the roadmap, not yet covered here

## Start here

1. Open the finished [entity-risk-sample report](../samples/reports/entity-risk-sample.md) (and its [dashboard](../samples/dashboards/entity-risk-sample.html)) to see the standard of output this team produces.
2. Run one entity through the [standalone entity risk assessment](../standalone/entity-risk-assessment.md) — no setup needed — to feel how the eight-domain assessment works end to end.
3. When you are rating more than one customer, switch to the [customer-risk-rating framework](../frameworks/customer-risk-rating/) for consistent, floor-safe scoring across the book, and use the [customer-file-review prompt](../prompts/compliance/customer-file-review.md) to pressure-test any rating before it is finalized.

---

*Coverage status: mature. Customer risk rating, KYC file review, and entity / counterparty assessment are covered. Beneficial-ownership (UBO) unwinding is on the roadmap and not yet part of this toolkit. All artifacts are generic, illustrative reference implementations — no real institution, client, or non-public data.*
