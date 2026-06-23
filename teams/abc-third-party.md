# ABC, Third-Party & Correspondent Banking — team hub

> This financial-crime team manages risk from parties beyond the direct customer — vendors and intermediaries, bribery and corruption exposure, correspondent-banking relationships, and trade-based laundering.

## In one minute

This team looks outward from the customer to the web of relationships around the
institution: the vendors and agents it engages, the bribery-and-corruption exposure
those relationships carry, the correspondent banks it serves (and the banks *they*
serve, nested behind them), and the trade-finance flows that can disguise value
movement. The work is structured due diligence and risk rating — deciding whom to
onboard, on what conditions, and what to monitor. "Good" looks like high-risk
relationships identified before they are entered, controls matched to the risk, and
every decision documented and defensible. AI here can run the due-diligence scorecard,
flag the red flags (corruption touchpoints, opaque ownership, nesting, invoice
anomalies), rate the risk, and recommend controls. The relationship decision itself
stays with a human.

> **In plain terms:** the tools vet the companies, intermediaries, banks, and trade
> deals the institution deals with, and recommend whether and how to proceed.

## What this team owns

- Third-party / vendor due diligence at onboarding and periodic review
- Anti-bribery & corruption (ABC) risk assessment of relationships, transactions, and intermediaries
- Correspondent-banking and nested-account / downstream-correspondent risk
- Trade-based money laundering (TBML) red-flag analysis

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Run third-party / vendor due diligence | vendor-due-diligence | prompt | [../prompts/third-party/vendor-due-diligence.md](../prompts/third-party/vendor-due-diligence.md) |
| Assess anti-bribery & corruption risk | abc-risk-assessment | prompt | [../prompts/third-party/abc-risk-assessment.md](../prompts/third-party/abc-risk-assessment.md) |
| Assess correspondent / nested-account risk | correspondent-nested-risk | prompt | [../prompts/third-party/correspondent-nested-risk.md](../prompts/third-party/correspondent-nested-risk.md) |
| Analyze a trade transaction for TBML red flags | tbml-redflag-analysis | prompt | [../prompts/third-party/tbml-redflag-analysis.md](../prompts/third-party/tbml-redflag-analysis.md) |
| Assess the entity itself (8-domain) | entity-risk-assessment | prompt | [../prompts/compliance/entity-risk-assessment.md](../prompts/compliance/entity-risk-assessment.md) |
| Screen a party against sanctions/watchlists | sanctions-watchlist-screen | prompt | [../prompts/compliance/sanctions-watchlist-screen.md](../prompts/compliance/sanctions-watchlist-screen.md) |
| Render any output as Word/Excel/PDF/HTML | BASE.md | companion | [../BASE.md](../BASE.md) |

## How the pieces fit

vendor-due-diligence is the broad onboarding/periodic scorecard; it leans on
entity-risk-assessment for the entity read and sanctions-watchlist-screen for the
screening leg, and triggers abc-risk-assessment where corruption exposure is present.
correspondent-nested-risk handles the bank-to-bank relationships and the downstream
access hidden behind them, and tbml-redflag-analysis examines the trade flows that move
through them. Flow: identify the party/relationship -> screen & assess the entity ->
domain due diligence (vendor / ABC / correspondent / TBML) -> rate risk & set controls
-> human onboarding decision.

## Capabilities & limitations

**What these tools DO**

- Run a multi-domain due-diligence scorecard and produce a severity-tagged residual-risk rating
- Flag corruption red flags, ownership opacity, nesting / payable-through access, and trade anomalies
- Recommend mitigations, contract terms, and monitoring expectations

**What they deliberately do NOT do**

- They analyze and recommend; the onboard / decline / exit decision and any contract terms are human and governed
- They frame FCPA / UK Bribery Act / Wolfsberg standards generically — confirm the applicable rules
- They work from the information provided; they do not connect to vendor systems or registries

## Start here

1. For a new or reviewed third party, start with [vendor-due-diligence](../prompts/third-party/vendor-due-diligence.md); for a bank relationship, [correspondent-nested-risk](../prompts/third-party/correspondent-nested-risk.md).
2. Where government touchpoints or intermediaries are involved, add [abc-risk-assessment](../prompts/third-party/abc-risk-assessment.md); for trade flows, [tbml-redflag-analysis](../prompts/third-party/tbml-redflag-analysis.md).
3. Pair with [entity-risk-assessment](../prompts/compliance/entity-risk-assessment.md) and [sanctions-watchlist-screen](../prompts/compliance/sanctions-watchlist-screen.md) for the entity and screening legs, then render with [BASE.md](../BASE.md).
