#!/usr/bin/env python3
"""
Append the universal renderer appendix + per-file customization to each
standalone/*.md file. Idempotent: if a file already contains the appendix
sentinel, the previous appendix block is replaced rather than duplicated.

Sentinel: "## Render as a formatted deliverable" — everything from that header
to end-of-file is replaced.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
HERE = Path(__file__).resolve().parent
SOURCE_FILE = HERE.parent / "methodology" / "report-templates.md"
SENTINEL_BEGIN = "<!-- BEGIN_RENDERER_APPENDIX -->"
SENTINEL_END = "<!-- END_RENDERER_APPENDIX -->"
SENTINEL = "## Render as a formatted deliverable"  # marks where to truncate in target files


def _extract_universal() -> str:
    text = SOURCE_FILE.read_text()
    start = text.find(SENTINEL_BEGIN)
    end = text.find(SENTINEL_END)
    if start == -1 or end == -1 or end < start:
        raise SystemExit(
            f"FATAL: cannot find sentinel pair in {SOURCE_FILE}. "
            f"Expected '{SENTINEL_BEGIN}' and '{SENTINEL_END}'."
        )
    # Take everything after the BEGIN sentinel line, up to (not including) the END sentinel line
    inner = text[start + len(SENTINEL_BEGIN):end]
    # Normalize leading/trailing whitespace so the result is exactly one '\n' before content
    return inner.strip("\n") + "\n"


UNIVERSAL = _extract_universal()

# Per-file customization block (appended AFTER the universal appendix in each file).
# Keys are file stems (no .md).
PER_FILE = {
"document-summarizer": """

---

## Per-analysis customization — document summary

This summary is best delivered as **Mode A (Word)** for a stakeholder hand-off or **Mode C (PDF)** for a formal one-page brief. Mode B (Excel) is useful when the document has a long deadlines/numbers/parties table worth filtering. Mode D (HTML dashboard) is overkill for most summaries but shines when summarizing a long regulation that has many obligations and a multi-stakeholder reader.

**Mode A (Word) — Heading 1 sections in order:**
1. Summary (with reader / purpose / source line at the top, then Bottom Line)
2. Key Points (as a table: Severity | Point | Source)
3. Deadlines, Numbers, Named Parties (table)
4. Obligations or Required Actions (bulleted, or table if ≥5)
5. Open Questions (bulleted)
6. Information Gaps + Overall Confidence

**Mode B (Excel) tabs:** Summary (Bottom Line, reader, source, confidence) · Key Points (sortable by severity) · Deadlines & Numbers · Obligations · Open Questions.

**Mode C (PDF) page sequence:**
- Page 1 Cover — hero stat = number of CRITICAL+HIGH key points; caption = "ITEMS REQUIRING ACTION"; KPI row = total key points / deadlines / obligations / open questions
- Page 2 — Executive Summary + Bottom Line callout
- Page 3 — Key Points table (severity-tagged)
- Page 4 — Deadlines, Numbers, Named Parties table
- Page 5 — Obligations + Open Questions (two-column)
- Page 6 — Methodology / Source / Confidence

**Mode D (HTML dashboard) DATA wiring:**
- `reportType`: "DOCUMENT SUMMARY"
- `accent`: pick by document subject (a regulation → `#0a84ff`; a research paper → `#bf5af2`; a vendor doc → `#22d3ee`)
- `kpis`: `[ {label: "Critical/High Items", value: count}, {label: "Deadlines", value: count}, {label: "Obligations", value: count}, {label: "Open Questions", value: count} ]`
- `navSections`: include `sec-summary`, `sec-findings` (renamed "Key Points" via the h2 in the body), `sec-gaps`; consider adding a deadlines section and an obligations section
- `chartConfig`: a `doughnut` of key-point severity distribution is the most useful chart for a summary
""",

"comparison-matrix": """

---

## Per-analysis customization — comparison matrix

This is the canonical **Mode B (Excel)** analysis — the weighted scorecard is exactly what Excel is for. **Mode D (HTML dashboard)** is the second-best for a presentation read because the option cards and decisive-criteria highlight are visually scannable. Word and PDF work for sign-off contexts.

**Mode A (Word) — Heading 1 sections in order:**
1. Decision + Recommendation (1-page summary)
2. Framing (decision / options / constraints / criteria table)
3. Scorecard (table — options as columns, criteria as rows, weighted total at bottom)
4. Option Reads (Heading 2 per option)
5. Decisive Criteria
6. Recommendation + Runner-up
7. Flip Conditions (bulleted)
8. Information Gaps + Confidence

**Mode B (Excel) tabs:**

| Tab | Headers | Severity column? |
|---|---|---|
| Summary | Decision · Recommendation · Composite · Confidence | no |
| Scorecard | Criterion · Weight · [Option A] · [Option B] · [Option C] · Decisive | the criterion column, color-coded by weight; option columns color-coded 0-100 |
| Constraints | Constraint · [Option A pass/fail] · [Option B] · [Option C] | yes — red for failed |
| Option Reads | Option · Best at · Weakest at · Cost · Constraints strained | no |
| Flip Conditions | Condition · Effect · Likely? | yes |

Excel's "Conditional Formatting → Color Scales" on the scorecard cells gives the heatmap effect for free.

**Mode C (PDF) page sequence:**
- Page 1 Cover — hero = recommended option name (large); caption = composite weighted score; KPI row = options compared / decisive criteria count / confidence / flip-condition count
- Page 2 — Framing (decision, options, criteria table)
- Page 3 — Scorecard with bar chart of weighted totals
- Page 4 — Option Reads (one paragraph each in a comparison grid)
- Page 5 — Decisive Criteria + Flip Conditions
- Page 6 — Methodology

**Mode D (HTML dashboard) DATA wiring:**
- `reportType`: "OPTION COMPARISON"
- `accent`: typically `#0a84ff` for general decision work; `#22d3ee` for tech/vendor selection
- `kpis`: `[ {label: "Recommended", value: optionName}, {label: "Weighted Score", value: "X/100"}, {label: "Options Considered", value: n}, {label: "Decisive Criteria", value: n} ]`
- `navSections`: Summary · Scorecard · Options · Decisive · Flip Conditions · Gaps
- `scorecard`: the headers row should be `["Criterion", "Weight"] + optionNames`; rows are criteria with per-option scores
- `chartConfig`: `radar` with one dataset per option (axes = criteria, values = scores) is the right chart for comparison work — better than a bar chart for showing shape differences
- Add `Trade-offs` and `Dissenting view` cards if running this comparison alongside `decision-memo` material
""",

"meeting-prep": """

---

## Per-analysis customization — meeting prep

This is best delivered as **Mode A (Word)** for a printable handout the user reads on the way to the meeting, or **Mode C (PDF)** when the brief is shared with a manager / chief of staff. **Mode D (HTML dashboard)** is over-engineered for most meeting prep but valuable for high-stakes meetings (regulatory exams, board reviews) where multiple stakeholders consult the prep beforehand.

**Mode A (Word) — Heading 1 sections in order:**
1. Meeting header (date · duration · user's role · non-negotiable highlighted in callout)
2. Attendees (table: Name | Role | Org | What they likely want | Watch-out)
3. Agenda (numbered list with minute allocations)
4. Questions to be ready for (numbered, each with ready answer)
5. Questions to ask (numbered, each with reason)
6. Watch-outs (bulleted)
7. Recap of relevant prior context (bulleted, if PRIOR CONTEXT provided)
8. Information Gaps

**Mode B (Excel) tabs:** Summary (meeting facts + non-negotiable) · Attendees · Agenda Timing · Questions (with a "Ready answer / Why ask" column) · Watch-outs. Less natural than Word for this analysis but useful when prepping for a recurring meeting series.

**Mode C (PDF) page sequence:**
- Page 1 Cover — hero = the single non-negotiable in 1-2 short sentences (no number); caption = "DO NOT LEAVE WITHOUT"; KPI row = attendees / agenda items / questions to ask / watch-outs
- Page 2 — Attendees table
- Page 3 — Agenda
- Page 4 — Questions to be ready for + Questions to ask (two-column)
- Page 5 — Watch-outs + Prior Context recap

**Mode D (HTML dashboard) DATA wiring:**
- `reportType`: "MEETING PREP"
- `accent`: `#5e5ce6` (indigo) for internal / `#0a84ff` for external — choose by meeting type
- `kpis`: `[ {label: "Duration", value: minutes}, {label: "Attendees", value: n}, {label: "Questions Ready", value: n}, {label: "Watch-outs", value: n} ]`
- `navSections`: Summary · Attendees · Agenda · Questions · Watch-outs
- Replace the default `sec-scorecard` with `sec-attendees` (relabel the H2 and DATA.scorecard with attendees as rows)
- `chartConfig`: omit or use a pie of agenda time allocation — for meeting prep, the chart is usually optional and can be removed entirely
""",

"decision-memo": """

---

## Per-analysis customization — decision memo

This is the canonical **Mode A (Word)** analysis — the one-page decision memo is exactly the shape Word produces best. **Mode C (PDF)** is the second choice when the memo needs to be circulated for sign-off. Excel works for the options-evaluation table when there are 4+ options. The HTML dashboard is best when the decision is high-stakes enough to warrant a shareable interactive read.

**Mode A (Word) — Heading 1 sections in order:**
1. Decision (one line) + Recommendation (1-2 sentences)
2. Context (3-5 sentences — why now, what's at stake)
3. Options & Evaluation (table — Option | Does well | Does poorly | Cost | Constraints strained, with **Recommended** marker on the chosen row)
4. Trade-offs of the Recommendation (bulleted, ≥2)
5. Risks & Mitigations (table — Risk | Likelihood | Impact | Mitigation | Mitigable?)
6. Dissenting View (italicized paragraph — visually set apart from the rest)
7. Flip Conditions (bulleted)
8. Next Step (one line, ownership)
9. Information Gaps + Confidence

**Mode B (Excel) tabs:** Summary (decision, recommendation, deadline, decision-maker) · Options Evaluation · Risk Register · Flip Conditions · Next Steps. The risks tab benefits from a heat-map (Likelihood × Impact) using conditional formatting.

**Mode C (PDF) page sequence:**
- Page 1 Cover — hero = the chosen option name; caption = "RECOMMENDATION"; KPI row = options considered / risks identified / trade-offs / flip conditions
- Page 2 — Context + Recommendation in full
- Page 3 — Options Evaluation table
- Page 4 — Trade-offs + Risks (two-column or stacked)
- Page 5 — Dissenting View (in a callout, prominent) + Flip Conditions
- Page 6 — Next Step + Methodology

**Mode D (HTML dashboard) DATA wiring:**
- `reportType`: "DECISION MEMO"
- `accent`: `#0a84ff` for strategic / `#f59e0b` for financial / `#5e5ce6` for technical
- `kpis`: `[ {label: "Recommendation", value: optionName}, {label: "Options", value: n}, {label: "Risks Identified", value: n}, {label: "Trade-offs", value: n} ]`
- `navSections`: Summary · Options · Trade-offs · Risks · Dissenting View · Flip Conditions · Next Step
- Add a `Dissenting View` card explicitly — it must be visually distinct (italics, alternate background) because it is the single highest-signal section of the memo
- `chartConfig`: a `bar` chart comparing option cost or option score works; a Likelihood × Impact risk-heatmap rendered as colored cells in a separate section card is even better for high-stakes decisions
""",

"weekly-comms-digest": """

---

## Per-analysis customization — weekly comms digest

This analysis is best delivered as **Mode D (HTML dashboard)** for a personal week-at-a-glance the user keeps open in a browser tab, or **Mode A (Word)** for a circulated team weekly. **Mode B (Excel)** is the right choice when the user tracks commitments / decisions / overdue items across weeks and wants to filter — it becomes a personal kanban. Mode C (PDF) is less natural for a digest but works for an end-of-quarter or end-of-year compilation.

**Mode A (Word) — Heading 1 sections in order:**
1. Top of mind (this week) — numbered, 3-5 items
2. By Priority (Heading 2 per priority — name as user provided; each with bulleted items)
3. Other (actionable, off-priority)
4. Commitments made or requested (table)
5. Decisions (Taken / Pending user / Pending others)
6. Overdue / Slipped (bulleted)
7. Appears unreplied — review before next week
8. Week ahead (table)
9. Information Gaps + Confidence

**Mode B (Excel) tabs:**

| Tab | Headers | Severity column? |
|---|---|---|
| Summary | Period · Top of mind · Commitments count · Overdue count | no |
| Top of Mind | Item · Required Action · Priority | the Required Action column |
| By Priority | Priority · Item · Source · Date · Required Action | the Required Action column |
| Commitments | Owner · Commitment · To whom · By when · Source · Status | yes — overdue/today/this week/later |
| Decisions | Status · Decision · Context · On the hook | the Status column |
| Overdue | Item · Original date · Days overdue · Source | yes — by days overdue threshold |
| Week Ahead | Date · Item · What it requires | by date |

**Mode C (PDF) page sequence:**
- Page 1 Cover — hero = count of Top-of-Mind items; caption = "ITEMS THIS WEEK"; KPI row = commitments / decisions / overdue / unreplied
- Page 2 — Top of Mind
- Page 3 — By Priority (one section per)
- Page 4 — Commitments table
- Page 5 — Decisions + Overdue + Unreplied
- Page 6 — Week Ahead

**Mode D (HTML dashboard) DATA wiring:**
- `reportType`: "WEEKLY DIGEST"
- `accent`: `#5e5ce6` (indigo) is the natural pick — a personal-productivity color
- `kpis`: `[ {label: "Top of Mind", value: n}, {label: "Commitments", value: n}, {label: "Overdue", value: n, delta: "needs attention" if >0}, {label: "Unreplied", value: n} ]`
- `navSections`: Top of Mind · By Priority · Commitments · Decisions · Overdue · Week Ahead
- Replace default sections with priority-specific cards (one card per user priority, each showing 3-5 items)
- `chartConfig`: a `bar` chart of activity per priority (items per priority bucket) is the most useful chart; a timeline visualization of "week ahead" is even better if there's time to build it
""",

"action-items-extractor": """

---

## Per-analysis customization — action items extractor

This is the canonical **Mode B (Excel)** analysis — action items live in a sortable, filterable table the user (or a team) updates over time. **Mode A (Word)** is the right choice when the items are appended to meeting notes for circulation. Mode C (PDF) suits a one-time deliverable like a workshop summary. Mode D (HTML dashboard) is appropriate when a team will track the items as a board.

**Mode A (Word) — Heading 1 sections in order:**
1. Source header (what / when / participants / extraction date)
2. Open Action Items (table — #, Owner, Action, Due, Depends on, Source)
3. Items Owned by [USER] *(if user's identity provided)*
4. Decisions Carried Forward (bulleted)
5. Open Questions (bulleted)
6. Status of Prior Action Items (table — if prior list provided)
7. Information Gaps + Confidence

**Mode B (Excel) tabs:**

| Tab | Headers | Severity column? |
|---|---|---|
| Summary | Source · Period · Open items · Closed-this-source · Open Questions | no |
| Open Action Items | # · Owner · Action · Due · Depends on · Source · Status | the Status column (Open / In progress / Blocked / Done) |
| User's Items *(if USER_ID supplied)* | # · Action · Due · Depends on · Source | by Due (overdue red) |
| Decisions | Decision · Context · Source | no |
| Open Questions | Question · Source · Suggested owner | no |
| Prior Items Reconciliation *(if PRIOR_LIST supplied)* | # · Prior action · Owner · Status (Closed / Slipped / Carries forward) · Evidence | the Status column |

Add data-validation dropdowns on Owner (from a participants list) and Status, so the workbook becomes a working tracker.

**Mode C (PDF) page sequence:**
- Page 1 Cover — hero = total open action item count; caption = "ACTION ITEMS"; KPI row = open items / user's items / decisions / open questions
- Page 2 — Open Action Items table (might span pages — landscape orientation helps)
- Page 3 — Decisions + Open Questions
- Page 4 — Prior Items Reconciliation (if applicable)
- Page 5 — Methodology

**Mode D (HTML dashboard) DATA wiring:**
- `reportType`: "ACTION ITEMS"
- `accent`: `#30d158` (green) — operational / forward-looking color
- `kpis`: `[ {label: "Open Items", value: n}, {label: "Owed by [User]", value: n}, {label: "Decisions", value: n}, {label: "Open Questions", value: n} ]`
- `navSections`: Summary · Open Items · User's Items · Decisions · Open Questions · Prior Status
- The default `sec-scorecard` becomes the Open Items table (relabel H2)
- `chartConfig`: a `bar` chart of items per owner (workload distribution) is the most useful single chart
""",

"entity-risk-assessment": """

---

## Per-analysis customization — entity risk assessment

This is the most format-rich analysis in the library — **all four modes are first-class**. Word is the canonical compliance hand-off. Excel is the working-paper format the analyst maintains. PDF is the polished deliverable for senior review. The HTML dashboard is the interactive read for ongoing monitoring of a watched counterparty.

**Mode A (Word) — Heading 1 sections in order:**
1. Cover (Entity / Composite / Rating / Date / Author / Classification)
2. Executive Summary
3. Risk Scorecard (8-domain weighted table — include the override note if triggered)
4. Domain Findings (Heading 2 per domain, 8 in total — even if "no adverse findings identified")
5. Red Flags
6. Information Gaps
7. Recommended Disposition (callout — prominent)
8. Sources & Confidence (Appendix-style at the end)

**Mode B (Excel) tabs:**

| Tab | Headers | Severity column? |
|---|---|---|
| Summary | Entity · Typology · Composite · Rating · Disposition · Confidence | the Rating column (LOW/MOD/ELEVATED/HIGH/SEVERE color scale) |
| Scorecard | Domain · Score · Weight · Weighted · Key driver | the Score column (color scale 0-100) |
| Domain Detail | Domain · Finding · Evidence · Source · Severity | the Severity column |
| Red Flags | Flag · Driver · Domain · Severity | yes |
| Information Gaps | Gap · Why it matters · What would close it | no |
| Sources | Source · Date · Type (primary/secondary) · Reliability | the Reliability column |

The Scorecard tab benefits from a 0-100 color scale on the Score column (green→yellow→red) — Excel's built-in conditional formatting handles this directly.

**Mode C (PDF) page sequence:**
- Page 1 Cover — hero stat = composite score (0-100, large, in accent); caption = "RISK SCORE — [RATING]"; KPI row = entity typology / red flag count / information gaps / confidence
- Page 2 — Executive Summary + Disposition callout
- Page 3 — Scorecard with bar chart of weighted scores per domain
- Page 4-5 — Domain Findings (8 domains, 1-2 paragraphs each, multi-page)
- Page 6 — Red Flags (severity-tagged list)
- Page 7 — Information Gaps + Methodology + Sources
- Page 8 — Footer / Disclaimer

If the SEVERE-override applied (sanctions hit or active indictment), the cover hero is the score AND a prominent red "SEVERE — OVERRIDE" badge under the caption.

**Mode D (HTML dashboard) DATA wiring:**
- `reportType`: "ENTITY RISK ASSESSMENT"
- `accent`: `#0a84ff` (regulatory blue) is the default; switch to `#22d3ee` if the entity is a digital-asset service provider
- `kpis`: `[ {label: "Composite", value: "n/100", delta: rating}, {label: "Typology", value: entityType}, {label: "Red Flags", value: count}, {label: "Confidence", value: rating} ]`
- `navSections`: Summary · Scorecard · Domain Findings · Red Flags · Gaps · Disposition
- `scorecard`: headers `["Domain", "Score", "Weight", "Weighted", "Key driver"]`; rows are the 8 domains
- `chartConfig`: a `radar` chart with 8 axes (one per domain) and a single dataset is the iconic entity-risk visualization — instantly shows shape of risk
- Findings cards: render one finding per domain in `findings`, severity-coded
- If SEVERE-override applied: add a prominent red banner at the top of the hero (above the title) — this is non-optional, the reader must see it
""",

"breaking-news-scan": """

---

## Per-analysis customization — breaking news scan

This analysis is best delivered as **Mode D (HTML dashboard)** for a live-feel news feed the user refreshes, or **Mode C (PDF)** for a circulated briefing document. **Mode A (Word)** suits a one-off written brief. **Mode B (Excel)** is useful when running the scan repeatedly and tracking severity trends across scans.

**Mode A (Word) — Heading 1 sections in order:**
1. Scan header (date · time · domains · basis)
2. Items by Severity (Heading 2 per severity — CRITICAL, HIGH, MEDIUM, LOW; each with item + why-it-matters lines)
3. Sources (per-item citation list)
4. Information Gaps

If "Nothing breaking — quiet scan" is the result, the Word doc says exactly that in a centered callout under the header. Do not pad.

**Mode B (Excel) tabs:**

| Tab | Headers | Severity column? |
|---|---|---|
| Summary | Scan date/time · Domains · Items · CRITICAL count · HIGH count · Basis | no |
| Items | Severity · Headline · Why it matters · Source · Timestamp · Domain · `BUILDING`? | yes |
| Sources | Source · Items cited · Type | no |
| Velocity (if running repeatedly) | Item ID · First seen · Last seen · Trend · Tagged BUILDING? | by Trend |

**Mode C (PDF) page sequence:**
- Page 1 Cover — hero = CRITICAL+HIGH item count; caption = "BREAKING ITEMS THIS SCAN"; KPI row = total items / CRITICAL / HIGH / quiet-scan flag
- Page 2 — Items by Severity (single-page if few items, otherwise multi-page in severity order)
- Page 3 — Sources

For a quiet scan, Page 1 is the only page — a single line under the hero says "Nothing breaking — quiet scan", and that is the deliverable.

**Mode D (HTML dashboard) DATA wiring:**
- `reportType`: "BREAKING NEWS SCAN"
- `accent`: pick by primary domain — `#22d3ee` for crypto, `#0a84ff` for regulatory, `#f59e0b` for macro/markets
- `kpis`: `[ {label: "Total Items", value: n}, {label: "CRITICAL", value: n}, {label: "HIGH", value: n}, {label: "Basis", value: basis} ]`
- `navSections`: Summary · Items · Sources · Gaps
- Replace the default `sec-scorecard` with severity-grouped item cards
- `findings`: one entry per scan item — severity is the scan's severity, title is the headline, body is the why-it-matters line, source is the citation
- `chartConfig`: a `bar` chart of items per severity tier is the canonical visualization; if running repeatedly, a `line` chart of items-per-severity over scan-time-series is more interesting
- For a quiet scan, render a single large "QUIET SCAN" card in `sec-summary` and hide the other sections (set `display: none` via inline style on those section IDs)
""",

"alert-triage": """

---

## Per-analysis customization — alert triage

This is best delivered as **Mode A (Word)** for the official disposition memo (the typical compliance artifact) or **Mode C (PDF)** for an examiner-facing version. **Mode B (Excel)** is the right choice when batch-triaging many alerts at once. **Mode D (HTML dashboard)** is useful for a team triage queue.

**Mode A (Word) — Heading 1 sections in order:**
1. Triage header (Alert ID / Rule / Customer / Disposition — disposition prominently displayed as a colored callout)
2. Alert Summary
3. Activity vs. Expected Profile
4. Typology Assessment
5. Factors Supporting a Concern + Factors Contradicting a Concern (two-column / paired tables)
6. Disposition Rationale
7. Recommended Next Steps
8. **Disposition Memo (audit-ready)** — set in a bordered callout box, this is the section the examiner reads first
9. Information Gaps + Confidence

**Mode B (Excel) tabs:**

| Tab | Headers | Severity column? |
|---|---|---|
| Summary | Alert ID · Customer · Rule · Disposition · Confidence | the Disposition column (CLOSE green / MONITOR yellow / ESCALATE orange / REFER red) |
| Activity vs Profile | Metric · Expected · Observed · Deviation % · Flag | the Flag column |
| Typology Assessment | Typology · Consistent? · Reasoning | the Consistent? column |
| Factors For | # · Factor · Evidence · Weight | by Weight |
| Factors Against | # · Factor · Evidence · Weight | by Weight |
| Disposition Memo | Section · Text | no |

For batch triage, structure the workbook differently: Summary becomes a list of all alerts with one row per alert and Disposition column, and each tab becomes one alert-specific tab — or use one tab and the user filters by Alert ID.

**Mode C (PDF) page sequence:**
- Page 1 Cover — hero stat = disposition word (CLOSE / MONITOR / ESCALATE / REFER) in disposition color; caption = "ALERT [ID] DISPOSITION"; KPI row = customer / typology fits / for/against factor counts / confidence
- Page 2 — Alert Summary + Activity vs Expected
- Page 3 — Typology Assessment
- Page 4 — Factors (two-column for-vs-against)
- Page 5 — Disposition Memo (full-page callout — this is the page the examiner reads)
- Page 6 — Methodology + Information Gaps

**Mode D (HTML dashboard) DATA wiring:**
- `reportType`: "TRANSACTION ALERT TRIAGE"
- `accent`: `#0a84ff` (regulatory blue); the disposition badge in the hero uses the disposition color (CLOSE green, MONITOR yellow, ESCALATE orange, REFER red)
- `kpis`: `[ {label: "Disposition", value: dispositionWord}, {label: "Typology Fit", value: "MATCH"/"NO-MATCH"}, {label: "Factors For", value: n}, {label: "Factors Against", value: n} ]`
- `navSections`: Summary · Activity vs Expected · Typology · Factors · Disposition Memo · Gaps
- Render the Disposition Memo as a single large card with extra visual weight (larger padding, top-position) — it must be the first thing the reader sees after the hero
- Findings cards: one per factor (for-vs-against), severity used to color-code factor weight
- `chartConfig`: a horizontal `bar` chart showing observed vs expected for the deviating metric is the most useful chart for a triage dashboard — visually anchors the disposition
""",
}


def transform(text: str, customization: str) -> str:
    """Append (or replace previous) appendix + per-file customization."""
    # If sentinel already present, truncate everything from sentinel onward
    m = re.search(r"^---\s*\n\s*\n## Render as a formatted deliverable", text, flags=re.MULTILINE)
    if m:
        text = text[:m.start()].rstrip() + "\n"
    else:
        # ensure exactly one trailing newline before we append
        text = text.rstrip() + "\n"
    return text + UNIVERSAL.rstrip() + customization.rstrip() + "\n"


def main():
    standalone_dir = ROOT / "standalone"
    if not standalone_dir.exists():
        print(f"FATAL: {standalone_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    changed, missing = 0, 0
    for f in sorted(standalone_dir.glob("*.md")):
        if f.name == "README.md":
            continue
        stem = f.stem
        if stem not in PER_FILE:
            print(f"  MISSING customization for {f.name}")
            missing += 1
            continue
        original = f.read_text()
        new = transform(original, PER_FILE[stem])
        f.write_text(new)
        changed += 1
        print(f"  updated: {f.name}  ({len(original.splitlines())} -> {len(new.splitlines())} lines)")
    print(f"\nDone. {changed} updated, {missing} missing per-file customizations.")


if __name__ == "__main__":
    main()
