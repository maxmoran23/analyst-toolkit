# Validation Report — Investigations Case-File QA Framework

> ILLUSTRATIVE / SYNTHETIC. Every figure is produced by running the reference QA engine over a seeded, fully synthetic population of investigation case files. No real case, customer, or institution is represented. Numbers are emitted by `run_validation.py`, not authored; re-run it to reproduce them.

**Run:** seed `42` · 50,000 case files · git `7e2eb3f` · 2026-07-09 22:01 UTC

**Headline:** critical-deficiency recall **1.0000** (8,996 of 8,996 planted critical deficiencies detected), critical-deficient cases passed QA: **0**, clean-case pass rate **100.0%** (false-flag burden on clean files: 0.0%).

## 1. Methodology summary
The engine grades each completed investigation case file against 13 named QA checks across five dimensions (completeness, evidence support, consistency, timeliness, narrative quality), producing a weighted 0-100 quality score and a QA disposition: QA_PASS, REMEDIATE, or REWORK_AND_ESCALATE. ANY critical deficiency — an unsupported disposition, a disposition contradicting the evidence, a missed escalation trigger, a missing mandatory element, or a no-finding closure over unreviewed scope — makes QA_PASS structurally unreachable regardless of score. The engine grades the file and routes it; it never reopens or re-decides the investigation. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
50,000 completed case files: ~55% clean, ~15% minor-issue, ~12% major-issue, and ~18% adversarial critical plants across five types. Each plant is an otherwise-pristine, well-scored file hiding exactly one critical defect (a fully-cited-looking file whose rationale cites no evidence, a corroborated typology closed as no-finding, escalation-trigger facts closed as normal, a missing mandatory element, a clearance over unreviewed scope) — the cases designed to defeat a score-only policy. Labels and categories are assigned by construction, never by the engine.

## 3. Operating-point results
- **Critical-deficiency recall (planted defects detected): 1.0000** — missed: 0
- **Critical-deficient cases receiving QA_PASS: 0** (ceiling: 0)
- Confusion (positive = critical-deficient, predicted = REWORK_AND_ESCALATE) — TP 8,996 · FP 0 · TN 41,004 · FN 0 · recall 1.0000 · precision 1.0000
- Non-critical cases over-escalated to REWORK_AND_ESCALATE: 0

| QA disposition | Count | Share |
| --- | --- | --- |
| QA_PASS | 35,070 | 70.1% |
| REMEDIATE | 5,934 | 11.9% |
| REWORK_AND_ESCALATE | 8,996 | 18.0% |

## 4. Per-category outcomes
Did each construction category land where designed? Clean files should pass; minor-issue files pass with advisory notes; major-issue files are remediated (never reworked as critical); every plant type is reworked. Note the plants' mean scores — they are well-scored files, which is exactly why the no-pass gate is a named check, not a score threshold.

| category | count | mean_score | QA_PASS | REMEDIATE | REWORK_AND_ESCALATE |
| --- | --- | --- | --- | --- | --- |
| clean | 27636 | 100.0 | 27636 | 0 | 0 |
| minor_findings | 7434 | 95.91 | 7434 | 0 | 0 |
| major_findings | 5934 | 87.24 | 0 | 5934 | 0 |
| plant_uncited_disposition | 1805 | 75.0 | 0 | 0 | 1805 |
| plant_hidden_contradiction | 1784 | 79.06 | 0 | 0 | 1784 |
| plant_missed_escalation | 1766 | 79.04 | 0 | 0 | 1766 |
| plant_missing_mandatory | 1768 | 74.02 | 0 | 0 | 1768 |
| plant_unreviewed_scope | 1873 | 75.0 | 0 | 0 | 1873 |

## 5. Threshold-sensitivity analysis
A naive policy that granted QA_PASS on `quality_score >= T` alone, for comparison. No threshold separates the population: every T at or below the plants' scores leaks critical-deficient files, and every T above them still passes major-deficient files or starts failing clean/minor files. The deployed policy does not pass on score — QA_PASS requires every critical and major check provably clean — so critical leakage is 0 by construction.

| threshold | naive_pass_count | critical_deficient_passed | major_deficient_passed | clean_or_minor_failed | clean_or_minor_failed_rate |
| --- | --- | --- | --- | --- | --- |
| 50 | 50000 | 8996 | 5934 | 0 | 0.0 |
| 55 | 50000 | 8996 | 5934 | 0 | 0.0 |
| 60 | 50000 | 8996 | 5934 | 0 | 0.0 |
| 65 | 50000 | 8996 | 5934 | 0 | 0.0 |
| 70 | 50000 | 8996 | 5934 | 0 | 0.0 |
| 75 | 49537 | 8533 | 5934 | 0 | 0.0 |
| 80 | 42778 | 2649 | 5059 | 0 | 0.0 |
| 85 | 38947 | 0 | 3877 | 0 | 0.0 |
| 90 | 37510 | 0 | 2440 | 0 | 0.0 |
| 95 | 33224 | 0 | 595 | 2441 | 0.0696 |
| 100 | 27636 | 0 | 0 | 7434 | 0.212 |

## 6. Critical-deficiency safety argument
1. Of 8,996 planted critical deficiencies, **8,996 were detected** by their named check (recall 1.0000) and **0 critical-deficient cases received QA_PASS**.
2. Safety is structural: the QA_PASS branch of the disposition logic is reachable only when zero critical checks have fired. A case with an unsupported disposition, a contradiction, a missed escalation trigger, a missing mandatory element, or a no-finding closure over unreviewed scope therefore cannot pass QA regardless of its quality score.
3. Enforced as a build gate — `run_validation.py` exits non-zero if any planted critical deficiency goes undetected or any critical-deficient case passes QA.

## 7. Volume / QA-burden impact
50,000 case files → 35,070 released with a named pass basis (70.1%) → 5,934 returned for targeted remediation → 8,996 reworked and escalated to the investigations supervisor. Clean-file pass rate 100.0% — the QA queue's human effort concentrates on genuinely deficient files.

## 8. Limitations
- The case record is structured metadata about the file (presence, counts, citations, flags, milestones), not the prose itself. The narrative checks are structural (chronology present, 5W field coverage, no empty mandatory fields); judging the analytical quality of the written narrative remains a human QA skill this engine routes to, not one it replaces.
- The policy tables (SLAs, minimum lookbacks, mandatory elements) are illustrative. A deployment substitutes its own procedures manual and recalibrates the dimension weights and deductions against a labelled sample of its own QA outcomes (`tuning.md`).
- The engine grades files and routes them; reopening a case, changing its disposition, or any filing decision is a documented human action.
- This is a transparent reference implementation, not a production control.

## 9. Reproduction
```bash
python3 run_validation.py --seed 42 --cases 50000
```
Same seed → identical population → identical metrics.
