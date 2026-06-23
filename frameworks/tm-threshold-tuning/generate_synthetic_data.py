"""
Synthetic data generator for transaction-monitoring threshold-tuning validation.

Produces two CSVs with KNOWN ground truth:
  rules.csv         — monitoring rules, each with a current threshold and a designed
                      scenario
  observations.csv  — per-rule population of (metric_value, label), where label=1 is
                      genuinely suspicious activity

Everything is invented and seeded. Each rule's suspicious population sits higher on
its metric than its benign population, with overlap, so a threshold trades alert
volume against missed suspicious activity. The "optimal" threshold T_opt is the
highest threshold that still detects the required share (recall floor) of suspicious
activity; each rule's current threshold is set relative to T_opt by its scenario:

  too_low    current well below T_opt  -> over-alerts -> engine should RAISE
  too_high   current above T_opt       -> leaks suspicious below the line (BTL)
                                          -> engine should LOWER
  optimal    current at T_opt          -> engine should KEEP
"""
from __future__ import annotations

import argparse
import csv
import os
import random

SCENARIOS = ["too_low", "too_high", "optimal"]
SCEN_W = [0.40, 0.35, 0.25]
RECALL_FLOOR = 0.95
METRIC_NAMES = [
    "monthly cash deposits ($k)", "wire velocity (count)", "rapid in-out ratio (%)",
    "cross-border volume ($k)", "structuring proximity (count)", "ATM withdrawals ($k)",
    "new-counterparty rate", "round-number frequency", "dormant-then-active spike",
    "high-risk-geo volume ($k)", "cash-to-wire ratio", "peer-group deviation (z)",
]


def _percentile(sorted_vals, q):
    if not sorted_vals:
        return 0.0
    i = max(0, min(len(sorted_vals) - 1, int(q * len(sorted_vals))))
    return sorted_vals[i]


def make_rule(rule_id, population, rng):
    scenario = rng.choices(SCENARIOS, SCEN_W)[0]
    mu_b = rng.uniform(20, 35)
    mu_s = rng.uniform(58, 80)
    sd = rng.uniform(12, 18)
    rate = rng.uniform(0.03, 0.05)
    obs = []
    suspicious_vals = []
    for _ in range(population):
        is_s = rng.random() < rate
        v = rng.gauss(mu_s, sd) if is_s else rng.gauss(mu_b, sd)
        v = round(max(0.0, v), 2)
        obs.append((v, 1 if is_s else 0))
        if is_s:
            suspicious_vals.append(v)
    suspicious_vals.sort()
    # T_opt = highest threshold detecting >= floor of suspicious = (1-floor) quantile
    t_opt = _percentile(suspicious_vals, 1 - RECALL_FLOOR)
    if scenario == "optimal":
        current = round(t_opt, 2)
    elif scenario == "too_high":
        current = round(t_opt + rng.uniform(12, 25), 2)   # above the line -> leaks
    else:  # too_low
        current = round(max(0.0, t_opt - rng.uniform(18, 30)), 2)  # over-alerts
    rule = {"rule_id": rule_id, "metric_name": rng.choice(METRIC_NAMES),
            "current_threshold": current, "scenario": scenario}
    return rule, obs


def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rules", type=int, default=12)
    ap.add_argument("--population", type=int, default=40000, help="observations per rule")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    rule_rows, obs_rows = [], []
    for i in range(args.rules):
        rule, obs = make_rule("RULE-%03d" % i, args.population, rng)
        rule_rows.append([rule["rule_id"], rule["metric_name"], rule["current_threshold"], rule["scenario"]])
        for v, lab in obs:
            obs_rows.append([rule["rule_id"], v, lab])
    write_csv(os.path.join(args.out, "rules.csv"),
              ["rule_id", "metric_name", "current_threshold", "scenario"], rule_rows)
    write_csv(os.path.join(args.out, "observations.csv"),
              ["rule_id", "metric_value", "label"], obs_rows)
    from collections import Counter
    dist = Counter(r[3] for r in rule_rows)
    print(f"rules: {len(rule_rows)} ({dict(dist)})  observations: {len(obs_rows):,} "
          f"-> {args.out}/   [seed={args.seed}]")


if __name__ == "__main__":
    main()
