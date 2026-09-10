# Quantitative Analytics Library

Dependency-free Python quant primitives — Value at Risk, risk-adjusted return ratios, portfolio optimization, Kelly position sizing, volatility models, Monte Carlo simulation, discounted cash flow, drawdown analysis, and correlation analysis.

Each module is a standalone script. No package to install, no framework to learn: JSON in, JSON out, pure functions.

## Design principles

1. **Zero install friction.** Every module is a standalone Python script. Run it with `python3 <module>.py <args>`.
2. **JSON in, JSON out.** All modules accept stdin JSON or CLI arguments and emit JSON to stdout — easy to chain into any pipeline.
3. **No silent failures.** The public calculation entrypoints reject malformed numeric inputs. The series contracts below define minimum sample sizes and applicable domains. Command-line failures return a non-zero exit code; older scripts may emit a traceback.
4. **Pure math.** No web calls, no persisted state, no side effects.

The Python modules use only the standard library. Keep `_validation.py` beside the scripts when copying them out of this directory; `markowitz.py` also needs `correlation.py` for its shared CSV reader.

## Modules

| Module | Purpose | Example invocation |
|--------|---------|--------------------|
| `var.py` | Value at Risk — historical, parametric, CVaR / expected shortfall | `python3 var.py --returns-json returns.json --confidence 0.95` |
| `sharpe.py` | Sharpe, Sortino, Calmar, Omega ratios | `python3 sharpe.py --returns-json returns.json --rf 0.05` |
| `markowitz.py` | Portfolio optimization — unconstrained min-variance and tangency weights | `python3 markowitz.py --returns-csv returns.csv --rf 0.05` |
| `kelly.py` | Full Kelly, fractional Kelly, multi-position Kelly with correlation haircuts | `python3 kelly.py --mode portfolio --edges-json edges.json --fraction 0.25` |
| `vol.py` | Realized volatility, EWMA, Parkinson, Garman-Klass, GARCH(1,1) | `python3 vol.py --returns-json returns.json --method ewma` |
| `monte_carlo.py` | Price-path simulation (GBM, jump-diffusion) | `python3 monte_carlo.py --spot 100 --vol 0.4 --days 30 --paths 10000` |
| `dcf.py` | Discounted cash flow valuation with scenario ranges | `python3 dcf.py --fees-yearly '[100,120]' --circulating-supply 1000 --discount 0.15` |
| `drawdown.py` | Max drawdown, underwater curve, recovery-time statistics | `python3 drawdown.py --equity-json equity.json` |
| `correlation.py` | Rolling and crisis-subset correlation | `python3 correlation.py --returns-csv assets.csv --window 30` |

## Usage examples

**Portfolio risk before adding a position**
```bash
python3 var.py --returns-json portfolio_returns.json --confidence 0.95 --method historical
# -> {"var_pct": 2.3, ...}  2.3% of value at risk at 95% confidence
```

**Position sizing across several correlated opportunities**
```bash
python3 kelly.py --mode portfolio --edges-json opportunities.json --fraction 0.25 --correlation-matrix corr.json
# -> per-position stake, total exposure, diversification benefit
```

**Risk-adjusted performance of a return series**
```bash
python3 sharpe.py --returns-json daily_returns.json --rf 0.05 --annualize 365
# -> {sharpe, sortino, calmar, omega, max_dd, win_rate, profit_factor}
```

**Valuation with explicit scenarios**
```bash
python3 dcf.py --fees-yearly '[120, 150, 180, 200, 210]' --circulating-supply 1000 --discount 0.15 --terminal-growth 0.04
# -> fair value, scenario range
```

## Notes

- These are analytical primitives, not advice. A Value at Risk number or a Kelly fraction is one input to a decision, not the decision.
- `kelly.py` defaults toward fractional Kelly for a reason — full Kelly maximizes long-run growth only if the edge estimate is exact, and carries severe drawdowns when it is not. See [`prompts/specialty/expected-value-analysis.md`](../prompts/specialty/expected-value-analysis.md) for the reasoning.
- The math is general-purpose: the modules work equally well on equities, crypto assets, or any return / price series.

## Numerical contracts and checks

- Gaussian VaR uses the inverse standard normal CDF at the requested confidence; it does not substitute a 95% quantile. Historical VaR retains the documented floor-index convention, with expected shortfall averaging through that index.
- DCF requires `discount > terminal_growth > -1`, positive supply, nonnegative finite fees and a capture ratio in `[0, 1]`. An invalid optional scenario or sensitivity point is marked `unavailable`; an invalid base case is rejected.
- Kelly probabilities and fractions lie in `[0, 1]`; decimal odds exceed one. Correlation is a heuristic haircut, not a multivariate Kelly optimizer. Negative correlation never increases the stake, and the reported portfolio stays within its 50% exposure ceiling after rounding.
- Markowitz permits short sales and requires positive-definite covariance. It rejects singular or indefinite matrices rather than silently changing their pivots. A nonpositive tangency normalization returns `None`; the code does not present that stationary portfolio as maximum Sharpe.

Run analytic and input-contract regressions with `python3 -m unittest discover -s quant -p 'test_*.py'` from the repository root. The Kotlin port has additional cross-language tests under `quant-jvm/`.

### Time-series and simulation input contracts

- **Sharpe:** at least 30 finite simple returns, each `>= -1`, positive integer annualization and annual risk-free rate `> -1`. Standard deviation requires at least two observations and `0 <= ddof < n`. Zero-denominator Sharpe/Sortino/Calmar retain the historical `0` display convention; `omega` and `profit_factor` use the string `"inf"` for no losses. These conventions do not imply statistically identified ratios.
- **Volatility:** sample realized volatility requires two finite observations; EWMA requires one, with `0 <= lambda <= 1`. Annualization is a positive integer. Range estimators require at least one positive, ordered high/low pair or OHLC bar; open and close must lie inside the reported range. Invalid bars are rejected, never omitted while retaining the original denominator. GARCH requires 20 finite observations, nonnegative `omega`, `alpha`, `beta`, and `alpha + beta < 1`; a short sample now fails with a nonzero CLI exit. Parameters remain fixed assumptions, not estimates fitted to the series. Volatility accepts finite numeric changes without imposing the simple-return floor, allowing log-return inputs; callers must identify the return convention.
- **Drawdown:** equity must be finite and nonnegative with a strictly positive initial value. Compounded simple returns cannot be below `-1`; a complete loss is valid and remains at zero. `top_n` must be a nonnegative integer. Recovery durations count observations, not calendar days; the retained `avg_recovery_days` field assumes daily observations. No observed recovery retains the historical `0` summary convention; inspect unrecovered episodes before interpreting it.
- **Correlation:** paired arrays must have equal lengths and finite values. The low-level helper retains `0` for fewer than two observations or zero variance as a compatibility sentinel, not evidence of independence. JSON reports use `null` for these unidentified correlations and exclude them from compression. CSV analysis requires at least two observations and two assets, an optional single all-text header, rectangular finite numeric rows, unique nonempty matching asset names, and window `>= 2`. Malformed data rows are rejected. The shared parser also applies to Markowitz, which permits a single asset. Nonconstant series whose variance underflows to zero are rejected rather than reported as uncorrelated. The Kotlin line parser supports simple unquoted or quoted numeric fields; embedded commas/newlines inside quoted fields are outside its CSV contract. The crisis-minus-full-sample difference is descriptive and the `0.2` review flag is not calibrated.
- **Simulation:** positive finite spot and time step, finite drift, nonnegative finite volatility, integer horizon `>= 0`, and positive integer path count. A zero horizon returns the initial spot. Percentiles require finite presorted samples and probability in `[0, 1]`, retaining the existing floor-index convention. Jump paths use at most one Bernoulli log-price jump per step; `intensity * dt <= 1` is enforced and the approximation is useful only when that probability is small. This is not an exact Poisson/Merton simulation; drift is not jump-compensated. Jump mean is finite and jump volatility/intensity nonnegative. Extreme calculations that overflow are rejected; no guarantee covers every representable finite input or resource-exhausting path count.

These contracts intentionally change previously accepted invalid inputs. Valid routine-input calculations retain their existing formulas and JSON fields, except undefined correlation values now appear as `null` and the interpretation text describes the threshold as a review flag.
