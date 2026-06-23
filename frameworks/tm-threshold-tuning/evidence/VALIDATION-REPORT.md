# Validation Report — Transaction-Monitoring Threshold-Tuning Framework

> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the tuning engine over a seeded population of monitoring rules whose correct action is known by construction. No real rule or customer is represented. Numbers are emitted by `run_validation.py`, not authored.

**Run:** seed `42` · 12 rules · 480,000 observations · git `b13053f` · 2026-06-23 17:36 UTC

**Headline:** every recommendation keeps detection at or above the 95% floor (min **0.9506**), all **6** leaking rules remediated, recommendation-direction accuracy **100%**.

## 1. Methodology summary
For each monitoring rule the engine runs above/below-the-line testing across candidate thresholds (a thin layer over `_lib/metrics.sweep`): ATL productivity is the precision of the alerts, BTL leakage is the suspicious activity below the threshold. It recommends the HIGHEST threshold that still detects at least the recall floor of suspicious activity — cutting alert volume only where it is safe to do so. Full spec: `METHODOLOGY.md`.

## 2. Population construction
12 rules x 40,000 observations each. Each rule's suspicious population sits higher on its metric than its benign population; the current threshold is set by a designed scenario (too_low / too_high / optimal) relative to the optimal threshold. The correct action is therefore known and is NOT used by the engine — only the metric values and labels are.

## 3. Recommendations (per rule)
| rule | scenario | action | cur_thr | rec_thr | cur_det | rec_det | cur_vol | rec_vol |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RULE-000 | too_high | LOWER | 65.9 | 40.3 | 0.4514 | 0.9718 | 800 | 4299 |
| RULE-001 | too_high | LOWER | 52.5 | 27.9 | 0.6554 | 0.9619 | 3853 | 19835 |
| RULE-002 | optimal | KEEP | 49.9 | 49.9 | 0.9506 | 0.9506 | 5021 | 5021 |
| RULE-003 | too_high | LOWER | 63.2 | 41.1 | 0.544 | 0.9597 | 1169 | 8729 |
| RULE-004 | too_high | LOWER | 50.5 | 31.9 | 0.7157 | 0.9515 | 5511 | 18703 |
| RULE-005 | too_high | LOWER | 66.1 | 46.8 | 0.722 | 0.9604 | 1386 | 5384 |
| RULE-006 | too_high | LOWER | 51.7 | 38.4 | 0.714 | 0.9543 | 1595 | 4640 |
| RULE-007 | too_low | RAISE | 27.7 | 46.1 | 0.9995 | 0.9647 | 20459 | 6260 |
| RULE-008 | too_low | RAISE | 25.4 | 50.1 | 1.0 | 0.9628 | 15776 | 1875 |
| RULE-009 | too_low | RAISE | 29.8 | 48.8 | 1.0 | 0.9684 | 24142 | 4968 |
| RULE-010 | too_low | RAISE | 10.9 | 31.6 | 0.9994 | 0.9549 | 35816 | 20606 |
| RULE-011 | too_low | RAISE | 26.4 | 47.4 | 1.0 | 0.9589 | 25776 | 6991 |

Recommendation-direction accuracy vs the designed scenario: **100%**.

## 4. Below-the-line safety (the gate)
- Minimum recommended detection across all rules: **0.9506** (floor 95%).
- Leaking rules (current threshold detects below the floor): **6**; remediated (recommended DOWN to restore detection): **6/6**.
No recommendation trades detection below the floor for alert-volume reduction — this is the regulator-facing safety property, enforced as a build gate.

## 5. ATL/BTL sweep — illustrative rule
Rule `RULE-000` (too_high). As the threshold rises, alert volume and BTL-missed move in opposite directions; the engine reads the highest threshold where detection still clears the floor.

| threshold | alert_volume | productivity | detection_rate | btl_missed |
| --- | --- | --- | --- | --- |
| 0.0 | 40000 | 0.0435 | 1.0 | 0 |
| 8.0595 | 33162 | 0.0524 | 1.0 | 0 |
| 16.119 | 25670 | 0.0677 | 1.0 | 0 |
| 24.178499999999996 | 16581 | 0.1048 | 0.9994 | 1 |
| 32.238 | 8920 | 0.1942 | 0.996 | 7 |
| 40.29749999999999 | 4299 | 0.3931 | 0.9718 | 49 |
| 48.35699999999999 | 2268 | 0.6808 | 0.8879 | 195 |
| 56.41649999999999 | 1394 | 0.8902 | 0.7136 | 498 |
| 64.476 | 876 | 0.9749 | 0.4911 | 885 |
| 72.53549999999998 | 484 | 0.9979 | 0.2777 | 1256 |
| 80.59499999999998 | 189 | 0.9947 | 0.1081 | 1551 |
| 88.65449999999998 | 58 | 1.0 | 0.0334 | 1681 |
| 96.71399999999998 | 8 | 1.0 | 0.0046 | 1731 |
| 104.77349999999998 | 3 | 1.0 | 0.0017 | 1736 |

## 6. Alert-volume impact
On the over-alerting rules recommended for RAISE, alert volume falls from 121,969 to 40,700 (**67%** reduction) with detection held at or above the floor — the productivity gain from tuning.

## 7. Limitations
- Synthetic metric distributions are unimodal per class; real rule metrics are messier and the 'suspicious' label is itself a historical disposition with its own error. The recall floor is a policy choice — set it from your risk appetite. Calibrate against a labelled sample (`tuning.md`).
- The engine recommends; a threshold change is a governed model-change decision a human approves and documents.
- A transparent reference implementation, not a production control.

## 8. Reproduction
```bash
python3 run_validation.py --seed 42 --rules 12 --population 40000
```
