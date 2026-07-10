"""
Synthetic data generator for NPA product-risk validation.

Produces products.csv — a population of fictional product / activity proposals at
the fictional Harborview Financial Group — with KNOWN designed-risk strata. A
pre-launch product-risk tier has no objective "true" value the way a sanctions
match does — it is a calibrated judgement — so the ground truth here is a coarse
DESIGNED stratum based on attribute presence, which is independent of the engine's
weighted formula. That lets the validation test the properties that matter:

  designed_low     benign attributes only                    -> should score low, tier LOW
  designed_medium  mixed / elevated factors, includes
                   all-middling profiles near the band edges -> mid scores
  designed_high    multiple high SOFT factors, NO hard
                   attribute                                 -> high scores
  hard_high        an otherwise-benign profile carrying ONE
                   buried floor-triggering attribute
                   (sanctions-exposed jurisdiction or asset,
                   digital-asset custody novelty, or the
                   new-segment + new-geography combination)  -> MUST never be tiered LOW
  prohibited       carries a documented prohibited attribute -> MUST route REFER_PROHIBITED

The hard_high stratum is the adversarial plant by construction: the base profile
is deliberately benign so the composite alone would land LOW — the floor has to
catch it. Everything is invented and seeded; same --seed reproduces byte-identical
files.
"""
from __future__ import annotations

import argparse
import csv
import os
import random

STRATA = ["designed_low", "designed_medium", "designed_high", "hard_high", "prohibited"]
STRATA_W = [0.45, 0.27, 0.12, 0.10, 0.06]

LOW_J = ["CA", "AU", "NL", "NZ"]
STANDARD_J = ["US", "GB", "DE", "SG", "FR", "JP"]
ELEVATED_J = ["AE", "TR", "PA", "HK"]
SANCTIONS_J = ["RU", "BY", "VE", "MM"]
PROHIBITED_J = ["KP", "IR", "SY", "CU"]

HARD_TYPES = ["sanctions_geo", "sanctions_asset", "da_custody_novelty", "segment_geo_combo"]
PROHIBITED_TYPES = ["prohibited_jurisdiction", "anonymity_instrument", "bearer_feature"]


def _blank(pid, stratum):
    return {"product_id": pid, "stratum": stratum, "hard_type": "",
            "client_segment": "RETAIL", "target_jurisdictions": "",
            "delivery_channel": "BRANCH", "asset_settlement_type": "FIAT",
            "novelty_to_firm": "EXISTING", "third_party_dependency": "NONE",
            "data_privacy_surface": 0.0, "cash_intensity": 0.0,
            "anonymity_features": 0, "cross_border_reach": 0.0,
            "model_ai_reliance": "NONE", "involves_custody": 0,
            "sanctions_exposed_asset": 0, "new_client_segment": 0,
            "new_geography": 0, "anonymity_enhanced_instrument": 0,
            "bearer_negotiable_feature": 0}


def _benign_base(c, rng):
    """An otherwise-unremarkable proposal — the camouflage for buried hard
    attributes in the hard_high stratum."""
    c["client_segment"] = rng.choice(["RETAIL", "INSTITUTIONAL", "HNW"])
    c["target_jurisdictions"] = rng.choice(LOW_J + STANDARD_J)
    c["delivery_channel"] = rng.choice(["BRANCH", "ONLINE"])
    c["asset_settlement_type"] = rng.choice(["FIAT", "SECURITIES"])
    c["novelty_to_firm"] = rng.choice(["EXISTING", "ADJACENT"])
    c["third_party_dependency"] = rng.choice(["NONE", "REGULATED"])
    c["data_privacy_surface"] = round(rng.uniform(0.0, 0.5), 2)
    c["cash_intensity"] = round(rng.uniform(0.0, 0.3), 2)
    c["cross_border_reach"] = round(rng.uniform(0.0, 0.4), 2)
    c["model_ai_reliance"] = rng.choice(["NONE", "ASSISTIVE"])


def make_products(n, rng):
    out = []
    for i in range(n):
        s = rng.choices(STRATA, STRATA_W)[0]
        c = _blank("NPA-%06d" % i, s)
        if s == "designed_low":
            c["client_segment"] = rng.choice(["RETAIL", "INSTITUTIONAL"])
            c["target_jurisdictions"] = rng.choice(LOW_J + STANDARD_J)
            c["delivery_channel"] = rng.choice(["BRANCH", "BRANCH", "ONLINE"])
            c["asset_settlement_type"] = rng.choice(["FIAT", "SECURITIES"])
            c["novelty_to_firm"] = "EXISTING"
            c["third_party_dependency"] = rng.choice(["NONE", "NONE", "REGULATED"])
            c["data_privacy_surface"] = round(rng.uniform(0.0, 0.25), 2)
            c["cash_intensity"] = round(rng.uniform(0.0, 0.15), 2)
            c["cross_border_reach"] = round(rng.uniform(0.0, 0.2), 2)
        elif s == "designed_medium":
            # Mixed / elevated factors; by design many land near the band edges
            # (all-middling profiles), which is the banding stress test.
            c["client_segment"] = rng.choice(["RETAIL", "INSTITUTIONAL", "HNW"])
            c["target_jurisdictions"] = rng.choice(
                [rng.choice(STANDARD_J), rng.choice(ELEVATED_J)])
            c["delivery_channel"] = rng.choice(["ONLINE", "INTERMEDIATED"])
            c["asset_settlement_type"] = rng.choice(["SECURITIES", "DERIVATIVES", "PHYSICAL"])
            c["novelty_to_firm"] = "ADJACENT"
            c["third_party_dependency"] = "REGULATED"
            c["data_privacy_surface"] = round(rng.uniform(0.25, 0.6), 2)
            c["cash_intensity"] = round(rng.uniform(0.15, 0.45), 2)
            c["cross_border_reach"] = round(rng.uniform(0.2, 0.55), 2)
            c["model_ai_reliance"] = rng.choice(["NONE", "ASSISTIVE"])
        elif s == "designed_high":
            # High SOFT factors but NO floor-triggering attribute (no sanctions
            # exposure, no digital-asset custody novelty, no segment+geo combo,
            # nothing prohibited) -> reaches MEDIUM/HIGH on the composite alone.
            c["client_segment"] = rng.choice(["NON_RESIDENT", "UNREGULATED_ENTITY"])
            c["target_jurisdictions"] = rng.choice(ELEVATED_J)
            c["delivery_channel"] = rng.choice(["API", "INTERMEDIATED"])
            c["asset_settlement_type"] = rng.choice(["DIGITAL_ASSET", "DERIVATIVES"])
            c["novelty_to_firm"] = rng.choice(["NEW_CAPABILITY", "ADJACENT"])
            c["third_party_dependency"] = "UNREGULATED"
            c["data_privacy_surface"] = round(rng.uniform(0.5, 0.9), 2)
            c["cash_intensity"] = round(rng.uniform(0.35, 0.75), 2)
            c["anonymity_features"] = rng.choice([0, 1])
            c["cross_border_reach"] = round(rng.uniform(0.5, 0.9), 2)
            c["model_ai_reliance"] = rng.choice(["ASSISTIVE", "AUTONOMOUS_DECISIONING"])
        elif s == "hard_high":
            # Adversarial plant: benign base + ONE buried floor-triggering
            # attribute. The composite alone would tier most of these LOW.
            _benign_base(c, rng)
            hard = rng.choice(HARD_TYPES)
            c["hard_type"] = hard
            if hard == "sanctions_geo":
                c["target_jurisdictions"] += "|" + rng.choice(SANCTIONS_J)
            elif hard == "sanctions_asset":
                c["sanctions_exposed_asset"] = 1
            elif hard == "da_custody_novelty":
                c["asset_settlement_type"] = "DIGITAL_ASSET"
                c["involves_custody"] = 1
                c["novelty_to_firm"] = "NEW_CAPABILITY"
            else:  # segment_geo_combo
                c["new_client_segment"] = 1
                c["new_geography"] = 1
        else:  # prohibited
            _benign_base(c, rng)
            pro = rng.choice(PROHIBITED_TYPES)
            c["hard_type"] = pro
            if pro == "prohibited_jurisdiction":
                c["target_jurisdictions"] += "|" + rng.choice(PROHIBITED_J)
            elif pro == "anonymity_instrument":
                c["asset_settlement_type"] = "DIGITAL_ASSET"
                c["anonymity_enhanced_instrument"] = 1
            else:
                c["bearer_negotiable_feature"] = 1
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
    ap.add_argument("--products", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    prods = make_products(args.products, rng)
    write_csv(os.path.join(args.out, "products.csv"), prods)
    from collections import Counter
    dist = Counter(p["stratum"] for p in prods)
    print(f"products: {len(prods)} -> {args.out}/products.csv   [seed={args.seed}]")
    print("strata:", dict(dist))


if __name__ == "__main__":
    main()
