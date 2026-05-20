# Word Document Generation

## Purpose
Produce professional-grade Word documents (`.docx`) with an AI assistant — reports,
memos, proposals, risk assessments, control matrices, letters,
and standard operating procedures. Target consulting / Big-Four quality standards.

## What you need
Most current AI assistants can generate `.docx` files directly, either through a
document-authoring tool/skill or by writing the file with a library such as Python's
`python-docx`. When you ask for a Word document, the assistant typically:
1. Creates the document
2. Builds the structure with heading styles
3. Applies formatting — bold headers, styled and bordered tables
4. Optionally exports a PDF copy
5. Saves the file

You do not need to specify the mechanism; describe the document you want and let the
assistant choose the tool available to it.

## Quality Standards

### Formatting Conventions
- **Title page:** document title, date, classification, author, version
- **Headers:** Heading 1 for major sections, Heading 2 for subsections, Heading 3 for detail
- **Tables:** bordered, header row bolded, alternating row shading where appropriate
- **Fonts:** a professional serif or sans-serif (Calibri, Arial, Times New Roman)
- **Margins:** 1" all sides (standard)
- **Page numbers:** bottom center or bottom right
- **Footer:** document classification + date

### Document Types & Outlines

#### Entity Risk Assessment Report
```
COVER PAGE: "Entity Risk Assessment — [Entity Name]"
  Date | Analyst | Classification | Version

1. EXECUTIVE SUMMARY (1 page max)
   - Entity overview (2-3 sentences)
   - Risk rating: [HIGH/MEDIUM/LOW] with justification
   - Key findings (3-5 bullets)
   - Recommendation: [APPROVE/ESCALATE/REJECT]

2. ENTITY PROFILE
   - Legal name, DBA, jurisdiction
   - Registration/licensing status
   - Ownership structure (table)
   - Key principals (table: name, title, nationality, PEP status)

3. BUSINESS ANALYSIS
   - Business model description
   - Products/services
   - Geographic footprint
   - Customer base profile
   - Revenue sources

4. RISK ASSESSMENT
   - Risk factor matrix (table: factor, rating, rationale)
   - AML/CFT risk indicators
   - Sanctions screening results
   - Adverse media findings
   - PEP screening results

5. TRANSACTION ANALYSIS (if applicable)
   - Volume/value summary
   - Pattern analysis
   - Unusual activity flags

6. REGULATORY STANDING
   - Licensing status
   - Enforcement history
   - Regulatory filings

7. CONCLUSIONS & RECOMMENDATIONS
   - Overall risk rating with rationale
   - Recommended controls/conditions
   - Next review date

APPENDICES
   A. Source documents list
   B. Screening results
   C. Methodology notes
```

#### Risk Assessment Report
```
1. EXECUTIVE SUMMARY
2. SCOPE & METHODOLOGY
3. RISK IDENTIFICATION
   - Risk inventory table
4. RISK ANALYSIS
   - Likelihood x Impact matrix
   - Inherent vs. residual risk
5. CONTROL ASSESSMENT
   - Control inventory
   - Effectiveness ratings
6. RISK TREATMENT
   - Mitigation strategies
   - Action items with owners/deadlines
7. RESIDUAL RISK SUMMARY
APPENDICES
```

#### Control Matrix Document
```
HEADER: Control Framework — [Domain]
VERSION: [X.X] | DATE | CLASSIFICATION

Table structure:
| # | Control ID | Control Description | Category | Owner | Frequency | Evidence | Effectiveness Rating |

Sections grouped by control domain:
- Customer Due Diligence (CDD)
- Transaction Monitoring (TM)
- Sanctions Screening
- SAR Filing
- Governance & Oversight
```

#### Professional Memo
```
TO: [Recipient]
FROM: [Author]
DATE: [Date]
RE: [Subject]
CLASSIFICATION: [Level]

I. PURPOSE
II. BACKGROUND
III. ANALYSIS
IV. RECOMMENDATION
V. NEXT STEPS
```

#### Standard Operating Procedure (SOP)
```
DOCUMENT CONTROL
  Title | SOP # | Version | Effective Date | Owner | Approver

1. PURPOSE
2. SCOPE
3. DEFINITIONS
4. RESPONSIBILITIES (RACI table)
5. PROCEDURE (numbered steps with decision points)
6. EXCEPTIONS
7. REFERENCES
8. REVISION HISTORY (table)
```

## Prompt Examples

**One-shot risk assessment:**
> "Create a Word doc entity risk assessment for [Entity]. Include risk assessment, ownership
> analysis, and regulatory standing. Export to PDF when done."

**Control matrix:**
> "Generate a .docx control matrix for digital-asset AML covering CDD, TM, sanctions,
> SAR, and governance domains. 25+ controls."

**Quick memo:**
> "Draft a Word doc memo on [topic] — professional formatting, 2 pages max."
