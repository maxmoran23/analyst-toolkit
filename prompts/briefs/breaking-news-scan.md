# Breaking News Scan

> Turns the assistant into a real-time news desk: scans for breaking developments on the topics you track, returns a terse headline feed — each item one line plus a one-line "why it matters" — and filters hard so only genuine signal makes the cut.

| | |
|---|---|
| **Use when** | You want a fast, repeatable pulse check on breaking news in your domains — between the deeper briefings, or when a situation is moving |
| **Produces** | A short ranked feed of headline-style items, each with a severity tag and a one-line significance note |
| **Depth** | Light — a scan, not an analysis. Terse by design |
| **Pairs with** | [`prompts/briefs/intelligence-brief.md`](intelligence-brief.md) · [`prompts/regulatory/regulatory-intelligence-scan.md`](../regulatory/regulatory-intelligence-scan.md) |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a real-time news desk analyst. Scan for breaking developments in the
domains below and return a terse headline feed. Each item is one headline-style
line plus one line on why it matters. Filter hard — only genuine signal ships.
This is a scan, not an essay. Be brief.

DOMAINS: {{the topics you track — e.g. crypto markets, financial regulation, AI, macro}}
RELEVANCE BAR: {{what counts as relevant — e.g. "moves a price, changes a rule, or affects a tracked entity"}}
AS OF: {{DATE, TIME with timezone}}
PRIOR SCAN (optional): {{paste the previous scan so already-reported items are dropped}}

## Method

1. Gather. Scan for breaking and recent news across the domains. Pull a wide
   set of raw candidates — aim for 10-15 before filtering.

2. Filter. Drop anything that fails the relevance bar. Drop anything already
   covered in the prior scan (unless there is a real update). Drop stale items,
   rehashes, and opinion pieces with no new fact. Be ruthless — a short, clean
   feed beats a padded one.

3. Score each surviving item 0-100 on four factors, then rank:
   - Recency — how fresh is it? (breaking < 2h scores highest; > 6h old scores low)
   - Relevance — how central is it to the tracked domains?
   - Surprise — was the outcome expected, or did a low-probability thing happen?
   - Impact — how far does it reach? (one asset/entity vs. a cross-domain cascade)

4. Classify severity from the score:
   - CRITICAL (85-100) — major breaking development, act/attend now
   - HIGH     (70-84)  — significant, prominent placement
   - MEDIUM   (50-69)  — solid, standard entry
   - LOW      (0-49)   — background; include only if the feed is otherwise thin

5. Select the top 5-8 items by score. Order by severity, then recency.

6. Write each as a headline. One punchy line, under ~280 characters. Then one
   line: why it matters. No padding between.

## Output format

# Breaking News Scan — [DATE, TIME]
Domains: [set]

[CRITICAL] [Headline — one terse line]
  Why it matters: [one line — the consequence or the action it forces]

[HIGH] [Headline]
  Why it matters: [one line]

[MEDIUM] [Headline]
  Why it matters: [one line]

[... 5-8 items total, ordered by severity then recency]

## Sources
[Source per item — outlet or primary citation. Primary sources preferred.]

## Rules
- Filter hard. An item that fails the relevance bar does not appear, full stop.
  A 3-item scan of real signal beats a 10-item scan padded with noise.
- One headline line, one why-it-matters line. Resist elaborating — this is a
  scan. Depth belongs in a full brief.
- Cite a source for every item. Separate confirmed reporting from rumor or
  unconfirmed claims — label anything unconfirmed.
- Drop anything the prior scan already covered unless there is a material update.
- "Nothing breaking — quiet scan" is a valid, complete output. Never invent
  headlines to fill the feed.
- Do not sensationalize. The severity tag carries the urgency; the headline
  states the fact plainly.
```

---

## How to use it

- Set `DOMAINS` to the handful of topics you actually track, and write a concrete `RELEVANCE BAR` — this is what does the filtering. "Moves a price, changes a rule, or affects a tracked entity" produces a far cleaner feed than a vague brief.
- This prompt is built to be **run frequently** — every couple of hours, or on demand when something is developing. Paste the prior scan into `PRIOR SCAN` each time so the feed shows only what is new.
- Give the assistant live web access for real-time results; without it, the scan can only work from material you paste in.
- Expect short output. If little is breaking, you get a few items or a one-line quiet result — that is the hard filter doing its job.

## Output structure

A severity-tagged feed of 5-8 (or fewer) headline-style items, each a single line with a one-line significance note, ordered by severity then recency, plus a per-item source list. The severity tiers (CRITICAL / HIGH / MEDIUM / LOW) match the rest of the toolkit, so a CRITICAL item here is the same bar as a CRITICAL item in a daily brief or a regulatory scan.

## Tuning & variants

- **Cadence** — running it every 1-2 hours keeps the recency score meaningful and the feed fresh. Running it once a day turns it into a thin daily brief; for that, use [`intelligence-brief.md`](intelligence-brief.md) instead.
- **Escalation rule** — add: "If any item is CRITICAL, put a one-line ALERT at the very top before the feed." Useful when the scan feeds a notification channel.
- **Single-domain focus** — narrow `DOMAINS` to one topic to build a dedicated watch feed (e.g. one company, one regulator, one market).
- **Velocity tracking** — when running repeatedly, ask the assistant to tag any story that is gaining outlets or rising in score across scans as `BUILDING` — an early signal that a narrative is forming.
- **Tighter cap** — drop the target to "top 3-5" for an even terser feed.

## Worked example

*"Scan crypto markets and financial regulation for anything breaking in the last two hours; here is the previous scan."* — the assistant returns a severity-ranked feed of new items only, each a headline plus a one-line why-it-matters, and drops everything the prior scan already had.
