# Tuning — Jurisdiction-Risk Framework

The engine ships with illustrative weights and bands. A deployment calibrates them to
its own geographic-risk methodology and risk appetite. Everything tunable is in
[`scorer.py`](scorer.py); nothing is hidden.

## What to calibrate

| Knob | Where | Guidance |
|---|---|---|
| **Dimension weights** | `WEIGHTS` in `scorer.py` | Relative importances; the composite renormalizes them, so they need not sum to 1. Raise AML/CFT and secrecy for a correspondent-banking book; raise organized crime / instability for cash- or corridor-heavy exposure. Re-run `run_validation.py` — discrimination and monotonicity must still pass. |
| **Tier bands** | `Config.med_band / high_band / crit_band` | Move the 40 / 60 / 80 cutoffs to match your firm's LOW/MEDIUM/HIGH/CRITICAL definitions. Wider CRITICAL band = fewer CRITICAL ratings; validate the resulting distribution against your appetite. |
| **Floor mapping** | `_floors()` in `scorer.py` | Which designations force which floor. Do not weaken a floor below its regulatory basis (a comprehensive sanctions program below CRITICAL, a FATF listing below HIGH) — the floor-safety gate exists to catch exactly that. |
| **Dimension set** | `WEIGHTS` + `dimension_scores()` | Add or drop a dimension (e.g. add a drug-trafficking index) by adding its weight and its normalization. The monotonicity test covers whatever dimensions `WEIGHTS` names. |
| **Normalization** | `dimension_scores()` | If your source uses a different scale (a rank rather than a score, a different secrecy range), change the conversion here and document it in `METHODOLOGY.md`. |

## The rule that cannot be tuned away

The floor-safety gate is a build gate: `run_validation.py` exits non-zero if any
hard-designated jurisdiction is rated below its mandated floor. You can move weights and
bands freely; you cannot ship a calibration that rates a sanctioned or FATF-black-listed
jurisdiction below CRITICAL, or a grey/EU/INCSR jurisdiction below HIGH. Re-run the
harness after every change and keep it green.

## Recalibration workflow

1. Change a weight, band, or floor.
2. `python3 run_validation.py --trials 5` — confirm discrimination, floor safety, and
   monotonicity hold across seeds.
3. Inspect the tier distribution against your risk appetite (too many CRITICAL? widen
   the band or re-weight — do not weaken a floor).
4. Regenerate the evidence pack (`python3 run_validation.py`) and commit it so the
   committed numbers match the calibration.
