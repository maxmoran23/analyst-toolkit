#!/usr/bin/env python3
"""
Volatility estimation — realized, EWMA, Parkinson, Garman-Klass, simplified GARCH(1,1).

Usage:
    python3 vol.py --returns-json returns.json --method ewma --annualize 365
    python3 vol.py --ohlc-json ohlc.json --method parkinson --annualize 365
"""
import argparse
try:
    from ._validation import number, series, integer
except ImportError:
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _validation import number, series, integer

import json
import math
import sys


def realized_vol(returns, annualize=252):
    series(returns, "returns", minimum_length=2)
    integer(annualize, "annualize")
    n = len(returns)
    mu = sum(returns) / n
    var = sum((r - mu) ** 2 for r in returns) / (n - 1)
    return number(math.sqrt(var) * math.sqrt(annualize), "volatility")


def ewma_vol(returns, lam=0.94, annualize=252):
    """RiskMetrics-style EWMA. Lambda=0.94 for daily (JPM default)."""
    series(returns, "returns")
    integer(annualize, "annualize")
    number(lam, "lambda", minimum=0, maximum=1)
    var = returns[0] ** 2
    for r in returns[1:]:
        var = lam * var + (1 - lam) * r * r
    return number(math.sqrt(var) * math.sqrt(annualize), "volatility")


def parkinson_vol(high_low_pairs, annualize=252):
    """Parkinson uses high/low range. Efficient for OHLC data."""
    integer(annualize, "annualize")
    if not high_low_pairs:
        raise ValueError("need at least one high/low pair")
    k = 1 / (4 * math.log(2))
    var_sum = 0.0
    for h, l in high_low_pairs:
        number(h, "high", minimum=0)
        number(l, "low", minimum=0)
        if not 0 < l <= h:
            raise ValueError("require 0 < low <= high")
        var_sum += (math.log(h / l)) ** 2
    var = k * var_sum / len(high_low_pairs)
    return number(math.sqrt(var) * math.sqrt(annualize), "volatility")


def garman_klass_vol(ohlc_list, annualize=252):
    """Uses O/H/L/C. More efficient than Parkinson for assets without overnight gaps."""
    integer(annualize, "annualize")
    if not ohlc_list:
        raise ValueError("need at least one OHLC bar")
    total = 0.0
    for o, h, l, c in ohlc_list:
        for value in (o, h, l, c):
            number(value, "OHLC price", minimum=0)
        if not (0 < l <= min(o, c) <= max(o, c) <= h):
            raise ValueError("require 0 < low <= open/close <= high")
        hl = math.log(h) - math.log(l) if not math.isfinite(h / l) else math.log(h / l)
        co = math.log(c) - math.log(o) if not math.isfinite(c / o) or c / o == 0 else math.log(c / o)
        total += 0.5 * hl * hl - (2 * math.log(2) - 1) * co * co
    var = number(total / len(ohlc_list), "Garman-Klass variance")
    return number(math.sqrt(max(0, var)) * math.sqrt(annualize), "volatility")


def simple_garch(returns, annualize=252, omega=None, alpha=0.10, beta=0.85):
    """
    Simplified GARCH(1,1) forecast. Uses fixed parameters (typical equity defaults)
    rather than MLE estimation; callers must assess those assumptions for their series.
    """
    series(returns, "returns", minimum_length=20)
    integer(annualize, "annualize")
    number(alpha, "alpha", minimum=0)
    number(beta, "beta", minimum=0)
    if alpha + beta >= 1:
        raise ValueError("GARCH requires alpha + beta < 1")
    if omega is not None:
        number(omega, "omega", minimum=0)
    n = len(returns)
    unconditional = sum(r * r for r in returns) / n
    if omega is None:
        omega = unconditional * (1 - alpha - beta)
    var_t = unconditional
    conditional_vols = [math.sqrt(var_t)]
    for r in returns:
        var_t = omega + alpha * r * r + beta * var_t
        conditional_vols.append(math.sqrt(var_t))
    forecast = number(math.sqrt(var_t) * math.sqrt(annualize), "volatility")
    return {
        "garch_annualized_vol_pct": round(forecast * 100, 3),
        "current_conditional_vol_pct": round(conditional_vols[-1] * math.sqrt(annualize) * 100, 3),
        "persistence": round(alpha + beta, 4),
        "unconditional_annual_vol_pct": round(math.sqrt(unconditional * annualize) * 100, 3),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--returns-json")
    ap.add_argument("--ohlc-json", help="array of [open, high, low, close] arrays")
    ap.add_argument("--method", choices=["realized", "ewma", "parkinson", "garman_klass", "garch"], default="realized")
    ap.add_argument("--annualize", type=int, default=252)
    ap.add_argument("--ewma-lambda", type=float, default=0.94)
    args = ap.parse_args()

    result = {"method": args.method, "annualize_factor": args.annualize}

    if args.method == "realized":
        with open(args.returns_json) as f:
            returns = json.load(f)
        result["annualized_vol_pct"] = round(realized_vol(returns, args.annualize) * 100, 3)
    elif args.method == "ewma":
        with open(args.returns_json) as f:
            returns = json.load(f)
        result["annualized_vol_pct"] = round(ewma_vol(returns, args.ewma_lambda, args.annualize) * 100, 3)
        result["ewma_lambda"] = args.ewma_lambda
    elif args.method == "parkinson":
        with open(args.ohlc_json) as f:
            ohlc = json.load(f)
        pairs = [(bar[1], bar[2]) for bar in ohlc]
        result["annualized_vol_pct"] = round(parkinson_vol(pairs, args.annualize) * 100, 3)
    elif args.method == "garman_klass":
        with open(args.ohlc_json) as f:
            ohlc = json.load(f)
        result["annualized_vol_pct"] = round(garman_klass_vol(ohlc, args.annualize) * 100, 3)
    elif args.method == "garch":
        with open(args.returns_json) as f:
            returns = json.load(f)
        result.update(simple_garch(returns, args.annualize))

    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
