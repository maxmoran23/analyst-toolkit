# Structured Update Formatting Guide

A formatting standard for posting a status update or analytical finding to a team
channel — Slack, Microsoft Teams, Discord, a wiki, or any plain-text/markdown surface.
The goal is a post that is **scannable in three seconds**: a header line that tells the
whole story, a compact metrics dashboard, structured finding cards, and a footer.

Use this when you have an analytical result, a status report, or a recurring intelligence
update to share, and you want it consistent and dense rather than a wall of prose.

## Design Principles

1. **Scan in 3 seconds** — the header line tells the full story; everything below is
   supporting detail.
2. **Density over length** — pack more information into less space. Tables beat prose.
   Numbers beat adjectives.
3. **Visual hierarchy** — bold headers, divider lines, indented detail. The eye should
   flow naturally from headline to detail.
4. **Consistent structure** — reuse the same card and section patterns every time.
   Familiarity makes a regular reader faster.
5. **Scores are glanceable** — `72/100` with a visual bar reads faster than a paragraph
   describing "moderate-to-strong."

---

## Message Structure Template

Every structured update follows this skeleton:

```
{SOURCE_NAME} | {DATE} {TIME} {TIMEZONE}

{HEADER_LINE — the single most important insight, bold}

{SUMMARY_DASHBOARD — composite indices, key metrics}

{SECTION_DIVIDER}

{FINDINGS — structured cards}

{SECTION_DIVIDER}

{FOOTER — sources, quality, runtime}
```

---

## Component Library

### 1. Header Line
```
*MARKET UPDATE* | Apr 13, 2026 2:00 PM ET
```
- Source / report name in bold caps
- Pipe separator
- Date and time with timezone
- No emoji in the header

### 2. Summary Dashboard (for updates with composite scores or key metrics)
```
Heat: *67*/100 `HOT`  |  Sentiment: *62* (Positive)  |  Regime: `EXPANSION`
Benchmark: *$68,142* (+2.1% 24h)  |  Volume: `ACTIVE`  |  Index: *71*/100
```
- Key metrics on one or two lines, no more
- Scores in bold numbers
- Tier / status labels in `code` backticks for visual distinction
- Pipe separators between metrics
- Signed direction indicators: (+2.1%) or (-1.3%)

### 3. Score Bar (for any 0-100 composite score)
Use plain ASCII characters for a visual bar that renders everywhere:

```
Fit: *87*/100 [>>>>>>>>--] `STRONG`
```

Bar construction rule:
- 10 characters wide
- `>` for filled, `-` for empty
- Round `score / 10` for the filled count
- Examples:
  - 87/100 = `[>>>>>>>>--]`
  - 42/100 = `[>>>>------]`
  - 100/100 = `[>>>>>>>>>>]`
  - 15/100 = `[>---------]`

Keep decoration minimal — the number carries the meaning, not an emoji next to it.

### 4. Section Divider
```
---
```
A horizontal rule. Use between major sections.

### 5. Finding Cards
```
> *[Source] Finding title* — context tag
> Score: *87*/100 [>>>>>>>>--] `STRONG`  |  Secondary metric: value `TIER`
> Detail metric: 8/10  |  Urgency: `HIGH` (deadline Apr 25)
> Supporting attributes: A + B + C + D
> _Next: the recommended follow-up action_
```
- Blockquote (`>`) for visual indentation
- Title in bold, with the source in brackets
- Scores and key data on a dense metrics line
- Recommended action in italics at the bottom

### 6. Data Tables
```
| Item | Value | 24h | 7d | Score |
|---|---|---|---|---|
| Row A | $68,142 | +2.1% | +5.4% | 71 |
| Row B | $3,812  | +1.8% | +3.2% | 68 |
| Row C | $187    | -0.4% | +8.1% | 74 |
```
- Most channels render basic markdown tables
- Keep columns tight — abbreviate headers
- Keep number formatting consistent down each column
- Six to eight columns maximum before it gets too wide

### 7. Trend Indicators
```
Heat:     62 > 58 > 61 > 67 > *72* (trending up)
Index:    78 > 81 > 79 > 83 > *85* (improving)
Pressure: 64 > 64 > 66 > 65 > *63* (stable)
```
- Last five data points with `>` separators
- Most recent value in bold
- A short parenthetical trend description

### 8. Pipeline / Status Summary
```
Pipeline: *3* active | Stage A: 2 | Stage B: 1 | Deadlines this week: Apr 25 (Item X)
```
- A single pipe-separated line
- Bold the headline count

### 9. Alert / Escalation Format
```
*ALERT* | `CRITICAL`
*Benchmark dropped 8.2% in 4 hours* — Momentum: 12/100 `FALLING`
Affected positions: A (-$4.1K unrealized), B (-$1.2K)
Health: 38/100 `CRITICAL` — recommend reviewing exposure limits
```
- Bold `ALERT` header with severity in a code backtick
- Lead with what happened
- Immediately show the impact
- End with a recommended action

### 10. Footer
```
---
_Sources: [list] | Quality: 4/5 | Runtime: 23s | Index: 67_
```
- Italic, single line
- Compact — abbreviate everything
- Include source attribution and any self-assessed quality rating

---

## Adapting to the Audience

Match the level of detail to where the update lands:

- **A high-level "front page" channel** — most polished and scannable. Always include
  the summary dashboard; show only the top three findings, with links to fuller detail
  elsewhere; include trend lines for key metrics.
- **A domain / working channel** — full technical detail is appropriate. Complete finding
  cards, full data tables, technical metrics and calculations.
- **An operations / infrastructure channel** — operational focus. Health metrics
  prominent, status tables, change-log style entries.
- **An emergency / alerts channel** — maximum signal, zero noise. Bold alert header;
  what happened, impact, recommended action; nothing else.
- **A direct message** — direct and conversational. Skip the source header; lead with
  the actionable insight; keep it short.

---

## Threading Discipline

Where the platform supports threaded replies (Slack, Teams, Discord), use a two-message
pattern so the channel stays scannable:

### 1. Top-level summary (keep it short — aim for under ~500 characters)
```
*{SOURCE_NAME}* | {DATE} {TIME} {TIMEZONE}

*{HEADLINE — single most important insight}*

{SUMMARY_DASHBOARD — one or two lines of key metrics}

_{N} findings in thread | Sources: {list} | Quality: {rating}/5_
```
This is what appears in the channel feed. It must be scannable in three seconds.

### 2. Thread reply (the full report)
Post the complete detailed report as a **reply to the summary message**. The thread reply
contains everything: all finding cards with full analysis, complete data tables,
supporting detail, and the full footer.

### Why threading
- **Channel readability** — each update takes a few lines in the feed instead of 30+
- **Mobile** — the summary fits on one phone screen; tap into the thread for detail
- **Interaction** — readers can reply in-thread with questions
- **No information loss** — full detail is one tap away

### When not to thread
- A single-line "no new developments" update — no thread needed
- A critical escalation to an alerts-only channel — post the full alert at top level
- A direct message — direct delivery, no threading
- A persistent dashboard / wiki update — edit the page in place

---

## Persistent Dashboard Formatting

For a living dashboard page (a wiki page or pinned document that is updated in place
rather than re-posted), use richer markdown:

- `# H1` for the page title
- `## H2` for major sections
- `### H3` for subsections
- Checklists for action items: `- [ ] Review item X`
- Blockquotes for alerts: `> Drawdown exceeds 15%`
- A "last updated" line under each section so readers know data freshness

### Example dashboard section layout
```
## Market Intelligence
Heat: 67/100 HOT | Benchmark: $68,142 | Regime: EXPANSION
Last updated: Apr 13, 2:00 PM

## Regulatory Landscape
Pressure: 63/100 ELEVATED | Next deadline: [item] (277 days)
Last updated: Apr 13, 10:00 AM

## Action Items
- [ ] Review item X (Score: 87, deadline Apr 25)
- [ ] Check secondary signal (up 8.1% 24h)
```

---

## Anti-Patterns (Avoid)

1. Emoji as bullet points or decoration — let the structure carry the hierarchy.
2. Multi-paragraph prose in a channel post — use tables and bullets.
3. Repeating a full identity / boilerplate block in every post — the header line is enough.
4. Repeating information already on the dashboard — reference it instead.
5. Posting when there is nothing new — silence beats noise.
6. `@channel` / `@here` / all-hands mentions for routine updates.
7. Code blocks for non-code content — use blockquotes for indentation instead.
8. Empty sections — if a category has no content this period, omit the section entirely.
9. Posting a full report as a top-level message where threading is available — summary
   at top, detail in the thread.
10. A summary with no thread reply — the summary alone is not the full report.
