# Crypto / Blockchain Intelligence — team hub

> This financial-crime team assesses blockchain addresses, fund flows, tokens, and protocols for financial-crime risk, and routes its findings to the analysts and decision-makers who act on them.

## In one minute

This team answers a narrow but high-volume question: given a blockchain address, transaction, token, or protocol, how exposed is it to illicit activity, and what should happen next. The work spans scoring a flagged address for its exposure to tainted funds, tracing where money moved across multiple hops, screening against sanctions and high-risk services like mixers, and judging whether a token or DeFi protocol carries elevated risk. "Good" looks like a consistent, evidence-backed disposition for every item reviewed — the same address scored the same way regardless of who picks it up — with a clear audit trail of why. AI is genuinely useful here: it standardizes scoring logic, drafts the trace narrative, classifies entity types, and cuts the noise so analysts spend time on the items that matter (the runnable scoring framework cuts false positives by roughly 88% while still catching every true positive in its test set). What AI does not do is make the call — it scores and routes, but a human analyst decides disposition, and nothing here blocks an address, freezes funds, or files a report on its own.

> **In plain terms:** the tools help an analyst quickly figure out how dirty a crypto address or token might be and explain why, but a person always makes the final decision.

## What this team owns

- Address KYT risk scoring — measuring an address's exposure to illicit funds
- Fund-flow tracing — following money across multiple hops between addresses
- DeFi protocol and token risk — assessing the safety and compliance posture of protocols and tokens
- On-chain sanctions screening — checking addresses against sanctions lists and high-risk services
- Entity-typology classification — identifying what kind of actor an address represents
- Evidence handling — capturing public block-explorer data so that where each fact came from, and when, survives to the case file

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Score a flagged address by tainted-path exposure | onchain-kyt-address-risk | framework (runnable, recall 1.0, 88% FP-cut) | [../frameworks/onchain-kyt-address-risk/](../frameworks/onchain-kyt-address-risk/) |
| Turn explorer data into a provenance-stamped evidence pack | onchain-osint-evidence | framework (runnable, 100% provenance, exact reconciliation, byte-identical re-runs) | [../frameworks/onchain-osint-evidence/](../frameworks/onchain-osint-evidence/) |
| Trace fund flow across hops | fund-flow-tracing | prompt | [../prompts/blockchain/fund-flow-tracing.md](../prompts/blockchain/fund-flow-tracing.md) |
| Screen an address against sanctions/mixers | onchain-sanctions-monitor | prompt | [../prompts/blockchain/onchain-sanctions-monitor.md](../prompts/blockchain/onchain-sanctions-monitor.md) |
| Build a sourced evidence annex from a block explorer | block-explorer-osint | prompt | [../prompts/blockchain/block-explorer-osint.md](../prompts/blockchain/block-explorer-osint.md) |
| Assess a DeFi protocol | defi-protocol-risk | prompt | [../prompts/blockchain/defi-protocol-risk.md](../prompts/blockchain/defi-protocol-risk.md) |
| Screen a token/project | token-compliance-screen | prompt | [../prompts/blockchain/token-compliance-screen.md](../prompts/blockchain/token-compliance-screen.md) |
| Assess Travel Rule readiness and transfer data completeness | travel-rule-compliance-review | prompt | [../prompts/blockchain/travel-rule-compliance-review.md](../prompts/blockchain/travel-rule-compliance-review.md) |
| Risk-assess a counterparty VASP | vasp-counterparty-assessment | prompt | [../prompts/blockchain/vasp-counterparty-assessment.md](../prompts/blockchain/vasp-counterparty-assessment.md) |
| Review a stablecoin issuer's reserves | stablecoin-reserve-review | prompt | [../prompts/blockchain/stablecoin-reserve-review.md](../prompts/blockchain/stablecoin-reserve-review.md) |
| Disposition mixer/bridge exposure in an alert | bridge-mixer-exposure-playbook | prompt | [../prompts/blockchain/bridge-mixer-exposure-playbook.md](../prompts/blockchain/bridge-mixer-exposure-playbook.md) |
| Classify a blockchain entity type | blockchain-entity-typologies | reference | [../reference/blockchain-entity-typologies.md](../reference/blockchain-entity-typologies.md) |
| See a finished fund-flow trace | fund-flow-tracing-sample | sample | [../samples/compliance/fund-flow-tracing-sample.md](../samples/compliance/fund-flow-tracing-sample.md) |

## How the pieces fit

The prompts handle ad-hoc, one-at-a-time investigations — trace a flow, screen an address for sanctions exposure, assess a single token or protocol — while the runnable frameworks apply consistent treatment at scale. onchain-kyt-address-risk scores many flagged addresses the same way; onchain-osint-evidence solves the other half of the problem, taking the explorer's own responses and stamping every fact with its source link, retrieval time, and a fingerprint of the exact bytes it came from, so the totals in the annex reconcile exactly to the captures and the same captures re-render byte-identically months later. block-explorer-osint is the paste-prompt version of that discipline for a single address. Both draw a hard line between an observation (this address received 4.2 BTC from that address on that date) and an attribution (this address belongs to an exchange) — the engine only ever produces the former. The reference and the sample sit alongside: the entity-typology reference tells you what kind of actor you are looking at, and the sample shows what a completed trace should read like before you write your own. A typical case runs: screen the address -> score its exposure with the framework -> trace the flow across hops -> capture the supporting facts as stamped evidence -> classify the entity type -> hand the dispositioned package to an analyst.

## Capabilities & limitations

**What these tools DO**

- Standardize how an address, token, or protocol is scored and explained, so results are consistent across analysts
- Trace funds across multiple hops and produce a readable narrative of the path
- Screen against sanctions lists and high-risk service categories such as mixers
- Preserve provenance on every captured fact — source URI, retrieval timestamp, content hash — so an evidence annex survives review months later
- Reconcile totals exactly to the source captures, without dropping or double-counting records across paginated pages
- Classify the likely entity type behind an address and reduce false-positive noise for triage

**What they deliberately do NOT do**

- The runnable frameworks are reference implementations for scoring, triage, and evidence capture, not a production control system of record
- They score and route — a human analyst makes the disposition decision
- The evidence engine states observations only; it never says who owns an address or whether anything is wrong — attribution is a human act
- They never auto-block an address, freeze or move funds, or file a regulatory report on their own
- They use generic, illustrative logic; calibration to a specific institution's risk appetite and data is a human step

## Start here

1. Open the [fund-flow-tracing-sample](../samples/compliance/fund-flow-tracing-sample.md) to see what a finished output looks like — it sets the standard before you run anything.
2. Pick up a real flagged address and run it through the [onchain-kyt-address-risk](../frameworks/onchain-kyt-address-risk/) framework to get a consistent exposure score and triage decision.
3. For anything the score surfaces, deepen the case with the matching prompt — [fund-flow-tracing](../prompts/blockchain/fund-flow-tracing.md) for the path, [onchain-sanctions-monitor](../prompts/blockchain/onchain-sanctions-monitor.md) for sanctions exposure — and capture what you relied on with [block-explorer-osint](../prompts/blockchain/block-explorer-osint.md) (or the [onchain-osint-evidence](../frameworks/onchain-osint-evidence/) framework at volume), using [blockchain-entity-typologies](../reference/blockchain-entity-typologies.md) to name the actor before handing it to an analyst.
