"""
Synthetic data generator for customer risk-rating validation.

Produces customers.csv with KNOWN designed-risk strata. A risk rating has no
objective "true tier" the way a sanctions match does — it is a judgement — so the
ground truth here is a coarse DESIGNED stratum based on attribute presence, which
is independent of the engine's weighted formula. That lets the validation test the
properties that matter for a rating model:

  designed_low     benign attributes only          -> should score low, tier LOW
  designed_medium  mixed / elevated factors         -> mid scores
  designed_high    multiple high SOFT factors, NO hard attribute -> high scores
  hard_high        carries a hard attribute (sanctions-nexus / prior-SAR / adverse
                   media / opaque shell / PEP) -> MUST never be rated LOW (floor)

Everything is invented and seeded; same --seed reproduces byte-identical files.
"""
from __future__ import annotations

import argparse
import csv
import os
import random

STRATA = ["designed_low", "designed_medium", "designed_high", "hard_high"]
STRATA_W = [0.55, 0.25, 0.12, 0.08]

LOW_GEO = ["CA", "AU", "NL", "US", "GB", "DE"]
ELEVATED_GEO = ["AE", "RU", "PA", "MM"]
HIGH_GEO = ["IR", "KP", "SY", "AF"]


def _blank(cid, stratum):
    return {"customer_id": cid, "stratum": stratum, "customer_type": "INDIVIDUAL",
            "domicile_country": "US", "operating_countries": "", "products": "",
            "channel": "FACE_TO_FACE", "pep": 0, "adverse_media": 0, "prior_sar": 0,
            "ownership_opacity": 0.0, "expected_activity_intensity": 0.0}


def make_customers(n, rng):
    out = []
    for i in range(n):
        s = rng.choices(STRATA, STRATA_W)[0]
        c = _blank("CUST-%06d" % i, s)
        if s == "designed_low":
            c["customer_type"] = rng.choice(["INDIVIDUAL", "SMB"])
            c["domicile_country"] = rng.choice(LOW_GEO)
            c["products"] = rng.choice(["retail_deposit", "lending", "retail_deposit|lending"])
            c["channel"] = "FACE_TO_FACE"
            c["ownership_opacity"] = round(rng.uniform(0.0, 0.2), 2)
            c["expected_activity_intensity"] = round(rng.uniform(0.0, 0.3), 2)
        elif s == "designed_medium":
            c["customer_type"] = rng.choice(["CORPORATE", "SMB", "TRUST"])
            c["domicile_country"] = rng.choice(LOW_GEO)
            c["operating_countries"] = rng.choice(["", rng.choice(ELEVATED_GEO)])
            c["products"] = rng.choice(["wire", "trade_finance", "wire|trade_finance", "private_banking"])
            c["channel"] = rng.choice(["FACE_TO_FACE", "REMOTE"])
            c["ownership_opacity"] = round(rng.uniform(0.2, 0.5), 2)
            c["expected_activity_intensity"] = round(rng.uniform(0.3, 0.6), 2)
        elif s == "designed_high":
            # high SOFT factors but NO hard attribute (no HIGH-geo, no PEP/SAR/adverse,
            # not opaque-shell) -> reaches MEDIUM/HIGH on the composite alone.
            c["customer_type"] = rng.choice(["MSB", "NBFI", "TRUST"])
            c["domicile_country"] = rng.choice(LOW_GEO)
            c["operating_countries"] = rng.choice(ELEVATED_GEO)
            c["products"] = rng.choice(["crypto", "correspondent", "cash", "crypto|wire"])
            c["channel"] = "REMOTE"
            c["ownership_opacity"] = round(rng.uniform(0.5, 0.8), 2)
            c["expected_activity_intensity"] = round(rng.uniform(0.6, 0.95), 2)
        else:  # hard_high
            c["customer_type"] = rng.choice(["CORPORATE", "MSB", "NBFI", "SHELL", "INDIVIDUAL"])
            c["products"] = rng.choice(["wire", "crypto", "private_banking", "trade_finance"])
            c["channel"] = rng.choice(["FACE_TO_FACE", "REMOTE"])
            c["ownership_opacity"] = round(rng.uniform(0.0, 0.9), 2)
            c["expected_activity_intensity"] = round(rng.uniform(0.2, 0.8), 2)
            hard = rng.choice(["sanctions_nexus", "prior_sar", "adverse_media", "shell", "pep"])
            if hard == "sanctions_nexus":
                c["operating_countries"] = rng.choice(HIGH_GEO)
            elif hard == "prior_sar":
                c["prior_sar"] = 1
            elif hard == "adverse_media":
                c["adverse_media"] = 1
            elif hard == "shell":
                c["customer_type"] = "SHELL"
                c["ownership_opacity"] = round(rng.uniform(0.6, 1.0), 2)
            else:
                c["pep"] = 1
        out.append(c)
    return out


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    cust = make_customers(args.customers, rng)
    write_csv(os.path.join(args.out, "customers.csv"), cust)
    from collections import Counter
    dist = Counter(c["stratum"] for c in cust)
    print(f"customers: {len(cust)} -> {args.out}/customers.csv   [seed={args.seed}]")
    print("strata:", dict(dist))


if __name__ == "__main__":
    main()
