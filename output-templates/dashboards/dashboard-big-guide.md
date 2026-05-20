# Dashboard BIG — Usage Guide

A guide to `dashboard-big.html`: a heavyweight, interactive, single-file HTML
dashboard template. Open it in a browser, populate it with your data, and you
have a Bloomberg-terminal-grade analytical view of a topic — no build step, no
framework, no server.

![dashboard-big.html populated into a finished entity risk assessment](../../samples/previews/entity-risk-preview.png)

*Above: `dashboard-big.html` fully populated — a finished entity risk assessment. The heavyweight template's payoff is depth; the full sample is in [`samples/`](../../samples/).*

## What it is

`dashboard-big.html` is a master template for **exhaustive** analytical
dashboards. The design intent: don't summarize — analyze every cut of the data.
Don't build four cards — build fifteen-plus sections. One dashboard that
replaces what would otherwise be a stack of separate reports.

Use it for any topic that deserves a deep, multi-section, interactive treatment:
market reviews, portfolio analysis, competitive intelligence, a regulatory
landscape, personal analytics, research compilations — anything explored from
every angle.

For lighter, one-off investigations, use the `deep-dive-dashboard.html` template
instead. See the directory `README.md` for the heavyweight-vs-lightweight call.

## Architecture

Single-file HTML. No build step. No framework. Two CDN dependencies only:

- `chart.js@4.4.1` — all chart visualizations
- `html2canvas@1.4.1` — section/full-page export to PNG

All CSS is inline `<style>`. All JS is inline `<script>`. Data is either:

- Embedded directly as `const DATA = { ... }`, or
- Loaded from a JSON file via `fetch()` at runtime

The file works when opened directly from disk (`file://`). For `fetch()`-based
data loading, serve the folder over a local HTTP server.

## Quality bar

Every Dashboard BIG should hit these. They are what separate this format from a
generic chart page.

### Structure

1. **10–20+ distinct sections** — each a different analytical angle
2. **Hero section** — title, subtitle, summary badge, 5–6 headline stat chips
3. **Sticky navigation bar** — scroll-to-section buttons with active highlighting
4. **KPI strips** at section tops — 4–6 metric cards with labels, values, deltas
5. **Multiple visualization types** — ranked lists, tables, charts (line/bar/
   donut/radar), heatmaps, progress bars, pill badges, timeline cards
6. **Modal drill-downs** — click an entity to open a detail view
7. **Global search** — real-time filtering across the data
8. **Data browser** — a full table with sort, filter, and pagination
9. **Tab systems** within sections for sub-views
10. **Milestones / achievements** — tiered progression (bronze → mythic)
11. **Footer** with generation metadata and source attribution
12. **Export FAB** — floating button for section-level and full-page export

### Visual

1. Dark mode default, with a light mode toggle
2. Animated liquid background (gradient blobs, subtle motion)
3. Glassmorphism cards — backdrop blur, subtle borders, hover lift
4. Color-coded severity/status system (red/amber/cyan/green/purple/indigo)
5. Alternating subtle section-level gradient backgrounds
6. Scroll-triggered fade-in animations via `IntersectionObserver`
7. Responsive grid (5 → 3 → 2 → 1 column breakpoints)
8. Print stylesheet that preserves the dark theme
9. Custom scrollbar styling
10. Accent-colored left borders on cards for categorization

### Interaction

1. Chart.js 4.x for all charts
2. Sortable tables (click column headers)
3. Filterable data (dropdowns, search inputs, range sliders)
4. Carousel navigation with arrow buttons
5. Modal system for detail views
6. Tab switching
7. Pagination for large tables (50 rows/page)
8. Debounced real-time search

## How to use the template

The fastest path is to hand the template and your data to an AI assistant and
ask it to populate the file. See the directory `README.md` for that workflow.

To work with it directly:

1. **Scope** — identify the topic and list 12–20 sections that apply (see the
   section blueprint below).
2. **Data** — determine what data you have (JSON, CSV, an API, manual entry).
3. **Sections** — keep, drop, or duplicate the `<section>` blocks in the HTML so
   the structure matches your scope. Each section follows one pattern:
   ```html
   <section class="section section-gradient-N" id="sec-{id}">
     <div class="section-title"><span class="icon">EMOJI</span> Title</div>
     <div id="{id}-content"></div>
   </section>
   ```
4. **Hero** — set the title, subtitle, and 5–6 headline stat chips.
5. **Accent color** — pick a topic-appropriate accent (see the table below) and
   change the `--accent` CSS variable once; the whole dashboard re-themes.
6. **Render functions** — in the inline `<script>`, write one render function
   per section that reads from `DATA` and injects content into the section's
   container element. The `render(d)` function is the entry point — call your
   section renderers from there.
7. **Charts** — add `<canvas>` elements and render them with the `makeChart()`
   helper.
8. **Data wiring** — embed `DATA` directly, or `fetch()` it. Uncomment the
   matching line in the `DOMContentLoaded` handler.
9. **Verify** — check the responsive breakpoints (1200px, 900px, 600px) and the
   dark/light toggle, and confirm the footer metadata is filled in.

## Section blueprint

When building a dashboard, select 10–20 of these section types based on the
topic:

| #  | Section type             | What it shows                                      |
|----|--------------------------|----------------------------------------------------|
| 1  | Hero / Overview          | Identity, headline stats, summary tag              |
| 2  | Executive Summary        | Key metrics, top categories, profile               |
| 3  | Rankings                 | Top entities across multiple tabs                  |
| 4  | Period-by-Period         | Historical breakdown by period                     |
| 5  | Growth / Timeline        | Trend over time                                    |
| 6  | Category Breakdown       | Composition by category/type                       |
| 7  | Entity Deep Dives        | Top entities as clickable cards with modals        |
| 8  | Relationships            | Connections, co-occurrences                        |
| 9  | Quantitative Lab         | Numeric analysis, distributions, gauges            |
| 10 | Activity Patterns        | When/where/how, via heatmap + time series          |
| 11 | Sentiment                | Qualitative or emotional analysis                  |
| 12 | Feature Analysis         | Multi-dimensional profiling via radar              |
| 13 | Records & Extremes       | Superlatives — most, least, first, longest         |
| 14 | Temporal Patterns        | Day-of-week, time-of-day, seasonal                 |
| 15 | Explorer / Browser       | Full table with search/filter/sort/paginate        |
| 16 | Recommendations          | Suggested items based on observed patterns         |
| 17 | Smart Collections        | Auto-generated groupings                           |
| 18 | Benchmarks               | How the data compares to external benchmarks       |
| 19 | Opportunity Pipeline     | Actionable items ranked by fit/priority            |
| 20 | Competency Map           | Inventory with gap analysis                        |
| 21 | Scenario Analysis        | Multiple paths with probabilities                  |
| 22 | Demand Signals           | Market/trend indicators                            |
| 23 | Priority Actions         | Prioritized next steps (P1/P2/P3)                  |
| 24 | Milestones               | Progress toward goals, unlockable tiers            |
| 25 | Global Comparisons       | How the subject compares to averages/norms         |
| 26 | Deep Insights            | Analysis narratives, tabbed by sub-topic           |
| 27 | Competitive Positioning  | Strengths, differentiators, market position        |
| 28 | Findings                 | Key discoveries, severity-rated                    |

## Design tokens

### Dark mode (default)

```css
:root, [data-theme="dark"] {
  --bg:    #0a0a0f;  --bg2:   #111118;  --bg3:  #1a1a24;  --bg4: #22222e;
  --text:  #f5f5f7;  --text2: #a1a1a6;  --text3:#6e6e73;
  --accent:#fa2d48;  /* Primary accent — change this to re-theme */
  --green: #30d158;  --blue:  #0a84ff;  --purple:#bf5af2;
  --orange:#ff9f0a;  --cyan:  #22d3ee;  --amber: #f59e0b;  --red: #ef4444;
  --card:  rgba(28,28,35,.7);
  --glass: rgba(255,255,255,.04);
  --radius:16px;
  --font:  -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
}
```

### Light mode

```css
[data-theme="light"] {
  --bg:    #faf8f6;  --bg2:   #ffffff;  --bg3:  #f0ecea;  --bg4: #e5e0dc;
  --text:  #1d1d1f;  --text2: #6e6e73;  --text3:#a1a1a6;
  --card:  rgba(255,255,255,.85);
  --glass: rgba(0,0,0,.03);
}
```

### Severity / status colors

| Level    | Color        | Use                                          |
|----------|--------------|----------------------------------------------|
| CRITICAL | Red          | Urgent findings, P1 actions, negative KPIs   |
| HIGH     | Amber/Orange | Important findings, P2 actions, warnings     |
| MEDIUM   | Cyan/Teal    | Informational findings, neutral data         |
| LOW      | Dim text     | Background info, minor items                 |
| POSITIVE | Green        | Growth, positive trends, completed items     |
| SPECIAL  | Purple       | Unique differentiators, premium tiers        |
| NEUTRAL  | Indigo       | Categories, labels, section markers          |

## Accent color guide

The template uses `--accent` throughout. Change it once to re-theme everything.

| Topic domain            | Accent        | Hex       |
|-------------------------|---------------|-----------|
| Finance / Trading       | Amber-Gold    | `#f59e0b` |
| Crypto / Blockchain     | Cyan-Teal     | `#22d3ee` |
| Regulatory / Legal      | Blue          | `#0a84ff` |
| Research / Academic     | Purple        | `#bf5af2` |
| Health / Fitness        | Green         | `#30d158` |
| Career / Professional   | Indigo        | `#5e5ce6` |
| Sports / Performance    | Orange        | `#ff9f0a` |
| Real Estate             | Emerald       | `#10b981` |
| Technology / AI         | Electric Blue | `#5e5ce6` |
| Media / Entertainment   | Red-Pink      | `#fa2d48` |

## Component reference

| Component       | Notes                                                       |
|-----------------|-------------------------------------------------------------|
| Hero            | Gradient overlay, animated logo, gradient title, stat chips |
| Stat chips      | Grid of centered glass cards with large color-coded values  |
| Findings list   | Left border colored by severity; badge + title + body       |
| Ranked list     | Numbered items, gold/silver/bronze top three                |
| Data tables     | Sortable, uppercase headers, zebra-hover rows               |
| Pill badges     | Color-coded rounded pills for tags/categories               |
| Cards           | `card`, `card-accent-{color}`, `card-glow`, `glass-card`    |
| Tab system      | Pill-shaped tab buttons with content-panel toggle           |
| Charts          | Line, bar, donut/pie, radar, stacked area (Chart.js)        |
| Progress bars   | Thin track + filled bar, color-coded by metric type         |
| Modals          | Centered overlay, blur backdrop, fade-in, for detail views  |
| Search + filter | Global search with results dropdown; advanced filter panel  |
| Carousel        | Horizontal scroll with snap points and arrow navigation     |
| Heatmap grid    | CSS grid of colored cells for activity density              |
| Priority actions| P1/P2/P3 badge + action description, sorted by priority     |
| Export FAB      | Fixed floating button opening an export menu                |
