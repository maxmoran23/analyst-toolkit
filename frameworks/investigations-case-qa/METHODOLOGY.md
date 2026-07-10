# Methodology — Investigations Case-File QA Engine

The regulator-facing specification of the QA grading and disposition logic.
Every check, severity class, weight, and decision rule below exists as a named
construct in [`scorer.py`](scorer.py); that file is the executable form of this
document. The evidence that the logic performs as specified is in
[`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md), produced by
[`run_validation.py`](run_validation.py). Model-governance framing is shared
across the pillar in [`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** When an investigator finishes a case, the file records what
> was looked at, what evidence was gathered, what was concluded and why, when it
> happened, and whether anything needed to be raised up the chain. A second-line
> reviewer then checks the file before it is closed for good. This engine runs
> the structural half of that check as 13 named tests across five questions: is
> the file complete, is the conclusion backed by evidence, is the conclusion
> consistent with the evidence, was it done on time, and is the write-up
> structurally sound? Serious defects send the file back and alert a supervisor;
> fixable ones return it with a to-do list; a file passes only when the engine
> can name exactly why it is clean. The engine never re-decides the case itself.

---

## 1. Problem framing and error posture

A financial-crime organization's second line (the fictional reference
institution here is Harborview Financial Group) quality-assures completed
investigation files before closure. The review has a structural half — presence,
citation, consistency, timeliness, narrative structure — and a judgement half
(is the analysis any good?). This engine automates only the structural half, so
QA reviewers spend their judgement on files that deserve it. The error costs are
asymmetric, exactly as elsewhere in this pillar:

- A **false pass** — a critically deficient file (an unsupported or
  contradicted conclusion, a missed escalation, a missing mandatory element)
  released through QA — defeats the purpose of the second line and leaves an
  indefensible file of record. Its tolerated rate is **zero**.
- A **false flag** — a clean file held back for correction — is operational
  cost: rework burden and closure delay.

The engine is a **QA triage and evidence-of-review** tool. It never reopens a
case, never overrides the investigative disposition, never auto-approves a
deficient file, and never makes a filing decision — it routes files, with named
reasons, to the humans who do.

---

## 2. Inputs (the structured case record)

`case_id`, `case_type` (STRUCTURING / FUNNEL_ACCOUNT / LAYERING_PASSTHROUGH /
SANCTIONS_REFERRAL / FRAUD_REFERRAL — sets the policy SLA and minimum lookback);
**completeness elements** — `subject_identified`, `account_scope_documented`,
`lookback_days`, `scope_elements_total` / `scope_elements_reviewed`;
**evidence** — `evidence_item_count`, `evidence_source_types`,
`corroborated_typology` (evidence on file corroborates the alert typology);
**disposition** — `disposition` (CLOSED_NO_FINDING / ESCALATED_WITH_FINDING),
`rationale_claim_count` / `rationale_cited_count` (claims referencing at least
one documented evidence item); **escalation posture** —
`escalation_trigger_count` (documented facts requiring escalation per policy),
`escalation_flag`; **timeline milestones** — `alert_to_open_days`,
`open_to_complete_days`; **narrative structure** — `chronology_present`,
`missing_5w` (among who/what/when/where/why), `empty_narrative_fields`.

The record is structured metadata about the file, not the prose itself — the
deliberate boundary of the model (see section 8).

## 3. QA dimensions and weights

Five dimensions, each scored 0-100, combined by `_lib/scoring.weighted_composite`:

| Dimension | Weight | Question it answers |
|---|---|---|
| completeness | 0.25 | Are all mandatory elements for the case type present? |
| evidence_support | 0.25 | Does documented evidence back the disposition? |
| consistency | 0.20 | Does the disposition agree with the evidence and the escalation posture? |
| narrative_quality | 0.20 | Is the write-up structurally complete? |
| timeliness | 0.10 | Were the policy SLAs met? |

Each fired check deducts from its dimension's sub-score by severity class —
CRITICAL 100 (zeroes the dimension), MAJOR 45, MINOR 15, floored at 0. The
weights and deductions are calibration points, not the safety mechanism: the
no-pass rule for critical deficiencies is a hard gate in section 6, not a weight.

## 4. Named QA checks

Each check (in [`scorer.py`](scorer.py), via the shared `_lib/rules.py`
mechanism) returns fired / severity / detail. A CRITICAL check carries a
**deficiency-class tag**; a fired tagged check is the signal that a case cannot
be QA_PASS — the same structural role a typology tag plays in the
transaction-monitoring framework.

| Check | Dimension | Class | Fires when |
|---|---|---|---|
| `missing_mandatory_element` | completeness | **CRITICAL** | subject identification, account scope, lookback period, or disposition rationale absent |
| `lookback_below_policy` | completeness | MAJOR | lookback present but below the case-type policy minimum |
| `unsupported_disposition` | evidence_support | **CRITICAL** | any disposition-rationale claim references no documented evidence item |
| `cleared_with_unreviewed_scope` | evidence_support | **CRITICAL** | closed as no-finding with scope elements unreviewed — the clearance cannot be supported |
| `single_source_evidence` | evidence_support | MINOR | all evidence items from a single source type (no corroborating source) |
| `contradictory_disposition` | consistency | **CRITICAL** | corroborated typology evidence on file, yet closed as no-finding |
| `missed_escalation` | consistency | **CRITICAL** | documented escalation trigger(s) present, no escalation flagged |
| `escalation_without_trigger` | consistency | MINOR | escalation flagged with no documented trigger |
| `sla_breach_material` | timeliness | MAJOR | completion beyond `sla_material_multiple` (1.5x) of the case-type SLA |
| `sla_breach_minor` | timeliness | MINOR | completion over SLA but within the material tolerance |
| `incomplete_5w` | narrative_quality | MAJOR | who/what/when/where/why coverage missing |
| `missing_chronology` | narrative_quality | MAJOR | no chronology of events in the narrative |
| `empty_narrative_field` | narrative_quality | MAJOR | a mandatory narrative field left empty |

Policy reference tables (`SLA_DAYS`, `MIN_LOOKBACK_DAYS`) are named constants in
`scorer.py` and are themselves calibration points — a deployment substitutes its
own procedures manual (see [`tuning.md`](tuning.md)).

## 5. Quality score

```
dim_score[d] = max(0, 100 - Σ DEDUCTION[class] over fired checks in d)
quality_score = Σ (dim_score[d] × weight[d])          # weights sum to 1.0 -> 0-100
```

The score ranks the remediation queue and feeds calibration reporting. It does
**not** by itself pass a file — the validation evidence shows why: the planted
critical-deficient files score 74-79, well inside the range a threshold policy
would eventually pass.

## 6. QA disposition rules (in firing order)

1. **Any CRITICAL check fired** → **REWORK_AND_ESCALATE**. The reason names each
   deficiency class and detail; the file returns to the investigator for rework
   and the QA finding is routed to the investigations supervisor. This branch is
   evaluated first and unconditionally — a critical deficiency makes QA_PASS
   unreachable regardless of the quality score.
2. **Any MAJOR check fired** (no critical) → **REMEDIATE**, with each major
   finding named. Correctable; no supervisor escalation.
3. **`quality_score` below `pass_score`** (no critical or major) → **REMEDIATE**
   on accumulated minor findings.
4. **Otherwise** → **QA_PASS**, only on the provable named basis: mandatory
   elements complete, all disposition-rationale claims evidence-cited,
   disposition consistent with the evidence, escalation posture correct, no
   material SLA breach, narrative structurally complete. Minor observations are
   appended as advisory notes.

### Why critical-deficiency safety is structural

The QA_PASS and REMEDIATE branches are reached **only when no critical check has
fired** — rule 1 consumes every case with a fired critical check. A file with an
unsupported disposition, a contradicted disposition, a missed escalation
trigger, a missing mandatory element, or a no-finding closure over unreviewed
scope therefore cannot pass QA regardless of its score. The validation harness
enforces this as a build gate: every planted critical deficiency must be
detected by its named check (deficiency recall floor 1.0) and zero
critical-deficient cases may receive QA_PASS; any violation exits non-zero.

---

## 7. Tunable constants

All in `scorer.Config` and the named module constants; defaults are the
conservative posture. Recalibration procedure in [`tuning.md`](tuning.md).

| Constant | Default | Effect |
|---|---|---|
| `pass_score` | 85.0 | Quality score required for QA_PASS (after the critical/major gates). |
| `sla_material_multiple` | 1.5 | SLA overrun beyond this multiple is a MAJOR breach. |
| `DIM_WEIGHTS` | see section 3 | Relative importance of the five dimensions. |
| `DEDUCTION` | 100 / 45 / 15 | Per-check deduction by severity class. |
| `SLA_DAYS` / `MIN_LOOKBACK_DAYS` | per case type | The policy tables the timeliness and completeness checks test against. |

Reclassifying a check's severity (the `SEVERITY_CLASS` table) is the most
consequential change: demoting a CRITICAL check removes it from the no-pass
gate and is the move that introduces false passes.

---

## 8. Governance and boundaries

Mapped to public guidance — SR 11-7 / OCC 2011-12 and the FFIEC BSA/AML
Examination Manual's expectations for investigation documentation and
independent review — per the shared [`../GOVERNANCE.md`](../GOVERNANCE.md).
Conceptual soundness: every check, weight, and gate is documented here and
readable in `scorer.py`. Outcomes analysis: the committed evidence pack, with
the deficiency-recall floor enforced as a build gate. Ongoing monitoring: the
multi-seed stability runs and the recalibration cadence in `tuning.md`.

Limitations, stated plainly: the engine grades structured metadata about the
file, not the prose — narrative checks are structural, and judging analytical
quality remains a human QA skill the engine routes to rather than replaces. The
policy tables and severity calibration are illustrative and must be rebuilt
from the deploying institution's procedures and labelled QA outcomes. The
engine grades and routes; reopening a case, changing an investigative
disposition, and any filing decision are documented human actions — QA_PASS
releases a file from the structural gate with its basis recorded, it does not
approve the underlying investigative judgement.
