#!/usr/bin/env python3
"""
Kelly criterion — single-bet, fractional, and multi-bet correlated (Markowitz-Kelly).

Supports both betting edges (decimal odds) and asset returns (mean/vol).

Usage (single bet):
    python3 kelly.py --mode single --p 0.55 --odds-decimal 2.0 --fraction 0.25

Usage (portfolio of bets, possibly correlated):
    python3 kelly.py --mode portfolio --edges-json edges.json --fraction 0.25
    # edges.json: [{"label":"NBA-BOS-ML","p":0.58,"odds":1.91},{...}]
"""
import argparse
try:
    from ._validation import number, series, confidence_level
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _validation import number, series, confidence_level
import json
import math
import sys


def kelly_single(p, odds_decimal):
    """
    Optimal full-Kelly fraction for a binary bet at decimal odds.
    b = odds - 1 (net payout), q = 1 - p
    f = (bp - q) / b
    """
    number(p, "p", minimum=0, maximum=1)
    number(odds_decimal, "odds_decimal")
    if odds_decimal <= 1:
        raise ValueError("decimal odds must exceed 1")
    b = odds_decimal - 1
    q = 1 - p
    f = (b * p - q) / b if b > 0 else 0.0
    return max(0.0, f)


def edge_pct(p, odds_decimal):
    """Expected value as % of stake."""
    kelly_single(p, odds_decimal)
    return p * (odds_decimal - 1) - (1 - p)


def kelly_portfolio(edges, fraction=0.25, corr_matrix=None):
    """
    Naive multi-bet Kelly assuming independence (or low correlation).
    Scales each bet by fractional Kelly and caps total exposure.
    If corr_matrix provided, applies diversification shrinkage.
    """
    number(fraction, "fraction", minimum=0, maximum=1)
    labels = [e.get("label", f"bet_{i}") for i, e in enumerate(edges)]
    if len(set(labels)) != len(labels):
        raise ValueError("bet labels must be unique")
    if corr_matrix is not None:
        if not isinstance(corr_matrix, dict):
            raise ValueError("correlation matrix must map labels to rows")
        for label, row in corr_matrix.items():
            if label not in labels or not isinstance(row, dict):
                raise ValueError("correlation rows must use known bet labels")
            for other, correlation in row.items():
                if other not in labels:
                    raise ValueError("correlation columns must use known bet labels")
                number(correlation, "correlation", minimum=-1, maximum=1)
                if label == other and correlation != 1:
                    raise ValueError("correlation diagonal must equal 1")
                reverse = corr_matrix.get(other, {}).get(label)
                if reverse is not None and not math.isclose(correlation, reverse, abs_tol=1e-12):
                    raise ValueError("correlations must be symmetric when both entries are supplied")
    results = []
    total_raw = 0.0
    for e in edges:
        k = kelly_single(e["p"], e["odds"])
        ev = edge_pct(e["p"], e["odds"])
        stake = k * fraction
        results.append({
            "label": e.get("label", f"bet_{len(results)}"),
            "p": e["p"],
            "odds": e["odds"],
            "ev_pct": round(ev * 100, 3),
            "full_kelly_pct": round(k * 100, 3),
            "fractional_kelly_pct": round(stake * 100, 3),
        })
        total_raw += stake

    # Total exposure cap: sum of fractional Kellys shouldn't exceed 50% of bankroll
    if total_raw > 0.50:
        scale = 0.50 / total_raw
        for r in results:
            r["fractional_kelly_pct"] = round(r["fractional_kelly_pct"] * scale, 3)
            r["scaled_for_total_exposure"] = True

    # Correlation shrinkage: if provided, cut each stake proportional to its avg correlation to others
    if corr_matrix:
        for i, r in enumerate(results):
            row = corr_matrix.get(r["label"], {})
            if row:
                others = [v for k, v in row.items() if k != r["label"]]
                avg_corr = sum(others) / len(others) if others else 0.0
                shrink = max(0.5, 1 - max(0.0, avg_corr) * 0.5)  # haircut only; no leverage from negative correlations
                r["fractional_kelly_pct"] = round(r["fractional_kelly_pct"] * shrink, 3)
                r["correlation_shrink"] = round(shrink, 3)

    # Display rounding must not turn the stated 50% ceiling into an excess.
    excess_units = max(0, sum(round(r["fractional_kelly_pct"] * 1000) for r in results) - 50000)
    for r in sorted(results, key=lambda row: row["fractional_kelly_pct"], reverse=True):
        reduction = min(excess_units, round(r["fractional_kelly_pct"] * 1000))
        r["fractional_kelly_pct"] = round(r["fractional_kelly_pct"] - reduction / 1000, 3)
        excess_units -= reduction
    total_exposure = sum(r["fractional_kelly_pct"] for r in results)
    return {
        "fraction": fraction,
        "bets": results,
        "total_exposure_pct": round(total_exposure, 3),
        "n_bets": len(results),
        "diversification_benefit": "applied" if corr_matrix else "not_applied",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["single", "portfolio"], required=True)
    ap.add_argument("--p", type=float, help="win probability (single mode)")
    ap.add_argument("--odds-decimal", type=float, help="decimal odds (single mode)")
    ap.add_argument("--edges-json", help="path to edges JSON (portfolio mode)")
    ap.add_argument("--correlation-matrix", help="path to correlation matrix JSON (portfolio mode)")
    ap.add_argument("--fraction", type=float, default=0.25, help="Kelly fraction (default 0.25 = quarter)")
    args = ap.parse_args()

    number(args.fraction, "fraction", minimum=0, maximum=1)
    if args.mode == "single":
        if args.p is None or args.odds_decimal is None:
            print(json.dumps({"error": "need --p and --odds-decimal"}))
            sys.exit(1)
        k = kelly_single(args.p, args.odds_decimal)
        ev = edge_pct(args.p, args.odds_decimal)
        out = {
            "p": args.p,
            "odds": args.odds_decimal,
            "edge_pct": round(ev * 100, 3),
            "full_kelly_pct": round(k * 100, 3),
            "fractional_kelly_pct": round(k * args.fraction * 100, 3),
            "fraction": args.fraction,
        }
    else:
        if not args.edges_json:
            print(json.dumps({"error": "need --edges-json"}))
            sys.exit(1)
        with open(args.edges_json) as f:
            edges = json.load(f)
        corr = None
        if args.correlation_matrix:
            with open(args.correlation_matrix) as f:
                corr = json.load(f)
        out = kelly_portfolio(edges, args.fraction, corr)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
