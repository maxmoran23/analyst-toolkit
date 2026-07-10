# Data-Quality Rules Framework — CDE fitness for screening

A runnable, deterministic engine that answers the data-governance team's
recurring question about any customer extract feeding financial-crime systems:
**"is this feed fit to screen against?"** Named data-quality rules across five
dimensions, a field-level scorecard for the critical data elements (CDEs), a
record-level defect list, and a feed disposition with a hard gate — plus
reproducible evidence that it catches every planted critical defect and never
passes a feed that breaches a screening-critical threshold.

> **In plain terms:** Sanctions screening, transaction monitoring, and
> regulatory reporting are only as good as the name, date-of-birth, country,
> and ID-number fields they are fed. If names are blank, dates are impossible,
> country codes are wrong, or one person exists as two records, downstream
> systems quietly miss things. This engine reads a customer file the way an
> inspector reads a shipment: it checks every record against named rules
> (is the mandatory field there? is the date a real date? is the country code
> on the approved list? does the ID's check digit verify? is this record a
> duplicate of another?), grades each critical field, and then issues one of
> three verdicts for the whole file — pass it to screening, send it for
> investigation, or block it. A file with too many broken critical fields can
> never pass, no matter how good everything else looks. On a 50,000-record
> test it caught every one of 2,750 planted critical defects while raising
> zero false alarms on clean records.

---

## What it produces

Per **record**, a defect list — each entry a named rule with dimension, the
CDE it binds to, severity (CRITICAL / MINOR), and a human-readable detail
string for the remediation queue. Per **feed**, a disposition:

- **FEED_PASS** — granted only on a provable named cause: every documented
  threshold met (screening-critical CDEs at or below the warn margin,
  supporting CDEs within ceilings, staleness within policy, composite score
  at or above the floor), listed in the reason.
- **INVESTIGATE** — named causes: a screening-critical CDE in the warn band,
  a supporting CDE over its ceiling, or the composite below the floor.
- **BLOCK_FEED_TO_SCREENING** — any screening-critical CDE over its documented
  ceiling. A hard gate, not a weight: a breached feed can never be FEED_PASS.
  The feed and its full defect list route to data-governance review; the
  engine never drops or silently repairs a record.

Five dimensions of named rules: **COMPLETENESS** (blank mandatory fields),
**VALIDITY** (strict date parse, approved country reference set, identifier
check-digit contract), **CONSISTENCY** (country vs account prefix, DOB vs
onboarding-date ordering, entity type vs field expectations), **UNIQUENESS**
(exact and transliterated near-duplicates on a shared identifier, via
`_lib/match`), **TIMELINESS** (refresh beyond the policy horizon).

## Validation result (seed 42, 50,000 records — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| Recall on planted critical defects (safety) | **1.0000 — 0 of 2,750 missed** |
| False-flag rate on clean records | **0.0000%** (0 of 42,250, incl. 3,000 adversarial-benign edges) |
| Per-dimension pass rates (main feed) | completeness 94.7% · validity 97.2% · consistency 97.6% · uniqueness 99.0% · timeliness 96.0% |
| Feed dispositions | contaminated main feed **BLOCK** (5 screening-critical breaches) · clean feed **FEED_PASS** · warn-band and degraded feeds **INVESTIGATE** — all 5 scenarios as expected |
| Near-duplicate detection | deployed detector recall 1.0; similarity-only alternative leaks to 0.88 at the same 0.85 threshold (see sweep) |
| Stability | recall 1.0000 and false-flag 0.0000% across 7 seeds (42-48); all scenario dispositions identical |
| Scale | 200,000 records + 5 scenario feeds in ~8s |

The zero false-flag rate is structural, not luck: every rule is a
deterministic parser or reference-set check, and the clean population includes
adversarial-benign records (accented and hyphenated names, leap-day and
boundary DOBs, refresh just inside the horizon) built to trip a sloppy engine.

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --records 50000
python3 run_validation.py          --seed 42 --records 50000
```

`run_validation.py` regenerates the extract in-memory (plus five
feed-disposition scenario feeds), scores everything, writes the evidence pack,
and **exits non-zero if any planted critical defect goes undetected, if any
feed with a planted screening-critical breach receives FEED_PASS, or if the
scenario grid deviates from its expected outcomes**. Optional: `--trials 6`,
`--records 200000`.

Ad-hoc single check: `python3 scorer.py` (runs a built-in three-record example
with a transliterated duplicate pair and a drifted country code).

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — CDE inventory, rules, thresholds, disposition logic, governance. |
| [`scorer.py`](scorer.py) | The deterministic engine (pure stdlib + `../_lib/`). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded, labelled, scalable synthetic extract with adversarial plants. |
| [`run_validation.py`](run_validation.py) | The validation harness; evidence pack; safety gates. |
| [`tuning.md`](tuning.md) | Recalibration for a real environment. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Copilot Studio / Power Platform mapping. |
| [`evidence/`](evidence/) | Committed real-run output. |

## Standing caveat

A transparent **reference implementation** for auditability, not a production
control. A real deployment recalibrates the ceilings, reference sets, and the
similarity threshold against its own profiled extracts; the scoring contract
in `METHODOLOGY.md` is what travels. All data synthetic; entities fictional
(the recurring institution is Harborview Financial Group). Nothing here
assesses any real customer record.
