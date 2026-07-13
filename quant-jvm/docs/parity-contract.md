# Parity Contract — quant-jvm ↔ quant (Python)

This document specifies the **executable agreement** between `analyst-toolkit/quant/` (Python) and `analyst-toolkit/quant-jvm/` (Kotlin). Every claim below is enforced by a JUnit test that fails the build if violated.

---

## 1. Categories of parity

Numerical functions split into three regimes, each with a different tolerance and a different verification strategy. Conflating them produces either spurious test failures (too tight) or false confidence (too loose).

### 1.1 Deterministic pure math

**Examples:** `kellySingle`, `edgePct`, `sharpeRatio`, `maxDrawdown`, `percentile`, `dcfValuation`.

**Tolerance:** `|python_result − kotlin_result| < 1e-10` on raw doubles.

**Rationale:** IEEE 754 double-precision arithmetic is deterministic per-operation. Cross-language drift here comes from (a) transcendental function ordering (Python's `math.exp` vs Kotlin's `kotlin.math.exp` may compile to different libm calls), and (b) compiler reorderings of associative operations. Both effects are bounded by a few ulps — well inside 1e-10 for the operation counts in this library.

**Verification:** Test harness invokes Python via `ProcessBuilder` on identical inputs, parses JSON output, and asserts each numerical field within tolerance. The unchanged `sharpe.py` CLI intentionally exposes only rounded report fields, so `SharpeParityTest` uses a `python3 -c` oracle that imports its `mean`, `stdev`, `downside_stdev`, and `max_drawdown` helpers and reconstructs the remaining raw operations in the same order. This keeps the authorized Python source byte-identical while still testing unrounded Kotlin values to `1e-10`.

### 1.2 Rounded display fields

**Examples:** `edge_pct`, `full_kelly_pct`, `fractional_kelly_pct`, `total_exposure_pct`, Sharpe-family ratios, and the two-decimal `win_rate_pct` field.

**Tolerance:** **Exact equality** after applying Python's `round(x, 3)` semantics.

**Rationale:** Python 3's `round()` uses half-to-even (banker's rounding) on floats — but the actual behavior depends on the float's binary representation, which is *not* obvious from the decimal input. The string `"1.235"` is stored as `1.234999999...`, so `round(1.235, 3) == 1.234` (not 1.235). To get exact agreement, Kotlin's `round3` uses `BigDecimal(value).setScale(3, RoundingMode.HALF_EVEN)`, which matches Python's behavior on the same binary representation.

**Verification:** A dedicated `round3` parity test runs both implementations on a set of edge cases (half-points, denormal-adjacent values, negatives) and asserts identical outputs. Sharpe public-contract tests compare the complete parsed JSON object field-for-field; `win_rate_pct` uses the equivalent two-decimal HALF_EVEN helper.

### 1.2.1 Infinity serialization

The Python public contract emits the JSON string `"inf"` when Omega has no losses below its threshold or profit factor has no negative returns. Kotlin emits the same string in those two fields; it never emits non-standard bare `Infinity`. Tests cover zero downside, zero volatility, infinite Omega, and infinite profit factor.

### 1.3 Stochastic functions (planned, applies to `monte_carlo`, parts of `var`)

**Tolerance:** Distributional agreement within **2 standard errors at N ≥ 10,000 samples**.

**Rationale:** Python's `random.gauss(seed=42)` and Kotlin's `kotlin.random.Random(42).nextGaussian()` both use Mersenne Twister but with different Gaussian sampling algorithms (Wichmann-Hill vs Box-Muller), different seed-initialization conventions, and different state layouts. **Bit-identical sequences are not achievable without porting the RNG implementation itself**, which defeats the purpose of demonstrating implementation independence.

**What's actually invariant:** the *distribution*. If both implementations sample correctly from N(μ=0, σ=1), their sample means, percentiles, and tail probabilities converge at the rate predicted by the Central Limit Theorem.

**Verification approach (chosen):** For each stochastic function, the parity test will:

1. Run both implementations with N=10,000 paths and matching parameters.
2. Compare sample statistics (mean, p05, p25, p50, p75, p95, max drawdown distribution).
3. Assert each statistic is within `± 2 × (standard error at N=10,000)` of the other.
4. At p < 0.05 confidence, this test fails ~5% of the time even when both implementations are correct. To handle this, the test is allowed **one retry with a new seed** before failing. Two consecutive failures indicate a real divergence.

**Rejected alternatives:**

| Approach | Why rejected |
|----------|--------------|
| Bit-match by porting Python's Mersenne Twister + Wichmann-Hill to Kotlin | ~100 LOC of state-mirroring; couples Kotlin to a specific Python implementation; defeats the audit narrative ("same math, different language") |
| Reseed-from-Python (dump RNG draws to JSON, load in Kotlin) | Tests only the post-RNG math, not the full function; couples tests to Python runtime; brittle if Python's `random` impl changes |
| Skip RNG-dependent tests entirely | No coverage on the most operationally important function (`monte_carlo`) |

### 1.4 Numerical linear algebra (planned, applies to `markowitz`, `correlation`)

**Tolerance:** `|python_result − kotlin_result| < 1e-6` on each matrix entry, with both implementations using the same decomposition algorithm (Cholesky for positive-definite covariance, otherwise SVD).

**Rationale:** Pivot ordering in matrix decomposition can produce results that differ by orders of magnitude more than basic arithmetic — both numerically correct, but on different floating-point paths. Pinning the algorithm (not just the spec) closes this gap. Apache Commons Math 3 is used in Kotlin to ensure the decomposition routines are well-validated.

---

## 2. What is *not* asserted

| Claim | Why not asserted |
|-------|------------------|
| JSON output is byte-identical | Field ordering varies between language JSON libs. Schema and values are asserted; whitespace and key order are not. |
| Error messages match exactly | Error strings are display surface, not contract. Both implementations emit `{"error": "..."}` with non-zero exit; the body text may differ. |
| Performance is comparable | Out of scope. Kotlin is expected to be faster on cold start in some cases and slower in others; this is not a benchmark. |
| Behavior on NaN / Infinity / overflow | Asserted only where the Python implementation has a documented behavior. Undocumented edge cases produce *whatever Python does*, in both languages, but are not contractually guaranteed. |

---

## 3. When parity tests should fail the build

1. A numerical regression in either implementation (the test is the *only* guard against an asymmetric bug fix).
2. A change in `round3` semantics on either side (Python deprecation, BigDecimal scale change).
3. A divergence in algorithm choice (e.g., one side switches from Cholesky to LU decomposition).

## 4. When parity tests should *not* fail the build

1. Python interpreter missing on the build machine → cross-language Sharpe tests use JUnit assumptions and are reported as skipped. Kotlin-only hand-math and CLI-contract assertions still run and must pass.
2. Stochastic test fails once → automatic retry with new seed. Two consecutive failures = real divergence.
3. JSON field ordering changes → not asserted, by design.

---

## 5. Maintenance discipline

When `quant/<module>.py` changes:

1. Note the change in `CHANGELOG.md` (this repo's, not the parent's).
2. If the change is **adding** a field or function: port to Kotlin, add parity test, build green.
3. If the change is **modifying** existing math: re-port, update parity test if tolerances need tuning, build green.
4. If the change is **removing** functionality: remove from Kotlin too.
5. If a Python change is **explicitly not portable** (e.g., uses a Python-only library with no JVM equivalent): document the decision in this file's section 6, and leave the Kotlin side at the prior version with a note.

Section 6 is empty as of v0.1.0 — every module in `quant/` is portable in principle.

## 6. Documented non-portable divergences

### 6.1 `round3(-0.0)` returns `+0.0` in Kotlin, `-0.0` in Python

Python's `round(-0.0, 3)` returns `-0.0` (preserving the sign of zero). Kotlin's `round3` uses `BigDecimal(value).setScale(3, RoundingMode.HALF_EVEN)`, and `BigDecimal` drops the sign of zero — converting back to `Double` always yields `+0.0`.

**Why not "fix" this:**
- No analytical primitive in this library propagates the sign of zero (Kelly fractions are clamped at 0; Sharpe / VaR / drawdown all collapse `-0.0` and `+0.0` to the same downstream result).
- Preserving negative zero would require post-processing every `BigDecimal` conversion — visual noise for no analytical gain.
- The fleet's Python code itself doesn't rely on this distinction anywhere.

**Recorded as a documented divergence**, not a bug to fix.
