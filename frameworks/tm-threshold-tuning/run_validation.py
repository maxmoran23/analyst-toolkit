"""
Validation harness for the transaction-monitoring threshold-tuning framework.

Runs the tuning engine over a seeded population of monitoring rules whose correct
action is known by construction, and checks the properties that matter for a
tuning/model-validation tool: does it recommend the right direction, does every
recommendation keep detection at or above the required floor, and does it remediate
every rule that currently leaks suspicious activity below the line?

Enforces the safety property as a BUILD GATE: if any recommended threshold detects
below the recall floor, or any leaking (too-high) rule is not recommended DOWN, it
exits non-zero.

Usage:
    python3 run_validation.py
    python3 run_validation.py --population 100000     # ~1.2M observations
    python3 run_validation.py --trials 5
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import subprocess
import time
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from _lib import attest, metrics  # noqa: E402
import engine as E  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

_T0 = time.time()   # wall-clock provenance for the evidence manifest

EXPECTED_ACTION = {"too_low": "RAISE", "too_high": "LOWER", "optimal": "KEEP"}


def generate(rules_n, population, seed):
    import random
    rng = random.Random(seed)
    rules = []
    for i in range(rules_n):
        rule, obs = G.make_rule("RULE-%03d" % i, population, rng)
        values = [v for v, _ in obs]
        labels = [lab for _, lab in obs]
        rules.append((E.Rule(rule["rule_id"], rule["metric_name"], rule["current_threshold"]),
                      rule["scenario"], values, labels))
    return rules


def evaluate(rules, config):
    results = []
    for rule, scenario, values, labels in rules:
        res = E.tune_rule(rule, values, labels, config)
        results.append({"rule": rule.name, "scenario": scenario, "action": res.action,
                        "expected": EXPECTED_ACTION[scenario],
                        "current_threshold": res.current_threshold,
                        "recommended_threshold": res.recommended_threshold,
                        "current_detection": res.current["detection_rate"],
                        "recommended_detection": res.recommended["detection_rate"],
                        "current_volume": res.current["alert_volume"],
                        "recommended_volume": res.recommended["alert_volume"],
                        "sweep": res.sweep})
    return results


def analyze(results, config):
    n = len(results)
    correct = sum(1 for r in results if r["action"] == r["expected"])
    min_rec_det = min(r["recommended_detection"] for r in results)
    safety_ok = all(r["recommended_detection"] >= config.recall_floor for r in results)
    too_high = [r for r in results if r["scenario"] == "too_high"]
    leaks = [r for r in too_high if r["current_detection"] < config.recall_floor]
    leaks_fixed = sum(1 for r in leaks
                      if r["action"] == "LOWER" and r["recommended_detection"] >= config.recall_floor)
    leaks_remediated = (leaks_fixed == len(leaks))
    # volume impact on RAISE rules (over-alerting rules that can be safely cut)
    raises = [r for r in results if r["action"] == "RAISE"]
    vol_before = sum(r["current_volume"] for r in raises)
    vol_after = sum(r["recommended_volume"] for r in raises)
    return {"n_rules": n, "action_accuracy": round(correct / n, 4) if n else 0.0,
            "min_recommended_detection": min_rec_det, "safety_ok": safety_ok,
            "leaking_rules": len(leaks), "leaks_remediated": leaks_remediated,
            "leaks_fixed": leaks_fixed,
            "raise_volume_before": vol_before, "raise_volume_after": vol_after,
            "raise_volume_reduction": round(1 - vol_after / vol_before, 4) if vol_before else 0.0}


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def render_report(results, a, manifest, config):
    rec_rows = [{"rule": r["rule"], "scenario": r["scenario"], "action": r["action"],
                 "cur_thr": round(r["current_threshold"], 1),
                 "rec_thr": round(r["recommended_threshold"], 1),
                 "cur_det": r["current_detection"], "rec_det": r["recommended_detection"],
                 "cur_vol": r["current_volume"], "rec_vol": r["recommended_volume"]}
                for r in results]
    rec_tbl = metrics.markdown_table(rec_rows, ["rule", "scenario", "action", "cur_thr",
                                                "rec_thr", "cur_det", "rec_det", "cur_vol", "rec_vol"])
    # one illustrative ATL/BTL sweep (a too_high rule if present)
    ex = next((r for r in results if r["scenario"] == "too_high"), results[0])
    sweep_rows = ex["sweep"][::max(1, len(ex["sweep"]) // 12)]
    sweep_tbl = metrics.markdown_table(sweep_rows,
                                       ["threshold", "alert_volume", "productivity", "detection_rate", "btl_missed"])

    L = []; A = L.append
    A("# Validation Report — Transaction-Monitoring Threshold-Tuning Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the tuning engine "
      "over a seeded population of monitoring rules whose correct action is known by "
      "construction. No real rule or customer is represented. Numbers are emitted by "
      "`run_validation.py`, not authored.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['rules']} rules · "
      f"{manifest['observations']:,} observations · git `{manifest['git_sha']}` · "
      f"{manifest['generated_utc']}")
    A("")
    A(f"**Headline:** every recommendation keeps detection at or above the "
      f"{config.recall_floor:.0%} floor (min **{a['min_recommended_detection']:.4f}**), "
      f"all **{a['leaking_rules']}** leaking rules remediated, recommendation-direction "
      f"accuracy **{a['action_accuracy']:.0%}**.")
    A("")
    A("## 1. Methodology summary")
    A("For each monitoring rule the engine runs above/below-the-line testing across "
      "candidate thresholds (a thin layer over `_lib/metrics.sweep`): ATL productivity "
      "is the precision of the alerts, BTL leakage is the suspicious activity below "
      "the threshold. It recommends the HIGHEST threshold that still detects at least "
      "the recall floor of suspicious activity — cutting alert volume only where it is "
      "safe to do so. Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Population construction")
    A(f"{manifest['rules']} rules x {manifest['observations']//manifest['rules']:,} "
      "observations each. Each rule's suspicious population sits higher on its metric "
      "than its benign population; the current threshold is set by a designed scenario "
      "(too_low / too_high / optimal) relative to the optimal threshold. The correct "
      "action is therefore known and is NOT used by the engine — only the metric "
      "values and labels are.")
    A("")
    A("## 3. Recommendations (per rule)")
    A(rec_tbl)
    A(f"\nRecommendation-direction accuracy vs the designed scenario: "
      f"**{a['action_accuracy']:.0%}**.")
    A("")
    A("## 4. Below-the-line safety (the gate)")
    A(f"- Minimum recommended detection across all rules: "
      f"**{a['min_recommended_detection']:.4f}** (floor {config.recall_floor:.0%}).")
    A(f"- Leaking rules (current threshold detects below the floor): "
      f"**{a['leaking_rules']}**; remediated (recommended DOWN to restore detection): "
      f"**{a['leaks_fixed']}/{a['leaking_rules']}**.")
    A("No recommendation trades detection below the floor for alert-volume reduction — "
      "this is the regulator-facing safety property, enforced as a build gate.")
    A("")
    A("## 5. ATL/BTL sweep — illustrative rule")
    A(f"Rule `{ex['rule']}` ({ex['scenario']}). As the threshold rises, alert volume "
      "and BTL-missed move in opposite directions; the engine reads the highest "
      "threshold where detection still clears the floor.")
    A("")
    A(sweep_tbl)
    A("")
    A("## 6. Alert-volume impact")
    A(f"On the over-alerting rules recommended for RAISE, alert volume falls from "
      f"{a['raise_volume_before']:,} to {a['raise_volume_after']:,} "
      f"(**{a['raise_volume_reduction']:.0%}** reduction) with detection held at or "
      "above the floor — the productivity gain from tuning.")
    A("")
    A("## 7. Limitations")
    A("- Synthetic metric distributions are unimodal per class; real rule metrics are "
      "messier and the 'suspicious' label is itself a historical disposition with its "
      "own error. The recall floor is a policy choice — set it from your risk "
      "appetite. Calibrate against a labelled sample (`tuning.md`).")
    A("- The engine recommends; a threshold change is a governed model-change decision "
      "a human approves and documents.")
    A("- A transparent reference implementation, not a production control.")
    A("")
    A("## 8. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} --rules {manifest['rules']} "
      f"--population {manifest['observations']//manifest['rules']}")
    A("```")
    A("")
    return "\n".join(L)


def write_evidence(out_dir, results, a, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    json.dump({"analysis": a, "manifest": manifest},
              open(os.path.join(out_dir, "metrics.json"), "w"), indent=2)
    with open(os.path.join(out_dir, "rule-recommendations.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["rule", "scenario", "action", "current_threshold", "recommended_threshold",
                    "current_detection", "recommended_detection", "current_volume", "recommended_volume"])
        for r in results:
            w.writerow([r["rule"], r["scenario"], r["action"], r["current_threshold"],
                        r["recommended_threshold"], r["current_detection"],
                        r["recommended_detection"], r["current_volume"], r["recommended_volume"]])
    ex = next((r for r in results if r["scenario"] == "too_high"), results[0])
    with open(os.path.join(out_dir, "example-atl-btl-sweep.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["threshold", "alert_volume", "productivity",
                                           "detection_rate", "btl_missed"])
        w.writeheader()
        w.writerows(ex["sweep"])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


def run_once(rules_n, population, seed, config):
    rules = generate(rules_n, population, seed)
    results = evaluate(rules, config)
    return results, analyze(results, config)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rules", type=int, default=12)
    ap.add_argument("--population", type=int, default=40000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = E.Config()
    results, a = run_once(args.rules, args.population, args.seed, config)
    obs = args.rules * args.population
    print(f"\n=== TM threshold tuning (seed {args.seed}, {args.rules} rules, {obs:,} obs) ===")
    print(f"action_accuracy {a['action_accuracy']:.4f}  min_rec_detection {a['min_recommended_detection']:.4f}  "
          f"safety_ok {a['safety_ok']}")
    print(f"leaking rules {a['leaking_rules']} -> remediated {a['leaks_fixed']}; "
          f"RAISE volume reduction {a['raise_volume_reduction']:.4f}")

    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            _, at = run_once(args.rules, args.population, s, config)
            print(f"  trial seed {s}: acc {at['action_accuracy']:.2f} min_det "
                  f"{at['min_recommended_detection']:.3f} leaks_remediated {at['leaks_remediated']}")

    # ---- safety build gate ----
    if not a["safety_ok"] or not a["leaks_remediated"]:
        print("\nSAFETY GATE FAILED:")
        if not a["safety_ok"]:
            print(f"   a recommendation detects below the {config.recall_floor:.0%} floor "
                  f"(min {a['min_recommended_detection']:.4f})")
        if not a["leaks_remediated"]:
            print(f"   {a['leaking_rules'] - a['leaks_fixed']} leaking rule(s) not remediated")
        return 1

    manifest = {"framework": "tm-threshold-tuning", "seed": args.seed, "rules": args.rules,
                "observations": obs, "recall_floor": config.recall_floor, "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

    manifest = attest.enrich_manifest(manifest, _T0)
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, results, a, manifest, render_report(results, a, manifest, config))
        print(f"\nevidence written -> {args.out}/  (safety gate PASSED)")
    else:
        print("\nsafety gate PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
