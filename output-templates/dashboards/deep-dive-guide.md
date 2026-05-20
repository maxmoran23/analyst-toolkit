# Deep-Dive Dashboard — Usage Guide

A guide to `deep-dive-dashboard.html`: a lightweight, self-contained,
interactive HTML report for ad-hoc analytical deep-dives. Open it in a browser,
drop in your data, and you have a clean three-tab dashboard with charts, tables,
and KPI cards — no build step, no dependencies beyond one CDN script.

![deep-dive-dashboard.html template — three tabs, KPI cards, charts](previews/deep-dive-dashboard-preview.png)

*Above: the `deep-dive-dashboard.html` template as shipped — three tabs, KPI cards, and charts, ready to populate.*

## What it is

A reusable HTML template for one-off investigations that don't warrant the
full heavyweight treatment. Faster to produce than `dashboard-big.html`, lighter
on the page, and focused on a single topic. Reach for it when the answer is
"I want to look at this more closely" rather than "I want an exhaustive,
permanent dashboard."

For deep, multi-section analytical experiences, use `dashboard-big.html`
instead. See the directory `README.md` for the heavyweight-vs-lightweight call.

## Typical use cases

- Performance analysis across regimes or segments
- Variance analysis (expected vs. actual)
- A quality deep-dive (why did metric X degrade?)
- Correlation analysis between several series
- A pressure or event timeline analysis
- Accuracy / calibration studies
- Any single-topic "look at this more closely" question

## Architecture

- Single-file HTML, fully self-contained
- Chart.js 4.x via CDN (the only external dependency)
- Dark theme, responsive, print-friendly
- Three-tab layout: Overview / Trends / Details
- KPI strip at the top (4–6 cards with deltas)
- No build step

The file works when opened directly from disk (`file://`).

## How to use the template

The fastest path is to hand the template and your data to an AI assistant and
ask it to populate the file. See the directory `README.md` for that workflow.

To work with it directly:

1. Open `deep-dive-dashboard.html` in an editor.
2. Replace the placeholder tokens — `TITLE_PLACEHOLDER`, `DATE_PLACEHOLDER`,
   `SOURCE_PLACEHOLDER`, `DATE_TIMESTAMP`.
3. Inject your data into the JavaScript data objects (`primaryData`,
   `secondaryData`, `trend1Data`, etc.).
4. Add or remove chart `<canvas>` elements and table rows to fit the analysis.
5. Open the file in a browser to review.

## Customization points

### KPI strip

```html
<div class="kpi-card">
  <div class="kpi-label">LABEL</div>
  <div class="kpi-value" style="color: var(--accent-indigo)">VALUE</div>
  <div class="kpi-delta kpi-up">+X.X%</div>  <!-- kpi-up, kpi-down, kpi-flat -->
</div>
```

Add or remove cards as needed. Use `kpi-up` (green), `kpi-down` (red), or
`kpi-flat` (gray) for delta styling.

### Charts

Add a `<canvas>` element and render it with `renderChart()`:

```javascript
// In HTML: <canvas id="myChart"></canvas>
renderChart('myChart', 'line', {
  labels: ['Mon', 'Tue', 'Wed'],
  datasets: [{
    label: 'My Data',
    data: [10, 20, 15],
    borderColor: CHART_COLORS.indigo,
    tension: 0.3
  }]
});
```

Available colors: `indigo`, `cyan`, `green`, `amber`, `red`, `purple`, `blue`.

If a chart's `labels` array is empty, `renderChart()` renders a tasteful
"No data available" placeholder instead of an empty canvas.

### Tables

```html
<table class="data-table">
  <thead><tr><th>Col1</th><th>Col2</th></tr></thead>
  <tbody>
    <tr><td>Data</td><td><span class="severity severity-high">HIGH</span></td></tr>
  </tbody>
</table>
```

Severity pills: `severity-critical`, `severity-high`, `severity-medium`,
`severity-low`, `severity-info`.

### Metric rows (key-value pairs)

```html
<div class="metric-row">
  <span class="metric-label">Label</span>
  <span class="metric-value">Value</span>
</div>
```

### Tabs

Add or remove tabs by editing the topbar buttons and creating matching
`tab-panel` divs:

```html
<button class="topbar-tab" onclick="showTab('newtab')">New Tab</button>
<!-- ... -->
<div id="tab-newtab" class="tab-panel">Content</div>
```

### Grid layouts

- `grid-2` — two columns
- `grid-3` — three columns
- `grid-full` — span the full width within any grid

## Suggested file naming

```
{topic}-deep-dive-{YYYY-MM-DD}.html
```

For throwaway analysis, save it anywhere temporary. For anything worth keeping,
name it by topic and date.
