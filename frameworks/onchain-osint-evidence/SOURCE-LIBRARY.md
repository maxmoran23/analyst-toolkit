# On-Chain OSINT Source Library & Capture Methodology

The source layer under the [evidence engine](README.md): where public block-explorer data
comes from, how far to trust each kind of it, and how to capture it so a provenance-stamped
annex survives review. The engine enforces this discipline in code; this document is the
human-facing whitelist and method. Cross-workflow master:
[`../../reference/osint-source-library.md`](../../reference/osint-source-library.md).

> Public sources only. Commercial attribution tools (Chainalysis, TRM, Elliptic) sit on top of
> this free baseline; the capture and provenance discipline below is identical whichever you use.

---

## The governing distinction: facts vs. labels

A block explorer gives you two very different things, and they sit at different tiers:

- **On-chain facts** — transactions, amounts, timestamps, token transfers, contract code. These
  are **Tier 1**: verifiable against the ledger itself.
- **Labels / name-tags** — "Exchange: Hot Wallet", "Tornado-adjacent", a scam report. These are
  **Tier 3**: single-source leads about the *service* operating an address, never proof that a
  natural person owns or transacted through it.

The whole method exists to keep those two from bleeding into each other.

---

## Tiered source whitelist

### Tier 1 — the ledger and official issuers (facts; and the sanctions/issuer tracks)

| Source | URL | Chain(s) | Establishes |
|--------|-----|----------|-------------|
| Etherscan & family | `etherscan.io`, `bscscan.com`, `arbiscan.io`, `polygonscan.com` | EVM chains | Transactions, token transfers, contracts, balances |
| Tronscan | `tronscan.org` | Tron | TRX/TRC-20 activity (a major USDT rail) |
| Solscan | `solscan.io` | Solana | SOL/SPL activity |
| mempool.space / Blockstream.info | `mempool.space` | Bitcoin | UTXO-level transaction detail |
| OFAC SDN crypto addresses | `ofac.treasury.gov` (in the SDN list) | multi | The authoritative on-chain sanctions screen |
| Stablecoin issuer freeze lists | Tether / Circle on-chain blocklists | ETH/Tron/etc. | Confirmed issuer-level address freezes |

### Tier 2 — reputable multi-chain aggregators

| Source | URL | Best for |
|--------|-----|----------|
| Blockchair | `blockchair.com` | Cross-chain search and explorer in one place |
| OpenSanctions | `opensanctions.org` | Tying an address/entity to list or PEP data |

### Tier 3 — labels, tags, and community reports (leads only)

Explorer public name-tags, `chainabuse.com` scam reports, forum/social attributions. Use to
generate hypotheses; never to conclude identity. Record the label *and its source*, and rate it
on the corroboration ladder (CORROBORATED / SINGLE-SOURCE / BEHAVIORAL-ONLY).

---

## Capture method (per subject address)

1. **Capture, don't summarize.** For every page you pull, record: explorer name, full URL,
   retrieval date/time, what it covers (address summary / tx list page N of M / token transfers /
   internal txns), and whether coverage is complete. Assign it a capture ID (C1, C2, …).
2. **Pull every page you can.** Partial coverage produces partial conclusions — get all pages of
   the transaction and token-transfer lists where practical; where you cannot, say so, and the
   annex tags the affected totals PARTIAL rather than overstating them.
3. **Keep assets separate.** Never mix native-asset movements with token transfers or sum across
   assets. Gas is context, not flow.
4. **Reconcile.** Compute totals from the extracted facts and tie them to the explorer's own
   summary figures; a discrepancy is a finding, not something to smooth over.
5. **Firewall observations from attributions.** Flows, timing, and counterparties are facts about
   addresses. Any claim that an address *is* a named service/person is an attribution — it stays
   in a separate register behind the corroboration ladder.
6. **Exclude noise.** Dust and unsolicited-token drops are not conduct; exclude them from flow
   conclusions and state that you did.

---

## Action-item scoping — what each finding triggers

| Finding | Action |
|---------|--------|
| **Direct flow with an OFAC-designated address (T1)** | Treat as a sanctions matter on its own strict-liability track; escalate immediately; a human decides any freeze/report. |
| **Strong structural pattern** (rapid pass-through, fan-in/out, peel chain) at material value | Hand the material counterparties to a multi-hop trace — [`../../prompts/blockchain/fund-flow-tracing.md`](../../prompts/blockchain/fund-flow-tracing.md). |
| **SINGLE-SOURCE high-risk label** on a material counterparty | Seek an independent corroborating source before any reliance; until then it is a lead, reported as "labeled by [source]". |
| **Counterparty attributed to a service** (exchange, mixer) | Route to the dedicated screen — [`../onchain-kyt-address-risk/`](../onchain-kyt-address-risk/) / [`../../prompts/blockchain/onchain-sanctions-monitor.md`](../../prompts/blockchain/onchain-sanctions-monitor.md). |
| **Partial coverage** materially bounds the picture | Capture the remaining pages before drawing conclusions; keep affected totals tagged PARTIAL. |
| **Nothing notable** | A valid, valuable result — record it; do not manufacture observations to justify the exercise. |

Every number and observation in the resulting annex cites back to a capture `[C#]` with URL and
retrieval date. Nothing here attributes identity, blocks, or reports on its own — it structures
evidence for a qualified human to act on.
