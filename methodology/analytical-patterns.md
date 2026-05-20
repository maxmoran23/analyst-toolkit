# Analytical Patterns

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
