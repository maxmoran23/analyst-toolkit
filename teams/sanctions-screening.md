# Sanctions & Screening — team hub

> This financial-crime team is accountable for screening customers and payments against sanctions, PEP, and watchlist data, and for dispositioning every alert that screening produces.

## In one minute

This team is the institution's checkpoint against doing business with sanctioned parties, and its early-warning system on politically exposed ones: it screens customer names, counterparties, and payment instructions against OFAC, UN, EU, PEP, and internal watchlists, then works through the alerts that fire. Most alerts are false positives — a common name that merely resembles a listed party — so the daily reality is high-volume triage to separate genuine matches from noise, fast and without missing a true hit. PEP screening adds a second axis to the same problem: even when the customer *is* the listed person, the question remains whether that entry still carries material risk, or whether it names a small-town official who stepped down eleven years ago. "Good" looks like zero missed true matches (full recall), a steadily cleared backlog, and every disposition documented well enough to defend to an examiner. AI can do the heavy lifting on the repetitive parts: pre-scoring alerts by likelihood, drafting the rationale for each disposition, and flagging the handful that need a closer human look — which is where the toolkit's largest payoff sits. What AI cannot do is make the call: it never auto-clears, auto-blocks, or files anything, and the listed-party data it screens against is only as current as the watchlist it is given.

> **In plain terms:** the team checks every name and payment against the sanctions and PEP lists, and the tools sort the mountain of "probably-not-a-match" alerts so a human can focus on the few that actually matter.

## What this team owns

- Name and entity screening, and the disposition of each hit that screening generates
- False-positive triage of the sanctions-alert backlog at scale (illustratively ~50k alerts a month)
- PEP screening and status assessment — the right-party question and the still-material question
- On-chain and wallet sanctions screening for digital-asset activity
- Maintaining awareness of sanctions-evasion typologies so screening logic stays current

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Triage the ~50k/month false-positive alert backlog | sanctions-name-screening | framework (runnable, recall 1.0, 92% FP-cut) | [../frameworks/sanctions-name-screening/](../frameworks/sanctions-name-screening/) |
| Triage PEP alerts on both axes (right party? in-scope status?) | pep-screening | framework (runnable, recall 1.0, 84% FP-cut) | [../frameworks/pep-screening/](../frameworks/pep-screening/) |
| Screen and disposition a single name/entity/vessel ad hoc | sanctions-watchlist-screen | prompt | [../prompts/compliance/sanctions-watchlist-screen.md](../prompts/compliance/sanctions-watchlist-screen.md) |
| Disposition one PEP alert (prominence, step-down, jurisdiction) | pep-screening-disposition | prompt | [../prompts/compliance/pep-screening-disposition.md](../prompts/compliance/pep-screening-disposition.md) |
| Screen a blockchain address against sanctions | onchain-sanctions-monitor | prompt | [../prompts/blockchain/onchain-sanctions-monitor.md](../prompts/blockchain/onchain-sanctions-monitor.md) |
| Keep the underlying list data deduplicated and current | watchlist-knowledge-base | framework (runnable, 0 false merges) | [../frameworks/watchlist-knowledge-base/](../frameworks/watchlist-knowledge-base/) |
| Look up evasion typologies and the regulatory map | aml-typologies | reference | [../reference/aml-typologies.md](../reference/aml-typologies.md) |
| Render any output as Word/Excel/PDF/HTML | BASE.md | companion | [../BASE.md](../BASE.md) |

## How the pieces fit

The prompts handle one item at a time: sanctions-watchlist-screen for a single name, entity, or vessel, pep-screening-disposition for a single PEP alert, and onchain-sanctions-monitor for a single blockchain address. The frameworks are the volume engines — they score and route a whole backlog at once, cutting the false positives a human has to read while keeping full recall on true hits. sanctions-name-screening and pep-screening are the same shape applied to different questions: the first asks only "is this the listed party?", the second asks that *and* "does the entry still carry material risk?", clearing a former low-level official past the documented step-down window while never auto-clearing a current PEP or a former head of state. Underneath both, watchlist-knowledge-base keeps the list data itself deduplicated and change-tracked, so the engines screen against something current. The reference keeps everyone's judgment sharp on how evasion actually happens, and BASE.md turns any of these outputs into a finished Word, Excel, PDF, or HTML deliverable. A typical chain: single-case screen (prompt) or backlog scoring (framework) -> triage and route -> human disposition -> render the record with BASE.md.

## Capabilities & limitations

**What these tools DO**

- Pre-score and rank alerts by match likelihood, then route the noise away from the genuine candidates
- Draft a defensible, documented rationale for each disposition a human reviewer can confirm
- Screen names, entities, vessels, and blockchain addresses against sanctions and watchlist data
- Separate the two PEP questions — right party, and materially in-scope status — instead of collapsing them into one score
- Keep evasion-typology and regulatory context one click away so screening logic stays informed
- Produce the final deliverable in the format an examiner or stakeholder expects

**What these tools deliberately do NOT do**

- The frameworks are reference implementations for triage and routing — not production screening controls
- They score and route, but a human makes every clear, escalate, or block decision
- They auto-clear only on a provable named cause; a bare common-name match with no identifying detail always goes to a person
- They never auto-clear a current PEP, a senior former one, or any corroborated match, whatever the score says
- They never auto-block a payment, freeze an account, or file a report
- They are only as accurate as the watchlist data supplied — a stale list yields stale results
- They do not replace the institution's system of record or its second-line review

## Start here

1. Open the framework at [../frameworks/sanctions-name-screening/](../frameworks/sanctions-name-screening/) and read its README to see how backlog triage scores and routes alerts while preserving full recall — then read [../frameworks/pep-screening/](../frameworks/pep-screening/) to see the same discipline applied to a two-axis question.
2. Run one real case end to end with [../prompts/compliance/sanctions-watchlist-screen.md](../prompts/compliance/sanctions-watchlist-screen.md) (or [../prompts/compliance/pep-screening-disposition.md](../prompts/compliance/pep-screening-disposition.md) for a PEP hit, [../prompts/blockchain/onchain-sanctions-monitor.md](../prompts/blockchain/onchain-sanctions-monitor.md) for a wallet) to feel how a single disposition is drafted.
3. Render that result into a shareable record with [../BASE.md](../BASE.md), and keep [../reference/aml-typologies.md](../reference/aml-typologies.md) open as the standing reference for evasion patterns and the regulatory map.
