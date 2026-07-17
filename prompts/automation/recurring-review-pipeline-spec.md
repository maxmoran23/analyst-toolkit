# Recurring Review Pipeline Spec
> A meta-prompt: describe any recurring review process in plain language and the assistant manufactures the full operating specification for an assistant-run pipeline — inputs, cadence, extraction rules, output files, refresh rules, and quality checks — ready to save and reuse as that desk's standing instruction.

| | |
|---|---|
| **Use when** | You do (or want to start doing) a review on a cycle — weekly comms triage, monthly tracker refresh, per-meeting minutes-to-actions — and want it converted from an informal habit into a written pipeline an assistant can execute the same way every run. |
| **Produces** | A complete pipeline operating spec: purpose statement, input contract, cadence, first-run vs refresh-run procedures, extraction rules, output file definitions, delta/refresh rules, quality checks, and an operator runbook — a configured instance of the indexing/refresh discipline for your specific process. |
| **Depth** | Heavy — one reusable operating spec per run |
| **Pairs with** | [`prompts/automation/comms-driven-report-refresh.md`](comms-driven-report-refresh.md) · [`prompts/automation/chat-history-index.md`](chat-history-index.md) |
| **Run-time needs** | **None — the prompt block below is fully self-contained.** For the strict voice + a Word / Excel / PDF / HTML deliverable, also attach [`BASE.md`](../../BASE.md) — one prompt + `BASE.md`, never a third file. |

---

## The prompt

Copy everything in the block below. Replace the {{PLACEHOLDERS}} before sending.

```text
You are a workflow engineer who converts a described recurring review process into a complete, written operating specification that an AI assistant can execute repeatably. The spec you produce is itself a prompt: a standing instruction the user saves and pastes (with that run's material) every cycle. Impose no domain assumptions — the process may involve any material, team, or subject. Design for repeatability: two runs of the finished spec over the same material must produce the same artifacts.

INPUTS
- PROCESS DESCRIPTION (required — what the user reviews, why, and what they need out of it, in their own words): {{PROCESS_DESCRIPTION}}
- SOURCE MATERIAL SHAPE (required — what arrives each cycle and in what form: emails, chat exports, reports, spreadsheets, notes): {{SOURCE_SHAPE}}
- CADENCE (optional — how often the review runs and any deadline it feeds): {{CADENCE}}
- DESIRED OUTPUTS (optional — artifacts the user already knows they want, e.g. "a maintained tracker and a two-line status note"): {{DESIRED_OUTPUTS}}
- CONSTRAINTS (optional — frozen sections, retention rules, tone requirements, things the pipeline must never do): {{CONSTRAINTS}}

## Preflight
Stop and ask once, as a numbered list, only if PROCESS_DESCRIPTION or SOURCE_SHAPE is missing or too vague to determine what a single run consumes and produces. If only optional inputs are missing, choose sensible defaults and mark every default DEFAULT in the spec so the user can override it.

## Method

Step 1 — Restate the process as a pipeline: what arrives, what is extracted, what artifacts are maintained, who reads them. Resolve the user's description into one sentence per stage. Anything the description leaves open becomes an explicit, marked default — never a silent assumption.

Step 2 — Define the input contract: the material the user supplies each run, required vs optional, acceptable forms, and what the pipeline does when something expected is absent (ask vs proceed-and-log).

Step 3 — Define the maintained artifacts. For each output file: name, format, structure (sections/columns), and whether it is REBUILT each run or MAINTAINED incrementally. For maintained artifacts, specify the refresh rules: stable identifiers so re-runs match, append/edit boundaries, a delta section, byte-preservation of untouched content, and an update log with date and sources per run.

Step 4 — Write the extraction rules: what gets pulled from the source material each cycle (facts, commitments, changes, metrics), the rule for each (where it comes from, how it is normalized), and the provenance requirement (every extracted item cites its source). Include an unparsed-material rule: anything unprocessable is listed verbatim, never dropped or invented.

Step 5 — Write the two run procedures:
- FIRST RUN: build the artifacts from scratch from a backlog of material; establish identifiers, baselines, and the update log.
- REFRESH RUN: consume only new material plus the existing artifacts; emit only new/changed content plus updated indexes and logs; never regenerate unchanged entries.

Step 6 — Write the quality checks the assistant must self-apply before returning, as a checklist: provenance complete, deltas consistent with logs, untouched content unchanged, all supplied material accounted for (processed, excluded-by-rule, or ledgered), and confidence stated with a reason.

Step 7 — Write the operator runbook: what the user does each cycle (gather, paste, review, store), how long a run should take them, what to check before trusting the output, and how to evolve the spec (change control: edits to the spec are dated and logged in the spec itself).

Step 8 — Assemble the final spec as one self-contained instruction block the user can paste into any assistant along with that cycle's material. It must reference no external file and restate every rule it depends on.

## Output format

**Subject:** {{ one line — process name, cadence, artifacts maintained }}

**1. Pipeline overview** — one-sentence-per-stage restatement, defaults marked DEFAULT.
**2. Input contract** — required/optional material per run and missing-input behavior.
**3. Maintained artifacts** — per file: name, structure, rebuild-vs-maintain, refresh rules.
**4. Extraction rules** — item types, normalization, provenance, unparsed-material rule.
**5. Run procedures** — FIRST RUN and REFRESH RUN, step by step.
**6. Quality checklist** — the self-checks each run must pass.
**7. Operator runbook** — the human's per-cycle steps and the spec's change-control rule.
**8. The pipeline spec, assembled** — the complete paste-ready instruction block (fenced), self-contained.

**Sources & Confidence:** HIGH / MODERATE / LOW — one-line reason (description completeness x how many defaults were assumed).

## Rules
- The assembled spec must be executable by an assistant with no file system and no memory of this conversation: everything it needs is inside it.
- Repeatability over cleverness: prefer deterministic rules (stable IDs, fixed section names, explicit thresholds) to judgment calls; where judgment is unavoidable, the spec must say so and require the judgment be logged.
- Every default you chose is marked DEFAULT with a one-line rationale; the user tunes by overriding, not by archaeology.
- The pipeline analyzes, extracts, and maintains artifacts; it never sends, files, or decides. Human review gates any outward action — write that into the spec.
- Capability-fallback: if the described process cannot be made repeatable as stated (e.g. sources the assistant cannot access), say which part and propose the closest paste-based equivalent — never spec a step that cannot actually run.
- No domain assumptions, no emoji. Direct and dense.
```

## How to use it
- Describe the process the way you would to a new team member — what shows up, what you do with it, what you produce. The prompt converts informality into structure; do not pre-formalize.
- Read section 1 first and correct the DEFAULT-marked assumptions — that is the entire configuration step. Everything else derives from it.
- Save section 8 (the assembled spec) as its own document; that block, plus each cycle's material, is what you paste from then on. This prompt is run once per process, not once per cycle.
- Re-run this prompt against the saved spec plus a description of what changed when the process evolves — treat the spec like any maintained artifact.
- The specs it manufactures follow the same discipline as the dedicated indexing and refresh prompts in this folder; use those directly when your process is exactly "index my mail/chat" or "refresh this report".

## Output structure
Eight fixed sections walking from restated pipeline through input contract, artifact definitions with refresh rules, extraction rules, first-run/refresh-run procedures, quality checklist, and operator runbook — culminating in the assembled, self-contained, paste-ready pipeline spec.

## Tuning & variants
- **Minimal spec:** add "compress the assembled spec to under 60 lines" for lightweight personal processes where the full apparatus is overkill.
- **Multi-artifact desks:** list several maintained artifacts in `DESIRED_OUTPUTS` (tracker + narrative + index); the spec will define cross-artifact consistency checks between them.
- **Handoff hardening:** add "write the operator runbook for someone who has never met me" when the pipeline will be run by a teammate.
- **Compliance overlay:** put retention, provenance, and no-fabrication requirements in `CONSTRAINTS`; they become non-negotiable rules inside the assembled spec rather than advisory notes.

## Worked example
*Input: "Every Friday I go through the week's project emails and our team channel, update a status tracker, and send my manager three bullets. Material arrives as pasted email threads and a chat export. Never change the Risks section without flagging it." Output: a spec defining two maintained artifacts (status tracker — MAINTAINED, keyed by stable project-row IDs, byte-preserving untouched rows; weekly three-bullet note — REBUILT) plus an update log; extraction rules for status changes, commitments, and blockers with per-item sourcing; FIRST RUN and REFRESH RUN procedures; a 6-item quality checklist; a runbook estimating 15 minutes per cycle; Risks-section edits gated behind an explicit flag per the constraint. Sources & Confidence: HIGH — concrete description, two DEFAULTs assumed (timezone; 30-minute chat segmentation).*

<!-- DEMO -->
## Try it now — paste this, nothing to fill in

The block below is the prompt above with every input already filled with **fictional demo data** — Harborview Financial Group, its counterparties, and every name, figure, and address in it are invented and synthetic. Paste it into any assistant (GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT) exactly as it is, with no edits, and you get the complete deliverable this prompt produces — the full method, rubric, and output structure, at depth. It is here so you can judge the quality before you ever supply your own material. When you run it for real, use the shell prompt above and put your own inputs in its place.

*Scenario: A Harborview analyst describes their informal Friday vendor-comms review and gets it manufactured into a written, repeatable pipeline spec.*

```text
You are a workflow engineer who converts a described recurring review process into a complete, written operating specification that an AI assistant can execute repeatably. The spec you produce is itself a prompt: a standing instruction the user saves and pastes (with that run's material) every cycle. Impose no domain assumptions — the process may involve any material, team, or subject. Design for repeatability: two runs of the finished spec over the same material must produce the same artifacts.

INPUTS
- PROCESS DESCRIPTION (required — what the user reviews, why, and what they need out of it, in their own words): Every Friday I go through the week's vendor-related emails and our #vendor-review channel, update our vendor status tracker, and send my manager a short status note. Today I do it from memory and the tracker drifts - rows get reworded, history gets lost, and nobody can tell what changed week to week. I want the tracker maintained properly with a record of what changed and why, and the status note generated from it.
- SOURCE MATERIAL SHAPE (required — what arrives each cycle and in what form: emails, chat exports, reports, spreadsheets, notes): Each cycle: pasted email threads (5-20 messages, mixed forwarded chains) and a copy-pasted chat transcript from one channel (30-80 lines, speaker and timestamp per line). Occasionally a vendor quote table embedded in an email body.
- CADENCE (optional — how often the review runs and any deadline it feeds): Weekly, Friday afternoon, feeding a Monday 9am team meeting.
- DESIRED OUTPUTS (optional — artifacts the user already knows they want, e.g. "a maintained tracker and a two-line status note"): A maintained vendor status tracker (one row per vendor) with an update log, and a rebuilt three-bullet status note each week.
- CONSTRAINTS (optional — frozen sections, retention rules, tone requirements, things the pipeline must never do): The tracker's Risk column may only change with an explicit flag in the update log. Nothing is ever sent by the assistant - I paste the note into email myself. No vendor pricing appears in the status note.

## Preflight
Stop and ask once, as a numbered list, only if PROCESS_DESCRIPTION or SOURCE_SHAPE is missing or too vague to determine what a single run consumes and produces. If only optional inputs are missing, choose sensible defaults and mark every default DEFAULT in the spec so the user can override it.

## Method

Step 1 — Restate the process as a pipeline: what arrives, what is extracted, what artifacts are maintained, who reads them. Resolve the user's description into one sentence per stage. Anything the description leaves open becomes an explicit, marked default — never a silent assumption.

Step 2 — Define the input contract: the material the user supplies each run, required vs optional, acceptable forms, and what the pipeline does when something expected is absent (ask vs proceed-and-log).

Step 3 — Define the maintained artifacts. For each output file: name, format, structure (sections/columns), and whether it is REBUILT each run or MAINTAINED incrementally. For maintained artifacts, specify the refresh rules: stable identifiers so re-runs match, append/edit boundaries, a delta section, byte-preservation of untouched content, and an update log with date and sources per run.

Step 4 — Write the extraction rules: what gets pulled from the source material each cycle (facts, commitments, changes, metrics), the rule for each (where it comes from, how it is normalized), and the provenance requirement (every extracted item cites its source). Include an unparsed-material rule: anything unprocessable is listed verbatim, never dropped or invented.

Step 5 — Write the two run procedures:
- FIRST RUN: build the artifacts from scratch from a backlog of material; establish identifiers, baselines, and the update log.
- REFRESH RUN: consume only new material plus the existing artifacts; emit only new/changed content plus updated indexes and logs; never regenerate unchanged entries.

Step 6 — Write the quality checks the assistant must self-apply before returning, as a checklist: provenance complete, deltas consistent with logs, untouched content unchanged, all supplied material accounted for (processed, excluded-by-rule, or ledgered), and confidence stated with a reason.

Step 7 — Write the operator runbook: what the user does each cycle (gather, paste, review, store), how long a run should take them, what to check before trusting the output, and how to evolve the spec (change control: edits to the spec are dated and logged in the spec itself).

Step 8 — Assemble the final spec as one self-contained instruction block the user can paste into any assistant along with that cycle's material. It must reference no external file and restate every rule it depends on.

## Output format

**Subject:** Friday vendor-comms review, weekly, 2 artifacts maintained

**1. Pipeline overview** — one-sentence-per-stage restatement, defaults marked DEFAULT.
**2. Input contract** — required/optional material per run and missing-input behavior.
**3. Maintained artifacts** — per file: name, structure, rebuild-vs-maintain, refresh rules.
**4. Extraction rules** — item types, normalization, provenance, unparsed-material rule.
**5. Run procedures** — FIRST RUN and REFRESH RUN, step by step.
**6. Quality checklist** — the self-checks each run must pass.
**7. Operator runbook** — the human's per-cycle steps and the spec's change-control rule.
**8. The pipeline spec, assembled** — the complete paste-ready instruction block (fenced), self-contained.

**Sources & Confidence:** HIGH / MODERATE / LOW — one-line reason (description completeness x how many defaults were assumed).

## Rules
- The assembled spec must be executable by an assistant with no file system and no memory of this conversation: everything it needs is inside it.
- Repeatability over cleverness: prefer deterministic rules (stable IDs, fixed section names, explicit thresholds) to judgment calls; where judgment is unavoidable, the spec must say so and require the judgment be logged.
- Every default you chose is marked DEFAULT with a one-line rationale; the user tunes by overriding, not by archaeology.
- The pipeline analyzes, extracts, and maintains artifacts; it never sends, files, or decides. Human review gates any outward action — write that into the spec.
- Capability-fallback: if the described process cannot be made repeatable as stated (e.g. sources the assistant cannot access), say which part and propose the closest paste-based equivalent — never spec a step that cannot actually run.
- No domain assumptions, no emoji. Direct and dense.
```
<!-- /DEMO -->

<!-- RUNTIME_CONTRACT -->

---

**Run-time contract** — links on this page are for browsing the repository, not dependencies. The ```` ```text ```` block above is complete as pasted: every rubric, rule, and output structure it relies on is inside it. The only companion file that ever adds anything is [`BASE.md`](../../BASE.md) (audit-defensible voice, quality floor, and the Word / Excel / PDF / HTML renderer). One prompt + `BASE.md` = the full toolkit quality system. Never a third file.
