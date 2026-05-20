# Spreadsheet Generation

## Purpose
Produce professional Excel spreadsheets (`.xlsx`) with an AI assistant — financial
models, data analysis, tracking sheets, control matrices, risk registers,
reconciliations. Includes formulas, formatting, charts, and multi-sheet workbooks.

## What you need
Most current AI assistants can generate `.xlsx` files directly, either through a
spreadsheet-authoring tool/skill or by writing the file with a library such as Python's
`openpyxl`. For data-heavy work, the assistant can also profile a dataset, run
statistical analysis, build charts, and write supporting queries. Describe the workbook
you want — sheets, columns, formulas, formatting — and let the assistant choose the
mechanism available to it.

## Spreadsheet Types

### Financial Model
```
Sheet 1: SUMMARY — KPIs, charts, executive view
Sheet 2: ASSUMPTIONS — Input cells (highlighted), drivers
Sheet 3: REVENUE — Revenue build-up, growth rates
Sheet 4: EXPENSES — Cost structure, fixed vs variable
Sheet 5: P&L — Income statement
Sheet 6: CASH FLOW — Cash flow statement
Sheet 7: SENSITIVITY — Scenario analysis (best/base/worst)
```

### Risk Register
```
Columns: Risk ID | Category | Description | Likelihood (1-5) | Impact (1-5) |
         Risk Score | Owner | Mitigating Controls | Residual Risk | Status | Due Date
Conditional formatting: Red (>15), Yellow (8-15), Green (<8)
Auto-calculated risk scores
Summary dashboard sheet with heat map
```

### Transaction Analysis
```
Sheet 1: RAW DATA — Import from CSV/source
Sheet 2: CLEANED — Deduplicated, standardized
Sheet 3: ANALYSIS — Pivot tables, aggregations
Sheet 4: PATTERNS — Anomaly flags, clustering
Sheet 5: SUMMARY — Charts, key findings
```

### Control Matrix (Excel format)
```
Columns: Control # | Domain | Control Name | Description | Type (Preventive/Detective) |
         Frequency | Owner | Evidence | Testing Status | Effectiveness | Notes
Filters on every column
Color-coded effectiveness ratings
Summary counts by domain and status
```

## Formatting Standards
- **Header row:** bold, colored background, frozen panes
- **Data validation:** dropdowns for categorical fields
- **Conditional formatting:** red/amber/green status, thresholds
- **Number formats:** currency ($#,##0.00), percentages, dates
- **Named ranges:** for key inputs/assumptions
- **Print area:** set for clean printing
- **Protection:** lock formula cells, protect structure
