#!/usr/bin/env python3
"""
Value at Risk (VaR) and Conditional VaR (Expected Shortfall).

Inputs: daily returns as JSON array.
Outputs: VaR and CVaR at specified confidence level, using historical or parametric methods.

Usage:
    python3 var.py --returns-json returns.json --confidence 0.95 --method historical
    echo '[-0.02, 0.01, -0.05, 0.03, ...]' | python3 var.py --stdin --confidence 0.95
"""
import argparse
import json
import math
import sys


def historical_var(returns, confidence):
    """VaR as the (1-confidence) quantile of the historical return distribution."""
    sorted_r = sorted(returns)
    idx = max(0, int(math.floor((1 - confidence) * len(sorted_r))))
    var = -sorted_r[idx]
    tail = sorted_r[: idx + 1] or [sorted_r[0]]
    cvar = -sum(tail) / len(tail)
    return var, cvar


def parametric_var(returns, confidence):
    """Gaussian VaR: mean - z * sigma. Approximation only, understates fat tails."""
    n = len(returns)
    mean = sum(returns) / n
    var_ = sum((r - mean) ** 2 for r in returns) / (n - 1)
    sigma = math.sqrt(var_)
    # inverse normal CDF approximation (Beasley-Springer-Moro would be more accurate)
    # For 95%: z=1.645, 99%: z=2.326, 99.9%: z=3.090
    z_table = {0.90: 1.282, 0.95: 1.645, 0.975: 1.960, 0.99: 2.326, 0.995: 2.576, 0.999: 3.090}
    z = z_table.get(round(confidence, 3), 1.645)
    var = z * sigma - mean
    # CVaR for gaussian: sigma * phi(z) / (1-confidence) - mean, where phi is normal PDF
    phi_z = math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
    cvar = sigma * phi_z / (1 - confidence) - mean
    return var, cvar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--returns-json", help="path to JSON file of daily returns (array)")
    ap.add_argument("--stdin", action="store_true", help="read returns JSON from stdin")
    ap.add_argument("--confidence", type=float, default=0.95)
    ap.add_argument("--method", choices=["historical", "parametric", "both"], default="both")
    ap.add_argument("--portfolio-value", type=float, default=1.0, help="scale result to dollar VaR")
    args = ap.parse_args()

    if args.stdin:
        returns = json.loads(sys.stdin.read())
    elif args.returns_json:
        with open(args.returns_json) as f:
            returns = json.load(f)
    else:
        print(json.dumps({"error": "must supply --returns-json or --stdin"}))
        sys.exit(1)

    if not isinstance(returns, list) or len(returns) < 20:
        print(json.dumps({"error": "need at least 20 return observations"}))
        sys.exit(1)

    result = {"confidence": args.confidence, "n_observations": len(returns), "portfolio_value": args.portfolio_value}

    if args.method in ("historical", "both"):
        v, c = historical_var(returns, args.confidence)
        result["historical"] = {
            "var_pct": round(v * 100, 4),
            "cvar_pct": round(c * 100, 4),
            "var_dollar": round(v * args.portfolio_value, 2),
            "cvar_dollar": round(c * args.portfolio_value, 2),
        }
    if args.method in ("parametric", "both"):
        v, c = parametric_var(returns, args.confidence)
        result["parametric"] = {
            "var_pct": round(v * 100, 4),
            "cvar_pct": round(c * 100, 4),
            "var_dollar": round(v * args.portfolio_value, 2),
            "cvar_dollar": round(c * args.portfolio_value, 2),
        }

    # basic stats
    mean = sum(returns) / len(returns)
    result["stats"] = {
        "mean_pct": round(mean * 100, 4),
        "worst_day_pct": round(min(returns) * 100, 4),
        "best_day_pct": round(max(returns) * 100, 4),
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
