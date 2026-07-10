# Tuning — recalibrating the QA operating point

The defaults in `scorer.Config`, the severity classification, and the policy
tables in `scorer.py` are a conservative posture validated on synthetic data —
a **starting point, not a production calibration**. Recalibrate against a
labelled sample of your own QA outcomes before relying on the engine, and
record every change.

> **In plain terms:** The settings below control which findings send a file
> back versus letting it pass with a note, and what the deadlines and lookback
> rules are. Set them from your own procedures manual and from files your QA
> team has already reviewed: the engine should agree with your reviewers on
> what is serious, and it must never pass a file your reviewers would have
> rejected outright.

## The three layers of dials

**Policy tables (what the checks test against — align to your procedures first):**

| Table | Where | Effect |
|---|---|---|
| `SLA_DAYS` | `scorer.py` | Per-case-type completion SLA the timeliness checks use. |
| `MIN_LOOKBACK_DAYS` | `scorer.py` | Per-case-type minimum review lookback. |
| Mandatory elements | `_missing_mandatory` | Which absences constitute the CRITICAL completeness defect. |

**Severity classification (the most consequential):** `SEVERITY_CLASS` decides
which checks sit inside the no-pass gate. Promoting a check to CRITICAL widens
the gate (more files reworked); demoting one removes it from the gate and is
the move that introduces false passes — treat any demotion as a model change
requiring re-validation on a labelled sample.

**Config (the operating point):**

| Constant | Default | Raise it → |
|---|---|---|
| `pass_score` | 85.0 | more minor-laden files held for remediation instead of passing with notes |
| `sla_material_multiple` | 1.5 | more SLA overruns treated as minor rather than major |
| `DIM_WEIGHTS` | 0.25/0.25/0.20/0.20/0.10 | shift which dimensions drive the score (ranking and reporting only — never the gate) |
| `DEDUCTION` | 100/45/15 | how hard each severity class hits the score |

## Calibrate against your own QA history

The single most important production step: assemble a labelled sample of case
files your QA team has already reviewed, with each reviewer finding classified
critical / major / minor under your own policy. That sample — not this
repository's synthetic population — defines what the checks should fire on and
where the pass threshold sits.

## Procedure

1. Assemble the labelled QA sample (reviewer disposition + classified findings).
   This is your ground truth.
2. Align the policy tables to your procedures manual exactly — SLAs, lookbacks,
   mandatory elements, escalation triggers. Mismatched policy tables produce
   noise findings that erode reviewer trust.
3. Run the engine over the sample. Reconcile every disagreement: an engine pass
   your reviewers failed for a structural reason is a gate gap (fix the check
   or its classification); an engine rework your reviewers passed is a
   false-flag cost (tighten the check's firing condition).
4. Confirm the safety property on your sample: zero reviewer-rejected files
   receive QA_PASS. This is your equivalent of the harness gate; a
   configuration that violates it is rejected.
5. Pick `pass_score` so the pass-with-notes band matches your risk appetite for
   advisory-only findings.
6. Record the constant changed, old/new values, the labelled-sample result
   before and after, and the rationale — the model-change-management evidence.

## What not to do

- Do not demote a CRITICAL check to cut the rework rate without re-running the
  safety confirmation on your labelled sample — that is the move that lets
  indefensible files through.
- Do not pass files on `quality_score` alone. QA_PASS requires every critical
  and major check provably clean; a pass justified only by a high score does
  not survive an exam.
- Do not treat the synthetic policy tables as production policy — derive them
  from your procedures manual, and keep them synchronized when the manual
  changes (a stale SLA table silently mis-grades timeliness).
- Do not let the engine's pass substitute for the judgement half of QA —
  sampling passed files for human analytical review remains part of the
  program.
