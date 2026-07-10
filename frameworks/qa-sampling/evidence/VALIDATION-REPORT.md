# Validation Report — QA / Independent-Testing Attribute-Sampling Framework

> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running plan-select-evaluate over a seeded population of controls whose true deviation rates are known by construction. No real control, tester, or institution is represented (the fictional institution is Harborview Financial Group). Numbers are emitted by `run_validation.py`, not authored.

**Run:** seed `42` · 12 controls · 480,000 items · git `531971e` · 2026-07-10 05:15 UTC

**Headline:** UDL cross-check exact — divergence below the **1e-09** tolerance on all 119 cases (0 integer mismatches); **0** structural breaches across 312 evaluations; measured false-assurance on failing populations **0.0000** (0/150) vs design risk 5%; solver monotonicity **0** violations across 40 grid cells.

## 1. Methodology summary
For each control the engine PLANS an exact attribute sample (smallest n and acceptance number c such that a population deviating at the tolerable rate is accepted with probability at most the design risk — exact hypergeometric, no lookup-table approximations), SELECTS it by seeded stratified random sampling, and EVALUATES the observed deviations into the exact one-sided upper deviation limit (UDL) and a named-rule conclusion. Observed deviations above the acceptance number can never conclude CONTROL_EFFECTIVE — that rule fires first. Full spec: `METHODOLOGY.md`.

## 2. Population construction
12 controls x 40,000 labelled test items each, on a deterministic scenario cycle: clean (true rate 0.08-0.22x tolerable), failing (2-3x tolerable), boundary (0.75-1.10x), and planted (one whole stratum 100% deviant — the adversarial case the stratified sample cannot miss). The true rate is known to the generator and NEVER used by the engine — only the plan parameters and the drawn sample are.

## 3. Sampling plans (exact solver)
| control | scenario | tolerable | expected | n | c | achieved_risk |
| --- | --- | --- | --- | --- | --- | --- |
| CTRL-000 | clean | 0.04 | 0.0082 | 117 | 1 | 0.0493 |
| CTRL-001 | failing | 0.04 | 0.0128 | 156 | 2 | 0.0486 |
| CTRL-002 | boundary | 0.04 | 0.0125 | 156 | 2 | 0.0486 |
| CTRL-003 | planted | 0.04 | 0.0113 | 156 | 2 | 0.0486 |
| CTRL-004 | clean | 0.1 | 0.0248 | 61 | 2 | 0.049 |
| CTRL-005 | failing | 0.04 | 0.0101 | 156 | 2 | 0.0486 |
| CTRL-006 | boundary | 0.05 | 0.0122 | 124 | 2 | 0.0493 |
| CTRL-007 | planted | 0.04 | 0.0116 | 156 | 2 | 0.0486 |
| CTRL-008 | clean | 0.1 | 0.0313 | 61 | 2 | 0.049 |
| CTRL-009 | failing | 0.06 | 0.0201 | 127 | 3 | 0.0494 |
| CTRL-010 | boundary | 0.06 | 0.0203 | 127 | 3 | 0.0494 |
| CTRL-011 | planted | 0.08 | 0.0222 | 77 | 2 | 0.0484 |

Every plan's achieved risk is at or below the 5% design risk (confidence 95%); sample sizes span 61-156 items (median 127), testing 1,474 of 480,000 items (0.31%).

## 4. Conclusions (per control)
| control | scenario | true_rate | tested | deviations | c | udl | tolerable | conclusion | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CTRL-000 | clean | 0.00363 | 117 | 0 | 1 | 0.0252 | 0.04 | CONTROL_EFFECTIVE | UDL_WITHIN_TOLERABLE |
| CTRL-001 | failing | 0.10805 | 156 | 24 | 2 | 0.2094 | 0.04 | CONTROL_INEFFECTIVE | OVER_ACCEPTANCE |
| CTRL-002 | boundary | 0.03793 | 156 | 3 | 2 | 0.0489 | 0.04 | CONTROL_INEFFECTIVE | OVER_ACCEPTANCE |
| CTRL-003 | planted | 0.2721 | 156 | 42 | 2 | 0.3337 | 0.04 | CONTROL_INEFFECTIVE | OVER_ACCEPTANCE |
| CTRL-004 | clean | 0.02045 | 61 | 3 | 2 | 0.1222 | 0.1 | CONTROL_INEFFECTIVE | OVER_ACCEPTANCE |
| CTRL-005 | failing | 0.1066 | 156 | 22 | 2 | 0.1951 | 0.04 | CONTROL_INEFFECTIVE | OVER_ACCEPTANCE |
| CTRL-006 | boundary | 0.04125 | 124 | 0 | 2 | 0.0238 | 0.05 | CONTROL_EFFECTIVE | UDL_WITHIN_TOLERABLE |
| CTRL-007 | planted | 0.31252 | 156 | 48 | 2 | 0.374 | 0.04 | CONTROL_INEFFECTIVE | OVER_ACCEPTANCE |
| CTRL-008 | clean | 0.01082 | 61 | 1 | 2 | 0.0754 | 0.1 | CONTROL_EFFECTIVE | UDL_WITHIN_TOLERABLE |
| CTRL-009 | failing | 0.15255 | 127 | 20 | 3 | 0.2205 | 0.06 | CONTROL_INEFFECTIVE | OVER_ACCEPTANCE |
| CTRL-010 | boundary | 0.05318 | 127 | 7 | 3 | 0.1009 | 0.06 | CONTROL_INEFFECTIVE | OVER_ACCEPTANCE |
| CTRL-011 | planted | 0.31895 | 77 | 23 | 2 | 0.3958 | 0.08 | CONTROL_INEFFECTIVE | OVER_ACCEPTANCE |

By scenario — boundary: 1 CONTROL_EFFECTIVE, 2 CONTROL_INEFFECTIVE; clean: 2 CONTROL_EFFECTIVE, 1 CONTROL_INEFFECTIVE; failing: 3 CONTROL_INEFFECTIVE; planted: 3 CONTROL_INEFFECTIVE.

## 5. UDL cross-check (gate)
The primary UDL (log-gamma tails, bisection, integer search) was recomputed for 119 cases by an independent brute-force exact path: direct `math.comb` summation for the binomial bound, exact integer/Fraction arithmetic for the hypergeometric bound. The two paths agree to within the **1e-09** tolerance on every case (**True**); hypergeometric integer-count mismatches **0**. Full table: `udl-crosscheck.csv`.

The observed divergence sits at the 1e-12 level — bisection round-off, not disagreement. That magnitude is platform-dependent (the same code yields 5.4e-12 on macOS/CPython 3.14 and 6.4e-12 on Linux/CPython 3.12), so the committed evidence asserts the divergence against a documented tolerance rather than pinning a float that cannot re-derive on another machine. The per-case values in `udl-crosscheck.csv` are diagnostics of the same round-off and vary at that magnitude for the same reason.

## 6. Measured false-assurance — the direction gate
On the failing controls (true rate 2-3x tolerable), 50 independent replicate samples were drawn per control and evaluated. CONTROL_EFFECTIVE conclusions: **0/150** (measured false-assurance 0.0000; gate fails above 0.10 = design risk + margin).

| control | scenario | true_rate | tolerable | n | c | exact_p_accept | effective | replicates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CTRL-001 | failing | 0.10805 | 0.04 | 156 | 2 | 3e-06 | 0 | 50 |
| CTRL-003 | planted | 0.2721 | 0.04 | 156 | 2 | 0.0 | 0 | 50 |
| CTRL-005 | failing | 0.1066 | 0.04 | 156 | 2 | 4e-06 | 0 | 50 |
| CTRL-007 | planted | 0.31252 | 0.04 | 156 | 2 | 0.0 | 0 | 50 |
| CTRL-009 | failing | 0.15255 | 0.06 | 127 | 3 | 2e-06 | 0 | 50 |
| CTRL-011 | planted | 0.31895 | 0.08 | 77 | 2 | 0.0 | 0 | 50 |

Calibration at the boundary: for each distinct plan, a population deviating at EXACTLY the tolerable count was constructed and the acceptance rate measured over 200 fresh samples — the design risk observed rather than asserted. Max |measured - exact| = **0.0193** (binomial sampling error at 200 replicates; exact value from the same hypergeometric tail the plan is built on).

| n | c | tolerable | exact_p_accept | measured_p_accept | replicates |
| --- | --- | --- | --- | --- | --- |
| 117 | 1 | 0.04 | 0.0493 | 0.04 | 200 |
| 156 | 2 | 0.04 | 0.0486 | 0.05 | 200 |
| 61 | 2 | 0.1 | 0.049 | 0.055 | 200 |
| 124 | 2 | 0.05 | 0.0493 | 0.03 | 200 |
| 127 | 3 | 0.06 | 0.0494 | 0.065 | 200 |
| 77 | 2 | 0.08 | 0.0484 | 0.055 | 200 |

## 7. Planted-deviation structural gate
3 planted controls carry a fully-deviant stratum sized so stratified allocation must place more than the acceptance number of items in it (design verified: yes). Across the main run and 150 replicate draws: **0** CONTROL_EFFECTIVE conclusions (must be 0). Combined with the rule-order guarantee, over-acceptance evaluations concluded EFFECTIVE in **0** of 312 evaluations.

## 8. Sample-size solver monotonicity (gate)
The exact solver was swept over 40 grid cells (confidence [0.9, 0.95, 0.975, 0.99] x tolerable [0.02, 0.04, 0.06, 0.08, 0.1], expected 0.01, binomial and finite-population). Higher confidence or a tighter tolerable rate never yields a smaller sample: **0** violations. The finite-population plan never exceeds the binomial plan: **0** violations. Excerpt (hypergeometric, N=40,000):

| confidence | tolerable_rate | n | c | achieved_risk |
| --- | --- | --- | --- | --- |
| 0.9 | 0.02 | 397 | 4 | 0.0996 |
| 0.9 | 0.04 | 96 | 1 | 0.099 |
| 0.9 | 0.06 | 64 | 1 | 0.0968 |
| 0.9 | 0.08 | 48 | 1 | 0.0944 |
| 0.9 | 0.1 | 38 | 1 | 0.0952 |
| 0.95 | 0.02 | 588 | 6 | 0.0495 |
| 0.95 | 0.04 | 156 | 2 | 0.0486 |
| 0.95 | 0.06 | 78 | 1 | 0.0478 |
| 0.95 | 0.08 | 58 | 1 | 0.0479 |
| 0.95 | 0.1 | 46 | 1 | 0.0479 |
| 0.99 | 0.02 | 996 | 10 | 0.01 |
| 0.99 | 0.04 | 248 | 3 | 0.0097 |
| 0.99 | 0.06 | 137 | 2 | 0.0098 |
| 0.99 | 0.08 | 81 | 1 | 0.0093 |
| 0.99 | 0.1 | 64 | 1 | 0.0095 |

## 9. Short-test demonstration (INCONCLUSIVE path)
Control `CTRL-002` was deliberately tested at 62 of its planned 156 items: 2 deviation(s), UDL 0.098 vs tolerable 0.04 -> **INCONCLUSIVE** (UDL_EXCEEDS_TOLERABLE, expand to 1735 items). A short test cannot silently pass: the UDL stays above the tolerable rate until enough items are tested, and the engine emits the exact expansion needed.

## 10. Limitations
- Synthetic deviations are independent draws within strata; real control failures cluster (by processor, by period, by branch). Stratify on the clustering dimension and treat any cluster found as a finding to scope, not just a count.
- The engine quantifies SAMPLING risk only. Non-sampling risk — the tester misreading an item — is untouched by sample size and is managed by workpaper review, not by this engine.
- Conclusions are statistical statements routed to the tester; the engine never certifies a control, closes a test, or files a result. Tolerable rate, confidence, and expected rate are policy choices set and owned by the institution.
- A transparent reference implementation, not a production control.

## 11. Reproduction
```bash
python3 run_validation.py --seed 42 --controls 12 --population 40000
```
