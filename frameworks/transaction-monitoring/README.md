# Transaction-Monitoring Alert-Scoring Framework

A runnable, deterministic engine that triages transaction-monitoring alerts: it
auto-closes the alerts it can prove are benign, ranks the rest for analysts, and
escalates the recognised laundering patterns — with reproducible evidence that it
never auto-closes genuinely suspicious activity.

> **In plain terms:** Monitoring systems bury analysts in alerts, most of which are
> ordinary customers doing ordinary things that happen to trip a rule. This engine
> reads each alert against what's normal *for that customer* and what their
> documented business explains, and clears the provable false positives — but only
> with a written reason and only when there's no laundering pattern present.
> Anything showing a real pattern (structuring, funnel accounts, money passing
> straight through) is kept and escalated; it never closes a real pattern and never
> files a SAR. On a 50,000-alert test it cut the human queue ~82% while missing zero
> suspicious cases.

---

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | Transaction-monitoring analysts and the investigations team receiving their escalations. |
| **The question it answers** | Which monitoring alerts are worth an analyst's time, and which can be closed with a documented reason? |
| **What it is** | A small, transparent, runnable scoring engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never auto-closes a recognised laundering pattern and never files a SAR. Every escalate/close decision is a human one. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/transaction-monitoring
python3 run_validation.py --seed 42 --customers 5000 --alerts 50000
```

Pure Python standard library: nothing to install, no network access, well under a second. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read "recall 1.0000" on this page

The engine missed **none** of the 2,052 truly suspicious alerts planted in the test population. Read that the way you would read an attribute sample that came back with zero exceptions: you do not conclude the deviation rate is zero — you conclude it is **below 0.15% at 95% confidence**. That exact one-sided bound is published for every engine in [`../EVIDENCE.md`](../EVIDENCE.md), and it tightens only by testing more true cases. It is a property of this synthetic population, not a forecast about live data.

<!-- /STANDALONE-BRIEF -->

## What it produces

Per alert (a customer + a window of aggregated transaction features), a disposition:

- **AUTO_CLOSE** — a provable benign alert, with a named cause: within-profile,
  documented-context, or below-typology-threshold. Never closes a typology hit.
- **ANALYST_REVIEW** — kept open, priority HIGH / MEDIUM / LOW. Includes emerging
  typology patterns and unexplained deviations.
- **ESCALATE** — a clear laundering typology, routed to investigation for a SAR
  decision. Never auto-files.

Every disposition carries a named reason and a component breakdown. The engine
scores and routes; the SAR decision stays human.

## Validation result (seed 42, 50,000 alerts — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| Recall on suspicious activity (false-negative safety) | **1.0000 — 0 false negatives** |
| False-positive reduction | **85.1%** |
| Human review-volume cut | **81.7%** (50,000 → 9,175 to a human) |
| Analyst queue precision lift | **4.1% → 22.4%** suspicious hit rate (~5.5×) |
| Stability | recall 1.0 across 6 seeds; FP-reduction 84.7–85.3% |
| Scale | 200,000 alerts in ~2.6s |

Per-category close rate: within_profile 100% · documented_context 100% ·
below_typology 100% · ambiguous_residual 0% (the irreducible band a human must
work). FP-reduction is lower than name screening's by design — behavioural alerts
have a larger genuinely-ambiguous band, which the engine correctly leaves open
rather than clearing.

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --customers 5000 --alerts 50000
python3 run_validation.py          --seed 42 --customers 5000 --alerts 50000
```

`run_validation.py` regenerates the population in-memory, scores it, writes the
evidence pack, and **exits non-zero if any suspicious alert is auto-closed** (the
false-negative safety gate). Optional: `--trials 5`, `--alerts 200000`.

Ad-hoc single check: `python3 scorer.py` (runs a built-in structuring example).

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — rules, thresholds, disposition logic, governance. |
| [`scorer.py`](scorer.py) | The deterministic engine (pure stdlib + `../_lib/`). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded, labelled, scalable synthetic population. |
| [`run_validation.py`](run_validation.py) | The validation harness; evidence pack; FN-safety gate. |
| [`tuning.md`](tuning.md) | Recalibration for a real environment. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Copilot Studio / Power Platform mapping. |
| [`evidence/`](evidence/) | Committed real-run output. |

## Standing caveat

A transparent **reference implementation** for auditability, not a production
control. A real deployment recalibrates the rule thresholds and operating point
against its own labelled alert history; the scoring contract in `METHODOLOGY.md` is
what travels. All data synthetic; entities fictional. Nothing here monitors any
real customer.
