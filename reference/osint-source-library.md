# OSINT Source Library — authoritative public sources for financial-crime work

A curated, tiered whitelist of **public** sources for open-source intelligence in
financial-crime analysis: sanctions and watchlist screening, PEP research, corporate
registry and beneficial-ownership tracing, adverse-media screening, court and litigation
records, blockchain intelligence, jurisdiction risk, regulatory and enforcement tracking,
and securities/market checks.

It exists because the hard part of OSINT is rarely the analysis — it is knowing *which*
source is authoritative for *which* question, how far to trust it, and how to record it so
the work survives review. This document answers those three questions for each source.

> **What this is not.** It is not a data feed and it redistributes no list data. Every
> source below is a pointer to a public resource you retrieve yourself at the time of use.
> Aggregators are listed as a convenience; an aggregator is never the authority. Before any
> reliance, a hit must be confirmed against the **primary, official source** named in the
> Tier-1 row.

---

## How to use this library

1. **Start from the workflow, not the source.** Find your task below (screening a name,
   unwinding an ownership chain, dispositioning a negative-news hit) and work the Tier-1
   sources first.
2. **Tier discipline.** Trust flows down, never up:

   | Tier | Meaning | How a hit from it may be used |
   |------|---------|-------------------------------|
   | **T1 — Authoritative** | The official issuer of the fact: a government sanctions list, a company registry of record, a court's own docket, an issuer's own filing. | May be relied on, cited by URL + retrieval date. Still confirm identity (right party). |
   | **T2 — Reputable secondary** | A serious, accountable aggregator or investigative body that curates from T1 (OpenSanctions, GLEIF, ICIJ, established newswires). | A strong lead and a pointer *to* the T1 source. Confirm against T1 before reliance. |
   | **T3 — Open / user-generated** | Search engines, wikis, crowd-sourced tags, social media, block-explorer name-tags. | A lead only. Never a finding on its own. Requires independent corroboration. |

3. **Provenance on every fact.** Record, for every retrieved fact: the source name, the
   full URL, the retrieval date (and time for volatile data), and the tier. A fact you
   cannot re-locate is a lead, not evidence. This mirrors the discipline the runnable
   engines enforce in code — see [`../frameworks/onchain-osint-evidence/`](../frameworks/onchain-osint-evidence/).
4. **Right-party before adverse.** A name, address, or entity match is not a subject match.
   Resolve identity (date of birth, jurisdiction, identifiers, corroborating attributes)
   *before* treating anything the source says as being about your subject.
5. **Respect access terms.** Use official APIs and public search where offered. Do not
   defeat access controls, scrape against a site's terms, or rely on paywalled content you
   are not licensed for. "Public" here means lawfully and openly accessible.
6. **Sanctions are strict-liability — lists change.** A clear screen is only clear as of the
   list version you checked. Always screen against the current authoritative list, never a
   cached copy.

---

## 1. Sanctions & watchlist screening

The question: *is this name, entity, vessel, or address on a list that legally restricts
dealing with it?*

| Source | Coverage | Best for | Access | Tier |
|--------|----------|----------|--------|------|
| **OFAC SDN & Consolidated (Non-SDN) lists** — `sanctionssearch.ofac.treas.gov`, list files at `ofac.treasury.gov` | US designations (SDN, SSI, FSE, NS-CMIC, etc.), incl. crypto addresses | The authoritative US screen | Free search + downloadable CSV/XML | T1 |
| **US Consolidated Screening List (CSL)** — `trade.gov/consolidated-screening-list` | 11 US export/sanctions lists incl. BIS Entity List, DDTC | One-stop US export + sanctions screen | Free search + API + CSV | T1 |
| **EU Consolidated Financial Sanctions List (FSF)** — `webgate.ec.europa.eu/fsd/fsf`; map at `sanctionsmap.eu` | EU-wide asset-freeze designations | The authoritative EU screen | Free (registration for the data file) | T1 |
| **UK OFSI Consolidated List** — `gov.uk` (financial sanctions targets) | UK asset-freeze targets | The authoritative UK screen | Free downloadable list | T1 |
| **UN Security Council Consolidated List** — `un.org/securitycouncil` | UN-mandated designations (all member states) | Multilateral baseline | Free downloadable list | T1 |
| **World Bank / MDB debarment lists** — `worldbank.org` (ineligible firms), plus AfDB/ADB/IADB/EBRD | Procurement debarment (fraud/corruption) | Vendor & third-party integrity | Free | T1 |
| **INTERPOL Notices (Red/others)** — `interpol.int` | Wanted-person and related notices | Law-enforcement interest as a lead | Free public extracts | T2 |
| **OpenSanctions** — `opensanctions.org` | Aggregates 200+ sanctions, PEP, watchlist, debarment sources | Fast cross-list first pass; entity graph | Free search + bulk/API | T2 |

**Retrieval discipline.** Screen the *authoritative* list for the relevant jurisdiction(s),
not only an aggregator. Capture the list version/date. Treat name-only matches as unresolved
until an identifier (DOB, passport, registration number, address) confirms the party. Fuzzy
and transliteration variants matter — see [`../frameworks/sanctions-name-screening/`](../frameworks/sanctions-name-screening/).

---

## 2. Politically exposed persons (PEPs)

The question: *is this person a PEP or close associate, and at what prominence, so I can
scope enhanced due diligence?* There is **no single authoritative free global PEP list**;
build from primary position-of-office records and corroborate.

| Source | Coverage | Best for | Access | Tier |
|--------|----------|----------|--------|------|
| **National parliament / government / gazette sites** | The office-holder's own jurisdiction | Confirming a current or former public function (the definitional test) | Free, varies by country | T1 |
| **US Senate/House financial disclosures; OGE** — `disclosures-clerk.house.gov`, `efd.senate.gov` | US federal officials | US PEP confirmation + interests | Free | T1 |
| **OpenSanctions PEP dataset** — `opensanctions.org/datasets/peps` | Global PEP positions curated from public sources | First-pass PEP screen and position history | Free search + bulk | T2 |
| **Wikidata** — `wikidata.org` | Structured "position held" statements with dates | Machine-readable office history and relatives | Free SPARQL/API | T2/T3 |
| **GLEIF LEI** — `search.gleif.org` | Legal entities the PEP is tied to | Linking a PEP to companies | Free | T1 |

**Retrieval discipline.** PEP status is about a *function*, not a person's fame. Record the
office, the dates held, the jurisdiction, and the prominence tier; separate the principal
from associates. A former PEP may step down in risk over time — capture the end date. See
[`../frameworks/pep-screening/`](../frameworks/pep-screening/).

---

## 3. Corporate registries & beneficial ownership

The question: *who legally owns and controls this entity, and can I walk the chain to a
natural person?*

| Source | Coverage | Best for | Access | Tier |
|--------|----------|----------|--------|------|
| **GLEIF LEI Search** — `search.gleif.org` | Global legal entities with an LEI; "direct/ultimate parent" relationships | Cross-border entity ID and parentage | Free search + API + bulk | T1 |
| **UK Companies House** — `find-and-update.company-information.service.gov.uk` | UK companies, officers, and the PSC (people-with-significant-control) register | Officers + declared beneficial owners | Free search + API | T1 |
| **US SEC EDGAR** — `sec.gov/edgar`, full-text `efts.sec.gov` | US public issuers and many funds | Ownership (SC 13D/G, Forms 3/4/5), filings, related parties | Free search + API | T1 |
| **US state Secretary of State registries** — e.g. Delaware `icis.corp.delaware.gov` | US company formation, agents, status | Existence, status, registered agent | Free/low-cost, varies | T1 |
| **EU Business Registers (BRIS) via e-Justice** — `e-justice.europa.eu` | Interconnected EU member-state registers | EU company existence and basic data | Free portal | T1 |
| **OpenCorporates** — `opencorporates.com` | 200M+ companies aggregated from official registries | Fast multi-jurisdiction lookup + officer network | Free search; API | T2 |
| **OpenOwnership Register** — `register.openownership.org` | Cross-border beneficial-ownership statements | Declared BO across jurisdictions | Free | T2 |
| **ICIJ Offshore Leaks Database** — `offshoreleaks.icij.org` | Entities/officers from Panama, Paradise, Pandora leaks | Offshore-structure leads | Free | T2 |
| **OCCRP Aleph** — `aleph.occrp.org` | Registries, leaks, and documents cross-indexed | Deep investigative cross-reference | Free (registration) | T2 |

> **Note on registers of record vs. leaks.** A registry of record (Companies House, SEC,
> GLEIF) is T1 for what the entity *declared*; a leak database (ICIJ, OCCRP) is a T2 lead
> that must be confirmed against a register or filing. The US FinCEN beneficial-ownership
> (BOI) registry is **not public** — do not represent BOI data as OSINT.

**Retrieval discipline.** Walk each layer with its own citation; compute effective ownership
as the product along each path; flag opacity (nominee directors, bearer shares, secrecy
jurisdictions, circular ownership) as findings, not conclusions. See
[`../prompts/compliance/ubo-beneficial-ownership.md`](../prompts/compliance/ubo-beneficial-ownership.md).

---

## 4. Adverse media / negative news

The question: *is there credible public reporting of conduct that matters to my risk
decision — and is it actually adverse, actually about my subject, and still relevant?*

Prefer **primary** sources of the underlying event (a regulator's or prosecutor's own
release, a court filing) over the reporting about it. Tier the outlet.

| Source | Coverage | Best for | Access | Tier |
|--------|----------|----------|--------|------|
| **DOJ / SEC / CFTC / FinCEN / FCA / FINRA press & enforcement pages** — `justice.gov/news`, `sec.gov/news/pressreleases`, `cftc.gov`, `fincen.gov/news-room`, `fca.org.uk/news`, `finra.org` | Official enforcement and charging announcements | The primary, most defensible adverse source | Free | T1 |
| **Court dockets / releases** (see §5) | The underlying legal action | Confirming an allegation vs. a conviction | Mixed | T1 |
| **Established newswires & investigative outlets** — Reuters, AP, Bloomberg, FT, and ICIJ / OCCRP / bellingcat for investigations | Global reporting | Corroboration and context | Free/paywalled | T2 |
| **GDELT Project** — `gdeltproject.org` | Structured global news-event index | Screening for events at scale; timelines | Free (BigQuery/API) | T2/T3 |
| **General web / search engines** | Everything else | Discovery and leads | Free | T3 |

**Retrieval discipline.** Distinguish **allegation** from **finding** from **conviction**;
distinguish subject-as-**perpetrator** from subject-as-**victim/witness**; weigh **recency**
and **materiality**; and never clear or damn a subject on a bare name match. This is exactly
what the runnable engine encodes — see [`../frameworks/adverse-media-screening/`](../frameworks/adverse-media-screening/)
and its focused whitelist in that folder's `SOURCE-LIBRARY.md`.

---

## 5. Court records & litigation

| Source | Coverage | Best for | Access | Tier |
|--------|----------|----------|--------|------|
| **CourtListener / RECAP** — `courtlistener.com` | US federal (and some state) dockets and opinions | Free access to federal filings and opinions | Free + API | T1/T2 |
| **PACER** — `pacer.uscourts.gov` | US federal dockets of record | Authoritative federal docket | Paid | T1 |
| **SEC Litigation Releases** — `sec.gov/litigation` | SEC civil actions | Securities enforcement detail | Free | T1 |
| **UK Courts & Tribunals; The Gazette** — `gov.uk/find-court-tribunal`, `thegazette.co.uk` | UK judgments; insolvency/statutory notices | UK litigation and insolvency | Free | T1 |
| **State / national court portals** | Local jurisdiction | Where the matter actually sits | Varies | T1 |

**Retrieval discipline.** Capture the case number, court, filing date, and stage. A civil
complaint is an allegation; a judgment or plea is a finding. Note appeals and sealings.

---

## 6. Blockchain / on-chain intelligence

The question: *what does the public ledger show about this address, token, or protocol — and
who, if anyone, does a public source attribute it to?*

| Source | Coverage | Best for | Access | Tier |
|--------|----------|----------|--------|------|
| **OFAC SDN crypto addresses** (within the SDN list, §1) | US-designated addresses | The authoritative on-chain sanctions screen | Free | T1 |
| **Issuer freeze lists** — Tether / Circle publish on-chain blocked addresses | USDT/USDC frozen addresses | Confirming a stablecoin issuer block | Free (on-chain / issuer) | T1 |
| **Etherscan & family** — `etherscan.io`, `bscscan.com`, `arbiscan.io`, `polygonscan.com`, `tronscan.org`, `solscan.io` | Per-chain transactions, tokens, contracts, public name-tags | Native-chain evidence capture | Free + API | T1 (facts) / T3 (labels) |
| **Blockchair** — `blockchair.com` | Multi-chain explorer + search | Cross-chain lookups in one place | Free + API | T2 |
| **mempool.space / Blockstream.info** — `mempool.space` | Bitcoin | BTC transaction/UTXO detail | Free | T1 |
| **Chainabuse** — `chainabuse.com` | Community-reported scam/abuse addresses | Fraud/scam leads | Free | T3 |

> **Explorer name-tags are T3.** A public "Exchange: Hot Wallet" tag is a single-source
> lead about the *service* operating an address — never proof that a natural person owns or
> transacted through it. Keep the observation/attribution firewall: facts about addresses ≠
> claims about identity.

**Retrieval discipline.** Capture each explorer page with URL + retrieval date; reconcile
extracted totals to the explorer's own summary; deduplicate paginated rows; exclude dust and
unsolicited-token noise from flow conclusions. The engine that enforces all of this is
[`../frameworks/onchain-osint-evidence/`](../frameworks/onchain-osint-evidence/) (with its own
`SOURCE-LIBRARY.md`); the paste sibling is
[`../prompts/blockchain/block-explorer-osint.md`](../prompts/blockchain/block-explorer-osint.md).

---

## 7. Jurisdiction / country risk

The question: *how much inherent AML/CFT, corruption, secrecy, and instability risk does a
country carry?* Composite the recognized public indices; never rely on one.

| Source | Measures | Cadence | Access | Tier |
|--------|----------|---------|--------|------|
| **FATF high-risk & monitored jurisdictions** — `fatf-gafi.org` | The "black" and "grey" lists (AML/CFT deficiencies) | ~3x/year | Free | T1 |
| **EU list of high-risk third countries** — `finance.ec.europa.eu` | EU AML high-risk designations | Periodic | Free | T1 |
| **Basel AML Index** — `index.baselgovernance.org` | Composite ML/TF country risk | Annual | Free (registration) | T1 |
| **Transparency International CPI** — `transparency.org/en/cpi` | Perceived public-sector corruption | Annual | Free | T1 |
| **Tax Justice Financial Secrecy Index** — `fsi.taxjustice.net` | Financial secrecy / haven scoring | Biennial | Free | T1 |
| **World Bank Worldwide Governance Indicators** — `worldbank.org` (WGI) | Rule of law, control of corruption, etc. | Annual | Free | T1 |
| **US State Dept INCSR Vol. II** — `state.gov` | Money-laundering country assessments | Annual | Free | T1 |
| **Global Organized Crime Index** — `ocindex.net` | Organized-crime prevalence + resilience | Periodic | Free | T2 |
| **Fragile States Index; Global Terrorism Index; Freedom House** — `fragilestatesindex.org`, `visionofhumanity.org`, `freedomhouse.org` | Instability; terrorism; political freedom | Annual | Free | T2 |

**Retrieval discipline.** Record each index's edition/year and the raw score, then combine
with a documented weighting — do not eyeball. A composite is defensible; a single index cited
alone is not. (A runnable country-risk engine over these indices is a planned framework — see
`HANDOFF.md`.)

---

## 8. Regulatory & enforcement tracking

| Source | Coverage | Best for | Access | Tier |
|--------|----------|----------|--------|------|
| **FFIEC BSA/AML Examination Manual** — `bsaaml.ffiec.gov/manual` | US examination expectations | The control-design and exam baseline | Free | T1 |
| **FinCEN** — `fincen.gov` | US advisories, rules, SAR guidance | Typology advisories + rulemaking | Free | T1 |
| **FATF** — `fatf-gafi.org` | Standards, guidance, mutual evaluations | International standard of record | Free | T1 |
| **Federal banking regulators** — OCC, FDIC, Federal Reserve enforcement actions | US bank enforcement | Precedent and expectations | Free | T1 |
| **EBA / ESMA / national regulators** — e.g. FCA, BaFin | EU/UK regulatory action | Non-US regulatory intelligence | Free | T1 |

See also [`regulatory-intelligence.md`](regulatory-intelligence.md) for the tracking method.

---

## 9. Securities & market participants

| Source | Coverage | Best for | Access | Tier |
|--------|----------|----------|--------|------|
| **SEC EDGAR** — `sec.gov/edgar` | US issuer filings | Financials, ownership, related parties | Free + API | T1 |
| **FINRA BrokerCheck** — `brokercheck.finra.org` | US brokers & firms | Registration + disclosure history | Free | T1 |
| **SEC IAPD** — `adviserinfo.sec.gov` | US investment advisers | Adviser registration + disclosures | Free | T1 |
| **GLEIF** — `search.gleif.org` | Legal-entity identifiers | Counterparty entity ID | Free | T1 |

---

## Recording a source in an evidence annex (the citation standard)

Every retrieved fact carries, at minimum:

```
[S#] Source name — full URL — retrieved YYYY-MM-DD (HH:MM TZ if volatile) — Tier T1/T2/T3
     what it establishes (one line) — corroboration: CORROBORATED / SINGLE-SOURCE / LEAD
```

A fact with no `[S#]` is removed, not footnoted. A T2/T3 fact relied on for a conclusion must
carry a corroborating T1 `[S#]` or be downgraded to a lead. This is the same provenance
contract the [`onchain-osint-evidence`](../frameworks/onchain-osint-evidence/) engine enforces
in code, generalized to every OSINT workflow above.

---

## Scope, boundaries, and caution

- **Public only.** Everything here is lawfully and openly accessible. Nothing on this page is
  proprietary, licensed-feed, or non-public data, and none of it is employer-specific.
- **Aggregators are convenience, not authority.** Confirm against the Tier-1 issuer before any
  reliance, especially for sanctions (strict liability) and ownership (legal effect).
- **Terms of service and law govern access.** Use official APIs and public search; do not
  defeat access controls or scrape against terms. Licensed/commercial tools (Chainalysis, TRM,
  Dow Jones, LexisNexis, Refinitiv, Moody's) are deliberately out of scope here — this library
  is the free, public-source baseline they sit on top of.
- **A source is a lead until identity is resolved.** The whole library serves one rule: find the
  authoritative fact, confirm it is about your subject, and record it so a reviewer can re-walk
  every step.
