# BASE — the universal companion file

> **The two-file rule.** Any prompt in this toolkit works pasted on its own.
> Attach **this one file** alongside it and you get the full quality system —
> the audit-defensible voice, the analytical discipline, the per-deliverable
> quality floor, and the Word / Excel / PDF / HTML renderer. One prompt +
> `BASE.md`. **Never a third file.**

This file is the entire `methodology/` framework consolidated into a single
attachable document, for environments where attaching multiple files is
costly or impossible — a Copilot chat with no file system, a locked-down work
machine, a one-shot share with a teammate.

**Three ways to load it:**

1. **Attach per task** — attach this file plus one prompt file (or paste both). Done.
2. **Set once as agent instructions** — paste this file into Copilot agent custom
   instructions, Claude Project instructions, or a ChatGPT custom GPT. Every task
   after that needs only the thin prompt.
3. **Repo-level** — drop the contents into `.github/copilot-instructions.md` in a
   working repository.

| Part | What it governs |
|------|-----------------|
| **Part 1 — Voice** | How findings are written down: sourcing, hedging, fact vs. allegation |
| **Part 2 — Method** | How analysis is structured: severity, source hierarchy, confidence, fallbacks |
| **Part 3 — Quality Bar** | The floor every deliverable type must clear before it ships |
| **Part 4 — Renderer** | How to produce a Word / Excel / PDF / interactive-HTML deliverable |

When this file accompanies a task prompt, treat every rule below as binding
instructions, not background reading. Where a task prompt and this file
conflict, the task prompt wins — it carries the task-specific scope.

---

# Part 1 — Voice: Audit-Defensible Writing

A writing standard for analytical work. The output of every prompt in this
toolkit is meant to survive scrutiny — a reviewer, a regulator, a desk head, a
future version of you re-reading it cold. This document defines the voice that
makes that possible.

It is a companion to **Part 3 — Quality Bar (in this file)**
(the *what* — quality bars per deliverable) and
**Part 2 — Method (in this file)** (the *how you think* — severity,
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

See **Part 2 — Method (in this file)** for how confidence
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

---

# Part 2 — Method: Analytical Patterns

Five patterns run through every prompt in this toolkit. They are what make the
outputs comparable, honest, and audit-defensible — a severity tag means the same
thing in a compliance screen as it does in a market brief; a confidence rating is
calculated the same way everywhere.

This document defines the patterns once, so the prompts can assume them.

| Pattern | What it solves |
|---------|----------------|
| [Severity rubric](#1-severity-rubric) | Makes "how bad is this" a shared, comparable scale |
| [Source hierarchy](#2-source-hierarchy) | Makes "how do we know" traceable and ranked |
| [Fallback chains](#3-fallback-chains) | Keeps output useful when a source is unavailable |
| [Quality self-rating](#4-quality-self-rating) | Gives every output a triage signal |
| [Observed vs. alleged vs. projected](#5-observed-vs-alleged-vs-projected) | Stops the three from blending into false certainty |

---

## 1. Severity rubric

Every finding gets a severity tier. The point is comparability: a reader scanning
ten findings across five reports should be able to triage on the tag alone,
without re-reading the underlying analysis.

| Tier | Meaning | Response expectation |
|------|---------|---------------------|
| **CRITICAL** | Immediate, material harm — or a confirmed disqualifying fact. Active and consequential. | Act now. Escalate. Do not wait for the next review cycle. |
| **HIGH** | Significant exposure or a strong adverse signal. Real, but not yet an emergency. | Address deliberately and soon. Put it on the near-term agenda. |
| **MEDIUM** | A genuine issue worth tracking. Moderate exposure, or a signal with material caveats. | Monitor. Schedule. Revisit if it escalates. |
| **LOW** | Minor, informational, or well-mitigated. Noted for completeness. | Awareness only. No action required. |

### How to assign a tier

Severity is a function of two things — **impact** (how much harm if this is
real) and **certainty** (how sure you are it *is* real). A confirmed small
problem and a speculative large problem can land on the same tier.

- A confirmed sanctions hit is CRITICAL — high impact, high certainty.
- A single unverified adverse-media mention of fraud is MEDIUM at most — the
  impact would be high, but the certainty is low. It is not CRITICAL until
  corroborated.
- A documented control gap with no evidence of exploitation is HIGH or MEDIUM —
  real, certain, but not yet harmful.

Do not inflate severity to seem thorough. "No CRITICAL findings" is a legitimate,
valuable result. Manufacturing a CRITICAL tag to pad a report destroys the
signal for every other report.

### Severity vs. confidence

These are different axes. Severity is *how bad*. Confidence (see pattern 4) is
*how sure*. State both. A HIGH-severity finding at LOW confidence is a real
output — it means "this would matter a lot if true, and we are not yet sure it
is true." That sentence is more useful than collapsing the two into one number.

Some workflows use a colored variant of the same four tiers (red / orange /
yellow / green). The labels and the meaning are identical — use whichever the
deliverable's format calls for.

---

## 2. Source hierarchy

Not all sources carry equal weight. Rank them, prefer the top of the ranking, and
make the ranking visible to the reader.

| Tier | Source type | Examples |
|------|-------------|----------|
| **Primary** | The original record. The thing itself. | Regulatory orders and press releases; court docket entries; financial filings and attestations; on-chain transactions; official statistics; the entity's own disclosures |
| **Secondary** | Reporting *about* a primary source. | News articles; analyst notes; law-firm advisories; trade publications; encyclopedic summaries |
| **Unverified** | Claims without a checkable basis. | Social-media posts; anonymous tips; vendor marketing; self-reported metrics with no attestation; rumor |

### Citing discipline

1. **Every material claim carries a source.** A number without a citation is a
   liability. Either source it or remove it.
2. **Prefer primary.** When you cite a secondary source for a fact a primary
   source could confirm, treat that as a gap — go find the primary source, or
   explicitly flag the lower confidence.
3. **Cite the rule before the violation.** In compliance and regulatory work,
   state the standard (the statute, the regulation, the guidance) before stating
   the breach. The reader needs the benchmark to judge the finding.
4. **Unverified is not a source — it is a lead.** A claim from an unverified
   source can be reported ("an unverified post alleges X"), but it cannot support
   a finding until a primary or secondary source corroborates it.
5. **Vendor and self-reported claims are unverified by default.** A vendor
   whitepaper, a company's own metric, a marketing page — treat all of these as
   unverified until an independent source or an attestation backs them.

### Citation formats

Match the format to the deliverable, but always make the source traceable.

| Source type | Format |
|-------------|--------|
| Statute | `31 U.S.C. § 5318(g)` |
| Regulation | `31 CFR § 1010.314` |
| Agency guidance | `[Advisory ID] ([date])` |
| Enforcement / regulatory action | `[Agency] [action], [date]` |
| Court decision | `[Party] v. [Party], No. [docket] ([court] [year])` |
| Financial filing | `[Entity] Form 10-Q, [period], p.X` |
| Attestation | `[Entity] [report name] ([auditor]), p.X` |
| News | `[Publication], [date], "Headline"` |
| On-chain | Transaction hash or block-explorer URL |

---

## 3. Fallback chains

A finding often depends on an external input — a live data feed, a search result,
a document, a prior analysis. Any of those can be unavailable. A fallback chain
defines what to do when the best input is missing, so the output degrades
gracefully instead of failing silently.

### The principle

In a one-off, interactive task, failing fast is often correct — surface the error
and let a human fix it. But for any output meant to stand on its own (a scheduled
report, a deliverable handed off without supervision), a hard failure is worse
than a degraded result, because:

- A failed run produces nothing — no signal that anything is wrong.
- Anything downstream has nothing to consume.
- The work *appears* fine while being silently broken.

A fallback chain trades perfection for observability. A degraded output is a loud
signal: it ships labeled as degraded, its quality rating drops, and a reviewer
can see the problem. A hard failure masks it.

### The canonical chain

Every data-gathering step defines an ordered chain. Try the best source first;
fall back on failure; always produce *some* output.

```
Primary:    The best source available — the authoritative feed, the real-time API,
            the primary document.
Secondary:  An alternative — a general search, a secondary API, cached data from a
            recent run.
Tertiary:   State-only — report what was last known, explicitly flagged as stale.
            No new finding, but an honest "here is the last good read."
```

Only step outside the chain with an explicit, loud escalation. Never fail
silently.

### Rules

1. **Every output names the tier it used.** A footer field — "Primary",
   "Secondary (fallback: primary source unreachable)", "Tertiary (data stale as
   of [timestamp])" — tells the reader exactly how much to trust the result.
2. **The tertiary fallback always produces output.** Even when everything is
   broken, emit a minimal result that says so. A reader must be able to tell
   "ran, but everything was down" apart from "did not run."
3. **Fallback use lowers the quality rating** (see pattern 4). Secondary and
   tertiary tiers cap the score — this makes the rating a reliable proxy for
   source health over time.
4. **Chronic fallback use is a signal to investigate.** If a step hits secondary
   or tertiary repeatedly, the primary source is dead, the configuration has
   drifted, or the primary choice was wrong from the start. Fix the cause; do not
   normalize the degradation.

### When the pattern does *not* apply

Fallback chains are for *intelligence and observability* output. They do **not**
apply to actions with downstream effects:

- **Destructive or write actions** — never fall back on a write. If a save fails,
  escalate loudly rather than writing something partial.
- **Compliance-critical enrichment** — never fall back on a sanctions-list check.
  If the sanctions source is down, the finding cannot be emitted; escalate
  instead. A degraded sanctions screen is worse than no screen, because it looks
  complete.
- **Execution** — anything that commits a transaction waits for primary data or
  aborts. It never degrades.

For those, the right pattern is the opposite: strict preconditions, explicit
refusal, loud escalation.

---

## 4. Quality self-rating

Every substantial output rates its own quality. The rating is a *triage signal* —
it lets a reviewer decide how hard to scrutinize a given output before reading
it. It is not a substitute for review; it makes review efficient.

### The two scales

Use whichever fits the deliverable. They map to each other.

**Numeric (1-10):**

| Score | Meaning |
|-------|---------|
| **9-10** | Best case — primary sources active, strong signal, clear synthesis, findings well-supported |
| **7-8** | Solid — good source coverage, reliable output, minor gaps |
| **5-6** | Adequate — some data gaps, thin coverage, or mostly low-severity findings |
| **3-4** | Degraded — significant fallback use, limited coverage, quality compromised |
| **1-2** | Minimal — primary sources down, near-placeholder output |

**Categorical:**

| Rating | Maps to | Meaning |
|--------|---------|---------|
| **HIGH** | 7-10 | Trust it. Primary sourcing, defensible findings. |
| **MODERATE** | 4-6 | Read with care. Gaps, caveats, or partial fallback use. |
| **LOW** | 1-3 | Treat as provisional. Degraded sourcing or thin coverage. |

### What goes into the rating

The score is not a vibe. It answers three concrete questions:

1. **Source quality.** Were primary sources active? Which fallback tier was used?
   Was the data fresh? (Fallback use lowers the score — see pattern 3.)
2. **Output density.** Were there enough substantive findings to be useful? Or is
   the report padded?
3. **Confidence.** Can every finding be defended with a citation? Were source
   conflicts resolved or at least flagged? Is the language over-hedged or
   over-claimed?

A high self-rating has to be defensible on all three. The rating is trustworthy
not because the rater is objective, but because the rubric is explicit — the
rater is answering specific questions, not inventing a number.

### Why self-rating works

- **The rubric constrains the rating.** It is an answer to fixed questions, not a
  free-form judgment.
- **Low scores are honest, not failures.** A 4/10 that correctly reflects a
  degraded run is a *good* output — it tells the reader the truth. Inflating it
  to 8/10 is the only failure.
- **There is no incentive to inflate.** The rater gains nothing from a high
  score. The rubric explicitly requires fallback use to lower it.

### Where the rating goes

Put it in the output — typically a footer:

```
Quality: [score]/10  |  Sources: [list]  |  Fallbacks: [count]  |  [runtime]
```

The rating is the most visible signal in the footer. A reader scanning a stack of
outputs can filter mentally: high, read closely; moderate, skim; low, treat as
provisional. The delta itself is information — the same source rating 8/10 today
and 5/10 tomorrow says something changed.

---

## 5. Observed vs. alleged vs. projected

The single most important discipline in analytical writing: never let these three
blend. Blending them manufactures false certainty — the most common and most
dangerous failure in an analytical document.

| Category | Definition | How to mark it |
|----------|------------|----------------|
| **Observed** | A fact you can point to in a primary source. It happened; here is the record. | State it plainly. Cite the source. |
| **Alleged** | A claim someone has made that is not yet confirmed. An accusation, a pending matter, an unverified report. | Label it: "alleged", "reportedly", "a pending suit claims". Name who alleges it. |
| **Projected** | A forward-looking estimate, forecast, or model output. It has not happened and may not. | Label it: "projected", "estimated", "the base case assumes". State the assumptions. |

### The rule

Every sentence makes clear which of the three it is. A reader must never have to
guess whether they are reading a fact, an accusation, or a forecast.

- **Observed:** "The company reported a $1.2M loss in Q1 (Source: 10-Q, p.34)."
- **Alleged:** "A class-action complaint filed in March alleges the loss was
  concealed from investors. The allegation is unproven; the matter is pending."
- **Projected:** "If the litigation settles near the plaintiffs' demand, the
  estimated additional exposure is $4-6M. This is a projection, not a reserve."

Three sentences, three categories, each one unmistakable.

### Why it matters most in compliance and risk work

- An **allegation reported as a finding** can defame an entity and will not
  survive review. A pending suit is not a verdict. An investigation is not a
  conviction. Write them as what they are.
- A **projection reported as a fact** turns a model output into a false
  certainty. A forecast that omits its assumptions cannot be evaluated or
  challenged — and a forecast that cannot be challenged is not analysis.
- The severity rubric (pattern 1) depends on this distinction. An observed
  disqualifying fact is CRITICAL. The same fact merely *alleged* is not — it is
  MEDIUM until corroborated. Collapse observed and alleged and the severity tag
  becomes meaningless.

When evidence is thin, say so and lower the confidence rating. Do not fill the
gap with inference dressed as fact. An honest "this could not be verified" is
worth more than a confident sentence that cannot be defended.

---

## The patterns together

These five are not independent — they reinforce each other:

- The **source hierarchy** determines what counts as **observed** (a primary
  source) versus **alleged** (an unverified claim).
- **Fallback-chain** tier feeds directly into the **quality self-rating** — a
  tertiary fallback caps the score.
- The **observed/alleged/projected** split sets a ceiling on **severity** — only
  observed facts can carry the top tiers at high confidence.
- The **quality rating** tells a reader how hard to scrutinize everything else.

Applied together, they produce the toolkit's core property: an output a skeptical
reader can trust, because every claim is traceable, every uncertainty is labeled,
and the document is honest about what it does not know.

---

# Part 3 — Quality Bar: Output Standards

Quality bars per output type. When you generate any deliverable below, the bar
described is the **floor** — not the ceiling. Anything under the floor is not
done; it is a draft.

This is a companion to **Part 1 — Voice (in this file)**
(the writing voice) and **Part 2 — Method (in this file)**
(severity, sourcing, and confidence discipline).

---

## Analytical memo / writeup (prose)

The most common deliverable: a structured analysis a reader can act on.

**Floor:**
- Bottom Line / Executive Summary at the top — three sentences maximum
- Key Findings — 3-7 bullets, each severity-tagged and sourced
- Analysis section — organized by sub-question, not by stream of consciousness
- Risks & Counterpoints section — the bear case stated honestly
- Methodology — one paragraph: what you looked at, what you couldn't
- Sources — numbered, with full citations

**Voice:** audit-defensible. Lead with the answer, source every claim, separate
observed from inferred.

---

## Research / synthesis

A multi-source investigation that has to hold up to a skeptical reader.

**Floor:**
- Three or more independent sources for any quantitative claim
- At least one primary source per major finding
- Observed / reported / estimated / inferred kept visibly distinct
- A contrarian / bear-case section — not optional
- A confidence rating (HIGH / MODERATE / LOW / SPECULATIVE) on each major finding
- Sources cited inline in the body *and* listed at the end

A synthesis that only cites secondary sources, or that omits the contrarian
section, has not met the floor.

---

## HTML dashboard (interactive)

**Floor:**
- Self-contained single-file HTML — no build step, no broken external
  dependencies
- Dark theme by default
- Four or more analytical sections
- At least one chart
- A sortable / filterable data table when the data exceeds ~10 rows
- A footer with the generation date and the sources
- Responsive at roughly 600 / 900 / 1200px breakpoints

For a topic that warrants depth, aim well above the floor: 10-20 sections,
modals, search, an export control. The floor is the minimum that ships; a
flagship dashboard is a different ambition.

---

## PDF report

**Floor:**
- A cover page — title, date, author
- A table of contents if the document runs longer than five pages
- Sourced findings — citations inline or footnoted
- A methodology section
- A scope / disclaimer footer

For a formal analytical deliverable, treat the floor as the starting point and
build toward a designed, multi-section report.

---

## DOCX report

**Floor:**
- A title page with metadata
- A table of contents for documents longer than five pages
- Section headers with consistent styling (Heading 1 / 2 / 3)
- Tables for any comparison of three or more items
- A sources section at the end
- Page numbers

Generate Word documents with a proper library and explicit style application.
Do not hand-write the underlying XML.

---

## Excel workbook

**Floor:**
- A multi-tab structure — a Cover/Summary tab, Data tab(s), and a Dashboard tab
  where relevant
- A frozen header row on data tabs
- Cell formatting — currency ($1,234.50), percentages (12.3%), dates
  (YYYY-MM-DD)
- Filtering enabled on data tabs
- Cell borders, no heavy gridlines
- Color coding for severity or status (red / amber / green)

Use a styling-capable library for full control. A quick unstyled dump from a
dataframe is a draft, not a deliverable.

---

## Email

**Floor:**
- An HTML body, not plain text
- A specific subject line — not "Daily Update" but "Daily Digest, [date]:
  [the two or three things that matter]"
- A greeting (skipping it is fine for automated digests)
- A top-of-fold summary — three bullets maximum, the key metrics
- Body sections with clear headers
- A footer with generation metadata
- Mobile-optimized — roughly 600px maximum width

---

## Short-form post / channel message

**Floor:**
- A header line — source/agent name and date/time
- A bold lead line carrying the single most important insight
- A score or metric dashboard when composite metrics are relevant
- Severity-coded finding cards
- A footer with sources, any fallbacks used, a quality rating, and runtime

**Threading discipline:** keep the top-level message short (a summary of ~500
characters or less); put the full report in a thread reply. This keeps a channel
scannable.

---

## Code

**Floor:**
- Runs without errors the first time — test it before declaring it done
- Type hints on every function signature (or the language's equivalent)
- A docstring only when the function's purpose is not obvious from its name
- No commented-out code
- No "TODO" markers without a linked issue or a concrete follow-up plan
- No debugging print statements left in

**Style:** match the surrounding codebase. For a new project, pick a standard
formatter and linter and apply them consistently.

---

## What "done" means

A deliverable is **done** when:

1. It meets the floor for its output type (above).
2. The voice matches the audience (see
   **Part 1 — Voice (in this file)**).
3. Sources are cited.
4. It has been spot-checked — numbers reconcile, charts render, links resolve.
5. Observed fact, allegation, and projection are visibly separated.

A deliverable is **not done** when:

- Sections are placeholders ("TBD", "Lorem ipsum").
- Charts have not been visually verified.
- Numbers have not been reconciled against their source.
- Citations are broken or missing.
- The output reads as generic, hedge-heavy, marketing-toned filler — the
  hallmark of work that was generated but never reviewed.

The floor is not a stretch goal. It is the line below which the work should not
leave your hands.

---

# Part 4 — Renderer: Word / Excel / PDF / HTML deliverables

When the user asks for a formatted deliverable, apply the renderer below to the analysis already produced. It defines four modes, a shared style standard, and working code skeletons.

---

## Render as a formatted deliverable (Word, Excel, PDF, or interactive HTML)

After the analysis above is produced, the user may ask for a formatted deliverable. Render in whichever format they request — Word document, Excel workbook, PDF report, or interactive HTML dashboard — using the patterns below. Each pattern is **fully self-contained**: no other file from any repository is required, and no shared library beyond standard format libraries (`python-docx`, `openpyxl`, `reportlab`, Chart.js from CDN).

The renderer below has four modes. The user invokes a mode with phrases like:
- *"Word doc"* / *"render as .docx"* / *"give me the report version"* → Mode A
- *"Excel"* / *".xlsx"* / *"workbook"* / *"spreadsheet"* → Mode B
- *"PDF"* / *"narrative report"* / *"formal report"* → Mode C
- *"dashboard"* / *"interactive HTML"* / *"single-page view"* → Mode D
- *"all formats"* / *"every format"* → produce each in turn

If the user does not specify a mode and the analysis would clearly benefit from one over the others, recommend it (see Per-analysis customization at the end of this file).

### How the assistant should produce the artifact

Two paths depending on what the assistant's environment can do:

1. **Direct file output** — Microsoft 365 Copilot in Word/Excel, Claude with file-producing tools, ChatGPT with Code Interpreter, or any assistant with a document-authoring skill. Produce the artifact directly using the style spec below and deliver the file.
2. **Code-based output** — GitHub Copilot Chat, plain chat assistants, or any environment without direct file output. Generate a self-contained Python script (or self-contained HTML file for Mode D) that the user runs locally to produce the artifact. Include the install command at the top of the script.

Either way, the artifact follows the style spec below. Style consistency is what makes a deliverable look professional rather than AI-generic.

---

### Universal style standards (apply to all four modes)

**Voice:** Direct, audit-defensible, no marketing language, no emojis in the artifact. Severity tags preserved exactly as in the analysis (CRITICAL / HIGH / MEDIUM / LOW). Every material claim sourced. "No adverse findings" and "Information gap" are valid, valuable findings — never padded over.

**Color palette** (dark-theme deliverables — Modes C and D, optional for Mode A header bar):

| Token | Hex | Use |
|---|---|---|
| `BG_PRIMARY` | `#111827` (PDF) / `#0a0a0f` (HTML) | Page background, full-bleed |
| `BG_CARD` | `#1a1f35` (PDF) / `#1c1c23` (HTML) | Card/table backgrounds |
| `ACCENT` | per topic (see table below) | Hero numbers, chart fills, section borders |
| `TEXT_PRIMARY` | `#ffffff` (PDF) / `#f5f5f7` (HTML) | Headings, hero stats |
| `TEXT_BODY` | `#c8ccd4` | Body prose |
| `TEXT_MUTED` | `#6e6e73` / `#8b92a0` | Captions, footnotes, page headers |
| `SEVERITY_CRITICAL` | `#ef4444` | CRITICAL items |
| `SEVERITY_HIGH` | `#f59e0b` | HIGH items |
| `SEVERITY_MEDIUM` | `#22d3ee` | MEDIUM items |
| `SEVERITY_LOW` | `#6e6e73` | LOW / background items |
| `POSITIVE` | `#30d158` | Positive findings, clearances, "no adverse findings" |

**Accent color by topic domain** (set once, used throughout):

| Topic | Accent | Hex |
|---|---|---|
| Finance / Trading | Amber-Gold | `#f59e0b` |
| Crypto / Blockchain | Cyan-Teal | `#22d3ee` |
| Regulatory / Legal / Compliance | Blue | `#0a84ff` |
| Research / Academic | Purple | `#bf5af2` |
| Health / Fitness | Green | `#30d158` |
| Career / Professional | Indigo | `#5e5ce6` |
| Sports / Performance | Orange | `#ff9f0a` |
| Real Estate | Emerald | `#10b981` |
| Technology / AI | Electric Blue | `#5e5ce6` |
| Media / Entertainment | Red-Pink | `#fa2d48` |

**Typography:**
- Family: Helvetica / Arial / system sans-serif (`-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif`)
- Section headers: ALL CAPS with 2–3px letter spacing in formal modes (C, D); Title Case in Mode A
- Hero stat: 72pt+ (Mode C cover), 48pt+ (Mode D hero)
- KPI numbers: 28–36pt
- Body: 10–11pt
- Captions / metadata: 8pt muted

**Page / canvas layout:**
- Mode A (Word): 1" margins, Calibri 11 default, Heading 1/2/3 hierarchy
- Mode B (Excel): Frozen header row, 11–14pt fonts, alternating row shading
- Mode C (PDF): Letter (8.5×11"), 54pt top/bottom and 60pt L/R margins, full-bleed dark bg, running page header from page 2
- Mode D (HTML): Responsive grid (5 → 3 → 2 → 1 col breakpoints at 1200/900/600px), max-width 1400px

**Severity / status badges:** rounded pills, color from palette above, 9–10pt uppercase letter-spaced text. In Word, use shaded table cells; in Excel, conditional formatting on the severity column.

---

### Mode A — Word document (.docx)

**When to use:** Stakeholder hand-off, signature workflows, formal memos, regulatory submissions, anything that gets redlined or printed.

**Style spec:**
- Cover page: title, subject, date, classification, author/version
- Heading hierarchy: Heading 1 = major sections, Heading 2 = sub-sections, Heading 3 = nested detail
- Tables: bordered, header row bolded with light background fill, alternating row shading for ≥10 rows
- Page numbers: bottom center, "Page X of Y"
- Footer: classification + date, left-aligned
- Optional: dark accent bar across top of cover page (accent color from palette)
- Font: Calibri 11 body, Calibri 14–16 bold headings (or Arial / Times New Roman if user prefers serif)
- Margins: 1" all sides
- Severity tags: rendered as colored shaded cells in scorecards, or as bold colored text inline

**Self-contained generator (Python, `python-docx`):**

```python
# pip install python-docx
# Run: python word_report.py
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT_PATH = "report.docx"

# ---- Customize per analysis ----
TITLE = "{{ ANALYSIS TITLE }}"
SUBJECT = "{{ SUBJECT (entity / topic / decision) }}"
DATE = "{{ YYYY-MM-DD }}"
AUTHOR = "{{ AUTHOR }}"
CLASSIFICATION = "Internal — for analytical use"
ACCENT_HEX = "0A84FF"  # set per topic, no leading #

# Each section: ("Heading Text", "body paragraph(s) — \\n-separated for multiple paras")
# Or for a table section: ("Heading", {"table": [["col1","col2"], ["v1","v2"], ...]})
SECTIONS = [
    ("Executive Summary", "{{ 3-5 sentence exec summary from the analysis output }}"),
    ("Scorecard / Findings", {"table": [
        ["Domain", "Score", "Weight", "Weighted", "Key driver"],
        # ...one row per scorecard row from the analysis...
    ]}),
    ("Detail", "{{ per-section narrative from the analysis output, separated by \\n\\n }}"),
    ("Red Flags / Risks", "{{ bulleted findings — one per line, prefixed with '- ' }}"),
    ("Information Gaps", "{{ what could not be established }}"),
    ("Recommended Disposition", "{{ recommendation + reasoning }}"),
    ("Sources & Confidence", "{{ source list + overall confidence rating }}"),
]
# --------------------------------

def add_accent_bar(doc, hex_color):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    top = OxmlElement("w:top")
    top.set(qn("w:val"), "single"); top.set(qn("w:sz"), "36")
    top.set(qn("w:space"), "1"); top.set(qn("w:color"), hex_color)
    pBdr.append(top); pPr.append(pBdr)

def set_cell_shading(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color); tcPr.append(shd)

def add_page_number(paragraph):
    run = paragraph.add_run()
    fldChar1 = OxmlElement("w:fldChar"); fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText"); instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar"); fldChar2.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1); run._r.append(instrText); run._r.append(fldChar2)

def build():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1); s.bottom_margin = Inches(1)
        s.left_margin = Inches(1); s.right_margin = Inches(1)

    style = doc.styles["Normal"]; style.font.name = "Calibri"; style.font.size = Pt(11)

    add_accent_bar(doc, ACCENT_HEX)
    t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = t.add_run(TITLE); run.font.size = Pt(28); run.bold = True
    sub = doc.add_paragraph(SUBJECT); sub.runs[0].font.size = Pt(16); sub.runs[0].font.color.rgb = RGBColor(0x6E,0x6E,0x73)
    meta = doc.add_paragraph(f"Date: {DATE}    Author: {AUTHOR}    Classification: {CLASSIFICATION}")
    meta.runs[0].font.size = Pt(10); meta.runs[0].font.color.rgb = RGBColor(0x6E,0x6E,0x73)
    doc.add_page_break()

    for heading, content in SECTIONS:
        h = doc.add_heading(heading, level=1)
        h.runs[0].font.color.rgb = RGBColor.from_string(ACCENT_HEX)
        if isinstance(content, dict) and "table" in content:
            rows = content["table"]
            table = doc.add_table(rows=len(rows), cols=len(rows[0]))
            table.style = "Light Grid Accent 1"
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    cell = table.cell(i, j)
                    cell.text = str(val); cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                    if i == 0:
                        for r in cell.paragraphs[0].runs: r.bold = True
                        set_cell_shading(cell, ACCENT_HEX)
            doc.add_paragraph()
        else:
            for para in str(content).split("\n\n"):
                doc.add_paragraph(para.strip())

    section = doc.sections[0]
    footer = section.footer.paragraphs[0]
    footer.text = f"{CLASSIFICATION}    {DATE}    "
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_number(footer)

    doc.save(OUT_PATH)
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    build()
```

---

### Mode B — Excel workbook (.xlsx)

**When to use:** Multi-section data, scorecards, registers, comparison matrices, anything the user will filter, sort, or update. Best when there's tabular data that benefits from manipulation.

**Style spec:**
- Tab 1 = **Summary / Dashboard** (KPIs, top finding, confidence). Always present.
- Tab 2..N = one tab per major analysis section, with the section name as the tab name
- Header row: bold, accent-color fill, white text, frozen pane
- Data validation: dropdowns for severity / disposition / status columns
- Conditional formatting: red ≥ HIGH-equivalent threshold, amber MEDIUM, green LOW or positive
- Number formats: currency `$#,##0.00`, percentages `0.0%`, dates `YYYY-MM-DD`
- Filters auto-enabled on every data tab
- Print area set on the Summary tab; orientation landscape
- Optional: an embedded chart on Summary if there's quantitative data worth visualizing

**Self-contained generator (Python, `openpyxl`):**

```python
# pip install openpyxl
# Run: python excel_report.py
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

OUT_PATH = "report.xlsx"

# ---- Customize per analysis ----
TITLE = "{{ ANALYSIS TITLE }}"
SUBJECT = "{{ SUBJECT }}"
DATE = "{{ YYYY-MM-DD }}"
ACCENT_HEX = "0A84FF"

# Summary KPIs (label, value, severity_or_color)
KPIS = [
    ("Headline Finding", "{{ one-line bottom line }}", "neutral"),
    ("Composite / Score", "{{ N/100 }}", "high"),
    ("Confidence", "{{ HIGH / MODERATE / LOW }}", "neutral"),
    ("Items Surfaced", "{{ count }}", "neutral"),
]
# Each tab beyond Summary: (sheet_name, header_row, data_rows, severity_col_index_or_None)
DATA_TABS = [
    ("Scorecard", ["Domain", "Score", "Weight", "Weighted", "Key driver"],
        [
            # one row per scorecard row from analysis output
        ], 1),  # severity_col_index = index of column to apply red/amber/green to (0-based), or None
    ("Findings", ["Severity", "Finding", "Source", "Action"],
        [
            # one row per finding from analysis output
        ], 0),
    ("Gaps", ["Gap", "Why it matters", "How to close"],
        [
            # one row per information gap
        ], None),
]
# --------------------------------

HEADER_FILL = PatternFill("solid", fgColor=ACCENT_HEX)
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
TITLE_FONT  = Font(bold=True, size=18)
SUB_FONT    = Font(size=11, color="6E6E73")
BORDER      = Border(left=Side(style="thin", color="DDDDDD"),
                     right=Side(style="thin", color="DDDDDD"),
                     top=Side(style="thin", color="DDDDDD"),
                     bottom=Side(style="thin", color="DDDDDD"))

SEV_COLORS = {
    "CRITICAL": ("FCA5A5", "7F1D1D"),
    "HIGH":     ("FDE68A", "78350F"),
    "MEDIUM":   ("A7F3D0", "064E3B"),
    "LOW":      ("E5E7EB", "374151"),
    "POSITIVE": ("BBF7D0", "065F46"),
}

def style_header_row(ws, row=1):
    for cell in ws[row]:
        cell.font = HEADER_FONT; cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="left", vertical="center")
        cell.border = BORDER
    ws.freeze_panes = ws.cell(row=row+1, column=1)
    ws.row_dimensions[row].height = 22

def autosize(ws, min_w=10, max_w=60):
    for col_cells in ws.columns:
        length = max((len(str(c.value)) for c in col_cells if c.value is not None), default=min_w)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, min_w), max_w)

def add_severity_formatting(ws, col_index, start_row=2):
    col_letter = get_column_letter(col_index + 1)
    rng = f"{col_letter}{start_row}:{col_letter}1000"
    for sev, (fill_hex, _) in SEV_COLORS.items():
        rule = CellIsRule(operator="equal", formula=[f'"{sev}"'],
                          fill=PatternFill("solid", fgColor=fill_hex))
        ws.conditional_formatting.add(rng, rule)

def build_summary(wb):
    ws = wb.active; ws.title = "Summary"
    ws["A1"] = TITLE; ws["A1"].font = TITLE_FONT
    ws["A2"] = SUBJECT; ws["A2"].font = SUB_FONT
    ws["A3"] = f"Date: {DATE}"; ws["A3"].font = SUB_FONT
    ws["A5"] = "KPI"; ws["B5"] = "Value"; ws["C5"] = "Severity"
    style_header_row(ws, row=5)
    for i, (label, val, sev) in enumerate(KPIS, start=6):
        ws.cell(row=i, column=1, value=label).font = Font(bold=True)
        ws.cell(row=i, column=2, value=val)
        sev_cell = ws.cell(row=i, column=3, value=sev.upper())
        fill_hex = SEV_COLORS.get(sev.upper(), ("E5E7EB","374151"))[0]
        sev_cell.fill = PatternFill("solid", fgColor=fill_hex)
    autosize(ws)
    ws.print_options.horizontalCentered = True
    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE

def build_data_tab(wb, name, header, rows, sev_col):
    ws = wb.create_sheet(name)
    ws.append(header)
    for row in rows:
        ws.append(row)
    style_header_row(ws, row=1)
    if rows:
        last_col = get_column_letter(len(header))
        last_row = len(rows) + 1
        table = Table(displayName=name.replace(" ","_"), ref=f"A1:{last_col}{last_row}")
        table.tableStyleInfo = TableStyleInfo(
            name="TableStyleLight15", showFirstColumn=False,
            showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        ws.add_table(table)
    if sev_col is not None:
        add_severity_formatting(ws, sev_col)
    autosize(ws)

def build():
    wb = Workbook()
    build_summary(wb)
    for name, header, rows, sev_col in DATA_TABS:
        build_data_tab(wb, name, header, rows, sev_col)
    wb.save(OUT_PATH)
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    build()
```

---

### Mode C — PDF narrative report (.pdf)

**When to use:** Formal report-style deliverable, print or archive, polished one-time hand-off. Visually distinctive — dark background, amber accents, designed pages.

**Style spec:**
- **Full-bleed dark background** (`#111827`) on every page — no white pages, ever
- **Amber/gold accent** (`#d4a574` or topic-accent) on hero numbers, chart fills, section borders
- **Cover page:** one massive hero stat (72–96pt) in accent color, KPI row underneath, methodology line at bottom
- **Running page header from page 2:** `{title} — {subject} — {date} | Page N`, 8pt muted
- **Page types** (mix as the analysis calls for):
  1. Cover / Hero
  2. Distribution / Positioning (bell curve + comparison cards)
  3. Radar / Profile (multi-axis radar)
  4. Evidence Table (source / weight / range / confidence)
  5. Comparison Grid (side-by-side entities)
  6. Narrative Analysis (1–3 pages of long-form prose)
  7. Trait / Matrix (two-column strength vs. risk)
  8. Methodology
  9. Footer / Disclaimer
- Typography: Helvetica, ALL CAPS section headers with 3px letter spacing, 18–20pt
- Body: 10–11pt, light gray (`#c8ccd4`), line-height 1.5

**Two paths to generate it:**

**Path C1 — HTML to PDF (no install beyond a browser):** generate a self-contained HTML file, then print to PDF. The HTML below uses static `<div>` blocks per page — the assistant populates the `{{PLACEHOLDER}}` tokens from the analysis output and writes the result to a file.

```html
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{{TITLE}} — {{SUBJECT}}</title>
<style>
  @page { size: Letter; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #111827; color: #c8ccd4; font: 11pt/1.5 Helvetica, Arial, sans-serif; }
  .page { width: 8.5in; min-height: 11in; padding: 0.75in 0.85in; background: #111827; page-break-after: always; position: relative; }
  .page:last-child { page-break-after: auto; }
  .page-header { position: absolute; top: 0.5in; left: 0.85in; right: 0.85in; font-size: 8pt; color: #5a6070; display: flex; justify-content: space-between; }
  h1.cover-title { font-size: 32pt; color: #ffffff; font-weight: bold; letter-spacing: 1px; margin-top: 1.2in; }
  .hero-stat { font-size: 96pt; color: #d4a574; font-weight: bold; line-height: 1; margin: 0.4in 0; letter-spacing: -2px; }
  .hero-label { font-size: 11pt; color: #8b92a0; text-transform: uppercase; letter-spacing: 3px; }
  .section-title { font-size: 18pt; color: #ffffff; text-transform: uppercase; letter-spacing: 3px; font-weight: bold; margin: 0.3in 0 0.2in; border-bottom: 1px solid #2a3045; padding-bottom: 0.1in; }
  .kpi-row { display: flex; gap: 0.3in; margin: 0.3in 0; }
  .kpi { flex: 1; background: #1a1f35; padding: 0.2in; border-left: 3px solid #d4a574; }
  .kpi-num { font-size: 28pt; color: #ffffff; font-weight: bold; }
  .kpi-label { font-size: 9pt; color: #8b92a0; text-transform: uppercase; letter-spacing: 2px; margin-top: 0.05in; }
  table { width: 100%; border-collapse: collapse; margin: 0.2in 0; font-size: 10pt; }
  th { text-transform: uppercase; letter-spacing: 2px; font-size: 9pt; color: #8b92a0; text-align: left; padding: 0.1in 0.12in; border-bottom: 1px solid #2a3045; }
  td { padding: 0.1in 0.12in; border-bottom: 1px solid #1e2440; color: #c8ccd4; }
  .sev-critical { color: #e05555; font-weight: bold; }
  .sev-high { color: #d4a574; font-weight: bold; }
  .sev-medium { color: #4cc9ce; font-weight: bold; }
  .sev-low { color: #8b92a0; }
  .sev-positive { color: #4ade80; font-weight: bold; }
  .callout { background: #1e2440; border-left: 3px solid #d4a574; padding: 0.2in; margin: 0.2in 0; font-size: 10pt; }
  .disclaimer { font-size: 7pt; color: #5a6070; margin-top: 0.5in; }
  p { margin: 0.08in 0; }
</style></head>
<body>

<div class="page">
  <div class="hero-label">{{REPORT TYPE}}</div>
  <h1 class="cover-title">{{TITLE}}</h1>
  <div class="hero-label" style="margin-top:0.2in;">{{SUBJECT}}</div>
  <div class="hero-stat">{{HERO NUMBER}}</div>
  <div class="hero-label">{{HERO NUMBER CAPTION — e.g. RISK SCORE / 100}}</div>
  <div class="kpi-row">
    <div class="kpi"><div class="kpi-num">{{KPI1}}</div><div class="kpi-label">{{LABEL1}}</div></div>
    <div class="kpi"><div class="kpi-num">{{KPI2}}</div><div class="kpi-label">{{LABEL2}}</div></div>
    <div class="kpi"><div class="kpi-num">{{KPI3}}</div><div class="kpi-label">{{LABEL3}}</div></div>
    <div class="kpi"><div class="kpi-num">{{KPI4}}</div><div class="kpi-label">{{LABEL4}}</div></div>
  </div>
  <div class="disclaimer" style="position:absolute;bottom:0.75in;left:0.85in;right:0.85in;">
    Generated {{DATE}} · {{AUTHOR}} · Analytical work product — not legal advice. Sources cited in the methodology section.
  </div>
</div>

<div class="page">
  <div class="page-header"><span>{{TITLE}} — {{SUBJECT}}</span><span>{{DATE}} | Page 2</span></div>
  <div class="section-title">Executive Summary</div>
  <p>{{ 3-5 sentence exec summary }}</p>
  <div class="callout">{{ headline finding in one line }}</div>
</div>

<div class="page">
  <div class="page-header"><span>{{TITLE}} — {{SUBJECT}}</span><span>{{DATE}} | Page 3</span></div>
  <div class="section-title">Findings / Scorecard</div>
  <table>
    <tr><th>Domain</th><th>Score</th><th>Weight</th><th>Key driver</th></tr>
    <!-- one <tr> per scorecard row, populated from the analysis -->
  </table>
</div>

<!-- ...additional pages per analysis: narrative, comparison grid, methodology, footer... -->

<div class="page">
  <div class="page-header"><span>{{TITLE}} — {{SUBJECT}}</span><span>{{DATE}} | Page N</span></div>
  <div class="section-title">Methodology &amp; Sources</div>
  <p>{{ how conclusions were reached, what would change them }}</p>
  <p style="margin-top:0.2in;"><strong>Sources:</strong> {{ source list }}</p>
  <p class="disclaimer">{{ disclaimer / limitations / no-legal-advice line }}</p>
</div>

</body></html>
```

Then convert to PDF in any of these ways (any is fine — pick the one that's already installed):

```bash
# macOS / Linux / Windows — Chrome headless
"google-chrome" --headless --disable-gpu --no-margins \
  --print-to-pdf=report.pdf report.html

# wkhtmltopdf (if installed)
wkhtmltopdf --page-size Letter --no-outline --enable-local-file-access \
  report.html report.pdf

# Or: open report.html in any browser → File → Print → Save as PDF (set background graphics ON)
```

**Path C2 — Pure-Python (`reportlab`), no browser needed:**

```python
# pip install reportlab
# Run: python pdf_report.py
import textwrap
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

OUT_PATH = "report.pdf"
TITLE = "{{ ANALYSIS TITLE }}"
SUBJECT = "{{ SUBJECT }}"
DATE = "{{ YYYY-MM-DD }}"
HERO_NUM = "{{ HERO NUMBER e.g. 72 }}"
HERO_CAPTION = "{{ HERO CAPTION e.g. RISK SCORE / 100 }}"

BG = HexColor("#111827"); CARD = HexColor("#1a1f35"); ACCENT = HexColor("#d4a574")
TEXT_WHITE = HexColor("#ffffff"); TEXT_BODY = HexColor("#c8ccd4"); TEXT_MUTED = HexColor("#8b92a0")

def draw_bg(c):
    c.setFillColor(BG); c.rect(0, 0, LETTER[0], LETTER[1], fill=1, stroke=0)

def draw_page_header(c, page_num):
    c.setFillColor(TEXT_MUTED); c.setFont("Helvetica", 8)
    c.drawString(0.85*inch, LETTER[1]-0.5*inch, f"{TITLE} — {SUBJECT}")
    c.drawRightString(LETTER[0]-0.85*inch, LETTER[1]-0.5*inch, f"{DATE} | Page {page_num}")

def cover(c):
    draw_bg(c)
    c.setFillColor(TEXT_MUTED); c.setFont("Helvetica", 11)
    c.drawString(0.85*inch, LETTER[1]-1.2*inch, "ANALYTICAL REPORT")
    c.setFillColor(TEXT_WHITE); c.setFont("Helvetica-Bold", 32)
    c.drawString(0.85*inch, LETTER[1]-1.8*inch, TITLE)
    c.setFillColor(TEXT_MUTED); c.setFont("Helvetica", 12)
    c.drawString(0.85*inch, LETTER[1]-2.1*inch, SUBJECT)
    c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 96)
    c.drawString(0.85*inch, LETTER[1]-4.2*inch, str(HERO_NUM))
    c.setFillColor(TEXT_MUTED); c.setFont("Helvetica", 11)
    c.drawString(0.85*inch, LETTER[1]-4.5*inch, HERO_CAPTION)
    c.setFillColor(TEXT_MUTED); c.setFont("Helvetica", 8)
    c.drawString(0.85*inch, 0.75*inch, f"Generated {DATE} — Analytical work product, not legal advice.")
    c.showPage()

def section_page(c, page_num, title, paragraphs):
    draw_bg(c); draw_page_header(c, page_num)
    c.setFillColor(TEXT_WHITE); c.setFont("Helvetica-Bold", 18)
    c.drawString(0.85*inch, LETTER[1]-1.4*inch, title.upper())
    c.setStrokeColor(HexColor("#2a3045")); c.setLineWidth(0.5)
    c.line(0.85*inch, LETTER[1]-1.5*inch, LETTER[0]-0.85*inch, LETTER[1]-1.5*inch)
    c.setFillColor(TEXT_BODY); c.setFont("Helvetica", 11)
    y = LETTER[1]-1.9*inch
    for para in paragraphs:
        for line in (textwrap.wrap(para, width=92) or [""]):
            c.drawString(0.85*inch, y, line); y -= 14
        y -= 8
    c.showPage()

def build():
    c = canvas.Canvas(OUT_PATH, pagesize=LETTER)
    cover(c)
    section_page(c, 2, "Executive Summary", ["{{ 3-5 sentence exec summary }}"])
    section_page(c, 3, "Findings", ["{{ first finding paragraph }}", "{{ second finding paragraph }}"])
    section_page(c, 4, "Methodology & Sources", ["{{ how conclusions were reached }}", "Sources: {{ list }}"])
    c.save()
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    build()
```

---

### Mode D — Interactive HTML dashboard (.html)

**When to use:** Browseable multi-section deep view, drill-down, the user wants to share a link or open in a browser. Best when the analysis has multiple sections worth navigating, KPIs worth surfacing, and any quantitative data worth charting.

**Style spec:**
- **Single self-contained `.html` file** — the user opens it directly with a browser, no server needed
- **Dark mode default, light mode toggle** (button in top-right)
- **Hero section** at top: title, subtitle, 4–6 KPI chips with values + labels + deltas
- **Sticky navigation bar** with scroll-to-section anchors, accent-colored active state
- **Section cards** with glassmorphism (backdrop blur, subtle border, hover lift)
- **Color-coded severity** (CRITICAL red, HIGH amber, MEDIUM cyan, LOW muted, POSITIVE green)
- **Chart.js** for any quantitative data (loaded from CDN — `cdn.jsdelivr.net/npm/chart.js`)
- **Responsive** at 1200 / 900 / 600px breakpoints
- **Footer** with generation metadata, sources, confidence rating
- Inline `<style>` and `<script>` — no external CSS/JS files
- Data embedded as `const DATA = { ... }` near the top of the `<script>` — assistant fills this with the analysis output
- **DOM is built with `createElement` + `textContent`** rather than `innerHTML` so the template is safe to use even when content includes user-supplied strings; structural HTML markup is written declaratively in the body, content is injected as text nodes

**Self-contained template:**

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{{TITLE}} — {{SUBJECT}}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root, [data-theme="dark"] {
  --bg: #0a0a0f; --bg2: #111118; --bg3: #1a1a24; --bg4: #22222e;
  --text: #f5f5f7; --text2: #a1a1a6; --text3: #6e6e73;
  --accent: #0a84ff;
  --critical: #ef4444; --high: #f59e0b; --medium: #22d3ee; --low: #6e6e73;
  --positive: #30d158;
  --card: rgba(28,28,35,.7); --glass: rgba(255,255,255,.04);
  --border: rgba(255,255,255,.08); --radius: 16px;
  --font: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
}
[data-theme="light"] {
  --bg: #faf8f6; --bg2: #ffffff; --bg3: #f0ecea; --bg4: #e5e0dc;
  --text: #1d1d1f; --text2: #6e6e73; --text3: #a1a1a6;
  --card: rgba(255,255,255,.85); --glass: rgba(0,0,0,.03);
  --border: rgba(0,0,0,.08);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: var(--font); font-size: 14px; line-height: 1.55; min-height: 100vh;
  background-image:
    radial-gradient(circle at 15% 20%, rgba(10,132,255,0.10), transparent 40%),
    radial-gradient(circle at 85% 80%, rgba(191,90,242,0.08), transparent 40%);
  background-attachment: fixed;
}
.container { max-width: 1400px; margin: 0 auto; padding: 24px; }
header.hero { padding: 56px 0 28px; }
.hero-eyebrow { color: var(--accent); text-transform: uppercase; letter-spacing: 3px; font-size: 11px; font-weight: 600; margin-bottom: 12px; }
h1.hero-title { font-size: 40px; line-height: 1.1; font-weight: 700; letter-spacing: -1px; }
.hero-sub { color: var(--text2); margin-top: 8px; font-size: 16px; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-top: 28px; }
.kpi { background: var(--card); backdrop-filter: blur(20px); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 20px; transition: transform .15s ease; }
.kpi:hover { transform: translateY(-2px); }
.kpi-label { color: var(--text2); font-size: 11px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }
.kpi-value { font-size: 28px; font-weight: 700; margin-top: 6px; color: var(--text); }
.kpi-delta { font-size: 11px; color: var(--text3); margin-top: 4px; }
nav.sticky { position: sticky; top: 0; z-index: 10; background: rgba(10,10,15,.85); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); padding: 12px 0; margin: 16px -24px 24px; }
nav.sticky .container { display: flex; gap: 6px; flex-wrap: wrap; padding: 0 24px; }
nav.sticky a { color: var(--text2); padding: 6px 12px; border-radius: 8px; text-decoration: none; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; }
nav.sticky a:hover, nav.sticky a.active { background: var(--accent); color: #fff; }
section.card { background: var(--card); backdrop-filter: blur(20px); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px; margin-bottom: 20px; border-left: 3px solid var(--accent); }
section.card h2 { font-size: 18px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 16px; color: var(--text); }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { text-align: left; text-transform: uppercase; letter-spacing: 1.5px; font-size: 10px; color: var(--text2); font-weight: 600; padding: 10px 12px; border-bottom: 1px solid var(--border); }
td { padding: 10px 12px; border-bottom: 1px solid var(--border); color: var(--text); }
tr:hover { background: var(--glass); }
.badge { display: inline-block; padding: 3px 9px; border-radius: 6px; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }
.badge.critical { background: rgba(239,68,68,.15); color: var(--critical); }
.badge.high     { background: rgba(245,158,11,.15); color: var(--high); }
.badge.medium   { background: rgba(34,211,238,.15); color: var(--medium); }
.badge.low      { background: rgba(110,110,115,.15); color: var(--low); }
.badge.positive { background: rgba(48,209,88,.15); color: var(--positive); }
.finding { padding: 14px 16px; margin: 10px 0; background: var(--glass); border-radius: 10px; border-left: 3px solid var(--text3); }
.finding.critical { border-left-color: var(--critical); }
.finding.high     { border-left-color: var(--high); }
.finding.medium   { border-left-color: var(--medium); }
.finding.positive { border-left-color: var(--positive); }
.finding-title { font-weight: 600; margin-bottom: 4px; display: flex; gap: 10px; align-items: center; }
.finding-body { color: var(--text2); }
.finding-source { color: var(--text3); font-size: 11px; margin-top: 4px; }
.theme-toggle { position: fixed; top: 18px; right: 18px; z-index: 20; background: var(--card); border: 1px solid var(--border); color: var(--text); border-radius: 50%; width: 36px; height: 36px; cursor: pointer; backdrop-filter: blur(20px); }
canvas { max-width: 100%; }
footer { margin-top: 40px; padding: 24px 0; border-top: 1px solid var(--border); color: var(--text3); font-size: 12px; text-align: center; }
ul { padding-left: 20px; color: var(--text2); }
li { margin: 4px 0; }
@media (max-width: 900px) { h1.hero-title { font-size: 30px; } .kpi-value { font-size: 22px; } }
@media (max-width: 600px) { .container { padding: 16px; } section.card { padding: 18px; } }
@media print { body { background: var(--bg); } nav.sticky, .theme-toggle { display: none; } }
</style>
</head>
<body>

<button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">◐</button>

<div class="container">

  <header class="hero" id="sec-hero">
    <div class="hero-eyebrow" id="hero-eyebrow"></div>
    <h1 class="hero-title" id="hero-title"></h1>
    <div class="hero-sub" id="hero-sub"></div>
    <div class="kpi-grid" id="kpi-grid"></div>
  </header>

  <nav class="sticky">
    <div class="container" id="nav-bar"></div>
  </nav>

  <section class="card" id="sec-summary">
    <h2>Executive Summary</h2>
    <p id="exec-summary"></p>
  </section>

  <section class="card" id="sec-scorecard">
    <h2>Scorecard</h2>
    <div id="scorecard"></div>
  </section>

  <section class="card" id="sec-findings">
    <h2>Findings</h2>
    <div id="findings"></div>
  </section>

  <section class="card" id="sec-chart">
    <h2>Visualization</h2>
    <canvas id="main-chart" height="280"></canvas>
  </section>

  <section class="card" id="sec-gaps">
    <h2>Information Gaps</h2>
    <div id="gaps"></div>
  </section>

  <section class="card" id="sec-disposition">
    <h2>Recommended Disposition</h2>
    <p id="disposition"></p>
  </section>

  <footer id="footer"></footer>

</div>

<script>
// ---- Customize per analysis (assistant fills this from the analysis output) ----
const DATA = {
  reportType: "{{REPORT TYPE}}",
  title: "{{TITLE}}",
  subject: "{{SUBJECT}}",
  date: "{{YYYY-MM-DD}}",
  basis: "{{e.g. OSINT + provided material}}",
  author: "{{AUTHOR}}",
  confidence: "{{HIGH/MODERATE/LOW}}",
  accent: "#0a84ff",

  kpis: [
    { label: "Composite", value: "{{n}}/100", delta: "{{tier}}" },
    { label: "Confidence", value: "{{HIGH/MOD/LOW}}", delta: "" },
    { label: "Red Flags", value: "{{n}}", delta: "" },
    { label: "Information Gaps", value: "{{n}}", delta: "" }
  ],

  navSections: [
    { id: "sec-summary",     label: "Summary" },
    { id: "sec-scorecard",   label: "Scorecard" },
    { id: "sec-findings",    label: "Findings" },
    { id: "sec-chart",       label: "Chart" },
    { id: "sec-gaps",        label: "Gaps" },
    { id: "sec-disposition", label: "Disposition" }
  ],

  execSummary: "{{ 3-5 sentence exec summary }}",

  scorecard: {
    headers: ["Domain", "Score", "Weight", "Weighted", "Key driver"],
    rows: [
      // ["Domain A", 45, "20%", 9, "..."], ...
    ]
  },

  findings: [
    // { severity: "CRITICAL", title: "...", body: "...", source: "..." }, ...
  ],

  chartConfig: {
    type: "bar",
    data: {
      labels: [],
      datasets: [{ label: "Score", data: [], backgroundColor: "rgba(10,132,255,0.6)" }]
    }
  },

  gaps: [],
  disposition: "{{ disposition + reasoning }}"
};
// --------------------------------------------------------------------------------

document.documentElement.style.setProperty('--accent', DATA.accent);

function el(tag, opts) {
  opts = opts || {};
  const e = document.createElement(tag);
  if (opts.className) e.className = opts.className;
  if (opts.text != null) e.textContent = opts.text;
  if (opts.attrs) for (const k in opts.attrs) e.setAttribute(k, opts.attrs[k]);
  if (opts.children) opts.children.forEach(c => c && e.appendChild(c));
  return e;
}

function renderHero() {
  document.getElementById("hero-eyebrow").textContent = DATA.reportType;
  document.getElementById("hero-title").textContent = DATA.title;
  document.getElementById("hero-sub").textContent =
    [DATA.subject, DATA.date, DATA.basis].filter(Boolean).join(" · ");
}

function renderKPIs() {
  const root = document.getElementById("kpi-grid");
  DATA.kpis.forEach(k => {
    const card = el("div", { className: "kpi", children: [
      el("div", { className: "kpi-label", text: k.label }),
      el("div", { className: "kpi-value", text: k.value }),
      el("div", { className: "kpi-delta", text: k.delta || "" })
    ]});
    root.appendChild(card);
  });
}

function renderNav() {
  const root = document.getElementById("nav-bar");
  DATA.navSections.forEach(s => {
    const a = el("a", { text: s.label, attrs: { href: "#" + s.id } });
    root.appendChild(a);
  });
}

function renderExec() {
  document.getElementById("exec-summary").textContent = DATA.execSummary;
}

function renderScorecard() {
  const root = document.getElementById("scorecard");
  const table = el("table");
  const thead = el("thead");
  const headRow = el("tr", { children: DATA.scorecard.headers.map(h => el("th", { text: h })) });
  thead.appendChild(headRow); table.appendChild(thead);
  const tbody = el("tbody");
  DATA.scorecard.rows.forEach(r => {
    tbody.appendChild(el("tr", { children: r.map(c => el("td", { text: String(c) })) }));
  });
  table.appendChild(tbody);
  root.appendChild(table);
}

function renderFindings() {
  const root = document.getElementById("findings");
  DATA.findings.forEach(f => {
    const sev = (f.severity || "low").toLowerCase();
    const titleRow = el("div", { className: "finding-title", children: [
      el("span", { className: "badge " + sev, text: f.severity || "LOW" }),
      el("span", { text: f.title || "" })
    ]});
    const body = el("div", { className: "finding-body", text: f.body || "" });
    const src = el("div", { className: "finding-source", text: f.source || "" });
    root.appendChild(el("div", { className: "finding " + sev, children: [titleRow, body, src] }));
  });
}

function renderChart() {
  const ctx = document.getElementById("main-chart").getContext("2d");
  const bodyStyle = getComputedStyle(document.body);
  Chart.defaults.color = bodyStyle.getPropertyValue("--text2");
  Chart.defaults.borderColor = "rgba(255,255,255,0.06)";
  new Chart(ctx, {
    type: DATA.chartConfig.type,
    data: DATA.chartConfig.data,
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: bodyStyle.getPropertyValue("--text") } } }
    }
  });
}

function renderGaps() {
  const root = document.getElementById("gaps");
  if (!DATA.gaps || DATA.gaps.length === 0) {
    root.appendChild(el("p", { text: "No material information gaps identified." }));
    return;
  }
  const list = el("ul", { children: DATA.gaps.map(g => el("li", { text: g })) });
  root.appendChild(list);
}

function renderDisposition() {
  document.getElementById("disposition").textContent = DATA.disposition;
}

function renderFooter() {
  document.getElementById("footer").textContent =
    `Generated ${DATA.date} · ${DATA.author} · Confidence: ${DATA.confidence} · ` +
    `Basis: ${DATA.basis} · Analytical work product — not legal advice.`;
}

function watchScroll() {
  const links = document.querySelectorAll("nav.sticky a");
  const observer = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        links.forEach(l => l.classList.toggle("active", l.getAttribute("href") === "#" + en.target.id));
      }
    });
  }, { threshold: 0.4 });
  document.querySelectorAll("section.card, header.hero").forEach(s => observer.observe(s));
}

document.getElementById("themeToggle").addEventListener("click", () => {
  const cur = document.documentElement.dataset.theme;
  document.documentElement.dataset.theme = (cur === "dark" ? "light" : "dark");
});

renderHero(); renderKPIs(); renderNav(); renderExec();
renderScorecard(); renderFindings(); renderChart();
renderGaps(); renderDisposition(); renderFooter(); watchScroll();
</script>
</body></html>
```

---

### Common rules for all four modes

- **No fabrication in artifact form.** The renderer surfaces what's in the analysis above — it does not add findings, scores, or sources that the analysis did not produce. If the analysis says "no adverse findings", the deliverable says it too, prominently and unhedged.
- **Severity tags are preserved exactly.** If the analysis uses CRITICAL / HIGH / MEDIUM / LOW, the deliverable uses the same words and the matching color from the palette. Do not re-tag, re-rank, or re-score during rendering.
- **Sources travel with claims.** Every cited claim in the analysis carries its source in the deliverable too — as a footnote (Word, PDF), a column (Excel), or a `.finding-source` line (HTML).
- **Confidence rating goes in the footer of every artifact.** The user needs to see the confidence on the artifact itself, not just in chat.
- **"Generated {date}, basis: {OSINT / provided material / training-data}"** in the footer of every artifact. The reader of a hand-off needs to know how the analysis was sourced.
- **One artifact, one file.** Do not split the deliverable into multiple files unless the user explicitly asks. Excel can use multiple tabs in one workbook; HTML is one self-contained `.html`; PDF is one file; Word is one `.docx`.
- **No emojis in the artifact** unless the user explicitly asks. The repo's quality bar is bank-grade; emojis read as informal and undercut that.

---

*GENERATED FILE — do not hand-edit. Sources: [`methodology/`](methodology/)
(`audit-defensible-writing.md`, `analytical-patterns.md`,
`output-quality-standards.md`, and the renderer block of
`report-templates.md`). Rebuild: `python3 _tooling/build_base.py` from the
repo root. CI fails if this file drifts from its sources.*
