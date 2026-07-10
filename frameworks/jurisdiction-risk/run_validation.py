"""
Validation harness for the jurisdiction-risk framework.

A rating model is validated by discrimination (do scores separate by designed risk?),
floor safety (is a hard-designated jurisdiction ever rated below its mandated floor?),
monotonicity (does raising any dimension never lower the score?), and distribution
sanity. This harness computes all four over the seeded synthetic population and writes
the evidence pack.

It enforces the rating analogue of false-negative safety as a BUILD GATE: if any
FATF-black-listed or comprehensively-sanctioned jurisdiction is rated below CRITICAL,
or any FATF-grey / EU-high-risk / INCSR-primary jurisdiction is rated below HIGH, or
discrimination ordering fails, or monotonicity fails, it exits non-zero.

Usage:
    python3 run_validation.py
    python3 run_validation.py --jurisdictions 40000
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
import time
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from _lib import attest, metrics  # noqa: E402
from _lib.scoring import check_monotonic  # noqa: E402
import scorer as S  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

_T0 = time.time()   # wall-clock provenance for the evidence manifest

STRATA = ["designed_low", "designed_medium", "designed_high", "hard_high", "hard_critical"]
TIERS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
_BOOLS = ("comprehensive_sanctions", "fatf_blacklist", "fatf_greylist",
          "eu_high_risk", "incsr_primary_concern")


def generate(n, seed):
    import random
    rng = random.Random(seed)
    return G.make_jurisdictions(n, rng)


def _to_jurisdiction(r):
    return S.Jurisdiction(
        code=r["code"], name=r["name"],
        cpi_score=float(r["cpi_score"]), basel_score=float(r["basel_score"]),
        wgi_rule_of_law_pct=float(r["wgi_rule_of_law_pct"]),
        wgi_control_corruption_pct=float(r["wgi_control_corruption_pct"]),
        secrecy_score=float(r["secrecy_score"]),
        organized_crime_score=float(r["organized_crime_score"]),
        terrorism_score=float(r["terrorism_score"]),
        instability_score=float(r["instability_score"]),
        comprehensive_sanctions=bool(int(r["comprehensive_sanctions"])),
        fatf_blacklist=bool(int(r["fatf_blacklist"])),
        fatf_greylist=bool(int(r["fatf_greylist"])),
        eu_high_risk=bool(int(r["eu_high_risk"])),
        incsr_primary_concern=bool(int(r["incsr_primary_concern"])),
        missing=[m for m in r["missing"].split("|") if m])


def score_population(rows, config):
    out = []
    for r in rows:
        rt = S.rate(_to_jurisdiction(r), config)
        out.append({"stratum": r["stratum"], "score": rt.score, "tier": rt.tier,
                    "crit_flag": bool(int(r["comprehensive_sanctions"]) or int(r["fatf_blacklist"])),
                    "high_flag": bool(int(r["fatf_greylist"]) or int(r["eu_high_risk"])
                                      or int(r["incsr_primary_concern"]))})
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
            **{f"tier_{t}": sum(1 for r in rs if r["tier"] == t) for t in TIERS},
        }
    # Discrimination applies to the SOFT strata only. The hard strata are defined by a
    # categorical designation that floors the TIER, not by high soft dimensions, so
    # their mean SCORE can sit below designed_high — they are validated by the floor
    # gate (never below their floor), not by score ordering.
    soft = ["designed_low", "designed_medium", "designed_high"]
    means = [per_stratum[s]["mean_score"] for s in soft if s in per_stratum]
    discrimination_ok = all(means[i] < means[i + 1] for i in range(len(means) - 1))
    # Floor safety, computed over the actual designated jurisdictions (not the stratum
    # label), so it holds regardless of how the population was built.
    crit_below = sum(1 for r in records if r["crit_flag"]
                     and TIERS.index(r["tier"]) < TIERS.index("CRITICAL"))
    high_below = sum(1 for r in records if r["high_flag"] and not r["crit_flag"]
                     and TIERS.index(r["tier"]) < TIERS.index("HIGH"))
    return {
        "n": n, "tier_distribution": tier_dist,
        "tier_shares": {t: round(tier_dist[t] / n, 4) for t in TIERS},
        "per_stratum": per_stratum, "discrimination_ok": discrimination_ok,
        "critical_floor_breaches": crit_below, "high_floor_breaches": high_below,
    }


def monotonicity_check(samples=300, seed=0):
    """Property test on the pure feature->score function: raising any one dimension
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
    cols = ["stratum", "count", "mean_score"] + TIERS
    strat_rows = [{"stratum": s, "count": ps[s]["count"], "mean_score": ps[s]["mean_score"],
                   **{t: ps[s][f"tier_{t}"] for t in TIERS}} for s in STRATA if s in ps]
    strat_tbl = metrics.markdown_table(strat_rows, cols)

    L = []; A = L.append
    A("# Validation Report — Jurisdiction-Risk Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the reference "
      "engine over a seeded, fully synthetic population of FICTIONAL jurisdictions. No "
      "real country is represented or rated. Numbers are emitted by "
      "`run_validation.py`, not authored.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['jurisdictions']:,} jurisdictions · "
      f"git `{manifest['git_sha']}` · {manifest['generated_utc']}")
    A("")
    A(f"**Headline:** discrimination {'PASS' if a['discrimination_ok'] else 'FAIL'} "
      f"(mean score rises across designed strata), floor safety **{a['critical_floor_breaches']} "
      f"below CRITICAL and {a['high_floor_breaches']} below HIGH** among hard-designated "
      f"jurisdictions, monotonicity {'PASS' if mono_ok else 'FAIL'}.")
    A("")
    A("## 1. Methodology summary")
    A("The engine rates each jurisdiction LOW / MEDIUM / HIGH / CRITICAL from a "
      "documented weighted composite of seven public-index dimensions (AML/CFT, "
      "corruption, governance, secrecy, organized crime, terrorism, instability), with "
      "mandatory floors driven by categorical designations: a comprehensive sanctions "
      "program or a FATF black list forces CRITICAL; a FATF grey list, an EU "
      "high-risk-third-country listing, or an INCSR primary-concern listing forces at "
      "least HIGH. It rates inherent geographic risk; it does not make the market or "
      "onboarding decision. Full spec: `METHODOLOGY.md`; sources: `SOURCE-LIBRARY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['jurisdictions']:,} fictional jurisdictions across five designed "
      "strata. The stratum is assigned from the construction, independent of the "
      "engine's weighted formula, so agreement is a real test, not a tautology. The "
      "two hard strata carry a categorical designation with moderate soft dimensions, "
      "so the floor — not the composite — is what must lift the tier; they are the "
      "safety population.")
    A("")
    A("## 3. Rating distribution")
    A("| Tier | Count | Share |")
    A("| --- | --- | --- |")
    for t in TIERS:
        A(f"| {t} | {a['tier_distribution'][t]:,} | {a['tier_shares'][t]:.1%} |")
    A("")
    A("## 4. Discrimination by designed stratum")
    A("Mean score must rise across designed_low → designed_medium → designed_high. The "
      "hard strata are validated by the floor gate below, not by score ordering.")
    A("")
    A(strat_tbl)
    A(f"\nDiscrimination ordering (soft strata): **{'PASS' if a['discrimination_ok'] else 'FAIL'}**.")
    A("")
    A("## 5. Floor-rule safety (the under-rating gate)")
    A(f"Hard-designated jurisdictions rated below their mandated floor — the analogue "
      f"of false-negative safety, enforced structurally and as a build gate:")
    A("")
    A(f"- Comprehensively-sanctioned or FATF-black-listed rated below CRITICAL: "
      f"**{a['critical_floor_breaches']}** (must be 0).")
    A(f"- FATF-grey / EU-high-risk / INCSR-primary rated below HIGH: "
      f"**{a['high_floor_breaches']}** (must be 0).")
    A("")
    A("A flattering index can never talk a designated jurisdiction below its floor: the "
      "floor is applied as the worse of the weighted tier and the mandated minimum.")
    A("")
    A("## 6. Monotonicity property test")
    A(f"Raising any single dimension sub-score never lowers the composite — tested over "
      f"300 random base vectors across all {len(S.WEIGHTS)} dimensions: "
      f"**{'PASS' if mono_ok else 'FAIL'}**. Monotonicity is a structural property of "
      "the non-negative weighted sum and the raise-only floors.")
    A("")
    A("## 7. Limitations")
    A("- A risk rating is a judgement; there is no objective true tier, so this "
      "validates discrimination, floor safety, and monotonicity rather than tier "
      "accuracy against a fabricated truth.")
    A("- The dimension weights and band thresholds are ILLUSTRATIVE. Calibrate them "
      "against your own geographic-risk methodology (`tuning.md`).")
    A("- The categorical designations (FATF, EU, INCSR, sanctions) move over time. A "
      "deployment must refresh them against the authoritative source at time of use "
      "(`SOURCE-LIBRARY.md`); the engine applies whatever it is given.")
    A("- The engine rates inherent geographic risk; the market/onboarding decision and "
      "any override are human, documented actions. It is not a judgement about a "
      "country or its people.")
    A("")
    A("## 8. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} --jurisdictions {manifest['jurisdictions']}")
    A("```")
    A("")
    return "\n".join(L)


def write_evidence(out_dir, a, mono_ok, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    json.dump({"analysis": a, "monotonicity_ok": mono_ok, "manifest": manifest},
              open(os.path.join(out_dir, "metrics.json"), "w"), indent=2)
    with open(os.path.join(out_dir, "stratum-scores.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stratum", "count", "mean_score"] + [f"tier_{t}" for t in TIERS])
        for s in STRATA:
            if s in a["per_stratum"]:
                p = a["per_stratum"][s]
                w.writerow([s, p["count"], p["mean_score"]] + [p[f"tier_{t}"] for t in TIERS])
    with open(os.path.join(out_dir, "tier-distribution.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["tier", "count", "share"])
        for t in TIERS:
            w.writerow([t, a["tier_distribution"][t], a["tier_shares"][t]])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jurisdictions", type=int, default=40000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = S.Config()
    rows = generate(args.jurisdictions, args.seed)
    a = analyze(score_population(rows, config))
    mono_ok, mono_fail = monotonicity_check()

    print(f"\n=== jurisdiction risk (seed {args.seed}, {args.jurisdictions:,} jurisdictions) ===")
    print(f"tier shares: {a['tier_shares']}")
    means = {s: a["per_stratum"][s]["mean_score"] for s in STRATA if s in a["per_stratum"]}
    print(f"mean score by stratum: {means}")
    print(f"discrimination_ok={a['discrimination_ok']}  critical_floor_breaches="
          f"{a['critical_floor_breaches']}  high_floor_breaches={a['high_floor_breaches']}  "
          f"monotonic={mono_ok}")

    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            at = analyze(score_population(generate(args.jurisdictions, s), config))
            print(f"  trial seed {s}: shares {at['tier_shares']} disc={at['discrimination_ok']} "
                  f"crit_breach={at['critical_floor_breaches']} high_breach={at['high_floor_breaches']}")

    # ---- safety / quality build gate ----
    if (a["critical_floor_breaches"] > 0 or a["high_floor_breaches"] > 0
            or not a["discrimination_ok"] or not mono_ok):
        print("\nGATE FAILED:")
        if a["critical_floor_breaches"] > 0:
            print(f"   {a['critical_floor_breaches']} sanctioned/black-listed jurisdictions rated below CRITICAL")
        if a["high_floor_breaches"] > 0:
            print(f"   {a['high_floor_breaches']} grey/EU/INCSR jurisdictions rated below HIGH")
        if not a["discrimination_ok"]:
            print("   discrimination ordering failed")
        if not mono_ok:
            print("   monotonicity failed:", mono_fail)
        return 1

    manifest = {"framework": "jurisdiction-risk", "seed": args.seed,
                "jurisdictions": args.jurisdictions, "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

    manifest = attest.enrich_manifest(manifest, _T0)
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, a, mono_ok, manifest, render_report(a, mono_ok, manifest))
        print(f"\nevidence written -> {args.out}/  (all gates PASSED)")
    else:
        print("\nall gates PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
