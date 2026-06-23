"""
Synthetic data generator for transaction-monitoring validation.

Produces two CSVs with KNOWN ground truth:
  customers.csv  — synthetic customer profiles (segment, risk, expected baseline,
                   documented business type)
  alerts.csv     — monitoring alerts, each a window of aggregated transaction
                   features for one customer, labelled with whether the activity
                   is genuinely suspicious and, for false positives, WHY it is one.

Everything is invented and seeded; re-running with the same --seed reproduces
byte-identical files. The population mirrors the real shape of transaction
monitoring: the large majority of alerts are false positives, with a thin band of
genuinely suspicious activity.

False-positive categories (each must auto-close for a NAMED reason):
  within_profile      activity inside the customer's expected baseline
  below_typology      a typology indicator present but below its pattern threshold
  documented_context  a firing rule explained by the customer's documented business
  ambiguous_residual  unexplained deviation, no typology — the irreducible band a
                      human must work (must NOT auto-close)

True-suspicious flavours (both fire a typology rule, so neither can be auto-closed):
  clear_typology  textbook structuring / funnel / pass-through  -> ESCALATE
  emerging        the same patterns at the edge of their threshold -> ANALYST_REVIEW
"""
from __future__ import annotations

import argparse
import csv
import os
import random

SEGMENTS = ["RETAIL", "SMB", "CORPORATE", "MSB"]
SEG_WEIGHTS = [0.50, 0.30, 0.12, 0.08]
# expected monthly (amount range, count range) by segment
SEG_BASELINE = {
    "RETAIL": ((8_000, 40_000), (8, 25)),
    "SMB": ((80_000, 300_000), (30, 80)),
    "CORPORATE": ((1_000_000, 5_000_000), (60, 200)),
    "MSB": ((300_000, 1_000_000), (100, 400)),
}
RISK = ["LOW", "MEDIUM", "HIGH"]
RISK_WEIGHTS = [0.7, 0.22, 0.08]
BUSINESS_TYPES = ["", "import_export", "cash_intensive", "remittance", "payroll"]
BIZ_WEIGHTS = [0.55, 0.13, 0.12, 0.10, 0.10]
CTR = 10000.0


def make_customers(n, rng):
    out = []
    for i in range(n):
        seg = rng.choices(SEGMENTS, SEG_WEIGHTS)[0]
        (amin, amax), (cmin, cmax) = SEG_BASELINE[seg]
        out.append({
            "customer_id": "CUST-%06d" % i,
            "segment": seg,
            "risk_rating": rng.choices(RISK, RISK_WEIGHTS)[0],
            "expected_amount": round(rng.uniform(amin, amax), 2),
            "expected_count": rng.randint(cmin, cmax),
            "home_country": rng.choice(["US", "GB", "DE", "CA", "SG", "AE"]),
            "business_type": rng.choices(BUSINESS_TYPES, BIZ_WEIGHTS)[0],
        })
    return out


def _blank():
    return {"total_in": 0.0, "total_out": 0.0, "txn_count": 0, "near_threshold_count": 0,
            "distinct_in_cp": 1, "distinct_out_cp": 1, "passthrough_ratio": 0.0,
            "same_day": 0, "high_risk_geo_fraction": 0.0}


def make_alerts(n, customers, rng, true_rate=0.04):
    with_biz = [c for c in customers if c["business_type"]]
    alerts = []
    for i in range(n):
        aid = "TMALR-%07d" % i
        f = _blank()

        if rng.random() < true_rate:
            # ---------------- TRUE SUSPICIOUS ----------------
            c = rng.choice(customers)
            clear = rng.random() < 0.60
            typ = rng.choice(["structuring", "funnel", "passthrough"])
            if typ == "structuring":
                n_near = rng.randint(4, 9) if clear else 3
                f["near_threshold_count"] = n_near
                f["txn_count"] = n_near + rng.randint(0, 3)
                f["total_in"] = n_near * rng.uniform(9000, 9900)
            elif typ == "funnel":
                din = rng.randint(7, 14) if clear else rng.randint(5, 6)
                f["distinct_in_cp"] = din
                f["distinct_out_cp"] = rng.randint(1, 2)
                f["total_in"] = rng.uniform(150_000, 600_000)
                f["total_out"] = f["total_in"] * rng.uniform(0.7, 0.95)
                f["txn_count"] = din + rng.randint(2, 6)
            else:  # passthrough
                r = rng.uniform(0.90, 0.99) if clear else rng.uniform(0.80, 0.85)
                f["passthrough_ratio"] = round(r, 2)
                f["same_day"] = 1
                f["total_in"] = rng.uniform(60_000, 300_000)
                f["total_out"] = f["total_in"] * r
                f["txn_count"] = rng.randint(4, 12)
            cat = ""
            label = 1
        else:
            # ---------------- FALSE POSITIVE ----------------
            roll = rng.random()
            if roll < 0.40:                                  # within_profile
                c = rng.choice(customers)
                ratio = rng.uniform(0.6, 1.3)
                tot = c["expected_amount"] * ratio
                f["total_in"] = tot * rng.uniform(0.5, 0.8)
                f["total_out"] = tot - f["total_in"]
                f["txn_count"] = max(1, int(c["expected_count"] * rng.uniform(0.6, 1.3)))
                cat = "within_profile"
            elif roll < 0.65:                                # below_typology
                c = rng.choice(customers)
                # control TOTAL throughput (in+out) to a moderate multiple so the
                # alert clears via below_typology rather than spilling into the
                # ambiguous band.
                throughput = c["expected_amount"] * rng.uniform(1.7, 2.6)
                f["txn_count"] = max(2, int(c["expected_count"] * rng.uniform(1.2, 1.8)))
                indicator = rng.choice(["struct", "funnel", "pass"])
                if indicator == "struct":
                    f["total_in"] = throughput
                    f["near_threshold_count"] = rng.randint(1, 2)
                elif indicator == "funnel":
                    f["total_in"] = throughput * 0.6
                    f["total_out"] = throughput * 0.4
                    f["distinct_in_cp"] = rng.randint(3, 4)
                    f["distinct_out_cp"] = rng.randint(1, 2)
                else:
                    f["total_in"] = throughput * 0.55
                    f["total_out"] = throughput * 0.45
                    f["passthrough_ratio"] = round(rng.uniform(0.60, 0.79), 2)
                    f["same_day"] = 1
                cat = "below_typology"
            elif roll < 0.85:                                # documented_context
                c = rng.choice(with_biz) if with_biz else rng.choice(customers)
                tot = c["expected_amount"] * rng.uniform(1.0, 2.5)
                f["total_in"] = tot * 0.6
                f["total_out"] = tot * 0.4
                f["txn_count"] = max(1, int(c["expected_count"] * rng.uniform(0.9, 2.2)))
                bt = c["business_type"]
                if bt in ("import_export", "remittance"):
                    f["high_risk_geo_fraction"] = round(rng.uniform(0.55, 0.9), 2)
                else:  # cash_intensive / payroll -> velocity
                    f["txn_count"] = max(f["txn_count"], int(c["expected_count"] * rng.uniform(3.2, 5.0)))
                cat = "documented_context"
            else:                                            # ambiguous_residual
                c = rng.choice(customers)
                tot = c["expected_amount"] * rng.uniform(3.5, 6.0)  # beyond context tolerance
                f["total_in"] = tot * rng.uniform(0.5, 0.9)
                f["total_out"] = tot - f["total_in"]
                f["txn_count"] = max(2, int(c["expected_count"] * rng.uniform(2.0, 4.0)))
                cat = "ambiguous_residual"
            label = 0

        alerts.append({
            "alert_id": aid, "customer_id": c["customer_id"], "window_days": 30,
            "total_in": round(f["total_in"], 2), "total_out": round(f["total_out"], 2),
            "txn_count": f["txn_count"], "near_threshold_count": f["near_threshold_count"],
            "distinct_in_cp": f["distinct_in_cp"], "distinct_out_cp": f["distinct_out_cp"],
            "passthrough_ratio": f["passthrough_ratio"], "same_day": f["same_day"],
            "high_risk_geo_fraction": f["high_risk_geo_fraction"],
            "label": label, "category": cat,
        })
    return alerts


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=5000)
    ap.add_argument("--alerts", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    cust = make_customers(args.customers, rng)
    al = make_alerts(args.alerts, cust, rng)
    write_csv(os.path.join(args.out, "customers.csv"), cust)
    write_csv(os.path.join(args.out, "alerts.csv"), al)
    sus = sum(a["label"] for a in al)
    print(f"customers: {len(cust)} -> {args.out}/customers.csv")
    print(f"alerts:    {len(al)} ({sus} suspicious, {len(al)-sus} false positives) "
          f"-> {args.out}/alerts.csv   [seed={args.seed}]")


if __name__ == "__main__":
    main()
