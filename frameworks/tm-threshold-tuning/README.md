# Transaction-Monitoring Threshold-Tuning Framework

A runnable, deterministic engine that runs above/below-the-line (ATL/BTL) testing on
monitoring rules and recommends thresholds — cutting unproductive alert volume only
where detection of suspicious activity stays above a required floor, and lowering any
rule that currently leaks suspicious activity below the line.

> **In plain terms:** Every monitoring rule has a threshold that decides what gets
> alerted. Too low buries analysts in junk; too high lets real risk slip past. This
> tool tests each rule both ways — how many of its alerts are worth working, and how
> much suspicious activity it's missing — and recommends the highest threshold that
> still catches the required share of suspicious activity. It answers the examiner's
> question directly: "is the line in the right place, and how do you know?" It is the
> model-validation framework of the set — it tunes the rules the other frameworks
> would score against.

---

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | Transaction-monitoring rule owners and the model-validation function that must challenge them. |
| **The question it answers** | Is this rule's threshold in the right place, and how do you know? |
| **What it is** | A small, transparent, runnable threshold-testing and recommendation engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never changes a live rule. It recommends a threshold with the evidence behind it, and it will never recommend one that pushes detection of suspicious activity below the required floor. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/tm-threshold-tuning
python3 run_validation.py --seed 42 --rules 12 --population 40000
```

Pure Python standard library: nothing to install, no network access, about a second. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read the result on this page

The claim here is a floor, not an accuracy figure: **every recommended threshold still detects at least 95% of the suspicious activity**, and the run fails if any recommendation would push a rule below that line. Rules that currently leak suspicious activity below the line are recommended *down*, never up.

<!-- /STANDALONE-BRIEF -->

## What it produces

Per rule, a `TuningResult`: an action (RAISE / LOWER / KEEP), the current and
recommended thresholds, the ATL/BTL stats at each (alert volume, productivity,
detection rate, BTL-missed), the full threshold sweep, and a reason.

## Validation result (seed 42, 12 rules, 480,000 observations — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| Below-the-line safety (min recommended detection) | **0.9506 — above the 95% floor** |
| Leaking rules remediated | **6 / 6** (every too-high rule recommended down) |
| Recommendation-direction accuracy | **100%** (RAISE / LOWER / KEEP vs designed scenario) |
| Alert-volume reduction (over-alerting rules) | **66.6%** (121,969 → 40,700) at detection ≥ floor |
| Stability | 100% accuracy, min detection ≈ 0.95 across 6 seeds |
| Scale | 1.2M observations in ~3s |

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --rules 12 --population 40000
python3 run_validation.py          --seed 42 --rules 12 --population 40000
```

`run_validation.py` regenerates the rule populations in-memory, tunes each rule,
writes the evidence pack, and **exits non-zero if any recommendation detects below
the recall floor, or any leaking rule is not remediated**. Optional: `--trials 5`,
`--population 100000` (~1.2M observations).

Ad-hoc: `python3 engine.py` tunes one example rule.

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — ATL/BTL testing, tuning logic, governance. |
| [`engine.py`](engine.py) | The deterministic tuning engine (a thin layer over `../_lib/metrics.sweep`). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded rules + labelled populations across designed scenarios. |
| [`run_validation.py`](run_validation.py) | Validation harness + evidence; below-the-line safety gate. |
| [`tuning.md`](tuning.md) · [`DEPLOYMENT.md`](DEPLOYMENT.md) · [`evidence/`](evidence/) | Recalibration · Copilot mapping · committed run output. |

## Standing caveat

A transparent **reference implementation** for auditability, not a production
control. The `recall_floor` is a policy choice set from your risk appetite, not a
model output. The "suspicious" label in real tuning is a historical disposition with
its own error rate. A recommended threshold change is a governed model-change
decision a human approves and documents. All data synthetic; nothing here tunes a
real rule.
