"""
Validation harness for the customer risk-rating framework.

A rating model is validated differently from a triage classifier: the questions are
discrimination (do scores separate by designed risk?), floor safety (is a
known-high-risk customer ever rated LOW?), monotonicity (does raising any factor
never lower the score?), and distribution sanity. This harness computes all four
over the seeded synthetic population and writes the evidence pack.

It enforces the rating analogue of false-negative safety as a BUILD GATE: if any
customer carrying a hard risk attribute is rated LOW, or discrimination ordering
fails, or monotonicity fails, it exits non-zero.

Usage:
    python3 run_validation.py
    python3 run_validation.py --customers 200000
    python3 run_validation.py --trials 5
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from _lib import metrics  # noqa: E402
from _lib.scoring import check_monotonic  # noqa: E402
import scorer as S  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

STRATA = ["designed_low", "designed_medium", "designed_high", "hard_high"]
TIERS = ["LOW", "MEDIUM", "HIGH"]


def generate(n, seed):
    import random
    rng = random.Random(seed)
    return G.make_customers(n, rng)


def _to_customer(r):
    return S.Customer(
        customer_id=r["customer_id"], customer_type=r["customer_type"],
        domicile_country=r["domicile_country"],
        operating_countries=[c for c in r["operating_countries"].split("|") if c],
        products=[p for p in r["products"].split("|") if p], channel=r["channel"],
        pep=bool(int(r["pep"])), adverse_media=bool(int(r["adverse_media"])),
        prior_sar=bool(int(r["prior_sar"])),
        ownership_opacity=float(r["ownership_opacity"]),
        expected_activity_intensity=float(r["expected_activity_intensity"]))


def score_population(rows, config):
    out = []
    for r in rows:
        rt = S.rate(_to_customer(r), config)
        out.append({"stratum": r["stratum"], "score": rt.score, "tier": rt.tier,
                    "floored": bool(rt.floors_applied)})
    return out


def analyze(records):
    n = len(records)
    tier_dist = {t: sum(1 for r in records if r["tier"] == t) for t in TIERS}
    per_stratum = {}
    for s in STRATA:
        rs = [r for r in records if r["stratum"] == s]
        if not rs:
            continue
        per_stratum[s] = {
            "count": len(rs),
            "mean_score": round(statistics.mean(r["score"] for r in rs), 2),
            "tier_LOW": sum(1 for r in rs if r["tier"] == "LOW"),
            "tier_MEDIUM": sum(1 for r in rs if r["tier"] == "MEDIUM"),
            "tier_HIGH": sum(1 for r in rs if r["tier"] == "HIGH"),
        }
    # Discrimination ordering applies to the SOFT strata only. hard_high is defined
    # by a hard attribute that floors the TIER, not by high soft factors, so its
    # mean SCORE can sit below designed_high — it is validated by the floor gate
    # (never LOW), not by score ordering.
    soft = ["designed_low", "designed_medium", "designed_high"]
    means = [per_stratum[s]["mean_score"] for s in soft if s in per_stratum]
    discrimination_ok = all(means[i] < means[i + 1] for i in range(len(means) - 1))
    hard_low = per_stratum.get("hard_high", {}).get("tier_LOW", 0)
    designed_high_low = per_stratum.get("designed_high", {}).get("tier_LOW", 0)
    return {
        "n": n, "tier_distribution": tier_dist,
        "tier_shares": {t: round(tier_dist[t] / n, 4) for t in TIERS},
        "per_stratum": per_stratum, "discrimination_ok": discrimination_ok,
        "hard_high_rated_low": hard_low, "designed_high_rated_low": designed_high_low,
    }


def monotonicity_check(samples=300, seed=0):
    """Property test on the pure feature->score function: raising any one factor
    sub-score never lowers the composite. Tested on random base vectors."""
    import random
    rng = random.Random(seed)
    failures = []
    for _ in range(samples):
        base = {k: rng.uniform(0, 100) for k in S.WEIGHTS}
        for f in S.WEIGHTS:
            ok, detail = check_monotonic(S.score_features, base, f, [0, 20, 40, 60, 80, 100])
            if not ok:
                failures.append(detail)
    return (not failures), failures[:5]


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def render_report(a, mono_ok, manifest):
    ps = a["per_stratum"]
    strat_rows = [{"stratum": s, "count": ps[s]["count"], "mean_score": ps[s]["mean_score"],
                   "LOW": ps[s]["tier_LOW"], "MEDIUM": ps[s]["tier_MEDIUM"],
                   "HIGH": ps[s]["tier_HIGH"]} for s in STRATA if s in ps]
    strat_tbl = metrics.markdown_table(strat_rows, ["stratum", "count", "mean_score", "LOW", "MEDIUM", "HIGH"])

    L = []; A = L.append
    A("# Validation Report — Customer Risk-Rating Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the reference "
      "engine over a seeded, fully synthetic customer population. No real customer "
      "is represented. Numbers are emitted by `run_validation.py`, not authored.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['customers']:,} customers · "
      f"git `{manifest['git_sha']}` · {manifest['generated_utc']}")
    A("")
    A(f"**Headline:** discrimination {'PASS' if a['discrimination_ok'] else 'FAIL'} "
      f"(mean score rises across designed strata), floor safety **{a['hard_high_rated_low']} "
      f"hard-risk customers rated LOW**, monotonicity {'PASS' if mono_ok else 'FAIL'}.")
    A("")
    A("## 1. Methodology summary")
    A("The engine rates each customer LOW / MEDIUM / HIGH from a documented weighted "
      "composite of eight risk factors, with mandatory floors (a PEP can never be "
      "LOW; a sanctions/high-risk-jurisdiction nexus, a prior SAR, confirmed adverse "
      "media, or an opaque shell force at least HIGH). It rates; it does not make the "
      "onboarding decision. Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['customers']:,} customers across four designed-risk strata. The "
      "stratum is assigned from attribute presence and is independent of the engine's "
      "weighted formula, so agreement is a real test, not a tautology. The hard_high "
      "stratum carries a hard risk attribute and is the safety population.")
    A("")
    A("## 3. Rating distribution")
    A("| Tier | Count | Share |")
    A("| --- | --- | --- |")
    for t in TIERS:
        A(f"| {t} | {a['tier_distribution'][t]:,} | {a['tier_shares'][t]:.1%} |")
    A("")
    A("## 4. Discrimination by designed stratum")
    A("Mean score must rise across designed_low → designed_medium → designed_high, "
      "and the hard_high stratum must concentrate in MEDIUM/HIGH (never LOW).")
    A("")
    A(strat_tbl)
    A(f"\nDiscrimination ordering: **{'PASS' if a['discrimination_ok'] else 'FAIL'}**.")
    A("")
    A("## 5. Floor-rule safety (the under-rating gate)")
    A(f"Customers carrying a hard risk attribute rated LOW: **{a['hard_high_rated_low']}** "
      "(must be 0). This is the rating analogue of false-negative safety, enforced "
      "structurally by the floor rules and as a build gate — a PEP floors to MEDIUM, "
      "every other hard attribute floors to HIGH, so no hard-risk customer can be "
      "rated LOW regardless of its other factors.")
    A(f"\ndesigned_high (soft factors only) rated LOW: {a['designed_high_rated_low']} "
      "(expected ~0 from the composite alone).")
    A("")
    A("## 6. Monotonicity property test")
    A(f"Raising any single factor sub-score never lowers the composite — tested over "
      f"300 random base vectors across all {len(S.WEIGHTS)} factors: "
      f"**{'PASS' if mono_ok else 'FAIL'}**. Monotonicity is a structural property of "
      "the non-negative weighted sum and the raise-only floors.")
    A("")
    A("## 7. Limitations")
    A("- A risk rating is a judgement; there is no objective true tier, so this "
      "validates discrimination, safety, and monotonicity rather than tier accuracy "
      "against a fabricated truth.")
    A("- The factor weights, country buckets, and band thresholds are ILLUSTRATIVE. "
      "Calibrate them against your own methodology and customer base (`tuning.md`); "
      "the country buckets in particular must track current FATF lists.")
    A("- The engine rates; the onboarding / exit decision and any override are human, "
      "documented actions.")
    A("")
    A("## 8. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} --customers {manifest['customers']}")
    A("```")
    A("")
    return "\n".join(L)


def write_evidence(out_dir, a, mono_ok, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    json.dump({"analysis": a, "monotonicity_ok": mono_ok, "manifest": manifest},
              open(os.path.join(out_dir, "metrics.json"), "w"), indent=2)
    with open(os.path.join(out_dir, "stratum-scores.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stratum", "count", "mean_score", "tier_LOW", "tier_MEDIUM", "tier_HIGH"])
        for s in STRATA:
            if s in a["per_stratum"]:
                p = a["per_stratum"][s]
                w.writerow([s, p["count"], p["mean_score"], p["tier_LOW"], p["tier_MEDIUM"], p["tier_HIGH"]])
    with open(os.path.join(out_dir, "tier-distribution.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["tier", "count", "share"])
        for t in TIERS:
            w.writerow([t, a["tier_distribution"][t], a["tier_shares"][t]])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = S.Config()
    rows = generate(args.customers, args.seed)
    a = analyze(score_population(rows, config))
    mono_ok, mono_fail = monotonicity_check()

    print(f"\n=== customer risk rating (seed {args.seed}, {args.customers:,} customers) ===")
    print(f"tier shares: {a['tier_shares']}")
    means = {s: a["per_stratum"][s]["mean_score"] for s in STRATA if s in a["per_stratum"]}
    print(f"mean score by stratum: {means}")
    print(f"discrimination_ok={a['discrimination_ok']}  hard_high_rated_low={a['hard_high_rated_low']}  "
          f"monotonic={mono_ok}")

    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            at = analyze(score_population(generate(args.customers, s), config))
            print(f"  trial seed {s}: shares {at['tier_shares']} disc={at['discrimination_ok']} "
                  f"hard_low={at['hard_high_rated_low']}")

    # ---- safety / quality build gate ----
    if a["hard_high_rated_low"] > 0 or not a["discrimination_ok"] or not mono_ok:
        print("\nGATE FAILED:")
        if a["hard_high_rated_low"] > 0:
            print(f"   {a['hard_high_rated_low']} hard-risk customers rated LOW")
        if not a["discrimination_ok"]:
            print("   discrimination ordering failed")
        if not mono_ok:
            print("   monotonicity failed:", mono_fail)
        return 1

    manifest = {"framework": "customer-risk-rating", "seed": args.seed,
                "customers": args.customers, "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, a, mono_ok, manifest, render_report(a, mono_ok, manifest))
        print(f"\nevidence written -> {args.out}/  (all gates PASSED)")
    else:
        print("\nall gates PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
