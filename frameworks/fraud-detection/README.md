# Fraud-Detection Transaction and Session Triage

> **In plain terms:** This small, transparent engine separates trusted sessions
> from events that need stronger authentication or human fraud review. It treats
> both kinds of customer harm as safety failures: approving confirmed fraud and
> hard-declining legitimate activity. It recommends a route; it never executes a
> block, decline, freeze, filing, or customer action.

This pure-Python-standard-library reference implementation is for fraud strategy,
fraud operations, independent validation, and control owners who need an explicit
decision trail. Every hard outcome names a fired typology and corroborating causes.
`APPROVE` is permitted only for `trusted_session_continuity` when no fraud rule
fired. A score ranks evidence; it never makes a hard decision by itself.

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | Fraud-strategy, fraud-operations, independent-validation, and control teams. |
| **The question it answers** | Which transaction or session can be approved on a named trusted-continuity cause, and which requires stronger authentication or human review? |
| **What it is** | A small, transparent, runnable scoring and triage engine. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never executes a decline, block, freeze, filing, or customer action. Hard recommendations require a named fired fraud rule and corroborating causes; a score alone never decides. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/fraud-detection
python3 run_validation.py --seed 42 --transactions 50000 --trials 6
```

Pure Python standard library: nothing to install, no network access, a few seconds. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read the result on this page

The symmetric claim has two gates: zero confirmed-fraud events may receive APPROVE, and zero legitimate events may receive a hard disposition. Each zero count must also place its exact one-sided 95% upper failure-rate bound at or below 0.1%.

<!-- /STANDALONE-BRIEF -->

## What it returns

- `APPROVE` — named, provable trusted-session continuity only.
- `STEP_UP_AUTH` — context is not trusted, but the hard-decision evidence contract
  is not met. Step-up is excluded from the false-decline definition.
- `DECLINE_PENDING_REVIEW` — a named fraud rule fired with at least two named
  corroborating causes; a human reviews the recommendation.
- `REFER_FOR_BLOCK_CONFIRMATION` — the highest hard-risk floor; a human confirms
  any block or related action.

Risk floors are raise-only: trusted-device or authentication signals never lower a
hard typology floor. The five named typologies are account takeover,
card-not-present fraud, first-party/bust-out, mule inflow, and synthetic identity.

## Validated operating point

<!-- GENERATED-METRICS:START -->
Validated at seed 42 on 50,000 synthetic transactions (4,000 confirmed fraud):

- Fraud recall **1.0000**; 0 misses; exact one-sided 95% upper miss-rate bound **0.0749%**.
- Legitimate false-decline rate **0.0000%**; 0 hard declines; exact one-sided 95% upper bound **0.0065%**.
- Intervention precision **0.2502**, a **3.13x** lift over prevalence.
- Stability: both gates passed on the primary seed plus 6 additional seeds.
<!-- GENERATED-METRICS:END -->

These are observations on labelled synthetic populations, not production
guarantees. The exact confidence bounds make the finite-sample limitation explicit.

## Run it

From this directory:

```bash
python3 run_validation.py --seed 42 --transactions 50000 --trials 6
```

The command regenerates the population in memory, scores it, writes `evidence/`,
and exits nonzero if either observed safety-failure count is nonzero or either exact
one-sided 95% upper failure-rate bound exceeds 0.1%. `--trials 6` means the primary
seed plus six additional seeds. Throughput appears only on stdout because runtime
is volatile.

Demonstrate each gate branch without changing the scorer:

```bash
python3 run_validation.py --seed 42 --transactions 50000 --no-write --inject-gate-failure fraud-miss
python3 run_validation.py --seed 42 --transactions 50000 --no-write --inject-gate-failure false-decline
```

Generate inspectable source data only when needed; generated data remains out of
the evidence pack:

```bash
python3 generate_synthetic_data.py --seed 42 --transactions 50000
```

## Files

| File | Purpose |
| --- | --- |
| [`METHODOLOGY.md`](METHODOLOGY.md) | Regulator-facing rules, thresholds, invariant, and model-risk framing. |
| [`scorer.py`](scorer.py) | Deterministic dataclasses, named rules, and disposition contract. |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded labelled population, boundary cases, and legitimate mimics. |
| [`run_validation.py`](run_validation.py) | Dual safety gates, evidence renderer, stability, and failure injection. |
| [`tuning.md`](tuning.md) | Recalibration procedure and symmetric constraints. |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Deployment mapping and upstream/downstream validation boundaries. |
| [`evidence/`](evidence/) | Generated report, JSON manifest/metrics, and CSV diagnostics. |

This is a transparent reference implementation chosen for auditability, not a
production control. Calibrate and independently validate it against representative,
time-split, labelled institutional data before reliance.

**Confidence rating: HIGH —** the implementation is deterministic and its symmetric
safety claims are executable, but production transfer has not been established.

