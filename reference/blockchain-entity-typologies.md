# Blockchain Entity Typologies

A classification reference for **what kind of entity you are assessing** when that
entity touches blockchain. Where [`aml-typologies.md`](aml-typologies.md) catalogs
*laundering patterns* — the behaviors detection logic targets — this document
catalogs *entity types*: the structural categories a counterparty, customer, or
investment target falls into, and how that category changes the risk analysis.

The premise: **classify before you score.** A centralized exchange, a DeFi
protocol, a DAO with no legal wrapper, a bitcoin miner, and a software company
that merely holds bitcoin on its balance sheet are five different risk problems.
Assessing them with one undifferentiated checklist produces inconsistent,
un-defensible results. Identifying the typology first tells you which regulatory
regimes attach, which risk dimensions dominate, and what evidence to demand.

All citations point to public bodies and public documents. This is general
domain reference, not legal advice.

---

## The four families

Every blockchain-touching entity falls into one of four families. The family
determines the single most important analytical question.

| Family | What it is | The central question |
|--------|-----------|----------------------|
| **Native digital-asset business** | The entity's core business *is* a digital-asset service. Generally a VASP under FATF terminology; frequently a money services business (MSB) under US law. | Is it registered/licensed for every activity in every jurisdiction it serves? |
| **Protocol-native / decentralized** | A decentralized protocol, network, or governance organization. May have no conventional legal entity at all. | Who, if anyone, is the accountable owner or operator? |
| **Blockchain-exposed traditional entity** | A traditional (non-crypto-service) entity carrying material blockchain exposure — a balance-sheet crypto position, crypto-derived revenue, or a crypto product line. *The exposure is the risk; the entity is not a VASP.* | How large is the exposure relative to the balance sheet, and how is it funded? |
| **Traditional (baseline)** | No material blockchain nexus. The standard entity risk assessment applies unchanged. | — |

The distinction that most often goes wrong is **operational vs. situational
exposure**. A native digital-asset business *operates* a service — it is subject
to VASP/MSB obligations. A blockchain-exposed entity merely *holds* exposure — it
is not a VASP, and applying VASP licensing tests to it is an analytical error.
A software company with bitcoin on its balance sheet is not an unlicensed money
transmitter.

---

## The classification protocol

1. **Identify the primary activity.** Classify by what the entity primarily
   does, not by what it is adjacent to.
2. **Record secondary typologies.** Many entities span several — a single brand
   may be a protocol, a development company, *and* a DAO. Assess the dominant
   typology as primary; note the others as context.
3. **Tag the life stage** — public, private, or early-stage — independently of
   typology. A private entity has no public financials; that is an information
   gap to document, never a risk score to inflate.
4. **If nothing fits, that is a framework gap.** Add a typology rather than
   improvising a one-off method. Congruence across assessments is the goal:
   the next entity of a given type should be assessed the way the last one was.

---

## Family 1 — Native digital-asset businesses (VASPs)

| Typology | What it is | Regulatory lens | Primary risk dimensions |
|----------|-----------|-----------------|-------------------------|
| **Centralized exchange (CEX)** | Custodial venue matching orders, holding customer fiat and digital assets | FinCEN MSB, state money-transmitter licensing, FATF VASP + Travel Rule, securities law if listing tokens | Regulatory, Sanctions, Geographic |
| **Stablecoin issuer** | Issues and redeems a fiat- or asset-referenced token against a reserve | Payment-stablecoin law, MSB/state licensing, securities law if asset-referenced | Financial (reserve quality), Regulatory |
| **Custodian / crypto bank** | Qualified custody of digital assets, often under a trust or bank charter | OCC / state trust charter, qualified-custodian rules, FATF VASP | Regulatory, Governance, Financial |
| **Infrastructure / technology provider** | B2B wallet, node, analytics, or tokenization technology; often never touches customer funds | Vendor-risk regime; *not* a VASP if it never controls customer assets | Governance, Regulatory |
| **Fiat on-ramp / payment processor** | Converts fiat to digital assets at point of purchase | MSB, state licensing, card-network rules, FATF VASP + Travel Rule | Regulatory, Sanctions |
| **OTC desk / crypto broker-dealer** | Principal or agency block trading off public order books | MSB, broker-dealer / commodities registration | Regulatory, Financial, Sanctions |
| **Mining operation** | Operates proof-of-work hardware for block rewards; frequently a public company | Securities law if public, energy/environmental regulators; *not* a VASP | Financial, Geographic, ESG |
| **Staking-as-a-service / validator operator** | Runs validator infrastructure for clients on proof-of-stake networks | Securities law (staking products), MSB (fact-dependent) | Regulatory, Governance |
| **Crypto fund / asset manager** | Investment manager deploying capital into digital assets | Investment-adviser and fund regulation, custody rule | Regulatory, Governance |
| **Crypto lending / yield platform** | Takes customer deposits and pays yield; lends or rehypothecates | Securities law (yield products), state regulators; high historical failure rate | Regulatory, Financial, Litigation |

## Family 2 — Protocol-native / decentralized

| Typology | What it is | Regulatory lens | Primary risk dimensions |
|----------|-----------|-----------------|-------------------------|
| **L1 / L2 network + foundation** | A base- or scaling-layer blockchain, stewarded by a foundation | Securities law (native token), foundation-jurisdiction law, network-level illicit-finance exposure | Regulatory, Sanctions, Governance |
| **DeFi protocol** | Smart contracts providing a financial service with no custodial intermediary | FATF owner/operator test, securities/commodities law for the front-end operator and token | Governance, Regulatory, Sanctions |
| **DAO** | Token-holder-governed organization directing a protocol or treasury | Unincorporated-association / partnership liability; DAO-LLC statutes; securities law | Governance, Regulatory, Financial |
| **Liquid staking protocol** | Pools staked assets and issues a liquid staking token | Securities law, FATF owner/operator; systemic-concentration scrutiny if dominant | Governance, Regulatory, Financial |
| **Privacy tool / mixer** | Obfuscates the on-chain link between source and destination of funds | Sanctions-designation and operator-prosecution precedent; the highest-inherent-risk typology | Sanctions, Regulatory, Governance |
| **Cross-chain bridge** | Locks assets on one chain, mints representations on another | FATF owner/operator, sanctioned-flow conduit risk; a high-exploit category | Sanctions, Governance, Regulatory |
| **NFT marketplace / platform** | Venue for minting, listing, and trading non-fungible tokens | Securities law (investment-themed NFTs), AML for art-market intermediaries | Regulatory, Litigation, Adverse Media |
| **Protocol development company ("Labs" entity)** | The conventional company that builds and operates a protocol's front-end | Securities/commodities law — the suable party behind a "decentralized" protocol | Regulatory, Governance, Financial |

## Family 3 — Blockchain-exposed traditional entities

| Typology | What it is | Regulatory lens | Primary risk dimensions |
|----------|-----------|-----------------|-------------------------|
| **Corporate treasury holder** | A traditional company holding a material crypto position as a treasury asset | Securities-disclosure and fair-value accounting; **not a VASP** | Financial, Governance, Regulatory |
| **Spot crypto ETF / ETP issuer** | A regulated fund sponsor offering an exchange-traded product holding digital assets | Securities law, exchange listing rules, custodian oversight | Regulatory, Financial, Governance |
| **Bank / FI with crypto activity** | A chartered institution offering crypto custody, settlement, or trading | Prudential banking regulators, crypto-specific supervisory guidance, BSA/AML | Regulatory, Financial, Governance |
| **Public fintech with crypto-derived revenue** | A payments or fintech company with a material crypto revenue line | Securities disclosure, MSB for the crypto feature, consumer-protection regime | Regulatory, Financial, Adverse Media |
| **Crypto-adjacent service vendor** | A professional-services or counterparty firm whose risk depends on *which* crypto clients it serves | Profession-specific regulation; gatekeeper / aiding-and-abetting exposure | Regulatory, Litigation, Adverse Media |

*Family 4 — traditional public and private companies with no blockchain nexus —
uses the standard [entity risk assessment](../prompts/compliance/entity-risk-assessment.md)
unchanged.*

---

## The crypto-service exposure framework

Risk attaches to a blockchain entity through the **service or activity** it
performs. Each activity creates a characteristic exposure — and the same activity
performed *operationally* (as a service) versus *situationally* (as incidental
exposure) carries different obligations.

| Activity | Characteristic exposure | What evidence reveals it |
|----------|------------------------|--------------------------|
| **Custody** | Loss of customer assets; commingling; bankruptcy-remoteness failure | Segregation disclosures, proof-of-reserves, insurance, SOC attestation |
| **Exchange / trading** | Unregistered operation, market manipulation, listing of unregistered securities | Licensing records, listing practices, surveillance posture |
| **Issuance** | Reserve-backing opacity; redemption failure; depeg | Reserve attestation/audit, redemption history, reserve composition |
| **Lending / yield** | Unregistered securities offering; asset-liability mismatch; run risk | Product registration, rehypothecation disclosure, redemption-suspension history |
| **Staking** | Securities treatment of the product; slashing risk passed to clients | Custody model (delegated vs. pooled), validator concentration, enforcement history |
| **Mining** | Energy-jurisdiction concentration; capital-intensity leverage | Power agreements, environmental permits, mined-asset treasury exposure |
| **Mixing / privacy** | Designation and prosecution exposure; sanctioned-actor use | Designation status, control framework (or its absence), illicit-flow analysis |
| **Bridging** | Exploit history; use as a sanctioned-fund laundering conduit | Audit and exploit record, validator trust model, sanctioned-flow throughput |
| **Treasury holding (situational)** | Volatility relative to the balance sheet; leverage funding the position | Filings disclosing the position, the debt/equity funding it, custodian identity |
| **Vendor / counterparty (situational)** | Concentration in high-risk crypto clients; reputational contagion | Client-portfolio concentration, gatekeeper-liability exposure |

---

## Typology-aware scoring

The entity typology does not change *what* you measure — a weighted, multi-domain
composite still applies (see the risk-scoring model in
[`aml-typologies.md`](aml-typologies.md)). It changes *how* you score:

- **Which dimensions dominate.** A miner's risk concentrates in Financial and
  Geographic; a DAO's in Governance; a stablecoin issuer's in Financial
  (reserve quality). Score every dimension, but expect the typology's primary
  dimensions to carry the rating.
- **Which mandatory minimums ("score floors") apply.** Certain confirmed facts
  set a floor under a dimension regardless of the surrounding rubric — an active
  sanctions designation, operating as a VASP without required registration, a
  mixer with no controls, a stablecoin with no reserve attestation. A floor is a
  minimum, never a cap; the highest applicable floor governs; and **VASP-specific
  floors never apply to a non-VASP** (a treasury holder, a miner).
- **How anchors shift.** A private entity's Financial dimension is scored on
  funding quality and runway, not on the absence of public statements. A DAO's
  Governance is scored on whether an accountable legal person exists, not on the
  absence of a conventional board. Absence of evidence is documented as a
  limitation — never scored as a finding.

The discipline this enforces: six months on, a novel entity is assessed the way
the nearest typology was. The framework grows by adding typologies, not by
re-deciding the method case by case.

---

## A note on currency

Crypto regulation moves faster than almost any other domain — new statutes,
agency guidance, designations added and withdrawn, entities relocating between
jurisdictions. The regulatory-lens column above is a starting map. Confirm the
current state of any specific regime against the issuing body before relying on
it.

---

## Related references

- [`aml-typologies.md`](aml-typologies.md) — laundering typologies, the
  regulatory framework, and the weighted risk-scoring model
- [`compliance-documents.md`](compliance-documents.md) — document structures for
  entity risk assessments and risk-assessment workpapers
- [`../prompts/compliance/entity-risk-assessment.md`](../prompts/compliance/entity-risk-assessment.md)
  — the prompt that operationalizes this taxonomy
- [`../prompts/blockchain/`](../prompts/blockchain/) — blockchain-specific
  analytical prompts (DeFi protocol risk, token compliance, fund-flow tracing)
