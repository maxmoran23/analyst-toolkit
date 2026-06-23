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
