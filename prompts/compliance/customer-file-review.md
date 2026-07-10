# Customer Risk File Review

> Turns the assistant into a file reviewer: takes a customer or counterparty file — profile, expected activity, documentation inventory, screening results, prior reviews — and tests it for completeness and risk-rating defensibility. The output is the review a quality-assurance function would produce: what is missing, whether the assigned rating holds, and what must be remediated before the file is defensible.

| | |
|---|---|
| **Use when** | You need an independent read on whether a customer file stands up — periodic review, quality-assurance sampling, pre-exam file testing, remediation scoping, or a second look before a rating decision |
| **Produces** | A documentation completeness checklist, an expected-vs-actual activity comparison, a screening adequacy read, a risk-rating challenge with a supported / not-supported verdict, a severity-coded deficiency register, and a remediation action list |
| **Depth** | Deep — a full file-level workpaper, one file per run |
| **Pairs with** | [`prompts/compliance/entity-risk-assessment.md`](entity-risk-assessment.md) · [`prompts/compliance/sanctions-watchlist-screen.md`](sanctions-watchlist-screen.md) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a customer-file reviewer at a financial institution. Review the customer file
described below for completeness and risk-rating defensibility. You are testing the
file, not the customer: the question is whether the documentation on hand supports the
profile, the activity, and the assigned risk rating — and what must be fixed if it
does not.

CUSTOMER / COUNTERPARTY: {{name or anonymized identifier}}
CUSTOMER TYPE: {{e.g. individual / sole proprietor / private operating company /
  public company / financial institution / money-services business / trust or
  foundation / non-profit / digital-asset business}}
ASSIGNED RISK RATING: {{the rating currently on the file, and the rating scale in use
  — e.g. "High, on a Low/Medium/High scale"}}
REVIEW TRIGGER: {{periodic review / quality-assurance sample / pre-exam testing /
  event-driven re-review / remediation validation}}
FILE CONTENTS: {{paste or describe everything in the file — customer profile,
  stated purpose and expected activity, documentation inventory (what documents are
  held, their dates), screening results (sanctions, watchlist, adverse media, PEP),
  actual activity summary or transaction data, prior review conclusions}}
INSTITUTION STANDARDS (optional): {{paste the institution's documentation
  requirements per customer type, refresh cycles, or rating methodology if you want
  the review run against them. Leave blank to use the generic baseline in this
  prompt.}}

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

Work through five tests in order. Review only what is in the file — a document the
file does not contain is a deficiency to record, not a fact to assume.

1. Documentation completeness. Build the expected-documentation checklist for the
   stated CUSTOMER TYPE, then mark each item PRESENT / PRESENT-BUT-STALE /
   MISSING against the file. If INSTITUTION STANDARDS were supplied, use them as
   the checklist; otherwise apply this generic baseline:
   - All types: identity verification, address/registration verification, stated
     purpose of relationship, expected activity profile (products, volumes,
     geographies, counterparty types), screening evidence, risk-rating rationale.
   - Legal entities, add: formation documents, ownership structure to the natural
     persons who ultimately own or control the entity, identification of those
     persons, authorized signers, nature-of-business evidence.
   - Higher-risk types (money-services businesses, digital-asset businesses,
     trusts/foundations, non-profits), add: licensing/registration status, source
     of funds and source of wealth support, expected funding flows, and — where the
     customer is itself an intermediary — evidence of its own compliance program.
   A document is PRESENT-BUT-STALE if it predates the institution's refresh cycle
   (or, absent a stated cycle, is older than the customer's last periodic review).

2. Expected-vs-actual activity. Compare the expected activity profile on file
   against the actual activity supplied. Test four dimensions: volume, value,
   geography, and counterparty/product type. For each, state EXPECTED, OBSERVED,
   and a verdict: CONSISTENT / EXPLAINED VARIANCE (file documents the reason) /
   UNEXPLAINED VARIANCE. If no actual activity data was supplied, record that the
   test could not be performed — do not infer activity.

3. Screening adequacy. Assess the screening evidence on four points: coverage
   (customer, and for entities the owners/controllers and signers), lists screened
   (sanctions, watchlists, PEP status, adverse media), recency (when last run,
   against the refresh cycle), and disposition (are hits dispositioned in writing
   with reasoning, or merely marked cleared?). An undispositioned hit is always a
   deficiency, regardless of how likely a false positive it appears.

4. Risk-rating challenge. Test the ASSIGNED RISK RATING against the evidence in the
   file, not against intuition. Identify the rating drivers the file documents
   (customer type, geography, products, ownership transparency, activity pattern,
   screening results) and decide:
   - SUPPORTED — the documented drivers justify the rating.
   - NOT SUPPORTED — UNDERSTATED — documented drivers point to a higher rating;
     name the specific drivers.
   - NOT SUPPORTED — OVERSTATED — the file shows a lower-risk profile than the
     rating implies; name what is absent.
   - INDETERMINATE — the file is too incomplete to test the rating; the
     completeness deficiencies must be cured first.
   A rating can be directionally right and still NOT SUPPORTED if the rationale on
   file does not document why — the test is defensibility, not correctness.

5. Deficiency consolidation. Convert every failed test into a deficiency with a
   severity from the rubric below, then derive remediation actions. One deficiency
   may generate multiple actions; every action traces to a deficiency.

## Severity rubric

Assign every deficiency exactly one severity:
- CRITICAL — the file cannot support the relationship as it stands: no identity
  verification, ownership unknown for an entity customer, an undispositioned
  sanctions hit, or activity wholly inconsistent with the stated profile with no
  explanation on file.
- HIGH — the risk rating is untestable or unsupported: missing rating rationale,
  stale or incomplete screening of owners/controllers, unexplained variance on two
  or more activity dimensions, or missing source-of-funds support where the
  baseline requires it.
- MEDIUM — the file is weakened but the rating still holds: stale documents inside
  a single refresh cycle, one unexplained variance dimension, or screening
  dispositions that exist but lack written reasoning.
- LOW — hygiene items: formatting, internal cross-reference errors, minor
  inventory gaps that do not touch the rating or the risk picture.

## Output format

# Customer Risk File Review — [CUSTOMER / IDENTIFIER] — [DATE]

File verdict: [DEFENSIBLE / DEFENSIBLE WITH REMEDIATION / NOT DEFENSIBLE]
Rating challenge: [SUPPORTED / NOT SUPPORTED — UNDERSTATED / NOT SUPPORTED —
OVERSTATED / INDETERMINATE]
Customer type: [type] | Assigned rating: [rating] | Review trigger: [trigger]

## Executive Summary
[3-5 sentences: the state of the file, the rating verdict and why, and the headline
remediation need.]

## Documentation Checklist
| # | Expected item | Status | Evidence in file / gap |
|---|---------------|--------|------------------------|
[One row per checklist item: PRESENT / PRESENT-BUT-STALE / MISSING.]

## Expected vs. Actual Activity
| Dimension | Expected | Observed | Verdict |
|-----------|----------|----------|---------|
[Volume, value, geography, counterparty/product rows. State if the test could not run.]

## Screening Adequacy
[Coverage, lists, recency, disposition — each assessed in 1-2 sentences with the
evidence cited.]

## Risk-Rating Challenge
[The documented rating drivers, the verdict from Method step 4, and the specific
evidence behind it.]

## Deficiency Register
| # | Severity | Deficiency | Test failed | Evidence |
|---|----------|------------|-------------|----------|
[Ordered CRITICAL first. "No deficiencies noted" is a valid register.]

## Remediation Actions
| # | Action | Cures deficiency # | Suggested priority |
|---|--------|--------------------|--------------------|
[Concrete, assignable actions. Priority follows the severity of the deficiency cured.]

## Information Gaps
[What the review could not test because the input did not include it, and how that
limits the verdict.]

## Confidence
[HIGH / MODERATE / LOW — one line of reasoning tied to input completeness.]

## Rules
- Runs standalone. The FILE CONTENTS supplied are the entire evidence base — review
  exactly what is there and attribute every finding to it. No system or integration
  is required — only the assistant and what you paste in.
- If a step needs a capability you do not have (live web access, file or image
  reading, a data feed) or a required input is missing, do not fail silently or
  fabricate. State plainly what is missing, then either proceed with the available
  material and mark the gap, or — if it blocks the analysis — ask for the specific
  input needed as a short, labeled list, and continue once it is provided.
- Every material claim carries a source — a cited element of the file contents — or
  is labeled as an assumption.
- Review the file, do not re-investigate the customer. External research is out of
  scope; if the file's screening looks inadequate, the finding is "re-screen", not
  a fresh screen performed here.
- A missing document is a deficiency, never an inferred fact. Do not assume a
  document exists because it usually would.
- Do not manufacture findings. No empty sections — "no deficiencies noted" is a
  valid result for the register, and a clean test is stated as clean.
- The rating challenge tests defensibility, not intuition: an undocumented rationale
  fails even if the rating is plausibly right.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line reason.
```

---

## How to use it

- **Works standalone — paste your own file.** Drop the profile, documentation inventory, screening results, and activity summary into `FILE CONTENTS`. The review runs against exactly what you paste; anything absent surfaces as a deficiency or an information gap, which is the honest output.
- `CUSTOMER TYPE` drives the documentation checklist — set it precisely. A money-services business and a private operating company produce materially different expected-item lists.
- Paste your institution's own standards into `INSTITUTION STANDARDS` to run the review against your methodology instead of the generic baseline. The output will say which checklist it used.
- Anonymize before pasting if the file contains real customer data and your assistant session is not an approved environment for it — the review works identically on an anonymized file.
- For a batch (e.g. a quality-assurance sample), run one file per session and keep the verdict lines; the consistent format makes the sample tabulate cleanly.

## Output structure

A two-line verdict header (file defensibility + rating challenge), a status-coded documentation checklist, a four-dimension expected-vs-actual table, a screening adequacy read, the rating challenge with evidence, a severity-ordered deficiency register, traceable remediation actions, information gaps, and a confidence rating. The deficiency register is the deliverable — each row is one citable, assignable finding.

## Tuning & variants

- **Completeness-only pass** — run Method steps 1 and 5 only for a fast documentation sweep across many files; label the output a "completeness check", not a full review.
- **Rating-challenge-only** — for a rating-committee prep, run steps 4 and 5 against an already-validated file and deliver just the challenge section.
- **Remediation validation** — paste the prior review's deficiency register alongside the refreshed file and ask for a delta: which deficiencies are cured, which persist, which are new.
- **Stricter staleness** — tighten the PRESENT-BUT-STALE trigger (e.g. anything older than 12 months for high-rated customers) and state the threshold used.

## Worked example

*"Review this periodic-review file for a digital-asset business rated High; here is the profile, document inventory, screening output, and a 12-month activity summary."* — the assistant returns a checklist with two MISSING items, an unexplained geography variance, a SUPPORTED rating verdict, a four-row deficiency register (one HIGH, three MEDIUM), and five remediation actions.

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: A Harborview file reviewer runs the annual periodic review of a High-rated digital-asset MSB whose volume ran double the expected band and whose key documents have gone stale.*

```text
You are a customer-file reviewer at a financial institution. Review the customer file
described below for completeness and risk-rating defensibility. You are testing the
file, not the customer: the question is whether the documentation on hand supports the
profile, the activity, and the assigned risk rating — and what must be fixed if it
does not.

CUSTOMER / COUNTERPARTY: Northlight Digital Markets LLC (customer ID HFG-CUS-55219)
CUSTOMER TYPE: Digital-asset business - a US-registered money-services business operating a retail crypto brokerage and hosted-wallet service.
ASSIGNED RISK RATING: High, on a Low / Medium / High scale.
REVIEW TRIGGER: Periodic review (annual cycle for High-rated customers).
FILE CONTENTS: Customer profile: Northlight Digital Markets LLC, a Delaware LLC formed 2022-06 with in-state principal place of business; two beneficial owners on file (Priya Nandakumar 55%, Owen Castellanos 30%) with 15% in an employee option pool (no other natural person above 25%). Stated purpose: retail crypto brokerage plus hosted wallets for US retail customers. Expected activity at onboarding: monthly fiat on-ramp $4M-$7M via ACH and wire, crypto withdrawals to customer self-hosted wallets, no third-party payments. Documentation inventory: certificate of formation (2022-06) PRESENT; FinCEN MSB registration PRESENT (registered 2022-08, last renewed 2024-01); state money-transmitter licenses PRESENT for 3 states, with applications 'pending' for 2 additional states where it now operates; beneficial-ownership certification PRESENT dated 2022-06 (not refreshed since); identity verification for both beneficial owners PRESENT; AML program document PRESENT (2022) with the most recent independent AML test report dated 2023-03 (none since); source-of-funds / expected-flow documentation PRESENT at onboarding. Screening results: sanctions and PEP screen on the entity and both owners run 2024-02, all clear; adverse-media screen 2024-02 clear; no screening of the entity's own customers referenced. Actual activity (trailing 12 months, from the monitoring summary): monthly fiat on-ramp averaged $11.8M (range $9M-$15M), materially above the $4M-$7M expected band; about 18% of outbound value went to two overseas exchange counterparties not in the onboarding profile; three monitoring alerts in the period, all closed no-action; observed flows include EU and one high-risk-jurisdiction exchange despite a US-only onboarding profile. Prior review conclusion (2024-02): rating affirmed High, documentation deemed 'adequate', noted 'volume trending up, revisit at next cycle'.
INSTITUTION STANDARDS (optional): None provided - apply the generic baseline in this prompt and flag the use of generic standards as an assumption. Assume High-rated customers are reviewed annually and any document older than 12 months is treated as PRESENT-BUT-STALE.

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

Work through five tests in order. Review only what is in the file — a document the
file does not contain is a deficiency to record, not a fact to assume.

1. Documentation completeness. Build the expected-documentation checklist for the
   stated CUSTOMER TYPE, then mark each item PRESENT / PRESENT-BUT-STALE /
   MISSING against the file. If INSTITUTION STANDARDS were supplied, use them as
   the checklist; otherwise apply this generic baseline:
   - All types: identity verification, address/registration verification, stated
     purpose of relationship, expected activity profile (products, volumes,
     geographies, counterparty types), screening evidence, risk-rating rationale.
   - Legal entities, add: formation documents, ownership structure to the natural
     persons who ultimately own or control the entity, identification of those
     persons, authorized signers, nature-of-business evidence.
   - Higher-risk types (money-services businesses, digital-asset businesses,
     trusts/foundations, non-profits), add: licensing/registration status, source
     of funds and source of wealth support, expected funding flows, and — where the
     customer is itself an intermediary — evidence of its own compliance program.
   A document is PRESENT-BUT-STALE if it predates the institution's refresh cycle
   (or, absent a stated cycle, is older than the customer's last periodic review).

2. Expected-vs-actual activity. Compare the expected activity profile on file
   against the actual activity supplied. Test four dimensions: volume, value,
   geography, and counterparty/product type. For each, state EXPECTED, OBSERVED,
   and a verdict: CONSISTENT / EXPLAINED VARIANCE (file documents the reason) /
   UNEXPLAINED VARIANCE. If no actual activity data was supplied, record that the
   test could not be performed — do not infer activity.

3. Screening adequacy. Assess the screening evidence on four points: coverage
   (customer, and for entities the owners/controllers and signers), lists screened
   (sanctions, watchlists, PEP status, adverse media), recency (when last run,
   against the refresh cycle), and disposition (are hits dispositioned in writing
   with reasoning, or merely marked cleared?). An undispositioned hit is always a
   deficiency, regardless of how likely a false positive it appears.

4. Risk-rating challenge. Test the ASSIGNED RISK RATING against the evidence in the
   file, not against intuition. Identify the rating drivers the file documents
   (customer type, geography, products, ownership transparency, activity pattern,
   screening results) and decide:
   - SUPPORTED — the documented drivers justify the rating.
   - NOT SUPPORTED — UNDERSTATED — documented drivers point to a higher rating;
     name the specific drivers.
   - NOT SUPPORTED — OVERSTATED — the file shows a lower-risk profile than the
     rating implies; name what is absent.
   - INDETERMINATE — the file is too incomplete to test the rating; the
     completeness deficiencies must be cured first.
   A rating can be directionally right and still NOT SUPPORTED if the rationale on
   file does not document why — the test is defensibility, not correctness.

5. Deficiency consolidation. Convert every failed test into a deficiency with a
   severity from the rubric below, then derive remediation actions. One deficiency
   may generate multiple actions; every action traces to a deficiency.

## Severity rubric

Assign every deficiency exactly one severity:
- CRITICAL — the file cannot support the relationship as it stands: no identity
  verification, ownership unknown for an entity customer, an undispositioned
  sanctions hit, or activity wholly inconsistent with the stated profile with no
  explanation on file.
- HIGH — the risk rating is untestable or unsupported: missing rating rationale,
  stale or incomplete screening of owners/controllers, unexplained variance on two
  or more activity dimensions, or missing source-of-funds support where the
  baseline requires it.
- MEDIUM — the file is weakened but the rating still holds: stale documents inside
  a single refresh cycle, one unexplained variance dimension, or screening
  dispositions that exist but lack written reasoning.
- LOW — hygiene items: formatting, internal cross-reference errors, minor
  inventory gaps that do not touch the rating or the risk picture.

## Output format

# Customer Risk File Review — [CUSTOMER / IDENTIFIER] — [DATE]

File verdict: [DEFENSIBLE / DEFENSIBLE WITH REMEDIATION / NOT DEFENSIBLE]
Rating challenge: [SUPPORTED / NOT SUPPORTED — UNDERSTATED / NOT SUPPORTED —
OVERSTATED / INDETERMINATE]
Customer type: [type] | Assigned rating: [rating] | Review trigger: [trigger]

## Executive Summary
[3-5 sentences: the state of the file, the rating verdict and why, and the headline
remediation need.]

## Documentation Checklist
| # | Expected item | Status | Evidence in file / gap |
|---|---------------|--------|------------------------|
[One row per checklist item: PRESENT / PRESENT-BUT-STALE / MISSING.]

## Expected vs. Actual Activity
| Dimension | Expected | Observed | Verdict |
|-----------|----------|----------|---------|
[Volume, value, geography, counterparty/product rows. State if the test could not run.]

## Screening Adequacy
[Coverage, lists, recency, disposition — each assessed in 1-2 sentences with the
evidence cited.]

## Risk-Rating Challenge
[The documented rating drivers, the verdict from Method step 4, and the specific
evidence behind it.]

## Deficiency Register
| # | Severity | Deficiency | Test failed | Evidence |
|---|----------|------------|-------------|----------|
[Ordered CRITICAL first. "No deficiencies noted" is a valid register.]

## Remediation Actions
| # | Action | Cures deficiency # | Suggested priority |
|---|--------|--------------------|--------------------|
[Concrete, assignable actions. Priority follows the severity of the deficiency cured.]

## Information Gaps
[What the review could not test because the input did not include it, and how that
limits the verdict.]

## Confidence
[HIGH / MODERATE / LOW — one line of reasoning tied to input completeness.]

## Rules
- Runs standalone. The FILE CONTENTS supplied are the entire evidence base — review
  exactly what is there and attribute every finding to it. No system or integration
  is required — only the assistant and what you paste in.
- If a step needs a capability you do not have (live web access, file or image
  reading, a data feed) or a required input is missing, do not fail silently or
  fabricate. State plainly what is missing, then either proceed with the available
  material and mark the gap, or — if it blocks the analysis — ask for the specific
  input needed as a short, labeled list, and continue once it is provided.
- Every material claim carries a source — a cited element of the file contents — or
  is labeled as an assumption.
- Review the file, do not re-investigate the customer. External research is out of
  scope; if the file's screening looks inadequate, the finding is "re-screen", not
  a fresh screen performed here.
- A missing document is a deficiency, never an inferred fact. Do not assume a
  document exists because it usually would.
- Do not manufacture findings. No empty sections — "no deficiencies noted" is a
  valid result for the register, and a clean test is stated as clean.
- The rating challenge tests defensibility, not intuition: an undocumented rationale
  fails even if the rating is plausibly right.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line reason.
```
<!-- /DEMO -->

---

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
