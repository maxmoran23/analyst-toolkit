# Changelog

All notable changes to `quant-jvm` are recorded here. This changelog tracks parity with `../quant/` (Python) — when a Python module changes, the corresponding entry here records the Kotlin re-port.

## [0.6.0] — 2026-07-18

QUEUE COMPLETE — all 9 modules of `analyst-toolkit/quant` are ported. This wave delivers the one §1.3 stochastic module, closing the port order that ran deterministic-first by design.

### Added
- `MonteCarlo.kt` — Kotlin port of `quant/monte_carlo.py`, split by parity regime:
  - Deterministic skeleton (§1.1 exact parity): `percentile` (truncating index + clamp), `pathMaxDrawdown`, `monteCarloSummary` (sorting, percentile/mean rounding, vs-spot fields, halving/doubling probabilities); explicit throws where Python raises ZeroDivisionError (zero paths, zero spot) so Kotlin never silently emits NaN/Infinity
  - Stochastic core (§1.3 distributional): `gbmPath`, `jumpGbmPath` (Poisson-approximated Merton jumps), `simulate` — RNG is `java.util.Random(seed)` (spec-pinned LCG + polar Gaussian), giving bit-reproducible Kotlin runs per seed; seeds are documented as NOT cross-language comparable, per the contract's rejection of bit-matching Python's Mersenne Twister
- `Cli.kt` — `monte_carlo` subcommand (`--spot --vol [--drift] [--days] [--paths] [--jumps] [--seed]`); the planned-modules list is gone
- `MonteCarloParityTest.kt` — 8 tests:
  - Exact §1.1: `percentile` picks vs the imported Python helper on a fixed array; full output-shaping oracle on fixed injected ep/dd samples (byte-value-identical JSON)
  - Distributional §1.3: GBM and jump-diffusion runs at N=10,000 vs the Python CLI — quantiles p05..p95, mean, and drawdown p50/p75/p95 each within 6 sqrt(2) estimated SE (quantile SE via density-inverse method). Rationale: ~2e-9 false-failure per statistic, ~4e-8 per run across 18 comparisons — under the 1e-6 flakiness budget without retries, while real process bugs sit tens-to-hundreds of SE away. dd p99 excluded (tail density estimation unreliable); the contract's 2 SE + retry scheme is documented as traded for the wider no-retry bound
  - Kotlin-only: closed-form GBM moment checks (E[S_T] = S0 e^(mu T), median = S0 e^((mu - sigma^2/2) T)) on a fixed seed; fixed-seed reproducibility (identical output) plus reseed perturbation; skeleton hand checks (percentile truncation/clamps, known-path max drawdown, probability fields); CLI error contract
- `README.md` — monte_carlo row ported with the §1.3 note, queue marked complete (9/9), parity-table stochastic row updated from "planned / 2 SE" to the implemented 6 sqrt(2) SE no-retry bound

### Verified
- `gradle test --no-daemon` — 59/59 tests pass (6 Kelly, 6 Sharpe, 6 Drawdown, 7 Vol, 6 Correlation, 7 VaR, 6 Markowitz, 7 DCF, 8 Monte Carlo) with python3 present; full suite run twice back-to-back to shake out statistical flakiness — both runs green

## [0.5.0] — 2026-07-17

Final deterministic wave — only `monte_carlo` (§1.3 stochastic/distributional) remains planned.

### Added
- `Markowitz.kt` — Kotlin port of `quant/markowitz.py`:
  - `meanVec`, `covMatrix` (ddof=1), `cholesky` (1e-10 non-positive-pivot regularization), `solveLinear` (factor / forward / transpose / backward, replicated operation-for-operation — no library solver), `minVariancePortfolio`, `maxSharpePortfolio` (null when |normalizer| < 1e-12, key omitted like Python), `portfolioStats`, `markowitzOutput`
  - Quirks mirrored: `zip` truncation of surplus asset names in solver weight dicts vs the equal-weight benchmark iterating every provided name; simple `rf / annualize` periodic rate; `{"error": "no numeric data found"}` on an empty/non-numeric CSV
  - Classification: §1.4 numerical linear algebra — raw solver parity asserted at the contract's 1e-6 per-entry tolerance
- `Dcf.kt` — Kotlin port of `quant/dcf.py` (§1.1 plain arithmetic):
  - `dcfValuation` (explicit-fee PV + growing-perpetuity terminal, degenerate when discount <= terminal growth), `dcfJson`, scenario shifts (bear +0.05 discount / growth floored at 0.01, bull discount floored at 0.05 / growth +0.02), fixed discount-rate sensitivity grid
  - Quirks mirrored: Python's integer `0` for `pv_of_terminal` and `terminal_weight_pct` in degenerate branches; upside/downside computed from the already-rounded fair values; truthy `--current-price` gate (explicit 0 suppresses the block); f-string sensitivity keys (`discount_0.2`, not `discount_0.20`); `--fees-yearly` as inline JSON
- `Cli.kt` — `markowitz` and `dcf` subcommands; `monte_carlo` left as the only planned module
- `MarkowitzParityTest.kt` — 6 tests: full-JSON value parity (named assets, surplus-name quirk), raw solver oracle at the §1.4 1e-6 tolerance, Cholesky/solve/min-variance hand checks, degenerate tangency + pivot regularization hand checks, CLI error contract
- `DcfParityTest.kt` — 7 tests: full-JSON value parity (scenarios, sensitivity, upside block, degenerate int-zero terminal), raw oracle at relative 1e-10, growing-perpetuity hand check, sensitivity key repr check, zero-price truthiness gate, CLI error contract

### Verified
- `gradle test --no-daemon` — 51/51 tests pass (6 Kelly, 6 Sharpe, 6 Drawdown, 7 Vol, 6 Correlation, 7 VaR, 6 Markowitz, 7 DCF) with python3 present, cross-language assertions exercised

## [0.4.0] — 2026-07-17

### Added
- `Correlation.kt` — Kotlin port of `quant/correlation.py`:
  - `corr(x, y)` — pairwise Pearson correlation (0.0 for short series or zero variance)
  - `parseReturnsCsv(text)` — Python-faithful CSV ingestion (blank rows skipped, any row failing float parse skipped whole, i.e. header handling)
  - `correlationOutput(cols, names, window, crisisThreshold)` — full-sample / crisis-only (only when > 5 crisis days) / rolling-window correlation, compression computed from the already-rounded values then re-rounded, `assets` echoing the full provided name list, Python negative-slice semantics for the rolling tail
  - Classification note: contract §1.4 lists correlation under linear algebra (1e-6), but the reference has no matrix decomposition, so parity is verified at the stronger §1.1 1e-10 regime
- `Var.kt` — Kotlin port of `quant/var.py`:
  - `historicalVar(returns, confidence)` — sorted-quantile VaR with floor-index clamp and worst-tail CVaR
  - `parametricVar(returns, confidence)` — Gaussian VaR from the fixed z-table keyed by `round(confidence, 3)` with 1.645 fallback; explicit throw on the zero denominator at confidence 1.0 (Python raises ZeroDivisionError; Kotlin would silently emit Infinity)
  - `varOutput(returns, confidence, method, portfolioValue)` — public JSON contract (per-method pct at 4 decimals, dollar at 2, stats block), 20-observation minimum enforced at the CLI boundary like Python
  - No deferral: `var.py` contains no Monte Carlo or bootstrap variant, so the §1.3 stochastic regime does not apply
- `Cli.kt` — `correlation` and `var` subcommands with the same flags as the Python entrypoints
- `CorrelationParityTest.kt` — 6 tests: full-JSON parity with crisis/rolling branches on and off, raw `corr` oracle at 1e-10 (incl. zero-variance), hand-math spot checks, CSV-parsing hand check, CLI error contract
- `VarParityTest.kt` — 7 tests: full-JSON parity (both/historical/parametric, dollar scaling, off-table confidence fallback, stdin path), raw `historical_var`/`parametric_var` oracle at 1e-10, quantile-index and z-table hand checks (incl. the `round(confidence, 3)` key quirk), CLI error contract incl. confidence-1.0 parity

### Verified
- `gradle test --no-daemon` — 38/38 tests pass (6 Kelly, 6 Sharpe, 6 Drawdown, 7 Vol, 6 Correlation, 7 VaR) with python3 present, cross-language assertions exercised

## [0.3.0] — 2026-07-17

### Added
- `Drawdown.kt` — Kotlin port of `quant/drawdown.py`:
  - `equityFromReturns(returns, start)` — compound a unit start through periodic returns
  - `drawdownSeries(equity)` — per-observation drawdown fractions from a running peak
  - `recoveryEpisodes(equity)` — peak/trough/recovery episode extraction, including the unrecovered tail (`still_underwater`, null `recovery_idx`)
  - `drawdownOutput(equity, topN)` — public JSON contract (max/current/avg drawdown, pct time underwater, top-N episodes sorted on the rounded `dd_pct`, truthy-filtered `avg_recovery_days`)
- `Vol.kt` — Kotlin port of `quant/vol.py`:
  - `realizedVol`, `ewmaVol` (RiskMetrics lambda=0.94), `parkinsonVol`, `garmanKlassVol`
  - `simpleGarch` — fixed-parameter GARCH(1,1) (alpha=0.10, beta=0.85, no MLE, no RNG), classified deterministic under parity-contract.md §1.1; mirrors the Python quirk where a short series (< 20 returns) merges `{"error": ...}` into the output and exits 0
  - `round4(value)` — half-even four-decimal helper for the `persistence` field
- `Cli.kt` — `drawdown` and `vol` subcommands with the same flags as the Python entrypoints
- `DrawdownParityTest.kt` — 6 tests: full-JSON equity/returns parity vs `drawdown.py` (episodes, sort order, `--top-n` truncation), raw `drawdown_series` oracle at 1e-10, hand-math spot check, primitive hand checks, CLI error contract
- `VolParityTest.kt` — 7 tests: full-JSON parity for all five methods vs `vol.py` (including the garch short-series exit-0 error merge), raw estimator oracle at 1e-10, estimator hand checks, garch fixed-point hand check, CLI error contract

### Verified
- `gradle test --no-daemon` — 25/25 tests pass (6 Kelly, 6 Sharpe, 6 Drawdown, 7 Vol) with python3 present, cross-language assertions exercised

## [0.2.1] — 2026-07-17

### Removed
- `gradle-wrapper.jar`, `gradlew`, `gradlew.bat` — executable wrapper artifacts removed so the repository's "Download ZIP" passes enterprise secure-web-gateway policies that block archives containing JARs or batch scripts. The Gradle version stays pinned in `gradle/wrapper/gradle-wrapper.properties`; build with an installed `gradle` (CI provisions Gradle 8.10.2 explicitly), or run `gradle wrapper` locally to regenerate a wrapper. Historical `./gradlew` commands in earlier entries reflect the toolchain at that time.

## [0.1.0] — 2026-05-26

Initial scaffold.

### Added
- Gradle Kotlin DSL project, JVM target 21 LTS via toolchain
- Kotlin 2.0.21, JUnit Jupiter 5.11.3, kotlinx-serialization-json 1.7.3, commons-math3 3.6.1
- `Kelly.kt` — Kotlin port of `quant/kelly.py`:
  - `kellySingle(p, oddsDecimal)` — full-Kelly fraction for binary bet
  - `edgePct(p, oddsDecimal)` — expected value as % of stake
  - `kellyPortfolio(edges, fraction, corrMatrix)` — multi-bet with 50% exposure cap + correlation shrink
  - `round3(value)` — half-to-even rounding matching Python's `round(x, 3)` via BigDecimal HALF_EVEN
- `Cli.kt` — single-entrypoint dispatcher mirroring `python3 <module>.py <args>` ergonomics
- `KellyParityTest.kt` — parity tests vs `quant/kelly.py`:
  - Single-bet: positive edge, negative edge clamps, hand-math spot checks
  - Portfolio: independent bets (exposure cap inactive), exposure cap engaging
  - `round3` Python semantics check via subprocess invocation
- `docs/parity-contract.md` — formal specification of the parity tolerance regime, with one documented divergence (negative zero in `round3`)
- `README.md` — toolchain, build, run, design principles

### Verified
- `./gradlew test` — 6/6 parity tests pass (5 numerical-vs-Python, 1 hand math)
- End-to-end CLI parity: `./gradlew run --args="kelly ..."` produces bit-identical numerical output to `python3 quant/kelly.py ...` on matching inputs (only whitespace and JSON field ordering differ — non-contract per parity-contract.md §2)
- Build time: 4m24s cold (deps download), ~3s incremental
