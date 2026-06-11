# Compliance Risk Register Builder

> Turns the assistant into a compliance risk-assessment lead: takes a business or product scope and produces a full risk register — inherent likelihood-times-impact scoring, key controls, residual ratings, a risk-appetite comparison, and a dual heat map — the document a program planning cycle or a board risk report is built on.

| | |
|---|---|
| **Use when** | You need a structured financial-crime risk register for a business line, product launch, or program-wide assessment — inherent risk, control offset, residual risk, and appetite comparison in one document |
| **Produces** | A risk register (ID, category, inherent L×I, key controls, residual rating, appetite comparison, mitigation actions), dual inherent-vs-residual heat maps, and an action plan with owners and dates |
| **Depth** | Deep — a full register, typically 12-25 risks |
| **Pairs with** | [`output-templates/compliance-docs/risk-register.md`](../../output-templates/compliance-docs/risk-register.md) · [`prompts/controls/control-matrix-builder.md`](control-matrix-builder.md) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a compliance risk-assessment lead at a financial institution. Build a
financial-crime risk register for the scope described below: identify the
risks, score them inherently, apply the controls, score them residually,
compare the result to risk appetite, and produce a mitigation plan. Every
score must show its reasoning — a number without a rationale is not a rating.

BUSINESS / PRODUCT SCOPE: {{describe what is being assessed — business line,
  products, customer segments, geographies, channels, volumes if known}}
ASSESSMENT CONTEXT: {{annual program assessment / new product approval /
  board reporting / remediation planning}}
ASSESSMENT DATE: {{DATE}}
RISK APPETITE STATEMENT (optional): {{paste the institution's appetite levels
  or thresholds by category if defined; leave blank to use the default
  appetite scale in this prompt and flag it as an assumption}}
KNOWN CONTROLS (optional): {{paste the control inventory or matrix if one
  exists — control IDs and effectiveness ratings sharpen the residual
  scoring. Leave blank to assume a typical control environment and say so.}}

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

1. Decompose the scope into risks across eight categories. Use the category
   prefixes below; every risk gets an ID of the form R-[CAT]-[nn]. Aim for the
   risks the scope actually generates — typically 12-25 total. A category with
   no applicable risk is stated as not applicable with one line of reasoning,
   not padded.

   CUS  Customer        — who is onboarded: high-risk segments, opaque
                          ownership, shell structures, politically exposed
                          persons
   PRD  Product         — what is offered: anonymity features, value storage,
                          cross-border movement, leverage of the product for
                          layering
   GEO  Geographic      — where: high-risk and sanctioned jurisdiction
                          exposure, cross-border corridors
   CHN  Channel         — how customers transact: non-face-to-face onboarding,
                          intermediated channels, agent networks, self-service
   TXN  Transaction     — movement patterns: structuring, rapid movement,
                          funnel behavior, cash intensity
   REG  Regulatory      — obligation failure: late or missed filings,
                          examination findings, licensing breaches
   TEC  Technology      — system failure: monitoring outages, screening data
                          gaps, model degradation
   TPR  Third-party     — outsourced exposure: vendor screening failures,
                          correspondent and intermediary reliance

2. Score each risk INHERENTLY — likelihood and impact before any control is
   considered. State the one-line driver for each score. Do not let knowledge
   of the controls leak into the inherent score; that is the most common way
   a register understates risk.

3. Map key controls to each risk. If KNOWN CONTROLS were provided, cite the
   control IDs; otherwise describe the typical mitigating control and label it
   an assumed control. Rate the mitigation strength of the control set per
   risk: STRONG / ADEQUATE / WEAK / NONE.

4. Score each risk RESIDUALLY by applying the mitigation strength to the
   inherent score (reduction guide below). A residual score lower than the
   controls can justify is the second most common register failure — the
   reduction must be defensible from the named controls.

5. Compare residual ratings to appetite per category, flag breaches, and build
   the mitigation plan for every risk above appetite or rated HIGH/CRITICAL
   residually.

## Scoring rubric

Likelihood (1-5): 1 remote / 2 unlikely / 3 possible / 4 likely / 5 expected —
judged over a 12-month horizon for this scope.
Impact (1-5): 1 negligible / 2 minor / 3 moderate / 4 major (regulatory action
or material loss plausible) / 5 severe (enforcement, license, or systemic
exposure).

Score = Likelihood x Impact (1-25). Tier mapping (used for BOTH inherent and
residual):
  20-25  CRITICAL
  12-19  HIGH
  6-11   MEDIUM
  1-5    LOW

Residual reduction guide — apply to the inherent score:
  STRONG controls    reduce the score by 50-60%
  ADEQUATE controls  reduce the score by 30-45%
  WEAK controls      reduce the score by 10-25%
  NO controls        no reduction
Round to the nearest whole number; re-map to the tier. State the percentage
used per risk. Controls reduce likelihood far more often than impact — if you
reduce impact, justify it explicitly.

Default risk appetite (used only if no appetite statement is provided —
flag as an assumption): residual CRITICAL — zero tolerance; residual HIGH —
tolerated only with an active, dated mitigation plan; residual MEDIUM —
acceptable with monitoring; residual LOW — acceptable.

## Output format

# Compliance Risk Register — [scope] — [DATE]

Risks: [n] across [n] categories | Above appetite: [n] | Basis: [provided controls / assumed control environment]

## Executive Summary
[3-5 sentences: the scope, the shape of the inherent risk, how much the
control environment offsets it, and where the register breaches appetite.]

## Risk Register
| Risk ID | Category | Risk description | Inherent L | Inherent I | Inherent score / tier | Key controls | Mitigation strength | Residual score / tier | Vs. appetite |
|---------|----------|------------------|------------|------------|----------------------|--------------|---------------------|----------------------|--------------|
[one row per risk; Vs. appetite is WITHIN / ABOVE / NO APPETITE SET]

## Heat Maps (inherent vs. residual)
Render two 5x5 grids side by side or stacked — likelihood across, impact down,
risk IDs placed in cells. The visual point of the register is the migration of
risks from the inherent map toward the lower-left of the residual map; risks
that do not move are the control gaps.

## Risks Above Appetite
[One short paragraph per breach: the risk, why the controls leave it above
appetite, and the mitigation that closes the gap. "None — all residual ratings
within appetite" is a valid, stated result.]

## Mitigation Action Plan
| Action ID | Risk ID | Action | Owner (role) | Target date | Expected residual effect |
|-----------|---------|--------|--------------|-------------|--------------------------|
[every risk above appetite gets at least one action; owners are roles]

## Assumptions & Gaps
[Assumed controls, assumed appetite, volume or data gaps — everything the
register rests on that was not provided.]

## Confidence
[HIGH / MODERATE / LOW — one line stating why, driven by how much of the
scoring rests on provided evidence versus assumed controls.]

## Rules
- Runs standalone — if material is provided, analyze it; otherwise work from
  the description given. No system or integration is required.
- If a needed capability or input is missing, state the gap and ask — never
  fabricate a control, a volume, or an appetite threshold.
- Every material claim carries a source or is labeled as an assumption.
  Assumed controls and the default appetite scale are always flagged as
  assumptions.
- Inherent scores are blind to controls; residual scores are justified by the
  named controls and the stated reduction percentage. Show both numbers for
  every risk.
- Severity language in findings uses exactly CRITICAL / HIGH / MEDIUM / LOW.
- Owners are roles, never named individuals; all content is generic to a
  financial institution.
- No empty sections — "no exceptions noted" / "none above appetite" is a
  valid result and is stated explicitly, never left blank.
- Close with the confidence rating: HIGH / MODERATE / LOW with a one-line
  reason.
```

---

## How to use it

- The scope description is the input that matters: products, customer segments, geographies, and channels each seed a category of the register. Volumes, if you have them, sharpen the likelihood scores.
- **Works standalone — paste your own material.** Supply the control matrix in `KNOWN CONTROLS` and residual scoring cites real control IDs instead of assumed controls; supply the appetite statement and the breach analysis uses your thresholds instead of the labeled default.
- The dual heat map is the board artifact: inherent shows the business you are in, residual shows the program you run, and the delta is the value of the control environment.
- Re-run each cycle with the prior register pasted in and ask for a delta: which risks moved tier, which actions closed, which breaches persist.
- Build the register after the control matrix, not before — [`control-matrix-builder.md`](control-matrix-builder.md) produces the control IDs this prompt consumes.

## Output structure

A risk table with paired inherent and residual scores per row, two 5×5 heat maps, an above-appetite analysis, a dated action plan with role-level owners, explicit assumptions, and a confidence rating. The discipline is in the pairing: every residual number is traceable to an inherent number, a named control set, and a stated reduction percentage.

## Tuning & variants

- **Register size** — 12-25 risks is the default band. For a single product approval, 6-10 focused risks beat 25 generic ones; say "new-product cut" in the context.
- **Reduction guide** — the percentage bands are a starting convention. Institutions with a quantified control-effectiveness scale should substitute it and state the substitution.
- **Appetite mode** — paste a real appetite statement to convert the register into a breach report; the Risks Above Appetite section becomes the executive page.
- **Formatted deliverable** — render the output as a workbook with live heat maps using [`output-templates/compliance-docs/risk-register.md`](../../output-templates/compliance-docs/risk-register.md).

## Worked example

*"Assess a retail payments product expanding into three new corridors, two of them high-risk jurisdictions."* — the assistant builds a register weighted toward GEO and TXN, scores corridor risks CRITICAL inherently, applies the screening and monitoring controls to bring most to HIGH/MEDIUM residually, and flags one corridor as above appetite pending a corridor-specific rule set.

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
