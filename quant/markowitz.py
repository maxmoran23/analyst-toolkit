#!/usr/bin/env python3
"""
Markowitz mean-variance portfolio optimization (min-variance, max-Sharpe, efficient frontier).

Uses pure-Python linear algebra (Cholesky / back-substitution) to stay dependency-free.
Short sales are allowed. Singular or indefinite covariance matrices are rejected;
no hidden regularization or third-party fallback changes the requested problem.

Usage:
    python3 markowitz.py --returns-csv returns.csv --rf 0.05
    # returns.csv: columns = assets, rows = daily returns (no header, comma-separated)
"""
import argparse
try:
    from ._validation import number, series, confidence_level
    from .correlation import parse_returns_csv
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _validation import number, series, confidence_level
    from correlation import parse_returns_csv
import csv
import json
import math
import sys


def mean_vec(matrix):
    if not matrix or not matrix[0]:
        raise ValueError("matrix must contain observations and assets")
    m = len(matrix[0])
    for row in matrix:
        series(row, "matrix row")
        if len(row) != m:
            raise ValueError("matrix rows must have equal lengths")
    n = len(matrix)
    return [sum(matrix[i][j] for i in range(n)) / n for j in range(m)]


def cov_matrix(matrix):
    if not matrix or not matrix[0]:
        raise ValueError("matrix must contain observations and assets")
    m = len(matrix[0])
    for row in matrix:
        series(row, "matrix row")
        if len(row) != m:
            raise ValueError("matrix rows must have equal lengths")
    n = len(matrix)
    if n < 2:
        raise ValueError("covariance requires at least two observations")
    mu = mean_vec(matrix)
    cov = [[0.0] * m for _ in range(m)]
    for j in range(m):
        for k in range(j, m):
            s = sum((matrix[i][j] - mu[j]) * (matrix[i][k] - mu[k]) for i in range(n))
            v = s / (n - 1)
            cov[j][k] = v
            cov[k][j] = v
    return cov, mu


def cholesky(A):
    n = len(A)
    if not n or any(len(row) != n for row in A):
        raise ValueError("matrix must be non-empty and square")
    for i, row in enumerate(A):
        series(row, "matrix row")
        for j in range(i):
            if not math.isclose(A[i][j], A[j][i], rel_tol=1e-12, abs_tol=1e-15):
                raise ValueError("matrix must be symmetric")
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                v = A[i][i] - s
                if v <= 0:
                    raise ValueError("matrix must be positive definite; remove redundant assets or explicitly regularize")
                L[i][j] = math.sqrt(v)
            else:
                L[i][j] = (A[i][j] - s) / L[j][j]
    return L


def forward_sub(L, b):
    n = len(L)
    x = [0.0] * n
    for i in range(n):
        x[i] = (b[i] - sum(L[i][k] * x[k] for k in range(i))) / L[i][i]
    return x


def backward_sub(U, b):
    n = len(U)
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - sum(U[i][k] * x[k] for k in range(i + 1, n))) / U[i][i]
    return x


def solve_linear(A, b):
    """Solve Ax=b via Cholesky. A must be positive definite."""
    series(b, "right-hand side")
    if len(b) != len(A):
        raise ValueError("right-hand side length must match matrix")
    L = cholesky(A)
    y = forward_sub(L, b)
    Lt = [[L[j][i] for j in range(len(L))] for i in range(len(L))]
    x = backward_sub(Lt, y)
    return x


def min_variance_portfolio(cov):
    """Global minimum variance: w = cov^-1 * 1 / (1' * cov^-1 * 1)"""
    n = len(cov)
    ones = [1.0] * n
    inv_cov_ones = solve_linear(cov, ones)
    denom = sum(inv_cov_ones)
    weights = [v / denom for v in inv_cov_ones]
    return weights


def max_sharpe_portfolio(cov, excess_returns):
    """
    Max-Sharpe tangency: w proportional to cov^-1 * excess_returns, normalized to sum=1.
    """
    inv_cov_r = solve_linear(cov, excess_returns)
    denom = sum(inv_cov_r)
    if denom <= 1e-12:
        return None
    return [v / denom for v in inv_cov_r]


def portfolio_stats(weights, mu, cov, rf=0.0, annualize=252):
    ret = sum(w * m for w, m in zip(weights, mu))
    var = 0.0
    n = len(weights)
    for i in range(n):
        for j in range(n):
            var += weights[i] * weights[j] * cov[i][j]
    vol = math.sqrt(max(0, var))
    sharpe = (ret * annualize - rf) / (vol * math.sqrt(annualize)) if vol > 0 else 0.0
    return {
        "expected_return_ann_pct": round(ret * annualize * 100, 3),
        "volatility_ann_pct": round(vol * math.sqrt(annualize) * 100, 3),
        "sharpe": round(sharpe, 3),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--returns-csv", required=True)
    ap.add_argument("--asset-names", help="comma-separated names (optional, else col0..colN)")
    ap.add_argument("--rf", type=float, default=0.05)
    ap.add_argument("--annualize", type=int, default=252)
    args = ap.parse_args()

    with open(args.returns_csv) as f:
        returns = parse_returns_csv(f, minimum_rows=0, minimum_assets=1)

    if not returns:
        print(json.dumps({"error": "no numeric data found"}))
        sys.exit(1)

    n_assets = len(returns[0])
    names = args.asset_names.split(",") if args.asset_names else [f"asset_{i}" for i in range(n_assets)]
    if len(names) != n_assets or len(set(names)) != n_assets or any(not name.strip() for name in names):
        raise ValueError("asset names must be unique, non-empty and match the data columns")
    number(args.rf, "rf")
    if args.annualize <= 0:
        raise ValueError("annualize must be positive")
    cov, mu = cov_matrix(returns)
    periodic_rf = args.rf / args.annualize
    excess = [m - periodic_rf for m in mu]

    out = {"n_assets": n_assets, "n_observations": len(returns), "asset_names": names}

    mv_w = min_variance_portfolio(cov)
    out["min_variance_portfolio"] = {
        "weights": {n: round(w, 4) for n, w in zip(names, mv_w)},
        **portfolio_stats(mv_w, mu, cov, args.rf, args.annualize),
    }

    ms_w = max_sharpe_portfolio(cov, excess)
    if ms_w:
        out["max_sharpe_portfolio"] = {
            "weights": {n: round(w, 4) for n, w in zip(names, ms_w)},
            **portfolio_stats(ms_w, mu, cov, args.rf, args.annualize),
        }

    # equal-weight benchmark
    ew_w = [1 / n_assets] * n_assets
    out["equal_weight_benchmark"] = {
        "weights": {n: round(1 / n_assets, 4) for n in names},
        **portfolio_stats(ew_w, mu, cov, args.rf, args.annualize),
    }

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
