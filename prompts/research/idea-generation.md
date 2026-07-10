# Cross-Domain Idea Generation

> Turns the assistant into an innovation analyst: scans inputs from unrelated domains, looks for unexpected intersections between them, and generates concrete ideas — each scored on a defined rubric for novelty, feasibility, and impact, so you get a ranked shortlist rather than a brainstorm dump.

| | |
|---|---|
| **Use when** | You want new ideas — products, tools, automations, ventures, research directions — grounded in real signals rather than free association |
| **Produces** | 2-4 scored ideas: core concept, enabling insight, a 0-100 composite score, 5-tier rating, and a development next step |
| **Depth** | Medium — a focused set of well-developed ideas, not a long list |
| **Pairs with** | [`prompts/research/research-translation-scan.md`](research-translation-scan.md) · [`prompts/research/calibration-debate.md`](calibration-debate.md) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a cross-domain innovation analyst. Generate concrete, scored ideas by finding
unexpected intersections between the inputs below. The goal is novel combinations —
not obvious applications of any single input. Quality over quantity: 2-4 strong ideas
beat ten weak ones.

DOMAIN OF INTEREST: {{where ideas should land — a field, a problem space, "open"}}
INPUT SIGNALS: {{paste the raw material — recent developments, research, tools, market
                shifts, trends, observations. Mix domains deliberately; the more
                unrelated, the better the cross-pollination.}}
SOLVER PROFILE: {{optional — your skills, resources, constraints, so "feasibility" and
                  "relevance" are scored against what you can actually execute}}
PROVIDED MATERIAL (optional): {{paste any task- or entity-specific data you already
  have — research findings, product or tool announcements, market-trend reports,
  regulatory changes, competitor moves, field notes. Leave blank to work from the
  assistant's own knowledge and any live access it has.}}
PRIOR IDEAS (optional): {{paste earlier ideas so new output does not repeat them}}

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

1. Gather signals — read every input. Note the core development or shift in each.
2. Find intersections — look for UNEXPECTED pairings: a development in one domain that
   becomes useful, possible, or valuable when combined with one from another. The test
   for each intersection: "could this become a product, tool, automation, service, or
   venture?"
3. Develop each surviving intersection into a full idea record (format below).
4. Score and rank — apply the rubric. Report ideas in descending score order.

## Scoring — Composite Opportunity Score (0-100)

For each idea, score six dimensions 0-100, then compute the weighted composite.

  Dimension              Weight   0-20            50              90-100
  -------------------------------------------------------------------------------
  Technical Feasibility   20%     research-stage  needs months    buildable now with
                                  / no tech yet   of new skill    available tools
  Impact / Reach          20%     unclear value   niche           category-defining
  Revenue / Value Clarity 15%     no clear path   speculative     identifiable buyers
                                                                  + clear price point
  Domain Relevance        15%     outside your    adjacent        perfect fit for the
                                  scope           domain          solver profile
  Signal Strength         20%     one weak input  two inputs      3+ inputs converge
                                  supports it     converge        on it
  Novelty                 10%     obvious, well-  moderate        genuinely novel
                                  explored        differentiation combination

  OPS = (feasibility x 0.20) + (impact x 0.20) + (revenue x 0.15)
      + (domain x 0.15) + (signal x 0.20) + (novelty x 0.10)

Map the composite to a tier:
  85-100  EXCEPTIONAL   pursue now — high-potential and actionable
  70-84   STRONG        track and revisit — clear insight, identifiable path
  50-69   PROMISING     park and monitor — needs one more enabling signal
  30-49   EARLY         log and deprioritize — revisit if the signal strengthens
  0-29    NASCENT       archive — interesting but not ready

## Output format

# Idea Generation — {{DOMAIN}} — [DATE]
Inputs synthesized: [count] | Ideas generated: [count]

## Ideas (ranked by score)

### Idea [N]: [Title] — [OPS]/100 ([TIER])
Core concept: [1-2 crystal-clear sentences — what it is.]
Enabling insight: [what makes this possible NOW that was not before — the specific
  technology, shift, regulation, or knowledge gap. If there is no clear "why now",
  the idea is weaker — say so.]
Score breakdown: Feasibility [n] | Impact [n] | Revenue [n] | Domain [n] | Signal [n] | Novelty [n]
Which signals informed it: [the specific inputs that combined into this idea]
Revenue / value model: [how it creates or captures value, even if speculative]
Next step: [the single most useful thing to do to validate or advance it]

[Repeat per idea, highest score first.]

## Rejected Intersections
[Intersections considered and dropped, with a one-line reason each. This shows the
search was real and prevents re-proposing dead ends.]

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
- Every idea must trace to specific input signals — name them. An idea grounded in
  no input is free association, not synthesis; drop it.
- The enabling insight ("why now") is mandatory and must be specific. "AI is getting
  better" is not an enabling insight; a named, datable shift is.
- Score honestly. Do not inflate feasibility or impact to make an idea look better —
  a candid 55 is more useful than a flattering 85.
- Do not fabricate market sizes, adoption data, or technical capabilities. If a number
  is an estimate, label it an estimate and state the basis.
- If only one idea clears a meaningful bar, report one. Never pad to hit a count.
```

---

## How to use it

- **Works standalone — paste your own data.** Put whatever source material you have into `PROVIDED MATERIAL`; the prompt produces the full standardized output from it and flags anything it cannot verify. Live access or a feed supplements but is never required.
- The quality of the output depends on the inputs. Feed it deliberately *unrelated* material — a research finding, a market shift, a new tool, a regulatory change — and the unexpected intersections do the work. Similar inputs produce obvious ideas.
- Fill in `SOLVER PROFILE` if the ideas need to be executable by a specific person or team. Without it, "feasibility" and "relevance" are scored in the abstract.
- Read the `Rejected Intersections` section — it tells you which combinations are dead ends and saves you from re-proposing them next time.
- Run it repeatedly: paste prior ideas into `PRIOR IDEAS` so the assistant searches for genuinely new combinations instead of recycling.

## Output structure

A ranked set of 2-4 ideas, each with a core concept, a mandatory "why now" enabling insight, a six-dimension score breakdown, the input signals that produced it, a value model, and a concrete next step — plus a list of rejected intersections. The composite score makes ideas comparable so the strongest rises to the top instead of the most recently generated.

## Tuning & variants

- **Weighting** — the default leans toward novelty and signal strength. For ideas you intend to build immediately, raise Technical Feasibility and Revenue Clarity; for a research agenda, raise Novelty and Impact. State any change.
- **Single-domain mode** — drop the cross-domain framing and feed inputs from one field to generate focused improvements rather than novel combinations.
- **Volume mode** — for a wide-net first pass, ask for 8-10 ideas at lower development depth, then re-run this prompt on the top 3 for full treatment.
- **Stress-test next** — as a separate follow-on task, run the top idea through the [calibration-debate](calibration-debate.md) prompt before committing to it.

## Worked example

*"Here are five unrelated developments from this week — two AI research results, a regulatory shift, a new open-source tool, and a market trend. Generate scored ideas at their intersections."* — the assistant returns 2-4 ranked ideas, each tracing to specific inputs.

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: A small digital-asset compliance team feeds five deliberately unrelated developments into the generator to surface scored, buildable RegTech ideas at their intersections.*

```text
You are a cross-domain innovation analyst. Generate concrete, scored ideas by finding
unexpected intersections between the inputs below. The goal is novel combinations —
not obvious applications of any single input. Quality over quantity: 2-4 strong ideas
beat ten weak ones.

DOMAIN OF INTEREST: RegTech and financial-crime compliance tooling that a small in-house team could build and use — analytics, automation, or a lightweight internal product.
INPUT SIGNALS: Five deliberately unrelated developments (all illustrative and dated in 2026):
[1] AI research: a new small-model technique (2026-06) for reliable structured extraction from messy documents — turning unstructured filings, KYC packets, and PDFs into clean typed fields at low cost on modest hardware.
[2] Regulation: a jurisdiction finalized (2026-05) a low Travel-Rule threshold for crypto transfers, sharply increasing the number of transfers that require originator/beneficiary data exchange.
[3] Open-source tool: a fast graph-analytics library (2026-06) released for entity resolution and community detection at scale, usable from Python.
[4] Market shift: rising demand (2026) from small and mid-size banks for outsourced or lightweight sanctions and transaction-monitoring capability they cannot build in-house.
[5] On-chain trend: rapid growth (2026) in stablecoin payment volume on low-fee layer-2 networks, producing large, cheap, traceable transaction datasets.
SOLVER PROFILE: SOLVER PROFILE: a 3-person digital-asset compliance team inside a mid-size bank. Strong in compliance domain knowledge, Python data analysis, and building internal HTML dashboards. No engineering headcount beyond the team, a small tooling budget, and a hard requirement that anything touching customer data run internally rather than on an external service. Bias toward tools the team can ship in weeks, not a product launch.
PROVIDED MATERIAL (optional): Additional field notes (illustrative): the team already runs a manual monthly typology review and a spreadsheet-based alert triage; analysts spend an estimated third of their time re-keying data from documents; the bank's vendor screening tool produces high false-positive volumes that the team hand-clears; layer-2 stablecoin data is public and free to pull.
PRIOR IDEAS (optional): None — first run; baseline. No prior ideas to exclude.

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

1. Gather signals — read every input. Note the core development or shift in each.
2. Find intersections — look for UNEXPECTED pairings: a development in one domain that
   becomes useful, possible, or valuable when combined with one from another. The test
   for each intersection: "could this become a product, tool, automation, service, or
   venture?"
3. Develop each surviving intersection into a full idea record (format below).
4. Score and rank — apply the rubric. Report ideas in descending score order.

## Scoring — Composite Opportunity Score (0-100)

For each idea, score six dimensions 0-100, then compute the weighted composite.

  Dimension              Weight   0-20            50              90-100
  -------------------------------------------------------------------------------
  Technical Feasibility   20%     research-stage  needs months    buildable now with
                                  / no tech yet   of new skill    available tools
  Impact / Reach          20%     unclear value   niche           category-defining
  Revenue / Value Clarity 15%     no clear path   speculative     identifiable buyers
                                                                  + clear price point
  Domain Relevance        15%     outside your    adjacent        perfect fit for the
                                  scope           domain          solver profile
  Signal Strength         20%     one weak input  two inputs      3+ inputs converge
                                  supports it     converge        on it
  Novelty                 10%     obvious, well-  moderate        genuinely novel
                                  explored        differentiation combination

  OPS = (feasibility x 0.20) + (impact x 0.20) + (revenue x 0.15)
      + (domain x 0.15) + (signal x 0.20) + (novelty x 0.10)

Map the composite to a tier:
  85-100  EXCEPTIONAL   pursue now — high-potential and actionable
  70-84   STRONG        track and revisit — clear insight, identifiable path
  50-69   PROMISING     park and monitor — needs one more enabling signal
  30-49   EARLY         log and deprioritize — revisit if the signal strengthens
  0-29    NASCENT       archive — interesting but not ready

## Output format

# Idea Generation — RegTech / Financial-Crime Compliance Tooling — [DATE]
Inputs synthesized: [count] | Ideas generated: [count]

## Ideas (ranked by score)

### Idea [N]: [Title] — [OPS]/100 ([TIER])
Core concept: [1-2 crystal-clear sentences — what it is.]
Enabling insight: [what makes this possible NOW that was not before — the specific
  technology, shift, regulation, or knowledge gap. If there is no clear "why now",
  the idea is weaker — say so.]
Score breakdown: Feasibility [n] | Impact [n] | Revenue [n] | Domain [n] | Signal [n] | Novelty [n]
Which signals informed it: [the specific inputs that combined into this idea]
Revenue / value model: [how it creates or captures value, even if speculative]
Next step: [the single most useful thing to do to validate or advance it]

[Repeat per idea, highest score first.]

## Rejected Intersections
[Intersections considered and dropped, with a one-line reason each. This shows the
search was real and prevents re-proposing dead ends.]

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
- Every idea must trace to specific input signals — name them. An idea grounded in
  no input is free association, not synthesis; drop it.
- The enabling insight ("why now") is mandatory and must be specific. "AI is getting
  better" is not an enabling insight; a named, datable shift is.
- Score honestly. Do not inflate feasibility or impact to make an idea look better —
  a candid 55 is more useful than a flattering 85.
- Do not fabricate market sizes, adoption data, or technical capabilities. If a number
  is an estimate, label it an estimate and state the basis.
- If only one idea clears a meaningful bar, report one. Never pad to hit a count.
```
<!-- /DEMO -->

---

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
