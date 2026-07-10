# QA / Independent-Testing Attribute-Sampling Framework

A runnable, deterministic engine for statistical attribute sampling in tests of
controls — plan the sample from exact probability mathematics, select it
reproducibly from seed, and evaluate the deviations found into an exact
statistical conclusion. The lookup tables and spreadsheet folklore this work is
usually done from are discretized snapshots of exact tail statements; this
engine computes the statements themselves.

> **In plain terms:** When a tester checks whether a control works — "did the
> branch verify every wire callback?" — they can't look at all 40,000 cases, so
> they test a sample. Three questions decide everything: how many items to test,
> which ones, and what the deviations found actually prove. Today those answers
> come from printed tables and habit. This tool computes them exactly: the
> smallest sample that gives the required confidence, a random selection anyone
> can reproduce from the seed, and the precise worst-case deviation rate the
> sample supports. It never grades the control itself — it hands the tester the
> exact statistical statement and the tester owns the call.

---

## What it produces

Per control, a `SamplingPlan` (exact sample size, acceptance number, achieved
risk of over-reliance), a `Selection` (seeded, optionally stratified, with the
selection log), and an `Evaluation`: the exact one-sided upper deviation limit
(UDL) at the stated confidence and a named-rule conclusion —
CONTROL_EFFECTIVE, INCONCLUSIVE (with exact expand-sample guidance), or
CONTROL_INEFFECTIVE — routed to the tester with the full statistical statement.

## Validation result (seed 42, 12 controls, 480,000 items — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| UDL cross-check vs independent brute-force exact recomputation | **max abs divergence 5.394e-12** over 119 cases (tolerance 1e-9, 0 integer mismatches) |
| Structural gate (deviations > acceptance number can never conclude EFFECTIVE) | **0 breaches** across 312 evaluations |
| Planted-deviation gate (fully-deviant stratum the sample cannot miss) | **0** EFFECTIVE conclusions across main run + 150 replicate draws |
| Measured false-assurance (populations at 2-3x the tolerable rate) | **0/150** replicate samples concluded EFFECTIVE (design risk 5%) |
| Sample-size solver monotonicity | **0 violations** across the 40-cell (confidence x tolerable) grid; finite-population plan never exceeds binomial |
| Stability | All gates pass across 6 additional seeds (max divergence 6.886e-12) |
| Scale | 480,000 items, 312 evaluations in ~0.5s |

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --controls 12 --population 40000
python3 run_validation.py          --seed 42 --controls 12 --population 40000
```

`run_validation.py` regenerates the control populations in-memory, runs
plan-select-evaluate plus replicate and cross-check measurements, writes the
evidence pack, and **exits non-zero if any gate is breached: a structural
over-acceptance EFFECTIVE, a planted control passed, measured false-assurance
above the design risk, a UDL cross-check divergence, or a solver monotonicity
violation**. Optional: `--trials 6` (every trial seed is gated), `--no-write`.

Ad-hoc: `python3 engine.py` plans, selects, and evaluates one example control.

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — exact solver, selection, UDL, named rules in firing order, governance. |
| [`engine.py`](engine.py) | The deterministic plan-select-evaluate engine (a thin layer over `../_lib/sampling.py`). |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded controls + labelled item populations across designed scenarios, including the planted adversarial case. |
| [`run_validation.py`](run_validation.py) | Validation harness + evidence; four build gates including the independent UDL cross-check. |
| [`tuning.md`](tuning.md) · [`DEPLOYMENT.md`](DEPLOYMENT.md) · [`evidence/`](evidence/) | Recalibration · Copilot mapping · committed run output. |

## Standing caveat

A transparent **reference implementation** for auditability, not a production
control. Confidence, tolerable deviation rate, and expected deviation rate are
policy choices set from the institution's risk appetite, not model outputs. The
engine quantifies sampling risk only — non-sampling risk (a tester misreading an
item) is managed by review, not by sample size. A real deployment recalibrates
these parameters against its own testing standards; the scoring contract in
`METHODOLOGY.md` is what travels. All data synthetic; the institution is the
fictional Harborview Financial Group. Nothing here tests a real control.
