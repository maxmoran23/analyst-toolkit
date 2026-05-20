# Output Quality Standards

Quality bars per output type. When you generate any deliverable below, the bar
described is the **floor** — not the ceiling. Anything under the floor is not
done; it is a draft.

This is a companion to [`audit-defensible-writing.md`](audit-defensible-writing.md)
(the writing voice) and [`analytical-patterns.md`](analytical-patterns.md)
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
   [`audit-defensible-writing.md`](audit-defensible-writing.md)).
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
