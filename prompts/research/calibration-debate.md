# Calibration Debate

> Turns the assistant into a debate panel plus a judge: takes a thesis or a prior call, argues both sides as hard as it can (a real steelman for and against), then scores how defensible the original reasoning was on a 1-5 rubric — a calibration layer that tells you whether a decision was sound, separate from whether it happened to work out.

| | |
|---|---|
| **Use when** | You want to pressure-test a thesis, a recommendation, or a past call — before committing, or as a post-mortem on decision quality |
| **Produces** | A steelmanned pro case, a steelmanned con case, a five-dimension verdict, a 0-100 defensibility score, and the single biggest lesson |
| **Depth** | Medium — a structured debate and verdict |
| **Pairs with** | [`prompts/research/idea-generation.md`](idea-generation.md) · [`prompts/research/cross-source-synthesis.md`](cross-source-synthesis.md) |

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
