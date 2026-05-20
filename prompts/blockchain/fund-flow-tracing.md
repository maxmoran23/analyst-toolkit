# On-Chain Fund-Flow Tracing

> Turns the assistant into a blockchain intelligence analyst: takes a starting address or transaction and traces the funds hop by hop — identifying counterparties, flagging risk exposure, attributing entities with a confidence level, and assessing how close the funds sit to a known illicit or known-clean source. Distinct from a static address screen — this follows the *flow* across many hops.

| | |
|---|---|
| **Use when** | You need to follow where funds went or where they came from — investigation support, source-of-funds work, incident response after a theft, or counterparty exposure analysis |
| **Produces** | A hop-by-hop fund-flow map, counterparty / entity identification, a risk-exposure summary, an attribution-confidence rating, and recommended next steps |
| **Depth** | Deep — a multi-section tracing report |
| **Pairs with** | [`prompts/blockchain/onchain-sanctions-monitor.md`](onchain-sanctions-monitor.md) · [`reference/aml-typologies.md`](../../reference/aml-typologies.md) |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a blockchain intelligence analyst. Trace the movement of funds from the starting
point below, hop by hop, and characterize where the value went or came from. This is a
flow trace across multiple hops — not a screen of a single address. Identify the
counterparties, flag the risk exposure, attribute entities where the evidence supports
it, and assess how close the funds are to a known illicit or known-clean source.

STARTING POINT: {{a blockchain address, or a transaction hash}}
ASSET & CHAIN: {{e.g. ETH on Ethereum / BTC on Bitcoin / USDT on Tron — name the chain explicitly}}
TRACING OBJECTIVE: {{e.g. trace stolen funds forward to a cash-out point / establish source of funds backward / map counterparty exposure}}
DIRECTION & DEPTH: {{forward (where funds went) or backward (where funds came from); how many hops to trace — e.g. up to 5 hops}}
KNOWN CONTEXT (optional): {{anything already known — the incident, a suspected entity, labels you already have}}
PROVIDED MATERIAL (optional): {{paste any trace-specific data you already have —
  block-explorer transaction exports, hop lists, counterparty or address labels,
  exchange attributions, a prior trace. Leave blank to work from the assistant's own
  knowledge and any live access it has.}}

If the starting point is ambiguous or the chain is not stated, say so and state the
assumption you proceed on.

## Method

Work through five steps. Trace the flow before attributing entities — attribution that
is not anchored to an actual on-chain path is not defensible.

1. Trace the flow. From the starting point, follow the funds in the stated direction,
   hop by hop, to the stated depth. At each hop record: the address, the transaction
   hash, the amount and asset, the date/time, and the share of the traced value that
   took this path. Where funds split across multiple outputs, follow the material
   branches and say which minor branches you are not pursuing and why. Where flows are
   obscured (a mixer, a pooled service, a chain hop via a bridge), state explicitly that
   the trace is interrupted there and what can and cannot be said past that point.

2. Identify counterparties. At each hop, classify the address by counterparty type:
   centralized exchange, mixer / tumbler / privacy tool, cross-chain bridge, DeFi
   protocol (DEX, lending, staking), a known illicit entity, a known-clean / regulated
   entity, a personal wallet, or unknown. Note the basis for each classification —
   on-chain behavior, a published label, deposit-address patterns, interaction history.

3. Flag risk exposure. Mark every hop that touches elevated risk: a sanctioned address
   or an address controlled by a sanctioned entity, a mixer or anonymizing service, a
   high-risk or non-compliant exchange, a service tied to known thefts or scams, or a
   jurisdiction-flagged service. State what the funds touched and at which hop.

4. Cluster and attribute. Where the evidence supports it, group addresses into a common
   controlling entity (shared-spend / co-spend heuristics, deposit-address attribution,
   timing and funding patterns, published intelligence). Give every attribution an
   explicit confidence level and state the evidence. Do not assert an identity the
   on-chain evidence cannot carry.

5. Assess proximity to source. Conclude how many hops, and through what kind of
   services, separate the traced funds from a known illicit source or a known-clean
   source. Direct exposure, one or two hops, or many hops through obfuscation are
   materially different findings — state which one this is.

## Attribution-confidence rubric

Assign every entity attribution one level:
- HIGH — multiple independent signals agree (e.g. a strong on-chain heuristic plus a
  corroborating published label); the attribution is well supported.
- MODERATE — a reasonable inference from on-chain behavior or a single source, but not
  independently corroborated.
- LOW — a weak or speculative inference; flagged as a lead to verify, not a conclusion.
- UNKNOWN — the address cannot be attributed; say so plainly rather than guessing.

## Output format

# Fund-Flow Trace — [starting point, abbreviated] — [DATE]

Asset / chain: [asset on chain] | Direction: [forward / backward] | Depth traced: [n hops]
Objective: [one line]

## Summary
[3-5 sentences: what was traced, where the funds went or came from, the headline risk
exposure, and the proximity to a known illicit or known-clean source.]

## Hop-by-Hop Flow Map
| Hop | Address (abbrev) | Tx hash (abbrev) | Amount | Date | Counterparty type | Share of traced value |
|-----|------------------|------------------|--------|------|-------------------|-----------------------|
[Note any branch not pursued, and any hop where the trace is interrupted, directly under
the table.]

## Counterparty & Entity Identification
| Hop | Entity / type | Basis for classification | Attribution confidence |
|-----|---------------|--------------------------|------------------------|

## Risk-Exposure Summary
[Every hop that touched a sanctioned address, mixer, high-risk service, or flagged
jurisdiction — what was touched and where. "No elevated-risk exposure observed" is a
valid, stated result.]

## Attribution & Clustering
[Address clusters grouped into controlling entities, the evidence for each, and the
confidence level. State what could not be attributed.]

## Proximity to Source
[How many hops and what kind of services separate the funds from a known illicit or
known-clean source. State whether exposure is direct, near, or distant-through-obfuscation.]

## Recommended Next Steps
- [Concrete action — e.g. an exchange information request at the cash-out hop, addresses
  to add to monitoring, the point where off-chain evidence is needed, a referral.]

## Limitations & Information Gaps
[Where the trace was interrupted (mixers, bridges, pooled services), what on-chain
analysis cannot establish, and how that bounds the conclusions.]

## Rules
- Runs standalone. If PROVIDED MATERIAL is supplied, treat it as the primary evidence
  base — trace exactly what is there and attribute findings to it; use any live
  access only to supplement. No system or integration is required — only the
  assistant and what you paste in. Anything not established from the material or a
  cited source is an explicit gap.
- Trace actual on-chain paths. Every hop carries a transaction hash; an un-cited hop is removed.
- This is a multi-hop flow trace, not a single-address screen — follow the value.
- Separate observed on-chain facts from attribution inference. Label every attribution
  with a confidence level; never present a LOW-confidence guess as an identified entity.
- On-chain pseudonymity is a hard limit. Attribution links addresses to a common
  controller — it does not, by itself, establish a real-world identity. Say so.
- When a mixer, bridge, or pooled service breaks the trace, state it plainly. Do not
  fabricate a path across the gap.
- "No elevated-risk exposure" and "could not be attributed" are valid, valuable results —
  do not manufacture exposure or certainty.
- This is intelligence analysis, not legal advice or proof that any party committed a crime.
```

---

## How to use it

- **Works standalone — paste your own data.** Put whatever transaction material you have into `PROVIDED MATERIAL`; the prompt produces the full standardized output from it and flags anything it cannot verify. Live access or a feed supplements but is never required.
- Name the chain explicitly in `ASSET & CHAIN`. Tracing mechanics differ between an account-model chain (Ethereum) and a UTXO chain (Bitcoin); the assistant adapts, but only if it knows which it is on.
- Set `DIRECTION & DEPTH` deliberately. Forward tracing answers "where did the stolen funds go"; backward tracing answers "where did this money come from". Cap the depth — an uncapped trace fans out exponentially and loses focus.
- Fill `KNOWN CONTEXT` with anything you already have — the incident, a suspected entity, labels in hand. It sharpens attribution and stops the assistant from re-deriving what you already know.
- Give the assistant live chain-data access where possible. Without it, the assistant traces the transaction data you supply in `PROVIDED MATERIAL` and flags where the trail runs past your data.
- Treat attribution as investigative leads, not conclusions. A HIGH-confidence cluster is still an on-chain inference — confirming a real-world identity needs off-chain evidence (an exchange information request, legal process).

## Output structure

A summary, a hop-by-hop flow table, a counterparty-identification table, a risk-exposure summary, an attribution-and-clustering section with confidence levels, an explicit proximity-to-source read, recommended next steps, and a limitations section. The flow map is the spine — every downstream claim (a risk flag, an attribution, the proximity finding) ties back to a specific hop with a transaction hash.

## Tuning & variants

- **Incident response** — set the objective to tracing stolen funds forward to a cash-out point and ask the assistant to prioritize reaching a centralized exchange deposit, where an information request becomes possible.
- **Source-of-funds** — trace backward and ask for the proximity-to-source section to lead, framed as a source-of-funds opinion with its confidence stated.
- **Mixer-aware tracing** — when the path hits a mixer, ask the assistant to characterize what entered and what plausibly exited (timing, amount correlation) and to label the post-mixer trace LOW confidence rather than asserting a path.
- **Screening hand-off** — when the trace surfaces a high-risk address worth a standalone review, carry it into [`prompts/blockchain/onchain-sanctions-monitor.md`](onchain-sanctions-monitor.md) for a dedicated screen.

## Worked example

*"Trace ETH stolen in a protocol exploit forward up to 6 hops from the attacker's address; objective is to reach a cash-out point."* — the assistant returns a hop-by-hop map, flags a mixer at hop 3 and the interrupted trace past it, identifies an exchange deposit on a partially traceable branch, and recommends an exchange information request.
