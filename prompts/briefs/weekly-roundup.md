# Weekly Roundup

> Turns the assistant into a chief-of-staff: closes out the week with a ranked review of what happened, a graded multi-dimension scorecard, a forward look at next week, and an explicit blocker list — the weekly review a sharp operator runs on themselves.

| | |
|---|---|
| **Use when** | You want an end-of-week review across the things you track — markets, projects, a portfolio, an operation — with a scorecard and a forward plan |
| **Produces** | Top findings of the week, a graded performance scorecard, a week-over-week metrics table, next-week priorities, and a blocker list |
| **Depth** | Medium-deep — a structured review, longer than a daily brief |
| **Pairs with** | [`prompts/briefs/intelligence-brief.md`](intelligence-brief.md) · [`output-templates/dashboards/`](../../output-templates/dashboards/) |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a chief-of-staff analyst running an end-of-week review. Close out the
week below: rank what happened, grade performance on a scorecard, set next
week's priorities, and name the blockers plainly.

REVIEW SCOPE: {{e.g. markets + portfolio / a set of projects / an operation / a research program}}
WEEK ENDING: {{DATE}}
INPUTS: {{paste the week's source material — daily briefs, status notes, metrics, logs — or grant live access}}
PRIOR WEEK'S ROUNDUP (optional): {{paste last week's roundup for week-over-week comparison}}

## Method

1. Assemble the week. Read every input across the full week. If last week's
   roundup was supplied, use its metrics and predictions as the comparison
   baseline.

2. Rank the top findings. Across the whole scope, select the 5 most significant
   developments of the week. Rank by impact, novelty, and actionability. One
   sentence each, with context.

3. Compile week-over-week metrics. For each tracked metric, state this week's
   value and the change vs. the prior week. Use real numbers; mark anything
   unavailable as N/A.

4. Grade the week on the scorecard (see Scorecard below). Score each dimension
   0-100, weight, and roll up to a composite grade.

5. Set next week's priorities. Name the 3-6 things that matter next week —
   events, deadlines, decisions, workstreams to push.

6. Name the blockers. List anything stalled or at risk, and what specifically
   would unblock it. Be direct; do not soften.

## Scorecard

Grade the week across six dimensions. Score each 0-100, apply the weight, sum
to a composite. Tune the dimensions and weights to your scope and state any
change.

  Outcomes / performance ........ 25%   Did the week's results land well?
  Execution / throughput ........ 20%   Did planned work ship?
  Reliability / consistency ..... 15%   Did recurring commitments hold up?
  Signal quality ................ 15%   Was the intelligence gathered useful and accurate?
  Blocker resolution ............ 15%   Were prior blockers cleared, or carried?
  Forward readiness ............. 10%   Is next week set up well — priorities clear, no surprises?

Per-dimension scoring band:
  90-100 Outstanding    70-89 Strong       50-69 Adequate
  30-49  Weak           0-29  Failed

Composite = sum(dimension score x weight). Map to a letter grade:

  90-100 A+    80-89 A     70-79 B
  60-69  C     50-59 D     0-49  F

If a prior roundup was supplied, also show the composite trend
(e.g. "B (74) | 4-week trend: 68 -> 71 -> 70 -> 74, improving").

## Output format

# Weekly Roundup — Week ending [DATE]

Week grade: [letter] ([composite]/100) [— trend, if prior roundup supplied]
Scope: [review scope]

## Top 5 Findings This Week
1. [Most significant development — one sentence with context.]
2. [...]
3. [...]
4. [...]
5. [...]

## Performance Scorecard
| Dimension | Score | Weight | Weighted | Note |
|-----------|-------|--------|----------|------|
[one row per dimension, then a Composite row]

## Week-over-Week Metrics
| Metric | This week | Prior week | Change |
|--------|-----------|------------|--------|

## Next Week — Priorities
- [Priority — event, deadline, decision, or workstream — and why it matters]

## Blockers
[What is stalled or at risk, and the specific unblock action. "None" is valid.]

## Sources & Confidence
[Inputs used. Overall confidence: HIGH / MODERATE / LOW, with reasoning.]

## Rules
- Cite a source for every finding and every metric. Separate observed results
  from forecasts.
- Grade honestly. A weak week graded a weak week is the point — do not inflate
  the scorecard. A bad grade with a clear root cause is more useful than a
  flattering one.
- Do not fabricate metrics. Unavailable number -> "N/A", and say why.
- Blockers are named plainly, with an owner-able next action. Do not bury a
  blocker in soft language.
- If a prior roundup was supplied, anchor every comparison to it.
```

---

## How to use it

- Set `REVIEW SCOPE` to whatever you run a weekly cadence on — a portfolio, a project portfolio, an operation, a research program. The scorecard dimensions are written to generalize; rename them to fit.
- Paste the week's raw material into `INPUTS` — daily briefs, status notes, metrics, logs. If you run the daily [`intelligence-brief.md`](intelligence-brief.md), feeding the week's briefs in is the fastest path.
- This prompt is designed to be **run every week**. Paste the prior roundup into `PRIOR WEEK'S ROUNDUP` — the metrics table becomes a running week-over-week ledger and the scorecard gains a trend line.
- The scorecard is the core. If you only want a quick review, you can still run it for the grade and the blocker list alone.

## Output structure

A composite week grade in the header, five ranked findings, a six-row weighted scorecard, a week-over-week metrics table, a next-week priority list, and an explicit blocker section. The scorecard converts a qualitative week into one comparable number, so weeks can be ranked against each other and a trend tracked over a quarter.

## Tuning & variants

- **Scorecard weighting** — the default leans on outcomes and execution. For a research or learning program, raise Signal quality and Forward readiness; for an operations function, raise Reliability. Always state the weighting used.
- **Project-portfolio variant** — set the scope to a list of projects and ask for a per-project velocity grade (0-100) and a stage tag (idea / scoped / active / blocked / shipped / paused) alongside the fleet-level scorecard. This turns the roundup into a Monday project tracker.
- **Forward-only variant** — for a planning use, ask for just the "Next Week — Priorities" and "Blockers" sections.
- **Quarterly roll-up** — run it over 13 weeks of prior roundups instead of one week's raw inputs to get a best-week / worst-week / median read.
- **Formatted deliverable** — pair the output with [`output-templates/dashboards/`](../../output-templates/dashboards/) to render the scorecard and metrics as a dashboard.

## Worked example

*"Run a weekly roundup across my four active projects for the week ending Friday; here is last week's roundup and this week's status notes."* — the assistant returns ranked findings, a graded scorecard with a trend line, a week-over-week metrics table, and a blocker list with unblock actions.
