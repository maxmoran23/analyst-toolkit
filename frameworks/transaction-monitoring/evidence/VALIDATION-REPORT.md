# Validation Report — Transaction-Monitoring Alert-Scoring Framework

> ILLUSTRATIVE / SYNTHETIC. Every figure is produced by running the reference scorer over a seeded, fully synthetic population. No real customer or transaction is represented. Numbers are emitted by `run_validation.py`, not authored; re-run it to reproduce them.

**Run:** seed `42` · 5,000 customers · 50,000 alerts · git `d2f4ef1` · 2026-07-10 05:10 UTC

**Headline:** recall on suspicious activity **1.0000** (false negatives: **0**), false-positive reduction **85.1%**, human review volume cut by **81.7%** (50,000 alerts → 9,175 to a human).

## 1. Methodology summary
The engine dispositions each TM alert (a customer plus a window of aggregated transaction features) as AUTO_CLOSE, ANALYST_REVIEW, or ESCALATE. It auto-closes only on a named benign cause (within-profile, documented-context, or below-typology-threshold) and only when NO laundering typology has fired; it never auto-files a SAR. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
50,000 alerts across 5,000 customers; ~4% genuinely suspicious. Each false positive carries a category; suspicious alerts come in clear-typology and emerging flavours, both of which fire a typology rule (so neither can be auto-closed) — the emerging flavour is the adversarial band that sits at the edge of the escalation threshold.

## 3. Operating-point results
- **Recall (suspicious retained): 1.0000** — **false negatives: 0**
- False-positive reduction (specificity): 0.8514
- Precision of the retained queue: 0.2237
- Confusion — TP 2,052 · FP 7,123 · TN 40,825 · FN 0

| Disposition | Count | Share |
| --- | --- | --- |
| AUTO_CLOSE | 40,825 | 81.7% |
| ANALYST_REVIEW | 7,960 | 15.9% |
| ESCALATE | 1,215 | 2.4% |

Analyst-review priority — HIGH 7,960 · MEDIUM 0 · LOW 0.

## 4. Per-category false-positive close rate
Did the engine close each false-positive type for the right named reason? The `ambiguous_residual` band — unexplained deviation with no typology — is deliberately NOT auto-closed; it is the irreducible queue a human must work.

| category | count | auto_closed | close_rate |
| --- | --- | --- | --- |
| within_profile | 19089 | 19089 | 1.0 |
| below_typology | 12198 | 12198 | 1.0 |
| documented_context | 9538 | 9538 | 1.0 |
| ambiguous_residual | 7123 | 0 | 0.0 |

## 5. Threshold-sensitivity analysis
A naive policy that auto-closed on `suspicion_score <= T` alone, for comparison. The deployed policy does not close on score — it closes only on a named benign cause and never when a typology has fired — so recall stays at 1.0 by construction while a bare threshold leaks suspicious activity as it rises.

| threshold | fp_closed | fp_close_rate | fn_leaked | recall |
| --- | --- | --- | --- | --- |
| 0.0 | 6844 | 0.1427 | 0 | 1.0 |
| 0.05 | 11874 | 0.2476 | 0 | 1.0 |
| 0.1 | 17740 | 0.37 | 0 | 1.0 |
| 0.15 | 18977 | 0.3958 | 0 | 1.0 |
| 0.2 | 19089 | 0.3981 | 0 | 1.0 |
| 0.3 | 20616 | 0.43 | 0 | 1.0 |
| 0.4 | 28560 | 0.5956 | 0 | 1.0 |
| 0.5 | 33441 | 0.6974 | 0 | 1.0 |
| 0.6 | 39659 | 0.8271 | 57 | 0.9722 |
| 0.7 | 45942 | 0.9582 | 180 | 0.9123 |
| 0.8 | 47707 | 0.995 | 620 | 0.6979 |
| 0.9 | 47948 | 1.0 | 892 | 0.5653 |

## 6. False-negative safety argument
**Statistical bound.** 0 misses were observed among 2,052 labelled truly suspicious alerts. Observing zero failures is not a guarantee of a zero failure rate: the exact one-sided 95% Clopper-Pearson upper bound on the miss rate is **0.1459%** (recall at least **99.8541%**) *on this synthetic population*. The bound is a property of the sample size, not a promise about live data — it tightens only by testing more true cases.

1. Of 2,052 planted suspicious alerts, **0 were auto-closed** — recall 1.0000.
2. Safety is structural: a genuinely suspicious alert fires a typology rule (structuring / funnel / pass-through), and the auto-close branches are reached only when NO typology has fired. A suspicious case therefore cannot be auto-closed regardless of its score.
3. Enforced as a build gate — `run_validation.py` exits non-zero if any suspicious alert is auto-closed.

## 7. Volume / funnel impact
50,000 alerts → 40,825 auto-closed (81.7%) → 9,175 to a human (18.4%), with recall held at 1.0.

## 8. Limitations
- Synthetic data models the shape of monitoring alerts (structuring, funnel, pass-through, velocity, geography) against a customer baseline, not the full richness of real transaction histories. Calibrate against a labelled sample of your own alerts before reliance (`tuning.md`).
- The engine scores and routes; it does not file SARs or close alerts of record. A typology hit is a human investigation decision.
- This is a transparent reference implementation, not a production control.

## 9. Reproduction
```bash
python3 run_validation.py --seed 42 --customers 5000 --alerts 50000
```
Same seed → identical population → identical metrics.
