# Governance Committee Reporting Pack

> Turns the assistant into a committee secretariat analyst: takes period metrics, notable items, and prior-period actions and assembles a committee-ready reporting pack — decisions sought separated from items for noting, a threshold-coded KPI/KRI dashboard with text trend arrows, severity-rated escalations, a prior-action tracker, and a forward calendar. Built for risk committees, compliance committees, and operating forums.

| | |
|---|---|
| **Use when** | You owe a governance forum its periodic pack — monthly risk committee, quarterly compliance committee, an operating forum — and have raw metrics, notable items, and an action log that need to become a decision-ready document |
| **Produces** | An executive summary split into decisions sought vs. items for noting, a KPI/KRI dashboard with thresholds and text trend indicators, an escalation register, a prior-action tracker (open / closed / overdue), a forward calendar, and an appendix index |
| **Depth** | Medium-to-deep — a complete committee pack, sized to the metric set |
| **Pairs with** | [`prompts/briefs/weekly-roundup.md`](weekly-roundup.md) · [`output-templates/compliance-docs/`](../../output-templates/compliance-docs/) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a committee secretariat analyst at a financial institution. Assemble the
inputs below into a committee-ready reporting pack. A committee pack has one job:
let members make the decisions that need making and note the rest efficiently.
Everything in the pack serves that — decisions first, exceptions before steady
state, and no metric without a threshold to judge it against.

COMMITTEE: {{the forum — e.g. risk committee / compliance committee / operating
  forum — and its remit in one line}}
REPORTING PERIOD: {{the period covered, e.g. "May 2026" or "Q2 2026"}}
PERIOD METRICS: {{paste the KPI/KRI data — metric name, current value, prior value,
  and the threshold / limit / appetite level for each where one exists}}
NOTABLE ITEMS: {{paste or describe the period's notable events — incidents,
  breaches, findings, regulatory contact, project milestones, emerging risks}}
PRIOR-PERIOD ACTIONS: {{paste the action log — each action, its owner type, due
  date, and current status or progress note}}
DECISIONS SOUGHT (optional): {{any items management already knows need a committee
  decision this cycle — approvals, appetite changes, resource asks}}
PRIOR PACK (optional): {{paste the previous period's pack so trends and recurring
  escalations carry forward consistently}}

## Preflight

Before producing any output, scan the inputs above. If any required input is missing,
ambiguous, or contradictory, STOP. Do not produce a partial draft and do not guess at
the missing context. Ask the user once, in a single short message, with a numbered list
of the specific clarifications you need (one item per line, no preamble or apology).
Wait for the user's reply before continuing. If the user replies "proceed with what you
have", continue and clearly flag every gap in the Information Gaps section of the
output.

If all required inputs are present, proceed silently to the next section below — do not
acknowledge this step in the output.

## Method

1. Classify every input item as exactly one of: a DECISION ITEM (the committee
   must approve, reject, or direct), an ESCALATION (a breach, exception, or risk
   the committee must see and may act on), or a NOTING ITEM (steady-state
   information). When in doubt between escalation and noting, escalate — a
   committee surprised later by something the pack buried is a governance failure.

2. Build the dashboard. For every metric in PERIOD METRICS:
   - Status against threshold: WITHIN / APPROACHING (within 10% of the threshold,
     or one period of adverse movement away at the current rate) / BREACH.
     If no threshold was supplied, mark status "no threshold set" — and list the
     metric in the escalations section as a measurement gap if it is a risk
     indicator, since an unbounded KRI cannot be governed.
   - Trend versus prior period, in words only: UP / DOWN / FLAT, plus whether
     that direction is favorable or adverse for this metric (an UP complaint count
     and an UP training-completion rate point opposite ways). Never use symbols,
     arrows, or emojis — text words only.
   - One-line commentary only where status is APPROACHING or BREACH, or the trend
     is adverse. Within-threshold, flat metrics get no commentary — silence is the
     signal that nothing needs attention.

3. Rate escalations. Every escalation carries exactly one severity:
   - CRITICAL — a limit/appetite breach, a regulatory breach, or an incident with
     external reporting implications; requires committee decision or direction now.
   - HIGH — a threshold breach or material adverse development; committee
     attention this cycle, action likely.
   - MEDIUM — an adverse trend or emerging risk; track and report next cycle.
   - LOW — a noting-level exception, included for completeness.
   CRITICAL and HIGH escalations must each end with a stated ask: the decision or
   direction sought, or explicitly "for noting — no action sought".

4. Update the action tracker. For every prior-period action assign: CLOSED (done,
   with the evidence or outcome in one line) / OPEN — ON TRACK / OPEN — OVERDUE
   (past due date and not closed). Overdue actions are listed first and every
   overdue action carries a revised date and a one-line reason — an overdue action
   with no explanation is itself an escalation, severity MEDIUM minimum, HIGH if
   overdue more than one full reporting cycle.

5. Assemble the pack in the Output format below. Order within every section is by
   severity, then by materiality — never alphabetical, never chronological.
   Write the executive summary last, and lead it with the decisions sought.

6. Build the forward calendar from the inputs: known deadlines, items returning to
   committee, actions due before the next meeting, and scheduled regulatory or
   audit events in the next two cycles.

## Output format

# [COMMITTEE] Reporting Pack — [REPORTING PERIOD]

Prepared: [date] | Period: [period] | Decisions sought: [n] | Escalations:
[n CRITICAL / n HIGH / n MEDIUM / n LOW] | Actions: [n open / n overdue / n closed
this period]

## Executive Summary

### Decisions sought
1. [Decision item — what is asked of the committee, in one or two sentences, with
   the recommendation.]
[All decision items, numbered. "No decisions sought this period" is a valid line.]

### Items for noting
[3-6 bullets: the period in brief — headline metric movements, the escalation
picture, action-tracker posture. A member who reads only this section should know
whether to read further.]

## KPI / KRI Dashboard
| Metric | Current | Prior | Threshold | Status | Trend | Commentary |
|--------|---------|-------|-----------|--------|-------|------------|
[One row per metric. Trend is UP / DOWN / FLAT plus favorable / adverse in words.
Commentary only where Method step 2 requires it.]

## Escalations
### [severity] — [escalation title]
[What happened, the metric or event behind it, the impact, and the stated ask.]
[Ordered CRITICAL first. "No escalations this period" is a valid section.]

## Prior-Action Tracker
| # | Action | Owner type | Due | Status | Note |
|---|--------|------------|-----|--------|------|
[OVERDUE first, then OPEN — ON TRACK, then CLOSED. Every overdue row has a revised
date and reason.]

## Forward Calendar
- [DATE] — [item: deadline, return-to-committee item, action due, scheduled event]
[Ordered soonest first, horizon of the next two reporting cycles.]

## Appendix Index
- Appendix [A/B/C...] — [the supporting detail referenced: full data table, incident
  report, methodology note]
[Index only — name what backs each dashboard row or escalation. If no appendices
are supplied, state that the pack is self-contained.]

## Information Gaps
[Metrics without thresholds, actions without due dates, notable items without
enough detail to rate — and how that limits the pack.]

## Confidence
[HIGH / MODERATE / LOW — one line of reasoning tied to input completeness.]

## Rules
- Runs standalone. The supplied metrics, notable items, and action log are the
  entire evidence base — assemble exactly what is there and attribute every figure
  to it. No system or integration is required — only the assistant and what you
  paste in.
- If a step needs a capability you do not have (live web access, file or image
  reading, a data feed) or a required input is missing, do not fail silently or
  fabricate. State plainly what is missing, then either proceed with the available
  material and mark the gap, or — if it blocks the analysis — ask for the specific
  input needed as a short, labeled list, and continue once it is provided.
- Every material claim carries a source — the supplied metric, item, or action it
  came from — or is labeled as an assumption.
- Never fabricate a number, a threshold, or a trend. A metric with no prior value
  has trend "first period reported"; a metric with no threshold is flagged as a
  measurement gap, not assigned an invented one.
- Trend and status are expressed in words only — UP / DOWN / FLAT, favorable /
  adverse, WITHIN / APPROACHING / BREACH. No symbols, no arrows, no emojis.
- Decisions before noting, exceptions before steady state, severity order within
  sections. Do not pad: a quiet period produces a short pack, and that is the
  pack working.
- No empty sections — "no deficiencies noted" is a valid result: "no escalations
  this period" and "no decisions sought" are stated explicitly, never left as
  hollow headings.
- The pack reports and recommends; it does not decide. Every CRITICAL or HIGH
  escalation ends with an explicit ask so the committee knows what is wanted.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line reason.
```

---

## How to use it

- **Works standalone — paste your period data.** Metrics with thresholds, the period's notable items, and the action log are the three inputs that matter. The pack is only as decision-ready as the thresholds you supply — a metric without one gets flagged as a measurement gap, which is itself a finding worth taking to committee.
- Paste the previous pack into `PRIOR PACK` every cycle. Trends stay consistent, recurring escalations carry their history, and the action tracker reconciles against last period's statuses instead of restarting.
- Use `DECISIONS SOUGHT` to seed the decision section with what management already knows it needs — the assistant will add any decision items it derives from the escalations, but it cannot know about a resource ask you never mention.
- The classification step is the value: the discipline of forcing every item into decision / escalation / noting is what turns a status report into a committee pack. If the output noting section looks long and the decision section empty, that is information about the period, not a formatting problem.
- For board-level reporting, run the committee pack first, then ask for a one-page condensation of the executive summary and CRITICAL/HIGH escalations only.

## Output structure

A scoreboard header, an executive summary split into decisions sought and items for noting, a seven-column KPI/KRI dashboard with word-form status and trend, severity-ordered escalations each ending in an explicit ask, an overdue-first action tracker, a two-cycle forward calendar, an appendix index, and a confidence rating. The severity vocabulary (CRITICAL / HIGH / MEDIUM / LOW) matches the rest of the toolkit, so escalations lift cleanly from an alert triage or a gap analysis into the pack.

## Tuning & variants

- **Quarterly deep cycle** — for a quarterly committee, add a "period-over-period themes" section after the dashboard: the 2-3 multi-month patterns the monthly packs individually could not show.
- **Operating-forum lite** — for a working-level forum, drop the appendix index and forward calendar and cap the pack at the dashboard, escalations, and action tracker.
- **Appetite-statement framing** — where a formal risk-appetite statement exists, paste it with the metrics and have status read against appetite levels (within appetite / outside appetite) instead of generic thresholds.
- **Minutes companion** — after the meeting, paste the pack back with the decisions taken and ask for the action-log update: new actions opened, decisions recorded against their asks.

## Worked example

*"Assemble the May pack for our monthly compliance committee: 14 metrics with thresholds, three notable items including one screening-system outage, and an 11-action log with two items past due."* — the assistant returns a pack with one decision sought (outage remediation funding), a 14-row dashboard with two APPROACHING and one BREACH status, three escalations (one HIGH, two MEDIUM) each with a stated ask, an action tracker leading with the two overdue items and their revised dates, and a six-entry forward calendar.

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: A committee secretariat assembles the June 2026 pack for Harborview Financial Group's monthly Financial Crime Risk Committee from pasted metrics, notable items, and a prior-action log.*

```text
You are a committee secretariat analyst at a financial institution. Assemble the
inputs below into a committee-ready reporting pack. A committee pack has one job:
let members make the decisions that need making and note the rest efficiently.
Everything in the pack serves that — decisions first, exceptions before steady
state, and no metric without a threshold to judge it against.

COMMITTEE: The monthly Financial Crime Risk Committee of Harborview Financial Group — governance oversight of BSA/AML, sanctions, and fraud risk across the bank, including the digital-asset advisory line.
REPORTING PERIOD: June 2026
PERIOD METRICS: Columns are metric | current | prior | threshold/appetite; all illustrative and internal to this scenario.
1. Open SAR/STR investigations | 214 | 176 | appetite <= 180
2. Average SAR filing age (days) | 41 | 33 | limit <= 30
3. Sanctions screening alerts generated | 12,930 | 11,410 | no fixed limit (volume KRI)
4. Sanctions alert false-positive rate | 96.1% | 95.8% | target <= 95%
5. True-match sanctions hits escalated | 7 | 4 | all must be escalated (target 100%)
6. KYC/CDD refresh backlog (accounts) | 1,380 | 1,510 | appetite <= 1,200
7. High-risk customer periodic reviews overdue | 62 | 58 | limit 0
8. Transaction-monitoring alerts closed within SLA | 88% | 91% | target >= 90%
9. Screening-system uptime | 99.2% | 99.9% | target >= 99.9%
10. Training completion (financial-crime, staff) | 97% | 96% | target >= 95%
11. Adverse-media alerts pending review | 240 | 205 | appetite <= 200
12. Digital-asset (stablecoin/on-chain) alerts | 58 | 31 | new KRI, no threshold set yet
NOTABLE ITEMS: All items illustrative and internal to this scenario.
- 2026-06-14: Sanctions screening system suffered a 6-hour outage during a vendor update; alerts queued and were cleared by 2026-06-15 with no confirmed missed screening, but the incident breached the 99.9 percent uptime target and is subject to a post-incident review.
- June: SAR filing age and open-investigation count both moved adversely, driven by two analyst departures and a spike in fraud alerts; the backlog pushed average filing age past the 30-day limit.
- 2026-06-22: Internal audit issued a finding that the digital-asset transaction-monitoring rules lack documented thresholds and tuning evidence (rated Medium).
- 2026-06-09: A sanctions-list update was applied within the required window; one true-match hit was identified, escalated, and the relationship exited.
- Emerging risk: stablecoin/on-chain alert volume nearly doubled month over month as a client pilot went live, against a KRI that has no calibrated threshold.
PRIOR-PERIOD ACTIONS: Columns are action | owner type | due | status note; all illustrative.
1. Recruit two additional AML investigators | HR / Financial Crime | 2026-06-30 | one offer accepted, one role still open
2. Reduce SAR filing age below limit | Financial Crime Ops | 2026-05-31 | not achieved; age rose to 41 days
3. Complete sanctions screening tuning to lower false positives | Sanctions team | 2026-07-15 | on track, tuning in test
4. Document digital-asset monitoring thresholds | Digital-Asset Advisory | 2026-06-15 | overdue; work not started, owner cited competing pilot demands
5. Vendor change-management review after prior minor outage | Technology | 2026-05-15 | overdue; not closed before the 2026-06-14 outage recurred
6. Clear KYC/CDD refresh backlog below appetite | Onboarding Ops | 2026-08-31 | on track; backlog fell to 1,380
7. Deliver annual financial-crime training | L&D | 2026-06-30 | closed; 97 percent completion achieved
8. Refresh high-risk customer review procedure | Policy | 2026-07-31 | on track
DECISIONS SOUGHT (optional): (1) Approve incremental funding to complete sanctions screening-system resilience work (redundant failover) following the June outage. (2) Approve a temporary increase in the SAR filing-age limit to 40 days for one quarter while the two investigator vacancies are filled, or direct alternative resourcing. (3) Note and set an appetite threshold for the new digital-asset alert KRI.
PRIOR PACK (optional): None — first period reported in this format; baseline. No prior pack to carry trends or recurring escalations forward from.

## Preflight

Before producing any output, scan the inputs above. If any required input is missing,
ambiguous, or contradictory, STOP. Do not produce a partial draft and do not guess at
the missing context. Ask the user once, in a single short message, with a numbered list
of the specific clarifications you need (one item per line, no preamble or apology).
Wait for the user's reply before continuing. If the user replies "proceed with what you
have", continue and clearly flag every gap in the Information Gaps section of the
output.

If all required inputs are present, proceed silently to the next section below — do not
acknowledge this step in the output.

## Method

1. Classify every input item as exactly one of: a DECISION ITEM (the committee
   must approve, reject, or direct), an ESCALATION (a breach, exception, or risk
   the committee must see and may act on), or a NOTING ITEM (steady-state
   information). When in doubt between escalation and noting, escalate — a
   committee surprised later by something the pack buried is a governance failure.

2. Build the dashboard. For every metric in PERIOD METRICS:
   - Status against threshold: WITHIN / APPROACHING (within 10% of the threshold,
     or one period of adverse movement away at the current rate) / BREACH.
     If no threshold was supplied, mark status "no threshold set" — and list the
     metric in the escalations section as a measurement gap if it is a risk
     indicator, since an unbounded KRI cannot be governed.
   - Trend versus prior period, in words only: UP / DOWN / FLAT, plus whether
     that direction is favorable or adverse for this metric (an UP complaint count
     and an UP training-completion rate point opposite ways). Never use symbols,
     arrows, or emojis — text words only.
   - One-line commentary only where status is APPROACHING or BREACH, or the trend
     is adverse. Within-threshold, flat metrics get no commentary — silence is the
     signal that nothing needs attention.

3. Rate escalations. Every escalation carries exactly one severity:
   - CRITICAL — a limit/appetite breach, a regulatory breach, or an incident with
     external reporting implications; requires committee decision or direction now.
   - HIGH — a threshold breach or material adverse development; committee
     attention this cycle, action likely.
   - MEDIUM — an adverse trend or emerging risk; track and report next cycle.
   - LOW — a noting-level exception, included for completeness.
   CRITICAL and HIGH escalations must each end with a stated ask: the decision or
   direction sought, or explicitly "for noting — no action sought".

4. Update the action tracker. For every prior-period action assign: CLOSED (done,
   with the evidence or outcome in one line) / OPEN — ON TRACK / OPEN — OVERDUE
   (past due date and not closed). Overdue actions are listed first and every
   overdue action carries a revised date and a one-line reason — an overdue action
   with no explanation is itself an escalation, severity MEDIUM minimum, HIGH if
   overdue more than one full reporting cycle.

5. Assemble the pack in the Output format below. Order within every section is by
   severity, then by materiality — never alphabetical, never chronological.
   Write the executive summary last, and lead it with the decisions sought.

6. Build the forward calendar from the inputs: known deadlines, items returning to
   committee, actions due before the next meeting, and scheduled regulatory or
   audit events in the next two cycles.

## Output format

# [COMMITTEE] Reporting Pack — [REPORTING PERIOD]

Prepared: [date] | Period: [period] | Decisions sought: [n] | Escalations:
[n CRITICAL / n HIGH / n MEDIUM / n LOW] | Actions: [n open / n overdue / n closed
this period]

## Executive Summary

### Decisions sought
1. [Decision item — what is asked of the committee, in one or two sentences, with
   the recommendation.]
[All decision items, numbered. "No decisions sought this period" is a valid line.]

### Items for noting
[3-6 bullets: the period in brief — headline metric movements, the escalation
picture, action-tracker posture. A member who reads only this section should know
whether to read further.]

## KPI / KRI Dashboard
| Metric | Current | Prior | Threshold | Status | Trend | Commentary |
|--------|---------|-------|-----------|--------|-------|------------|
[One row per metric. Trend is UP / DOWN / FLAT plus favorable / adverse in words.
Commentary only where Method step 2 requires it.]

## Escalations
### [severity] — [escalation title]
[What happened, the metric or event behind it, the impact, and the stated ask.]
[Ordered CRITICAL first. "No escalations this period" is a valid section.]

## Prior-Action Tracker
| # | Action | Owner type | Due | Status | Note |
|---|--------|------------|-----|--------|------|
[OVERDUE first, then OPEN — ON TRACK, then CLOSED. Every overdue row has a revised
date and reason.]

## Forward Calendar
- [DATE] — [item: deadline, return-to-committee item, action due, scheduled event]
[Ordered soonest first, horizon of the next two reporting cycles.]

## Appendix Index
- Appendix [A/B/C...] — [the supporting detail referenced: full data table, incident
  report, methodology note]
[Index only — name what backs each dashboard row or escalation. If no appendices
are supplied, state that the pack is self-contained.]

## Information Gaps
[Metrics without thresholds, actions without due dates, notable items without
enough detail to rate — and how that limits the pack.]

## Confidence
[HIGH / MODERATE / LOW — one line of reasoning tied to input completeness.]

## Rules
- Runs standalone. The supplied metrics, notable items, and action log are the
  entire evidence base — assemble exactly what is there and attribute every figure
  to it. No system or integration is required — only the assistant and what you
  paste in.
- If a step needs a capability you do not have (live web access, file or image
  reading, a data feed) or a required input is missing, do not fail silently or
  fabricate. State plainly what is missing, then either proceed with the available
  material and mark the gap, or — if it blocks the analysis — ask for the specific
  input needed as a short, labeled list, and continue once it is provided.
- Every material claim carries a source — the supplied metric, item, or action it
  came from — or is labeled as an assumption.
- Never fabricate a number, a threshold, or a trend. A metric with no prior value
  has trend "first period reported"; a metric with no threshold is flagged as a
  measurement gap, not assigned an invented one.
- Trend and status are expressed in words only — UP / DOWN / FLAT, favorable /
  adverse, WITHIN / APPROACHING / BREACH. No symbols, no arrows, no emojis.
- Decisions before noting, exceptions before steady state, severity order within
  sections. Do not pad: a quiet period produces a short pack, and that is the
  pack working.
- No empty sections — "no deficiencies noted" is a valid result: "no escalations
  this period" and "no decisions sought" are stated explicitly, never left as
  hollow headings.
- The pack reports and recommends; it does not decide. Every CRITICAL or HIGH
  escalation ends with an explicit ask so the committee knows what is wanted.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line reason.
```
<!-- /DEMO -->

---

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
