# Validation Report — Fraud-Detection Triage Engine

> ILLUSTRATIVE / SYNTHETIC. Every figure below was rendered by `run_validation.py` from a seeded, labelled population. No real person, account, or transaction is represented.

> **In plain terms:** The engine caught every planted confirmed-fraud event and hard-declined none of the legitimate events. Both zero counts are paired with exact statistical bounds; they are finite-sample evidence, not a guarantee about live activity.

**Run:** seed `42`; 50,000 transactions; 4,000 confirmed fraud (8.00%); results digest `fb19646b2eaa3c650bc12ffd720232ce55d8784e107614d4646e376461fa3118`.

## Dual safety invariant

- Fraud miss: **0** confirmed-fraud events received `APPROVE`; recall **1.0000**. Exact one-sided 95% upper miss-rate bound: **0.0749%**.
- False decline: **0** legitimate events received a hard disposition; rate **0.0000%**. Exact one-sided 95% upper false-decline-rate bound: **0.0065%**.
- Gate requirement: each observed count is zero and each bound is no greater than **0.1%**. Both branches passed.

The false-decline definition includes `DECLINE_PENDING_REVIEW` and `REFER_FOR_BLOCK_CONFIRMATION`; `STEP_UP_AUTH` is excluded. `APPROVE` is available only for `trusted_session_continuity` and no fired fraud rule. Risk floors are raise-only.

## Operating point

Interventions (step-up or harder): 15,990; precision **0.2502**; lift **3.13x** over the 8.00% fraud prevalence.

| Disposition | Count | Share |
| --- | ---: | ---: |
| APPROVE | 34,010 | 68.02% |
| STEP_UP_AUTH | 11,990 | 23.98% |
| DECLINE_PENDING_REVIEW | 1,600 | 3.20% |
| REFER_FOR_BLOCK_CONFIRMATION | 2,400 | 4.80% |

## Per-typology performance

| typology | confirmed | boundary_cases | detected | recall |
| --- | --- | --- | --- | --- |
| account_takeover | 800 | 2 | 800 | 1.0000 |
| card_not_present | 800 | 2 | 800 | 1.0000 |
| first_party_bustout | 800 | 2 | 800 | 1.0000 |
| mule_inflow | 800 | 2 | 800 | 1.0000 |
| synthetic_identity | 800 | 2 | 800 | 1.0000 |

## Multi-seed stability

`--trials 6` means the primary seed plus 6 additional seeds.

| seed | fraud_recall | fraud_misses | false_declines | intervention_precision |
| --- | --- | --- | --- | --- |
| 42 | 1.0000 | 0 | 0 | 0.2502 |
| 43 | 1.0000 | 0 | 0 | 0.2501 |
| 44 | 1.0000 | 0 | 0 | 0.2505 |
| 45 | 1.0000 | 0 | 0 | 0.2504 |
| 46 | 1.0000 | 0 | 0 | 0.2505 |
| 47 | 1.0000 | 0 | 0 | 0.2506 |
| 48 | 1.0000 | 0 | 0 | 0.2501 |

## Counterfactual score-only threshold sweep

This table demonstrates why the deployed engine does not use a bare score for a hard decision. The actual disposition contract requires a named rule and corroborating causes.

| score_threshold | fraud_recall_if_score_only | fraud_misses_if_score_only | legitimate_false_decline_rate_if_score_only | legitimate_hard_declines_if_score_only |
| --- | --- | --- | --- | --- |
| 0.25 | 1.0 | 0 | 0.076543 | 3521 |
| 0.4 | 1.0 | 0 | 0.049326 | 2269 |
| 0.55 | 1.0 | 0 | 0.02463 | 1133 |
| 0.7 | 1.0 | 0 | 0.0 | 0 |
| 0.8 | 0.912 | 352 | 0.0 | 0 |
| 0.88 | 0.6 | 1600 | 0.0 | 0 |
| 0.94 | 0.453 | 2188 | 0.0 | 0 |

## Limitations

- Labels are constructed and features are stylized. Live prevalence, drift, upstream authentication quality, merchant intelligence, and identity resolution must be independently validated.
- Exact bounds describe these independent seeded synthetic populations; they are not production guarantees.
- The engine recommends routing. It does not execute a decline, block, filing, freeze, or customer action.

## Reproduction

```bash
python3 run_validation.py --seed 42 --transactions 50000 --trials 6
```

**Confidence rating: HIGH —** the deterministic evidence re-runs byte-for-byte and both planted gate branches fail as designed; production transfer remains unvalidated.
