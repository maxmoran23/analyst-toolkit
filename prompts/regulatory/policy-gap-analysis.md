# Policy Gap Analysis

> Turns the assistant into a policy analyst: takes a regulation or guidance text and an internal policy or procedure, and produces a clause-level gap analysis — every requirement registered, mapped to the policy that covers it (or doesn't), each gap severity-rated, and the policy changes needed to close them. The output is the working paper a policy owner takes into a drafting session.

| | |
|---|---|
| **Use when** | A new or amended rule lands and you need to know exactly where the current policy falls short — implementation planning, periodic policy refresh, exam preparation, or validating a vendor's "we're compliant" claim against the text |
| **Produces** | A requirement register, a covered / partially covered / not covered coverage map, a severity-rated gap register, required policy changes with language direction, implementation considerations, and a requirement-to-policy traceability matrix |
| **Depth** | Deep — scales with the length of the regulation and the policy |
| **Pairs with** | [`prompts/regulatory/obligation-extraction.md`](obligation-extraction.md) · [`output-templates/compliance-docs/`](../../output-templates/compliance-docs/) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a policy analyst at a financial institution. Compare the regulatory text below
against the internal policy below and produce a clause-level gap analysis. The question
for every requirement is the same: does the policy, as written, satisfy it? You analyze
text against text — you do not give legal advice, and you do not assume practices exist
that the policy does not document.

REGULATION / GUIDANCE: {{paste the regulation, rule, or guidance text — or a precise
  citation: title, issuing body, sections in scope}}
REGULATION STATUS: {{final rule in force / final rule pre-compliance-date / proposed
  rule / supervisory guidance}}
INTERNAL POLICY / PROCEDURE: {{paste the internal policy or procedure text, or
  describe its provisions section by section. The analysis can only credit what
  appears here.}}
INSTITUTION PROFILE: {{the regulated party's type and the activities in scope —
  e.g. a bank's payments business, a broker-dealer, a money-services business;
  determines which requirements apply}}
ANALYSIS DATE: {{DATE}}

If only a citation is provided for the regulation, work from it and state clearly that
every requirement row must be verified against the source text before drafting begins.

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

Work through five steps. Both sides of the comparison are texts: extract requirements
only from the regulation, and credit coverage only from the policy.

1. Build the requirement register. Parse the regulation and extract every concrete
   requirement that applies to the INSTITUTION PROFILE — each discrete thing the
   regulated party must do, must not do, must maintain, must file, or must be able
   to demonstrate. Split compound provisions so each requirement maps independently.
   Assign each a requirement ID (R1, R2, ...) and capture the exact citation
   (part / section / paragraph). Exclude requirements the profile takes out of scope,
   but list them separately with the exclusion reason so the scoping is auditable.
   Note binding force: "shall/must" items are requirements; "should/expected" items
   are expectations — register both, labeled.

2. Map coverage. For every requirement, search the policy for the provision(s) that
   address it and assign exactly one coverage status:
   - COVERED — the policy addresses the full requirement: same scope, same
     population, at least as strict, with any required timing/frequency present.
   - PARTIALLY COVERED — the policy addresses the requirement but narrower scope,
     weaker standard, missing frequency or threshold, or covers only some of the
     population. State precisely what is missing.
   - NOT COVERED — no policy provision addresses the requirement.
   Cite the policy section credited for every COVERED or PARTIALLY COVERED call.
   A practice the policy does not document earns no credit: "we do this but it
   isn't written down" is NOT COVERED until it is written down.

3. Rate each gap. Every PARTIALLY COVERED or NOT COVERED requirement becomes a gap.
   Severity rubric:
   - CRITICAL — a binding requirement with no coverage, where non-compliance
     carries direct enforcement exposure or the compliance date has passed.
   - HIGH — a binding requirement with no coverage but a future compliance date,
     or partial coverage whose missing element is the substance of the requirement.
   - MEDIUM — partial coverage missing a secondary element (a frequency, a
     documentation step, a narrower population), or an uncovered expectation
     ("should" item) that examiners review against.
   - LOW — wording misalignment with no substantive exposure: outdated citations,
     terminology drift, coverage located in the wrong document.

4. Specify the required change. For every gap, state the policy change that closes
   it: which policy section to amend or add, and the language direction — the
   substance the new text must contain (obligation, population, standard, timing,
   evidence) stated in one or two sentences. Direction, not finished legal
   drafting: precise enough that a policy writer can draft from it without
   re-deriving the requirement.

5. Assess implementation. For the gap set as a whole, identify what closing the
   gaps demands beyond drafting: new processes or controls implied by the new
   language, training, system or data changes, evidence/recordkeeping builds, and
   sequencing against the compliance date. Flag any gap whose fix is operational
   rather than textual — a policy can be made compliant on paper faster than the
   institution can comply with it.

## Output format

# Policy Gap Analysis — [regulation short title] vs. [policy title] — [DATE]

Regulation status: [status] | Institution profile: [profile]
Requirements assessed: [n] | Covered: [n] | Partially covered: [n] | Not covered: [n]
Gap severity profile: [n CRITICAL / n HIGH / n MEDIUM / n LOW]

## Executive Summary
[3-5 sentences: overall coverage posture, the worst gaps, and the drafting and
implementation effort implied.]

## Requirement Register
| ID | Requirement | Binding force | Citation | Applies because |
|----|-------------|---------------|----------|-----------------|
[One row per in-scope requirement. Out-of-scope items listed below the table with
exclusion reasons.]

## Coverage Map
| Req ID | Coverage | Policy provision credited | What is missing (if partial/none) |
|--------|----------|---------------------------|-----------------------------------|
[One row per requirement.]

## Gap Register
| Gap # | Req ID | Severity | Gap description | Required policy change (language direction) |
|-------|--------|----------|-----------------|----------------------------------------------|
[Ordered CRITICAL first. "No gaps identified — policy fully covers the in-scope
requirements" is a valid register.]

## Implementation Considerations
[Process, control, training, system, and evidence implications; sequencing against
the compliance date; gaps whose fix is operational rather than textual.]

## Traceability Matrix
| Req ID | Citation | Policy section(s) | Coverage | Gap # |
|--------|----------|-------------------|----------|-------|
[The complete requirement-to-policy crosswalk — every requirement appears exactly
once. This is the audit artifact.]

## Information Gaps
[What could not be assessed — regulation supplied by citation only, policy sections
described rather than pasted, profile ambiguities — and how that limits the analysis.]

## Confidence
[HIGH / MODERATE / LOW — one line of reasoning tied to whether both full texts were
supplied.]

## Rules
- Runs standalone. The pasted regulation and policy are the entire evidence base —
  compare exactly what is there and attribute every call to specific text on each
  side. No system or integration is required — only the assistant and what you
  paste in.
- If a step needs a capability you do not have (live web access, file or image
  reading, a data feed) or a required input is missing, do not fail silently or
  fabricate. State plainly what is missing, then either proceed with the available
  material and mark the gap, or — if it blocks the analysis — ask for the specific
  input needed as a short, labeled list, and continue once it is provided.
- Every material claim carries a source — a citation on the regulation side, a
  section reference on the policy side — or is labeled as an assumption.
- Extract requirements from the regulation text only; do not import requirements
  from general knowledge of the subject area. Credit coverage from the policy text
  only; undocumented practice is NOT COVERED.
- Do not upgrade a "should" to a "must", and reflect the regulation's status: a
  proposed rule creates planning items, not compliance gaps — label them.
- Severity follows the rubric, not the section count: one CRITICAL gap outweighs
  ten LOW ones, and the executive summary must say so plainly.
- No empty sections — "no deficiencies noted" is a valid result: a fully covered
  requirement set produces an empty gap register, stated explicitly, with the
  traceability matrix still delivered in full.
- This is text-against-text analysis for drafting and planning, not a legal opinion.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line reason.
```

---

## How to use it

- **Works standalone — paste both texts.** The analysis is only as good as its inputs: pasting the full regulation and the full policy yields a citation-anchored matrix; pasting a citation and a policy summary yields a draft the output will explicitly tell you to verify. Both modes are supported, and the confidence rating reflects which one you used.
- Set `INSTITUTION PROFILE` precisely — it is the scoping filter. The same rule produces different requirement registers for a bank and a money-services business, and the out-of-scope list keeps your scoping decisions auditable.
- For a long regulation, run one part or subpart at a time and concatenate the registers — requirement IDs stay traceable and citations stay exact. Prefix IDs per run (A-R1, B-R1) to avoid collisions.
- Route the outputs to different owners: the gap register and language direction go to the policy writer; Implementation Considerations go to the process and control owners; the traceability matrix goes in the change file as the audit artifact.
- For a very long rule, a useful two-step chain: run [`obligation-extraction.md`](obligation-extraction.md) first, then feed its register in as the requirement side of this analysis. (A chain of two separate runs — each run still takes only one prompt.)

## Output structure

A coverage scoreboard in the header, the requirement register, a coverage map with cited policy provisions, a severity-ordered gap register with drafting direction per gap, implementation considerations, and a complete requirement-to-policy traceability matrix. The matrix is the artifact that survives the project — every requirement appears exactly once with its citation, its policy home, and its gap number if any.

## Tuning & variants

- **Delta analysis** — paste an amended rule and the prior version alongside the policy; ask for gaps created by the amendment only, each tagged with both rule citations.
- **Procedure-level pass** — run the same analysis with a procedure (not a policy) as the internal text to test whether operational documents implement what the policy promises.
- **Multi-policy mapping** — when coverage is spread across several documents, paste them all and have the coverage map cite document + section; the traceability matrix then doubles as a policy-inventory crosswalk.
- **Exam-prep framing** — add "for each CRITICAL or HIGH gap, state the question an examiner would ask and the answer the institution can currently give" to pressure-test the gap register.

## Worked example

*"Compare this final recordkeeping rule against our payments policy; we are a bank, the compliance date is in nine months; both texts pasted."* — the assistant returns a 23-requirement register, a coverage map crediting 14 covered, a gap register of 9 (1 CRITICAL, 3 HIGH, 4 MEDIUM, 1 LOW) with language direction per gap, implementation notes flagging two gaps as system builds, and the full traceability matrix.

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: A clause-level gap check of Harborview's digital-asset sanctions-screening policy against an illustrative synthetic sanctions-screening and blocking rule now in force.*

```text
You are a policy analyst at a financial institution. Compare the regulatory text below
against the internal policy below and produce a clause-level gap analysis. The question
for every requirement is the same: does the policy, as written, satisfy it? You analyze
text against text — you do not give legal advice, and you do not assume practices exist
that the policy does not document.

REGULATION / GUIDANCE: ILLUSTRATIVE EXCERPT — synthetic demonstration text, fabricated to exercise the gap-analysis method. The short title, section numbers, and obligations are invented and must not be attributed to any real instrument.

SANCTIONS-SCREENING AND BLOCKING RULE (illustrative), cited as Part 501, sections 501.10 through 501.90. Applies to any covered financial institution, including one conducting digital-asset activity.

501.10 — A covered institution shall screen every customer at onboarding, and every counterparty to a transaction it processes, against the current consolidated list of sanctioned persons and, for digital-asset activity, against the current list of designated blockchain addresses.

501.20 — A covered institution shall re-screen its entire existing customer base against the consolidated list within 24 hours of any update to that list, and in all cases no less frequently than daily.

501.30 — A covered institution shall block, and shall not process, any transaction in which a party or, for digital-asset activity, a wallet address matches a designated person or designated address, and shall report the blocked transaction to the sanctions authority within 10 business days.

501.40 — A covered institution shall maintain a documented process for resolving potential matches (alert adjudication), including the standard for clearing a false positive and the evidence retained for each decision.

501.50 — A covered institution shall screen against, at minimum, the sanctions authority's designated-persons list, the designated-address list, and any applicable foreign consolidated lists to which the institution is subject.

501.60 — A covered institution shall retain records of each screening run, each match, and each adjudication decision for five years, and shall be able to demonstrate, for any date in that period, which list version was in effect.

501.70 — A covered institution should apply risk-based enhanced screening to higher-risk customers and jurisdictions and is expected to review its screening configuration at least annually.

501.80 — A covered institution shall designate an officer accountable for the screening program and shall provide role-appropriate training to staff who adjudicate alerts.

501.90 — Effective and compliance dates: this Part is in force; the compliance date was 2026-01-01. Violations may result in civil penalties and enforcement action.
REGULATION STATUS: Final rule in force — the compliance date of 2026-01-01 has passed (illustrative).
INTERNAL POLICY / PROCEDURE: HARBORVIEW FINANCIAL GROUP — Digital-Asset Sanctions Screening Policy, version 3.1 (excerpt).

Section A — Purpose and scope. This policy governs sanctions screening for Harborview's digital-asset custody and transfer business. It applies to customers of the digital-asset subsidiary.

Section B — Customer screening. All new customers of the digital-asset subsidiary are screened against the sanctions authority's designated-persons list at onboarding. Screening results are recorded in the onboarding file.

Section C — Ongoing screening. The existing customer base is re-screened against the designated-persons list on a monthly basis.

Section D — Wallet screening. At onboarding, a customer's primary deposit wallet is screened using a third-party blockchain-analytics vendor. Transaction counterparties are screened where the analytics vendor returns a risk flag.

Section E — Alert handling. Potential matches are reviewed by the sanctions team. A match that is cleared is documented with a short note in the case system.

Section F — Blocking and reporting. Confirmed matches are blocked and escalated to the BSA Officer, who arranges reporting to the authority.

Section G — Governance. The BSA Officer owns the sanctions program. Training is provided to compliance staff during annual BSA training.

Section H — Records. Screening records are retained in the case system in accordance with the firm's records-retention schedule.
INSTITUTION PROFILE: Harborview Financial Group — a bank operating a digital-asset custody and transfer subsidiary (a DASP). In scope: retail and institutional digital-asset custody, deposits, withdrawals, and transfers. The traditional banking lines are out of scope for this analysis.
ANALYSIS DATE: 2026-03-05

If only a citation is provided for the regulation, work from it and state clearly that
every requirement row must be verified against the source text before drafting begins.

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

Work through five steps. Both sides of the comparison are texts: extract requirements
only from the regulation, and credit coverage only from the policy.

1. Build the requirement register. Parse the regulation and extract every concrete
   requirement that applies to the INSTITUTION PROFILE — each discrete thing the
   regulated party must do, must not do, must maintain, must file, or must be able
   to demonstrate. Split compound provisions so each requirement maps independently.
   Assign each a requirement ID (R1, R2, ...) and capture the exact citation
   (part / section / paragraph). Exclude requirements the profile takes out of scope,
   but list them separately with the exclusion reason so the scoping is auditable.
   Note binding force: "shall/must" items are requirements; "should/expected" items
   are expectations — register both, labeled.

2. Map coverage. For every requirement, search the policy for the provision(s) that
   address it and assign exactly one coverage status:
   - COVERED — the policy addresses the full requirement: same scope, same
     population, at least as strict, with any required timing/frequency present.
   - PARTIALLY COVERED — the policy addresses the requirement but narrower scope,
     weaker standard, missing frequency or threshold, or covers only some of the
     population. State precisely what is missing.
   - NOT COVERED — no policy provision addresses the requirement.
   Cite the policy section credited for every COVERED or PARTIALLY COVERED call.
   A practice the policy does not document earns no credit: "we do this but it
   isn't written down" is NOT COVERED until it is written down.

3. Rate each gap. Every PARTIALLY COVERED or NOT COVERED requirement becomes a gap.
   Severity rubric:
   - CRITICAL — a binding requirement with no coverage, where non-compliance
     carries direct enforcement exposure or the compliance date has passed.
   - HIGH — a binding requirement with no coverage but a future compliance date,
     or partial coverage whose missing element is the substance of the requirement.
   - MEDIUM — partial coverage missing a secondary element (a frequency, a
     documentation step, a narrower population), or an uncovered expectation
     ("should" item) that examiners review against.
   - LOW — wording misalignment with no substantive exposure: outdated citations,
     terminology drift, coverage located in the wrong document.

4. Specify the required change. For every gap, state the policy change that closes
   it: which policy section to amend or add, and the language direction — the
   substance the new text must contain (obligation, population, standard, timing,
   evidence) stated in one or two sentences. Direction, not finished legal
   drafting: precise enough that a policy writer can draft from it without
   re-deriving the requirement.

5. Assess implementation. For the gap set as a whole, identify what closing the
   gaps demands beyond drafting: new processes or controls implied by the new
   language, training, system or data changes, evidence/recordkeeping builds, and
   sequencing against the compliance date. Flag any gap whose fix is operational
   rather than textual — a policy can be made compliant on paper faster than the
   institution can comply with it.

## Output format

# Policy Gap Analysis — [regulation short title] vs. [policy title] — [DATE]

Regulation status: [status] | Institution profile: [profile]
Requirements assessed: [n] | Covered: [n] | Partially covered: [n] | Not covered: [n]
Gap severity profile: [n CRITICAL / n HIGH / n MEDIUM / n LOW]

## Executive Summary
[3-5 sentences: overall coverage posture, the worst gaps, and the drafting and
implementation effort implied.]

## Requirement Register
| ID | Requirement | Binding force | Citation | Applies because |
|----|-------------|---------------|----------|-----------------|
[One row per in-scope requirement. Out-of-scope items listed below the table with
exclusion reasons.]

## Coverage Map
| Req ID | Coverage | Policy provision credited | What is missing (if partial/none) |
|--------|----------|---------------------------|-----------------------------------|
[One row per requirement.]

## Gap Register
| Gap # | Req ID | Severity | Gap description | Required policy change (language direction) |
|-------|--------|----------|-----------------|----------------------------------------------|
[Ordered CRITICAL first. "No gaps identified — policy fully covers the in-scope
requirements" is a valid register.]

## Implementation Considerations
[Process, control, training, system, and evidence implications; sequencing against
the compliance date; gaps whose fix is operational rather than textual.]

## Traceability Matrix
| Req ID | Citation | Policy section(s) | Coverage | Gap # |
|--------|----------|-------------------|----------|-------|
[The complete requirement-to-policy crosswalk — every requirement appears exactly
once. This is the audit artifact.]

## Information Gaps
[What could not be assessed — regulation supplied by citation only, policy sections
described rather than pasted, profile ambiguities — and how that limits the analysis.]

## Confidence
[HIGH / MODERATE / LOW — one line of reasoning tied to whether both full texts were
supplied.]

## Rules
- Runs standalone. The pasted regulation and policy are the entire evidence base —
  compare exactly what is there and attribute every call to specific text on each
  side. No system or integration is required — only the assistant and what you
  paste in.
- If a step needs a capability you do not have (live web access, file or image
  reading, a data feed) or a required input is missing, do not fail silently or
  fabricate. State plainly what is missing, then either proceed with the available
  material and mark the gap, or — if it blocks the analysis — ask for the specific
  input needed as a short, labeled list, and continue once it is provided.
- Every material claim carries a source — a citation on the regulation side, a
  section reference on the policy side — or is labeled as an assumption.
- Extract requirements from the regulation text only; do not import requirements
  from general knowledge of the subject area. Credit coverage from the policy text
  only; undocumented practice is NOT COVERED.
- Do not upgrade a "should" to a "must", and reflect the regulation's status: a
  proposed rule creates planning items, not compliance gaps — label them.
- Severity follows the rubric, not the section count: one CRITICAL gap outweighs
  ten LOW ones, and the executive summary must say so plainly.
- No empty sections — "no deficiencies noted" is a valid result: a fully covered
  requirement set produces an empty gap register, stated explicitly, with the
  traceability matrix still delivered in full.
- This is text-against-text analysis for drafting and planning, not a legal opinion.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line reason.
```
<!-- /DEMO -->

---

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
