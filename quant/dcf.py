#!/usr/bin/env python3
"""
DCF for token fee-capture businesses (L1s, DEXs, stablecoin issuers).

Inputs: projected annual fees/revenue for N years, discount rate, terminal growth, circulating supply.
Outputs: fair value per token + scenario range (bear/base/bull multipliers).

Usage:
    python3 dcf.py --fees-yearly '[120e6,150e6,180e6,200e6,210e6]' \
        --discount 0.15 --terminal-growth 0.04 --circulating-supply 1e9
    # Output includes fair value per token, scenarios, sensitivity to discount rate
"""
import argparse
import json


def dcf(fees_yearly, discount, terminal_growth, circulating_supply, capture_ratio=1.0):
    """
    fees_yearly: list of projected annual fee/revenue in dollars
    discount: annual discount rate (e.g. 0.15)
    terminal_growth: perpetual growth rate after last year (e.g. 0.03)
    circulating_supply: tokens outstanding (not max supply)
    capture_ratio: fraction of fees captured by token holders (burn + staking yield); 1.0 = 100% pass-through
    """
    years = len(fees_yearly)
    pv_fees = 0.0
    for t, fee in enumerate(fees_yearly, start=1):
        pv_fees += (fee * capture_ratio) / ((1 + discount) ** t)

    # terminal value at end of year N, assuming growing perpetuity
    terminal_fee = fees_yearly[-1] * (1 + terminal_growth) * capture_ratio
    if discount > terminal_growth:
        tv = terminal_fee / (discount - terminal_growth)
        pv_tv = tv / ((1 + discount) ** years)
    else:
        pv_tv = 0  # degenerate case
    enterprise_value = pv_fees + pv_tv
    fair_value_per_token = enterprise_value / circulating_supply
    return {
        "pv_of_explicit_fees": round(pv_fees, 2),
        "pv_of_terminal": round(pv_tv, 2),
        "enterprise_value": round(enterprise_value, 2),
        "fair_value_per_token": round(fair_value_per_token, 4),
        "terminal_weight_pct": round(pv_tv / enterprise_value * 100, 2) if enterprise_value > 0 else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fees-yearly", required=True, help="JSON array of yearly fees in USD")
    ap.add_argument("--discount", type=float, default=0.15)
    ap.add_argument("--terminal-growth", type=float, default=0.03)
    ap.add_argument("--circulating-supply", type=float, required=True)
    ap.add_argument("--capture-ratio", type=float, default=1.0, help="fraction of fees accruing to token holders (1.0 = 100 pct)")
    ap.add_argument("--current-price", type=float, help="optional: compare to current market price")
    args = ap.parse_args()

    fees = json.loads(args.fees_yearly)

    base = dcf(fees, args.discount, args.terminal_growth, args.circulating_supply, args.capture_ratio)

    # scenarios — bear: -40% fees, higher discount, lower terminal; bull: +40%, lower discount
    bear_fees = [f * 0.6 for f in fees]
    bull_fees = [f * 1.4 for f in fees]
    bear = dcf(bear_fees, args.discount + 0.05, max(0.01, args.terminal_growth - 0.02), args.circulating_supply, args.capture_ratio)
    bull = dcf(bull_fees, max(0.05, args.discount - 0.03), args.terminal_growth + 0.02, args.circulating_supply, args.capture_ratio)

    # sensitivity to discount rate
    sens = {}
    for d in [0.10, 0.12, 0.15, 0.18, 0.20, 0.25]:
        sens[f"discount_{d}"] = round(dcf(fees, d, args.terminal_growth, args.circulating_supply, args.capture_ratio)["fair_value_per_token"], 4)

    out = {
        "inputs": {
            "years": len(fees),
            "discount": args.discount,
            "terminal_growth": args.terminal_growth,
            "circulating_supply": args.circulating_supply,
            "capture_ratio": args.capture_ratio,
        },
        "base_case": base,
        "bear_case": bear,
        "bull_case": bull,
        "sensitivity_per_token": sens,
    }
    if args.current_price:
        out["current_price"] = args.current_price
        out["upside_base_pct"] = round((base["fair_value_per_token"] / args.current_price - 1) * 100, 2)
        out["upside_bull_pct"] = round((bull["fair_value_per_token"] / args.current_price - 1) * 100, 2)
        out["downside_bear_pct"] = round((bear["fair_value_per_token"] / args.current_price - 1) * 100, 2)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
