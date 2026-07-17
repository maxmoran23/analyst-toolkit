# quant-jvm — Kotlin / JVM port of analyst-toolkit/quant

A parallel implementation of the analytical primitives in [`../quant/`](../quant/) (Python) using Kotlin on the JVM. Same math, same JSON I/O contract, verified by parity tests that run both implementations on identical inputs and assert numerical agreement.

## Why this exists

The Python `quant/` library was designed with one rule: *no silent failures, no language-specific assumptions, JSON in / JSON out*. That contract means the math is **portable** — it should not matter whether the caller is Python, a JVM service, or a shell pipeline. This directory proves it: every module that exists here computes the same number, on the same input, as its Python sibling, within a documented tolerance.

The audit-defensible claim is precise:

> *Given a fixed input and a deterministic function, the output is invariant under implementation language and within a stated numerical tolerance. Stochastic functions agree distributionally within stated confidence intervals.*

This is a stronger claim than "the code looks right" — it is an executable assertion run on every test build.

## What's implemented

| Module | Status | Python source | Kotlin file | Parity test |
|--------|--------|---------------|-------------|-------------|
| Kelly criterion | ported | [`../quant/kelly.py`](../quant/kelly.py) | [`Kelly.kt`](src/main/kotlin/org/maxmoran/quant/Kelly.kt) | [`KellyParityTest.kt`](src/test/kotlin/org/maxmoran/quant/KellyParityTest.kt) |
| Sharpe / Sortino / Calmar / Omega | ported | [`../quant/sharpe.py`](../quant/sharpe.py) | [`Sharpe.kt`](src/main/kotlin/org/maxmoran/quant/Sharpe.kt) | [`SharpeParityTest.kt`](src/test/kotlin/org/maxmoran/quant/SharpeParityTest.kt) |
| Drawdown | ported | [`../quant/drawdown.py`](../quant/drawdown.py) | [`Drawdown.kt`](src/main/kotlin/org/maxmoran/quant/Drawdown.kt) | [`DrawdownParityTest.kt`](src/test/kotlin/org/maxmoran/quant/DrawdownParityTest.kt) |
| Volatility (realized, EWMA, Parkinson, Garman-Klass, GARCH) | ported | [`../quant/vol.py`](../quant/vol.py) | [`Vol.kt`](src/main/kotlin/org/maxmoran/quant/Vol.kt) | [`VolParityTest.kt`](src/test/kotlin/org/maxmoran/quant/VolParityTest.kt) |
| Correlation | planned | `../quant/correlation.py` | — | — |
| Value at Risk | planned | `../quant/var.py` | — | — |
| Markowitz optimization | planned | `../quant/markowitz.py` | — | — |
| Monte Carlo (stochastic) | planned | `../quant/monte_carlo.py` | — | — |
| DCF | planned | `../quant/dcf.py` | — | — |

Port order is deliberate: deterministic modules first (Kelly through DCF), stochastic last (Monte Carlo). See [`docs/parity-contract.md`](docs/parity-contract.md) for why.

Note on GARCH: `vol.py`'s `simple_garch` is a fixed-parameter recursion (alpha=0.10, beta=0.85, no MLE fit, no RNG), so the entire volatility module is classified as deterministic pure math under parity-contract.md §1.1 — nothing in this wave was deferred to the §1.3 stochastic regime.

## Toolchain

| Tool | Version | Install |
|------|---------|---------|
| JDK | OpenJDK 21 LTS | `brew install openjdk@21` |
| Build | Gradle 8.10.2 | `brew install gradle` (or SDKMAN / your package manager) |
| Language | Kotlin 2.0.21 | resolved by Gradle |
| Test | JUnit Jupiter 5.11.3 | resolved by Gradle |

JDK 21 is the audit-defensible LTS choice. To use a different JDK locally, set `JAVA_HOME` before invoking `gradle`; the project's Gradle toolchain declaration in `build.gradle.kts` will still pin the **build** target to 21.

**Why no Gradle wrapper binaries.** This repository deliberately ships no `gradle-wrapper.jar`, `gradlew`, or `gradlew.bat`. Enterprise secure-web gateways commonly block any downloadable archive that contains an executable JAR or batch script, which would make the repo's "Download ZIP" unusable on locked-down corporate machines — the primary consumption path for this toolkit. The Gradle version is still pinned in [`gradle/wrapper/gradle-wrapper.properties`](gradle/wrapper/gradle-wrapper.properties) (plain text); running `gradle wrapper` locally regenerates the wrapper from it if you want one.

## Build and test

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home  # macOS Homebrew
gradle build           # compile + test
gradle test            # tests only
gradle test --tests KellyParityTest  # specific class
gradle test --tests org.maxmoran.quant.SharpeParityTest
```

Parity tests resolve the Python interpreter from `PATH`. If `python3` is missing, parity assertions are **skipped with a logged message**, not silently passed — Kotlin-internal correctness tests (e.g. hand-math spot checks) still run and must pass.

## Run a module

The project ships a single `main` entrypoint that dispatches by module name, mirroring the Python `python3 <module>.py <args>` ergonomics:

```bash
# Single bet
gradle run --args="kelly --mode single --p 0.55 --odds 2.0 --fraction 0.25"

# Portfolio of independent bets
gradle run --args="kelly --mode portfolio --edges-json edges.json --fraction 0.25"

# Portfolio with correlation matrix
gradle run --args="kelly --mode portfolio --edges-json edges.json --correlation-matrix corr.json --fraction 0.25"

# Return-series ratios from a JSON file
gradle run --args="sharpe --returns-json returns.json --rf 0.05 --annualize 252"

# Or provide the same 30-or-more-period JSON array on standard input
gradle run --args="sharpe --stdin --rf 0.05 --annualize 252" < returns.json

# Drawdown profile from an equity curve or a return series
gradle run --args="drawdown --equity-json equity.json --top-n 5"
gradle run --args="drawdown --returns-json returns.json"

# Volatility estimators
gradle run --args="vol --returns-json returns.json --method ewma --annualize 365 --ewma-lambda 0.94"
gradle run --args="vol --ohlc-json ohlc.json --method garman_klass"
gradle run --args="vol --returns-json returns.json --method garch"
```

Output goes to stdout as pretty-printed JSON, matching the Python schema exactly. Errors go to stdout as `{"error": "..."}` with exit code 1.

## Design principles (inherited from `quant/`)

1. **JSON in, JSON out.** Every module accepts the same JSON shapes as its Python sibling and emits the same JSON shapes back.
2. **No silent failures.** Bad input → JSON error + non-zero exit code. Never a wrong number.
3. **Pure math.** No web calls, no persistent state, no side effects.
4. **Dependency-minimal.** `kotlinx-serialization-json` for JSON and `commons-math3` for distributions/decomp when pure-Kotlin would be a worse re-implementation. Everything else is the standard library.

## Parity contract (short version)

| Category | Tolerance | Rationale |
|----------|-----------|-----------|
| Deterministic math | `\|py - kt\| < 1e-10` on raw doubles | Floating-point determinism modulo transcendental ordering |
| Rounded output fields | Exact JSON equality (`round(x, 3)`, and `round(x, 2)` for `win_rate_pct`) | Matches Python's `round()` semantics via BigDecimal HALF_EVEN; infinity is serialized as the string `"inf"` |
| Stochastic outputs (planned) | Within 2 standard errors at N=10,000 paths | RNG implementations differ across languages; distribution is the invariant |

Full contract: [`docs/parity-contract.md`](docs/parity-contract.md).

## Not a runtime dependency

This directory is **not used by the agent fleet at runtime**. The fleet's Python `/quant/` is the production code path. `quant-jvm/` is a **methodology proof** and a portability demonstration — useful in JVM-house environments (banking, finance), but not part of any scheduled agent's critical path.

If `quant-jvm` ever falls behind `quant/` (a Python change without a corresponding Kotlin port), the parity tests for the new code will simply be absent — not red. The fleet keeps working. Re-syncing is a deliberate act.

## License

MIT, matching the parent repo.
