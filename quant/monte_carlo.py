#!/usr/bin/env python3
"""
Monte Carlo price path simulation — geometric Brownian motion, with optional Merton jumps.
Useful for portfolio stress-testing and expected drawdown distribution.

Usage:
    python3 monte_carlo.py --spot 60000 --vol 0.80 --drift 0.05 --days 30 --paths 10000
    python3 monte_carlo.py --spot 3500 --vol 1.0 --days 90 --paths 5000 --jumps
"""
import argparse
import json
import math
import random


def gbm_path(spot, drift, vol, days, dt=1 / 365):
    path = [spot]
    for _ in range(days):
        z = random.gauss(0, 1)
        path.append(path[-1] * math.exp((drift - 0.5 * vol * vol) * dt + vol * math.sqrt(dt) * z))
    return path


def jump_gbm_path(spot, drift, vol, days, jump_intensity=0.5, jump_mean=-0.05, jump_vol=0.15, dt=1 / 365):
    path = [spot]
    for _ in range(days):
        z = random.gauss(0, 1)
        # Poisson-approximated jump arrival
        jump = 0.0
        if random.random() < jump_intensity * dt:
            jump = random.gauss(jump_mean, jump_vol)
        path.append(path[-1] * math.exp((drift - 0.5 * vol * vol) * dt + vol * math.sqrt(dt) * z + jump))
    return path


def percentile(sorted_list, p):
    idx = int(p * len(sorted_list))
    idx = min(max(0, idx), len(sorted_list) - 1)
    return sorted_list[idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spot", type=float, required=True)
    ap.add_argument("--vol", type=float, required=True, help="annualized vol as decimal (0.8 = 80 pct)")
    ap.add_argument("--drift", type=float, default=0.0, help="annualized drift")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--paths", type=int, default=10000)
    ap.add_argument("--jumps", action="store_true", help="enable Merton jump-diffusion")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)

    ending_prices = []
    max_drawdowns = []
    for _ in range(args.paths):
        if args.jumps:
            path = jump_gbm_path(args.spot, args.drift, args.vol, args.days)
        else:
            path = gbm_path(args.spot, args.drift, args.vol, args.days)
        ending_prices.append(path[-1])
        peak = path[0]
        max_dd = 0.0
        for p in path:
            peak = max(peak, p)
            dd = (peak - p) / peak if peak > 0 else 0.0
            max_dd = max(max_dd, dd)
        max_drawdowns.append(max_dd)

    ep = sorted(ending_prices)
    dd = sorted(max_drawdowns)
    mean_ending = sum(ep) / len(ep)

    out = {
        "inputs": {"spot": args.spot, "vol": args.vol, "drift": args.drift, "days": args.days, "paths": args.paths, "jumps": args.jumps},
        "ending_price_distribution": {
            "p05": round(percentile(ep, 0.05), 4),
            "p25": round(percentile(ep, 0.25), 4),
            "p50": round(percentile(ep, 0.50), 4),
            "p75": round(percentile(ep, 0.75), 4),
            "p95": round(percentile(ep, 0.95), 4),
            "mean": round(mean_ending, 4),
            "vs_spot_pct_p50": round((percentile(ep, 0.50) / args.spot - 1) * 100, 3),
            "vs_spot_pct_p05": round((percentile(ep, 0.05) / args.spot - 1) * 100, 3),
            "vs_spot_pct_p95": round((percentile(ep, 0.95) / args.spot - 1) * 100, 3),
        },
        "max_drawdown_distribution": {
            "p50_max_dd_pct": round(percentile(dd, 0.50) * 100, 3),
            "p75_max_dd_pct": round(percentile(dd, 0.75) * 100, 3),
            "p95_max_dd_pct": round(percentile(dd, 0.95) * 100, 3),
            "p99_max_dd_pct": round(percentile(dd, 0.99) * 100, 3),
        },
        "prob_below_spot": round(sum(1 for p in ep if p < args.spot) / len(ep) * 100, 2),
        "prob_halving": round(sum(1 for p in ep if p < args.spot * 0.5) / len(ep) * 100, 2),
        "prob_doubling": round(sum(1 for p in ep if p > args.spot * 2) / len(ep) * 100, 2),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
