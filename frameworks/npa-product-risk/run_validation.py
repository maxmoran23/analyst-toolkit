"""
Validation harness for the NPA product-risk framework.

A pre-launch product-risk model is validated like a rating model, not a triage
classifier: the questions are discrimination (do scores separate by designed
risk?), floor safety (is a floor-triggered product ever tiered LOW?), prohibited
routing (is a prohibited attribute ever scored around?), monotonicity (does
worsening any factor never lower the score?), and distribution sanity. This
harness computes all five over the seeded synthetic population and writes the
evidence pack.

It enforces the assessment analogue of false-negative safety as a BUILD GATE: if
any product carrying a floor-triggering attribute is tiered LOW, or any product
carrying a prohibited attribute is routed anywhere but REFER_PROHIBITED, or
discrimination ordering fails, or monotonicity fails, it exits non-zero.

Usage:
    python3 run_validation.py
    python3 run_validation.py --products 200000
    python3 run_validation.py --trials 6 --no-write
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import statistics
import subprocess
import time
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from _lib import attest, metrics  # noqa: E402
from _lib.scoring import check_monotonic  # noqa: E402
import scorer as S  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

_T0 = time.time()   # wall-clock provenance for the evidence manifest

STRATA = ["designed_low", "designed_medium", "designed_high", "hard_high", "prohibited"]
SOFT_STRATA = ["designed_low", "designed_medium", "designed_high"]
TIERS = ["LOW", "MEDIUM", "HIGH"]
ROUTES = ["STANDARD_APPROVAL", "ENHANCED_REVIEW", "FULL_COMMITTEE", "REFER_PROHIBITED"]


def generate(n, seed):
    import random
    rng = random.Random(seed)
    return G.make_products(n, rng)


def _to_product(r):
    return S.Product(
        product_id=r["product_id"], client_segment=r["client_segment"],
        target_jurisdictions=[j for j in r["target_jurisdictions"].split("|") if j],
        delivery_channel=r["delivery_channel"],
        asset_settlement_type=r["asset_settlement_type"],
        novelty_to_firm=r["novelty_to_firm"],
        third_party_dependency=r["third_party_dependency"],
        data_privacy_surface=float(r["data_privacy_surface"]),
        cash_intensity=float(r["cash_intensity"]),
        anonymity_features=bool(int(r["anonymity_features"])),
        cross_border_reach=float(r["cross_border_reach"]),
        model_ai_reliance=r["model_ai_reliance"],
        involves_custody=bool(int(r["involves_custody"])),
        sanctions_exposed_asset=bool(int(r["sanctions_exposed_asset"])),
        new_client_segment=bool(int(r["new_client_segment"])),
        new_geography=bool(int(r["new_geography"])),
        anonymity_enhanced_instrument=bool(int(r["anonymity_enhanced_instrument"])),
        bearer_negotiable_feature=bool(int(r["bearer_negotiable_feature"])))


def score_population(rows, config):
    out = []
    for r in rows:
        a = S.assess(_to_product(r), config)
        out.append({"stratum": r["stratum"], "score": a.score, "tier": a.tier,
                    "routing": a.routing, "floored": bool(a.floors_applied),
                    "prohibited": bool(a.prohibited_attributes)})
    return out


def analyze(records):
    n = len(records)
    tier_dist = {t: sum(1 for r in records if r["tier"] == t) for t in TIERS}
    route_dist = {rt: sum(1 for r in records if r["routing"] == rt) for rt in ROUTES}
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
    # Discrimination ordering applies to the SOFT strata only. hard_high is
    # defined by a buried hard attribute that floors the TIER, not by high soft
    # factors, so its mean SCORE deliberately sits low — it is validated by the
    # floor gate (never LOW), not by score ordering. prohibited is validated by
    # the routing gate.
    means = [per_stratum[s]["mean_score"] for s in SOFT_STRATA if s in per_stratum]
    discrimination_ok = all(means[i] < means[i + 1] for i in range(len(means) - 1))
    hard_low = per_stratum.get("hard_high", {}).get("tier_LOW", 0)
    # Structural double-check across the WHOLE population, not just the stratum:
    # any product with a floor applied must never end LOW.
    floored_low = sum(1 for r in records if r["floored"] and r["tier"] == "LOW")
    prohibited_total = sum(1 for r in records if r["stratum"] == "prohibited")
    prohibited_missed = sum(1 for r in records
                            if r["stratum"] == "prohibited" and r["routing"] != "REFER_PROHIBITED")
    # And structurally: every engine-detected prohibited attribute must route there.
    detected_misrouted = sum(1 for r in records
                             if r["prohibited"] and r["routing"] != "REFER_PROHIBITED")
    return {
        "n": n, "tier_distribution": tier_dist,
        "tier_shares": {t: round(tier_dist[t] / n, 4) for t in TIERS},
        "routing_distribution": route_dist,
        "routing_shares": {rt: round(route_dist[rt] / n, 4) for rt in ROUTES},
        "per_stratum": per_stratum, "discrimination_ok": discrimination_ok,
        "hard_high_tiered_low": hard_low, "floored_tiered_low": floored_low,
        "prohibited_total": prohibited_total, "prohibited_missed": prohibited_missed,
        "detected_prohibited_misrouted": detected_misrouted,
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


def gate_failures(a, mono_ok):
    fails = []
    if a["hard_high_tiered_low"] > 0:
        fails.append(f"{a['hard_high_tiered_low']} floor-triggered (hard_high) products tiered LOW")
    if a["floored_tiered_low"] > 0:
        fails.append(f"{a['floored_tiered_low']} products with a floor applied still tiered LOW")
    if a["prohibited_missed"] > 0 or a["detected_prohibited_misrouted"] > 0:
        fails.append(f"{a['prohibited_missed']} prohibited-stratum products routed past "
                     f"REFER_PROHIBITED ({a['detected_prohibited_misrouted']} detected-but-misrouted)")
    if not a["discrimination_ok"]:
        fails.append("discrimination ordering failed")
    if not mono_ok:
        fails.append("monotonicity failed")
    return fails


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
    A("# Validation Report — NPA Product-Risk Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the reference "
      "engine over a seeded, fully synthetic population of product proposals at the "
      "fictional Harborview Financial Group. No real product or institution is "
      "represented. Numbers are emitted by `run_validation.py`, not authored.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['products']:,} product proposals · "
      f"git `{manifest['git_sha']}` · {manifest['generated_utc']}")
    A("")
    A(f"**Headline:** discrimination {'PASS' if a['discrimination_ok'] else 'FAIL'} "
      f"(mean score rises across designed strata), floor safety **{a['hard_high_tiered_low']} "
      f"floor-triggered products tiered LOW**, prohibited routing **{a['prohibited_missed']} of "
      f"{a['prohibited_total']:,} prohibited proposals routed past REFER_PROHIBITED**, "
      f"monotonicity {'PASS' if mono_ok else 'FAIL'}.")
    A("")
    A("## 1. Methodology summary")
    A("The engine scores each product / activity proposal 0-100 from a documented "
      "weighted composite of nine risk factors, tiers it LOW / MEDIUM / HIGH, and "
      "routes it to a named approval route with named mandatory pre-launch "
      "conditions and a post-launch review interval. Mandatory floors are raise-only "
      "(a sanctions-exposed jurisdiction or asset, or digital-asset custody the firm "
      "has never operated, force at least HIGH; a new client segment combined with a "
      "new geography forces at least MEDIUM), and a documented prohibited list is "
      "never scored around (REFER_PROHIBITED). The engine routes; the approval "
      "decision is the committee's. Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['products']:,} proposals across five designed-risk strata. The "
      "stratum is assigned from attribute presence and is independent of the engine's "
      "weighted formula, so agreement is a real test, not a tautology. The hard_high "
      "stratum is the adversarial safety population: an otherwise-benign profile "
      "carrying ONE buried floor-triggering attribute, so the composite alone would "
      "tier most of them LOW — the floor has to catch every one. The prohibited "
      "stratum carries a documented prohibited attribute and must always route "
      "REFER_PROHIBITED.")
    A("")
    A("## 3. Tier and routing distribution")
    A("| Tier | Count | Share |")
    A("| --- | --- | --- |")
    for t in TIERS:
        A(f"| {t} | {a['tier_distribution'][t]:,} | {a['tier_shares'][t]:.1%} |")
    A("")
    A("| Routing | Count | Share |")
    A("| --- | --- | --- |")
    for rt in ROUTES:
        A(f"| {rt} | {a['routing_distribution'][rt]:,} | {a['routing_shares'][rt]:.1%} |")
    A("")
    A("## 4. Discrimination by designed stratum")
    A("Mean score must rise across designed_low → designed_medium → designed_high. "
      "hard_high is deliberately benign apart from its buried hard attribute, so its "
      "mean score sits low — it is judged by the floor gate (never LOW), not by "
      "score ordering; prohibited is judged by the routing gate.")
    A("")
    A(strat_tbl)
    A(f"\nDiscrimination ordering: **{'PASS' if a['discrimination_ok'] else 'FAIL'}**.")
    A("")
    A("## 5. Floor-rule safety (the under-rating gate)")
    A(f"Floor-triggered (hard_high) proposals tiered LOW: **{a['hard_high_tiered_low']}** "
      "(must be 0). Structural double-check over the whole population — proposals "
      f"with any floor applied that still ended LOW: **{a['floored_tiered_low']}** "
      "(must be 0). This is the assessment analogue of false-negative safety: every "
      "hard attribute maps to a raise-only floor (sanctions exposure and digital-asset "
      "custody novelty to HIGH, the new-segment + new-geography combination to at "
      "least MEDIUM), so a proposal carrying one cannot be tiered LOW regardless of "
      "how benign the rest of the profile is.")
    A("")
    A("## 6. Prohibited-attribute gate (never scored around)")
    A(f"Prohibited-stratum proposals: {a['prohibited_total']:,}; routed anywhere other "
      f"than REFER_PROHIBITED: **{a['prohibited_missed']}** (must be 0). "
      f"Engine-detected prohibited attributes misrouted: "
      f"**{a['detected_prohibited_misrouted']}** (must be 0). A prohibited attribute "
      "dominates the routing regardless of the composite score — there is no score "
      "at which the engine will pass one through a scoring route.")
    A("")
    A("## 7. Monotonicity property test")
    A(f"Raising any single factor sub-score never lowers the composite — tested over "
      f"300 random base vectors across all {len(S.WEIGHTS)} factors: "
      f"**{'PASS' if mono_ok else 'FAIL'}**. Monotonicity is a structural property of "
      "the non-negative weighted sum and the raise-only floors.")
    A("")
    A("## 8. Limitations")
    A("- A pre-launch product-risk tier is a judgement; there is no objective true "
      "tier, so this validates discrimination, floor safety, prohibited routing, and "
      "monotonicity rather than tier accuracy against a fabricated truth.")
    A("- The factor weights, jurisdiction buckets, reference tables, and band "
      "thresholds are ILLUSTRATIVE. Calibrate them against your own product-approval "
      "methodology and history (`tuning.md`); the jurisdiction buckets in particular "
      "must track current sanctions programs and FATF lists.")
    A("- The engine tiers and routes; the approval decision, any conditions waiver, "
      "and any override are human, documented committee actions. It never approves, "
      "blocks, or files anything.")
    A("- The prohibited list here is a three-item illustration; a real deployment "
      "carries its institution's full prohibited-product register.")
    A("")
    A("## 9. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} --products {manifest['products']}")
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
    with open(os.path.join(out_dir, "routing-distribution.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["routing", "count", "share"])
        for rt in ROUTES:
            w.writerow([rt, a["routing_distribution"][rt], a["routing_shares"][rt]])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--products", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = S.Config()
    rows = generate(args.products, args.seed)
    a = analyze(score_population(rows, config))
    mono_ok, mono_fail = monotonicity_check()

    print(f"\n=== NPA product risk (seed {args.seed}, {args.products:,} proposals) ===")
    print(f"tier shares: {a['tier_shares']}")
    print(f"routing shares: {a['routing_shares']}")
    means = {s: a["per_stratum"][s]["mean_score"] for s in STRATA if s in a["per_stratum"]}
    print(f"mean score by stratum: {means}")
    print(f"discrimination_ok={a['discrimination_ok']}  hard_high_tiered_low={a['hard_high_tiered_low']}  "
          f"floored_tiered_low={a['floored_tiered_low']}  prohibited_missed={a['prohibited_missed']}  "
          f"monotonic={mono_ok}")

    all_fails = gate_failures(a, mono_ok)
    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            at = analyze(score_population(generate(args.products, s), config))
            print(f"  trial seed {s}: shares {at['tier_shares']} disc={at['discrimination_ok']} "
                  f"hard_low={at['hard_high_tiered_low']} prohibited_missed={at['prohibited_missed']}")
            all_fails += [f"trial seed {s}: {f}" for f in gate_failures(at, True)]

    # ---- safety / quality build gate ----
    if all_fails:
        print("\nGATE FAILED:")
        for f in all_fails:
            print(f"   {f}")
        if not mono_ok:
            print("   monotonicity detail:", mono_fail)
        return 1

    manifest = {"framework": "npa-product-risk", "seed": args.seed,
                "products": args.products, "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "floor": {"floor_triggered_tiered_low_max": 0, "prohibited_missed_max": 0}}

    manifest = attest.enrich_manifest(manifest, _T0)
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, a, mono_ok, manifest, render_report(a, mono_ok, manifest))
        print(f"\nevidence written -> {args.out}/  (all gates PASSED)")
    else:
        print("\nall gates PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
