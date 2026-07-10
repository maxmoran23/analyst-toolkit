# Source Library — Jurisdiction-Risk Framework

Where each of the engine's seven dimensions is drawn from: the authoritative **public**
index, what it measures, its edition cadence, and the retrieval discipline. The engine
composites normalized sub-scores; this document is where those raw values come from. The
cross-workflow master is
[`../../reference/osint-source-library.md`](../../reference/osint-source-library.md) (§7).

> Public sources only. Commercial country-risk products sit on top of this free
> baseline; the compositing discipline below is identical whichever you use. Nothing
> here redistributes index data — each row is a pointer you retrieve yourself.

---

## The compositing indices (the weighted dimensions)

| Dimension | Index | URL | Measures | Cadence | Tier |
|---|---|---|---|---|---|
| AML/CFT deficiency | Basel AML Index | `index.baselgovernance.org` | Composite ML/TF country risk (0-10) | Annual | T1 |
| Corruption | Transparency International CPI | `transparency.org/en/cpi` | Perceived public-sector corruption (0-100) | Annual | T1 |
| Corruption / Governance | World Bank WGI | `worldbank.org` (WGI) | Rule of law; control of corruption (percentiles) | Annual | T1 |
| Financial secrecy | Tax Justice Financial Secrecy Index | `fsi.taxjustice.net` | Secrecy / haven scoring | Biennial | T1 |
| Organized crime | Global Organized Crime Index | `ocindex.net` | Organized-crime prevalence + resilience | Periodic | T2 |
| Terrorism | Global Terrorism Index | `visionofhumanity.org` | Terrorism impact | Annual | T2 |
| Instability | Fragile States Index | `fragilestatesindex.org` | State fragility / political instability | Annual | T2 |

## The categorical designations (the hard-risk floors)

These are not weighted into the composite — they force a minimum tier. Each is an
authoritative T1 determination; retrieve the current version, never a cached copy.

| Designation | Source | URL | Floor |
|---|---|---|---|
| FATF high-risk & monitored jurisdictions (black / grey list) | FATF | `fatf-gafi.org` | CRITICAL / HIGH |
| EU list of high-risk third countries | European Commission | `finance.ec.europa.eu` | HIGH |
| INCSR Vol. II money-laundering assessment (primary concern) | US State Department | `state.gov` | HIGH |
| Comprehensive sanctions program | OFAC / EU / UN | see [master §1](../../reference/osint-source-library.md#1-sanctions--watchlist-screening) | CRITICAL |

## Retrieval discipline

- **Record the edition.** Every raw value carries the index name and edition/year. A
  score without its edition is not reproducible; the engine's `reason` and the evidence
  pack both assume every input is dated.
- **Designations are strict and time-sensitive.** FATF updates its lists roughly three
  times a year; check the current statement of record, not a summary. A grey/black
  listing is a categorical floor, not one input among many.
- **Missing is missing, not zero.** If a dimension has no current data for a
  jurisdiction, mark it absent — the engine excludes it and renormalizes the weights
  rather than scoring it as zero or a midpoint, and the confidence in the rating drops.
- **Composite, never single-source.** A defensible geographic rating rests on several of
  these indices with a documented weighting. A single index cited alone is not a
  jurisdiction risk assessment.

## Action-item scoping — what each tier triggers

| Tier | Typical action (a human decides) |
|---|---|
| **CRITICAL** | Prohibitive without senior/committee sign-off; comprehensive EDD; enhanced ongoing monitoring; consider whether the exposure is permissible at all. |
| **HIGH** | Enhanced due diligence, source-of-funds/wealth corroboration, senior approval, and a defined re-score trigger (e.g. next FATF plenary). |
| **MEDIUM** | Standard-plus diligence; monitor the drivers that could move the tier. |
| **LOW** | Standard diligence; periodic refresh on the index cycle. |

The tier scopes the work; it never makes the decision. Pair with the paste-in analyst
workflow [`../../prompts/compliance/jurisdiction-risk-osint.md`](../../prompts/compliance/jurisdiction-risk-osint.md)
for a one-off, documented composite with its sources cited.
