"""
Synthetic data generator for QA / independent-testing attribute-sampling validation.

Produces two CSVs with KNOWN ground truth:
  controls.csv  — controls under test, each with stated plan parameters
                  (confidence, tolerable rate, expected rate) and a designed
                  scenario with a known true deviation rate
  items.csv     — per-control population of test items (control_id, item_id,
                  stratum, is_deviation), where is_deviation=1 is a genuine
                  control deviation

Everything is invented and seeded (the institution is the fictional Harborview
Financial Group). Each control's population carries labelled deviations at a
designed true rate, so the correct statistical behaviour of plan-select-evaluate
is known by construction:

  clean     true rate well below tolerable (0.08-0.22x) -> the sample should
            support reliance almost always
  boundary  true rate near tolerable (0.75-1.10x)       -> conclusions split;
            reported, not gated
  failing   true rate materially above tolerable (2-3x) -> the DIRECTION gate:
            the measured rate of CONTROL_EFFECTIVE conclusions must not exceed
            the design risk
  planted   one whole stratum is 100% deviant           -> the STRUCTURAL gate:
            stratified selection must allocate more than the acceptance number
            of items to that stratum, so every drawn sample observes more
            deviations than the plan accepts; zero EFFECTIVE conclusions

The scenario cycle is deterministic (clean, failing, boundary, planted, ...) so
every run of >= 4 controls contains every scenario at every seed.
"""
from __future__ import annotations

import argparse
import csv
import os
import random

SCENARIO_CYCLE = ["clean", "failing", "boundary", "planted"]
CONFIDENCE = 0.95                     # design confidence for every control (alpha = 5%)
TOLERABLE_CHOICES = [0.04, 0.05, 0.06, 0.08, 0.10]
STRATA = ["retail-branch", "commercial", "private-client", "operations", "digital-channel"]
CONTROL_NAMES = [
    "wire-callback verification completed",
    "new-account documentation complete at onboarding",
    "sanctions screening evidence retained",
    "alert disposition rationale documented",
    "periodic review completed on schedule",
    "watchlist match escalated within SLA",
    "monitoring case notes meet documentation standard",
    "high-risk relationship approval obtained",
    "negative-news review documented",
    "annual training completion recorded",
    "user access recertification performed",
    "exception approved before processing",
    "currency-transaction report filed timely",
    "customer risk rating refreshed after trigger event",
]


def make_control(control_id: str, population: int, scenario: str, rng: random.Random):
    """One control under test: stated plan parameters + a labelled item
    population at a designed true deviation rate. Returns (control_dict, items)
    where items is a list of (stratum, is_deviation) tuples."""
    tolerable = rng.choice(TOLERABLE_CHOICES)
    expected = round(tolerable * rng.uniform(0.20, 0.40), 4)
    k_strata = rng.randint(3, 5)
    labels = sorted(rng.sample(STRATA, k_strata))
    planted_stratum = None
    if scenario == "planted":
        planted_stratum = rng.choice(labels)
        share = rng.uniform(0.25, 0.35)
        others = [rng.uniform(0.5, 1.5) for _ in range(k_strata - 1)]
        tot = sum(others)
        weights = []
        for s in labels:
            if s == planted_stratum:
                weights.append(share)
            else:
                weights.append((1 - share) * others.pop() / tot)
    else:
        w = [rng.uniform(0.5, 1.5) for _ in labels]
        tot = sum(w)
        weights = [x / tot for x in w]

    if scenario == "clean":
        base_rate = tolerable * rng.uniform(0.08, 0.22)
    elif scenario == "boundary":
        base_rate = tolerable * rng.uniform(0.75, 1.10)
    elif scenario == "failing":
        base_rate = tolerable * rng.uniform(2.0, 3.0)
    else:  # planted: benign-looking base outside the fully-deviant stratum
        base_rate = tolerable * rng.uniform(0.30, 0.70)

    strata_seq = rng.choices(labels, weights=weights, k=population)
    items = []
    deviations = 0
    for s in strata_seq:
        if s == planted_stratum:
            dev = 1
        else:
            dev = 1 if rng.random() < base_rate else 0
        deviations += dev
        items.append((s, dev))
    control = {"control_id": control_id, "name": rng.choice(CONTROL_NAMES),
               "scenario": scenario, "population": population,
               "confidence": CONFIDENCE, "tolerable_rate": tolerable,
               "expected_rate": expected, "true_rate": round(deviations / population, 5),
               "planted_stratum": planted_stratum or ""}
    return control, items


def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--controls", type=int, default=12)
    ap.add_argument("--population", type=int, default=40000, help="test items per control")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    ctl_rows, item_rows = [], []
    for i in range(args.controls):
        scenario = SCENARIO_CYCLE[i % len(SCENARIO_CYCLE)]
        ctl, items = make_control("CTRL-%03d" % i, args.population, scenario, rng)
        ctl_rows.append([ctl["control_id"], ctl["name"], ctl["scenario"], ctl["population"],
                         ctl["confidence"], ctl["tolerable_rate"], ctl["expected_rate"],
                         ctl["true_rate"], ctl["planted_stratum"]])
        for j, (s, dev) in enumerate(items):
            item_rows.append([ctl["control_id"], "%s-I%06d" % (ctl["control_id"], j), s, dev])
    write_csv(os.path.join(args.out, "controls.csv"),
              ["control_id", "name", "scenario", "population", "confidence",
               "tolerable_rate", "expected_rate", "true_rate", "planted_stratum"], ctl_rows)
    write_csv(os.path.join(args.out, "items.csv"),
              ["control_id", "item_id", "stratum", "is_deviation"], item_rows)
    from collections import Counter
    dist = Counter(r[2] for r in ctl_rows)
    print(f"controls: {len(ctl_rows)} ({dict(dist)})  items: {len(item_rows):,} "
          f"-> {args.out}/   [seed={args.seed}]")


if __name__ == "__main__":
    main()
