# Investigations Case-File QA Framework

A runnable, deterministic engine for second-line quality assurance of completed
financial-crime investigation case files: it grades each file against named
structural checks, passes the provably clean ones with a written basis, returns
correctable files for remediation, and sends every critically deficient file
back for rework — with reproducible evidence that a critically deficient file
can never pass QA.

> **In plain terms:** Before an investigation file is closed for good, a second
> pair of eyes checks the work: did the investigator look at everything they were
> supposed to, does the evidence actually back up the conclusion, does the
> conclusion match what the evidence shows, was it done on time, and is the
> write-up complete? This engine does the structural half of that review. It
> passes a file only when it can name exactly why the file is clean, and it has
> one unbreakable rule: a file with a serious defect — a conclusion no evidence
> supports, a conclusion that contradicts the evidence, a red flag that should
> have been escalated but wasn't, a required section missing — can never pass, no
> matter how polished the rest of the file looks. On a 50,000-file test it caught
> every one of 8,996 planted serious defects and passed zero of those files,
> while passing 100% of the genuinely clean ones.

---

## What it produces

Per completed case file (a structured record of scope, evidence, disposition
rationale, timeline, escalation posture, and narrative structure), a QA review:

- **QA_PASS** — granted only on a provable named basis: every critical and major
  check demonstrably clean. Minor observations ride along as advisory notes.
- **REMEDIATE** — correctable major/minor deficiencies, returned to the
  investigator with each finding named. No critical deficiency present.
- **REWORK_AND_ESCALATE** — at least one critical deficiency; the file goes back
  for rework and the QA finding is routed to the investigations supervisor.

Every review carries a weighted 0-100 quality score, per-dimension sub-scores,
and the named deficiencies. The engine grades the file and routes it; it never
reopens a case, changes an investigative disposition, or makes a filing decision.

## Validation result (seed 42, 50,000 case files — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| Critical-deficiency recall (planted defects detected) | **1.0000 — 8,996 of 8,996** |
| Critical-deficient cases passed QA | **0** |
| Clean-case pass rate (false-flag burden) | **100.0%** (0.0% false-flag) |
| Non-critical files over-escalated to rework | **0** (rework-queue precision 1.0000) |
| Disposition funnel | QA_PASS 70.1% · REMEDIATE 11.9% · REWORK_AND_ESCALATE 18.0% |
| Stability | recall 1.0000, 0 critical passes across 6 additional seeds |
| Scale | 200,000 case files in ~4s |

The adversarial plants are the point: each is an otherwise-pristine file hiding
exactly one critical defect, and they score 74-79 on the quality composite —
well-scored files a score-only policy would eventually pass. The threshold sweep
in the evidence pack shows no score threshold separates them cleanly; the named
checks do.

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --cases 50000
python3 run_validation.py          --seed 42 --cases 50000
```

`run_validation.py` regenerates the population in-memory, reviews it, writes the
evidence pack, and **exits non-zero if any planted critical deficiency goes
undetected or any critical-deficient case passes QA** (the safety gate).
Optional: `--trials 6`, `--cases 200000`.

Ad-hoc single check: `python3 scorer.py` (reviews a clean file and a
hidden-contradiction file).

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — checks, severities, weights, disposition logic, governance. |
| [`scorer.py`](scorer.py) | The deterministic QA engine (pure stdlib + `../_lib/`). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded, labelled, scalable synthetic case-file population with adversarial plants. |
| [`run_validation.py`](run_validation.py) | The validation harness; evidence pack; critical-deficiency safety gate. |
| [`tuning.md`](tuning.md) | Recalibration for a real environment. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Copilot Studio / Power Platform mapping. |
| [`evidence/`](evidence/) | Committed real-run output. |

## Standing caveat

A transparent **reference implementation** for auditability, not a production
control. The policy tables (SLAs, minimum lookbacks, mandatory elements) and the
severity weights are illustrative — a real deployment substitutes its own
procedures manual and recalibrates against a labelled sample of its own QA
outcomes; the scoring contract in `METHODOLOGY.md` is what travels. All data
synthetic; entities fictional. Nothing here reviews any real investigation.
