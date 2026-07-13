# Dashboard Templates

Three self-contained, interactive HTML dashboard templates for analytical work.
All three open directly in a browser, need no build step, and are designed to be
populated with your own data — by hand or, faster, by an AI assistant.

| File                          | What it is                                          |
|-------------------------------|-----------------------------------------------------|
| `dashboard-big.html`          | Heavyweight, exhaustive, 10–20 section dashboard     |
| `dashboard-big-guide.md`      | Full usage guide for `dashboard-big.html`           |
| `deep-dive-dashboard.html`    | Lightweight, three-tab, single-topic dashboard      |
| `deep-dive-guide.md`          | Full usage guide for `deep-dive-dashboard.html`     |
| `adaptive-dashboard.html`     | Domain-neutral shell whose cards, charts, lists, and searchable tables are derived from arbitrary supplied data |

## Previews

**`dashboard-big.html`**, populated into a finished entity risk assessment — the
heavyweight template's payoff is depth, ten-to-twenty interlocking sections:

![dashboard-big.html populated into an entity risk assessment](../../samples/previews/entity-risk-preview.png)

**`deep-dive-dashboard.html`**, the lightweight three-tab template as shipped —
KPI cards, charts, and tables, ready to populate in minutes:

![deep-dive-dashboard.html template](previews/deep-dive-dashboard-preview.png)

The adaptive template ships with three domain-neutral populated samples and their
raw fixtures: a [24-month series](../../samples/dashboards/24-month-time-series-sample.html)
([fixture](../../samples/dashboards/fixtures/24-month-time-series.json)), a
[four-measure categorical table](../../samples/dashboards/four-column-categories-sample.html)
([fixture](../../samples/dashboards/fixtures/four-column-categories.json)), and a
[mixed-material input](../../samples/dashboards/mixed-material-sample.html)
([fixture](../../samples/dashboards/fixtures/mixed-material.json)).

*The legacy previews are 1440×900. Additional populated samples are in
[`samples/`](../../samples/).*

## Which template to use

The templates cover a weight spectrum plus a data-derived option. Pick by the
depth and structure the material actually warrants.

| Dimension          | `dashboard-big.html` | `deep-dive-dashboard.html` | `adaptive-dashboard.html` |
|--------------------|----------------------|----------------------------|---------------------------|
| Weight             | Heavyweight | Lightweight | Data-derived |
| Sections           | 10–20+ | 3 tabs | Inferred from the supplied structures |
| File size          | ~40 KB | ~17 KB | ~27 KB before embedded data |
| Build time         | Substantial | Minutes to populate | Quick once arbitrary input is normalized |
| Dependencies       | Chart.js + html2canvas (CDN) | Chart.js only (CDN) | Chart.js 4.4.1 only (CDN); tables and ledger remain usable without it |
| Theme              | Dark + light toggle | Dark only | Dark + light toggle |
| Interactivity      | Modals, search, sortable/paginated tables, carousels, export | Tab switching, charts | Sticky navigation, charts, table search and sort |
| Best for           | A deep, permanent analytical reference | A focused single-topic investigation | CSV, JSON, tables, lists, prose, or mixed material with no required input schema |

**Use `dashboard-big.html`** when the topic deserves a deep, lasting,
multi-section analytical experience — a market review, portfolio analysis,
competitive intelligence, a regulatory landscape, a research compilation.

**Use `deep-dive-dashboard.html`** when you want a fast, clean answer to a
focused question and don't need the full treatment — variance analysis, a
quality investigation, a correlation study, a calibration check.

**Use `adaptive-dashboard.html`** when the source shape should determine the
layout. It retains every leaf value in a source ledger and routes anything it
cannot safely normalize to an explicit Unparsed material section.

When in doubt, start with the deep-dive. It is far cheaper to produce, and you
can always escalate to the heavyweight template if the topic grows.

## How to use these templates with an AI assistant

All three templates are built to be filled in by a capable AI assistant. The
templates supply the structure, styling, and interaction logic; the assistant
supplies the content and wires up the data.

A workflow that works well:

1. **Pick the template** using the table above.
2. **Paste the raw template file** into the conversation, or point the assistant
   at the file path.
3. **Provide your data** — paste a CSV or JSON, attach a file, or describe the
   dataset and the analysis you want.
4. **Ask the assistant to populate the template.** For example:

   > Here is the `dashboard-big.html` template and a CSV of quarterly sales
   > data. Populate the template into a finished dashboard: scope 12–15
   > sections appropriate to this data, fill in the hero stats, write the
   > render functions, wire up the charts, and set the accent color to the
   > finance amber. Keep it a single self-contained file.

5. **Open the result in a browser** and iterate. Ask for added sections,
   different charts, copy edits, or a different accent color.

Tips:

- Tell the assistant the **topic and accent color** up front so the dashboard is
  themed coherently. `dashboard-big.html` re-themes from a single `--accent`
  CSS variable.
- For `dashboard-big.html`, tell the assistant **which sections** you want, or
  let it scope them from your data — the section blueprint in
  `dashboard-big-guide.md` is the menu.
- Ask for the data to be **embedded directly** in the file (`const DATA = …`)
  if you want a single portable file with no separate data file.
- The guides (`dashboard-big-guide.md`, `deep-dive-guide.md`) document every
  component, customization point, and design token — give them to the assistant
  if you want it to follow the conventions precisely.

## Notes

- All three files are standalone. Opening them straight from disk (`file://`) works.
- If you wire `dashboard-big.html` to load data via `fetch()` from a separate
  JSON file, serve the folder over a local HTTP server so the browser allows
  the request.
- The templates ship with neutral placeholder content and tokens so the raw
  files preview cleanly before you populate them.
