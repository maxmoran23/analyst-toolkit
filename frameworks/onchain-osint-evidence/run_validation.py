"""
Validation harness for the on-chain OSINT evidence framework.

Generates the seeded synthetic explorer-fixture population WITH ground truth,
writes it to disk as fixture files, runs the engine over those files (the same
offline/fixture path a user runs — no network anywhere), and enforces the three
properties that make an evidence pack investigation-grade, as BUILD GATES:

  * PROVENANCE COMPLETENESS — 100% of emitted facts carry every provenance field
    (source URI, retrieval timestamp, content sha256, origin id). An
    unprovenance'd fact is an assertion, not evidence.
  * RECONCILIATION — engine totals (tx counts, per-direction value sums, token
    transfer counts, counterparty counts) equal the fixture-source ground truth
    EXACTLY: 0 records dropped, 0 double-counted, pagination overlap deduplicated
    exactly once, and BTC parsed totals tie to the explorer's own summary.
  * DETERMINISM — two runs over the same fixtures produce byte-identical annex +
    CSVs (the run timestamp is isolated to the evidence manifest).

Also verified: planted structural observations are detected exactly (no misses,
no spurious flags), the committed fixtures/sample/ round-trips from disk against
its committed truth, and the optional live-mode collectors degrade to None
offline without raising. Any violation exits non-zero.

Usage:
    python3 run_validation.py
    python3 run_validation.py --addresses 400 --transactions 50000
    python3 run_validation.py --trials 6 --no-write
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import os
import random
import shutil
import subprocess
import time
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # frameworks/ on path

from _lib import provenance as P  # noqa: E402
from _lib import attest  # noqa: E402
import engine as E  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

_T0 = time.time()   # wall-clock provenance for the evidence manifest

PROVENANCE_FLOOR = 1.0            # every fact fully provenance-stamped
RECONCILIATION_TOLERANCE = 0      # exact — no dropped, no duplicated

_COUNT_MEASURES = ("native_tx_count", "token_transfer_count")
_EXACT_MEASURES = ("native_tx_count", "token_transfer_count", "value_in",
                   "value_out", "self_transfer_count", "counterparty_count")


# --------------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------------

def process(esets, config):
    return [E.build_pack(s, config) for s in esets]


def render_digest(packs):
    """One digest over every deterministic rendered artifact (annex + both CSVs),
    in set order. Byte-identical output <=> identical digest."""
    h = hashlib.sha256()
    for p in sorted(packs, key=lambda p: p.set_id):
        h.update(p.annex_md.encode("utf-8"))
        h.update(p.facts_csv.encode("utf-8"))
        h.update(p.counterparties_csv.encode("utf-8"))
    return h.hexdigest()


def reconcile(packs, truths):
    """Per-set exact tie-out of engine output against generator ground truth."""
    rows, mismatches = [], []
    dropped = duplicated = 0
    dup_planted = dup_removed = 0
    ties_ok = True
    agg = {}

    def bump(chain, measure, t, e):
        a = agg.setdefault((chain, measure), {"truth": 0, "engine": 0})
        a["truth"] += t
        a["engine"] += e

    for p in sorted(packs, key=lambda p: p.set_id):
        t = truths[p.set_id]
        s = p.stats
        engine_vals = {"native_tx_count": s["native_unique"],
                       "token_transfer_count": s["token_unique"],
                       "value_in": s["value_in"], "value_out": s["value_out"],
                       "self_transfer_count": s["self_transfer_count"],
                       "counterparty_count": s["counterparty_count"]}
        exact = True
        for m in _EXACT_MEASURES:
            bump(t["chain"], m, t[m], engine_vals[m])
            if engine_vals[m] != t[m]:
                exact = False
                mismatches.append({"set_id": p.set_id, "measure": m,
                                   "truth": t[m], "engine": engine_vals[m]})
            if m in _COUNT_MEASURES:
                dropped += max(0, t[m] - engine_vals[m])
                duplicated += max(0, engine_vals[m] - t[m])
        dup_planted += t["duplicates_planted"]
        dup_removed += s["duplicates_removed"]
        if s["duplicates_removed"] != t["duplicates_planted"]:
            exact = False
            mismatches.append({"set_id": p.set_id, "measure": "duplicates_removed",
                               "truth": t["duplicates_planted"],
                               "engine": s["duplicates_removed"]})
        if not s["summary_ties_to_parsed"]:
            exact = False
            ties_ok = False
            mismatches.append({"set_id": p.set_id, "measure": "summary_tie",
                               "truth": "EXACT", "engine": "MISMATCH"})
        rows.append({"set_id": p.set_id, "chain": t["chain"],
                     **{"%s_truth" % m: t[m] for m in _EXACT_MEASURES},
                     **{"%s_engine" % m: engine_vals[m] for m in _EXACT_MEASURES},
                     "duplicates_planted": t["duplicates_planted"],
                     "duplicates_removed": s["duplicates_removed"],
                     "exact": exact})

    agg_rows = [{"chain": c, "measure": m, "source_truth": v["truth"],
                 "engine": v["engine"], "delta": v["engine"] - v["truth"]}
                for (c, m), v in sorted(agg.items())]
    agg_rows.append({"chain": "all", "measure": "pagination_duplicates",
                     "source_truth": dup_planted, "engine": dup_removed,
                     "delta": dup_removed - dup_planted})
    n_exact = sum(1 for r in rows if r["exact"])
    return {"sets": len(rows), "exact_sets": n_exact,
            "mismatched_sets": len(rows) - n_exact,
            "dropped_records": dropped, "duplicated_records": duplicated,
            "duplicates_planted": dup_planted, "duplicates_removed": dup_removed,
            "btc_summary_ties": ties_ok, "aggregate": agg_rows,
            "mismatch_examples": mismatches[:10], "per_set_rows": rows}


def check_observations(packs, truths):
    missed, spurious = [], []
    planted = detected = 0
    for p in sorted(packs, key=lambda p: p.set_id):
        expected = set(truths[p.set_id]["expected_observations"])
        got = {o["id"] for o in p.observations}
        planted += len(expected)
        detected += len(expected & got)
        for oid in sorted(expected - got):
            missed.append({"set_id": p.set_id, "observation": oid})
        for oid in sorted(got - expected):
            spurious.append({"set_id": p.set_id, "observation": oid})
    return {"planted": planted, "detected": detected,
            "missed": len(missed), "spurious": len(spurious),
            "missed_examples": missed[:5], "spurious_examples": spurious[:5],
            "ok": not missed and not spurious}


def check_live_degrade():
    """The optional live collectors must degrade to None offline — no exception,
    no network. This is the only brush CI has with the live path."""
    checks = {
        "fetch_json_offline_none": E.fetch_json("https://host.invalid/x", offline=True) is None,
        "collect_evm_offline_none": E.collect_live_evm("https://host.invalid", "0xabc",
                                                       offline=True) is None,
        "collect_btc_offline_none": E.collect_live_btc("https://host.invalid", "bc1qabc",
                                                       offline=True) is None,
        "collect_evm_no_base_none": E.collect_live_evm("", "0xabc", offline=True) is None,
    }
    return {**checks, "all_none": all(checks.values())}


def run_once(n_addresses, n_transactions, seed, config, use_disk=False, data_dir=None):
    rng = random.Random(seed)
    specs, truths = G.build_population(n_addresses, n_transactions, rng)
    if use_disk:
        shutil.rmtree(data_dir, ignore_errors=True)
        G.write_fixtures(specs, data_dir)
        G.write_truth(truths, data_dir)
        esets = E.load_fixture_dir(data_dir)
    else:
        esets = G.to_engine_sets(specs)
    packs = process(esets, config)
    digest_1 = render_digest(packs)
    digest_2 = render_digest(process(esets, config))     # full second pass
    all_facts = [f for p in packs for f in p.facts]
    return {
        "packs": packs, "truths": truths,
        "provenance": P.completeness(all_facts),
        "reconciliation": reconcile(packs, truths),
        "observations": check_observations(packs, truths),
        "determinism": {"digest": digest_1, "identical": digest_1 == digest_2,
                        "artifacts_hashed": ["annex.md", "facts.csv", "counterparties.csv"]},
        "facts_emitted": len(all_facts),
        "unique_records": sum(p.stats["native_unique"] + p.stats["token_unique"]
                              for p in packs),
        "records_seen": sum(p.stats["native_records_seen"] + p.stats["token_records_seen"]
                            for p in packs),
        "evm_sets": sum(1 for p in packs if p.chain == "evm"),
        "btc_sets": sum(1 for p in packs if p.chain == "btc"),
    }


def check_sample(config):
    """The committed fixtures/sample/ must round-trip from disk against its
    committed truth — same gates, real files."""
    sample_dir = os.path.join(HERE, "fixtures", "sample")
    truth_path = os.path.join(sample_dir, "truth.json")
    if not os.path.exists(truth_path):
        return {"present": False}
    truths = json.load(open(truth_path))
    esets = E.load_fixture_dir(sample_dir)
    packs = process(esets, config)
    d1 = render_digest(packs)
    d2 = render_digest(process(esets, config))
    all_facts = [f for p in packs for f in p.facts]
    return {"present": True, "sets": len(packs),
            "facts": len(all_facts),
            "provenance": P.completeness(all_facts),
            "reconciliation": reconcile(packs, truths),
            "observations": check_observations(packs, truths),
            "determinism": {"digest": d1, "identical": d1 == d2},
            "packs": packs}


def gate_failures(tag, res):
    fails = []
    if res["provenance"]["complete_rate"] < PROVENANCE_FLOOR:
        fails.append("%s: provenance completeness %.4f < %.1f (%d incomplete facts)"
                     % (tag, res["provenance"]["complete_rate"], PROVENANCE_FLOOR,
                        res["provenance"]["incomplete"]))
    r = res["reconciliation"]
    if (r["mismatched_sets"] > RECONCILIATION_TOLERANCE
            or r["dropped_records"] > 0 or r["duplicated_records"] > 0):
        fails.append("%s: reconciliation not exact — %d mismatched sets, %d dropped, "
                     "%d duplicated" % (tag, r["mismatched_sets"],
                                        r["dropped_records"], r["duplicated_records"]))
    if not r["btc_summary_ties"]:
        fails.append("%s: BTC parsed totals do not tie to the explorer summary" % tag)
    if not res["determinism"]["identical"]:
        fails.append("%s: NON-DETERMINISTIC — repeat run digests differ" % tag)
    if not res["observations"]["ok"]:
        fails.append("%s: observations — %d planted missed, %d spurious"
                     % (tag, res["observations"]["missed"], res["observations"]["spurious"]))
    return fails


# --------------------------------------------------------------------------------
# evidence
# --------------------------------------------------------------------------------

def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _mdtable(rows, columns):
    head = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = "\n".join("| " + " | ".join(str(r.get(c, "")) for c in columns) + " |"
                     for r in rows)
    return "\n".join([head, sep, body])


def render_report(res, sample, degrade, manifest):
    pr, rc, ob, dt = (res["provenance"], res["reconciliation"],
                      res["observations"], res["determinism"])
    L = []
    A = L.append
    A("# Validation Report — On-Chain OSINT Evidence Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the engine over "
      "a seeded population of synthetic explorer fixtures (Blockscout-style EVM and "
      "mempool-style BTC payloads) with known ground truth. No real address, "
      "transaction, or explorer is represented. Numbers are emitted by "
      "`run_validation.py`, not authored.")
    A("")
    A("**Run:** seed `%d` · %d addresses (%d EVM / %d BTC) · %s unique transaction "
      "records (%s source records incl. planted duplicates) · git `%s` · %s"
      % (manifest["seed"], rc["sets"], res["evm_sets"], res["btc_sets"],
         format(res["unique_records"], ","), format(res["records_seen"], ","),
         manifest["git_sha"], manifest["generated_utc"]))
    A("")
    A("**Headline:** provenance completeness **%.1f%%** across **%s facts** (floor "
      "100%%), reconciliation **exact** — **%d dropped / %d duplicated** (%s "
      "pagination duplicates planted, %s removed), rendered evidence "
      "**byte-identical across repeat runs** (digest `%s`)."
      % (100 * pr["complete_rate"], format(res["facts_emitted"], ","),
         rc["dropped_records"], rc["duplicated_records"],
         format(rc["duplicates_planted"], ","), format(rc["duplicates_removed"], ","),
         dt["digest"][:16]))
    A("")
    A("## 1. What this validates")
    A("The engine turns public block-explorer payloads into an investigation-grade "
      "evidence pack: every fact provenance-stamped (source URI, retrieval time, "
      "content sha256, origin id), totals reconciled exactly to source, output "
      "deterministic, and structural patterns flagged by named rule without "
      "attribution. It assembles and routes evidence to a human investigator — it "
      "never blocks, files, or concludes who controls an address. Full spec: "
      "`METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A("%d fixture sets written to disk as explorer-shaped capture files and read "
      "back exactly as a user run would. Adversarial plants: multi-page pagination "
      "with boundary duplicates (dedupe exactly once), dust/airdrop spam, "
      "self-transfers, mixed-case display forms of one EVM address, token decimal "
      "traps (6/8/18), and zero-value transfers. Ground truth (counts, per-direction "
      "value sums, counterparties, planted duplicates, expected observations) is "
      "recorded at generation." % rc["sets"])
    A("")
    A("## 3. Provenance completeness (gate: 100%)")
    A("- Facts emitted: **%s** — complete: **%s** — incomplete: **%d**"
      % (format(pr["total_facts"], ","), format(pr["complete"], ","), pr["incomplete"]))
    A("- Completeness: **%.4f** (floor %.1f). A fact missing any provenance field "
      "fails the build." % (pr["complete_rate"], PROVENANCE_FLOOR))
    A("")
    A("## 4. Reconciliation (gate: exact)")
    A("Engine totals vs fixture-source ground truth, aggregated over all sets "
      "(every set is also checked individually — %d/%d exact):"
      % (rc["exact_sets"], rc["sets"]))
    A("")
    A(_mdtable(rc["aggregate"], ["chain", "measure", "source_truth", "engine", "delta"]))
    A("")
    A("- Records dropped: **%d** · double-counted: **%d** (tolerance %d)"
      % (rc["dropped_records"], rc["duplicated_records"], RECONCILIATION_TOLERANCE))
    A("- Pagination duplicates: planted %s, removed %s — deduplicated exactly once, "
      "on the one named cause (identical record across a page boundary)."
      % (format(rc["duplicates_planted"], ","), format(rc["duplicates_removed"], ",")))
    A("- BTC parsed totals tie to the explorer's own `chain_stats`: **%s**"
      % ("EXACT" if rc["btc_summary_ties"] else "MISMATCH"))
    if rc["mismatch_examples"]:
        A("- Mismatch examples (should be none): %s" % rc["mismatch_examples"])
    A("")
    A("## 5. Determinism (gate: byte-identical)")
    A("Two full passes over the same fixture files: annex + facts CSV + "
      "counterparty CSV digests **%s** (`%s`). The run timestamp exists only in "
      "the evidence manifest, never in rendered evidence."
      % ("identical" if dt["identical"] else "DIFFER", dt["digest"][:32]))
    A("")
    A("## 6. Structural observations (planted vs detected)")
    A("- Planted: **%d** · detected: **%d** · missed: **%d** · spurious: **%d**"
      % (ob["planted"], ob["detected"], ob["missed"], ob["spurious"]))
    A("- Named rules: OBS_DUST_SPAM, OBS_SELF_TRANSFER, "
      "OBS_HIGH_FREQ_SAME_COUNTERPARTY. Observations are structural flags for a "
      "human — never attributions; an address is not an identity.")
    A("")
    A("## 7. Committed sample fixtures")
    sp, sr = sample["provenance"], sample["reconciliation"]
    A("`fixtures/sample/` (%d sets, %d facts) round-trips from disk against its "
      "committed truth: provenance %.1f%%, %d/%d sets exact, deterministic: %s. "
      "The rendered sample annex is committed at `evidence/annex-sample.md`."
      % (sample["sets"], sample["facts"], 100 * sp["complete_rate"],
         sr["exact_sets"], sr["sets"], sample["determinism"]["identical"]))
    A("")
    A("## 8. Live-mode degradation")
    A("The optional live collectors (user-supplied explorer base URL; no default "
      "endpoint) degrade to None offline without raising: **%s**. CI never touches "
      "the network." % degrade["all_none"])
    A("")
    A("## 9. Limitations")
    A("- Synthetic fixtures model the SHAPE of explorer payloads and their failure "
      "modes (pagination overlap, decimal traps, spam, case variance), not the full "
      "messiness of live explorer data. Validate live captures against the target "
      "explorer's current schema before reliance.")
    A("- Token metadata (symbol, name, decimals) is recorded as claimed by the "
      "source; a token contract can claim any symbol. Nothing here verifies a "
      "token's legitimacy.")
    A("- The Blockscout-style module API carries no per-transfer log index, so "
      "token-transfer identity is the full record; EIP-55 checksum validation is "
      "out of scope (identity is case-folded hex).")
    A("- Observations are structural, not attributions. Address does not equal "
      "identity; counterparty exposure and entity attribution remain the job of a "
      "chain-analytics vendor and a human investigator. This engine complements — "
      "never replaces — those.")
    A("")
    A("## 10. Reproduction")
    A("```bash")
    A("python3 run_validation.py --seed %d --addresses %d --transactions %d"
      % (manifest["seed"], manifest["addresses"], manifest["transactions_requested"]))
    A("```")
    A("")
    return "\n".join(L)


def write_evidence(out_dir, res, sample, degrade, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    metrics = {"provenance": res["provenance"],
               "reconciliation": {k: v for k, v in res["reconciliation"].items()
                                  if k != "per_set_rows"},
               "determinism": res["determinism"],
               "observations": res["observations"],
               "sample": {k: v for k, v in sample.items() if k != "packs"},
               "live_degrade": degrade,
               "manifest": manifest}
    metrics["sample"]["reconciliation"] = {
        k: v for k, v in metrics["sample"]["reconciliation"].items()
        if k != "per_set_rows"}
    json.dump(metrics, open(os.path.join(out_dir, "metrics.json"), "w"), indent=2)
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    rows = res["reconciliation"]["per_set_rows"]
    with open(os.path.join(out_dir, "reconciliation.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)
    for p in sample["packs"]:
        if p.set_id == "evm-sample-01":
            open(os.path.join(out_dir, "annex-sample.md"), "w").write(p.annex_md)
            break


# --------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--addresses", type=int, default=400)
    ap.add_argument("--transactions", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = E.Config()
    data_dir = os.path.join(HERE, "data", "fixtures")

    sample = check_sample(config)
    if not sample.get("present"):
        print("GATE FAILED: committed fixtures/sample/ missing — run "
              "generate_synthetic_data.py --write-sample")
        return 1

    res = run_once(args.addresses, args.transactions, args.seed, config,
                   use_disk=True, data_dir=data_dir)
    pr, rc, ob, dt = (res["provenance"], res["reconciliation"],
                      res["observations"], res["determinism"])
    print("\n=== on-chain OSINT evidence (seed %d, %d addresses, ~%d transactions) ==="
          % (args.seed, args.addresses, args.transactions))
    print("facts %s  provenance %.4f  recon exact_sets %d/%d  dropped %d  dup %d  "
          "dedup %s/%s" % (format(res["facts_emitted"], ","), pr["complete_rate"],
                           rc["exact_sets"], rc["sets"], rc["dropped_records"],
                           rc["duplicated_records"],
                           format(rc["duplicates_removed"], ","),
                           format(rc["duplicates_planted"], ",")))
    print("deterministic %s (digest %s)  obs planted %d detected %d (missed %d, "
          "spurious %d)  btc_ties %s"
          % (dt["identical"], dt["digest"][:16], ob["planted"], ob["detected"],
             ob["missed"], ob["spurious"], rc["btc_summary_ties"]))
    degrade = check_live_degrade()
    print("sample sets %d exact %d/%d deterministic %s  live offline degrade %s"
          % (sample["sets"], sample["reconciliation"]["exact_sets"],
             sample["reconciliation"]["sets"], sample["determinism"]["identical"],
             degrade["all_none"]))

    fails = gate_failures("main", res) + gate_failures("sample", sample)
    if not degrade["all_none"]:
        fails.append("live collectors did not degrade gracefully offline")

    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            r = run_once(args.addresses, args.transactions, s, config)
            print("  trial seed %d: facts %s prov %.4f dropped %d dup %d "
                  "deterministic %s obs_ok %s"
                  % (s, format(r["facts_emitted"], ","),
                     r["provenance"]["complete_rate"],
                     r["reconciliation"]["dropped_records"],
                     r["reconciliation"]["duplicated_records"],
                     r["determinism"]["identical"], r["observations"]["ok"]))
            fails += gate_failures("trial seed %d" % s, r)

    if fails:
        print("\nGATE FAILED:")
        for f in fails:
            print("  ", f)
        for ex in (rc["mismatch_examples"] or [])[:5]:
            print("   mismatch:", ex)
        for ex in pr["incomplete_examples"][:5]:
            print("   incomplete fact:", ex)
        return 1

    manifest = {"framework": "onchain-osint-evidence", "seed": args.seed,
                "addresses": args.addresses,
                "transactions_requested": args.transactions,
                "transaction_records": res["unique_records"],
                "source_records_incl_duplicates": res["records_seen"],
                "facts_emitted": res["facts_emitted"],
                "evm_sets": res["evm_sets"], "btc_sets": res["btc_sets"],
                "provenance_floor": PROVENANCE_FLOOR,
                "reconciliation_tolerance": RECONCILIATION_TOLERANCE,
                "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                                 .strftime("%Y-%m-%d %H:%M UTC")}

    manifest = attest.enrich_manifest(manifest, _T0)
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, res, sample, degrade, manifest,
                       render_report(res, sample, degrade, manifest))
        print("\nevidence written -> %s/  (all gates PASSED)" % args.out)
    else:
        print("\nall gates PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
