#!/usr/bin/env python3
"""
Sharpe, Sortino, Calmar, Omega ratios. All annualized.

Usage:
    python3 sharpe.py --returns-json returns.json --rf 0.05 --annualize 252
    python3 sharpe.py --returns-json crypto_daily.json --rf 0.05 --annualize 365
"""
import argparse
import json
import math
import sys


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def stdev(xs, ddof=1):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - ddof))


def downside_stdev(xs, target=0.0):
    below = [min(0.0, x - target) for x in xs]
    if not below:
        return 0.0
    return math.sqrt(sum(x * x for x in below) / len(below))


def max_drawdown(returns):
    """Returns max DD as positive fraction (e.g. 0.42 = 42% drawdown)."""
    equity = [1.0]
    for r in returns:
        equity.append(equity[-1] * (1 + r))
    peak = equity[0]
    max_dd = 0.0
    for v in equity:
        peak = max(peak, v)
        dd = (peak - v) / peak
        max_dd = max(max_dd, dd)
    return max_dd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--returns-json", required=False)
    ap.add_argument("--stdin", action="store_true")
    ap.add_argument("--rf", type=float, default=0.05, help="annual risk-free rate")
    ap.add_argument("--annualize", type=int, default=252, help="periods per year (252 equities, 365 crypto)")
    args = ap.parse_args()

    if args.stdin:
        returns = json.loads(sys.stdin.read())
    elif args.returns_json:
        with open(args.returns_json) as f:
            returns = json.load(f)
    else:
        print(json.dumps({"error": "need --returns-json or --stdin"}))
        sys.exit(1)

    if len(returns) < 30:
        print(json.dumps({"error": "need >= 30 periods"}))
        sys.exit(1)

    n = len(returns)
    periodic_rf = (1 + args.rf) ** (1 / args.annualize) - 1
    excess = [r - periodic_rf for r in returns]

    mu = mean(excess)
    sigma = stdev(excess)
    down_sigma = downside_stdev(returns, target=periodic_rf)

    sharpe = (mu / sigma) * math.sqrt(args.annualize) if sigma > 0 else 0.0
    sortino = (mu / down_sigma) * math.sqrt(args.annualize) if down_sigma > 0 else 0.0

    total_return = 1.0
    for r in returns:
        total_return *= 1 + r
    cagr = total_return ** (args.annualize / n) - 1
    max_dd = max_drawdown(returns)
    calmar = cagr / max_dd if max_dd > 0 else 0.0

    # Omega ratio with threshold = rf
    gains = sum(max(0, r - periodic_rf) for r in returns)
    losses = sum(max(0, periodic_rf - r) for r in returns)
    omega = gains / losses if losses > 0 else float("inf")

    wins = sum(1 for r in returns if r > 0)
    win_rate = wins / n
    avg_win = mean([r for r in returns if r > 0]) if wins else 0.0
    avg_loss = mean([r for r in returns if r < 0]) if (n - wins) else 0.0
    profit_factor = abs(sum(r for r in returns if r > 0) / sum(r for r in returns if r < 0)) if any(r < 0 for r in returns) else float("inf")

    out = {
        "n_periods": n,
        "annualize_factor": args.annualize,
        "risk_free_rate": args.rf,
        "cagr_pct": round(cagr * 100, 3),
        "annualized_vol_pct": round(sigma * math.sqrt(args.annualize) * 100, 3),
        "sharpe": round(sharpe, 3),
        "sortino": round(sortino, 3),
        "calmar": round(calmar, 3),
        "omega": round(omega, 3) if omega != float("inf") else "inf",
        "max_drawdown_pct": round(max_dd * 100, 3),
        "win_rate_pct": round(win_rate * 100, 2),
        "avg_win_pct": round(avg_win * 100, 3),
        "avg_loss_pct": round(avg_loss * 100, 3),
        "profit_factor": round(profit_factor, 3) if profit_factor != float("inf") else "inf",
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
