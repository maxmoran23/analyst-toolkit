"""
Validation harness for the adverse-media-screening framework.

Runs the deterministic scorer over the full seeded synthetic population, computes
the asymmetric-error metrics (recall on genuine adverse-media matches must hold at
1.0; false-positive reduction is the operational value), and writes the evidence
pack. Numbers are emitted here, not hand-written.

Enforces false-negative safety as a BUILD GATE: if the engine ever auto-clears a
genuine adverse-media match, or recall falls below the floor, it exits non-zero.

Usage:
    python3 run_validation.py
    python3 run_validation.py --hits 200000
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
from _lib.text_normalize import TokenStats  # noqa: E402
import scorer as S  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

_T0 = time.time()   # wall-clock provenance for the evidence manifest

FN_RECALL_FLOOR = 1.0
SWEEP_THRESHOLDS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
FP_CATEGORIES = ["wrong_entity", "not_adverse", "low_role", "stale_immaterial", "common_name_ambiguous"]


def generate(subjects_n, hits_n, seed):
    import random
    rng = random.Random(seed)
    subjects = G.make_subjects(subjects_n, rng)
    hits = G.make_hits(hits_n, subjects, rng)
    lookup = {s["subject_id"]: s for s in subjects}
    stats = TokenStats.from_names([s["name"] for s in subjects])
    return lookup, hits, stats


def score_population(hits, lookup, stats, config):
    records = []
    for h in hits:
        s = lookup[h["subject_id"]]
        subj = S.Subject(name=s["name"], entity_type=s["entity_type"],
                         ids={k: s[k] for k in ("country", "dob") if s.get(k)})
        art_ids = {}
        if h["art_country"]:
            art_ids["country"] = h["art_country"]
        if h["art_dob"]:
            art_ids["dob"] = h["art_dob"]
        if h["art_passport"]:
            art_ids["passport"] = h["art_passport"]
        hit = S.MediaHit(hit_id=h["hit_id"], article_name=h["article_name"],
                         category=h["category"], role=h["role"], age_days=float(h["age_days"]),
                         article_ids=art_ids, source_reliability=float(h["source_reliability"]))
        d = S.score_hit(subj, hit, stats, config)
        records.append({"label": int(h["label"]), "fp_category": h["fp_category"],
                        "decision": d.decision, "priority": d.priority, "combined": d.combined,
                        "reason": d.reason})
    return records


def operating_point(records):
    y_true = [r["label"] for r in records]
    y_pred = [0 if r["decision"] == "AUTO_CLEAR" else 1 for r in records]
    conf = metrics.confusion(y_true, y_pred)
    funnel = {"AUTO_CLEAR": 0, "ANALYST_REVIEW": 0, "ESCALATE": 0}
    priorities = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in records:
        funnel[r["decision"]] += 1
        if r["decision"] == "ANALYST_REVIEW":
            priorities[r["priority"]] += 1
    cats = {}
    for r in records:
        if r["label"] == 1:
            continue
        c = cats.setdefault(r["fp_category"], {"total": 0, "auto_cleared": 0})
        c["total"] += 1
        if r["decision"] == "AUTO_CLEAR":
            c["auto_cleared"] += 1
    for c in cats.values():
        c["clear_rate"] = round(c["auto_cleared"] / c["total"], 4) if c["total"] else 0.0
    leaked = [r for r in records if r["label"] == 1 and r["decision"] == "AUTO_CLEAR"]
    total = len(records)
    reviewed = funnel["ANALYST_REVIEW"] + funnel["ESCALATE"]
    return {"confusion": conf.as_dict(), "funnel": funnel, "review_priorities": priorities,
            "per_category_clear_rate": cats, "fn_count": conf.fn,
            "fn_leaked_examples": [r["reason"] for r in leaked[:5]],
            "volume": {"total_hits": total, "auto_cleared": funnel["AUTO_CLEAR"],
                       "human_reviewed": reviewed,
                       "human_workload_reduction": round(1 - reviewed / total, 4) if total else 0.0}}


def threshold_sweep(records):
    n_true = sum(r["label"] for r in records)
    n_fp = len(records) - n_true
    rows = []
    for t in SWEEP_THRESHOLDS:
        fp_cleared = sum(1 for r in records if r["label"] == 0 and r["combined"] <= t)
        fn_leaked = sum(1 for r in records if r["label"] == 1 and r["combined"] <= t)
        rows.append({"threshold": t, "fp_cleared": fp_cleared,
                     "fp_clear_rate": round(fp_cleared / n_fp, 4) if n_fp else 0.0,
                     "fn_leaked": fn_leaked,
                     "recall": round(1 - fn_leaked / n_true, 4) if n_true else 1.0})
    return rows


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def render_report(op, sweep, manifest):
    c = op["confusion"]; v = op["volume"]; f = op["funnel"]; cats = op["per_category_clear_rate"]
    cat_rows = [{"fp_category": k, "count": cats[k]["total"], "auto_cleared": cats[k]["auto_cleared"],
                 "clear_rate": cats[k]["clear_rate"]} for k in FP_CATEGORIES if k in cats]
    cat_tbl = metrics.markdown_table(cat_rows, ["fp_category", "count", "auto_cleared", "clear_rate"])
    sweep_tbl = metrics.markdown_table(sweep, ["threshold", "fp_cleared", "fp_clear_rate", "fn_leaked", "recall"])
    L = []; A = L.append
    A("# Validation Report — Adverse-Media-Screening Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the reference "
      "scorer over a seeded, fully synthetic population. No real person or article "
      "is represented. Numbers are emitted by `run_validation.py`, not authored.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['subjects']:,} subjects · "
      f"{manifest['hits']:,} hits · git `{manifest['git_sha']}` · {manifest['generated_utc']}")
    A("")
    A(f"**Headline:** recall on genuine adverse matches **{c['recall']:.4f}** "
      f"(false negatives: **{op['fn_count']}**), false-positive reduction "
      f"**{c['specificity']:.1%}**, human review volume cut by "
      f"**{v['human_workload_reduction']:.1%}** "
      f"({v['total_hits']:,} hits → {v['human_reviewed']:,} to a human).")
    A("")
    A("## 1. Methodology summary")
    A("Each media hit is dispositioned AUTO_CLEAR / ANALYST_REVIEW / ESCALATE on two "
      "axes — is it the right party (entity resolution, reusing the sanctions "
      "name-matching engine), and is it materially adverse (category, role, "
      "recency). Auto-clears only on a named cause; never auto-clears a confirmed "
      "match on material adverse content. Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['hits']:,} hits across {manifest['subjects']:,} subjects (a mix of "
      "common and distinctive names); ~5% genuine adverse matches. False positives "
      "span wrong-party, non-adverse, low-role, stale, and the common-name-ambiguous "
      "residual — common-name matches with no identifier, which cannot be cleared OR "
      "confirmed and must go to a human.")
    A("")
    A("## 3. Operating-point results")
    A(f"- **Recall (adverse matches retained): {c['recall']:.4f}** — "
      f"**false negatives: {op['fn_count']}**")
    A(f"- False-positive reduction (specificity): {c['specificity']:.4f}")
    A(f"- Precision of the retained queue: {c['precision']:.4f}")
    A(f"- Confusion — TP {c['tp']:,} · FP {c['fp']:,} · TN {c['tn']:,} · FN {c['fn']:,}")
    A("")
    A("| Disposition | Count | Share |")
    A("| --- | --- | --- |")
    for k in ("AUTO_CLEAR", "ANALYST_REVIEW", "ESCALATE"):
        A(f"| {k} | {f[k]:,} | {f[k]/v['total_hits']:.1%} |")
    A(f"\nAnalyst-review priority — HIGH {op['review_priorities']['HIGH']:,} · "
      f"MEDIUM {op['review_priorities']['MEDIUM']:,} · LOW {op['review_priorities']['LOW']:,}.")
    A("")
    A("## 4. Per-category false-positive clear rate")
    A("The `common_name_ambiguous` band — a common-name match with no identifier — is "
      "deliberately NOT auto-cleared: it cannot be resolved without more information, "
      "so it is the irreducible queue a human must work. The other categories clear "
      "on a named, provable cause.")
    A("")
    A(cat_tbl)
    A("")
    A("## 5. Threshold-sensitivity analysis")
    A("A naive policy auto-clearing on the combined score `<= T`, for comparison. The "
      "deployed policy clears only on a named cause, holding recall at 1.0 by "
      "construction while a bare threshold leaks true matches as it rises.")
    A("")
    A(sweep_tbl)
    A("")
    A("## 6. False-negative safety argument")
    A(attest.bound_sentence(c["tp"], c["fn"], unit="materially adverse true hits"))
    A("")
    A(f"1. Of {manifest['true_hits']:,} genuine adverse matches, "
      f"**{op['fn_count']} were auto-cleared** — recall {c['recall']:.4f}.")
    A("2. Safety is structural: a genuine adverse match is a name-match on materially "
      "adverse content with the subject as a perpetrator/alleged actor, so it cannot "
      "satisfy any of the four clear causes (wrong-entity, non-adverse, low-role, "
      "stale-immaterial). A common-name match with no identifier is never cleared — "
      "it is routed to review precisely because it cannot be safely resolved.")
    A("3. Enforced as a build gate — `run_validation.py` exits non-zero if any "
      "genuine adverse match is auto-cleared.")
    A("")
    A("## 7. Volume / funnel impact")
    A(f"{v['total_hits']:,} hits → {v['auto_cleared']:,} auto-cleared "
      f"({v['auto_cleared']/v['total_hits']:.1%}) → {v['human_reviewed']:,} to a human "
      f"({v['human_reviewed']/v['total_hits']:.1%}), with recall held at 1.0. FP "
      "reduction is bounded by the common-name-ambiguous residual, which is left open "
      "by design rather than cleared — the honest outcome for unidentifiable matches.")
    A("")
    A("## 8. Limitations")
    A("- Synthetic data models the two false-positive axes (wrong party, "
      "non-material content), not the full nuance of real news text or a real media "
      "classifier. Category and role here are taken as given; in production they come "
      "from an upstream NLP classifier whose own error rate compounds. Calibrate "
      "against a labelled sample (`tuning.md`).")
    A("- The engine dispositions screening hits; the enhanced-review / exit / SAR "
      "decision is a documented human action.")
    A("- A transparent reference implementation, not a production control.")
    A("")
    A("## 9. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} "
      f"--subjects {manifest['subjects']} --hits {manifest['hits']}")
    A("```")
    A("")
    return "\n".join(L)


def write_evidence(out_dir, op, sweep, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    json.dump({"operating_point": op, "manifest": manifest},
              open(os.path.join(out_dir, "metrics.json"), "w"), indent=2)
    with open(os.path.join(out_dir, "threshold-sweep.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sweep[0].keys())); w.writeheader(); w.writerows(sweep)
    c = op["confusion"]
    with open(os.path.join(out_dir, "confusion-matrix.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["", "predicted_adverse", "predicted_cleared"])
        w.writerow(["actual_adverse", c["tp"], c["fn"]])
        w.writerow(["actual_false_positive", c["fp"], c["tn"]])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


def run_once(subjects_n, hits_n, seed, config):
    lookup, hits, stats = generate(subjects_n, hits_n, seed)
    records = score_population(hits, lookup, stats, config)
    return operating_point(records), threshold_sweep(records), records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--subjects", type=int, default=8000)
    ap.add_argument("--hits", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = S.Config()
    op, sweep, records = run_once(args.subjects, args.hits, args.seed, config)
    n_true = sum(r["label"] for r in records)
    c = op["confusion"]
    print(f"\n=== adverse-media screening (seed {args.seed}, {args.hits:,} hits) ===")
    print(f"recall {c['recall']:.4f}  FN {op['fn_count']}  FP-reduction {c['specificity']:.4f}  "
          f"review-cut {op['volume']['human_workload_reduction']:.4f}")
    print("funnel:", op["funnel"])
    print("per-category clear:", {k: v["clear_rate"] for k, v in op["per_category_clear_rate"].items()})

    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            o, _, _ = run_once(args.subjects, args.hits, s, config)
            print(f"  trial seed {s}: recall {o['confusion']['recall']:.4f} FN {o['fn_count']} "
                  f"FP-red {o['confusion']['specificity']:.4f}")

    if op["fn_count"] > 0 or c["recall"] < FN_RECALL_FLOOR:
        print(f"\nFN-SAFETY GATE FAILED: recall {c['recall']:.4f} < {FN_RECALL_FLOOR} "
              f"({op['fn_count']} adverse matches auto-cleared)")
        for ex in op["fn_leaked_examples"]:
            print("   leaked:", ex)
        return 1

    manifest = {"framework": "adverse-media-screening", "seed": args.seed,
                "subjects": args.subjects, "hits": args.hits, "true_hits": n_true,
                "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

    manifest = attest.enrich_manifest(manifest, _T0)
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, op, sweep, manifest, render_report(op, sweep, manifest))
        print(f"\nevidence written -> {args.out}/  (FN-safety gate PASSED)")
    else:
        print("\nFN-safety gate PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
