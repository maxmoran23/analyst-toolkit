# Quantitative Analytics Library

Dependency-free Python quant primitives — Value at Risk, risk-adjusted return ratios, portfolio optimization, Kelly position sizing, volatility models, Monte Carlo simulation, discounted cash flow, drawdown analysis, and correlation analysis.

Each module is a standalone script. No package to install, no framework to learn: JSON in, JSON out, pure functions.

## Design principles

1. **Zero install friction.** Every module is a standalone Python script. Run it with `python3 <module>.py <args>`.
2. **JSON in, JSON out.** All modules accept stdin JSON or CLI arguments and emit JSON to stdout — easy to chain into any pipeline.
3. **No silent failures.** Bad input produces a non-zero exit code and a JSON error object, never a wrong number.
4. **Pure math.** No web calls, no persisted state, no side effects.

`numpy` is used when available; each module falls back to pure-Python implementations when it is not.

## Modules

| Module | Purpose | Example invocation |
|--------|---------|--------------------|
| `var.py` | Value at Risk — historical, parametric, CVaR / expected shortfall | `python3 var.py --returns-json returns.json --confidence 0.95` |
| `sharpe.py` | Sharpe, Sortino, Calmar, Omega ratios | `python3 sharpe.py --returns-json returns.json --rf 0.05` |
| `markowitz.py` | Portfolio optimization — min-variance, max-Sharpe, efficient frontier | `python3 markowitz.py --returns-csv returns.csv --target-return 0.12` |
| `kelly.py` | Full Kelly, fractional Kelly, multi-position correlated Kelly | `python3 kelly.py --edges-json edges.json --fraction 0.25` |
| `vol.py` | Realized volatility, EWMA, Parkinson, Garman-Klass, GARCH(1,1) | `python3 vol.py --prices-json ohlc.json --method ewma` |
| `monte_carlo.py` | Price-path simulation (GBM, jump-diffusion), portfolio simulation | `python3 monte_carlo.py --spot 100 --vol 0.4 --days 30 --paths 10000` |
| `dcf.py` | Discounted cash flow valuation with scenario ranges | `python3 dcf.py --fees-yearly fees.json --discount 0.15 --terminal-growth 0.03` |
| `drawdown.py` | Max drawdown, underwater curve, recovery-time statistics | `python3 drawdown.py --equity-json equity.json` |
| `correlation.py` | Rolling correlation, DCC, correlation-breakdown risk | `python3 correlation.py --returns-csv assets.csv --window 30` |

## Usage examples

**Portfolio risk before adding a position**
```bash
python3 var.py --returns-json portfolio_returns.json --confidence 0.95 --method historical
# -> {"var_pct": 2.3, ...}  2.3% of value at risk at 95% confidence
```

**Position sizing across several correlated opportunities**
```bash
python3 kelly.py --edges-json opportunities.json --fraction 0.25 --correlation-matrix corr.json
# -> per-position stake, total exposure, diversification benefit
```

**Risk-adjusted performance of a return series**
```bash
python3 sharpe.py --returns-json daily_returns.json --rf 0.05 --annualize 365
# -> {sharpe, sortino, calmar, omega, max_dd, win_rate, profit_factor}
```

**Valuation with explicit scenarios**
```bash
python3 dcf.py --fees-yearly '[120, 150, 180, 200, 210]' --discount 0.15 --terminal-growth 0.04
# -> fair value, scenario range
```

## Notes

- These are analytical primitives, not advice. A Value at Risk number or a Kelly fraction is one input to a decision, not the decision.
- `kelly.py` defaults toward fractional Kelly for a reason — full Kelly maximizes long-run growth only if the edge estimate is exact, and carries severe drawdowns when it is not. See [`prompts/specialty/expected-value-analysis.md`](../prompts/specialty/expected-value-analysis.md) for the reasoning.
- The math is general-purpose: the modules work equally well on equities, crypto assets, or any return / price series.
