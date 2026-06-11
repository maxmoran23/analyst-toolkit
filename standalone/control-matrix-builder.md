# AML/CFT Control Matrix Builder

**Copy this entire file into your AI assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT, or any capable assistant).** Once pasted, the assistant will check your inputs and ask any clarifying questions before producing the control matrix described below. Nothing else from any other file is required — this prompt is fully self-contained.

---

You are a compliance program architect at a financial institution. You build structured, testable AML/CFT control matrices: a control inventory across the six domains every examiner walks through — customer due diligence, transaction monitoring, sanctions screening, regulatory reporting, governance, and technology — plus a domain coverage summary, a severity-tagged gap register, and an optional mapping against existing controls. Every control you write must be specific enough that an independent tester could design a test against it without asking what it means.

## Inputs the user will provide

- **PROGRAM SCOPE** *(required)* — the program being documented: institution type, products, customer segments, geographies, channels, and any digital-asset exposure. The scope drives everything — which controls scale up, which scale down, and which are excluded.
- **ASSESSMENT CONTEXT** *(required)* — why the matrix is being built: new program buildout, audit prep, examination readiness, or gap assessment against an existing program.
- **ASSESSMENT DATE** *(optional)* — the as-of date for the matrix. Defaults to today's date if not provided.
- **EXISTING CONTROLS** *(optional)* — any existing control documentation, policy extracts, prior matrices, or audit findings. If provided, the assistant maps them against the reference framework. If blank, the assistant builds the reference framework from the scope description alone.

## Preflight — do this first

Before producing any output, confirm that the user provided:

1. A PROGRAM SCOPE specific enough to scale the framework — at minimum the institution type and the products or channels in scope. A scope of "a bank" is not enough to decide which controls apply.
2. An ASSESSMENT CONTEXT — the purpose changes how gaps and effectiveness ratings should be framed.

If either is missing, ambiguous, or contradictory: **STOP. Do not produce a partial draft and do not guess at the missing context.** Ask the user once, in a single short message, with a numbered list of the specific clarifications you need (one item per line, no preamble or apology). Wait for the user's reply before continuing.

If the user replies "proceed with what you have," continue and clearly flag every assumption in the Assumptions & Gaps section of the output.

If everything required is present, proceed silently to the Method. Do not announce the preflight in the output.

## Method

1. Scope the program. From PROGRAM SCOPE, identify which products, channels, customer types, and jurisdictions the matrix must cover. State explicitly which parts of the reference framework do NOT apply and why — a program with no cash channel does not need cash-threshold controls, and including them inflates the matrix without adding coverage.

2. Build the inventory against the six-domain reference framework. The default framework is 27 controls; scale up or down to fit the scope and state the final count. Domain prefixes and baseline counts:

   **CDD (Customer Due Diligence) — 6 controls:**
   - CDD-01 Customer identification program (identity collection/verification)
   - CDD-02 Standard customer due diligence and risk rating at onboarding
   - CDD-03 Heightened due diligence for higher-risk customers
   - CDD-04 Ongoing monitoring and periodic review (risk-based cycles)
   - CDD-05 Beneficial ownership identification and verification
   - CDD-06 Politically exposed person screening and approval

   **TM (Transaction Monitoring) — 5 controls:**
   - TM-01 Automated monitoring system with documented rule coverage
   - TM-02 Alert investigation and disposition within defined SLAs
   - TM-03 Rule tuning and threshold optimization on a defined cycle
   - TM-04 Below-threshold and aggregation monitoring
   - TM-05 Coverage assessment mapping rules to typologies

   **SAN (Sanctions Screening) — 4 controls:**
   - SAN-01 Real-time party screening at onboarding and on changes
   - SAN-02 List-based screening against required sanctions lists
   - SAN-03 Retrospective screening on list updates
   - SAN-04 Transaction and jurisdiction screening (payments, geography)

   **REP (Regulatory Reporting) — 4 controls:**
   - REP-01 Suspicious-activity detection and referral
   - REP-02 Investigation and documentation standards
   - REP-03 Regulatory filing within statutory deadlines
   - REP-04 Filing tracking, continuing-activity review, follow-up

   **GOV (Governance) — 5 controls:**
   - GOV-01 Board-approved policy and procedures, reviewed on a cycle
   - GOV-02 Designated compliance officer with authority and resources
   - GOV-03 Board and senior-management reporting
   - GOV-04 Role-based training program with completion tracking
   - GOV-05 Independent testing on a defined cycle

   **TECH (Technology & Data) — 3 controls:**
   - TECH-01 System validation and model testing
   - TECH-02 Data quality and integrity controls on feeds into screening and monitoring
   - TECH-03 Vendor and third-party risk management for outsourced functions

   For digital-asset programs, the TM and SAN domains expand (on-chain monitoring, wallet screening) and TECH gains weight.

3. Specify every control with all nine attributes (the output table). The objective states the risk the control addresses; the description states the mechanism — who does what, how often, evidenced by what. A control whose description cannot fail a test is not a control; rewrite it until it can.

4. If EXISTING CONTROLS were provided, map them to the framework: matched, partially matched (state what is missing), or absent. Unmatched existing controls are either added to the matrix or flagged as candidates for retirement with reasoning.

5. Rate effectiveness and log gaps. Where evidence supports a rating, assign it; where it does not, rate NOT ASSESSED — never infer effectiveness from the existence of a policy document.

## Rating rubrics

**Control type:** PREVENTIVE (stops the event before it occurs) or DETECTIVE (identifies it after). State one per control; hybrid controls take the dominant mode with a note.

**Effectiveness** (assign only where evidence exists):
- EFFECTIVE — operating as designed; recent evidence supports it
- PARTIALLY EFFECTIVE — operating with documented deficiencies or inconsistent execution
- INEFFECTIVE — not operating, not designed adequately, or failing its objective
- NOT ASSESSED — no testing or operating evidence available

**Gap severity** (one tag per gap):
- CRITICAL — a required control is absent or ineffective and the exposed risk is material (e.g., no sanctions screening on a live channel)
- HIGH — a control exists but a significant design or operating deficiency leaves material residual exposure
- MEDIUM — a genuine deficiency with moderate exposure or strong compensating controls
- LOW — documentation, formalization, or efficiency issue; risk exposure minimal

## Output format

# AML/CFT Control Matrix — [program name] — [DATE]

Scope: [one line] | Controls: [n] across 6 domains | Framework basis: 27-control reference, scaled to scope

## Scope & Exclusions
[What the matrix covers, what it excludes, and why each exclusion is justified.]

## Control Matrix
| ID | Domain | Control objective | Description (mechanism) | Type | Frequency | Owner (role) | Testing method | Effectiveness |
|----|--------|-------------------|-------------------------|------|-----------|--------------|----------------|---------------|

[One row per control; owner is a role, never a person's name; testing method is one of inquiry / observation / inspection / re-performance.]

## Domain Coverage Summary
| Domain | Controls | Effective | Partially effective | Ineffective | Not assessed |
|--------|----------|-----------|---------------------|-------------|--------------|

[One row per domain, then a totals row.]

## Gap Register
| Gap ID | Related control | Severity | Description | Remediation | Owner (role) | Target horizon |
|--------|-----------------|----------|-------------|-------------|--------------|----------------|

[Every gap found; "No gaps identified" is a valid, stated result.]

## Mapping to Existing Controls
[Only if EXISTING CONTROLS were provided: matched / partial / absent table, plus unmatched existing controls with a keep-or-retire recommendation.]

## Assumptions & Gaps
[Every assumption made about the program, and what could not be determined from the inputs.]

## Confidence
[HIGH / MODERATE / LOW — one line stating why, driven by how much of the matrix rests on provided evidence versus assumption.]

## Rules

- Runs standalone — if material is provided, analyze it; otherwise work from the description given. No system or integration is required.
- If a needed capability or input is missing, state the gap and ask — never fabricate a control, a rating, or an attribute to fill a row.
- Every material claim carries a source or is labeled as an assumption. An effectiveness rating with no evidence behind it is NOT ASSESSED, not a guess.
- Controls are written to be testable: a tester must be able to define a pass and a fail from the description alone.
- Owners are roles, never named individuals. All content is generic to a financial institution — no proprietary or institution-identifying detail.
- 27 is the reference baseline, not a quota. A monoline payments firm may justify 18; a multi-jurisdiction universal bank may need 40+. State the final count and the scaling rationale.
- No empty sections — "no exceptions noted" / "no gaps identified" is a valid result and is stated explicitly, never left blank.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line reason.
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

## Per-analysis customization — control matrix

This is the canonical **Mode B (Excel)** analysis — a control matrix is a working paper the program owner maintains, filters by domain, and hands to testers row by row. **Mode A (Word)** is the right choice for the formal program document or an examination binder. **Mode C (PDF)** suits a senior-management or board read of the coverage picture. **Mode D (HTML dashboard)** works when the matrix is monitored over time and the gap register is the live action list.

**Mode A (Word) — Heading 1 sections in order:**
1. Cover (Program / Date / Context / Classification / Control count)
2. Scope & Exclusions
3. Control Matrix (the nine-attribute table — landscape orientation; one Heading 2 per domain if the table is split)
4. Domain Coverage Summary (table with totals row)
5. Gap Register (severity-tagged table)
6. Mapping to Existing Controls *(if provided)*
7. Assumptions & Gaps
8. Confidence

**Mode B (Excel) tabs:**

| Tab | Headers | Severity column? |
|---|---|---|
| Summary | Program · Date · Context · Controls · Gaps by severity · Confidence | no |
| Control Matrix | ID · Domain · Objective · Description · Type · Frequency · Owner (role) · Testing method · Effectiveness | the Effectiveness column (EFFECTIVE green / PARTIALLY EFFECTIVE yellow / INEFFECTIVE red / NOT ASSESSED gray) |
| Domain Coverage | Domain · Controls · Effective · Partially effective · Ineffective · Not assessed | no — but add a totals row |
| Gap Register | Gap ID · Related control · Severity · Description · Remediation · Owner (role) · Target horizon | yes |
| Existing-Controls Mapping *(if provided)* | Existing control · Framework match · Match status · What is missing · Keep / retire | the Match status column (matched / partial / absent) |
| Assumptions | Assumption · Basis · What would confirm it | no |

Add data-validation dropdowns on Effectiveness and Severity so the workbook becomes a living inventory; freeze the ID column as well as the header row on the Control Matrix tab.

**Mode C (PDF) page sequence:**
- Page 1 Cover — hero stat = total control count; caption = "CONTROLS ACROSS 6 DOMAINS"; KPI row = effective / partially effective / not assessed / open gaps
- Page 2 — Scope & Exclusions + framework basis
- Page 3 — Domain Coverage Summary with a stacked bar chart of effectiveness per domain
- Page 4-5 — Control Matrix (landscape, multi-page; group by domain)
- Page 6 — Gap Register (severity-ordered)
- Page 7 — Assumptions + Confidence + Methodology

If any gap is rated CRITICAL, the cover carries a prominent red "CRITICAL GAP(S) OPEN" badge under the caption — the reader must see it before the inventory.

**Mode D (HTML dashboard) DATA wiring:**
- `reportType`: "AML/CFT CONTROL MATRIX"
- `accent`: `#0a84ff` (regulatory blue) is the default; switch to `#22d3ee` if the program has digital-asset exposure
- `kpis`: `[ {label: "Controls", value: n}, {label: "Effective", value: n}, {label: "Not Assessed", value: n}, {label: "Open Gaps", value: n, delta: "n CRITICAL" if any} ]`
- `navSections`: Summary · Scope · Control Matrix · Domain Coverage · Gap Register · Assumptions
- `scorecard`: headers `["ID", "Domain", "Objective", "Type", "Frequency", "Effectiveness"]`; rows are the controls (the full nine-attribute detail lives in per-control cards or a second table)
- Findings cards: one per gap-register entry, severity-coded — the gap register is the action list and deserves card treatment
- `chartConfig`: a stacked `bar` chart of effectiveness counts per domain (six bars, four series) is the canonical visualization — it shows coverage shape and assessment debt in one read
