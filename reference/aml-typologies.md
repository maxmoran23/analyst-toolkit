# Crypto AML Typologies & Regulatory Reference

A working reference for digital-asset anti-money-laundering (AML) and
counter-terrorist-financing (CFT) work — the regulatory frameworks, the core
laundering typologies with detection logic, a risk-scoring model, and key risk
indicators. Use it when producing entity risk assessments, control
matrices, regulatory analyses, typology mappings, or risk assessments.

All citations point to public bodies and public documents. This is general
domain reference, not legal advice.

---

## US regulatory framework

| Authority | Scope | Key documents |
|-----------|-------|---------------|
| **FinCEN** | Bank Secrecy Act administration, money-services-business (MSB) regulation, SAR / CTR rules | 31 CFR Parts 1010 / 1022; FIN-2013-G001 (virtual currency MSB guidance); FIN-2019-A003 (illicit activity involving convertible virtual currencies); the Travel Rule |
| **OFAC** | Sanctions enforcement, the SDN list, prohibitions on designated entities | OFAC SDN list; cyber-related sanctions guidance; the Tornado Cash designation (Aug 2022) and its withdrawal (Mar 2025) |
| **SEC** | Securities laws as applied to digital assets | The Howey and Reves tests; custody-accounting guidance |
| **CFTC** | Commodities oversight, derivatives | Bitcoin and Ether treated as commodities; derivatives and market-manipulation enforcement |
| **DOJ** | Criminal enforcement | Dedicated cryptocurrency enforcement program |
| **IRS** | Tax reporting | Notice 2014-21; broker-reporting rules (Form 1099-DA) |
| **OCC** | National-bank crypto activities | Interpretive letters on custody and payment activities |
| **State regulators** | State-level licensing | Money-transmitter licensing; the New York BitLicense regime (23 NYCRR Part 200) |

## International framework

| Authority | Key documents |
|-----------|---------------|
| **FATF** | Recommendation 15 (virtual asset service providers); the Travel Rule (Recommendation 16); the 2021 updated VASP guidance; periodic targeted updates on implementation |
| **EU** | The Markets in Crypto-Assets Regulation (MiCA); the Transfer of Funds Regulation (TFR) |
| **UK** | FCA crypto-asset registration; the developing stablecoin regulatory framework |
| **Basel Committee** | Prudential treatment of bank cryptoasset exposures |
| **IOSCO** | Policy recommendations for crypto and digital-asset markets |

A reference like this dates quickly — legislation moves, agencies issue new
guidance, designations are added and withdrawn. Treat the framework tables as a
starting map and confirm the current state of any specific rule against the
issuing body before relying on it.

---

## Core crypto AML typologies

The fifteen laundering patterns most relevant to digital-asset compliance. Each
entry pairs the typology with the on-chain or behavioral signature that detection
logic should target.

| # | Typology | Description | Detection signal |
|---|----------|-------------|------------------|
| 1 | **Mixer / tumbler usage** | Funds routed through a mixing service to break the on-chain trail | Direct deposits to or withdrawals from known mixer addresses; taint propagation from post-mix funds |
| 2 | **Privacy-coin conversion** | Conversion of transparent-ledger assets into privacy coins to sever traceability | Cross-asset swaps into privacy coins; swap-DEX patterns at the conversion point |
| 3 | **Cross-chain bridge layering** | Bridges used to chain-hop and obfuscate origin | Rapid multi-chain hopping; routing through low-liquidity bridges |
| 4 | **Peel chains** | A large sum peeled into many small outputs across many addresses | Tree-pattern outflow analysis; a long sequence of small, declining transfers |
| 5 | **Layering via DEXs** | Many wallet hops and swaps through decentralized exchanges to obscure flow | Round-trip swap detection; repetitive wallet-hop sequences |
| 6 | **Stablecoin laundering** | Stablecoins moved cross-chain to exploit fee and oversight asymmetries | High-velocity stablecoin flows; routing through low-fee or low-oversight chains |
| 7 | **NFT wash trading** | Collusive buy/sell between related parties to create fake provenance or value | Same-counterparty buy/sell pairs; repeated round-trip sales of the same asset |
| 8 | **NFT-based value transfer** | Deliberately overpriced NFT purchases used to move value | Outlier-priced sales to previously unconnected wallets |
| 9 | **DeFi protocol exploitation** | Flash loans or governance attacks used for theft, then laundering of proceeds | A flash-loan or exploit transaction immediately followed by a laundering pattern |
| 10 | **Ransomware proceeds** | Extortion payments collected and laundered on-chain | Matches against public ransomware address indicators |
| 11 | **Darknet marketplace flows** | Deposits to and withdrawals from illicit marketplaces | Address matches against known darknet-marketplace clusters |
| 12 | **Investment / romance scams ("pig butchering")** | Long-con fraud; victim deposits aggregated and exfiltrated | Low-velocity inbound deposits followed by a sudden large transfer to an exchange |
| 13 | **Sanctions evasion** | State-linked or sanctioned actors moving value to evade restrictions | Matches against the OFAC SDN list and law-enforcement advisories on threat-actor addresses |
| 14 | **Terrorism financing** | Small-value aggregation toward addresses linked to designated organizations | Matches against Treasury designations and FATF advisories |
| 15 | **Tax evasion** | Concealment of large gains; use of non-compliant venues to avoid reporting | Large unreported flows to non-licensed or offshore exchanges |

For each typology, detection in production means translating the signal column
into concrete transaction-monitoring rules — thresholds, time windows, entity
types, and exclusions — and mapping each rule back to the typology it covers.

---

## Risk-scoring model (8 dimensions)

A weighted, multi-dimension model for scoring an entity or counterparty. The
composite runs 0-100; the dimension weights are a financial-crime-leaning
default — tune them to the risk appetite of the assessment and state any change.

| Dimension | Weight | Typical sources |
|-----------|--------|-----------------|
| 1. Regulatory enforcement | 15% | OFAC, securities-regulator filings, FinCEN, state regulators, foreign equivalents |
| 2. Litigation exposure | 12% | Court dockets, class actions |
| 3. Sanctions / PEP screening | 15% | OFAC SDN, UN / EU consolidated lists, politically-exposed-person screening |
| 4. Adverse media | 10% | News (recent coverage weighted most heavily), reputational signals |
| 5. Financials / solvency | 12% | Financial filings, attestations, audits, leverage ratios |
| 6. Ownership / structure | 10% | Beneficial ownership, incorporation jurisdiction, holding-company structure |
| 7. Governance | 8% | Board independence, internal controls, governance reputation |
| 8. Geographic / sector risk | 18% | FATF grey/black lists, sanctions exposure, inherent sector risk |

**Override rule.** A confirmed disqualifying fact forces the top of the scale
regardless of the weighted composite — for example, an active OFAC designation, a
criminal indictment for fraud or money laundering, or a multi-billion-dollar
adverse judgment. State the override explicitly when it applies.

---

## Key risk indicators (KRIs)

Indicative thresholds for a compliance-program dashboard. Calibrate them to the
institution's size, risk profile, and regulatory expectations — the values below
are illustrative starting points, not universal standards.

| KRI | Indicative threshold | Source |
|-----|---------------------|--------|
| Sanctions-screening true-positive rate | > 0.5% | Screening logs |
| SAR filing latency | > 30 days from detection | Filing records |
| Alert clearance within SLA | < 60% | Transaction-monitoring system |
| High-risk customer review refresh on schedule | < 85% | KYC system |
| Beneficial-ownership coverage | < 95% of legal entities | KYC system |
| Sanctions-list refresh latency | > 24 hours from publication | List-pull logs |
| Independent-testing exception rate | > 10% of controls | Testing workpapers |
| Training completion by deadline | < 95% | Learning-management system |

---

## Voice for compliance writing

Compliance findings follow the toolkit's general writing standard, with a few
domain-specific habits:

- **Tag every finding with a severity tier** (see
  [`../methodology/analytical-patterns.md`](../methodology/analytical-patterns.md)).
- **Cite the rule before the violation.** State the standard — the statute, the
  regulation, the guidance — before stating the breach. The reader needs the
  benchmark.
- **Distinguish allegations from findings.** An active proceeding is not a
  settled fact. Write pending matters as pending and allegations as allegations.
- **Quantify exposure** wherever possible — volume, count, period.
- **Recommend remediation** with a timeline and an owner.

For the full writing standard, see
[`../methodology/audit-defensible-writing.md`](../methodology/audit-defensible-writing.md).

## Citation formats for compliance work

| Source type | Format |
|-------------|--------|
| Statute | `31 U.S.C. § 5318(g)` |
| Regulation | `31 CFR § 1010.314` |
| FinCEN guidance | `FIN-2019-A003 ([date])` |
| OFAC action | `OFAC Recent Actions, [date]` |
| Court decision | `[Party] v. [Party], No. [docket] ([court] [year])` |
| Enforcement order | `In the Matter of [Entity], [agency] No. [number]` |
| News | `[Publication], [date], "Headline"` |
| Financial filing | `[Entity] Form 10-Q, [period], p.X` |
| Attestation | `[Entity] [report name] ([auditor]), p.X` |

---

## Related references

- [`compliance-documents.md`](compliance-documents.md) — document structures for
  entity risk assessments, control matrices, SAR narratives, policies
- [`regulatory-intelligence.md`](regulatory-intelligence.md) — tracking and
  analyzing regulatory developments
- [`audit-documentation.md`](audit-documentation.md) — control testing,
  workpapers, deficiency classification
