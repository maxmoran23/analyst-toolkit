# Trade & Communications Surveillance — team hub

> This financial-crime team protects market integrity — detecting market abuse in trading activity and misconduct in communications, and building the investigation when one is warranted.

## In one minute

This team watches two streams: trading activity, for manipulation and insider dealing,
and communications (chat, email, voice), for collusion, information leakage, and
conduct risk. Both streams generate mostly false positives — a cancelled order is
usually just a cancelled order, and a keyword is usually just ordinary business
language — so the work is disciplined review that separates the genuinely abusive from
the benign, and assembles a defensible case on the rare hit that matters. "Good" looks
like real abuse caught and escalated, benign alerts closed with a clear reason, and
investigations documented to a standard a regulator would accept. AI here can classify
the pattern, read the alert in context, weigh intent against innocent explanations, and
draft the case narrative. It does not judge guilt or make a referral — it prepares the
analysis for a human and, ultimately, legal and compliance leadership.

> **In plain terms:** the tools sort the huge volume of "probably nothing" trade and
> chat alerts and build the file on the few that look like genuine abuse.

## What this team owns

- Trade-surveillance alert review for market abuse (spoofing, layering, wash trading, marking-the-close, front-running, insider dealing)
- Communications-surveillance review for conduct and market-integrity risk
- Market-abuse investigation and case-narrative assembly for a file or regulator referral

## The toolkit for this team

| Need | Tool | Type | Where |
| --- | --- | --- | --- |
| Review a trade-surveillance alert for abuse | trade-surveillance-review | prompt | [../prompts/surveillance/trade-surveillance-review.md](../prompts/surveillance/trade-surveillance-review.md) |
| Review a communications-surveillance alert | comms-surveillance-review | prompt | [../prompts/surveillance/comms-surveillance-review.md](../prompts/surveillance/comms-surveillance-review.md) |
| Build a market-abuse investigation case | market-abuse-case | prompt | [../prompts/surveillance/market-abuse-case.md](../prompts/surveillance/market-abuse-case.md) |
| Draft the broader investigation narrative | investigation-narrative | prompt | [../prompts/compliance/investigation-narrative.md](../prompts/compliance/investigation-narrative.md) |
| Render the case as Word/Excel/PDF/HTML | BASE.md | companion | [../BASE.md](../BASE.md) |

## How the pieces fit

The two review prompts are the front line: trade-surveillance-review for an
order/trade alert, comms-surveillance-review for a flagged communication — each
emphasizing context and false-positive discipline so noise is closed and only genuine
signals advance. A signal that survives review escalates to market-abuse-case, which
assembles the chronology, evidence, and intent analysis into a defensible file (and
investigation-narrative for the broader write-up). Flow: alert -> contextual review ->
escalate genuine signals -> case narrative -> human/legal decision.

## Capabilities & limitations

**What these tools DO**

- Classify the trading pattern or communications risk and judge intent against innocent explanations
- Apply false-positive discipline — a cancelled order or a keyword alone is not abuse
- Assemble a sourced, chronological market-abuse case suitable for a file or referral

**What they deliberately do NOT do**

- They analyze and recommend; the surveillance disposition, escalation, and any regulator referral are human decisions
- They reference market-abuse regimes (MAR, SEC/FINRA, CFTC) generically — confirm the applicable rule
- They work from the alert and data provided; they do not connect to order books or comms archives

## Start here

1. Start at the matching review prompt — [trade-surveillance-review](../prompts/surveillance/trade-surveillance-review.md) for a trade alert, [comms-surveillance-review](../prompts/surveillance/comms-surveillance-review.md) for a communication.
2. Close the benign ones with a stated reason; advance only the signals that survive contextual review.
3. For a surviving signal, build the file with [market-abuse-case](../prompts/surveillance/market-abuse-case.md) and render it with [BASE.md](../BASE.md).
