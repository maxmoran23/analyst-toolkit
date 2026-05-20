# AML/CFT Risk Register — Excel Template Spec

## Purpose
Generate an institutional-grade risk register for AML/CFT programs. Covers inherent risk
assessment, control effectiveness, and residual risk scoring with heat map visualization.
Suitable for board reporting, regulatory examination, and program planning. The risk
categories and scoring logic align with the FFIEC BSA/AML risk assessment approach and
FATF risk-based methodology.

This is a generic, industry-standard framework. Adapt the risk inventory, scenarios, and
scores to the specific institution and its product, customer, and geographic profile.

## Output
`.xlsx` workbook, 4 tabs. Built with the Python `openpyxl` library.

---

## Tab 1: Risk Register

### Columns
| Col | Header | Width | Format |
|-----|--------|-------|--------|
| A | Risk ID | 10 | Text (AML-R001, etc.) |
| B | Category | 16 | Dropdown: Customer, Product, Geographic, Transaction, Channel, Regulatory, Technology, Third-Party |
| C | Risk Description | 45 | Text (wrapped) |
| D | Risk Scenario | 40 | Text (wrapped) — specific typology or scenario |
| E | Likelihood (1-5) | 12 | Integer dropdown |
| F | Impact (1-5) | 12 | Integer dropdown |
| G | Inherent Risk Score | 14 | Formula: E*F |
| H | Inherent Tier | 12 | Formula: CRITICAL (20-25), HIGH (12-19), MEDIUM (6-11), LOW (1-5) |
| I | Mitigating Controls | 40 | Text (wrapped) — control IDs from control matrix |
| J | Control Effectiveness (1-5) | 14 | Integer dropdown (5=strong, 1=weak) |
| K | Residual Risk Score | 14 | Formula: G * (1 - (J-1)/5) |
| L | Residual Tier | 12 | Formula: same tier logic as H |
| M | Risk Owner | 18 | Text (role) |
| N | Treatment | 14 | Dropdown: Accept, Mitigate, Transfer, Avoid |
| O | Action Plan | 40 | Text (wrapped) |
| P | Due Date | 12 | Date |
| Q | Status | 12 | Dropdown: Open, In Progress, Closed, Monitoring |
| R | Last Reviewed | 12 | Date |

### Styling
- Header: indigo fill, white bold text, frozen at A2
- Inherent/Residual Tier conditional formatting:
  - CRITICAL: dark red fill, white text
  - HIGH: red fill
  - MEDIUM: amber fill
  - LOW: green fill
- Auto-filter on all columns
- Data validation dropdowns on Category, Likelihood, Impact, Control Effectiveness, Treatment, Status

### Pre-populated Risk Items (15 baseline)

**Customer Risks:**
- AML-R001: High-risk customer onboarding (PEPs, high-risk jurisdictions)
- AML-R002: Shell company / nominee structure abuse
- AML-R003: Beneficial ownership opacity

**Product/Service Risks:**
- AML-R004: Privacy coin / mixer usage
- AML-R005: Cross-chain bridge exploitation
- AML-R006: DeFi protocol interaction (unhosted wallets)

**Geographic Risks:**
- AML-R007: FATF gray/black list jurisdiction exposure
- AML-R008: Sanctions jurisdiction nexus (OFAC, EU, UN)

**Transaction Risks:**
- AML-R009: Structuring / smurfing patterns
- AML-R010: Rapid movement (layering through multiple wallets)
- AML-R011: Darknet marketplace association

**Channel Risks:**
- AML-R012: P2P / peer-to-peer transfer abuse
- AML-R013: ATM / cash-in channel exploitation

**Regulatory/Compliance Risks:**
- AML-R014: SAR filing timeliness failure
- AML-R015: Regulatory examination deficiency

---

## Tab 2: Heat Map

### Layout
- 5x5 grid: Likelihood (x-axis, 1-5) vs. Impact (y-axis, 5 to 1)
- Each cell contains count of risks landing in that score
- Color gradient: green (1-5) -> yellow (6-11) -> orange (12-19) -> red (20-25)
- Risk IDs listed in each cell
- Uses COUNTIFS formulas referencing Tab 1

### Styling
- Large cells (column width 18, row height 50)
- Centered text, bold counts
- Axis labels: Likelihood across top, Impact down left side
- Title row: "INHERENT RISK HEAT MAP" and "RESIDUAL RISK HEAT MAP" (side by side)

---

## Tab 3: Risk Appetite

### Content
| Category | Appetite Level | Threshold | Current Exposure | Gap |
|----------|---------------|-----------|-----------------|-----|

- Appetite levels: None (0), Low (1-5), Moderate (6-11), Elevated (12-19), High (20-25)
- Current Exposure: MAX of residual scores in that category (formula from Tab 1)
- Gap: Exposure - Threshold (conditional formatting: positive = red, negative/zero = green)
- Pre-populated with all 8 risk categories

---

## Tab 4: Trend Tracker

### Columns
| Col | Header | Format |
|-----|--------|--------|
| A | Assessment Period | Text (Q1 2026, etc.) |
| B | Total Risks | Number |
| C | Critical Count | Number |
| D | High Count | Number |
| E | Medium Count | Number |
| F | Low Count | Number |
| G | Avg Inherent Score | Number (1 decimal) |
| H | Avg Residual Score | Number (1 decimal) |
| I | Open Actions | Number |
| J | Overdue Actions | Number |
| K | Notes | Text |

- Pre-populate current period from Tab 1 formulas
- Future periods added manually per assessment cycle
- Sparkline-ready column layout

---

## Generation Pattern

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, numbers
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from datetime import datetime

wb = Workbook()

# Colors
CRITICAL = PatternFill(start_color="8B0000", end_color="8B0000", fill_type="solid")
HIGH = PatternFill(start_color="FF4444", end_color="FF4444", fill_type="solid")
MEDIUM = PatternFill(start_color="FFB347", end_color="FFB347", fill_type="solid")
LOW = PatternFill(start_color="77DD77", end_color="77DD77", fill_type="solid")

# Tab 1: Risk Register with all 15 pre-populated risks
# Tab 2: Dual heat maps (inherent + residual) with COUNTIFS
# Tab 3: Risk appetite thresholds vs current exposure
# Tab 4: Trend tracker with current period auto-populated

wb.save(f'risk-register-{datetime.now().strftime("%Y-%m-%d")}.xlsx')
```

## How to Use with an AI Assistant
Hand this spec to an AI assistant and ask it to generate the workbook. Update quarterly
as part of the program assessment cycle. Cross-reference the Mitigating Controls column
with the Control IDs in the companion `control-matrix.md` template.
