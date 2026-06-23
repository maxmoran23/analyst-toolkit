# Validation Report — On-Chain KYT Address-Risk Framework

> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the reference scorer over a seeded, fully synthetic population whose exposure features are derived by the real `_lib/graph` taint propagation. No real address is represented. Numbers are emitted by `run_validation.py`, not authored.

**Run:** seed `42` · 50,000 addresses · git `423f27c` · 2026-06-23 16:22 UTC

**Headline:** recall on high-risk addresses **1.0000** (false negatives: **0**), false-positive reduction **87.9%**, human review volume cut by **82.5%** (50,000 addresses → 8,741 to a human).

## 1. Methodology summary
Each flagged address is dispositioned AUTO_CLEAR / ANALYST_REVIEW / ESCALATE from its strongest tainted-path exposure to an illicit entity (severity, hop distance with decay, traceable value share, and whether a commingling intermediary breaks the trail). Auto-clears only on a named cause; never auto-clears material, proximate, unbroken exposure to a serious category. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
50,000 addresses; ~6% genuinely high-risk. Each address's exposure features are computed by `_lib/graph` over a constructed subgraph (seed, optional commingling breaker, intermediates). False positives span benign-category, broken-intermediary, de-minimis, diluted-distant, and a mid-severity ambiguous residual that is left open by design.

## 3. Operating-point results
- **Recall (high-risk retained): 1.0000** — **false negatives: 0**
- False-positive reduction (specificity): 0.8789
- Precision of the retained queue: 0.3495
- Confusion — TP 3,055 · FP 5,686 · TN 41,259 · FN 0

| Disposition | Count | Share |
| --- | --- | --- |
| AUTO_CLEAR | 41,259 | 82.5% |
| ANALYST_REVIEW | 6,922 | 13.8% |
| ESCALATE | 1,819 | 3.6% |

Analyst-review priority — HIGH 5,878 · MEDIUM 1,044 · LOW 0.

## 4. Per-category false-positive clear rate
The `ambiguous_residual` band (mid-severity, moderate exposure) is deliberately NOT auto-cleared — it goes to a human. The other categories clear on a named, provable cause.

| fp_category | count | auto_cleared | clear_rate |
| --- | --- | --- | --- |
| benign_category | 13071 | 13071 | 1.0 |
| broken_intermediary | 9361 | 9361 | 1.0 |
| de_minimis | 8384 | 8384 | 1.0 |
| diluted_distant | 10443 | 10443 | 1.0 |
| ambiguous_residual | 5686 | 0 | 0.0 |

## 5. Threshold-sensitivity analysis
A naive policy auto-clearing on the risk score `<= T`, for comparison. The deployed policy clears only on a named cause, holding recall at 1.0 while a bare threshold leaks high-risk addresses as it rises.

| threshold | fp_cleared | fp_clear_rate | fn_leaked | recall |
| --- | --- | --- | --- | --- |
| 0.0 | 22432 | 0.4778 | 0 | 1.0 |
| 0.02 | 40153 | 0.8553 | 0 | 1.0 |
| 0.04 | 41259 | 0.8789 | 0 | 1.0 |
| 0.06 | 41259 | 0.8789 | 3 | 0.999 |
| 0.1 | 41259 | 0.8789 | 308 | 0.8992 |
| 0.15 | 44202 | 0.9416 | 625 | 0.7954 |
| 0.2 | 46945 | 1.0 | 894 | 0.7074 |
| 0.3 | 46945 | 1.0 | 1236 | 0.5954 |
| 0.4 | 46945 | 1.0 | 1908 | 0.3755 |
| 0.6 | 46945 | 1.0 | 2645 | 0.1342 |

## 6. False-negative safety argument
1. Of 3,055 genuinely high-risk addresses, **0 were auto-cleared** — recall 1.0000.
2. Safety is structural: material, proximate, unbroken exposure to a serious category cannot satisfy any clear cause — it is not benign, not broken by an intermediary, not de-minimis, and not diluted/distant.
3. Enforced as a build gate — `run_validation.py` exits non-zero if any high-risk address is auto-cleared.

## 7. Volume / funnel impact
50,000 addresses → 41,259 auto-cleared (82.5%) → 8,741 to a human (17.5%), recall held at 1.0.

## 8. Limitations
- Synthetic subgraphs model the exposure shape (severity, hops, decay, commingling breaks, value share), not the full complexity of a real chain graph or the attribution quality of a real analytics vendor. In production the exposure features come from that vendor, whose attribution accuracy must be validated alongside this engine. Calibrate against labelled cases (`tuning.md`).
- The engine dispositions; the freeze / SAR / off-boarding decision is a documented human action.
- A transparent reference implementation, not a production control.

## 9. Reproduction
```bash
python3 run_validation.py --seed 42 --addresses 50000
```
