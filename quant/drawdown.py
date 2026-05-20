#!/usr/bin/env python3
"""
Max drawdown, underwater curve, recovery time distribution.

Usage:
    python3 drawdown.py --equity-json equity.json
    python3 drawdown.py --returns-json returns.json
"""
import argparse
import json
import sys


def equity_from_returns(returns, start=1.0):
    eq = [start]
    for r in returns:
        eq.append(eq[-1] * (1 + r))
    return eq


def drawdown_series(equity):
    dds = []
    peak = equity[0]
    for v in equity:
        peak = max(peak, v)
        dd = (peak - v) / peak if peak > 0 else 0.0
        dds.append(dd)
    return dds


def recovery_episodes(equity):
    """Return list of (peak_idx, trough_idx, recovery_idx, dd_pct, duration_days)."""
    episodes = []
    peak = equity[0]
    peak_idx = 0
    in_dd = False
    trough = peak
    trough_idx = 0
    for i, v in enumerate(equity):
        if v >= peak:
            if in_dd and trough < peak:
                dd_pct = (peak - trough) / peak
                episodes.append({
                    "peak_idx": peak_idx,
                    "trough_idx": trough_idx,
                    "recovery_idx": i,
                    "dd_pct": round(dd_pct * 100, 3),
                    "duration_to_trough": trough_idx - peak_idx,
                    "duration_to_recovery": i - peak_idx,
                })
                in_dd = False
            peak = v
            peak_idx = i
            trough = v
            trough_idx = i
        else:
            in_dd = True
            if v < trough:
                trough = v
                trough_idx = i
    # Unrecovered tail
    if in_dd and trough < peak:
        episodes.append({
            "peak_idx": peak_idx,
            "trough_idx": trough_idx,
            "recovery_idx": None,
            "dd_pct": round((peak - trough) / peak * 100, 3),
            "duration_to_trough": trough_idx - peak_idx,
            "duration_to_recovery": None,
            "still_underwater": True,
        })
    return episodes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--equity-json")
    ap.add_argument("--returns-json")
    ap.add_argument("--top-n", type=int, default=5, help="top N drawdown episodes to report")
    args = ap.parse_args()

    if args.equity_json:
        with open(args.equity_json) as f:
            equity = json.load(f)
    elif args.returns_json:
        with open(args.returns_json) as f:
            returns = json.load(f)
        equity = equity_from_returns(returns)
    else:
        print(json.dumps({"error": "need --equity-json or --returns-json"}))
        sys.exit(1)

    dds = drawdown_series(equity)
    eps = recovery_episodes(equity)
    eps_sorted = sorted(eps, key=lambda e: e["dd_pct"], reverse=True)

    out = {
        "n_observations": len(equity),
        "max_drawdown_pct": round(max(dds) * 100, 3),
        "current_drawdown_pct": round(dds[-1] * 100, 3),
        "avg_drawdown_pct": round(sum(dds) / len(dds) * 100, 3),
        "pct_time_underwater": round(sum(1 for d in dds if d > 0.001) / len(dds) * 100, 2),
        "n_drawdown_episodes": len(eps),
        "top_drawdowns": eps_sorted[: args.top_n],
        "avg_recovery_days": round(
            sum(e["duration_to_recovery"] for e in eps if e.get("duration_to_recovery")) /
            max(1, sum(1 for e in eps if e.get("duration_to_recovery"))), 2
        ),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
