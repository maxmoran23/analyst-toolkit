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
try:
    from ._validation import number, series, integer
except ImportError:
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _validation import number, series, integer

import csv
import json
import math
import sys


def corr(x, y):
    series(x, "x", minimum_length=0)
    series(y, "y", minimum_length=0)
    if len(x) != len(y):
        raise ValueError("paired series must have equal lengths")
    n = len(x)
    if n < 2 or all(v == x[0] for v in x) or all(v == y[0] for v in y):
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    dx = math.sqrt(sum((v - mx) ** 2 for v in x))
    dy = math.sqrt(sum((v - my) ** 2 for v in y))
    if dx == 0 or dy == 0:
        raise ValueError("nonconstant variance is below floating-point resolution")
    return number(num / (dx * dy), "correlation")


def correlation_value(x, y):
    """JSON report uses null for unidentified Pearson correlations instead of a zero sentinel."""
    value = corr(x, y)
    if len(x) < 2 or all(v == x[0] for v in x) or all(v == y[0] for v in y):
        return None
    return round(value, 4)


def parse_returns_csv(lines, *, minimum_rows=2, minimum_assets=2):
    """Accept one all-text header, then finite rectangular numeric rows; never drop bad data."""
    rows = []
    first = True
    for line_number, row in enumerate(csv.reader(lines), 1):
        if not row:
            continue
        parsed = []
        for value in row:
            try:
                parsed.append(float(value))
            except ValueError:
                parsed.append(None)
        if first and all(value is None for value in parsed):
            first = False
            continue
        first = False
        if any(value is None for value in parsed):
            raise ValueError(f"malformed numeric CSV row {line_number}")
        series(parsed, f"CSV row {line_number}")
        if rows and len(parsed) != len(rows[0]):
            raise ValueError(f"ragged CSV row {line_number}")
        rows.append(parsed)
    if len(rows) < minimum_rows or (rows and len(rows[0]) < minimum_assets):
        raise ValueError(f"need at least {minimum_rows} observations and {minimum_assets} asset columns")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--returns-csv", required=True)
    ap.add_argument("--asset-names", help="comma-separated")
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--crisis-threshold", type=float, default=-0.05,
                    help="day is 'crisis' if benchmark (col 0) return < threshold")
    args = ap.parse_args()

    integer(args.window, "window", minimum=2)
    number(args.crisis_threshold, "crisis threshold")
    with open(args.returns_csv) as f:
        cols = parse_returns_csv(f)

    n_rows = len(cols)
    n_assets = len(cols[0])
    names = args.asset_names.split(",") if args.asset_names else [f"a{i}" for i in range(n_assets)]
    if len(names) != n_assets or any(not name.strip() for name in names) or len(set(names)) != len(names):
        raise ValueError("asset names must be nonempty, unique and match the columns")
    series = [[row[j] for row in cols] for j in range(n_assets)]

    # full-sample pairwise correlation matrix
    full_corr = {}
    for i in range(n_assets):
        for j in range(i + 1, n_assets):
            full_corr[f"{names[i]}__{names[j]}"] = correlation_value(series[i], series[j])

    # crisis-only correlation: days where benchmark (asset 0) < threshold
    crisis_idx = [k for k in range(n_rows) if series[0][k] < args.crisis_threshold]
    crisis_corr = {}
    if len(crisis_idx) > 5:
        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                crisis_corr[f"{names[i]}__{names[j]}"] = correlation_value(
                    [series[i][k] for k in crisis_idx], [series[j][k] for k in crisis_idx]
                )

    # correlation compression flag: crisis - normal
    compression = {}
    for k in full_corr:
        if full_corr[k] is not None and crisis_corr.get(k) is not None:
            compression[k] = round(crisis_corr[k] - full_corr[k], 4)

    # rolling window correlation vs. benchmark (last window)
    rolling = {}
    if n_rows >= args.window:
        for i in range(1, n_assets):
            tail_bench = series[0][-args.window:]
            tail_asset = series[i][-args.window:]
            rolling[f"{names[i]}_vs_{names[0]}"] = correlation_value(tail_bench, tail_asset)

    print(json.dumps({
        "n_observations": n_rows,
        "n_assets": n_assets,
        "assets": names,
        "window": args.window,
        "crisis_threshold": args.crisis_threshold,
        "n_crisis_days": len(crisis_idx),
        "undefined_correlation_convention": "null means insufficient observations or zero variance; excluded from compression",
        "full_sample_correlation": full_corr,
        "crisis_correlation": crisis_corr,
        "correlation_compression": compression,
        "rolling_correlation_last_window": rolling,
        "interpretation_hint": "Compression > 0.2 is a descriptive review flag, not a calibrated threshold or proof that diversification fails.",
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
