# Adverse-Media Screening — team hub

> This financial-crime team decides whether a negative-news hit is about the right customer and whether it is materially adverse enough to act on.

## In one minute

This team works the negative-news (adverse-media) queue: for every news hit raised against a customer, it answers two plain questions — is this actually our customer, and is the story serious enough to matter for financial-crime risk. "Good" looks like a clean, consistent disposition record where genuinely adverse hits about the right party are escalated, look-alike name matches and trivial articles are cleared with a documented reason, and nothing material is missed. AI is strong at the first-pass sort: it reads large volumes of hits, drafts a relevance and materiality call with rationale, and routes the queue so analysts spend their time on the cases that deserve it. What AI cannot do is make the final risk decision, confirm identity on its own authority, or take any downstream action — it proposes and explains; a qualified analyst confirms, and the institution decides. The tools here are reference implementations and prompts, not connected production controls, so every output is a draft for human review.

> **In plain terms:** the tools sort and reason about negative-news hits so a person can quickly tell the real, serious ones from the noise — but a person still makes the call.

## What this team owns

- Name-to-article relevance — confirming whether a news hit genuinely concerns the customer or is a look-alike name match
- Adverse-media hit disposition — judging whether a confirmed hit is materially adverse and worth escalating
- Entity resolution / disambiguation — separating the right party from same-name or similarly-named entities and individuals

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Disposition negative-news hits at scale | adverse-media-screening | framework (runnable, recall 1.0, 80% FP-cut) | [../frameworks/adverse-media-screening/](../frameworks/adverse-media-screening/) |
| Assess an entity including its adverse-media dimension | entity-risk-assessment | prompt | [../prompts/compliance/entity-risk-assessment.md](../prompts/compliance/entity-risk-assessment.md) |
| Look up the typology / regulatory map | aml-typologies | reference | [../reference/aml-typologies.md](../reference/aml-typologies.md) |

## How the pieces fit

The framework is the workhorse for volume: it screens and dispositions a batch of negative-news hits at scale, cutting the obvious false positives while keeping recall complete so genuinely adverse items survive. The prompt is for the single, deeper look — assessing one entity in full, including its adverse-media dimension — when a hit needs more than a queue-level call. The reference grounds both in the underlying typologies and regulatory context so a disposition rationale can cite why a hit matters. In practice: intake hits -> framework screens and dispositions at scale -> analyst takes survivors into the entity-risk-assessment prompt for a deeper read -> reference confirms the typology / regulatory basis -> escalate or clear with documented rationale.

## Capabilities & limitations

What these tools DO:

- Sort and disposition large volumes of negative-news hits, reducing false positives while preserving complete recall on adverse items
- Draft a relevance and materiality call with a written rationale a reviewer can check or override
- Support deeper, single-entity assessment and ground every call in named typologies and regulatory context

What they deliberately do NOT do:

- Act as production controls — they are reference implementations and prompts, not connected, validated screening systems
- Make the final risk decision — they score and route; a qualified human confirms and the institution decides
- Take any downstream action — they never auto-clear, auto-escalate, auto-block, or file anything on their own

## Start here

1. Read the [adverse-media-screening](../frameworks/adverse-media-screening/) framework — it is the team's primary, runnable tool and shows how hits get screened and dispositioned at scale.
2. Run a small, illustrative batch of hits through it and read the drafted relevance / materiality rationales, then take one survivor into the [entity-risk-assessment](../prompts/compliance/entity-risk-assessment.md) prompt to see the deeper single-entity read.
3. Keep [aml-typologies](../reference/aml-typologies.md) open as you go to ground each disposition in the right typology and regulatory basis. This team sits next to KYC/CDD and Sanctions — cross-link to both hubs, since identity confirmation and sanctions exposure often decide an adverse-media call.
