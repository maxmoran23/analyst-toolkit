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

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Score a flagged address by tainted-path exposure | onchain-kyt-address-risk | framework (runnable, recall 1.0, 88% FP-cut) | [../frameworks/onchain-kyt-address-risk/](../frameworks/onchain-kyt-address-risk/) |
| Trace fund flow across hops | fund-flow-tracing | prompt | [../prompts/blockchain/fund-flow-tracing.md](../prompts/blockchain/fund-flow-tracing.md) |
| Screen an address against sanctions/mixers | onchain-sanctions-monitor | prompt | [../prompts/blockchain/onchain-sanctions-monitor.md](../prompts/blockchain/onchain-sanctions-monitor.md) |
| Assess a DeFi protocol | defi-protocol-risk | prompt | [../prompts/blockchain/defi-protocol-risk.md](../prompts/blockchain/defi-protocol-risk.md) |
| Screen a token/project | token-compliance-screen | prompt | [../prompts/blockchain/token-compliance-screen.md](../prompts/blockchain/token-compliance-screen.md) |
| Classify a blockchain entity type | blockchain-entity-typologies | reference | [../reference/blockchain-entity-typologies.md](../reference/blockchain-entity-typologies.md) |
| See a finished fund-flow trace | fund-flow-tracing-sample | sample | [../samples/compliance/fund-flow-tracing-sample.md](../samples/compliance/fund-flow-tracing-sample.md) |

## How the pieces fit

The prompts handle ad-hoc, one-at-a-time investigations — trace a flow, screen an address for sanctions exposure, assess a single token or protocol — while the runnable framework applies consistent scoring at scale across many flagged addresses. The reference and the sample sit alongside both: the entity-typology reference tells you what kind of actor you are looking at, and the sample shows what a completed trace should read like before you write your own. A typical case runs: screen the address -> score its exposure with the framework -> trace the flow across hops -> classify the entity type -> hand the dispositioned package to an analyst.

## Capabilities & limitations

**What these tools DO**

- Standardize how an address, token, or protocol is scored and explained, so results are consistent across analysts
- Trace funds across multiple hops and produce a readable narrative of the path
- Screen against sanctions lists and high-risk service categories such as mixers
- Classify the likely entity type behind an address and reduce false-positive noise for triage

**What they deliberately do NOT do**

- The runnable framework is a reference implementation for scoring and triage, not a production control system of record
- They score and route — a human analyst makes the disposition decision
- They never auto-block an address, freeze or move funds, or file a regulatory report on their own
- They use generic, illustrative logic; calibration to a specific institution's risk appetite and data is a human step

## Start here

1. Open the [fund-flow-tracing-sample](../samples/compliance/fund-flow-tracing-sample.md) to see what a finished output looks like — it sets the standard before you run anything.
2. Pick up a real flagged address and run it through the [onchain-kyt-address-risk](../frameworks/onchain-kyt-address-risk/) framework to get a consistent exposure score and triage decision.
3. For anything the score surfaces, deepen the case with the matching prompt — [fund-flow-tracing](../prompts/blockchain/fund-flow-tracing.md) for the path, [onchain-sanctions-monitor](../prompts/blockchain/onchain-sanctions-monitor.md) for sanctions exposure — and use [blockchain-entity-typologies](../reference/blockchain-entity-typologies.md) to name the actor before handing it to an analyst.
