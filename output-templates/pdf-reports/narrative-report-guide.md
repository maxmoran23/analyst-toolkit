# PDF Narrative Report — Usage Guide

A guide to the multi-page PDF narrative report: a dark-background,
amber-accented, designed document that turns analytical findings into a
polished narrative — hero statistics, vector charts, structured tables,
comparison grids, and long-form prose, in one cohesive visual system.

This directory provides two ways to generate the report:

- `narrative-report-template.html` — an HTML template, converted to PDF
- `generate_report.py` — a pure-Python (ReportLab) generator

## What it is

This is **not** a plain text PDF. It is a designed report with:

- A full-bleed dark background on every page — no white pages
- An amber/gold accent for hero numbers, chart elements, and highlights
- Vector-rendered data visualizations (bell curves, radar charts)
- Typographic hierarchy with ALL CAPS section headers and letter spacing
- Running page headers carrying the report metadata
- A set of reusable page types that map to different content needs

Use it when you want a formal, report-style deliverable from a dataset, a
dashboard, or an analysis — something to hand to a stakeholder.

## Design system

### Color palette

```
BACKGROUND_PRIMARY   #111827   Deep charcoal — page background, full-bleed
BACKGROUND_CARD      #1a1f35   Slightly lighter — card/table backgrounds
BACKGROUND_CALLOUT   #1e2440   Callout boxes, special sections
ACCENT_AMBER         #d4a574   Primary accent — hero numbers, chart fills
ACCENT_AMBER_LIGHT   #e8c9a0   Light amber — secondary accents
TEXT_PRIMARY         #ffffff   White — headings, hero stats
TEXT_BODY            #c8ccd4   Light gray — body text, descriptions
TEXT_SECONDARY       #8b92a0   Muted gray — captions, metadata, page headers
TEXT_MUTED           #5a6070   Very muted — disclaimers, footnotes
BORDER_SUBTLE        #2a3045   Table borders, divider lines
SEVERITY_HIGH        #e05555   Red — warnings, risks
SEVERITY_POSITIVE    #4ade80   Green — strengths, positives
```

### Typography

```
FONT_FAMILY     Helvetica, Arial, sans-serif
HERO_NUMBER     Helvetica-Bold, 72–96pt, amber
SECTION_TITLE   Helvetica-Bold, 18–20pt, white, ALL CAPS, letter-spacing 3px
BODY_TEXT       Helvetica, 10–11pt, light gray, line-height 1.5
KPI_NUMBER      Helvetica-Bold, 28–36pt, white or amber
TABLE_HEADER    Helvetica-Bold, 9–10pt, muted gray, ALL CAPS
PAGE_HEADER     Helvetica, 8pt, muted
DISCLAIMER      Helvetica, 7–8pt, muted
```

### Page layout

```
PAGE_SIZE       Letter (612 x 792 pt / 8.5 x 11 in)
MARGINS         54pt top/bottom, 60pt left/right
CONTENT_WIDTH   ~492pt
SECTION_SPACING 36pt between major sections
```

### Running page header

Every page except the cover carries a running header:

```
{Report Title} — {Subject Name} — {Date} | Page {N}
```

Style: 8pt, muted, left-aligned at the top margin.

## Page types

A report uses a selection of these reusable page types, adapted to the content.
Not every report needs every type — choose what fits the data.

| # | Page type                  | Contains                                              |
|---|----------------------------|-------------------------------------------------------|
| 1 | Cover / Hero               | Title, one massive hero stat, KPI row, methodology    |
| 2 | Distribution / Positioning | Bell curve with the subject marked, comparison cards  |
| 3 | Radar / Profile            | Multi-axis radar chart, legend, profile-shape analysis|
| 4 | Evidence Table             | Source/weight/range/confidence table, narrative depth |
| 5 | Comparison Grid            | Side-by-side table of comparable entities             |
| 6 | Narrative Analysis         | Long-form prose, subsections, optional callout box    |
| 7 | Trait / Matrix             | Two-column attribute table (strength vs. risk)        |
| 8 | Methodology                | How conclusions were reached, what would change them  |
| 9 | Footer / Disclaimer         | Generated date, sources, usage restrictions           |

## Report structure

A standard narrative report follows this flow:

```
1. Cover / Hero            — The headline finding + key stats
2. Distribution            — Where the subject sits in context
3. Radar / Profile         — Component breakdown
4. Evidence Table          — What the analysis is built on
5. Comparison Grid         — Benchmarks and parallels
6. Narrative Analysis      — Deep-dive analytical prose (1–3 pages)
7. Trait / Matrix          — Structured attribute breakdown
8. Methodology             — How conclusions were reached
9. Footer / Disclaimer     — Sources, caveats
```

Adapt the flow to the content. For example:

- A **performance report**: win-rate hero stat → P&L distribution curve →
  segment-by-segment radar → performance table → peer comparison grid →
  variance discussion → data-sources methodology.
- A **regulatory report**: total actions this quarter → actions by jurisdiction
  → key enforcement cases table → agency comparison grid → trend analysis →
  methodology.

## Generation methods

### Method 1 — HTML to PDF

Edit `narrative-report-template.html`, replacing the `{{PLACEHOLDER}}` tokens,
then convert to PDF:

```bash
# Chrome headless print-to-PDF
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --print-to-pdf=report.pdf --no-margins report.html

# Or wkhtmltopdf, if installed
wkhtmltopdf --page-size Letter --no-outline --enable-local-file-access \
  report.html report.pdf

# Or open report.html in a browser and use Print -> Save as PDF
```

This method gives the richest output — full CSS layout control, SVG charts.

### Method 2 — ReportLab (Python)

Use `generate_report.py`. ReportLab is a pure-Python PDF engine — no headless
browser required.

```bash
pip3 install reportlab
python3 generate_report.py --output report.pdf
```

Run with no arguments to produce a demo report exercising every page type.
For programmatic use, import `NarrativeDashboardReport`, call its `add_*`
page-builder methods, then call `generate()`.

See this directory's `README.md` for more on `generate_report.py`.

## Checklist

Before delivering, verify:

- [ ] Full-bleed dark background (#111827) on every page — no white pages
- [ ] Amber accent (#d4a574) on hero numbers and chart highlights
- [ ] ALL CAPS section headers with letter spacing
- [ ] The hero stat is 72pt+ and visually dominant on page 1
- [ ] A running page header on pages 2+
- [ ] Tables use subtle borders, not heavy grid lines
- [ ] Body text is light gray (#c8ccd4), not pure white
- [ ] Helvetica font family throughout
- [ ] Generous margins and section spacing
- [ ] A methodology / disclaimer section at the end
- [ ] Charts rendered with amber fills on dark backgrounds
