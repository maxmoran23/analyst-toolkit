> ILLUSTRATIVE SAMPLE — synthetic/illustrative content produced for format demonstration. Not a real assessment.

# Alert Triage — TM-ROUND-WIRE-7741 — 2026-05-20

Disposition: ESCALATE FOR REVIEW
Customer: Cedar Hollow Landscaping LLC (acct ****6209) | Alert reason: Burst of round-value outbound international wires inconsistent with the customer's stated business profile

> **Fictional scenario notice.** "Cedar Hollow Landscaping LLC" and every counterparty, account number, transaction, and figure below are synthetic, invented solely to demonstrate the output format of the Alert Triage prompt. Nothing here describes any real customer, business, or transaction.

## Alert Summary

Rule TM-ROUND-WIRE-7741 ("round-value cross-border wire velocity") fired on 2026-05-19 after account ****6209 sent five outbound international wires totaling $214,000.00 over nine calendar days, each in a whole-thousand amount, to four beneficiaries the account had never previously paid. The triggering behavior is the concentration of round-number, first-time cross-border payments in a short window from a domestic small-business account.

## Activity vs. Expected Profile

The customer is a fictional residential and commercial landscaping business, presented as opened 2021-03 (account age ~5 years), KYC risk rating LOW at last refresh (2025-04), with a stated expected profile of domestic operating activity — payroll, equipment, fuel, and nursery suppliers — and a stated expected monthly outbound volume of $30,000–$60,000. No international activity is recorded in the stated profile, and the prior 12 months show none.

The flagged activity deviates from that baseline on four measurable dimensions:

| Dimension | Stated / baseline profile | Flagged activity (2026-05-10 to 2026-05-19) | Deviation |
|---|---|---|---|
| Geography | 100% domestic in prior 12 months | 5 of 5 wires cross-border | New behavior — no precedent |
| Counterparties | Recurring domestic suppliers/payroll | 4 first-time foreign beneficiaries | New behavior — no precedent |
| Value pattern | Mixed/invoice-driven amounts | 5 of 5 whole-thousand amounts ($28k / $39k / $45k / $50k / $52k) | All round; none invoice-shaped |
| Volume / velocity | $30k–$60k outbound per month | $214,000.00 outbound in 9 days | ~3.6x–7.1x the stated monthly band, in under a third of a month |

Source for transaction figures: account ****6209 wire detail, 2026-05-10 through 2026-05-19 (5 records), summarized in the table below.

| Date | Amount (USD) | Beneficiary (fictional) | Beneficiary bank jurisdiction | First-time? |
|---|---|---|---|---|
| 2026-05-10 | $50,000.00 | Brightwater Trading Partners | Jurisdiction A | Yes |
| 2026-05-12 | $45,000.00 | Brightwater Trading Partners | Jurisdiction A | Yes |
| 2026-05-14 | $39,000.00 | Olivos Group Holdings | Jurisdiction B | Yes |
| 2026-05-16 | $52,000.00 | Keystone Equipment Importers | Jurisdiction C | Yes |
| 2026-05-19 | $28,000.00 | Marfil Consulting Services | Jurisdiction B | Yes |
| **Total** | **$214,000.00** | **4 distinct beneficiaries** | **3 jurisdictions** | **5 of 5** |

Two wires (2026-05-10 and 2026-05-12, $95,000.00 combined) went to a single beneficiary, "Brightwater Trading Partners," whose name does not indicate a landscaping-supply function. The wire-instruction memo fields, as recorded, read "consulting" (x2), "equipment," "services," and a blank — none referencing nursery stock, plant material, or landscaping equipment consistent with the customer's line of business. The activity is **anomalous for this customer**: it is not merely large, it is categorically different from five years of recorded behavior.

## Typology Assessment

The pattern is assessed against four typologies:

- **Pass-through / funnel-account behavior — consistent.** A small-business operating account sending a rapid burst of round-value funds to multiple new offshore beneficiaries, with payment purposes that do not match the business, is consistent with an account being used to move funds onward rather than to pay genuine trade obligations. This is the closest typology fit.
- **Trade-based laundering — partially consistent, unconfirmed.** Round-number payments to foreign "trading" and "import" counterparties with vague memo descriptions are a recognized trade-based-laundering indicator. The typology cannot be confirmed without invoices, shipping documents, or contracts — none are on file — so it is recorded as a partial fit and an open question, not a finding.
- **Structuring — not consistent.** No amount sits just below a regulatory reporting threshold; the wires are well above any cash-reporting line and are not cash. The round numbers here read as "untethered to an invoice," not as "engineered under a threshold."
- **Account takeover / fraud against the customer — possible, not established.** A sudden out-of-pattern burst can also indicate the customer's own account being compromised by a third party. This alternative is noted because it changes who the victim is, not whether the activity is unusual; it is one of the questions a reviewer must resolve.

## Factors Supporting a Concern

- Five first-time cross-border wires totaling $214,000.00 in nine days from an account with zero international activity in the prior 12 months (account ****6209 wire detail).
- Outbound velocity of $214,000.00 in nine days against a stated expected band of $30,000–$60,000 per month — a 3.6x–7.1x overage compressed into roughly nine days (KYC stated profile vs. wire detail).
- Every wire is a whole-thousand amount; none is shaped like a supplier invoice (wire detail, amount column).
- Payment purposes recorded in memo fields ("consulting," "services," "equipment," one blank) do not correspond to a landscaping business's expected suppliers (wire-instruction memo fields).
- Beneficiary names ("Trading Partners," "Group Holdings," "Importers," "Consulting Services") indicate trading/consulting/import functions, not landscaping supply (beneficiary detail).
- $95,000.00 — 44% of the total — routed to one new offshore beneficiary across two wires two days apart (wire detail, 2026-05-10 and 2026-05-12).

## Factors Contradicting a Concern

- The customer has a ~5-year tenure and a LOW KYC risk rating with no prior transaction-monitoring alerts (customer record; alert history shows none before TM-ROUND-WIRE-7741).
- No counterparty, beneficiary bank, or destination jurisdiction in the flagged set returned a sanctions-screening hit at the time of the wires (screening log for the 5 wires — clean).
- A genuine benign explanation is *possible* and cannot be excluded on the current file: a real business may legitimately begin importing equipment or nursery stock, or expand cross-border, and round-number payments can reflect deposits, retainers, or pro-forma amounts. This explanation is recorded as plausible but **unverified** — no invoice, contract, customer statement, or KYC update on file corroborates a new import or expansion line.
- The activity stopped after five wires within the nine-day window; there is no evidence in the data of it continuing past 2026-05-19 (wire detail ends 2026-05-19 — note this is also a function of the data cut-off, not necessarily a behavioral stop).

## Disposition Rationale

The flagged activity deviates from the customer's established profile on every measured dimension — geography, counterparty, value shape, and velocity — and fits a pass-through / funnel-account typology, with a partial and unconfirmed trade-based-laundering overlay. A benign explanation (a legitimate new import or cross-border expansion line) is plausible but is **not supported by anything in the file**: there are no invoices, no contracts, no customer correspondence, and no KYC update evidencing a changed business model. The triage rule is that a close requires a benign explanation that fits the facts, not merely the absence of proof of wrongdoing — that bar is not met here.

The factors do not, however, support a direct REFER FOR SUSPICIOUS-ACTIVITY REPORTING on the present record: there is no sanctions nexus, no confirmed illicit counterparty, and the funnel-account read rests on a pattern that a documented commercial explanation could still resolve. The defensible disposition is **ESCALATE FOR REVIEW** — the activity is unusual and not adequately explained, and it needs an investigative second look that can obtain the documents and the customer's account of the activity. The residual uncertainty is the purpose of the payments: the file cannot currently distinguish a genuine new trade line, a funnel-account misuse, or a third-party compromise of the account, and that distinction determines whether the matter ultimately closes or proceeds to a referral.

## Recommended Next Steps

- Escalate ****6209 to investigations with this triage as the case opener; classify the account for enhanced monitoring pending the outcome.
- Conduct a documented customer outreach (reach-back) to obtain the business purpose of the five wires and supporting documentation — invoices, contracts, or purchase orders for each beneficiary — and confirm the customer, not a third party, initiated them.
- Pull and review the full 90-day inbound history on ****6209: a funnel-account read strengthens materially if the $214,000.00 was funded by recent unusual inbound credits rather than from accumulated operating balances.
- Re-screen all four beneficiaries and their banks against current sanctions and adverse-media sources, and check whether any beneficiary is linked to other alerts or customers at the institution.
- If the customer cannot produce documentation that fits the activity, or gives an inconsistent or evasive account, the reviewer should move the matter toward a suspicious-activity-report referral.
- Flag for KYC: if a genuine cross-border import line is confirmed, the expected-activity profile and risk rating on ****6209 require updating regardless of the alert outcome.

## Disposition Memo (audit-ready)

On 2026-05-19, rule TM-ROUND-WIRE-7741 fired on business account ****6209 (Cedar Hollow Landscaping LLC) after five outbound international wires totaling $214,000.00 were sent over nine days, each in a whole-thousand amount, to four first-time foreign beneficiaries. The customer is a domestic landscaping business with a ~5-year tenure, a LOW KYC rating, no prior alerts, and a stated profile of domestic-only activity at $30,000–$60,000 outbound per month; the flagged activity deviates from that baseline on geography, counterparty, value shape, and velocity simultaneously, running 3.6x–7.1x the stated monthly band in under a third of a month with no prior international history. The payment purposes recorded in the wire memos ("consulting," "services," "equipment," one blank) and the beneficiary names do not correspond to a landscaping business's expected suppliers, and the pattern is consistent with pass-through / funnel-account behavior, with a partial unconfirmed trade-based-laundering overlay. No sanctions hit was identified on any counterparty or jurisdiction. A benign explanation — a legitimate new import or cross-border expansion line — is plausible but is not supported by any invoice, contract, or KYC update on file, so the activity cannot be closed as explained; equally, the absence of a confirmed illicit nexus does not support a direct suspicious-activity-report referral. The activity was therefore escalated for an investigative review to obtain the supporting documentation and the customer's account of the payments, which will determine whether the matter closes or proceeds to a referral.

## Information Gaps

- **Business purpose and supporting documents** for the five wires — no invoices, contracts, or purchase orders are on file. This is the central gap; it is the difference between a benign new trade line and a funnel-account read.
- **Inbound funding source** — the 90-day inbound history on ****6209 was not in the material reviewed for this triage, so it is not established whether the $214,000.00 came from normal operating receipts or from recent unusual credits.
- **Customer's account of the activity** — no customer outreach has yet been conducted; the account-compromise alternative cannot be excluded without it.
- **Beneficiary backgrounds** — the four foreign beneficiaries were name-screened clean at the time of the wires but have not been subject to adverse-media or enhanced research.

These gaps lower confidence in any benign reading and are the reason the disposition is ESCALATE rather than CLOSE. They do not lower confidence that the activity is anomalous — that is established from the transaction record itself.
