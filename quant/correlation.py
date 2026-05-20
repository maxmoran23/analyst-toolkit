#!/usr/bin/env python3
"""
Rolling correlation + crisis-correlation check.

Tests the hypothesis "this asset diversifies my portfolio" —
calculates correlation in normal vs. stressed periods.
A portfolio that looks diversified in calm markets often compresses to ~1 in crashes.

Usage:
    python3 correlation.py --returns-csv returns.csv --window 30
    python3 correlation.py --returns-csv crypto_daily.csv --window 30 --crisis-threshold -0.05
"""
import argparse
import csv
import json
import math
import sys


def corr(x, y):
    n = len(x)
    if n < 2:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    dx = math.sqrt(sum((v - mx) ** 2 for v in x))
    dy = math.sqrt(sum((v - my) ** 2 for v in y))
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--returns-csv", required=True)
    ap.add_argument("--asset-names", help="comma-separated")
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--crisis-threshold", type=float, default=-0.05,
                    help="day is 'crisis' if benchmark (col 0) return < threshold")
    args = ap.parse_args()

    cols = []
    with open(args.returns_csv) as f:
        for row in csv.reader(f):
            if not row:
                continue
            try:
                vals = [float(x) for x in row]
                cols.append(vals)
            except ValueError:
                continue

    n_rows = len(cols)
    n_assets = len(cols[0])
    names = args.asset_names.split(",") if args.asset_names else [f"a{i}" for i in range(n_assets)]
    series = [[row[j] for row in cols] for j in range(n_assets)]

    # full-sample pairwise correlation matrix
    full_corr = {}
    for i in range(n_assets):
        for j in range(i + 1, n_assets):
            full_corr[f"{names[i]}__{names[j]}"] = round(corr(series[i], series[j]), 4)

    # crisis-only correlation: days where benchmark (asset 0) < threshold
    crisis_idx = [k for k in range(n_rows) if series[0][k] < args.crisis_threshold]
    crisis_corr = {}
    if len(crisis_idx) > 5:
        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                crisis_corr[f"{names[i]}__{names[j]}"] = round(
                    corr([series[i][k] for k in crisis_idx], [series[j][k] for k in crisis_idx]), 4
                )

    # correlation compression flag: crisis - normal
    compression = {}
    for k in full_corr:
        if k in crisis_corr:
            compression[k] = round(crisis_corr[k] - full_corr[k], 4)

    # rolling window correlation vs. benchmark (last window)
    rolling = {}
    if n_rows >= args.window:
        for i in range(1, n_assets):
            tail_bench = series[0][-args.window:]
            tail_asset = series[i][-args.window:]
            rolling[f"{names[i]}_vs_{names[0]}"] = round(corr(tail_bench, tail_asset), 4)

    print(json.dumps({
        "n_observations": n_rows,
        "n_assets": n_assets,
        "assets": names,
        "window": args.window,
        "crisis_threshold": args.crisis_threshold,
        "n_crisis_days": len(crisis_idx),
        "full_sample_correlation": full_corr,
        "crisis_correlation": crisis_corr,
        "correlation_compression": compression,
        "rolling_correlation_last_window": rolling,
        "interpretation_hint": "If compression > 0.2, diversification collapses in crashes. Treat 'uncorrelated' tag with suspicion.",
    }, indent=2))


if __name__ == "__main__":
    main()
