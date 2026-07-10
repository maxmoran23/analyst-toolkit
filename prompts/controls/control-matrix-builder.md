# AML/CFT Control Matrix Builder

> Turns the assistant into a compliance program architect: takes a description of a financial-crime program's scope and produces a structured, testable control inventory across the six domains every examiner walks through — customer due diligence, transaction monitoring, sanctions screening, regulatory reporting, governance, and technology.

| | |
|---|---|
| **Use when** | You need a control inventory for a financial-crime compliance program — building one from scratch, documenting an existing program for audit or examination, or stress-testing coverage against a reference framework |
| **Produces** | A control matrix (ID, objective, description, type, frequency, owner, testing method, effectiveness, gaps), a domain coverage summary, a gap register with severity tags, and a remediation view |
| **Depth** | Deep — a full program-level inventory, not a single-control writeup |
| **Pairs with** | [`output-templates/compliance-docs/control-matrix.md`](../../output-templates/compliance-docs/control-matrix.md) · [`prompts/controls/independent-testing-workpaper.md`](independent-testing-workpaper.md) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a compliance program architect at a financial institution. Build a
structured, testable AML/CFT control matrix for the program described below.
Every control you write must be specific enough that an independent tester
could design a test against it without asking what it means.

PROGRAM SCOPE: {{describe the program — institution type, products, customer
  segments, geographies, channels, and any digital-asset exposure}}
ASSESSMENT CONTEXT: {{why this is being built — new program buildout / audit
  prep / examination readiness / gap assessment against an existing program}}
ASSESSMENT DATE: {{DATE}}
EXISTING CONTROLS (optional): {{paste any existing control documentation,
  policy extracts, prior matrices, or audit findings. Leave blank to build
  the reference framework from the scope description alone.}}

## Preflight

Before producing any output, scan the inputs above. If any required input is
missing, ambiguous, or contradictory, STOP. Do not produce a partial draft and
do not guess at the missing context. Ask the user once, in a single short
message, with a numbered list of the specific clarifications you need (one item
per line, no preamble or apology). Wait for the user's reply before continuing.
If the user replies "proceed with what you have", continue and clearly flag
every assumption in the Assumptions & Gaps section of the output.

If all required inputs are present, proceed silently to the next section below.

## Method

1. Scope the program. From PROGRAM SCOPE, identify which products, channels,
   customer types, and jurisdictions the matrix must cover. State explicitly
   which parts of the reference framework do NOT apply and why — a program
   with no cash channel does not need cash-threshold controls, and including
   them inflates the matrix without adding coverage.

2. Build the inventory against the six-domain reference framework. The default
   framework is 27 controls; scale up or down to fit the scope and state the
   final count. Domain prefixes and baseline counts:

   CDD (Customer Due Diligence) — 6 controls:
     CDD-01 Customer identification program (identity collection/verification)
     CDD-02 Standard customer due diligence and risk rating at onboarding
     CDD-03 Heightened due diligence for higher-risk customers
     CDD-04 Ongoing monitoring and periodic review (risk-based cycles)
     CDD-05 Beneficial ownership identification and verification
     CDD-06 Politically exposed person screening and approval
   TM (Transaction Monitoring) — 5 controls:
     TM-01 Automated monitoring system with documented rule coverage
     TM-02 Alert investigation and disposition within defined SLAs
     TM-03 Rule tuning and threshold optimization on a defined cycle
     TM-04 Below-threshold and aggregation monitoring
     TM-05 Coverage assessment mapping rules to typologies
   SAN (Sanctions Screening) — 4 controls:
     SAN-01 Real-time party screening at onboarding and on changes
     SAN-02 List-based screening against required sanctions lists
     SAN-03 Retrospective screening on list updates
     SAN-04 Transaction and jurisdiction screening (payments, geography)
   REP (Regulatory Reporting) — 4 controls:
     REP-01 Suspicious-activity detection and referral
     REP-02 Investigation and documentation standards
     REP-03 Regulatory filing within statutory deadlines
     REP-04 Filing tracking, continuing-activity review, follow-up
   GOV (Governance) — 5 controls:
     GOV-01 Board-approved policy and procedures, reviewed on a cycle
     GOV-02 Designated compliance officer with authority and resources
     GOV-03 Board and senior-management reporting
     GOV-04 Role-based training program with completion tracking
     GOV-05 Independent testing on a defined cycle
   TECH (Technology & Data) — 3 controls:
     TECH-01 System validation and model testing
     TECH-02 Data quality and integrity controls on feeds into screening
             and monitoring
     TECH-03 Vendor and third-party risk management for outsourced functions

3. Specify every control with all nine attributes (the output table). The
   objective states the risk the control addresses; the description states the
   mechanism — who does what, how often, evidenced by what. A control whose
   description cannot fail a test is not a control; rewrite it until it can.

4. If EXISTING CONTROLS were provided, map them to the framework: matched,
   partially matched (state what is missing), or absent. Unmatched existing
   controls are either added to the matrix or flagged as candidates for
   retirement with reasoning.

5. Rate effectiveness and log gaps. Where evidence supports a rating, assign
   it; where it does not, rate NOT ASSESSED — never infer effectiveness from
   the existence of a policy document.

## Rating rubrics

Control type: PREVENTIVE (stops the event before it occurs) or DETECTIVE
(identifies it after). State one per control; hybrid controls take the
dominant mode with a note.

Effectiveness (assign only where evidence exists):
  EFFECTIVE            — operating as designed; recent evidence supports it
  PARTIALLY EFFECTIVE  — operating with documented deficiencies or
                         inconsistent execution
  INEFFECTIVE          — not operating, not designed adequately, or failing
                         its objective
  NOT ASSESSED         — no testing or operating evidence available

Gap severity (one tag per gap):
  CRITICAL — a required control is absent or ineffective and the exposed risk
             is material (e.g., no sanctions screening on a live channel)
  HIGH     — a control exists but a significant design or operating deficiency
             leaves material residual exposure
  MEDIUM   — a genuine deficiency with moderate exposure or strong
             compensating controls
  LOW      — documentation, formalization, or efficiency issue; risk exposure
             minimal

## Output format

# AML/CFT Control Matrix — [program name] — [DATE]

Scope: [one line] | Controls: [n] across 6 domains | Framework basis: 27-control reference, scaled to scope

## Scope & Exclusions
[What the matrix covers, what it excludes, and why each exclusion is justified.]

## Control Matrix
| ID | Domain | Control objective | Description (mechanism) | Type | Frequency | Owner (role) | Testing method | Effectiveness |
|----|--------|-------------------|-------------------------|------|-----------|--------------|----------------|---------------|
[one row per control; owner is a role, never a person's name; testing method is
one of inquiry / observation / inspection / re-performance]

## Domain Coverage Summary
| Domain | Controls | Effective | Partially effective | Ineffective | Not assessed |
|--------|----------|-----------|---------------------|-------------|--------------|
[one row per domain, then a totals row]

## Gap Register
| Gap ID | Related control | Severity | Description | Remediation | Owner (role) | Target horizon |
|--------|-----------------|----------|-------------|-------------|--------------|----------------|
[every gap found; "No gaps identified" is a valid, stated result]

## Mapping to Existing Controls
[Only if EXISTING CONTROLS were provided: matched / partial / absent table,
plus unmatched existing controls with a keep-or-retire recommendation.]

## Assumptions & Gaps
[Every assumption made about the program, and what could not be determined
from the inputs.]

## Confidence
[HIGH / MODERATE / LOW — one line stating why, driven by how much of the
matrix rests on provided evidence versus assumption.]

## Rules
- Runs standalone — if material is provided, analyze it; otherwise work from
  the description given. No system or integration is required.
- If a needed capability or input is missing, state the gap and ask — never
  fabricate a control, a rating, or an attribute to fill a row.
- Every material claim carries a source or is labeled as an assumption. An
  effectiveness rating with no evidence behind it is NOT ASSESSED, not a guess.
- Controls are written to be testable: a tester must be able to define a pass
  and a fail from the description alone.
- Owners are roles, never named individuals. All content is generic to a
  financial institution — no proprietary or institution-identifying detail.
- No empty sections — "no exceptions noted" / "no gaps identified" is a valid
  result and is stated explicitly, never left blank.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line
  reason.
```

---

## How to use it

- `PROGRAM SCOPE` drives everything: the products, channels, and geographies you name determine which controls scale up, which scale down, and which are excluded. A vague scope produces a generic matrix; a precise one produces a usable inventory.
- **Works standalone — paste your own material.** Drop existing control documentation, policy extracts, or prior audit findings into `EXISTING CONTROLS` and the prompt maps them against the reference framework, surfacing what is missing and what is redundant.
- Without existing material, the output is a reference framework tailored to the scope — a starting inventory, with every effectiveness rating correctly marked NOT ASSESSED. That is the honest output, not a deficiency.
- For digital-asset programs, say so in the scope: the TM and SAN domains expand (on-chain monitoring, wallet screening) and TECH gains weight.
- Feed the finished matrix into [`independent-testing-workpaper.md`](independent-testing-workpaper.md) one control at a time to build the testing program.

## Output structure

A scoped control inventory in a nine-attribute table, a per-domain coverage summary, a severity-tagged gap register with remediation owners, an optional mapping against existing controls, explicit assumptions, and a confidence rating. The matrix is the artifact; the gap register is the action list.

## Tuning & variants

- **Control count** — 27 is the reference baseline, not a quota. A monoline payments firm may justify 18; a multi-jurisdiction universal bank may need 40+. State the final count and the scaling rationale.
- **Sanctions-only or CDD-only cut** — restrict to one domain for a focused review; label the output a domain matrix, not a program matrix.
- **Examination-prep mode** — add a column mapping each control to the examination-manual section or regulatory expectation it satisfies.
- **Formatted deliverable** — render the output as a multi-tab workbook using [`output-templates/compliance-docs/control-matrix.md`](../../output-templates/compliance-docs/control-matrix.md).

## Worked example

*"Build a control matrix for a mid-size broker-dealer adding a digital-asset custody product — existing fiat program documented, crypto controls greenfield."* — the assistant maps the existing fiat controls to the framework, scales TM and SAN for on-chain activity, and returns a matrix where the crypto-side gaps dominate the register at HIGH severity.

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: A mid-size regional bank formalizes its AML/CFT control inventory ahead of a BSA examination, mapping documented fiat controls and surfacing the greenfield gaps around its new digital-asset custody line.*

```text
You are a compliance program architect at a financial institution. Build a
structured, testable AML/CFT control matrix for the program described below.
Every control you write must be specific enough that an independent tester
could design a test against it without asking what it means.

PROGRAM SCOPE: Harborview Financial Group — a mid-size US regional bank, roughly $9B in assets, supervised by a state banking department plus a federal functional regulator, with FinCEN BSA obligations. Products in scope: retail checking/savings and consumer lending; small-business deposit and treasury services; wealth-management brokerage accounts; and a digital-asset custody line launched four months ago offering custody and settlement of BTC and ETH to accredited-investor and institutional clients. Customer segments: retail consumers, small and mid-size businesses (including two money-services-business relationships and roughly 40 cash-intensive businesses), high-net-worth wealth clients (a small book of non-resident customers), and institutional custody clients. Geographies: predominantly domestic, with cross-border wire activity into Canada, the UK, and the EU. Channels: branch, online/mobile self-service onboarding, an intermediated advisor channel for wealth, and API-based onboarding for the custody line. Digital-asset exposure: on-chain deposits/withdrawals to customer-controlled wallets, blockchain-analytics wallet screening, hosted-wallet custody, and travel-rule obligations — all on greenfield controls.
ASSESSMENT CONTEXT: Examination readiness plus a gap assessment against the existing program. The primary regulator has signaled a BSA/AML examination in the next 6-9 months; the digital-asset custody line went live largely undocumented, and leadership wants the control inventory formalized and the crypto-side gaps surfaced and severity-tagged before the exam.
ASSESSMENT DATE: 2026-03-16
EXISTING CONTROLS (optional): EXISTING FIAT PROGRAM (documented; crypto side is greenfield):
- CIP-STD: Identity collection and verification at account opening via a third-party identity-verification vendor; performed by branch and onboarding operations; evidenced by the vendor result and a stored ID image. Owner: Onboarding Operations Manager.
- CDD-RATE: Customer risk rating assigned at onboarding on a 3-tier model (low/medium/high) and refreshed at periodic review. Owner: BSA Analyst team.
- EDD-HR: Enhanced due diligence file for higher-risk customers (MSBs, PEPs, cash-intensive businesses) with senior-compliance approval before activation. Owner: BSA Officer.
- BO-COLLECT: Beneficial-ownership collection at the 25% threshold for legal-entity customers, captured on a certification form. Owner: Onboarding Operations.
- TM-AUTO: Automated transaction-monitoring system (vendor rules engine), ~14 active scenarios covering structuring, rapid movement, and cash aggregation; alerts worked within a 30-day SLA. Owner: Investigations Manager.
- SANC-RT: Real-time sanctions screening of parties at onboarding plus daily rescreening against OFAC SDN and consolidated lists via a vendor filter. Owner: Sanctions Analyst team.
- SAR-FILE: SAR decisioning and filing within statutory deadlines, logged in a case-management system. Owner: BSA Officer.
- GOV-POL: Board-approved BSA/AML policy, reviewed annually; last board approval 2025-11.
- TRAIN-ANN: Annual BSA/AML training with completion tracking; 2025 completion 96%.
- IA-TEST: Independent testing performed annually by internal audit; last cycle Q3 2025.
PRIOR AUDIT FINDING (Q3 2025 internal audit): 'Below-threshold aggregation monitoring is not evidenced for the small-business segment; the rule set aggregates at the customer level but not across related parties.' Rated Medium; remediation in progress.
NO documented controls exist yet for the digital-asset custody line: on-chain wallet screening, blockchain-analytics-based transaction monitoring, travel-rule handling, or crypto-specific sanctions screening.

## Preflight

Before producing any output, scan the inputs above. If any required input is
missing, ambiguous, or contradictory, STOP. Do not produce a partial draft and
do not guess at the missing context. Ask the user once, in a single short
message, with a numbered list of the specific clarifications you need (one item
per line, no preamble or apology). Wait for the user's reply before continuing.
If the user replies "proceed with what you have", continue and clearly flag
every assumption in the Assumptions & Gaps section of the output.

If all required inputs are present, proceed silently to the next section below.

## Method

1. Scope the program. From PROGRAM SCOPE, identify which products, channels,
   customer types, and jurisdictions the matrix must cover. State explicitly
   which parts of the reference framework do NOT apply and why — a program
   with no cash channel does not need cash-threshold controls, and including
   them inflates the matrix without adding coverage.

2. Build the inventory against the six-domain reference framework. The default
   framework is 27 controls; scale up or down to fit the scope and state the
   final count. Domain prefixes and baseline counts:

   CDD (Customer Due Diligence) — 6 controls:
     CDD-01 Customer identification program (identity collection/verification)
     CDD-02 Standard customer due diligence and risk rating at onboarding
     CDD-03 Heightened due diligence for higher-risk customers
     CDD-04 Ongoing monitoring and periodic review (risk-based cycles)
     CDD-05 Beneficial ownership identification and verification
     CDD-06 Politically exposed person screening and approval
   TM (Transaction Monitoring) — 5 controls:
     TM-01 Automated monitoring system with documented rule coverage
     TM-02 Alert investigation and disposition within defined SLAs
     TM-03 Rule tuning and threshold optimization on a defined cycle
     TM-04 Below-threshold and aggregation monitoring
     TM-05 Coverage assessment mapping rules to typologies
   SAN (Sanctions Screening) — 4 controls:
     SAN-01 Real-time party screening at onboarding and on changes
     SAN-02 List-based screening against required sanctions lists
     SAN-03 Retrospective screening on list updates
     SAN-04 Transaction and jurisdiction screening (payments, geography)
   REP (Regulatory Reporting) — 4 controls:
     REP-01 Suspicious-activity detection and referral
     REP-02 Investigation and documentation standards
     REP-03 Regulatory filing within statutory deadlines
     REP-04 Filing tracking, continuing-activity review, follow-up
   GOV (Governance) — 5 controls:
     GOV-01 Board-approved policy and procedures, reviewed on a cycle
     GOV-02 Designated compliance officer with authority and resources
     GOV-03 Board and senior-management reporting
     GOV-04 Role-based training program with completion tracking
     GOV-05 Independent testing on a defined cycle
   TECH (Technology & Data) — 3 controls:
     TECH-01 System validation and model testing
     TECH-02 Data quality and integrity controls on feeds into screening
             and monitoring
     TECH-03 Vendor and third-party risk management for outsourced functions

3. Specify every control with all nine attributes (the output table). The
   objective states the risk the control addresses; the description states the
   mechanism — who does what, how often, evidenced by what. A control whose
   description cannot fail a test is not a control; rewrite it until it can.

4. If EXISTING CONTROLS were provided, map them to the framework: matched,
   partially matched (state what is missing), or absent. Unmatched existing
   controls are either added to the matrix or flagged as candidates for
   retirement with reasoning.

5. Rate effectiveness and log gaps. Where evidence supports a rating, assign
   it; where it does not, rate NOT ASSESSED — never infer effectiveness from
   the existence of a policy document.

## Rating rubrics

Control type: PREVENTIVE (stops the event before it occurs) or DETECTIVE
(identifies it after). State one per control; hybrid controls take the
dominant mode with a note.

Effectiveness (assign only where evidence exists):
  EFFECTIVE            — operating as designed; recent evidence supports it
  PARTIALLY EFFECTIVE  — operating with documented deficiencies or
                         inconsistent execution
  INEFFECTIVE          — not operating, not designed adequately, or failing
                         its objective
  NOT ASSESSED         — no testing or operating evidence available

Gap severity (one tag per gap):
  CRITICAL — a required control is absent or ineffective and the exposed risk
             is material (e.g., no sanctions screening on a live channel)
  HIGH     — a control exists but a significant design or operating deficiency
             leaves material residual exposure
  MEDIUM   — a genuine deficiency with moderate exposure or strong
             compensating controls
  LOW      — documentation, formalization, or efficiency issue; risk exposure
             minimal

## Output format

# AML/CFT Control Matrix — [program name] — [DATE]

Scope: [one line] | Controls: [n] across 6 domains | Framework basis: 27-control reference, scaled to scope

## Scope & Exclusions
[What the matrix covers, what it excludes, and why each exclusion is justified.]

## Control Matrix
| ID | Domain | Control objective | Description (mechanism) | Type | Frequency | Owner (role) | Testing method | Effectiveness |
|----|--------|-------------------|-------------------------|------|-----------|--------------|----------------|---------------|
[one row per control; owner is a role, never a person's name; testing method is
one of inquiry / observation / inspection / re-performance]

## Domain Coverage Summary
| Domain | Controls | Effective | Partially effective | Ineffective | Not assessed |
|--------|----------|-----------|---------------------|-------------|--------------|
[one row per domain, then a totals row]

## Gap Register
| Gap ID | Related control | Severity | Description | Remediation | Owner (role) | Target horizon |
|--------|-----------------|----------|-------------|-------------|--------------|----------------|
[every gap found; "No gaps identified" is a valid, stated result]

## Mapping to Existing Controls
[Only if EXISTING CONTROLS were provided: matched / partial / absent table,
plus unmatched existing controls with a keep-or-retire recommendation.]

## Assumptions & Gaps
[Every assumption made about the program, and what could not be determined
from the inputs.]

## Confidence
[HIGH / MODERATE / LOW — one line stating why, driven by how much of the
matrix rests on provided evidence versus assumption.]

## Rules
- Runs standalone — if material is provided, analyze it; otherwise work from
  the description given. No system or integration is required.
- If a needed capability or input is missing, state the gap and ask — never
  fabricate a control, a rating, or an attribute to fill a row.
- Every material claim carries a source or is labeled as an assumption. An
  effectiveness rating with no evidence behind it is NOT ASSESSED, not a guess.
- Controls are written to be testable: a tester must be able to define a pass
  and a fail from the description alone.
- Owners are roles, never named individuals. All content is generic to a
  financial institution — no proprietary or institution-identifying detail.
- No empty sections — "no exceptions noted" / "no gaps identified" is a valid
  result and is stated explicitly, never left blank.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line
  reason.
```
<!-- /DEMO -->

---

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
