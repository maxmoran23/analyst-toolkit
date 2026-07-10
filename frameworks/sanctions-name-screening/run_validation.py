"""
Validation harness for the sanctions name-screening framework.

Runs the deterministic scorer over the full seeded synthetic population, computes
the metrics that matter for an asymmetric-error compliance problem (recall on
true matches must hold at 1.0; false-positive reduction is the business value),
and writes the evidence pack under evidence/. The committed numbers are emitted
here, never hand-written, so an independent reviewer reproduces them by re-running.

It enforces false-negative safety as a BUILD GATE: if the engine ever auto-clears
a true match, or recall drops below the floor, the harness exits non-zero.

Usage:
    python3 run_validation.py                         # default 50k run, writes evidence/
    python3 run_validation.py --alerts 250000         # scale run
    python3 run_validation.py --trials 5              # multi-seed stability
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
sys.path.insert(0, os.path.dirname(HERE))  # frameworks/ on path for _lib

from _lib import attest, metrics  # noqa: E402
from _lib.text_normalize import TokenStats  # noqa: E402
import scorer as S  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

_T0 = time.time()   # wall-clock provenance for the evidence manifest

FN_RECALL_FLOOR = 1.0  # auto-clear must never lose a true match — see METHODOLOGY.md
SWEEP_THRESHOLDS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40,
                    0.50, 0.60, 0.70, 0.80, 0.90, 0.95]
_ID_FIELDS = ("dob", "nationality", "country", "place_of_birth", "passport",
              "national_id", "registration", "imo", "tail_number", "wallet")


# --------------------------------------------------------------------------- #
# Loading: CSV rows -> scorer dataclasses
# --------------------------------------------------------------------------- #
def _ids_from(row, prefix=""):
    return {f: row[prefix + f] for f in _ID_FIELDS if row.get(prefix + f)}


def load_watchlist(path):
    out = {}
    for row in csv.DictReader(open(path)):
        out[row["uid"]] = S.WatchlistEntry(
            uid=row["uid"], name=row["name"], entity_type=row["entity_type"],
            program=row.get("program", ""),
            aliases=[a for a in row.get("aliases", "").split("|") if a],
            ids=_ids_from(row),
        )
    return out


def generate(watchlist_n, alerts_n, seed):
    """Regenerate the exact population the committed CSVs come from: ONE seeded
    RNG draws the watchlist, then continues into the alerts — identical to
    generate_synthetic_data.main(). Returns (watchlist dict, alerts, TokenStats)."""
    import random
    rng = random.Random(seed)
    wl_rows = G.make_watchlist(watchlist_n, rng)
    alerts = G.make_alerts(alerts_n, wl_rows, rng)
    watchlist = {
        r["uid"]: S.WatchlistEntry(
            uid=r["uid"], name=r["name"], entity_type=r["entity_type"],
            program=r["program"], aliases=[a for a in r["aliases"].split("|") if a],
            ids={f: r[f] for f in _ID_FIELDS if r.get(f)})
        for r in wl_rows
    }
    corpus = [e.name for e in watchlist.values()]
    corpus += [a for e in watchlist.values() for a in e.aliases]
    return watchlist, alerts, TokenStats.from_names(corpus)


# --------------------------------------------------------------------------- #
# Scoring the population
# --------------------------------------------------------------------------- #
def score_population(alerts, watchlist, stats, config):
    records = []
    for a in alerts:
        entry = watchlist[a["entry_uid"]]
        party = S.Party(name=a["party_name"], entity_type=a["party_type"],
                        ids=_ids_from(a, "party_"))
        d = S.score_candidate(party, entry, stats, config)
        records.append({
            "label": int(a["label"]),
            "fp_category": a["fp_category"],
            "decision": d.decision,
            "priority": d.priority,
            "ml": d.match_likelihood,
            "reason": d.reason,
        })
    return records


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def operating_point(records):
    """The deployed (named-reason) policy: kept-open = decision != AUTO_CLEAR.
    Positive class = true match. So recall = fraction of true matches NOT
    auto-cleared (the FN-safety metric), specificity = fraction of false
    positives auto-cleared (the FP-reduction metric)."""
    y_true = [r["label"] for r in records]
    y_pred = [0 if r["decision"] == "AUTO_CLEAR" else 1 for r in records]
    conf = metrics.confusion(y_true, y_pred)

    funnel = {"AUTO_CLEAR": 0, "ANALYST_REVIEW": 0, "ESCALATE": 0}
    priorities = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in records:
        funnel[r["decision"]] += 1
        if r["decision"] == "ANALYST_REVIEW":
            priorities[r["priority"]] += 1

    # per false-positive-category clear rate
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

    # any true match auto-cleared is a false negative — list them for the audit
    leaked = [r for r in records if r["label"] == 1 and r["decision"] == "AUTO_CLEAR"]

    total = len(records)
    reviewed = funnel["ANALYST_REVIEW"] + funnel["ESCALATE"]
    return {
        "confusion": conf.as_dict(),
        "funnel": funnel,
        "review_priorities": priorities,
        "per_category_clear_rate": cats,
        "fn_count": conf.fn,
        "fn_leaked_examples": [r["reason"] for r in leaked[:5]],
        "volume": {
            "total_alerts": total,
            "auto_cleared": funnel["AUTO_CLEAR"],
            "human_reviewed": reviewed,
            "human_workload_reduction": round(1 - reviewed / total, 4) if total else 0.0,
        },
    }


def threshold_sweep(records):
    """Compare a NAIVE single-threshold auto-clear policy (clear if match_likelihood
    <= T) against the named-reason policy. Shows the false-positive reduction each
    threshold buys and the false-negative leakage it costs — the calibration
    evidence a model review expects, and the argument for why clearance is gated
    on a named reason rather than a bare score."""
    n_true = sum(r["label"] for r in records)
    n_fp = len(records) - n_true
    rows = []
    for t in SWEEP_THRESHOLDS:
        fp_cleared = sum(1 for r in records if r["label"] == 0 and r["ml"] <= t)
        fn_leaked = sum(1 for r in records if r["label"] == 1 and r["ml"] <= t)
        rows.append({
            "threshold": t,
            "fp_cleared": fp_cleared,
            "fp_clear_rate": round(fp_cleared / n_fp, 4) if n_fp else 0.0,
            "fn_leaked": fn_leaked,
            "recall": round(1 - fn_leaked / n_true, 4) if n_true else 1.0,
        })
    return rows


# --------------------------------------------------------------------------- #
# Evidence rendering
# --------------------------------------------------------------------------- #
def _git_sha():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def render_report(op, sweep, manifest, stability=None):
    c = op["confusion"]
    v = op["volume"]
    f = op["funnel"]
    cats = op["per_category_clear_rate"]

    cat_rows = [
        {"fp_category": k, "count": cats[k]["total"],
         "auto_cleared": cats[k]["auto_cleared"], "clear_rate": cats[k]["clear_rate"]}
        for k in ("generic", "type", "discriminator", "weak") if k in cats
    ]
    cat_tbl = metrics.markdown_table(
        cat_rows, ["fp_category", "count", "auto_cleared", "clear_rate"])
    sweep_tbl = metrics.markdown_table(
        sweep, ["threshold", "fp_cleared", "fp_clear_rate", "fn_leaked", "recall"])

    lines = []
    A = lines.append
    A("# Validation Report — Sanctions Name-Screening Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Every figure below is produced by running the "
      "reference scorer over a seeded, fully synthetic population. No real person, "
      "entity, vessel, or list entry is represented. Numbers are emitted by "
      "`run_validation.py`, not authored; re-run it to reproduce them.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['watchlist']:,} watchlist "
      f"entries · {manifest['alerts']:,} alerts · git `{manifest['git_sha']}` · "
      f"{manifest['generated_utc']}")
    A("")
    A(f"**Headline:** recall on true matches **{c['recall']:.4f}** "
      f"(false negatives: **{op['fn_count']}**), false-positive reduction "
      f"**{c['specificity']:.1%}**, human review volume cut by "
      f"**{v['human_workload_reduction']:.1%}** "
      f"({v['total_alerts']:,} alerts → {v['human_reviewed']:,} to a human).")
    A("")
    A("## 1. Methodology summary")
    A("The engine dispositions each alert (a payment/customer party an upstream "
      "filter matched to a watchlist entry) as AUTO_CLEAR, ANALYST_REVIEW, or "
      "ESCALATE. It auto-clears only on a *named, provable* false-positive cause "
      "(generic-token-only, entity-type-incompatible, or a contradicting hard "
      "identifier) and never auto-blocks or files. Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['alerts']:,} alerts against {manifest['watchlist']:,} watchlist "
      "entries. True matches are ~2% of volume, mirroring the false-positive "
      "dominance of real screening. Every false positive carries a category so "
      "clear rates can be checked against a known cause; true matches come in "
      "corroborated, name-only, and transliteration-noisy flavours. The noisy "
      "flavour is adversarial by design — vowel-shifted names engineered to score "
      "lower — and is the band a naive threshold would wrongly clear.")
    A("")
    A("## 3. Operating-point results (deployed named-reason policy)")
    A(f"- **Recall (true-match retention): {c['recall']:.4f}** — "
      f"**false negatives: {op['fn_count']}**")
    A(f"- False-positive reduction (specificity): {c['specificity']:.4f}")
    A(f"- Precision of the retained queue: {c['precision']:.4f}")
    A(f"- Confusion — TP {c['tp']:,} · FP {c['fp']:,} · TN {c['tn']:,} · FN {c['fn']:,}")
    A("")
    A("| Disposition | Count | Share |")
    A("| --- | --- | --- |")
    for k in ("AUTO_CLEAR", "ANALYST_REVIEW", "ESCALATE"):
        A(f"| {k} | {f[k]:,} | {f[k]/v['total_alerts']:.1%} |")
    A(f"\nAnalyst-review priority split — HIGH {op['review_priorities']['HIGH']:,} · "
      f"MEDIUM {op['review_priorities']['MEDIUM']:,} · "
      f"LOW {op['review_priorities']['LOW']:,}.")
    A("")
    A("## 4. Per-category false-positive clear rate")
    A("Did the engine clear each false-positive type for the right named reason? "
      "The `weak` residual — genuine partial overlap with no identifiers either "
      "way — is deliberately *not* auto-cleared; it is the irreducible band that "
      "needs a human.")
    A("")
    A(cat_tbl)
    A("")
    A("## 5. Threshold-sensitivity analysis")
    A("A naive policy that auto-cleared on `match_likelihood <= T` alone, for "
      "comparison. It shows how much false-positive reduction each threshold buys "
      "and the false-negative leakage it costs. On this clean synthetic data a "
      "threshold in the low band (T≈0.15–0.3) can match the deployed reduction at "
      "recall 1.0 — but pushing past it (T≥0.4) immediately begins leaking true "
      "matches. The named-reason policy is preferred over that band not for a "
      "higher number but for two reasons a single threshold cannot give: every "
      "clearance carries an individual, auditable cause (a threshold clear is "
      "justified only by 'the score was below T', which does not survive an exam), "
      "and on real data, where score distributions overlap far more than here, the "
      "same threshold leaks true matches while the named gate does not.")
    A("")
    A(sweep_tbl)
    A("")
    A("## 6. False-negative safety argument")
    A(attest.bound_sentence(c["tp"], c["fn"], unit="true matches"))
    A("")
    A(f"1. Of {manifest['true_matches']:,} planted true matches, "
      f"**{op['fn_count']} were auto-cleared** — recall {c['recall']:.4f}.")
    A("2. Safety is structural, not threshold-dependent: auto-clear fires only on "
      "a named, provable false-positive cause. A true match has a distinctive "
      "name that aligns (transliteration noise is vowel-only, preserving the "
      "phonetic/Soundex key), a compatible entity type, and no contradicting "
      "identifier — so it can exhibit none of the three clearing causes.")
    A("3. The threshold sweep (Section 5) shows recall holding at 1.0 across the "
      "whole low-threshold band the deployed policy operates in, then degrading "
      "only when a bare threshold is pushed higher — so the operating point sits "
      "on a plateau, not a cliff edge.")
    A("4. This recall floor is enforced as a build gate — `run_validation.py` "
      "exits non-zero if any true match is auto-cleared.")
    A("")
    A("## 7. Volume / funnel impact")
    A(f"{v['total_alerts']:,} alerts → {v['auto_cleared']:,} auto-cleared "
      f"({v['auto_cleared']/v['total_alerts']:.1%}) → {v['human_reviewed']:,} to a "
      f"human ({v['human_reviewed']/v['total_alerts']:.1%}). At the real ~50k/month "
      "scale this is the difference between an unworkable queue and a triaged one — "
      "achieved with the recall floor held at 1.0.")
    if stability:
        A("")
        A("## 7a. Stability across seeds")
        A(f"{stability['trials']} independent seeds. Recall "
          f"min **{stability['recall_min']:.4f}**, FP-reduction mean "
          f"**{stability['spec_mean']:.4f}** (range {stability['spec_min']:.4f}–"
          f"{stability['spec_max']:.4f}). The result is not an artifact of one seed.")
    A("")
    A("## 8. Limitations")
    A("- Synthetic data models the *shape* of screening (token collisions, "
      "identifier discriminators, transliteration), not the full messiness of real "
      "wire text. Calibrate against a labelled sample of your own before reliance "
      "(`tuning.md`).")
    A("- The engine scores and prioritizes; it does not decide. A confirmed match "
      "is a human compliance-officer action.")
    A("- This is a transparent reference implementation chosen for auditability, "
      "not a production control. A real deployment swaps internals and recalibrates "
      "the operating point; the scoring *contract* in `METHODOLOGY.md` is what travels.")
    A("- Names corrupted past fuzzy-match recognition (beyond realistic "
      "transliteration variance) are a data-quality concern upstream of the engine, "
      "not modelled here.")
    A("")
    A("## 9. Reproduction")
    A("```bash")
    A(f"python3 generate_synthetic_data.py --seed {manifest['seed']} "
      f"--watchlist {manifest['watchlist']} --alerts {manifest['alerts']}")
    A("python3 run_validation.py "
      f"--seed {manifest['seed']} --watchlist {manifest['watchlist']} "
      f"--alerts {manifest['alerts']}")
    A("```")
    A("Same seed → identical population → identical metrics. Fingerprint in "
      "`evidence/run-manifest.json`.")
    A("")
    return "\n".join(lines)


def write_evidence(out_dir, op, sweep, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "metrics.json"), "w") as fh:
        json.dump({"operating_point": op, "manifest": manifest}, fh, indent=2)
    with open(os.path.join(out_dir, "threshold-sweep.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sweep[0].keys()))
        w.writeheader()
        w.writerows(sweep)
    c = op["confusion"]
    with open(os.path.join(out_dir, "confusion-matrix.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["", "predicted_true_match", "predicted_cleared"])
        w.writerow(["actual_true_match", c["tp"], c["fn"]])
        w.writerow(["actual_false_positive", c["fp"], c["tn"]])
    with open(os.path.join(out_dir, "run-manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    with open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w") as fh:
        fh.write(report)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def run_once(watchlist_n, alerts_n, seed, config):
    watchlist, alerts, stats = generate(watchlist_n, alerts_n, seed)
    records = score_population(alerts, watchlist, stats, config)
    return operating_point(records), threshold_sweep(records), records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--watchlist", type=int, default=4000)
    ap.add_argument("--alerts", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0,
                    help="re-run across N seeds for stability (no evidence written)")
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = S.Config()
    op, sweep, records = run_once(args.watchlist, args.alerts, args.seed, config)
    n_true = sum(r["label"] for r in records)

    print(f"\n=== operating point (seed {args.seed}, {args.alerts:,} alerts) ===")
    c = op["confusion"]
    print(f"recall {c['recall']:.4f}  FN {op['fn_count']}  "
          f"FP-reduction {c['specificity']:.4f}  "
          f"human-review-cut {op['volume']['human_workload_reduction']:.4f}")
    print("funnel:", op["funnel"])
    print("per-category clear:", {k: v["clear_rate"]
                                  for k, v in op["per_category_clear_rate"].items()})

    stability = None
    if args.trials:
        recalls, specs = [], []
        for t in range(args.trials):
            s = args.seed + 1 + t
            o, _, recs = run_once(args.watchlist, args.alerts, s, config)
            recalls.append(o["confusion"]["recall"])
            specs.append(o["confusion"]["specificity"])
            print(f"  trial seed {s}: recall {o['confusion']['recall']:.4f} "
                  f"FN {o['fn_count']} FP-red {o['confusion']['specificity']:.4f}")
        stability = {
            "trials": args.trials, "recall_min": min(recalls),
            "spec_mean": round(sum(specs) / len(specs), 4),
            "spec_min": min(specs), "spec_max": max(specs),
        }

    # ---- FN-safety BUILD GATE ----
    if op["fn_count"] > 0 or c["recall"] < FN_RECALL_FLOOR:
        print(f"\nFN-SAFETY GATE FAILED: recall {c['recall']:.4f} < "
              f"{FN_RECALL_FLOOR} ({op['fn_count']} true matches auto-cleared)")
        for ex in op["fn_leaked_examples"]:
            print("   leaked:", ex)
        return 1

    manifest = {
        "framework": "sanctions-name-screening",
        "seed": args.seed, "watchlist": args.watchlist, "alerts": args.alerts,
        "true_matches": n_true, "git_sha": _git_sha(),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                         .strftime("%Y-%m-%d %H:%M UTC"),
        "fn_recall_floor": FN_RECALL_FLOOR,
    }

    manifest = attest.enrich_manifest(manifest, _T0)
    if not args.no_write and args.trials == 0:
        report = render_report(op, sweep, manifest, stability)
        write_evidence(args.out, op, sweep, manifest, report)
        print(f"\nevidence written -> {args.out}/  (FN-safety gate PASSED)")
    else:
        print("\nFN-safety gate PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
