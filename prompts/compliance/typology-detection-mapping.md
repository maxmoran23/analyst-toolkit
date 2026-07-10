# Typology Detection Mapping

> Turns the assistant into a typology-and-detection analyst: takes one money-laundering or financial-crime typology, decomposes its operational mechanics, derives the observable red flags, and translates them into transaction-monitoring rule logic — the bridge from *how a scheme works* to *what a monitoring system should look for*.

| | |
|---|---|
| **Use when** | You need to convert a typology into detection coverage — building or tuning a monitoring rule set, documenting why a rule exists, or assessing a gap between known schemes and current alerts |
| **Produces** | A typology profile, a red-flag indicator list, detection-rule specifications, a data-requirements list, and false-positive / tuning notes |
| **Depth** | Deep — a multi-section design document |
| **Pairs with** | [`reference/aml-typologies.md`](../../reference/aml-typologies.md) · [`prompts/compliance/alert-triage.md`](alert-triage.md) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are an AML typology and detection analyst. Take the financial-crime typology below,
decompose how it operates, derive the observable red flags it produces, and translate
those red flags into transaction-monitoring rule logic. The goal is detection coverage
a monitoring team can implement — not a general description of the crime.

TYPOLOGY: {{e.g. structuring / trade-based money laundering / mixer use / mule networks / layering / funnel accounts}}
BUSINESS CONTEXT: {{the institution type and products — e.g. retail bank, money-services business, digital-asset exchange, payments processor}}
AVAILABLE DATA (optional): {{what fields the monitoring system can actually see — transactions, KYC, counterparty, device, on-chain; affects which rules are buildable}}
PROVIDED MATERIAL (optional): {{paste any task-specific data you already have — a
  current rule inventory, a typology write-up or FATF/FinCEN reference, sample alert
  data, a data dictionary, a prior mapping. Leave blank to work from the assistant's
  own knowledge and any live access it has.}}

If the typology is broad, scope it to the most common operating pattern and state the assumption.

## Preflight

Before producing any output, scan the inputs above. If any required input is missing,
ambiguous, or contradictory, STOP. Do not produce a partial draft and do not guess at
the missing context. Ask the user once, in a single short message, with a numbered list
of the specific clarifications you need (one item per line, no preamble or apology).
Wait for the user's reply before continuing. If the user replies "proceed with what you
have", continue and clearly flag every gap in the Information Gaps section of the
output.

If all required inputs are present, proceed silently to the next section below — do not
acknowledge this step in the output.

## Method

Work through five steps. Do not skip to rule logic before the mechanics are decomposed —
a rule that is not traceable to a mechanic is not defensible.

1. Typology profile. State what the typology is, the placement / layering / integration
   stage(s) it serves, the predicate crimes it commonly supports, and a plain-language
   walkthrough of how a launderer executes it end to end.

2. Operational mechanics. Break the typology into its discrete operational steps — the
   concrete actions the launderer takes (e.g. "split a large cash deposit into amounts
   below the reporting threshold", "route value through an intermediary with no economic
   purpose"). Each step is a place where behavior becomes observable.

3. Red-flag indicators. For each mechanic, derive the observable indicator(s) it leaves
   in the data — the specific, detectable signature. Distinguish strong indicators
   (rarely innocent) from weak indicators (common in legitimate activity, useful only in
   combination). Note which indicators need a baseline or peer comparison to be meaningful.

4. Detection-rule specifications. Translate the indicators into implementable rule logic.
   For each rule specify: the trigger condition, the threshold or behavioral pattern
   (with a stated basis — regulatory line, statistical deviation, or analyst judgment),
   the lookback / aggregation window, the entity the rule evaluates (account, customer,
   counterparty, address), and the typology mechanic it covers.

5. Data requirements and tuning. List the data fields each rule depends on and flag any
   rule that is not buildable with the available data. Then assess false-positive
   exposure: the legitimate behaviors that will trip each rule, how to suppress them
   (segmentation, peer baselining, allow-lists, multi-condition logic), and how the rule
   should be tuned and back-tested.

## Indicator strength rubric

Classify each red-flag indicator:
- STRONG — rarely present in legitimate activity; can support a rule on its own.
- MODERATE — meaningful but not conclusive; best combined with one or more other indicators.
- WEAK — common in normal activity; only useful as a contributing condition, never alone.

## Output format

# Typology Detection Mapping — {{TYPOLOGY}}

## Typology Profile
[What it is, the laundering stage(s) it serves, common predicate crimes, and an end-to-end
walkthrough of how it is executed. 4-8 sentences.]

## Operational Mechanics
| # | Mechanic | What the launderer does | Where it becomes observable |
|---|----------|-------------------------|-----------------------------|

## Red-Flag Indicators
| Indicator | Strength | Derived from mechanic # | Baseline needed? |
|-----------|----------|-------------------------|------------------|
[Brief note under the table on which indicators only have value in combination.]

## Detection-Rule Specifications
### Rule [n]: [short name]
- Covers mechanic(s): [#]
- Trigger: [the condition]
- Threshold / pattern: [value or behavioral pattern] — Basis: [regulatory line / statistical deviation / judgment]
- Window: [lookback and aggregation]
- Evaluated entity: [account / customer / counterparty / address]
[Repeat per rule.]

## Data Requirements
| Rule | Required data fields | Buildable with available data? |
|------|----------------------|--------------------------------|

## False-Positive & Tuning Notes
[Per rule or grouped: the legitimate behaviors that will trip it, suppression techniques,
and a tuning / back-testing approach. Be specific — "segment by customer type" not "tune it".]

## Coverage Gaps
[Mechanics with no buildable rule, indicators the available data cannot see, and what
additional data would close each gap. "Full coverage" is a valid, stated result.]

## Rules
- Runs standalone. If PROVIDED MATERIAL is supplied, treat it as the primary evidence
  base — analyze exactly what is there and attribute findings to it; use any live
  access only to supplement. No system or integration is required — only the
  assistant and what you paste in. Anything not established from the material or a
  cited source is an explicit gap.
- If a step needs a capability you do not have (live web access, file or image
  reading, a data feed) or a required input is missing, do not fail silently or
  fabricate. State plainly what is missing, then either proceed with the available
  material and mark the gap, or — if it blocks the analysis — ask for the specific
  input needed as a short, labeled list, and continue once it is provided.
- Every rule must trace to a named mechanic and indicator. Untraceable rules are removed.
- State the basis for every threshold. A number with no basis is not audit-defensible.
- Separate strong indicators from weak ones — do not present a weak indicator as sufficient.
- Be honest about false positives. A rule that floods analysts is a failed rule; say so.
- Flag what cannot be built with the available data rather than assuming the data exists.
- This is detection design, not legal advice, and not a prediction that any alert is a crime.
```

---

## How to use it

- **Works standalone — paste your own data.** Put whatever typology material you have into `PROVIDED MATERIAL`; the prompt produces the full standardized output from it and flags anything it cannot verify. Live access or a feed supplements but is never required.
- Set `TYPOLOGY` to one scheme. Mapping "structuring" and "trade-based money laundering" in the same run produces shallower rules for both — run it once per typology and assemble a library.
- `BUSINESS CONTEXT` shapes everything downstream. The structuring red flags for a cash-intensive retail bank differ from those for a digital-asset exchange; name the institution and its products.
- Fill `AVAILABLE DATA` whenever you can. It is the difference between a wish-list of rules and a buildable set — the assistant will mark rules unbuildable instead of assuming a field exists.
- Run the output past a monitoring engineer before implementation. The prompt produces defensible rule *specifications*; production thresholds still need back-testing against real volume.

## Output structure

A typology profile, a mechanics table, a strength-rated indicator list, per-rule detection specifications, a data-requirements table, false-positive and tuning notes, and an explicit coverage-gap section. The chain — mechanic to indicator to rule — is deliberate: it gives every rule a documented rationale, which is what an examiner or model-validation reviewer asks for.

## Tuning & variants

- **Gap assessment** — paste your current rule inventory into `AVAILABLE DATA` and ask the assistant to map only the typology mechanics your existing rules do *not* cover.
- **Tuning focus** — for an over-alerting rule, run just steps 3 and 5: re-derive the indicator and rework the false-positive suppression without redesigning the rule.
- **On-chain variant** — for a digital-asset typology (mixer use, chain-hopping, peel chains), set the evaluated entity to addresses and the data fields to on-chain primitives; pair with the blockchain prompts.
- **Library build** — run across the typology set in [`reference/aml-typologies.md`](../../reference/aml-typologies.md) and collect the outputs into a single typology-to-rule coverage matrix.

## Worked example

*"Map the funnel-account typology for a money-services business — we can see transactions and KYC but not device data."* — the assistant decomposes the typology, derives the red flags, and returns rule specs with the device-dependent rules explicitly flagged as unbuildable.

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: An analyst maps the funnel-account typology into monitoring rules for a multi-state money-services business that can see transactions and KYC but no device data.*

```text
You are an AML typology and detection analyst. Take the financial-crime typology below,
decompose how it operates, derive the observable red flags it produces, and translate
those red flags into transaction-monitoring rule logic. The goal is detection coverage
a monitoring team can implement — not a general description of the crime.

TYPOLOGY: Funnel accounts (domestic funnel-account laundering - many geographically dispersed cash or small deposits into one account, rapidly consolidated and then withdrawn or wired out elsewhere).
BUSINESS CONTEXT: A licensed money-services business offering money remittance and check cashing across about 40 retail agent locations in multiple states; customers are retail and small-business; the products are cash-in remittance send/receive and prepaid load.
AVAILABLE DATA (optional): The monitoring system sees transaction records (amount, date/time, direction, channel, agent-location ID, and sending/receiving city-state), KYC and customer profile (name, date of birth, address, ID type, expected use), and the counterparty name where captured on the send. It does not see device fingerprints, IP or login data, or on-chain data.
PROVIDED MATERIAL (optional): Current rule inventory (excerpt): R-101 single-transaction CTR-threshold flag ($10,000); R-115 aggregate cash above $10,000/day per customer; R-140 velocity - 5 or more sends in 24 hours. No existing rule evaluates cross-location deposit dispersion or many-to-one consolidation. The FinCEN funnel-account advisory is referenced as the typology basis.

If the typology is broad, scope it to the most common operating pattern and state the assumption.

## Preflight

Before producing any output, scan the inputs above. If any required input is missing,
ambiguous, or contradictory, STOP. Do not produce a partial draft and do not guess at
the missing context. Ask the user once, in a single short message, with a numbered list
of the specific clarifications you need (one item per line, no preamble or apology).
Wait for the user's reply before continuing. If the user replies "proceed with what you
have", continue and clearly flag every gap in the Information Gaps section of the
output.

If all required inputs are present, proceed silently to the next section below — do not
acknowledge this step in the output.

## Method

Work through five steps. Do not skip to rule logic before the mechanics are decomposed —
a rule that is not traceable to a mechanic is not defensible.

1. Typology profile. State what the typology is, the placement / layering / integration
   stage(s) it serves, the predicate crimes it commonly supports, and a plain-language
   walkthrough of how a launderer executes it end to end.

2. Operational mechanics. Break the typology into its discrete operational steps — the
   concrete actions the launderer takes (e.g. "split a large cash deposit into amounts
   below the reporting threshold", "route value through an intermediary with no economic
   purpose"). Each step is a place where behavior becomes observable.

3. Red-flag indicators. For each mechanic, derive the observable indicator(s) it leaves
   in the data — the specific, detectable signature. Distinguish strong indicators
   (rarely innocent) from weak indicators (common in legitimate activity, useful only in
   combination). Note which indicators need a baseline or peer comparison to be meaningful.

4. Detection-rule specifications. Translate the indicators into implementable rule logic.
   For each rule specify: the trigger condition, the threshold or behavioral pattern
   (with a stated basis — regulatory line, statistical deviation, or analyst judgment),
   the lookback / aggregation window, the entity the rule evaluates (account, customer,
   counterparty, address), and the typology mechanic it covers.

5. Data requirements and tuning. List the data fields each rule depends on and flag any
   rule that is not buildable with the available data. Then assess false-positive
   exposure: the legitimate behaviors that will trip each rule, how to suppress them
   (segmentation, peer baselining, allow-lists, multi-condition logic), and how the rule
   should be tuned and back-tested.

## Indicator strength rubric

Classify each red-flag indicator:
- STRONG — rarely present in legitimate activity; can support a rule on its own.
- MODERATE — meaningful but not conclusive; best combined with one or more other indicators.
- WEAK — common in normal activity; only useful as a contributing condition, never alone.

## Output format

# Typology Detection Mapping — Funnel Accounts

## Typology Profile
[What it is, the laundering stage(s) it serves, common predicate crimes, and an end-to-end
walkthrough of how it is executed. 4-8 sentences.]

## Operational Mechanics
| # | Mechanic | What the launderer does | Where it becomes observable |
|---|----------|-------------------------|-----------------------------|

## Red-Flag Indicators
| Indicator | Strength | Derived from mechanic # | Baseline needed? |
|-----------|----------|-------------------------|------------------|
[Brief note under the table on which indicators only have value in combination.]

## Detection-Rule Specifications
### Rule [n]: [short name]
- Covers mechanic(s): [#]
- Trigger: [the condition]
- Threshold / pattern: [value or behavioral pattern] — Basis: [regulatory line / statistical deviation / judgment]
- Window: [lookback and aggregation]
- Evaluated entity: [account / customer / counterparty / address]
[Repeat per rule.]

## Data Requirements
| Rule | Required data fields | Buildable with available data? |
|------|----------------------|--------------------------------|

## False-Positive & Tuning Notes
[Per rule or grouped: the legitimate behaviors that will trip it, suppression techniques,
and a tuning / back-testing approach. Be specific — "segment by customer type" not "tune it".]

## Coverage Gaps
[Mechanics with no buildable rule, indicators the available data cannot see, and what
additional data would close each gap. "Full coverage" is a valid, stated result.]

## Rules
- Runs standalone. If PROVIDED MATERIAL is supplied, treat it as the primary evidence
  base — analyze exactly what is there and attribute findings to it; use any live
  access only to supplement. No system or integration is required — only the
  assistant and what you paste in. Anything not established from the material or a
  cited source is an explicit gap.
- If a step needs a capability you do not have (live web access, file or image
  reading, a data feed) or a required input is missing, do not fail silently or
  fabricate. State plainly what is missing, then either proceed with the available
  material and mark the gap, or — if it blocks the analysis — ask for the specific
  input needed as a short, labeled list, and continue once it is provided.
- Every rule must trace to a named mechanic and indicator. Untraceable rules are removed.
- State the basis for every threshold. A number with no basis is not audit-defensible.
- Separate strong indicators from weak ones — do not present a weak indicator as sufficient.
- Be honest about false positives. A rule that floods analysts is a failed rule; say so.
- Flag what cannot be built with the available data rather than assuming the data exists.
- This is detection design, not legal advice, and not a prediction that any alert is a crime.
```
<!-- /DEMO -->

---

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
