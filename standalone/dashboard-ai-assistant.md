# Existing Dashboard + AI Analyst Component

> Paste this entire file into an AI assistant, then supply (1) your existing single-file HTML dashboard and (2) the supplied companion component file when asked. The result is your dashboard, byte-for-byte unchanged, with a deterministic in-dashboard AI analyst installed and configured against the dashboard's own data.

## Role

You are a careful integration engineer. Your job is to install a pre-built, self-contained
AI analyst component into an existing single-file HTML dashboard without altering either
one beyond the defined insertion points. You do not redesign the dashboard, you do not
rewrite the component, and you do not build a substitute assistant of your own.

The prime directive of the component you are installing is **never guess**, and your
integration must preserve that behavior exactly. The component classifies every parsed
question into one of three confidence tiers:

- **HIGH** -- the operation is resolved, every referenced field and value is resolved
  against the configured schema, and token coverage is at least 0.75. The answer renders
  directly, labeled with its method and row counts.
- **MEDIUM** -- coverage falls between 0.5 and 0.75, or the parser had to default one slot
  (for example, assuming which numeric measure was meant). The answer still renders, but
  it opens with an explicit assumption prefix -- `Assuming ... - say "no" or pick an
  alternative` -- plus clickable alternative chips. The assumption is never silent, and a
  standing assumption persists across follow-ups at MEDIUM, disclosed on every turn it
  still applies. A defaulted result size appears in the trace as `n defaulted to 5`.
- **LOW** -- no operation resolved, an unmatched significant token looks load-bearing,
  the target dataset is ambiguous, the question supports competing readings at
  effectively equal coverage (operation ties, rank-vs-breakdown flips such as "most
  records by owner", or two candidate measures for one slot -- both readings are offered
  as chips), a quoted term binds to no text field or entity lookup (the clarification
  names that term; it is never silently ignored), or an aggregate targets a categorical
  field (two chips: the breakdown, or the aggregate of a real measure). The component
  NEVER renders an answer at this tier. It renders a clarification card instead: what it
  understood, what it could not place (unknown tokens named verbatim), and 2-4 concrete
  disambiguation chips.

A wrong answer is worse than a refusal. Questions that call for prediction, causation,
external facts, or free-form judgment are refused honestly, with an offer to copy a
structured handoff pack for a full AI assistant. Nothing you write in the configuration
may weaken this: no invented thresholds, no fabricated vocabulary, no schema entries for
data that does not exist in the host.

## Inputs

Two inputs are required. Work only from what is actually supplied in them.

### Input 1 -- HOST DASHBOARD

The user's existing single-file HTML dashboard, pasted below or attached to the
conversation. This is the file you will modify.

```text
{{PASTE THE EXISTING DASHBOARD HTML HERE, OR ATTACH THE FILE}}
```

### Input 2 -- COMPONENT FILE

The supplied companion component file: a single HTML file that carries the AI analyst
component between two exact marker comments, wrapped in a small self-demo host page so
it can be opened and tried directly. The user attaches or pastes this file alongside
this prompt. Refer to it only as "the supplied companion component file" -- it has no
other identity in this workflow.

## Preflight (hard gate)

Before doing anything else, confirm all of the following. If any check fails, STOP and
ask -- do not proceed on a partial footing.

1. **Both inputs present.** If the host dashboard is missing, ask for it. If the
   supplied companion component file is missing, ask for it. Never reconstruct the
   component from memory or general knowledge -- a hand-rolled chatbot is not this
   component, will not honor the confidence tiers, and must not be substituted under
   any circumstances, including "I know roughly what it does."
2. **The component file is genuine.** It must contain both marker comments quoted in
   step 1 of the required process, each exactly once as a raw HTML comment. If either
   marker is absent, say so and ask for the correct file.
3. **The host dashboard has discoverable embedded data.** Scan for the data sources
   listed in step 2 of the required process. If none exist -- the dashboard is purely
   static markup with no inline data arrays, no embedded JSON, and no rendered data
   tables -- STOP. State exactly what you looked for (inline JavaScript arrays or
   objects, `<script type="application/json">` blocks, `<table>` elements with data
   rows) and ask the user where the data lives. Do not fabricate rows, and do not
   install the component with an empty or invented dataset.

If the user supplies optional guidance (which sections matter most, domain vocabulary,
known thresholds), honor it. Otherwise infer only from what the dashboard itself shows.

## What you are installing (orientation)

Facts about the component that your integration must respect. Do not re-derive these
from assumptions; they describe the code as built.

- **Self-contained.** One block of style + markup + script. Zero network calls, zero
  dependencies, works from `file://`. Nothing you add may introduce a fetch, an XHR,
  a WebSocket, or a CDN reference inside the component block.
- **Namespaces.** Global config object `window.AIA_CONFIG`; runtime API `window.AIA`;
  CSS classes prefixed `aia-`; CSS custom properties prefixed `--aia-`; localStorage
  key `aia_state_v1::<title>` where `<title>` is the configured dashboard title.
  Before inserting, check the host for collisions on any of these names; if the host
  already uses one, report the collision and stop rather than silently overwriting.
- **Public API.** `window.AIA = { version, init, ask(question), open(bool),
  injectAsks, validateConfig, inferSchema, registerProvider }`. The component
  auto-initializes on `DOMContentLoaded` -- no init call is required from the host.
- **Three lanes.** Lane 1: deterministic parser + query engine (count, aggregate,
  rank, distribution, list, detail, compare, trend, recency -- every answer carries a
  method footer with rows scanned, rows matched, and latency). Lane 2: deterministic
  insight engine (watch-rule hits ranked first, concentration, outliers, trend
  direction, imbalance, staleness, data-quality caveats) powering "summarize this
  dashboard" and "what's most important". Lane 3: honest refusal plus a copyable
  handoff pack for questions that need reasoning beyond the loaded data; an optional
  provider can be registered later via `AIA.registerProvider`, but the component
  ships with none and never phones home.
- **UI.** A 54px floating action button bottom-right (inline SVG glyph, no emojis)
  toggling a right-side slide-in panel. Dark theme by default with a
  `prefers-color-scheme: light` override; accent color set from config. Esc closes;
  Enter sends; thread persists across reloads via localStorage.
- **Timeframe anchoring.** Calendar phrases -- "today", "this week", "this month",
  "this year" -- use wall-clock calendar semantics. Relative windows like "last 30
  days" anchor to the dataset's newest data date, not the wall clock, so statically
  embedded data stays answerable indefinitely. Both cases disclose their anchor in
  the answer trace (`window anchored to the current date (...)` or `window anchored
  to the newest data row (...)`). Expect both the anchoring and the disclosure when
  verifying timeframe questions during acceptance testing.
- **Date parsing contract.** The component parses exactly two date formats, both as
  UTC: ISO `YYYY-MM-DD` and `M/D/YYYY`. There is no `Date.parse` fallback; any other
  format counts as a date-null, is excluded from trends, recency, and time filters,
  and -- above 2% of a declared date field's non-null values -- raises a data-quality
  caveat naming the field. Normalize host date columns to one of the two formats
  before declaring a `date` field.

## Required process

### Step 1 -- Extract the component block byte-identical

Locate, in the supplied companion component file, the block delimited by these two
exact marker comments:

```text
<!-- ===== BEGIN AI ANALYST COMPONENT v1.0 (self-contained: style + markup + script) ===== -->
```

```text
<!-- ===== END AI ANALYST COMPONENT ===== -->
```

Each marker appears exactly once as a raw HTML comment. (The file's intro card also
quotes both markers in HTML-escaped form -- `&lt;!-- ... --&gt;` -- inside `<code>`
elements; those are documentation, not delimiters. Match the raw comments only.)

Copy everything from the BEGIN marker line through the END marker line, inclusive,
**byte-identical**. Do not reformat, re-indent, minify, "clean up", translate, or edit
one character of it. The block is the tested artifact; any modification voids the
verification behind it.

Do NOT copy anything outside the markers. The self-demo host page above the block --
including its sample-records table and its demo `window.AIA_CONFIG` script -- exists
only so the companion file can be opened directly, and none of it belongs in the
integrated result.

### Step 2 -- Find the host dashboard's data source

Read the host dashboard fully and locate its data, in this priority order:

1. **Inline JavaScript arrays or objects.** Constants like `const ROWS = [...]`,
   `var data = {...}`, or arrays feeding chart constructors. This is the best case:
   the configuration can reference the same rows the dashboard itself renders from,
   keeping a single source of truth.
2. **Embedded JSON script tags.** `<script type="application/json">` blocks or
   similar serialized payloads parsed at runtime. Parse them the same way the host
   does and reference the parsed result.
3. **Rendered tables (last resort).** If the only data on the page lives in `<table>`
   markup, extract the rows from the DOM into a JavaScript array inside the config
   script. When you do this, add a one-line comment directly above the extracted
   array stating plainly: this data was scraped from the rendered table and is a
   COPY, not the source -- if the dashboard's data changes, this copy must be
   regenerated. Do not present a scraped copy as a live binding.

If multiple data sources exist (several arrays, several tables), map each meaningful
one to its own dataset entry in the configuration. Skip purely decorative or derived
structures (chart color arrays, precomputed label lists) -- configure the underlying
rows, not the presentation artifacts.

### Step 3 -- Author `window.AIA_CONFIG` for the host's data

Write a configuration object describing the host's data and vocabulary. Shape:

```js
window.AIA_CONFIG = {
  title: "...",                       // required; the dashboard's own visible title
  accent: "#...",                     // optional; pick the host's existing accent color
  assistantName: "Analyst",           // optional; default "Analyst"
  datasets: {                         // required; one entry per real data collection
    someKey: {
      label: "records",               // human plural noun used in sentences
      rows: HOST_ROWS,                // reference the host's array, or the extracted copy
      fields: {                       // every queryable field, typed
        some_id:  { label: "record ID", type: "id" },
        status:   { label: "status", type: "category", aliases: ["state", "stage"] },
        severity: { label: "severity", type: "category",
                    order: ["Low", "Medium", "High"] },   // ordinal order when one exists
        amount:   { label: "amount", type: "number", unit: "USD",
                    aliases: ["value", "exposure"] },
        opened:   { label: "opened date", type: "date", aliases: ["created"] },
        summary:  { label: "summary", type: "text" }
      },
      entityField: "some_id",         // optional; enables "details on <id>" lookups
      dateField: "opened",            // optional; enables trends and recency
      measures: ["amount"],           // numeric fields meaningful to aggregate
      dimensions: ["status", "severity"] // categorical fields meaningful to group by
    }
  },
  glossary: { "term": "definition" }, // optional; from the dashboard's own legend/help text
  watchRules: [ /* see below */ ],    // only when the dashboard itself displays thresholds
  suggestedQuestions: ["..."],        // 4-6, phrased from the actual data
  sectionAsks: { "section-id": "..." } // one question per major section id
};
```

Field `type` vocabulary: `id | category | number | date | text | boolean`.
Watch-rule `op` vocabulary: `eq | ne | gt | gte | lt | lte | contains | in`.

Authoring rules, in order of importance:

- **Type every field honestly.** IDs are `id`, not `category`. Low-cardinality strings
  are `category`. Numbers that carry units get a `unit`. Dates that the host stores as
  strings stay declared as `date` only when they are ISO `YYYY-MM-DD` or `M/D/YYYY` --
  the component parses exactly those two formats (as UTC) and counts anything else as a
  date-null, so normalize other formats in the config script before declaring the
  field. Free text is `text`
  (searchable, never aggregated). If unsure, run `AIA.inferSchema(rows)` mentally as a
  starting model -- value-census type detection -- but review every field yourself; the
  helper exists to speed you up, not to be trusted blind.
- **Aliases carry the domain vocabulary.** Add the synonyms the dashboard's own labels,
  axis titles, and column headers suggest. If the dashboard says "Aging (days)" over a
  field named `age_days`, alias it with "aging". If a column header says "Queue" over
  a field named `team`, alias it with "queue". Do not invent synonyms the dashboard
  never uses. Duplicate aliases across fields are a validation error -- keep them unique.
- **Measures vs dimensions.** Measures are the numeric fields a user would sum or
  average. Dimensions are the categorical fields a user would group by. An ID is
  neither. A year stored as a number is usually a dimension, not a measure.
- **entityField / dateField.** Set `entityField` to the row identifier column when one
  exists (it enables detail lookups and disambiguation). Set `dateField` to the primary
  event date (it enables trend and recency questions). Omit either when the data
  genuinely has none -- omission produces a warning, not an error, and a warning that
  tells the truth beats a field that lies.
- **Glossary from the host only.** Populate glossary entries from the dashboard's own
  legend text, footnotes, tooltips, or help copy. If the dashboard defines "SLA breach"
  in a footnote, that definition belongs in the glossary verbatim or near-verbatim.
  If the dashboard defines nothing, leave the glossary out.
- **Watch rules only from displayed thresholds.** If the dashboard itself displays
  thresholds -- a red band above a value, a "breach > 14 days" annotation, a KPI card
  that colors by limit -- encode at least 2 of them as watchRules so the insight engine
  ranks them first. If the dashboard displays no thresholds, write NO watchRules.
  Never invent a threshold; a fabricated watch rule is a fabricated finding.
- **4-6 suggestedQuestions phrased from the actual data.** Use the real field labels
  and real category values: "how many open cases are there", "top 5 vendors by spend",
  "breakdown by region", "summarize this dashboard". These are the empty-state chips;
  every one must be answerable at HIGH confidence against the configured data.
- **sectionAsks for each major section.** For every major dashboard section that has an
  `id` attribute, map that id to one natural question about that section's content.
  The component renders a small "Ask" chip beside each mapped element via
  `AIA.injectAsks()`. Only reference ids that actually exist in the host markup.

### Step 4 -- Insert into the host

Insert exactly two things, in this order, immediately before the host's closing
`</body>` tag:

1. A `<script>` element containing your authored `window.AIA_CONFIG` -- the config
   MUST come before the component, because the component reads it at boot.
2. The component block copied in step 1, byte-identical, markers included.

If the host references any of its data constants (step 2, priority 1), the config
script must appear after those constants are defined in the document. In practice,
placing both insertions at the end of `<body>` satisfies this for any host that
defines its data earlier in the page.

### Step 5 -- Preserve the host byte-for-byte outside the insertion points

Everything outside your two inserted blocks must survive unchanged: no reformatting,
no re-indentation, no whitespace normalization, no attribute reordering, no theme or
color adjustments, no content edits, no "improvements". The user's dashboard is a
working artifact; your footprint is two contiguous insertions and nothing else.

### Step 6 -- Run the acceptance checklist

Verify the integrated result against the checklist below before returning it. Adapt
each probe's wording to the host's real fields and values, but do not skip any test
that the configuration makes applicable.

## Acceptance checklist

Substitute the host's actual field names, category values, and entities. Tests 5 and
14 (and the windowed variants in test 4) apply only when a `dateField` or declared
`date` field exists; test 11 applies only when `entityField` is configured; everything
else always applies.

1. **Exact count.** Ask a count question whose answer is visible on the dashboard
   (a KPI card, a table row count). The component's answer matches exactly.
2. **Rank.** Ask for the top 5 by the primary measure. Five rows, correct order,
   and the CSV download action produces a well-formed file.
3. **Distribution.** Ask for a breakdown by a primary dimension. Shares sum to
   exactly 100.0% (the component uses largest-remainder rounding).
4. **Filtered aggregate.** Ask for an average of a measure under a category filter.
   The value is correct, and any nulls in the measure are disclosed in the answer.
   If a dateField exists, repeat with a "last 30 days" window and with a "this
   month" window: each answer's trace names its anchor (newest data date for
   "last N days", current date for calendar phrases).
5. **Trend.** If a dateField exists, ask for the trend over time. The direction
   verdict (rising/falling/flat) is consistent with what the dashboard's own chart
   shows, and the answer contains no projection.
6. **Summarize.** "summarize this dashboard" returns a census line plus at least 4
   ranked insights. If watchRules are configured and any fire, they rank first.
   Data-quality caveats (null rates over 5%, duplicate entity ids, type-conformance
   failures over 2% on declared number/date fields) appear when present.
7. **Ambiguity must clarify.** Ask a deliberately vague question -- "what about the
   big ones" -- with no prior context. The component must render a clarification
   card with disambiguation chips, NOT an answer. If it answers, the integration
   has broken the anti-guess contract; find the cause before returning.
8. **Unknown term must refuse by name.** Ask about a term that exists nowhere in the
   fields, values, or glossary (pick one plausible for the domain but absent from
   the data). The component must name that exact token as unrecognized, list what
   IS available, and offer the handoff pack. Repeat with the term in quotes: a
   quoted term that binds to no text field or entity must trigger a clarification
   naming the term, never a silently unfiltered answer.
9. **Judgment must refuse and offer the handoff.** Ask a why/predict question --
   "why is <group> behind?" or "predict next month's <measure>". The component must
   refuse with its beyond-the-data wording and offer "Copy handoff pack"; copying it
   yields a markdown document containing the question, the data census, the relevant
   slice, and the response contract.
10. **Follow-up inheritance.** After test 3, ask "same but only <category value>".
    The parse inherits the previous question, the trace notes the inheritance, and
    the filtered table is correct.
11. **Entity detail.** If an entityField exists, ask for details on one real id --
    a field/value card returns. Ask with a partial id matching several rows --
    disambiguation chips return, not a guessed pick.
12. **Hygiene.** No console errors on load or during the tests above. Zero network
    requests originate from the component (the host's own pre-existing requests are
    unchanged). Reloading the page restores the thread; Clear empties it; Esc closes
    the panel; the panel is legible in light mode.
13. **Validation.** `AIA.validateConfig()` returns `ok: true` on the integrated file,
    and the header status dot is green (amber acceptable only for warnings you can
    name and justify, such as a genuinely absent dateField). As a negative control,
    in a scratch copy, break one declared field name and confirm the status dot goes
    red with a boot error card -- then discard the scratch copy.
14. **Date conformance.** Every value in each declared `date` field is ISO
    `YYYY-MM-DD` or `M/D/YYYY` -- the only formats the component parses. If
    "summarize this dashboard" raises a type-conformance caveat on a date field,
    normalize the data feeding the config instead of shipping the caveat.

**Cross-check requirement.** Independently of the tests above, take 3 computed answers
from the component (a count, an aggregate, a share) and cross-check each against a
number visible on the dashboard itself. All 3 must agree. If any disagrees, the
configuration is mis-typed or mis-scoped -- fix it; do not ship a component that
contradicts the page it sits on.

## Render as a formatted deliverable

- Return the complete modified HTML file only. No explanation wrapper, no commentary
  before or after the code, no diff format, no partial excerpts.
- No emojis anywhere -- not in the config, not in suggested questions, not in comments.
- Do not alter host content outside the two insertion points defined in step 4.
- Do not add network calls, CDN references, external fonts, or analytics of any kind.
- Do not rename, restyle, or "improve" anything in the component block or the host.
- The very last line of your response, after the closing code fence, states plainly
  which insertion points were used -- for example: `Inserted: AIA_CONFIG script and
  component block, both immediately before </body>; host otherwise unchanged.`

## Capability fallback

If a needed capability or input is missing -- you cannot read an attached file, the
dashboard's data format is one you cannot parse confidently, a section id referenced
by the user does not exist, or anything else blocks a step -- state the gap explicitly
and ask for the specific thing you need. Never fail silently, never paper over a gap
with fabricated data or a partial install, and never downgrade to writing your own
assistant in place of the supplied component.

## Preflight before returning

Confirm internally that:

1. the component block in the output is byte-identical to the block between the BEGIN
   and END markers in the supplied companion component file, markers included;
2. nothing from the companion file outside the markers (self-demo host, demo config,
   sample rows) leaked into the output;
3. `window.AIA_CONFIG` appears before the component block, and after any host data
   constants it references;
4. every field declared in the config exists in the actual rows, every measure and
   dimension references a declared field, and no two fields share an alias;
5. every watchRule encodes a threshold the dashboard itself displays -- none invented;
6. every sectionAsks id exists in the host markup;
7. all 14 applicable acceptance tests passed, including the three anti-guess tests
   (ambiguity clarifies, unknown terms -- quoted or bare -- are refused by name,
   judgment questions are refused with the handoff offer);
8. the 3 cross-checked answers agree with numbers visible on the dashboard;
9. the host is byte-for-byte unchanged outside the two insertion points;
10. the output contains no emojis and the component introduced no network activity.
