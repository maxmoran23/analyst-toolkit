# AML/CFT Control Matrix — Excel Template Spec

## Purpose
Generate a 27-control AML/CFT control matrix as an Excel workbook. Suitable for audit
preparation, regulatory examination readiness, and program governance. The structure
follows FFIEC BSA/AML examination domains and FATF Recommendation themes.

This is a generic, industry-standard framework. Adapt the control inventory, owners,
and ratings to the specific institution and assessment scope.

## Output
`.xlsx` workbook, 3 tabs. Built with the Python `openpyxl` library.

---

## Tab 1: Control Matrix

### Columns
| Col | Header | Width | Format |
|-----|--------|-------|--------|
| A | Control ID | 12 | Text (CDD-01, TM-01, etc.) |
| B | Domain | 18 | Dropdown: CDD, TM, Sanctions, SAR, Governance, Tech |
| C | Control Name | 30 | Text |
| D | Description | 50 | Text (wrapped) |
| E | Type | 14 | Dropdown: Preventive, Detective |
| F | Frequency | 14 | Dropdown: Continuous, Daily, Weekly, Monthly, Quarterly, Annual |
| G | Owner | 20 | Text (role, not person name) |
| H | Testing Method | 20 | Dropdown: Inquiry, Observation, Inspection, Re-performance |
| I | Evidence Type | 20 | Text |
| J | Last Tested | 14 | Date (YYYY-MM-DD) |
| K | Effectiveness | 14 | Dropdown: Effective, Partially Effective, Ineffective, Not Tested |
| L | Gap/Issue | 40 | Text (wrapped) |
| M | Remediation Plan | 40 | Text (wrapped) |
| N | Target Date | 14 | Date |
| O | Status | 14 | Dropdown: Open, In Progress, Closed, N/A |

### Styling
- Header row: bold, white text, indigo fill (#6C63FF), frozen panes at A2
- Effectiveness column conditional formatting:
  - Effective: green fill (#C6EFCE)
  - Partially Effective: yellow fill (#FFEB9C)
  - Ineffective: red fill (#FFC7CE)
  - Not Tested: gray fill (#D9D9D9)
- Status column conditional formatting:
  - Open: red text
  - In Progress: amber text
  - Closed: green text
- Data validation dropdowns on Type, Frequency, Testing Method, Effectiveness, Status
- All text columns: wrap text enabled

### Pre-populated Controls (27)

**CDD Domain (6):**
- CDD-01: Customer Identification Program (CIP)
- CDD-02: Customer Due Diligence (standard)
- CDD-03: High-Risk Customer Review
- CDD-04: Ongoing Monitoring / Periodic Review
- CDD-05: Beneficial Ownership Identification
- CDD-06: PEP Screening

**Transaction Monitoring (5):**
- TM-01: Automated Transaction Monitoring System
- TM-02: Alert Investigation & Disposition
- TM-03: Rule Tuning & Optimization
- TM-04: Below-Threshold Monitoring
- TM-05: Coverage Assessment

**Sanctions Screening (4):**
- SAN-01: Real-Time Name Screening
- SAN-02: OFAC SDN/Consolidated List Screening
- SAN-03: Retrospective Screening (list updates)
- SAN-04: Transaction/Jurisdiction Screening

**SAR Filing (4):**
- SAR-01: Suspicious Activity Detection
- SAR-02: Investigation & Documentation
- SAR-03: SAR Filing (FinCEN)
- SAR-04: SAR Tracking & Follow-up

**Governance & Oversight (5):**
- GOV-01: AML/CFT Policy & Procedures
- GOV-02: BSA Officer Designation
- GOV-03: Board/Senior Mgmt Reporting
- GOV-04: Training Program
- GOV-05: Independent Audit/Testing

**Technology & Data (3):**
- TECH-01: System Validation & Testing
- TECH-02: Data Quality & Integrity
- TECH-03: Vendor/Third-Party Risk Management

---

## Tab 2: Summary Dashboard

### Content
- Row 1-2: Title "AML/CFT Control Matrix — Summary" (merged, bold, 16pt)
- Row 4: Assessment date, assessor role (generic), scope
- Row 6-12: Domain summary table:

| Domain | Total | Effective | Partial | Ineffective | Not Tested | Coverage % |
|--------|-------|-----------|---------|-------------|------------|------------|

- Formulas: COUNTIFS referencing Tab 1 data
- Row 14-20: Conditional formatting heat map by domain
- Row 22+: Top gaps/issues (pull from Tab 1 where Effectiveness != "Effective")

### Styling
- Same indigo theme
- Summary counts use COUNTIFS formulas
- Coverage % = (Effective + Partial) / Total * 100

---

## Tab 3: Testing Workpaper

### Columns
| Col | Header | Format |
|-----|--------|--------|
| A | Control ID | Text |
| B | Test Date | Date |
| C | Tester | Text (role) |
| D | Sample Size | Number |
| E | Sample Selection Method | Dropdown: Random, Judgmental, Haphazard |
| F | Exceptions Found | Number |
| G | Exception Rate | Percentage (formula: F/D) |
| H | Conclusion | Dropdown: No Exceptions, Exception Noted, Unable to Test |
| I | Exception Details | Text (wrapped) |
| J | Management Response | Text (wrapped) |
| K | Follow-up Date | Date |

### Styling
- Same header styling as Tab 1
- Exception Rate conditional formatting: >5% red, 1-5% yellow, 0% green
- Pre-populated with all 27 Control IDs from Tab 1

---

## Generation Pattern

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from datetime import datetime

wb = Workbook()
INDIGO = PatternFill(start_color="6C63FF", end_color="6C63FF", fill_type="solid")
HEADER = Font(bold=True, color="FFFFFF", size=11)
GREEN = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
YELLOW = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
RED = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
GRAY = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
WRAP = Alignment(wrap_text=True, vertical='top')
THIN_BORDER = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)

# Build Tab 1 with all 27 controls pre-populated
# Build Tab 2 with COUNTIFS formulas
# Build Tab 3 with control IDs and dropdowns
# Apply data validation, conditional formatting, freeze panes
# Set print area and page setup

wb.save(f'control-matrix-{datetime.now().strftime("%Y-%m-%d")}.xlsx')
```

## How to Use with an AI Assistant
Hand this spec to an AI assistant and ask it to generate the workbook. Reference this
document for structure and styling; specify the assessment scope and any institution-
specific control variations. The assistant fills in column values, applies the data
validation and conditional formatting, and saves the `.xlsx`.
