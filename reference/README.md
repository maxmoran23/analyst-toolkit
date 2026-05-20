# Reference

Domain cheat-sheets — the *what you need to know* half of the toolkit. Where
[`methodology/`](../methodology/) defines how to think and write,
these documents supply the subject-matter knowledge: the frameworks, document
structures, regulatory citations, and typologies that compliance, audit,
regulatory, and financial work depend on.

Use them as a fast lookup while running a prompt, or as a primer before tackling
an unfamiliar domain.

---

## The five references

| Document | Covers |
|----------|--------|
| [`aml-typologies.md`](aml-typologies.md) | Crypto / digital-asset AML: the US and international regulatory frameworks, fifteen core laundering typologies with detection signals, an 8-dimension risk-scoring model, and key risk indicators. |
| [`compliance-documents.md`](compliance-documents.md) | Document structures for compliance work: enhanced due diligence reports, AML/CFT risk assessments, control matrices, SAR narratives, policy documents, and transaction-monitoring rule documentation. |
| [`audit-documentation.md`](audit-documentation.md) | Internal-audit and SOX-style work: testing workpapers, sample selection, deficiency classification, and the audit-trail finding structure. |
| [`regulatory-intelligence.md`](regulatory-intelligence.md) | Tracking regulatory change: the source hierarchy, the six analysis dimensions, tracking categories, the key regulatory bodies, and a regulatory-alert output format. |
| [`financial-analysis.md`](financial-analysis.md) | Financial modeling: variance analysis, financial-statement analysis, scenario modeling, and portfolio analysis. |

---

## How the references connect

The compliance and regulatory documents form a chain — regulatory change flows
into compliance documentation, which is then tested by audit:

```
regulatory-intelligence.md  →  a new rule or enforcement action is identified
        │
        ▼
aml-typologies.md           →  the framework and typologies it touches
        │
        ▼
compliance-documents.md     →  updated policies, controls, risk assessments
        │
        ▼
audit-documentation.md      →  the controls are tested for effectiveness
```

`financial-analysis.md` stands somewhat apart — it supports the financial-health
dimension of an EDD assessment, the quantitative side of a risk model, and
standalone financial work.

---

## Using these with the methodology

The references supply *content*; the methodology supplies *standard*. Every
reference here defers to two methodology documents:

- [`../methodology/audit-defensible-writing.md`](../methodology/audit-defensible-writing.md)
  — the writing voice every compliance and analytical document should use.
- [`../methodology/analytical-patterns.md`](../methodology/analytical-patterns.md)
  — severity tiers, the source hierarchy, and the observed/alleged/projected
  discipline that compliance and regulatory findings depend on.

A document built from these references but written without that standard is data
without rigor. Use both halves of the toolkit together.

---

## A note on currency

Regulatory frameworks change — legislation passes, agencies issue new guidance,
sanctions designations are added and withdrawn. The framework tables in these
references are a starting map, accurate to a point in time. Before relying on any
specific rule, citation, or threshold, confirm its current state against the
issuing body. These are reference cheat-sheets, not a substitute for the primary
source — or for legal advice.
