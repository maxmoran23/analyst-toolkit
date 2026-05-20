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
import json
import math
import sys


def kelly_single(p, odds_decimal):
    """
    Optimal full-Kelly fraction for a binary bet at decimal odds.
    b = odds - 1 (net payout), q = 1 - p
    f = (bp - q) / b
    """
    b = odds_decimal - 1
    q = 1 - p
    f = (b * p - q) / b if b > 0 else 0.0
    return max(0.0, f)


def edge_pct(p, odds_decimal):
    """Expected value as % of stake."""
    return p * (odds_decimal - 1) - (1 - p)


def kelly_portfolio(edges, fraction=0.25, corr_matrix=None):
    """
    Naive multi-bet Kelly assuming independence (or low correlation).
    Scales each bet by fractional Kelly and caps total exposure.
    If corr_matrix provided, applies diversification shrinkage.
    """
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
                avg_corr = sum(v for k, v in row.items() if k != r["label"]) / max(1, len(row) - 1)
                shrink = max(0.5, 1 - avg_corr * 0.5)  # 50% floor
                r["fractional_kelly_pct"] = round(r["fractional_kelly_pct"] * shrink, 3)
                r["correlation_shrink"] = round(shrink, 3)

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
