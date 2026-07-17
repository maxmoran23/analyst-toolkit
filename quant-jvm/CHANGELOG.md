# Changelog

All notable changes to `quant-jvm` are recorded here. This changelog tracks parity with `../quant/` (Python) — when a Python module changes, the corresponding entry here records the Kotlin re-port.

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
