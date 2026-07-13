# Arbitrary Data to Adaptive Dashboard

> Paste this entire file into an AI assistant, then put your source material in the `INPUT MATERIAL` block. The result is one browser-ready HTML dashboard whose structure is inferred from the material rather than imposed by an input schema.

## Role

You are an analytical information designer and careful data-preservation engineer. Turn the supplied material into a clear, single-file HTML dashboard. Make structural inferences only when the input supports them. Never invent, omit, aggregate away, relabel, or silently coerce a supplied value.

## Input material

```text
{{PASTE ARBITRARY DATA HERE}}
```

The material may be JSON, CSV-like rows, a Markdown table, key/value metrics, ranked items, nested objects, prose, or a mixture. It does not need to match a predefined schema.

## Required process

1. Parse only structures you can identify confidently. Keep original spellings, units, order, precision, and null/blank distinctions.
2. Normalize the material into an internal JavaScript object named `DASHBOARD_MODEL`. The internal object is a render contract, not an input requirement:

   ```text
   {
     metadata: {eyebrow, title, subtitle, date, source, confidence, accent},
     kpis: [{label, value, detail}],
     sections: [
       {type: "kpi", ...},
       {type: "chart", ...},
       {type: "table", ...},
       {type: "ranked-list", ...},
       {type: "hierarchy", ...},
       {type: "text", ...},
       {type: "unparsed-material", ...}
     ],
     ledger: [{path, value}]
   }
   ```

3. Apply these evidence-based inferences:

   - A period/date field plus numeric measures becomes a line chart and a complete table.
   - A categorical label plus numeric measures becomes a bar chart or, for one small part-to-whole series, a donut chart; retain the complete table.
   - A key/value metric set becomes KPI cards.
   - An explicitly ordered or ranked collection becomes a horizontal ranked list.
   - Nested parent/child material becomes a hierarchy.
   - Prose remains verbatim text.
   - Mixed material becomes multiple sections, one per supported structure.
   - Any value or group that cannot be parsed safely appears under **Unparsed material** verbatim.

4. Include a leaf-level **Source value ledger** so that every supplied scalar value remains visibly recoverable, including material already represented in another section.
5. If a title, date, source, or confidence rating is absent, say that it was not supplied. Do not manufacture metadata.

## Render as a formatted deliverable

Use the supplied single companion HTML template as the implementation surface. Return exactly one complete `.html` file with:

- dark mode by default and a keyboard-accessible light/dark toggle;
- a hero title, subtitle, metadata line, and KPI cards;
- sticky section navigation;
- glass section cards, a 1400px maximum shell, and the Mode D design tokens;
- Chart.js pinned to `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js`;
- a responsive KPI grid with exactly five columns above 1200px, three at 1200px and below, two at 900px and below, and one at 600px and below;
- searchable, sortable tables;
- accessible names for the toggle, navigation, searches, tables, and charts;
- a footer stating date, source/basis, confidence, and that the source-value ledger is complete.

## Data and DOM safety

- Embed the source data directly in the HTML. Do not fetch it at runtime.
- Before placing JSON inside a `<script>`, serialize it with `JSON.stringify` semantics and replace every literal `<` with the Unicode escape `\u003c`. This prevents source strings from ending the script element.
- Treat every supplied string as text. Create dynamic nodes with `document.createElement`, assign user material only with `textContent`, and set only fixed, implementation-owned attributes.
- Do not parse supplied strings as markup. Do not use string-to-markup DOM APIs, template interpolation into HTML, `document.write`, `eval`, `Function`, `fetch`, XHR, WebSocket, or remote data calls.
- Chart labels and datasets must originate from the normalized model; the corresponding source rows must also remain available in a table or the source ledger.
- If Chart.js is unavailable, show a plain-language fallback while keeping every value accessible in the table and ledger.

## Output rules

- Output the complete HTML only. Do not wrap it in explanation.
- Do not fabricate findings, trends, calculations, thresholds, sources, or confidence.
- Do not replace exact values with rounded values unless both the exact source value and the display transformation are shown.
- Do not drop duplicate, blank, zero, false, null, nested, or unparsed values.
- Do not use emoji unless the user explicitly requests it.

## Preflight before returning

Confirm internally that:

1. every source leaf is present in the Source value ledger;
2. every inferred chart is backed by a table or ledger;
3. unknown material is visible under Unparsed material;
4. the theme toggle, navigation, search, and sort handlers target existing elements;
5. no supplied string is treated as markup;
6. the Chart.js URL and 5 -> 3 -> 2 -> 1 breakpoints are exact;
7. the first render remains useful if the chart CDN cannot load.
