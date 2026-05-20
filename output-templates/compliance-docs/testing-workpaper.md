# Independent Testing Workpaper — Excel Template Spec

## Purpose
Generate a testing workpaper for compliance control testing. Covers sample selection,
test execution, exception tracking, and summary reporting. Designed for BSA/AML
independent testing, SOX 404 control testing, and regulatory examination preparation.
Sample sizing and exception-rating conventions follow standard internal-audit practice.

This is a generic framework suitable for any financial institution. Adapt test
procedures, attributes, and population descriptions to the specific control environment.

## Output
`.xlsx` workbook, 4 tabs. Built with the Python `openpyxl` library.

---

## Tab 1: Test Plan

### Columns
| Col | Header | Width | Format |
|-----|--------|-------|--------|
| A | Test ID | 10 | Text (TST-001) |
| B | Control ID | 12 | Text (references control matrix) |
| C | Control Description | 40 | Text (wrapped) |
| D | Test Objective | 40 | Text (wrapped) |
| E | Test Procedure | 50 | Text (wrapped) — step-by-step |
| F | Population Description | 30 | Text |
| G | Population Size | 12 | Number |
| H | Sample Size | 12 | Number |
| I | Sample Method | 16 | Dropdown: Random, Judgmental, Haphazard, Systematic |
| J | Testing Period | 16 | Text (e.g., "Q1 2026") |
| K | Tester | 16 | Text (role) |
| L | Status | 14 | Dropdown: Not Started, In Progress, Complete, Blocked |
| M | Planned Date | 12 | Date |
| N | Completion Date | 12 | Date |

### Pre-populated Tests (mapped to 27 controls)
- TST-001 through TST-027, one per control from the control matrix
- Test procedures pre-written for each control type:
  - CIP/CDD: "Select [N] new accounts. Verify CIP documents collected, identity verified, risk rating assigned within [X] days of account opening."
  - TM: "Select [N] alerts from period. Verify investigation completed within SLA, disposition documented, escalation where required."
  - Sanctions: "Select [N] screening results. Verify true matches escalated, false positives documented, list version current."
  - SAR: "Select [N] SAR filings. Verify filing within 30 days of detection, narrative complete, supporting documentation retained."
  - Governance: "Obtain training records for [N] employees. Verify completion within [X] days of hire/annual requirement."

### Sample Size Guide (embedded in header comment)
```
Population < 50:     Test all
Population 50-250:   Sample 25
Population 251-1000: Sample 40
Population > 1000:   Sample 60
Risk-based override:  High-risk controls +50%
```

---

## Tab 2: Test Results

### Columns
| Col | Header | Width | Format |
|-----|--------|-------|--------|
| A | Test ID | 10 | Text |
| B | Sample # | 8 | Number (1, 2, 3...) |
| C | Sample Identifier | 20 | Text (account #, alert ID, etc.) |
| D | Attribute 1 | 20 | Pass/Fail/N/A |
| E | Attribute 2 | 20 | Pass/Fail/N/A |
| F | Attribute 3 | 20 | Pass/Fail/N/A |
| G | Attribute 4 | 20 | Pass/Fail/N/A |
| H | Overall Result | 14 | Formula: if any Fail then "EXCEPTION" else "PASS" |
| I | Exception Detail | 40 | Text (wrapped) — only if exception |
| J | Root Cause | 30 | Dropdown: Process Gap, Training, System Issue, Human Error, Design Deficiency |
| K | Severity | 12 | Dropdown: Critical, Significant, Minor, Observation |

### Styling
- EXCEPTION rows: light red background
- PASS in H column: green text
- Data validation on Pass/Fail/N/A and dropdowns
- Attribute headers customizable per test (fill in the specific attributes being tested)

---

## Tab 3: Exception Summary

### Columns
| Col | Header | Format |
|-----|--------|--------|
| A | Exception # | EXC-001 |
| B | Test ID | Text |
| C | Control ID | Text |
| D | Description | Text (wrapped) |
| E | Root Cause | Text |
| F | Severity | Dropdown |
| G | Impact Assessment | Text (wrapped) |
| H | Compensating Control | Text |
| I | Remediation Plan | Text (wrapped) |
| J | Owner | Text (role) |
| K | Target Date | Date |
| L | Status | Dropdown: Open, Remediated, Accepted, Escalated |
| M | Verification Date | Date |

### Auto-populated
- Pull from Tab 2 where Overall Result = "EXCEPTION"
- Cross-reference Control ID from Tab 1

---

## Tab 4: Summary Report

### Content
Row 1-2: "INDEPENDENT TESTING REPORT" (merged, bold, 18pt)
Row 3: Assessment period, scope, methodology
Row 5-6: Headers

**Section 1: Scope Summary**
| Metric | Value |
|--------|-------|
| Controls Tested | COUNTA from Tab 1 |
| Total Samples | SUM of Sample Size from Tab 1 |
| Testing Period | [Period] |
| Tests Complete | COUNTIF Status="Complete" |
| Tests Pending | COUNTIF Status!="Complete" |

**Section 2: Results Summary**
| Result | Count | % |
|--------|-------|---|
| Pass (no exceptions) | Formula | Formula |
| Exception - Critical | COUNTIF | |
| Exception - Significant | COUNTIF | |
| Exception - Minor | COUNTIF | |
| Exception - Observation | COUNTIF | |

**Section 3: Exception Rate by Domain**
| Domain | Tests | Exceptions | Rate | Rating |
|--------|-------|-----------|------|--------|
| CDD | | | | |
| TM | | | | |
| Sanctions | | | | |
| SAR | | | | |
| Governance | | | | |
| Tech | | | | |

Rating: Satisfactory (<5%), Needs Improvement (5-15%), Unsatisfactory (>15%)

**Section 4: Key Findings** (manual entry area)
- Numbered list of significant findings
- Cross-reference to exception IDs

**Section 5: Recommendations** (manual entry area)

---

## Generation Pattern

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from datetime import datetime

wb = Workbook()

# Tab 1: Test Plan with 27 pre-populated test procedures
# Tab 2: Test Results with pass/fail data validation
# Tab 3: Exception Summary linked to Tab 2 exceptions
# Tab 4: Summary Report with COUNTIF/COUNTA formulas

wb.save(f'testing-workpaper-{datetime.now().strftime("%Y-%m-%d")}.xlsx')
```

## How to Use with an AI Assistant
Hand this spec to an AI assistant and ask it to generate the workbook for a quarterly or
annual independent testing cycle. Fill in sample identifiers and attribute results during
test execution; the Summary tab auto-calculates from the test results. Cross-reference
the Control ID column with the companion `control-matrix.md` template.
