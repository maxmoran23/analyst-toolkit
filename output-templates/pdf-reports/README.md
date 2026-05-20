# PDF Narrative Report Template

A multi-page PDF narrative report: a designed, dark-background, amber-accented
document that turns analytical findings into a polished narrative deliverable.
Hero statistics, vector data visualizations, structured tables, comparison
grids, and long-form prose — in one cohesive visual system.

This is not a plain text PDF. It is a designed report with full-bleed dark
backgrounds, an amber/gold accent, ALL CAPS section headers, running page
headers, and a set of reusable page types. Use it for formal, report-style
deliverables you intend to hand to a stakeholder.

| File                            | What it is                                       |
|---------------------------------|--------------------------------------------------|
| `narrative-report-template.html`| HTML template — convert to PDF                   |
| `generate_report.py`            | Pure-Python (ReportLab) PDF generator            |
| `narrative-report-guide.md`     | Full usage guide — design system, page types     |

## The two generation paths

The report can be produced two ways. They share the same design system, so the
output looks the same; pick the path that fits your workflow.

| Path                | Best when                                                  |
|---------------------|------------------------------------------------------------|
| HTML to PDF         | You want the richest layout control and SVG charts, and have a browser or `wkhtmltopdf` available |
| `generate_report.py`| You want a scriptable, dependency-light generator with no headless browser, or you are building reports programmatically |

### HTML to PDF

Edit `narrative-report-template.html`, replace the `{{PLACEHOLDER}}` tokens with
your content, then convert:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --print-to-pdf=report.pdf --no-margins report.html
```

Or open the HTML in a browser and use Print → Save as PDF.

### generate_report.py

```bash
pip3 install reportlab
python3 generate_report.py --output report.pdf
```

## What generate_report.py does

`generate_report.py` is a self-contained PDF generator built on
[ReportLab](https://www.reportlab.com/), a pure-Python PDF engine. It needs no
headless browser and no external services — just the `reportlab` package.

The script is organized in three layers:

1. **`Theme`** — a class of design tokens (colors, fonts, page geometry) that
   define the visual system. Change a value here and it propagates everywhere.
2. **`NarrativeDashboardReport`** — the report builder. It exposes:
   - Low-level drawing helpers (text, wrapped text, accent lines, cards, tables)
   - Chart helpers that draw vector visualizations directly onto the PDF
     canvas — a `_draw_bell_curve()` distribution chart and a
     `_draw_radar_chart()` spider chart, both amber-on-dark
   - Page builders — one method per page type: `add_cover_page()`,
     `add_distribution_page()`, `add_radar_page()`, `add_evidence_page()`,
     `add_comparison_page()`, `add_narrative_page()`, `add_trait_page()`,
     `add_methodology_page()`, `add_footer_page()`
   - `generate()` — finalizes and writes the PDF
3. **`demo()`** — a worked example that builds a full report exercising every
   page type. Running the script with no arguments produces this demo, which is
   the quickest way to see the design system on a real page.

### Run the demo

```bash
pip3 install reportlab
python3 generate_report.py
```

This writes a demo PDF and prints its path and page count. Open it to see the
cover, distribution, radar, evidence, narrative, and footer pages rendered.

### Build your own report programmatically

Import the builder and assemble pages in the order you want:

```python
from generate_report import NarrativeDashboardReport

report = NarrativeDashboardReport(
    filename='report.pdf',
    title='Quarterly Review',
    subject='Operations',
    date='Q3 2026',
    descriptor='Performance Assessment',
)

report.add_cover_page(
    hero_number='87.3',
    hero_label='Composite Performance Score',
    hero_sublabel='Range: 82-91 | Prior: 84.1',
    kpis=[('Top 6%', 'Population rank'),
          ('94th', 'Percentile'),
          ('+3.2', 'vs. prior period')],
    methodology_text='This report synthesizes data from multiple sources ...',
)

# ... add more pages: add_distribution_page(), add_radar_page(), etc.

report.generate()
```

Each `add_*` method's signature documents the content it expects. The usage
guide (`narrative-report-guide.md`) describes every page type in detail.

## Using these templates with an AI assistant

Both paths are well suited to being driven by an AI assistant: the templates
supply the design system and structure; the assistant supplies the content.

- Paste `narrative-report-template.html` (or point at `generate_report.py`)
  into the conversation, provide your data, and ask the assistant to produce a
  finished report — choosing the page types that fit the data, writing the
  narrative prose, and filling in the tables and chart values.
- Give the assistant `narrative-report-guide.md` so it follows the design
  system precisely — the dark background, the amber accent, the page-type
  conventions, the methodology section at the end.

## Dependencies

- **HTML to PDF path**: a Chromium-based browser or `wkhtmltopdf`.
- **`generate_report.py` path**: Python 3 and the `reportlab` package
  (`pip3 install reportlab`).

## Notes

- The templates ship with neutral demo content so the raw files and the demo
  PDF preview cleanly before you populate them.
- Page size is US Letter (8.5 x 11 in). Adjust the page geometry in the
  `Theme` class (Python) or the `@page` rule and `.page` dimensions (HTML) for
  other sizes.
