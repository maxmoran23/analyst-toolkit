# Parity Contract — quant-jvm and quant (Python)

This contract describes the checks implemented in the [Kotlin test suite](../src/test/kotlin/org/maxmoran/quant/).
It establishes agreement on those inputs, not correctness for every possible input.
Independent hand calculations and boundary tests supplement cross-language comparisons:
two implementations can preserve the same error.

## 1. Categories of parity

### 1.1 Deterministic calculations

Kelly, return ratios, drawdown, volatility, pairwise correlation, VaR, DCF, and the
Monte Carlo output-shaping helpers are compared against Python on fixed inputs.
Raw scalar comparisons generally use an absolute tolerance of `1e-10`. DCF uses
relative tolerance at large currency magnitudes; an absolute `1e-10` bound there
can be smaller than floating-point spacing. Individual tests define the actual
field-level tolerance and whether the oracle imports a helper or reconstructs a
calculation. Those are different forms of evidence and must not be conflated.

### 1.2 Rounded display fields

Public output comparisons use parsed JSON values, with the precision declared by each
field. Kelly uses three decimal places; some other report fields use two or four.
The Kotlin rounding helpers use `BigDecimal(value)` and `HALF_EVEN` to retain the
input double's representation when rounding. Agreement is tested on selected half-point
and signed values, not asserted from a decimal example alone.

#### Infinity serialization

The Sharpe-family output uses the JSON string `"inf"` in its documented unbounded
Omega and profit-factor cases. This is distinct from invalid numeric inputs or
non-standard bare JSON infinity. Preserve the documented field semantics and reject
malformed inputs where the owning module defines a boundary contract.

### 1.3 Stochastic functions

The implemented stochastic module is Monte Carlo, including GBM and jump-diffusion.
The Python and JVM samplers do not promise identical draws for the same numeric seed.
The JVM implementation uses `java.util.Random`; the Python implementation uses its
standard-library random generator. Fixed seeds test repeatability within a runtime.

[MonteCarloParityTest](../src/test/kotlin/org/maxmoran/quant/MonteCarloParityTest.kt)
compares two 10,000-path runs using a bound of `6 * sqrt(2) * estimated_standard_error`,
plus the specified rounding allowance. Standard errors are estimated from the JVM
sample; quantile errors use the sample's local quantile slope. The square-root-of-two
factor allows for variability in both samples under comparable variance. The test has
no automatic retry. This is a regression tolerance, not a calibrated guarantee of the
suite's false-failure probability or model validity. Tail statistics whose standard
errors cannot be estimated reliably are explicitly excluded in the test.

Separate tests check deterministic output shaping on fixed injected samples,
closed-form GBM moments, and seed reproducibility. Current VaR has historical and
Gaussian methods only; it does not implement a stochastic VaR estimator.

### 1.4 Numerical linear algebra

Markowitz uses explicit Cholesky factorization and forward/backward substitution in
both languages. Raw solver comparisons use `1e-6` per-entry tolerance on the tested
matrices. Singular or indefinite covariance is rejected; there is no SVD fallback
or silent pivot replacement. A matrix must satisfy the input and positive-definiteness
checks before the solve. These unconstrained portfolios can include short positions.

Pairwise correlation performs no matrix decomposition and belongs to the scalar
comparison tests in section 1.1. Gaussian VaR now uses inverse-normal quantiles in
both languages at the requested confidence, replacing the former fixed-table fallback.

## 2. Boundaries of the claim

| Property | Contract |
|---|---|
| JSON bytes | Whitespace, key order, and scientific notation can differ; compare schema and numeric values. |
| Errors | Nonzero CLI status and a structured error where the module specifies it; wording need not match. |
| Missing Python | Cross-language tests can be skipped locally. A skipped check is unverified parity; CI provisions Python and a complete parity result requires no such skips. |
| Performance | No cross-language speed or memory claim is made by the parity suite. |
| Invalid inputs | Boundary tests cover the enumerated cases; undocumented older module edges remain outside the guarantee. |
| Negative zero | Kotlin BigDecimal rounding may lose the sign of zero. Numeric equality is the comparison contract. |
| Real-world validity | Cross-language agreement does not establish forecasting, investment, or production decision effectiveness. |

## 3. Failure and maintenance rules

A numerical disagreement, unexpected error, or failed stochastic comparison fails the
build. Do not retry with fresh seeds until the result passes. Diagnose the failed
statistic, the input, and the oracle; preserve the original failure.

When a Python primitive changes:

1. Record the behavioral change and migration impact in the [changelog](../CHANGELOG.md).
2. Port the relevant valid-input behavior and rejection semantics to Kotlin.
3. Add a regression that fails under the old behavior, plus an independent expected
   value or invariant where feasible.
4. Run the complete suite with Python available and inspect skipped-test counts.
5. Update this contract when algorithms, comparison tolerances, or the covered domain
   change. Do not loosen tolerances merely to conceal a regression.

Source-specific validation is still required before applying a primitive to a new
population or decision. Keep model assumptions separate from implementation parity.
