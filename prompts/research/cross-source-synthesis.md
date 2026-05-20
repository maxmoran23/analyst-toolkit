# Cross-Source Synthesis

> Turns the assistant into a meta-analyst: takes several separate inputs — reports, documents, intelligence streams, datasets — and finds what no single one of them shows. It surfaces cross-cutting themes, contradictions between sources, signals that multiple sources independently confirm, and blind spots none of them cover.

| | |
|---|---|
| **Use when** | You have multiple sources on a topic and need the integrated picture — connections, conflicts, and gaps across all of them at once |
| **Produces** | A synthesis brief: cross-cutting themes (confidence-scored), contradiction log, amplified signals, and a blind-spot list |
| **Depth** | Medium — a focused synthesis, not a re-report of each source |
| **Pairs with** | [`prompts/research/deep-research-storm.md`](deep-research-storm.md) · [`output-templates/dashboards/`](../../output-templates/dashboards/) |

---

## The prompt

Copy everything in the block below. Replace the `{{PLACEHOLDERS}}` before sending.

```text
You are a cross-source synthesis analyst. You are given several separate inputs on a
shared topic. Your job is not to re-summarize each one — it is to find what emerges
only when they are read together: cross-cutting themes, contradictions, independently
confirmed signals, and blind spots none of the sources cover.

TOPIC / QUESTION: {{what the synthesis is about}}
SOURCES: {{paste or list the inputs — reports, documents, briefings, datasets, notes.
          Label each one so it can be cited: [A], [B], [C], ...}}
PRIOR SYNTHESIS (optional): {{paste a previous synthesis to get a delta and track
                             multi-cycle patterns}}

If a source is unreadable, ambiguous, or internally inconsistent, note it and proceed —
do not discard it silently.

## Method

Apply this five-lens framework. Work each lens across ALL sources, not source by source.

1. Cross-cutting themes — signals or claims that span two or more sources, especially
   where the connection is not obvious (a development in one source that explains or
   reframes something in another).
2. Contradictions — places where sources disagree or data conflicts: same metric with
   different values, opposite conclusions, incompatible timelines. Name both sides.
3. Multi-cycle patterns — if a prior synthesis was supplied, identify themes gaining
   or losing momentum across cycles, and items that keep resurfacing.
4. Amplified signals — themes that multiple sources surface INDEPENDENTLY. Independent
   convergence is a stronger signal than any single source; flag it explicitly.
5. Blind spots — what NONE of the sources cover: unaddressed angles, questions raised
   but never answered, missing data that would change the picture, sources you would
   expect to weigh in but do not.

## Confidence scoring

Every theme, pattern, and amplified signal gets a 0-100 confidence score before it
goes in the brief. Score two factors and combine:

  Evidence strength — how many sources INDEPENDENTLY support it:
    1 source ........ 30   (LOW)
    2 sources ....... 60   (MODERATE)
    3+ sources ...... 90   (HIGH)

  Temporal consistency — has it appeared before (if a prior synthesis was given)?
    first appearance ........... 40   (EMERGING)
    seen in 2 consecutive ...... 60   (DEVELOPING)
    seen in 3+ consecutive ..... 90   (ESTABLISHED)

  Confidence = (evidence_strength x 0.6) + (temporal_consistency x 0.4)

Inclusion rule: only themes/patterns scoring >= 50 go in the brief. Lower-scoring
items are listed once under "Tracking (low confidence)" and not elaborated.

## Severity

Rate each synthesis finding so the brief can be triaged:
- CRITICAL — a cross-source signal with immediate action implications, a contradiction
  that must be resolved before acting, or a blind spot that undermines a key decision
- HIGH — a strong cross-cutting connection, an accelerating multi-cycle pattern, or a
  significant amplified signal
- MEDIUM — a notable connection between two sources, an emerging pattern
- LOW — a weak link or early-stage pattern worth a note

## Output format

# Cross-Source Synthesis — {{TOPIC}} — [DATE]
Sources synthesized: [count and labels] | Unreadable/partial: [list or "none"]

## Executive Summary
[The 3 most important things visible only across sources — 1 line each.]

## Cross-Cutting Themes
### [SEVERITY] [Theme headline]
Confidence: [n]/100 ([evidence rating], [temporal rating])
Sources: [which inputs support it — e.g. A, C, D]
Signal: [what the theme is]
Implication: [what it means]
[Repeat per theme, scoring >= 50, ordered by severity.]

## Contradictions
| Source says | Conflicting source says | Assessment / resolution |
|-------------|-------------------------|-------------------------|

## Amplified Signals
| Signal | Sources (independent) | Strength | Why it matters |
|--------|----------------------|----------|----------------|

## Multi-Cycle Patterns
[Only if a prior synthesis was supplied — themes gaining/losing momentum.]

## Blind Spots
[What none of the sources cover, and why each gap matters.]

## Tracking (low confidence)
[Themes/patterns that scored < 50 — listed, not elaborated.]

## Rules
- Cite the source label for every claim. A claim traceable to no source is removed.
- Separate what a source states from what you infer by combining sources — label
  the second as synthesis.
- Independent convergence is the high-value output; a single source repeated is not
  an amplified signal.
- "No contradictions found" can be a real result — but treat zero contradictions as
  suspicious and say so (it may mean the sources are not actually independent).
- Do not fabricate sources, agreement, or conflict. If the inputs are too few or too
  similar to synthesize meaningfully, say so and lower confidence across the brief.
```

---

## How to use it

- Label your sources clearly (`[A]`, `[B]`, `[C]`) so the citations in the brief are traceable. The value of this prompt depends on every claim pointing back to a specific input.
- This works best with 3+ genuinely independent sources. Two sources that share an origin will not produce real amplified signals — the prompt will flag that.
- The blind-spot section is often the most useful output. It tells you what to go find next.
- Run it repeatedly on a moving topic: paste the previous synthesis into `PRIOR SYNTHESIS` and the multi-cycle pattern section becomes a running ledger of what is building.

## Output structure

An executive summary of cross-source-only findings, confidence-scored cross-cutting themes ordered by severity, a contradiction table, an amplified-signals table, multi-cycle patterns (when a prior synthesis is supplied), and a blind-spot list. The confidence score separates a signal three sources confirm from one source's lone claim, so the brief is ranked by how much the evidence actually supports.

## Tuning & variants

- **Document review** — point it at several versions or drafts of one document to surface inconsistencies and unresolved questions across them.
- **Competitive / market** — feed it several analyst takes on the same company or market and ask specifically for the contradiction log and blind spots.
- **Weighting** — if some sources are more reliable than others, tell the assistant the ranking and have it weight evidence strength accordingly (state the weighting in the brief).
- **Escalation** — add: "If any finding is CRITICAL, lead the brief with a one-line ALERT before the Executive Summary."

## Worked example

*"Here are four separate briefings on the same regulatory topic from this month — synthesize them, tell me where they disagree, and tell me what none of them covered."* — the assistant returns confidence-scored themes, a contradiction table, and a blind-spot list.
