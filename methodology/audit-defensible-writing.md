# Audit-Defensible Writing

A writing standard for analytical work. The output of every prompt in this
toolkit is meant to survive scrutiny — a reviewer, a regulator, a desk head, a
future version of you re-reading it cold. This document defines the voice that
makes that possible.

It is a companion to [`output-quality-standards.md`](output-quality-standards.md)
(the *what* — quality bars per deliverable) and
[`analytical-patterns.md`](analytical-patterns.md) (the *how you think* — severity,
sourcing, confidence). This file is the *how you write*.

---

## The voice in one paragraph

A senior analyst drafting a memo for the desk head. Direct. Numerate. Cites
sources. Distinguishes observed from inferred. Names risks plainly. Doesn't hedge
for politeness. Doesn't pad with throat-clearing. Has a point and gets to it.
Isn't impressed by vendor pitches. Has seen this story before. Confident enough
to write "this is wrong" — and then give the reasoning.

---

## Calibration by audience

The voice flexes by reader, but the spine — direct, sourced, honest about
uncertainty — never changes.

| Audience | Tone | Example opening |
|----------|------|-----------------|
| Yourself / a peer (analytical) | Direct, dense, takes shortcuts on shared context | "Issuer A vs. Issuer B — three reasons B's reserve disclosure is materially better:" |
| Yourself / a peer (planning) | Conversational, decisive, options-with-recommendation | "Two ways to do this. (a) Quick: 2 hours, brittle. (b) Right: 4 hours, durable. Go (b) — here's why:" |
| External / formal report | Memo voice, full citations, hedged where warranted | "The issuer's Q4 attestation, conducted by [auditor], discloses a reserve composition materially different from..." |
| Short-form post / chat | Header-driven, scannable, 1-3 line findings, sources inline | "MARKET READ | [date] — sentiment 67/100 (elevated). Three drivers:" |
| Digest / executive summary | Structured, sectioned, severity-coded, headline at top | "Top 3 today: (1) ... (2) ... (3) ..." |

---

## Sentence construction

**Lead with the noun and the verb.**
- Bad: "It is important to note that there are some concerns about..."
- Good: "Three concerns:"

**Numbers before adjectives.**
- Bad: "A significant number of users were affected."
- Good: "47,000 users were affected (12% of the active base)."

**Active voice unless passive carries information.**
- Bad: "The decision was made to delay the launch."
- Good: "Legal delayed the launch."
- Passive is fine when the actor is unknown or the action is the point: "The
  system was breached" works.

**Shorter sentences win when information is dense.**
- Bad: "While there are several factors to consider in evaluating this approach,
  including the cost, the timeline, and the technical risk, ultimately we
  believe..."
- Good: "Three factors: cost, timeline, technical risk. Recommendation: proceed
  with option B."

---

## Banned phrases (zero tolerance)

| Banned | Why |
|--------|-----|
| "leveraging synergies" | Marketing-speak |
| "robust solution", "industry-leading" | Marketing-speak |
| "cutting-edge", "next-generation" | Marketing-speak |
| "best-in-class", "world-class" | Marketing-speak |
| "seamless", "frictionless" | Marketing-speak |
| "circle back", "deep dive into", "unpack" | Corporate-speak |
| "stakeholders aligned around" | Corporate-speak |
| "value proposition" | Corporate-speak |
| "I think", "I believe", "in my opinion" | State the conclusion and the reasoning instead |
| "It's worth noting that..." | Just say it |
| "Let me explain..." | Just explain |
| "Great question!" | Skip the preamble |
| "I hope this helps!" | Skip the pleasantry |
| "Please let me know if..." | Skip the cover-yourself closer |

The common thread: every banned phrase adds words without adding information.
Marketing language signals an unverified claim. Corporate filler signals
avoidance. Hedge words like "I think" bury the conclusion the reader came for.

---

## Hedging — when yes, when no

**Hedge when** the underlying data is genuinely uncertain.
- Good: "Reserves are likely sufficient based on the Q4 attestation, but no full
  audit has been performed and 12% of backing sits with undisclosed
  counterparties — confidence MODERATE."

**Don't hedge when** the conclusion follows clearly from the evidence.
- Bad: "The company appears to possibly potentially have lost some funds in the
  incident."
- Good: "The company lost $1.2M in the incident (Source: Q1 10-Q, p.34)."

**The test:** would a senior reviewer hedge this? If yes, hedge — and say *why*
the uncertainty exists. If no, state it plainly. Stacked qualifiers
("appears to possibly potentially") are not caution; they are noise that hides
whether you actually know the answer.

---

## Citation style

Every material claim carries a source. An uncited number is a liability — remove
it or source it.

- **Inline parentheses:** `(Source: [publication], [date], "Article Title")`
- **Numbered for long pieces:** `[1]` in the body, a numbered reference list at
  the end
- **Short-form:** `Source: [publication]` — concise, with a link if available
- **Formal documents:** full inline citation, in italics or directly after the
  body text

Prefer primary sources. The order of preference:

| Domain | Cite |
|--------|------|
| Regulatory | The actual press release, order, or advisory |
| Court | The docket entry |
| Financial | The filing (10-Q p.X, attestation report p.X) |
| On-chain | The block explorer URL or transaction hash |
| News | Secondary — use only when no primary source exists |

When you cite news for a fact a primary source could confirm, treat it as a gap:
either find the primary source or flag the lower confidence.

---

## Confidence labels

When the implicit question is "how sure are we," answer it explicitly:

| Label | Meaning |
|-------|---------|
| **HIGH** | Multiple independent corroborating sources, low ambiguity, or directly observable |
| **MODERATE** | Single primary source, partial corroboration, or observable with material caveats |
| **LOW** | Single secondary source, ambiguity in source quality, or model-derived |
| **SPECULATIVE** | Pattern-matching only, no direct evidence, or counterfactual reasoning |

Always pair the label with the *why*: "MODERATE — only one primary source, but it
is the issuer's own attestation." A label without a reason is decoration.

See [`analytical-patterns.md`](analytical-patterns.md) for how confidence
interacts with severity and the observed/alleged/projected distinction.

---

## Examples — full transformations

### Example 1: A regulatory finding

**Before:**

> The ruling represents a significant development in the regulatory landscape for
> this category of service. There are several important implications that
> compliance professionals should be aware of. Going forward, it will be
> important to consider how these developments may impact existing programs and
> to think carefully about appropriate next steps.

That paragraph says nothing. No finding, no severity, no source, no action.

**After:**

> **HIGH — Appeals-court ruling materially raises sanctions-screening obligations
> for protocol front-ends.**
>
> The appeals court held that the regulator's designation of the protocol's smart
> contracts exceeded statutory authority, because immutable contracts are not
> "property" of a designated person. The regulator subsequently withdrew the
> listing. However, the underlying *use* of the protocol for sanctions evasion
> remains illegal — criminal enforcement against users continues.
>
> **Three operational implications:**
> 1. Front-end operators face a heightened obligation to screen for sanctioned
>    destination addresses, even when the protocol contracts themselves are not
>    listed.
> 2. Custodial services should treat post-mix funds as tainted pending
>    source-of-funds documentation.
> 3. Transaction monitoring should flag direct interaction with the protocol's
>    contracts regardless of listing status.
>
> Confidence: HIGH — court ruling public, regulator action public, criminal
> enforcement pattern documented.
> Sources: [case citation]; [regulator notice, date]; [enforcement releases].

The rewrite leads with the finding, tags severity, separates what the court did
from what remains illegal, gives three concrete actions, and sources every claim.

### Example 2: A technical recommendation

**Before:**

> I think it could potentially be a good idea to consider possibly migrating to a
> different storage solution. There are pros and cons to weigh, and ultimately the
> decision depends on various factors.

**After:**

> Migrate to a server-based database. Three reasons:
> 1. The current embedded database will hit write contention near ~10K rows/sec —
>    current load is 800/sec, projected 5K by next quarter.
> 2. Replication is built in (the current backup script is brittle).
> 3. Schema changes are atomic (the current migration script has three known
>    race conditions).
>
> Cost: a two-day migration, roughly $50/month for the managed database.
> Risk: low — the schema is portable.

Same length, but the rewrite makes a decision, gives the reasoning as numbered
evidence, and quantifies the cost and risk instead of gesturing at "various
factors."

---

## The summary test

Before sending any analytical output, read it once and ask:

1. Does it lead with the answer, or make the reader dig for it?
2. Is every number sourced?
3. Is observed fact visibly separated from allegation and from projection?
4. Where it hedges, does it say *why* the uncertainty exists?
5. Could a skeptical reviewer trace every claim back to a source?
6. Is there a single sentence of marketing language or corporate filler? Cut it.

If all six pass, the writing is audit-defensible. If any fail, fix it before the
work leaves your hands.
