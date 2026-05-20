> ILLUSTRATIVE SAMPLE — synthetic/illustrative content produced for format demonstration. Not a real assessment.

# AML/CFT Control Matrix — Sample (Partially Populated)

> **Sample note.** This is a markdown rendering of the [`control-matrix.md`](../../output-templates/compliance-docs/control-matrix.md) template, populated with ~10 illustrative controls to demonstrate structure. The full template specifies a 27-control, 3-tab `.xlsx` workbook (Control Matrix · Summary Dashboard · Testing Workpaper); this sample shows a representative subset of each tab in markdown. All control descriptions, test results, ratings, owners, dates, and exception figures are **synthetic** — invented for format demonstration. This is a generic, industry-standard framework following FFIEC BSA/AML examination domains and FATF Recommendation themes; it is not specific to, and does not describe, any institution.

**Assessment scope (illustrative):** Annual AML/CFT control assessment, sample financial institution, all business lines.
**Assessor (role, generic):** Independent Testing function.
**Assessment date:** 2026-05-19.

---

## Tab 1: Control Matrix (10 of 27 controls shown)

Columns follow the template spec (Control ID · Domain · Control Name · Description · Type · Frequency · Owner · Testing Method · Evidence Type · Last Tested · Effectiveness · Gap/Issue · Remediation Plan · Target Date · Status). Rendered here in two halves for readability.

### Control inventory and attributes

| Control ID | Domain | Control Name | Description | Type | Frequency | Owner |
|---|---|---|---|---|---|---|
| CDD-01 | CDD | Customer Identification Program (CIP) | Collect and verify identifying information for every customer at account opening; document verification method and outcome. | Preventive | Continuous | Onboarding Operations |
| CDD-03 | CDD | Enhanced Due Diligence (EDD) | Apply heightened due diligence to high-risk customers — additional information, source-of-funds review, senior approval before onboarding. | Preventive | Continuous | Financial Crimes Unit |
| CDD-05 | CDD | Beneficial Ownership Identification | Identify and verify natural-person beneficial owners and a controlling individual for legal-entity customers. | Preventive | Continuous | Onboarding Operations |
| TM-01 | TM | Automated Transaction Monitoring System | Operate an automated system that screens transactions against typology-based detection scenarios and generates alerts. | Detective | Continuous | Transaction Monitoring |
| TM-02 | TM | Alert Investigation & Disposition | Investigate every generated alert within defined SLA; document rationale for closure or escalation. | Detective | Daily | Transaction Monitoring |
| TM-03 | TM | Rule Tuning & Optimization | Periodically review and tune monitoring scenario thresholds against productivity and effectiveness data. | Detective | Quarterly | Monitoring Analytics |
| SAN-01 | Sanctions | Real-Time Name Screening | Screen customers and counterparties against sanctions lists at onboarding and on transactions in real time. | Preventive | Continuous | Sanctions Operations |
| SAN-03 | Sanctions | Retrospective Screening (list updates) | Re-screen the existing customer base against sanctions lists promptly after each list update. | Detective | Daily | Sanctions Operations |
| SAR-03 | SAR | SAR Filing (FinCEN) | File suspicious activity reports with the relevant financial intelligence unit within the regulatory deadline. | Detective | Continuous | Financial Crimes Unit |
| GOV-05 | Governance | Independent Audit/Testing | Commission periodic independent testing of the AML/CFT program covering design and operating effectiveness. | Detective | Annual | Internal Audit |

### Testing outcomes and remediation

| Control ID | Testing Method | Evidence Type | Last Tested | Effectiveness | Gap / Issue | Remediation Plan | Target Date | Status |
|---|---|---|---|---|---|---|---|---|
| CDD-01 | Inspection | Account-opening records sample | 2026-04-22 | Effective | None identified in the tested sample. | N/A | — | Closed |
| CDD-03 | Re-performance | EDD case files | 2026-04-24 | Partially Effective | 3 of 25 high-risk files lacked documented senior approval prior to onboarding. | Reinforce approval-gate control; add system block preventing activation without recorded approval. | 2026-07-31 | In Progress |
| CDD-05 | Inspection | Beneficial-ownership certifications | 2026-04-25 | Effective | None identified; certifications complete and verified in the tested sample. | N/A | — | Closed |
| TM-01 | Observation | System configuration / scenario inventory | 2026-04-28 | Effective | Scenario coverage maps to the institution's risk assessment. | N/A | — | Closed |
| TM-02 | Re-performance | Alert investigation records | 2026-04-29 | Partially Effective | 4 of 40 alerts closed without sufficient documented rationale; 2 closed outside SLA. | Refresher training on disposition documentation; SLA exception reporting added to monthly MI. | 2026-08-15 | In Progress |
| TM-03 | Inspection | Tuning analysis memoranda | 2026-04-30 | Ineffective | No documented threshold tuning performed in the preceding 12 months; quarterly cadence not met. | Re-establish quarterly tuning cycle; complete an initial above-the-line/below-the-line review. | 2026-09-30 | Open |
| SAN-01 | Re-performance | Screening logs / match results | 2026-05-02 | Effective | Real-time screening operating as designed in the tested sample. | N/A | — | Closed |
| SAN-03 | Inspection | List-update and re-screening logs | 2026-05-05 | Partially Effective | Re-screening completed but, in 2 of 12 sampled updates, not within the same business day. | Automate post-update re-screening trigger to remove manual scheduling lag. | 2026-07-15 | In Progress |
| SAR-03 | Inspection | Filing records / submission confirmations | 2026-05-07 | Effective | All sampled filings submitted within the regulatory deadline. | N/A | — | Closed |
| GOV-05 | Inquiry | Independent testing reports / audit plan | 2026-05-09 | Effective | Independent testing performed on schedule with appropriate scope and reporting line. | N/A | — | Closed |

**Effectiveness legend** (per template conditional formatting): Effective (green) · Partially Effective (yellow) · Ineffective (red) · Not Tested (gray).
**Status legend:** Open (red) · In Progress (amber) · Closed (green) · N/A.

---

## Tab 2: Summary Dashboard

**AML/CFT Control Matrix — Summary** | Assessment date 2026-05-19 | Independent Testing | Scope: 10 controls tested (subset of 27-control framework).

### Domain summary

Coverage % = (Effective + Partially Effective) / Total × 100.

| Domain | Total | Effective | Partial | Ineffective | Not Tested | Coverage % |
|---|---|---|---|---|---|---|
| CDD | 3 | 2 | 1 | 0 | 0 | 100.0% |
| Transaction Monitoring | 3 | 1 | 1 | 1 | 0 | 66.7% |
| Sanctions | 2 | 1 | 1 | 0 | 0 | 100.0% |
| SAR | 1 | 1 | 0 | 0 | 0 | 100.0% |
| Governance | 1 | 1 | 0 | 0 | 0 | 100.0% |
| **Total (sample)** | **10** | **6** | **3** | **1** | **0** | **90.0%** |

*In the workbook these counts populate via `COUNTIFS` formulas against Tab 1, and a per-domain heat map applies the indigo theme.*

### Top gaps / issues (Effectiveness ≠ Effective)

| Control ID | Effectiveness | Issue summary | Status | Target Date |
|---|---|---|---|---|
| TM-03 | Ineffective | No documented scenario threshold tuning in the preceding 12 months. | Open | 2026-09-30 |
| CDD-03 | Partially Effective | Missing documented senior approval on 3 of 25 high-risk onboarding files. | In Progress | 2026-07-31 |
| TM-02 | Partially Effective | Insufficient disposition rationale on 4 of 40 alerts; 2 SLA breaches. | In Progress | 2026-08-15 |
| SAN-03 | Partially Effective | Post-update re-screening not completed same-day in 2 of 12 sampled updates. | In Progress | 2026-07-15 |

**Assessment read (illustrative).** Of the 10 controls tested, 6 are Effective, 3 Partially Effective, and 1 Ineffective. The single Ineffective rating (TM-03, rule tuning) is the priority remediation item — an untuned monitoring estate degrades the effectiveness of TM-01 and TM-02 over time and is the kind of finding an examiner would expect to see tracked to closure. The three Partially Effective findings are documentation- and timeliness-type gaps rather than control-design failures, and each has a dated remediation plan. No control was left Not Tested in this sample.

---

## Tab 3: Testing Workpaper (sampling detail for the 10 controls shown)

Columns follow the template spec (Control ID · Test Date · Tester · Sample Size · Sample Selection Method · Exceptions Found · Exception Rate · Conclusion · Exception Details · Management Response · Follow-up Date).

| Control ID | Test Date | Tester (role) | Sample Size | Selection Method | Exceptions | Exception Rate | Conclusion | Exception Details | Management Response | Follow-up Date |
|---|---|---|---|---|---|---|---|---|---|---|
| CDD-01 | 2026-04-22 | Independent Testing | 30 | Random | 0 | 0.0% | No Exceptions | — | Noted. | — |
| CDD-03 | 2026-04-24 | Independent Testing | 25 | Judgmental | 3 | 12.0% | Exception Noted | 3 files lacked documented senior approval prior to onboarding. | Accepted; approval-gate system block to be implemented. | 2026-07-31 |
| CDD-05 | 2026-04-25 | Independent Testing | 25 | Random | 0 | 0.0% | No Exceptions | — | Noted. | — |
| TM-01 | 2026-04-28 | Independent Testing | N/A | Judgmental | 0 | 0.0% | No Exceptions | Configuration review; scenario inventory complete. | Noted. | — |
| TM-02 | 2026-04-29 | Independent Testing | 40 | Random | 4 | 10.0% | Exception Noted | 4 alerts closed with insufficient rationale; 2 outside SLA. | Accepted; training and SLA MI to be added. | 2026-08-15 |
| TM-03 | 2026-04-30 | Independent Testing | 4 | Judgmental | 4 | 100.0% | Exception Noted | No tuning evidence for any of the 4 quarters reviewed. | Accepted; quarterly cycle to be re-established. | 2026-09-30 |
| SAN-01 | 2026-05-02 | Independent Testing | 35 | Random | 0 | 0.0% | No Exceptions | — | Noted. | — |
| SAN-03 | 2026-05-05 | Independent Testing | 12 | Judgmental | 2 | 16.7% | Exception Noted | Re-screening not completed same business day for 2 list updates. | Accepted; automated trigger to be implemented. | 2026-07-15 |
| SAR-03 | 2026-05-07 | Independent Testing | 20 | Random | 0 | 0.0% | No Exceptions | All filings within regulatory deadline. | Noted. | — |
| GOV-05 | 2026-05-09 | Independent Testing | N/A | Judgmental | 0 | 0.0% | No Exceptions | Independent testing scope and reporting line appropriate. | Noted. | — |

**Exception Rate conditional formatting** (per template): >5% red · 1–5% yellow · 0% green. In the workbook, Exception Rate is a formula (`Exceptions / Sample Size`); rows where sample-based testing does not apply (TM-01, GOV-05) are marked N/A for sample size and assessed by inspection/inquiry.

---

*Sample ends. The full template produces all 27 controls across six domains (CDD ×6, TM ×5, Sanctions ×4, SAR ×4, Governance ×5, Technology & Data ×3) as a formatted `.xlsx` workbook with data-validation dropdowns, conditional formatting, frozen panes, and `COUNTIFS`-driven summary formulas.*
