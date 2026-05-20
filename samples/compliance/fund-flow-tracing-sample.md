> ILLUSTRATIVE SAMPLE — synthetic/illustrative content produced for format demonstration. Not a real assessment.

# Fund-Flow Trace — 0x7A3f…E219 — 2026-05-20

Asset / chain: ETH on Ethereum | Direction: forward | Depth traced: 6 hops
Objective: Trace funds forward from a flagged origin address to a cash-out point and characterize risk exposure along the path

> **Fictional scenario notice.** Every address, transaction hash, amount, label, and counterparty in this trace is synthetic and invented solely to demonstrate the output format of the On-Chain Fund-Flow Tracing prompt. The addresses and hashes below are illustrative strings, not real on-chain objects. The "Helix Protocol exploit" is a fictional incident. Nothing here is a statement about any real address, transaction, exchange, or party.

## Summary

This trace follows ETH forward from address `0x7A3f…E219`, the fictional origin address designated in this sample as the recipient of funds drained in the (fictional) "Helix Protocol" exploit, across six hops. From a starting balance of **2,400.0 ETH**, the funds were consolidated, split across a fan-out of intermediary wallets, and a material branch — **920.0 ETH** — was sent into a coin-mixing service at hop 3. The trace is **interrupted at the mixer**: what entered is observed, but the specific outputs cannot be attributed on-chain. A separate, **non-mixed branch of 760.0 ETH** was traced cleanly through two intermediary wallets to a deposit address at a centralized exchange ("Northwind Exchange," fictional) at hop 6. The headline risk exposure is direct interaction with a mixer (hop 3) and, on the traceable branch, the funds reaching a regulated-exchange deposit one information request away from a real-world identity. Proximity to the illicit source is **direct** on the traceable branch — six hops, no obfuscation between the origin and the exchange deposit — and **broken** on the mixed branch.

## Hop-by-Hop Flow Map

| Hop | Address (abbrev) | Tx hash (abbrev) | Amount | Date | Counterparty type | Share of traced value |
|-----|------------------|------------------|--------|------|-------------------|-----------------------|
| 0 | 0x7A3f…E219 | — (origin) | 2,400.0 ETH | 2026-05-11 | Origin — flagged (exploit recipient) | 100% |
| 1 | 0x7A3f…E219 → 0xC1d4…9b07 | 0x4f8a…d213 | 2,400.0 ETH | 2026-05-11 | Personal wallet (consolidation) | 100% |
| 2 | 0xC1d4…9b07 → 0x2Ee9…7a55 | 0x9c02…1f7e | 920.0 ETH | 2026-05-12 | Personal wallet (split — branch A) | 38.3% |
| 2 | 0xC1d4…9b07 → 0x88Ba…0c31 | 0x1d77…ab90 | 760.0 ETH | 2026-05-12 | Personal wallet (split — branch B) | 31.7% |
| 2 | 0xC1d4…9b07 → (5 further outputs) | (5 hashes) | 720.0 ETH | 2026-05-12 | Personal wallets (minor branches) | 30.0% |
| 3 | 0x2Ee9…7a55 → 0xMixerEntry…F4 | 0x6b3c…44de | 920.0 ETH | 2026-05-13 | Mixer / coin-anonymizing service | 38.3% |
| 4 | 0x88Ba…0c31 → 0x5Fd0…e6a2 | 0xa210…8c61 | 760.0 ETH | 2026-05-14 | Personal wallet (pass-through) | 31.7% |
| 5 | 0x5Fd0…e6a2 → 0x9Ab7…3d18 | 0x7e44…02bf | 755.0 ETH | 2026-05-15 | Personal wallet (pass-through) | 31.5% |
| 6 | 0x9Ab7…3d18 → 0xDEP-Northwind…7C | 0xc803…91aa | 750.0 ETH | 2026-05-16 | Centralized exchange — deposit address | 31.3% |

**Branches not pursued.** At hop 2 the consolidation wallet `0xC1d4…9b07` produced seven outputs; this trace pursues the two material branches (branch A, 920.0 ETH to a mixer; branch B, 760.0 ETH toward an exchange) and does not pursue the five minor outputs totaling 720.0 ETH (30.0% of value, none individually exceeding ~180 ETH). Those five are listed for completeness and flagged below as residual untraced value.

**Trace interruption.** The trace is **interrupted at hop 3**. The 920.0 ETH sent to `0xMixerEntry…F4` enters a coin-mixing service; the deposit is observed on-chain, but the service pools and re-mixes deposits, so the specific outputs cannot be linked to this deposit by on-chain analysis. The mixed branch is not traced past hop 3. The small differences between hop amounts on branch B (760.0 → 755.0 → 750.0 ETH) reflect gas paid and small residual balances left at each pass-through wallet, not additional outbound branches.

## Counterparty & Entity Identification

| Hop | Entity / type | Basis for classification | Attribution confidence |
|-----|---------------|--------------------------|------------------------|
| 0 | Flagged origin — exploit recipient | Designated as the origin for this trace; the address received the funds in scope | HIGH (as a designation; the "exploit" is fictional) |
| 1 | Consolidation wallet (`0xC1d4…9b07`) | Receives the full origin balance and immediately re-distributes; classic consolidation behavior | MODERATE — consistent with single-controller use, no independent corroboration |
| 2 | Splitter / fan-out wallet | Same address as hop 1; produces 7 near-simultaneous outputs — fan-out / layering pattern | MODERATE |
| 3 | Coin-mixing service (`0xMixerEntry…F4`) | Deposit address pattern and pooling behavior consistent with a mixing service; treated as a service contract, not a personal wallet | MODERATE — behavioral; no corroborating published label cited in this sample |
| 4–5 | Pass-through wallets (`0x5Fd0…e6a2`, `0x9Ab7…3d18`) | Receive and forward the full balance within ~24h, hold no residual, no other activity — pass-through pattern | MODERATE |
| 6 | Centralized-exchange deposit address (`0xDEP-Northwind…7C`) | Deposit-address pattern: receives from external wallets and forwards inward to an exchange hot-wallet cluster; attributed to a centralized exchange ("Northwind Exchange") | MODERATE — deposit-address heuristic; would be HIGH if corroborated by a published exchange-address label |

No address in this trace is attributed to a **named real-world individual**. Every attribution above links addresses to a *type* of counterparty or to a *common-control inference* — none establishes a person's identity. See Proximity to Source and Limitations.

## Risk-Exposure Summary

The trace touched elevated risk at the following points:

- **Hop 3 — direct mixer exposure.** 920.0 ETH (38.3% of the traced value) was sent directly into a coin-mixing / anonymizing service via tx `0x6b3c…44de` on 2026-05-13. Direct interaction with a mixer is the most significant risk exposure in this trace: it is both an elevated-risk counterparty in its own right and the point at which 38.3% of the value becomes untraceable.
- **Hop 6 — regulated-exchange deposit.** 750.0 ETH (31.3%) reached a centralized-exchange deposit address. This is not an *illicit* exposure — a regulated exchange is a known/regulated counterparty type — but it is the operationally significant hop: it is where the funds enter a custodial service that can identify the depositor and where an information request becomes possible.

No interaction with a **sanctioned address** (OFAC SDN-listed or otherwise consolidated-list-flagged) was identified on any traced hop in this sample. No interaction with a cross-chain bridge was observed; the trace remained on Ethereum throughout. The five minor branches at hop 2 (720.0 ETH) were not traced and so carry **unassessed** risk exposure — not "no exposure."

## Attribution & Clustering

- **Cluster 1 — origin and consolidation (`0x7A3f…E219`, `0xC1d4…9b07`).** The origin sent its entire balance to the consolidation wallet in a single transaction, and the consolidation wallet immediately fanned the funds out. The funding relationship and the immediate full-balance forwarding support a **MODERATE-confidence** inference that these two addresses are under common control. This is an on-chain behavioral inference, not a confirmed identity.
- **Cluster 2 — branch B pass-through chain (`0x88Ba…0c31`, `0x5Fd0…e6a2`, `0x9Ab7…3d18`).** Each address received the branch-B balance and forwarded substantially all of it within ~24 hours, held no residual, and showed no other activity. This sequential single-purpose pass-through pattern supports a **MODERATE-confidence** inference of common control across the branch-B chain.
- **Exchange deposit address (`0xDEP-Northwind…7C`).** Attributed to a centralized exchange by the deposit-address heuristic (receives externally, forwards inward to an exchange-controlled cluster) at **MODERATE** confidence. The deposit address belongs to the exchange; the *depositor's identity* is held off-chain by the exchange and cannot be determined from the chain.
- **Could not be attributed.** The mixer outputs (everything past hop 3 on branch A) cannot be attributed — by design of the service. The five minor hop-2 branches (720.0 ETH) were not traced and are unattributed. No address in this trace is clustered to a named person or real-world entity.

## Proximity to Source

On the **traceable branch (branch B)**, the funds sit **direct / near** to the flagged origin: 750.0 ETH reached a centralized-exchange deposit address in **six hops with no mixer, no bridge, and no other obfuscation** between the origin and the exchange. Every hop on this branch carries a transaction hash and an amount that reconciles to the next. This is the strongest possible posture for an investigation — the funds are one exchange information request away from a potential real-world identity.

On the **mixed branch (branch A)**, proximity is **broken**. 920.0 ETH entered a mixer at hop 3; on-chain analysis cannot place those funds any closer to a destination than "deposited into a mixing service." Anything asserted about where that 920.0 ETH went would be speculation.

The five minor hop-2 branches (720.0 ETH) are **untraced** — their proximity to any destination is simply not established in this sample.

## Recommended Next Steps

- **Issue an exchange information request for the hop-6 deposit.** The deposit address `0xDEP-Northwind…7C` at "Northwind Exchange" is the actionable cash-out point. A request to the exchange for the account holder, KYC records, and subsequent activity tied to the 750.0 ETH deposit (tx `0xc803…91aa`, 2026-05-16) is the single highest-value next step — this is where on-chain leads can become an identity.
- **Add the traced branch-B addresses to monitoring.** Place `0x88Ba…0c31`, `0x5Fd0…e6a2`, and `0x9Ab7…3d18` under ongoing monitoring for any further activity.
- **Trace the five minor hop-2 branches.** The 720.0 ETH in unpursued branches (30.0% of value) should be traced in a follow-up pass; one or more may also reach an exchange.
- **Characterize, do not assert, the mixer branch.** For the 920.0 ETH at hop 3, a timing-and-amount correlation analysis of mixer outflows may yield *leads*, but any post-mixer address must be treated as LOW confidence — see Limitations.
- **Off-chain evidence is required to close.** Confirming who controls any clustered address needs off-chain evidence (the exchange response, legal process). On-chain attribution here is investigative lead material, not proof of identity.

## Limitations & Information Gaps

- **The mixer breaks the trace at hop 3.** 920.0 ETH (38.3% of traced value) entered a coin-mixing service. On-chain analysis can confirm what was deposited but cannot attribute the specific outputs. No path is asserted past the mixer; doing so would be fabrication.
- **Attribution is pseudonymous.** Every entity attribution in this trace links addresses to a counterparty *type* or to a common-control *inference*. None establishes a real-world identity. On-chain pseudonymity is a hard limit — a depositor's identity at hop 6 is held by the exchange, off-chain.
- **Minor branches untraced.** The five hop-2 outputs totaling 720.0 ETH (30.0%) were not pursued in this sample; their risk exposure and destination are unassessed, not cleared.
- **Confidence levels are behavioral.** The MODERATE attributions rest on on-chain heuristics (consolidation, pass-through, deposit-address patterns) without independent corroboration; a published address label or exchange confirmation would raise specific attributions to HIGH.
- **This is intelligence analysis.** This trace is investigative analysis of on-chain data — it is not legal advice and not proof that any party committed an offense. The "Helix Protocol exploit" framing is a fictional designation for this sample; no real incident is referenced.
