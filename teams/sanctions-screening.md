# Sanctions & Screening — team hub

> This financial-crime team is accountable for screening customers and payments against sanctions and watchlists, and for dispositioning every alert that screening produces.

## In one minute

This team is the institution's checkpoint against doing business with sanctioned parties: it screens customer names, counterparties, and payment instructions against OFAC, UN, EU, and internal watchlists, then works through the alerts that fire. Most alerts are false positives — a common name that merely resembles a listed party — so the daily reality is high-volume triage to separate genuine matches from noise, fast and without missing a true hit. "Good" looks like zero missed true matches (full recall), a steadily cleared backlog, and every disposition documented well enough to defend to an examiner. AI can do the heavy lifting on the repetitive parts: pre-scoring alerts by likelihood, drafting the rationale for each disposition, and flagging the handful that need a closer human look — which is where the toolkit's largest payoff sits. What AI cannot do is make the call: it never auto-clears, auto-blocks, or files anything, and the listed-party data it screens against is only as current as the watchlist it is given.

> **In plain terms:** the team checks every name and payment against the sanctions lists, and the tools sort the mountain of "probably-not-a-match" alerts so a human can focus on the few that actually matter.

## What this team owns

- Name and entity screening, and the disposition of each hit that screening generates
- False-positive triage of the sanctions-alert backlog at scale (illustratively ~50k alerts a month)
- On-chain and wallet sanctions screening for digital-asset activity
- Maintaining awareness of sanctions-evasion typologies so screening logic stays current

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Triage the ~50k/month false-positive alert backlog | sanctions-name-screening | framework (runnable, recall 1.0, 92% FP-cut) | [../frameworks/sanctions-name-screening/](../frameworks/sanctions-name-screening/) |
| Screen and disposition a single name/entity/vessel ad hoc | sanctions-watchlist-screen | prompt | [../prompts/compliance/sanctions-watchlist-screen.md](../prompts/compliance/sanctions-watchlist-screen.md) |
| Screen a blockchain address against sanctions | onchain-sanctions-monitor | prompt | [../prompts/blockchain/onchain-sanctions-monitor.md](../prompts/blockchain/onchain-sanctions-monitor.md) |
| Look up evasion typologies and the regulatory map | aml-typologies | reference | [../reference/aml-typologies.md](../reference/aml-typologies.md) |
| Render any output as Word/Excel/PDF/HTML | BASE.md | companion | [../BASE.md](../BASE.md) |

## How the pieces fit

The two prompts handle one item at a time: use sanctions-watchlist-screen for a single name, entity, or vessel, and onchain-sanctions-monitor for a single blockchain address. The framework is the volume engine — it scores and routes a whole backlog of alerts at once, cutting the false positives a human has to read while keeping full recall on true hits. The reference keeps everyone's judgment current on how evasion actually happens, and BASE.md turns any of these outputs into a finished Word, Excel, PDF, or HTML deliverable. A typical chain: single-case screen (prompt) or backlog scoring (framework) -> triage and route -> human disposition -> render the record with BASE.md.

## Capabilities & limitations

**What these tools DO**

- Pre-score and rank alerts by match likelihood, then route the noise away from the genuine candidates
- Draft a defensible, documented rationale for each disposition a human reviewer can confirm
- Screen names, entities, vessels, and blockchain addresses against sanctions and watchlist data
- Keep evasion-typology and regulatory context one click away so screening logic stays informed
- Produce the final deliverable in the format an examiner or stakeholder expects

**What these tools deliberately do NOT do**

- The frameworks are reference implementations for triage and routing — not production screening controls
- They score and route, but a human makes every clear, escalate, or block decision
- They never auto-clear, auto-block a payment, freeze an account, or file a report
- They are only as accurate as the watchlist data supplied — a stale list yields stale results
- They do not replace the institution's system of record or its second-line review

## Start here

1. Open the framework at [../frameworks/sanctions-name-screening/](../frameworks/sanctions-name-screening/) and read its README to see how backlog triage scores and routes alerts while preserving full recall.
2. Run one real case end to end with [../prompts/compliance/sanctions-watchlist-screen.md](../prompts/compliance/sanctions-watchlist-screen.md) (or [../prompts/blockchain/onchain-sanctions-monitor.md](../prompts/blockchain/onchain-sanctions-monitor.md) for a wallet) to feel how a single disposition is drafted.
3. Render that result into a shareable record with [../BASE.md](../BASE.md), and keep [../reference/aml-typologies.md](../reference/aml-typologies.md) open as the standing reference for evasion patterns and the regulatory map.
