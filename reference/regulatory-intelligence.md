# Regulatory Intelligence

A cheat-sheet for tracking, analyzing, and reporting on regulatory developments —
legislation, enforcement actions, agency guidance, rulemaking, and industry-impact
assessment. The framework below is oriented to digital assets, AML/CFT, and
financial-services regulation, but the structure generalizes to any regulated
domain.

For severity tiers and the source hierarchy, see
[`../methodology/analytical-patterns.md`](../methodology/analytical-patterns.md).

---

## Source hierarchy

Rank sources, prefer the top of the ranking, and cite accordingly. A regulatory
finding sourced to a trade-press summary is weaker than the same finding sourced
to the agency's own release — find the primary document.

| Priority | Source type | Examples |
|----------|-------------|----------|
| 1 | Official government | The financial-crime regulator, securities and commodities regulators, the banking regulators, the sanctions authority, the treasury department |
| 2 | Legislative | The legislature's official record, committee hearings, bill text |
| 3 | Standards bodies | FATF, the Basel Committee, IOSCO |
| 4 | Legal analysis | Law-firm advisories, compliance publications |
| 5 | Industry news | Trade press, financial news outlets |

---

## Analysis dimensions

For each regulatory development, work through six questions. They convert a raw
news item into an assessment a compliance program can act on.

1. **What** — a description of the action, rule, or guidance
2. **Who** — which agency issued it; which entities it affects
3. **When** — effective date, comment periods, compliance deadlines
4. **Impact** — how it changes obligations for affected businesses and their
   compliance programs
5. **Action required** — what must change in policies and procedures
6. **Risk level** — HIGH / MEDIUM / LOW, based on enforcement likelihood and
   penalty severity

---

## Tracking categories

Organize regulatory monitoring into six streams:

- **Legislation** — bills, amendments, votes, committee activity
- **Rulemaking** — proposed rules, final rules, comment periods
- **Enforcement** — actions, settlements, consent orders, penalties
- **Guidance** — advisories, FAQs, interpretive letters, no-action letters
- **Sanctions** — designations, list updates, geographic sanctions
- **International** — developments in other jurisdictions and at standards bodies

---

## Key regulatory bodies (digital assets)

| Body | Jurisdiction | Focus |
|------|-------------|-------|
| Financial-crime regulator (FinCEN, US) | National | BSA/AML, MSB registration, SAR filing |
| Securities regulator | Securities | Token classification, exchange registration |
| Commodities regulator | Commodities | Derivatives, fraud, market manipulation |
| Banking regulators | Banking | Bank engagement with crypto, custody |
| Sanctions authority (OFAC, US) | Sanctions | The SDN list, designated addresses |
| FATF | International | The Travel Rule, VASP standards, mutual evaluations |
| EU (MiCA) | Europe | Comprehensive crypto regulation |
| State / sub-national regulators | Sub-national | Money-transmitter licensing |

---

## Tracking a statute's implementing rules by RIN

A statute that delegates rulemaking to several agencies produces a stream of
documents over a year or more: requests for comment, proposals, re-proposals,
procedural rules, final rules. The question a compliance program actually needs
answered, *which obligations are final, and from when*, is a status question per
rulemaking, not per document.

Track it by **Regulation Identifier Number (RIN)**, not by keyword:

1. **Build a candidate set by term search.** Quote the term (see the query-precision
   note in [`osint-source-library.md`](osint-source-library.md)) and restrict to rule
   and proposed-rule document types from the enactment date forward.
2. **Treat the candidate set as noise-bearing.** Even a quoted phrase search returns
   documents outside the statute's scope. Classify every hit before counting it.
3. **Resolve each in-scope document to its RIN**, then query by RIN
   (`conditions[regulation_id_number]` on the Federal Register API). A final rule
   carries the same RIN as the proposal it finalizes, so the RIN is the stable key
   across the rulemaking's life. A keyword match is not.
4. **Report status per RIN, dated.** Proposed / final, effective date, comment close.
   Rulemaking status changes weekly; an undated status table is wrong by default.
5. **Separate the obligation streams.** A first final rule in one stream (issuer
   licensing, capital, reserves) says nothing about another (AML/CFT, sanctions,
   customer identification). Programs map controls to final text, so a stream that
   is entirely proposed is a stream with nothing final to map to yet.

### Worked example: GENIUS Act implementing rules (snapshot 2026-10-25)

Built with the method above from the live Federal Register API on 2026-10-25. Two
quoted term searches (`"payment stablecoin"`, `"GENIUS Act"`, rule and proposed-rule
types, published on or after the 2025-07-18 enactment) returned 27 documents each,
29 in union. Both included out-of-scope hits, among them a tax rule on tipped
occupations, which is why step 2 exists. Re-run before relying on any row.

**Issuer framework**

| Agency | RIN | Document(s) | Status | Key date |
|---|---|---|---|---|
| OCC | 1557-AF41 | 91 FR 10202 (proposed 2026-03-02) → **91 FR 67000** (2026-10-23) | **Final** | Effective 2027-01-18 |
| Treasury | 1505-AC97 | 91 FR 61688 (2026-09-30), state-certification review forms and procedures | **Final** (procedural) | Effective 2026-09-30 |
| Treasury | 1505-ZA10 | 90 FR 45159 (2025-09-19), 90 FR 47251 (2025-10-01) | Proposed-rule documents | Comments closed 2025-11-04 |
| Treasury | 1505-AC90 | 91 FR 16844, principles for "substantially similar" state regimes | Proposed | Comments closed 2026-06-02 |
| Treasury | 1505-AC95 | 91 FR 53368, issuance, offer and sale | Proposed | Comments closed 2026-10-19 |
| FDIC | 3064-AG20 | 90 FR 59409, 91 FR 6138, subsidiary approval | Proposed | Comments closed 2026-05-18 |
| FDIC | 3064-AG19 | 91 FR 18534, requirements and standards | Proposed | Comments closed 2026-06-09 |
| NCUA | 3133-AF69, 3133-AG10 | 91 FR 6531, 91 FR 28956 | Proposed | Comments closed 2026-04-13, 2026-07-17 |
| Federal Reserve | 7100-AH29, 7100-AH30 | 91 FR 61580, 91 FR 61346 | Proposed | Comments close 2026-11-30 |

**Issuer AML/CFT, sanctions and customer identification**

| Agency | RIN | Document | Status | Comment close |
|---|---|---|---|---|
| FinCEN and OFAC | 1506-AB73 | 91 FR 18582, issuer AML/CFT program and sanctions compliance | Proposed | 2026-06-09 |
| FinCEN | 1506-AB74 | 91 FR 37234, issuer customer identification program | Proposed | 2026-08-21 |
| OCC | 1557-AF55 | 91 FR 37840, issuer AML/CFT and sanctions compliance | Proposed | 2026-07-24 |
| FDIC | 3064-AG29 | 91 FR 34171, issuer BSA and sanctions compliance | Proposed | 2026-08-04 |

Adjacent and not counted above: three bank-wide AML/CFT program proposals that
reference payment stablecoins (FinCEN 1506-AB72; OCC/FDIC/NCUA 1557-AF14; Federal
Reserve 7100-AG78). The last two carry the same RINs as the 2024 program-rule
proposal at 89 FR 65242, so they are re-proposals of an existing rulemaking, not new
GENIUS rulemakings.

What the snapshot supports: one substantive final rule exists, from one primary
regulator, in the issuer-framework stream. Its effective date falls exactly 18 months
after enactment. In the AML/CFT, sanctions and customer-identification stream, all
four issuer-specific RINs are still proposed. A program can map its issuer-licensing
work to final OCC text today. It cannot yet map issuer AML, sanctions or CIP controls
to any final rule.

What it does not support: any claim about the content of the final rule beyond its
publication facts, or about when the proposed rules will finalize. Read the rule
text for the first; watch the OIRA review queue for the second.

---

## Output format

A standard structure for a regulatory alert. It leads with severity and category
so a reader can triage before reading the body.

```
REGULATORY ALERT — [Date]
SEVERITY: [CRITICAL / HIGH / MEDIUM / LOW]
CATEGORY: [Legislation / Enforcement / Guidance / Sanctions]

DEVELOPMENT
[A one-to-two-sentence summary.]

DETAILS
[Three to five sentences with the specifics.]

IMPACT ASSESSMENT
- Who is affected: [Entity types]
- What changes:    [Policy and procedure implications]
- Timeline:        [Effective dates, compliance deadlines]

REQUIRED ACTIONS
1. [Specific action]
2. [Specific action]

SOURCE: [URL or citation]
```

---

## Related references

- [`aml-typologies.md`](aml-typologies.md) — the regulatory framework in depth,
  plus crypto laundering typologies
- [`compliance-documents.md`](compliance-documents.md) — turning regulatory
  change into updated policies and controls
