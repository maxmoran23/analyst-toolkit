# Changelog

All notable changes to `quant-jvm` are recorded here. This changelog tracks parity with `../quant/` (Python) — when a Python module changes, the corresponding entry here records the Kotlin re-port.

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
