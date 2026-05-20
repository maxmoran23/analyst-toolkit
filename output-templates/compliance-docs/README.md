# Compliance Document Templates

Three Excel-workbook specifications for AML/CFT (anti-money-laundering / countering the
financing of terrorism) compliance work. Each is a generic, bank-grade industry
reference — not tied to any institution — structured around FFIEC BSA/AML examination
domains and FATF risk-based methodology.

These are **specifications**, not finished workbooks. Each file describes the tabs,
columns, formatting, formulas, and pre-populated content for an Excel deliverable. You
hand the spec to an AI assistant, which generates the `.xlsx` using the Python `openpyxl`
library.

## The three templates

| File | Output | What it is |
|------|--------|------------|
| `control-matrix.md` | 3-tab `.xlsx` | A 27-control AML/CFT control inventory across six domains (CDD, transaction monitoring, sanctions, SAR, governance, technology), plus a summary dashboard and an embedded testing workpaper tab. Use for audit prep, exam readiness, and program governance. |
| `risk-register.md` | 4-tab `.xlsx` | A 15-risk AML/CFT risk register with inherent vs. residual scoring, dual heat maps, a risk-appetite tab, and a period-over-period trend tracker. Use for board reporting, exam prep, and program planning. |
| `testing-workpaper.md` | 4-tab `.xlsx` | An independent-testing workpaper covering test planning, sample selection, exception tracking, and a summary report. Designed for BSA/AML independent testing and SOX 404 control testing. |

The three are designed to interlock: the risk register's *Mitigating Controls* column
and the testing workpaper's *Control ID* column both reference the Control IDs defined
in the control matrix.

## How to use with an AI assistant

1. Open the relevant `.md` spec and read it for structure.
2. Ask an AI assistant to generate the workbook — for example:
   *"Generate the AML/CFT control matrix described in this spec as an .xlsx file. Use
   openpyxl. Apply the data validation and conditional formatting exactly as written."*
3. Tell the assistant any institution-specific adaptations: assessment scope, additional
   controls or risks, role-based owners, current effectiveness or risk ratings.
4. The assistant produces the `.xlsx`; you then fill in live data (test results, sample
   identifiers, dates) during the actual assessment cycle.

## Scope and disclaimer

These templates encode publicly available, industry-standard compliance frameworks
(FFIEC, FATF, FinCEN guidance). They are reference scaffolding for building compliance
documentation — they are not legal advice and not a substitute for an institution's own
risk assessment, policies, or qualified compliance counsel. Adapt them to your
jurisdiction, regulator expectations, and risk profile before use.
