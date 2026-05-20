# HTML Dashboard Generation

## Purpose
Create interactive, single-file HTML dashboards and web applications with an AI
assistant — data visualizations, intelligence terminals, analytics tools, monitoring
cockpits. Self-contained files that can be opened directly in a browser or served with a
simple static server (for example `python3 -m http.server`).

## What you need
Most current AI assistants can generate single-file HTML directly. For richer results,
ask for production-grade UI quality, a component library, or a consistent theme.
Describe the dashboard — its sections, data, and interactions — and let the assistant
build it.

## Architecture
Build dashboards as **single-file HTML** with embedded CSS and JavaScript. Load
libraries from a CDN so the file stays self-contained:
- **Charts:** Chart.js, D3.js, Plotly.js, Apache ECharts
- **UI:** Tailwind CSS via CDN, or hand-written components
- **Data:** the Fetch API for live data, embedded JSON for static data
- **Interactivity:** vanilla JavaScript or a lightweight framework

## Reference Design System
A dark theme works well for intelligence and analytics dashboards:
```css
/* Dark theme */
--bg-primary: #0a0a0f;
--bg-card: #12121a;
--bg-hover: #1a1a2e;
--text-primary: #e0e0e0;
--text-secondary: #8888aa;
--accent-blue: #4a9eff;
--accent-green: #00d4aa;
--accent-red: #ff4757;
--accent-yellow: #ffa502;
--border: #2a2a3e;
--radius: 12px;
```

## Dashboard Types

### Intelligence Terminal
- Header with title, timestamp, status indicators
- Grid layout with card-based sections
- Real-time data feeds with auto-refresh
- Filter / search bar
- Severity color coding (CRITICAL red, HIGH orange, MEDIUM yellow, LOW green)
- Expandable detail panels

### Analytics Dashboard
- KPI cards at the top (big numbers with trend arrows)
- Time-series charts (line / area)
- Comparison charts (bar / grouped bar)
- Data tables with sorting and filtering
- Date-range picker
- Export functionality

### Monitoring Cockpit
- Status grid (green / yellow / red indicators)
- Alert queue with severity sorting
- Timeline / activity feed
- Drill-down panels
- Auto-refresh on an interval

## Quality Checklist
- [ ] Responsive layout (works on tablet and up)
- [ ] Dark theme with proper contrast ratios
- [ ] Loading states for async data
- [ ] Error handling for failed fetches
- [ ] Print-friendly styles
- [ ] Keyboard navigation
- [ ] Professional typography (for example Inter for text, JetBrains Mono for data)
- [ ] Smooth transitions / animations
- [ ] Data-freshness indicators (timestamps)
