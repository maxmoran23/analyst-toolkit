# Deployment notes — Jurisdiction-Risk Framework

This is a reference engine, not a turnkey control. The notes below map its pure-stdlib
core onto a Microsoft-stack deployment; the same shape applies to any host.

## What travels

The **scoring contract** — the seven dimensions, their normalization, the weighting, the
tier bands, and the hard-risk floors ([`METHODOLOGY.md`](METHODOLOGY.md)) — is the
durable artifact. `scorer.py` is its executable reference; a deployment re-implements the
same contract in its own runtime and validates it the same way (discrimination, floor
safety, monotonicity).

## Copilot Studio / Power Platform mapping

| Engine element | Deployment analogue |
|---|---|
| `Jurisdiction` inputs (raw index values + designations) | A Dataverse table row, or the fields a flow pulls from your country-risk source of record |
| `dimension_scores()` normalization | A Power Fx / plugin transform, or a pre-computed column per index |
| `WEIGHTS` + `score_features()` | The composite calculation (Power Fx, a plugin, or an Azure Function) |
| `_floors()` overrides | A rules step that reads the current FATF/EU/INCSR/sanctions designations and applies the floor |
| `run_validation.py` gates | A test suite in CI that re-runs the discrimination / floor-safety / monotonicity checks on every change to the weights or floors |

## Non-negotiables in any deployment

- **Refresh the designations.** FATF, EU, INCSR, and sanctions statuses are the floors;
  a deployment must pull the current designation from the authoritative source
  ([`SOURCE-LIBRARY.md`](SOURCE-LIBRARY.md)), not a cached value.
- **Keep the floor gate.** Whatever the calibration, no sanctioned or FATF-black-listed
  jurisdiction may be rated below CRITICAL, and no grey/EU/INCSR jurisdiction below HIGH.
  Enforce it as a test, not a convention.
- **Human decision.** The engine rates; the market/onboarding decision and any override
  are documented human actions.
