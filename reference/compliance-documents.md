# Compliance Documents

A cheat-sheet for producing professional-grade compliance and financial-crime
documentation — enhanced due diligence reports, risk assessments, control
matrices, suspicious-activity-report narratives, policy documents, and
transaction-monitoring rule documentation. The structures below target
bank- and consulting-quality standards.

---

## What good looks like

Compliance documentation is judged on whether it survives examination. Across
every document type, the same markers apply:

- Every risk rating carries a written rationale.
- Every screening result is documented with a date and a source.
- Every factual claim is sourced.
- Recommendations are specific, owned, and time-bound.
- Allegations are labeled as allegations; settled matters as settled.

For the writing voice, see
[`../methodology/audit-defensible-writing.md`](../methodology/audit-defensible-writing.md).
For severity tiers and the observed/alleged distinction, see
[`../methodology/analytical-patterns.md`](../methodology/analytical-patterns.md).

---

## Document library

### 1. Enhanced Due Diligence (EDD) report

**Purpose:** A deep-dive assessment of a high-risk entity, customer, or
counterparty.
**Format:** A formal document, typically 8-15 pages.

**Required sections:**
- Executive summary with a risk rating (HIGH / MEDIUM / LOW)
- Entity profile — legal name, jurisdiction, ownership, principals
- Business analysis — model, products, geography, customer base
- Risk assessment — a factor matrix with ratings and rationale
- AML/CFT risk indicators
- Sanctions / PEP / adverse-media screening results
- Transaction analysis (where applicable)
- Regulatory standing
- Conclusions and recommendations
- Appendices — sources, screening results, methodology

**Quality markers:**
- Every risk rating has a written rationale.
- All screening results are documented with a date and a source.
- Ownership is traced to ultimate beneficial owners.
- Recommendations are specific and actionable.
- Sources are cited for all factual claims.

### 2. AML/CFT risk assessment

**Purpose:** Assess money-laundering and terrorist-financing risk for an entity,
product, geography, or business line.
**Format:** A formal document or a spreadsheet matrix.

**Framework — inherent risk:**

| Risk factor | Rating (1-5) | Weight | Score | Rationale |
|-------------|-------------|--------|-------|-----------|
| Customer type | | | | |
| Geographic risk | | | | |
| Product / service risk | | | | |
| Delivery channel | | | | |
| Transaction volume / patterns | | | | |
| Regulatory environment | | | | |
| **Inherent risk score** | | | **[sum]** | |

**Framework — control effectiveness:**

| Control | Effectiveness (1-5) | Weight | Score | Evidence |
|---------|---------------------|--------|-------|----------|
| CDD / KYC | | | | |
| Transaction monitoring | | | | |
| Sanctions screening | | | | |
| SAR filing | | | | |
| Training | | | | |
| **Control effectiveness** | | | **[sum]** | |

**Residual risk = inherent risk − control-effectiveness adjustment.**

### 3. Control matrix

**Purpose:** Document the control environment for a compliance program.
**Format:** A spreadsheet workbook (preferred) or a document table.

**Standard domains (a 27-control framework):**

| Domain | # Controls | Focus |
|--------|-----------|-------|
| Customer Due Diligence (CDD) | 6 | KYC, EDD, ongoing monitoring, beneficial ownership |
| Transaction Monitoring (TM) | 5 | Rules, alerts, tuning, coverage |
| Sanctions Screening | 4 | OFAC, list management, real-time and retrospective screening |
| SAR Filing | 4 | Detection, investigation, filing, tracking |
| Governance & Oversight | 5 | Policy, training, audit, reporting, the BSA officer function |
| Technology & Data | 3 | Systems, data quality, vendor management |

**Per-control fields:**
Control ID, description, type (preventive / detective), frequency, owner, testing
method, evidence type, last tested, effectiveness rating, gap or issue,
remediation plan.

### 4. SAR narrative

**Purpose:** A suspicious-activity-report narrative for regulatory filing.
**Format:** Structured text (for a filing system) or a formal document.

```
SUBJECT INFORMATION
- Name / entity
- Account(s) involved
- Suspicious activity date range
- Amount involved

SUMMARY OF SUSPICIOUS ACTIVITY
[A one-to-two-paragraph overview: who, what, when, where, how much, why
suspicious.]

DETAILED NARRATIVE
1. Background on the subject
2. Description of the suspicious activity
   - Transaction details (dates, amounts, counterparties)
   - Patterns identified
   - Red flags triggered
3. Investigation conducted
   - Sources reviewed
   - Systems checked
   - Additional findings
4. Conclusion
   - Why the activity is suspicious
   - Typology match (if applicable)
   - Law-enforcement referral recommendation (if applicable)

SUPPORTING DOCUMENTATION
- Transaction logs
- Screening results
- Prior SARs on the subject (if any)
```

### 5. Policy document

**Purpose:** A formal compliance policy or procedure.
**Format:** A formal document.

```
DOCUMENT CONTROL
  Policy #: [XXX]
  Title: [Policy name]
  Version: [X.X]
  Effective date: [date]
  Owner: [title / department]
  Approver: [title]
  Next review: [date]

1.  PURPOSE AND SCOPE
2.  REGULATORY FRAMEWORK (applicable laws and regulations)
3.  DEFINITIONS
4.  POLICY STATEMENTS
    4.1 [Requirement 1]
    4.2 [Requirement 2]
5.  ROLES AND RESPONSIBILITIES (a RACI matrix)
6.  PROCEDURES
    6.1 [Process 1 — step by step]
    6.2 [Process 2]
7.  ESCALATION PROCEDURES
8.  RECORD RETENTION
9.  TRAINING REQUIREMENTS
10. EXCEPTIONS
11. ENFORCEMENT
12. RELATED POLICIES
13. REVISION HISTORY
```

### 6. Transaction-monitoring rule documentation

**Purpose:** Document a transaction-monitoring rule for audit and governance.
**Format:** A formal document or a spreadsheet.

```
RULE DOCUMENTATION
  Rule ID: [TM-XXX]
  Rule name: [Descriptive name]
  Version: [X.X]
  Effective date: [date]

RULE LOGIC
  Trigger: [What generates an alert]
  Parameters: [Thresholds, time windows, entity types]
  Exclusions: [What is excluded, and why]

TYPOLOGY MAPPING
  AML typology: [Which laundering typology this rule detects]
  Risk indicators: [The red flags this rule targets]

TUNING HISTORY
| Date | Change | Rationale | SAR yield before | SAR yield after |
|------|--------|-----------|------------------|-----------------|

PERFORMANCE METRICS
  Alert volume (monthly average)
  SAR conversion rate
  False-positive rate
  Average investigation time
```

---

## Regulatory reference points

- **BSA / AML:** 31 CFR Chapter X; FinCEN guidance
- **OFAC:** the SDN list, the 50 Percent Rule, sectoral sanctions
- **EU AMLD / MiCA:** the Anti-Money Laundering Directives; the Markets in
  Crypto-Assets Regulation
- **FATF:** the 40 Recommendations; mutual evaluations
- **Banking-regulator examination manuals:** the BSA/AML examination manual

For digital-asset typologies and the full regulatory map, see
[`aml-typologies.md`](aml-typologies.md).

---

## Related references

- [`aml-typologies.md`](aml-typologies.md) — crypto laundering typologies,
  regulatory frameworks, risk scoring
- [`audit-documentation.md`](audit-documentation.md) — control testing and
  workpaper documentation
- [`regulatory-intelligence.md`](regulatory-intelligence.md) — tracking
  regulatory developments
