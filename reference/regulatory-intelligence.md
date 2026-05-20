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
