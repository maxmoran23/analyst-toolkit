"""
Synthetic data generator for on-chain KYT address-risk validation.

Produces addresses.csv with KNOWN ground truth. For each address it constructs a
small transaction subgraph (an illicit/benign seed, optional commingling breaker,
intermediates, and the address) and runs the REAL taint propagation in
`_lib/graph` to derive the exposure features — exactly as a chain-analytics layer
would in production. The disposition engine then consumes those features.

False-positive categories (each must auto-clear for a NAMED reason):
  benign_category     exposure is to a licensed exchange / blue-chip DeFi / merchant
  broken_intermediary illicit funds reach the address only through a commingling CEX
  de_minimis          traceable value share below materiality
  diluted_distant     illicit source too many hops away / exposure decayed out
  ambiguous_residual  mid-severity moderate exposure — not clearable, not escalatable

True-risk flavours (material, proximate, unbroken exposure to a serious category;
neither can be auto-cleared):
  clear_serious  direct/near exposure to sanctioned / mixer / darknet / ransomware -> ESCALATE
  emerging       moderate exposure to stolen-funds / scam / fraud-proceeds -> ANALYST_REVIEW
"""
from __future__ import annotations

import argparse
import csv
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.graph import address_exposure  # noqa: E402
import scorer as S  # noqa: E402  (for CATEGORY_SEVERITY)

HOP_DECAY = 0.7
SERIOUS = ["sanctioned_address", "mixer", "darknet_market", "ransomware"]
EMERGING = ["stolen_funds", "scam", "fraud_proceeds"]
BENIGN = ["licensed_exchange", "defi_bluechip", "merchant_processor", "mining_pool"]
MID = ["high_risk_exchange", "gambling"]


def _chain(hops, frac, breaker_idx=None):
    """Build a directed path S -> ... -> T of `hops` edges, each carrying `frac`.
    If breaker_idx is set, that intermediate node is a commingling breaker."""
    nodes = ["S"] + ["n%d" % i for i in range(1, hops)] + ["T"]
    breakers = set()
    if breaker_idx is not None:
        nodes[breaker_idx] = "X"
        breakers.add("X")
    edges = [(nodes[i], nodes[i + 1], frac) for i in range(hops)]
    return edges, breakers


def _features(category, hops, frac, breaker_idx=None):
    sev = S.CATEGORY_SEVERITY.get(category, 0.3)
    edges, breakers = _chain(hops, frac, breaker_idx)
    ex = address_exposure(edges, {"S": sev}, "T", breakers=breakers, hop_decay=HOP_DECAY)
    amount_fraction = frac ** hops
    return {"top_category": category, "exposure": round(ex["exposure"], 6),
            "hops": ex["hops"] if ex["hops"] is not None else "",
            "amount_fraction": round(amount_fraction, 6),
            "via_breaker": int(ex["via_breaker"])}


def make_addresses(n, rng, true_rate=0.06):
    rows = []
    for i in range(n):
        aid = "0x%012x" % rng.randrange(16 ** 12)
        direction = rng.choice(["inbound", "outbound"])
        if rng.random() < true_rate:
            if rng.random() < 0.6:  # clear_serious
                cat = rng.choice(SERIOUS); hops = rng.randint(1, 2)
                frac = rng.uniform(0.8, 0.97); fpc = ""
            else:                   # emerging
                cat = rng.choice(EMERGING); hops = rng.randint(2, 3)
                frac = rng.uniform(0.6, 0.82); fpc = ""
            f = _features(cat, hops, frac)
            label = 1
        else:
            roll = rng.random()
            if roll < 0.28:                       # benign_category
                cat = rng.choice(BENIGN); f = _features(cat, rng.randint(1, 3), rng.uniform(0.6, 0.95))
                fpc = "benign_category"
            elif roll < 0.48:                     # broken_intermediary
                cat = rng.choice(SERIOUS)
                f = _features(cat, 3, rng.uniform(0.7, 0.95), breaker_idx=2)
                fpc = "broken_intermediary"
            elif roll < 0.66:                     # de_minimis
                cat = rng.choice(SERIOUS); f = _features(cat, 1, rng.uniform(0.004, 0.018))
                fpc = "de_minimis"
            elif roll < 0.88:                     # diluted_distant
                cat = rng.choice(SERIOUS); f = _features(cat, rng.randint(5, 6), rng.uniform(0.5, 0.7))
                fpc = "diluted_distant"
            else:                                 # ambiguous_residual: mid-severity,
                # 2-hop, material share -> exposure lands between the dilution and
                # escalation lines, so it is neither clearable nor escalatable.
                cat = "high_risk_exchange"
                f = _features(cat, 2, rng.uniform(0.62, 0.80))
                fpc = "ambiguous_residual"
            label = 0
        rows.append({"address_id": aid, **f, "direction": direction,
                     "label": label, "fp_category": fpc})
    return rows


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--addresses", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    rows = make_addresses(args.addresses, rng)
    write_csv(os.path.join(args.out, "addresses.csv"), rows)
    t = sum(r["label"] for r in rows)
    print(f"addresses: {len(rows)} ({t} true-risk, {len(rows)-t} false positives) "
          f"-> {args.out}/addresses.csv   [seed={args.seed}]")


if __name__ == "__main__":
    main()
