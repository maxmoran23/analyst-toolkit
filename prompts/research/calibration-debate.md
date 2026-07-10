# Calibration Debate

> Turns the assistant into a debate panel plus a judge: takes a thesis or a prior call, argues both sides as hard as it can (a real steelman for and against), then scores how defensible the original reasoning was on a 1-5 rubric — a calibration layer that tells you whether a decision was sound, separate from whether it happened to work out.

| | |
|---|---|
| **Use when** | You want to pressure-test a thesis, a recommendation, or a past call — before committing, or as a post-mortem on decision quality |
| **Produces** | A steelmanned pro case, a steelmanned con case, a five-dimension verdict, a 0-100 defensibility score, and the single biggest lesson |
| **Depth** | Medium — a structured debate and verdict |
| **Pairs with** | [`prompts/research/idea-generation.md`](idea-generation.md) · [`prompts/research/cross-source-synthesis.md`](cross-source-synthesis.md) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are running a calibration debate. Take the thesis or prior call below, argue both
sides as hard as you can, then judge how DEFENSIBLE the original reasoning was. The
point is calibration, not criticism: a well-reasoned call with weak counter-evidence
scores high even if the outcome turned out wrong — a decision can only be judged on
what was knowable at the time.

THE CALL: {{the thesis, prediction, recommendation, or decision being examined}}
ORIGINAL REASONING: {{the stated case for it — the evidence and logic used. If none
                      was recorded, write "not recorded" and the judge will note the
                      absence of an evidence trail.}}
CONTEXT / DATE: {{when the call was made and what was known then}}
PROVIDED MATERIAL (optional): {{paste any task- or entity-specific data you already
  have — the source documents behind the call, supporting data, analyst notes,
  evidence that was available at the time, related precedents. Leave blank to work
  from the assistant's own knowledge and any live access it has.}}
OUTCOME (optional): {{what actually happened, if known — used as a footnote, NOT as
                      the basis for the score}}

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

Run three roles in sequence. The two debaters must not soften their cases.

### Role 1 — Pro debater (steelman the call)
Produce the THREE strongest arguments supporting the original call. For each:
- Cite a specific piece of evidence that was available when the call was made.
- Ground it in mechanism, base rates, or precedent — not vibes.
Focus on the best version of the case, even if you personally doubt it.

### Role 2 — Con debater (steelman the opposite)
Produce the THREE strongest arguments the original reasoning SHOULD have weighed.
For each:
- Cite a specific piece of evidence or a specific reasoning gap.
- Focus on: missed evidence, base-rate violations, alternative explanations,
  analogous cases that went the other way.
The con case must be the strongest honest version — no straw men.

### Role 3 — Judge (score the original reasoning)
Read both debaters and the original reasoning. Score five dimensions 1-5:

  Dimension              Weight   1                3                 5
  -------------------------------------------------------------------------------
  Evidence quality        25%     hand-wave,       adequate but      multi-source,
                                  no sources       single-source     primary-document
  Reasoning quality       25%     post-hoc /       plausible chain,  mechanistic,
                                  circular         one weak leap     base-rate-aware
  Counter-consideration   20%     ignored obvious  acknowledged one  steelmanned the
                                  objections       counter           opposing case
  Actionability           15%     vague            clear but         specific, timed,
                                                   unscoped          and scoped
  Intellectual honesty    15%     over-claimed     balanced          honest about
                                  confidence                         uncertainty

Calibration anchors for the two hardest dimensions:
- Evidence quality 5: "Regulator X published action Y on [date], primary document at
  [source], with a specific named provision." Evidence quality 1: "It seems likely,
  given general conditions" — no source.
- Reasoning quality 5: names a base rate ("3 of the last 4 comparable cases resolved
  this way within 12 months") and a mechanism. Reasoning quality 1: "they will
  probably do something."

## Score

  CDS_raw = (evidence x 0.25) + (reasoning x 0.25) + (counter x 0.20)
          + (actionability x 0.15) + (honesty x 0.15)
  Defensibility Score = CDS_raw / 5 x 100   (0-100)

  80-100  EXEMPLARY   benchmark-quality reasoning
  60-79   SOLID       sound, with minor gaps
  40-59   ADEQUATE    defensible but with a clear weak dimension
  0-39    WEAK        the reasoning does not hold up — name what broke

## Output format

# Calibration Debate — [DATE]
The call: [restate in one line]

## Pro Case (steelmanned)
1. [argument] — Evidence: [specific, dated, sourced]
2. ...
3. ...

## Con Case (steelmanned)
1. [argument] — Evidence / gap: [specific]
2. ...
3. ...

## Verdict
| Dimension | Score (1-5) | Note |
|-----------|-------------|------|
| Evidence quality | | |
| Reasoning quality | | |
| Counter-consideration | | |
| Actionability | | |
| Intellectual honesty | | |

Defensibility Score: [n]/100 — [TIER]

## The Biggest Lesson
[Max 120 words. The single most important thing this debate reveals about the
reasoning — the one fix that would most improve the next call like it.]

## Outcome Note (if supplied)
[What happened, and whether it changes the lesson — explicitly NOT the score. A sound
call that lost, or a flawed call that won, is stated as exactly that.]

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
- Score the REASONING, not the outcome. A correct prediction from bad logic is a weak
  call; a wrong prediction from sound logic, given what was knowable, is a strong one.
- Both debaters must cite specific evidence. An argument with no evidence is dropped.
- The con case must be a genuine steelman. A weak con case inflates the score and
  defeats the purpose.
- Do not fabricate evidence, base rates, or precedents. If a base rate is unknown,
  say so — that itself is a finding about the reasoning's limits.
- Be honest in the verdict. Calibration only works if a weak call is scored weak.
```

---

## How to use it

- **Works standalone — paste your own data.** Put whatever source material you have into `PROVIDED MATERIAL`; the prompt produces the full standardized output from it and flags anything it cannot verify. Live access or a feed supplements but is never required.
- Paste the `ORIGINAL REASONING` in full. The judge scores the quality of the stated case — if no reasoning was recorded, that absence is itself a low score on evidence and honesty.
- Keep `OUTCOME` separate and optional. The whole point is to judge the decision independently of luck — supply the outcome only as a footnote.
- Use it forward (pressure-test a thesis before you commit) and backward (post-mortem a call to learn from it). Backward use over many calls builds a real sense of your own calibration.
- The con debater is the engine. If the con case feels soft, tell the assistant to make it harder and re-judge — a weak steelman produces a falsely high score.

## Output structure

A three-argument steelmanned pro case, a three-argument steelmanned con case, a five-dimension scored verdict table, a 0-100 defensibility score with tier, the single biggest lesson in under 120 words, and an optional outcome footnote. The score rewards sound reasoning under uncertainty, not lucky outcomes — which is what makes it a calibration tool.

## Tuning & variants

- **Weighting** — the default weights evidence and reasoning most heavily. For an action-oriented decision, raise Actionability; for a forecast, raise Counter-consideration. State any change.
- **Multi-call mode** — run it on several past calls and track defensibility scores over time to see whether your decision quality is improving.
- **Pre-commitment mode** — run it on a thesis you have *not* yet acted on; treat the con case as a checklist of what to verify before committing.
- **Panel variant** — for a high-stakes call, ask for two independent con debaters with different framings before the judge scores.

## Worked example

*"Here is a call I made three months ago and the reasoning behind it. Argue both sides and tell me how defensible the reasoning was — I want to know if it was a good decision, not just whether it worked."* — the assistant returns a steelmanned debate, a scored verdict, and the biggest lesson.

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: A compliance desk at Harborview Financial Group pressure-tests a late-2025 recommendation to onboard a major USD stablecoin for client settlement, judging whether the reasoning was sound independent of how it played out.*

```text
You are running a calibration debate. Take the thesis or prior call below, argue both
sides as hard as you can, then judge how DEFENSIBLE the original reasoning was. The
point is calibration, not criticism: a well-reasoned call with weak counter-evidence
scores high even if the outcome turned out wrong — a decision can only be judged on
what was knowable at the time.

THE CALL: Recommendation made 2025-11-15 by Harborview Financial Group's digital-asset advisory desk: begin accepting a major fully-reserved USD-pegged stablecoin (the 'reference stablecoin') as an eligible client-settlement asset within two quarters (by end of Q2 2026), on the thesis that the GENIUS Act's federal stablecoin framework would materially de-risk large, fully-reserved USD stablecoins for regulated settlement use by mid-2026.
ORIGINAL REASONING: Four points were recorded. (1) The GENIUS Act established a federal licensing and reserve regime for payment stablecoins, requiring 1:1 high-quality liquid reserves, monthly attestations, and priority redemption in insolvency — narrowing the reserve-quality uncertainty that had been the primary onboarding blocker. (2) Two peer mid-size banks had publicly disclosed settlement pilots with the same reference stablecoin in Q3 2025 with no reported loss events. (3) Client demand: 3 managed-account clients had asked in writing for stablecoin settlement in the prior 90 days. (4) The reference stablecoin held the largest circulating supply in its category and had maintained a peg within 30 basis points across the prior 12 months per public exchange data. Conclusion drawn: reserve and legal risk would be 'substantially resolved' by the framework's effective date, making a two-quarter onboarding timeline low-risk.
CONTEXT / DATE: The call was made 2025-11-15. Known at the time: the GENIUS Act was enacted but implementing rules (reserve-composition detail, examination expectations, the licensing queue) were not yet finalized; the effective date and phase-in schedule were published but subject to agency rulemaking. No enforcement precedent existed under the new regime. Peg history was benign but covered only a calm-market period. The desk had not yet completed its own reserve-attestation review of the issuer.
PROVIDED MATERIAL (optional): Treat as the primary evidence base; all figures illustrative and internal to this scenario.
[1] GENIUS Act summary note (desk-prepared, 2025-10): federal payment-stablecoin regime; permitted reserve assets limited to cash and short-dated government instruments; monthly third-party attestation; redemption priority in issuer insolvency; state/federal licensing paths; implementing rulemaking delegated to the primary regulator with an 18-month phase-in.
[2] Peer-pilot tracker (public disclosures, 2025-Q3): two mid-size banks announced limited stablecoin settlement pilots; disclosures did not state reserve-review depth or volumes.
[3] Peg-history extract (public exchange mid-prices, trailing 12 months): reference stablecoin deviation from 1.00 stayed within +/- 0.003 except one 0.006 intraday dip during a broad market sell-off in 2025-08, recovered same day.
[4] Client-demand log (internal, redacted to counts): 3 written requests for stablecoin settlement, all from managed-account clients, 2025-08 to 2025-10.
[5] Open-item note (desk, 2025-11): issuer reserve-attestation review not yet performed; examination expectations for bank use of third-party stablecoins not yet published; no insolvency-scenario test run.
OUTCOME (optional): OUTCOME (footnote only, not an input to the score): by 2026-06 the implementing rules had slipped — reserve-composition detail and examination guidance were still in a comment period, and the licensing queue was backlogged. The reference stablecoin held its peg throughout, but a smaller competing stablecoin de-pegged to 0.91 for 48 hours in 2026-04 after a reserve-transparency dispute, raising supervisory scrutiny across the category. Harborview deferred onboarding to Q4 2026 pending final examination guidance. The peg thesis held; the timeline thesis did not.

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

Run three roles in sequence. The two debaters must not soften their cases.

### Role 1 — Pro debater (steelman the call)
Produce the THREE strongest arguments supporting the original call. For each:
- Cite a specific piece of evidence that was available when the call was made.
- Ground it in mechanism, base rates, or precedent — not vibes.
Focus on the best version of the case, even if you personally doubt it.

### Role 2 — Con debater (steelman the opposite)
Produce the THREE strongest arguments the original reasoning SHOULD have weighed.
For each:
- Cite a specific piece of evidence or a specific reasoning gap.
- Focus on: missed evidence, base-rate violations, alternative explanations,
  analogous cases that went the other way.
The con case must be the strongest honest version — no straw men.

### Role 3 — Judge (score the original reasoning)
Read both debaters and the original reasoning. Score five dimensions 1-5:

  Dimension              Weight   1                3                 5
  -------------------------------------------------------------------------------
  Evidence quality        25%     hand-wave,       adequate but      multi-source,
                                  no sources       single-source     primary-document
  Reasoning quality       25%     post-hoc /       plausible chain,  mechanistic,
                                  circular         one weak leap     base-rate-aware
  Counter-consideration   20%     ignored obvious  acknowledged one  steelmanned the
                                  objections       counter           opposing case
  Actionability           15%     vague            clear but         specific, timed,
                                                   unscoped          and scoped
  Intellectual honesty    15%     over-claimed     balanced          honest about
                                  confidence                         uncertainty

Calibration anchors for the two hardest dimensions:
- Evidence quality 5: "Regulator X published action Y on [date], primary document at
  [source], with a specific named provision." Evidence quality 1: "It seems likely,
  given general conditions" — no source.
- Reasoning quality 5: names a base rate ("3 of the last 4 comparable cases resolved
  this way within 12 months") and a mechanism. Reasoning quality 1: "they will
  probably do something."

## Score

  CDS_raw = (evidence x 0.25) + (reasoning x 0.25) + (counter x 0.20)
          + (actionability x 0.15) + (honesty x 0.15)
  Defensibility Score = CDS_raw / 5 x 100   (0-100)

  80-100  EXEMPLARY   benchmark-quality reasoning
  60-79   SOLID       sound, with minor gaps
  40-59   ADEQUATE    defensible but with a clear weak dimension
  0-39    WEAK        the reasoning does not hold up — name what broke

## Output format

# Calibration Debate — [DATE]
The call: [restate in one line]

## Pro Case (steelmanned)
1. [argument] — Evidence: [specific, dated, sourced]
2. ...
3. ...

## Con Case (steelmanned)
1. [argument] — Evidence / gap: [specific]
2. ...
3. ...

## Verdict
| Dimension | Score (1-5) | Note |
|-----------|-------------|------|
| Evidence quality | | |
| Reasoning quality | | |
| Counter-consideration | | |
| Actionability | | |
| Intellectual honesty | | |

Defensibility Score: [n]/100 — [TIER]

## The Biggest Lesson
[Max 120 words. The single most important thing this debate reveals about the
reasoning — the one fix that would most improve the next call like it.]

## Outcome Note (if supplied)
[What happened, and whether it changes the lesson — explicitly NOT the score. A sound
call that lost, or a flawed call that won, is stated as exactly that.]

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
- Score the REASONING, not the outcome. A correct prediction from bad logic is a weak
  call; a wrong prediction from sound logic, given what was knowable, is a strong one.
- Both debaters must cite specific evidence. An argument with no evidence is dropped.
- The con case must be a genuine steelman. A weak con case inflates the score and
  defeats the purpose.
- Do not fabricate evidence, base rates, or precedents. If a base rate is unknown,
  say so — that itself is a finding about the reasoning's limits.
- Be honest in the verdict. Calibration only works if a weak call is scored weak.
```
<!-- /DEMO -->

---

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
