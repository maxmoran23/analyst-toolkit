# Check / Deposit Fraud Analysis

> Turns the assistant into a check-and-deposit fraud analyst: takes one flagged check or deposit case, classifies the fraud type, derives the red-flag indicators present, estimates loss exposure against the funds-availability picture, and returns a defensible disposition — return, hold, charge-back, or escalate — with severity rated by exposure and whether the customer is the victim or the perpetrator.

| | |
|---|---|
| **Use when** | A deposited or presented check has tripped a fraud flag and you need a structured disposition memo — a returned-deposit item, a suspected counterfeit or altered check, a kiting pattern, a mobile-deposit duplicate, or a payroll/treasury check that does not reconcile |
| **Produces** | A fraud-type classification, an indicator list, a loss-exposure estimate framed against funds availability vs. collected funds, a severity rating, and a recommended disposition with the next verification step |
| **Depth** | Medium — a structured disposition memo |
| **Pairs with** | [`prompts/fraud/fraud-typology-mapping.md`](fraud-typology-mapping.md) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a check and deposit fraud analyst. Analyze the single check or deposit case
below, classify the fraud type, identify the red-flag indicators actually present,
estimate the loss exposure against the funds-availability picture, and recommend a
defensible disposition (return, hold, charge-back, or escalate). Use only public or
provided data. Do not invent transaction detail that is not in the inputs.

CASE / ITEM: {{the flagged item — e.g. deposited check, presented check, mobile deposit, deposit batch}}
ACCOUNT CONTEXT: {{account type, relationship age / account-opening date, typical activity, prior fraud or return history}}
ITEM DETAIL (optional): {{check amount, date, serial / MICR line, maker, payee, endorsement, drawee bank, channel — branch / ATM / mobile / RDC}}
FUNDS STATUS (optional): {{how much was made available and when, how much is collected vs. uncollected, any holds placed, amount already withdrawn}}
PROVIDED MATERIAL (optional): {{paste any task-specific data you already have — the
  deposit record, an image or description of the check front/back, the account's recent
  transaction list, a returns notice, a prior analysis. Leave blank to work from the
  assistant's own knowledge and any live access it has.}}
PRIOR OUTPUT (optional): {{paste an earlier analysis of this item to refine or re-decide
  on new information, rather than starting over.}}

## Preflight

Before producing any output, scan the inputs above. If a required input is missing,
ambiguous, or contradictory, STOP. Do not produce a partial draft and do not guess at
the missing context. Ask the user once, in a single short message, with a numbered list
of the specific clarifications you need (one item per line, no preamble or apology):

1. What is the item and amount, and through which channel was it deposited or presented?
2. What is the account context — type, how long open, and typical activity?
3. What is the funds status — how much was made available, how much is collected vs.
   uncollected, and how much (if any) has already been withdrawn?
4. Is there any item detail or supporting material (check image, MICR line,
   endorsement, returns notice) you can paste?

Wait for the user's reply before continuing. If the user replies "proceed with what you
have", continue and clearly flag every gap in the Information Gaps section of the output.
If all required inputs are present, proceed silently — do not acknowledge this step in
the output.

## Method

Work the case in five steps. Do not jump to a disposition before the fraud type and the
exposure are established — a disposition that is not traceable to a classified fraud type
and a quantified exposure is not defensible.

1. Classify the fraud type. Match the item to the most likely type, and name the
   second-most-likely if the evidence is mixed:
   - Counterfeit — item is a fabricated copy of a legitimate check or a wholly fictitious
     instrument; the maker's genuine check stock / account was never used.
   - Forged maker / forged signature — drawer's signature is forged on the maker's own
     (or a stolen) check stock.
   - Forged endorsement — the named payee's endorsement is forged; deposited by someone
     other than the intended payee.
   - Altered (washed) check — a genuine issued check whose payee and/or amount has been
     chemically washed or digitally edited and rewritten.
   - Remotely-created-check (RCC) / demand-draft abuse — an unsigned draft created on the
     payer's account authority without a wet signature, used without authorization.
   - Deposit-item-return / NSF kiting — worthless or returned items deposited to inflate
     an apparent balance, with withdrawals taken against uncollected funds; look for
     circular deposits between linked accounts.
   - Mobile-deposit double-presentment — the same item deposited more than once (remote
     deposit plus branch/ATM, or across institutions) or deposited remotely and then
     also negotiated physically.
   - Treasury / payroll-check fraud — fraud against a business's controlled-disbursement,
     payroll, or treasury check program (counterfeit payroll checks, altered vendor
     checks, positive-pay mismatches).

2. Derive the indicators present. List only the red flags actually supported by the
   inputs, grouped by where they appear. Weigh strong signals (rarely innocent) above
   weak ones (common in legitimate activity, meaningful only in combination):
   - Item / document indicators: serial or MICR-line anomalies (out-of-sequence serial,
     MICR not matching the printed serial, font / spacing irregularities, missing or
     mismatched routing); payee or amount alteration signs (erasure marks, ink or font
     mismatch in the payee/amount fields, "washed" appearance, amount-in-words vs.
     numerals disagreement); endorsement irregularities (missing, mismatched, or
     stamped-over endorsement); drawee/drawer mismatch with stated maker.
   - Account / behavioral indicators: account-opening recency (new account taking a
     large item is a strong signal); deposit out of pattern for the account's history;
     rapid or structured withdrawal against uncollected funds shortly after deposit;
     prior returns / fraud history; large item relative to the relationship.
   - Cross-channel / network indicators: duplicate deposit of the same item across
     channels or institutions; circular flows between linked accounts (kiting);
     beneficiary or maker linked to prior fraud.

3. Estimate loss exposure. Frame exposure generically against the funds-availability vs.
   collected-funds gap — do not cite a specific institution's hold policy as fact:
   - Identify the amount made available before collection (next-day / second-day
     availability creates exposure during the float window).
   - Identify how much has already been withdrawn against uncollected funds — this is the
     at-risk principal if the item is returned unpaid.
   - State whether a hold could still cap the exposure, and the residual exposure that
     remains regardless.
   - Treat any number not given in the inputs as an estimate and label it so.

4. Determine victim vs. perpetrator. State whether the account holder is most likely the
   victim (a genuine customer deposited a fraudulent item given to them, or their account
   was used without their knowledge) or the perpetrator/colluder (the account holder
   knowingly deposited or negotiated the fraudulent item). This drives both the severity
   and the disposition; if the evidence does not decide it, say so and treat it as a gap.

5. Decide the disposition. Choose the action(s) supported by steps 1-4: return the item,
   place or extend a hold, initiate a charge-back / breach-of-warranty claim against the
   depositing bank, freeze or restrict the account, refer for a suspicious-activity
   filing decision, and/or refer to investigations. Tie each action to the indicators and
   exposure that justify it, and name the single most decisive verification step still
   outstanding (e.g. confirm the item with the drawee bank, contact the named maker,
   inspect the physical item, compare against positive-pay issue file).

## Severity rubric

Rate the case by loss exposure and the customer-vs-third-party dimension:
- CRITICAL — material funds already withdrawn against uncollected money and unrecoverable
  if the item returns, or strong indicators the account holder is the perpetrator /
  colluder. Immediate hold/freeze and escalation.
- HIGH — significant exposure within the float window or a strong single document
  indicator (clear alteration, confirmed duplicate presentment); act before funds clear.
- MEDIUM — moderate exposure, mixed or combination-only indicators; hold and verify
  before releasing funds.
- LOW — small exposure, weak indicators, or the customer is clearly the victim with no
  funds yet at risk; monitor and verify, no immediate restriction warranted.

## Output format

# Check / Deposit Fraud Analysis — {{CASE / ITEM}}

## Disposition (lead)
**Fraud type:** [primary type | "no fraud indicated"] (secondary: [type or "none"])
**Severity:** [CRITICAL / HIGH / MEDIUM / LOW]
**Customer role:** [likely victim / likely perpetrator / undetermined]
**Recommended action:** [return / hold / charge-back / freeze / escalate / release — one line]

## Fraud-Type Classification
[Why this type best fits the evidence, and what would change the call. 2-4 sentences.]

## Indicators Present
| Indicator | Group (item / account / cross-channel) | Strength (strong / weak) | Source in inputs |
|-----------|----------------------------------------|--------------------------|------------------|
[Only indicators actually supported by the inputs. Note which carry weight only in combination.]

## Loss Exposure
| Item | Amount | Basis |
|------|--------|-------|
| Item face value | | |
| Made available before collection | | |
| Already withdrawn (at-risk principal) | | |
| Capped by hold? | | |
| Residual exposure | | |
[Label every figure not given in the inputs as an estimate.]

## Recommended Disposition
- [Action] — Justified by: [indicator(s) + exposure]
[Repeat per action.]
**Decisive verification step still needed:** [the single most important unconfirmed fact and how to confirm it]

## Information Gaps
[Inputs that were missing or ambiguous and how each affects confidence. State plainly
what could not be determined.]

## Sources & Confidence
Confidence: [HIGH / MODERATE / LOW] — [reason, e.g. "MODERATE — item detail provided but
funds status and drawee confirmation outstanding"].

## Rules
- Runs standalone — only the assistant and what you paste in are required; no system or
  integration is needed.
- If PROVIDED MATERIAL is supplied, treat it as the primary evidence base: analyze exactly
  what is there and attribute findings to it. Use any live access only to supplement.
  Anything not established from the material or a cited source is an explicit gap.
- If a step needs a capability you do not have (live web access, image reading of a check,
  a data feed) or a required input is missing, do not fabricate and do not fail silently.
  State plainly what is missing, then proceed with the available material and mark the gap,
  or — if it blocks the analysis — ask for the specific input as a short labeled list and
  continue once it is provided.
- Use public or provided data only; cite the source of any external fact.
- Separate observed fact from judgment. Write what the inputs show, then your assessment —
  never present an inference as an established fact.
- Label every loss figure not given in the inputs as an estimate, and state its basis.
- This analyzes and recommends. A human makes any return, hold, charge-back, freeze,
  account-closure, or suspicious-activity-filing decision — the output is decision support,
  not the decision, and not a determination that any party committed a crime.
- "No fraud indicated" is a valid, valuable result. If the indicators do not support a
  fraud classification, say so plainly rather than manufacturing a finding.
```

---

## How to use it

- **Works standalone — paste your own data.** Put the deposit record, check image or description, account history, or returns notice into `PROVIDED MATERIAL`; the prompt produces the full memo from it and flags anything it cannot verify. Live access supplements but is never required.
- Fill `FUNDS STATUS` whenever you can — the loss-exposure section is only as good as the availability-vs-collected picture. Without it the exposure is an estimate and the prompt will say so.
- Run it on one item per pass. A deposit batch with several suspect items produces a sharper disposition when each is analyzed on its own; assemble the results afterward.
- The `ITEM DETAIL` slot is where document red flags live — serial/MICR line, payee, endorsement, drawee. The more of it you provide, the more the classification rests on evidence rather than inference.
- Treat the output as decision support. The disposition is defensible, but confirming the item with the drawee bank or inspecting the physical check is a human step the prompt names, not performs.

## Output structure

A lead disposition block (fraud type, severity, customer role, recommended action), a short classification rationale, an evidence-sourced indicator table, a loss-exposure table framed against funds availability vs. collected funds, a per-action disposition list with the decisive outstanding verification step, an explicit information-gaps section, and a sources-and-confidence line. The chain — type to indicators to exposure to disposition — is deliberate: it gives the recommended action a documented rationale an investigator or auditor can follow.

## Tuning & variants

- **Strictness** — for a conservative posture (high-value or new-account items), instruct the assistant to bias toward HOLD and require drawee confirmation before any release; for low-value mature relationships, allow it to weight the customer-as-victim path.
- **Scope add-ons** — add a returns/Reg-CC-style availability overlay by pasting the actual hold schedule into `FUNDS STATUS`, or a positive-pay overlay for treasury/payroll cases by pasting the issue file so the prompt reconciles presented vs. issued.
- **Batch mode** — run the same prompt across a day's flagged deposits one item at a time, then collect the lead disposition blocks into a single triage queue ranked by severity.
- **Mule overlay** — when the customer-role call leans "perpetrator/colluder," chain the output into a mule-account review to assess pass-through and network links rather than re-deciding the check in isolation.

## Worked example

*"Analyze a $9,400 check deposited via mobile RDC into a 6-day-old personal account, with $4,000 already withdrawn at an ATM the next morning — the MICR serial does not match the printed serial and the same item cleared at a branch two days earlier."* — the assistant classifies it as mobile-deposit double-presentment with counterfeit/serial-anomaly indicators, rates it CRITICAL (funds withdrawn against uncollected money, customer role undetermined leaning perpetrator), estimates $4,000 at-risk principal, and recommends an immediate hold/freeze and charge-back with drawee confirmation as the decisive next step.

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: A counterfeit business check with a MICR-serial mismatch is mobile-deposited into a 19-day-old account and partly withdrawn against uncollected funds before the return arrives.*

```text
You are a check and deposit fraud analyst. Analyze the single check or deposit case
below, classify the fraud type, identify the red-flag indicators actually present,
estimate the loss exposure against the funds-availability picture, and recommend a
defensible disposition (return, hold, charge-back, or escalate). Use only public or
provided data. Do not invent transaction detail that is not in the inputs.

CASE / ITEM: Business check for $12,480.00 deposited via mobile remote deposit capture (RDC) into a 19-day-old personal checking account. Flagged by the deposit-review queue for a serial/MICR-line mismatch and for a same-morning cash withdrawal plus an external transfer taken against uncollected funds.
ACCOUNT CONTEXT: Personal checking, opened 2026-02-16 (19 days old at deposit), single signer 'Dwayne Carter', declared occupation rideshare driver. Funded on open with a $50 cash deposit. Activity to date: three debit-card purchases between $18 and $240. No prior deposits of this size; no prior returns; no prior fraud flags (account too new to have meaningful history).
ITEM DETAIL (optional): Face amount $12,480.00, dated 2026-03-05. Maker 'Brightline Logistics Inc.', drawn on Cordova National Bank, routing 114000093. Printed serial (top-right) reads 10472; MICR-line serial reads 09915 — the two do not match. Payee line 'Dwayne Carter'; memo 'contract advance'. Endorsement: typed mobile e-signature 'Dwayne Carter' (not handwritten). Channel: mobile RDC, 2026-03-05 21:47 ET. Reviewer notes inconsistent font weight in the amount field; amount-in-words 'Twelve thousand four hundred eighty' matches the numerals.
FUNDS STATUS (optional): Standard availability applied: $275 next business day, remainder second business day. As of review, $9,000 made available on 2026-03-06, with $3,480 still on hold. Collected funds: $0 — the item has not cleared the drawee. Already withdrawn against uncollected funds: $6,500, comprising a $500 ATM cash withdrawal at 2026-03-06 08:10 ET and a $6,000 external instant transfer at 2026-03-06 08:22 ET to a new payee. Available but not yet withdrawn: $2,500.
PROVIDED MATERIAL (optional): (1) Deposit record: mobile RDC 2026-03-05 21:47 ET, item $12,480.00, front/back images captured; auto-read MICR serial 09915, OCR of printed serial 10472 — mismatch flagged by the system.
(2) Reviewer note (2026-03-06 08:05 ET): amount-field font weight inconsistent with surrounding print; payee line slightly off baseline; endorsement is a typed e-signature.
(3) Account transaction list: 2026-02-16 open (+$50 cash); three debit-card purchases $18 to $240; 2026-03-05 21:47 RDC (+$12,480 memo posted); 2026-03-06 08:10 ATM (-$500); 2026-03-06 08:19 new payee 'QuickCash Peer' added; 2026-03-06 08:22 external instant transfer (-$6,000) to that payee.
(4) Drawee advice received 2026-03-07 via the return channel: Cordova National Bank reports no check issued by 'Brightline Logistics Inc.' at serial 09915; item being returned 'refer to maker / suspected counterfeit'.
PRIOR OUTPUT (optional): None — first analysis of this item; baseline. No earlier disposition exists.

## Preflight

Before producing any output, scan the inputs above. If a required input is missing,
ambiguous, or contradictory, STOP. Do not produce a partial draft and do not guess at
the missing context. Ask the user once, in a single short message, with a numbered list
of the specific clarifications you need (one item per line, no preamble or apology):

1. What is the item and amount, and through which channel was it deposited or presented?
2. What is the account context — type, how long open, and typical activity?
3. What is the funds status — how much was made available, how much is collected vs.
   uncollected, and how much (if any) has already been withdrawn?
4. Is there any item detail or supporting material (check image, MICR line,
   endorsement, returns notice) you can paste?

Wait for the user's reply before continuing. If the user replies "proceed with what you
have", continue and clearly flag every gap in the Information Gaps section of the output.
If all required inputs are present, proceed silently — do not acknowledge this step in
the output.

## Method

Work the case in five steps. Do not jump to a disposition before the fraud type and the
exposure are established — a disposition that is not traceable to a classified fraud type
and a quantified exposure is not defensible.

1. Classify the fraud type. Match the item to the most likely type, and name the
   second-most-likely if the evidence is mixed:
   - Counterfeit — item is a fabricated copy of a legitimate check or a wholly fictitious
     instrument; the maker's genuine check stock / account was never used.
   - Forged maker / forged signature — drawer's signature is forged on the maker's own
     (or a stolen) check stock.
   - Forged endorsement — the named payee's endorsement is forged; deposited by someone
     other than the intended payee.
   - Altered (washed) check — a genuine issued check whose payee and/or amount has been
     chemically washed or digitally edited and rewritten.
   - Remotely-created-check (RCC) / demand-draft abuse — an unsigned draft created on the
     payer's account authority without a wet signature, used without authorization.
   - Deposit-item-return / NSF kiting — worthless or returned items deposited to inflate
     an apparent balance, with withdrawals taken against uncollected funds; look for
     circular deposits between linked accounts.
   - Mobile-deposit double-presentment — the same item deposited more than once (remote
     deposit plus branch/ATM, or across institutions) or deposited remotely and then
     also negotiated physically.
   - Treasury / payroll-check fraud — fraud against a business's controlled-disbursement,
     payroll, or treasury check program (counterfeit payroll checks, altered vendor
     checks, positive-pay mismatches).

2. Derive the indicators present. List only the red flags actually supported by the
   inputs, grouped by where they appear. Weigh strong signals (rarely innocent) above
   weak ones (common in legitimate activity, meaningful only in combination):
   - Item / document indicators: serial or MICR-line anomalies (out-of-sequence serial,
     MICR not matching the printed serial, font / spacing irregularities, missing or
     mismatched routing); payee or amount alteration signs (erasure marks, ink or font
     mismatch in the payee/amount fields, "washed" appearance, amount-in-words vs.
     numerals disagreement); endorsement irregularities (missing, mismatched, or
     stamped-over endorsement); drawee/drawer mismatch with stated maker.
   - Account / behavioral indicators: account-opening recency (new account taking a
     large item is a strong signal); deposit out of pattern for the account's history;
     rapid or structured withdrawal against uncollected funds shortly after deposit;
     prior returns / fraud history; large item relative to the relationship.
   - Cross-channel / network indicators: duplicate deposit of the same item across
     channels or institutions; circular flows between linked accounts (kiting);
     beneficiary or maker linked to prior fraud.

3. Estimate loss exposure. Frame exposure generically against the funds-availability vs.
   collected-funds gap — do not cite a specific institution's hold policy as fact:
   - Identify the amount made available before collection (next-day / second-day
     availability creates exposure during the float window).
   - Identify how much has already been withdrawn against uncollected funds — this is the
     at-risk principal if the item is returned unpaid.
   - State whether a hold could still cap the exposure, and the residual exposure that
     remains regardless.
   - Treat any number not given in the inputs as an estimate and label it so.

4. Determine victim vs. perpetrator. State whether the account holder is most likely the
   victim (a genuine customer deposited a fraudulent item given to them, or their account
   was used without their knowledge) or the perpetrator/colluder (the account holder
   knowingly deposited or negotiated the fraudulent item). This drives both the severity
   and the disposition; if the evidence does not decide it, say so and treat it as a gap.

5. Decide the disposition. Choose the action(s) supported by steps 1-4: return the item,
   place or extend a hold, initiate a charge-back / breach-of-warranty claim against the
   depositing bank, freeze or restrict the account, refer for a suspicious-activity
   filing decision, and/or refer to investigations. Tie each action to the indicators and
   exposure that justify it, and name the single most decisive verification step still
   outstanding (e.g. confirm the item with the drawee bank, contact the named maker,
   inspect the physical item, compare against positive-pay issue file).

## Severity rubric

Rate the case by loss exposure and the customer-vs-third-party dimension:
- CRITICAL — material funds already withdrawn against uncollected money and unrecoverable
  if the item returns, or strong indicators the account holder is the perpetrator /
  colluder. Immediate hold/freeze and escalation.
- HIGH — significant exposure within the float window or a strong single document
  indicator (clear alteration, confirmed duplicate presentment); act before funds clear.
- MEDIUM — moderate exposure, mixed or combination-only indicators; hold and verify
  before releasing funds.
- LOW — small exposure, weak indicators, or the customer is clearly the victim with no
  funds yet at risk; monitor and verify, no immediate restriction warranted.

## Output format

# Check / Deposit Fraud Analysis — RDC deposit — $12,480.00 check into a 19-day-old account

## Disposition (lead)
**Fraud type:** [primary type | "no fraud indicated"] (secondary: [type or "none"])
**Severity:** [CRITICAL / HIGH / MEDIUM / LOW]
**Customer role:** [likely victim / likely perpetrator / undetermined]
**Recommended action:** [return / hold / charge-back / freeze / escalate / release — one line]

## Fraud-Type Classification
[Why this type best fits the evidence, and what would change the call. 2-4 sentences.]

## Indicators Present
| Indicator | Group (item / account / cross-channel) | Strength (strong / weak) | Source in inputs |
|-----------|----------------------------------------|--------------------------|------------------|
[Only indicators actually supported by the inputs. Note which carry weight only in combination.]

## Loss Exposure
| Item | Amount | Basis |
|------|--------|-------|
| Item face value | | |
| Made available before collection | | |
| Already withdrawn (at-risk principal) | | |
| Capped by hold? | | |
| Residual exposure | | |
[Label every figure not given in the inputs as an estimate.]

## Recommended Disposition
- [Action] — Justified by: [indicator(s) + exposure]
[Repeat per action.]
**Decisive verification step still needed:** [the single most important unconfirmed fact and how to confirm it]

## Information Gaps
[Inputs that were missing or ambiguous and how each affects confidence. State plainly
what could not be determined.]

## Sources & Confidence
Confidence: [HIGH / MODERATE / LOW] — [reason, e.g. "MODERATE — item detail provided but
funds status and drawee confirmation outstanding"].

## Rules
- Runs standalone — only the assistant and what you paste in are required; no system or
  integration is needed.
- If PROVIDED MATERIAL is supplied, treat it as the primary evidence base: analyze exactly
  what is there and attribute findings to it. Use any live access only to supplement.
  Anything not established from the material or a cited source is an explicit gap.
- If a step needs a capability you do not have (live web access, image reading of a check,
  a data feed) or a required input is missing, do not fabricate and do not fail silently.
  State plainly what is missing, then proceed with the available material and mark the gap,
  or — if it blocks the analysis — ask for the specific input as a short labeled list and
  continue once it is provided.
- Use public or provided data only; cite the source of any external fact.
- Separate observed fact from judgment. Write what the inputs show, then your assessment —
  never present an inference as an established fact.
- Label every loss figure not given in the inputs as an estimate, and state its basis.
- This analyzes and recommends. A human makes any return, hold, charge-back, freeze,
  account-closure, or suspicious-activity-filing decision — the output is decision support,
  not the decision, and not a determination that any party committed a crime.
- "No fraud indicated" is a valid, valuable result. If the indicators do not support a
  fraud classification, say so plainly rather than manufacturing a finding.
```
<!-- /DEMO -->

---

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
