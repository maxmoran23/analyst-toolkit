"""
Validation harness for the watchlist knowledge base.

Runs the full pipeline over a seeded synthetic multi-list population with known ground
truth and checks the properties that make a self-maintaining watchlist defensible:

  * ZERO FALSE MERGE (the build gate) — no resolved entity may combine two distinct
    true entities. A false merge erases a designation; the harness exits non-zero if
    any occurs.
  * Merge recall — cross-list duplicates of the same true entity are unified.
  * Delta correctness — planted additions / removals / amendments are detected.
  * Feedback safety — the false-positive learning loop genericizes common tokens but
    NEVER a token that is distinctive for a real designated entity.
  * Ingest degradation — sources ingest offline-safely (return None, not raise).
  * Parser correctness — every shipped list parser (OFAC SDN, UN consolidated, UK OFSI)
    is exercised against a synthetic document reproducing its published schema, including
    the quirks the live files exhibit. A parser regression fails the build.

Usage:
    python3 run_validation.py
    python3 run_validation.py --entities 10000
    python3 run_validation.py --trials 5
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # frameworks/ on path

from _lib import metrics  # noqa: E402
from _lib.knowledge_base import dedup, delta, feedback, ingest, sources  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

_ID_FIELDS = ("dob", "nationality", "country", "place_of_birth", "passport",
              "national_id", "registration", "imo", "tail_number", "wallet")
MERGE_RECALL_FLOOR = 0.95   # over identifier-linked duplicates (the auto-mergeable set)


def to_records(rows):
    recs, true_id = [], {}
    for r in rows:
        ids = {f: r["id_" + f] for f in _ID_FIELDS if r.get("id_" + f)}
        rec = sources.normalize_record(r["uid"], r["name"], r["entity_type"],
                                       r["program"], [], ids, r["source"])
        recs.append(rec)
        true_id[r["uid"]] = int(r["true_entity_id"])
    return recs, true_id


_STRONG_COLS = ("passport", "national_id", "registration", "imo", "tail_number", "wallet")


def score_dedup(entities, true_id, rows, review_candidates):
    from collections import Counter, defaultdict
    recs_by_tid = defaultdict(list)
    for r in rows:
        recs_by_tid[int(r["true_entity_id"])].append(r)
    multi, id_linked = set(), set()
    for tid, rs in recs_by_tid.items():
        if len(rs) > 1:
            multi.add(tid)
        vc = Counter()
        for r in rs:
            for f in _STRONG_COLS:
                if r.get("id_" + f):
                    vc[(f, r["id_" + f])] += 1
        if any(c >= 2 for c in vc.values()):  # a shared unique id -> auto-mergeable
            id_linked.add(tid)
    tid_clusters = defaultdict(set)
    false_merges = []
    for ci, e in enumerate(entities):
        tids = {true_id[u] for u in e["member_uids"]}
        for t in tids:
            tid_clusters[t].add(ci)
        if len(tids) > 1:
            false_merges.append({"cluster": e["name"], "true_ids": sorted(tids)})
    unified = sum(1 for t in id_linked if len(tid_clusters[t]) == 1)
    false_merge_count = sum(len(fm["true_ids"]) - 1 for fm in false_merges)
    return {
        "records": len(rows), "resolved_entities": len(entities),
        "dedup_reduction": round(1 - len(entities) / len(rows), 4),
        "multi_list_entities": len(multi), "id_linked_entities": len(id_linked),
        "auto_merge_recall": round(unified / len(id_linked), 4) if id_linked else 1.0,
        "false_merge_count": false_merge_count, "false_merge_examples": false_merges[:5],
        "review_candidates": len(review_candidates),
    }


def check_delta(entities, rng):
    # Delta is reliable for entities that carry a stable identifier (a unique key).
    # Name-only entities have no stable cross-snapshot key, so plant changes on the
    # id-keyed set — the tractable, common case (limitation noted in the report).
    def keyed(e):
        return any(e["ids"].get(f) for f in _STRONG_COLS)
    prev = entities
    id_keyed = [e for e in entities if keyed(e)]
    to_remove = set(delta.identity_key(e) for e in rng.sample(id_keyed, min(20, len(id_keyed))))
    cur = [dict(e) for e in entities if delta.identity_key(e) not in to_remove]
    remaining = [i for i, e in enumerate(cur) if keyed(e) and delta.identity_key(e) not in to_remove]
    amend_idx = rng.sample(remaining, min(15, len(remaining)))
    for i in amend_idx:
        cur[i] = dict(cur[i], program=cur[i]["program"] + "; ADDED-PROG")
    added = [sources.normalize_record("OFAC_SDN-NEW-%d" % i, "NEWENTITY%d HOLDINGS" % i,
             "ENTITY", "SDGT", [], {"registration": "REGNEW%05d" % i, "country": "IR"}, "OFAC_SDN")
             for i in range(25)]
    cur = cur + added
    s = delta.summary(delta.diff(prev, cur))
    planted = {"added": 25, "removed": len(to_remove), "amended": len(amend_idx)}
    ok = (s["added"] == planted["added"] and s["removed"] == planted["removed"]
          and s["amended"] == planted["amended"])
    return {"planted": planted, "detected": s, "ok": ok}


def check_feedback(entities, rng):
    # planted FP tokens: common business tokens (should be learned) + one DISTINCTIVE
    # token taken from a real resolved entity (must be blocked).
    import random
    from _lib.text_normalize import tokens, TokenStats
    names = [e["name"] for e in entities]
    stats = TokenStats.from_names(names)
    distinctive = None
    for e in entities:
        for t in tokens(e["name"]):
            if not stats.is_generic(t, 0.005):
                distinctive = t
                break
        if distinctive:
            break
    fp_counts = {"CAPITAL": 200, "TRADING": 180, "HOLDINGS": 150, "GLOBAL": 120}
    if distinctive:
        fp_counts[distinctive] = 140  # an on-list distinctive token also driving FPs
    res = feedback.learn_generic(fp_counts, entities, min_count=50)
    learned = {x["token"] for x in res["learned"]}
    blocked = {x["token"] for x in res["blocked"]}
    ok = "CAPITAL" in learned and (distinctive is None or distinctive in blocked)
    return {"distinctive_token": distinctive, "learned": sorted(learned),
            "blocked": sorted(blocked), "protected_ok": ok}


def check_ingest():
    offline = {k: ingest.ingest_source(k, offline=True) for k in sources.SOURCES}
    return {"offline_all_none": all(v is None for v in offline.values()),
            "configured_sources": sources.configured_sources()}


# --- parser self-test -----------------------------------------------------------
# Synthetic documents that reproduce the SHAPE of each published schema, including
# the specific quirks the live files exhibit. No real list data is embedded — the
# knowledge base redistributes nothing — so these fixtures are authored to exercise
# the parser, not to stand in for the list.
#
# Each fixture deliberately plants the trap that a naive parser falls into:
#   OFAC — "-0-" is the blank marker, not a value; identifiers hide in `remarks`.
#   UN   — an empty <ALIAS_NAME>; a DOB expressed as YEAR and as FROM/TO range;
#          a TYPE_OF_DOCUMENT carrying an embedded newline and a French variant.
#   UK   — rows are NAME VARIANTS, not targets; a group with two "Primary name"
#          rows and a group with none; identifiers carried on a non-primary row.

_FIX_OFAC = (
    '36,"AEROTEST LIMITED",-0- ,"DEMO-PROG",-0- ,-0- ,-0- ,-0- ,-0- ,-0- ,-0- ,-0- \n'
    '37,"RIVERA, Juan Carlos","individual","DEMO-PROG",-0- ,-0- ,-0- ,-0- ,-0- ,-0- ,-0- ,'
    '"DOB 12 Mar 1970; POB Springfield; nationality Freedonia; Passport X1234567"\n'
)

_FIX_UN = """<?xml version="1.0" encoding="UTF-8"?>
<CONSOLIDATED_LIST>
  <INDIVIDUALS>
    <INDIVIDUAL>
      <DATAID>1001</DATAID>
      <FIRST_NAME>JUAN</FIRST_NAME><SECOND_NAME>CARLOS</SECOND_NAME><THIRD_NAME>RIVERA</THIRD_NAME>
      <UN_LIST_TYPE>DEMO</UN_LIST_TYPE>
      <NATIONALITY><VALUE>Freedonia</VALUE></NATIONALITY>
      <INDIVIDUAL_ALIAS><QUALITY>Good</QUALITY><ALIAS_NAME>J C RIVERA</ALIAS_NAME></INDIVIDUAL_ALIAS>
      <INDIVIDUAL_ALIAS><QUALITY/><ALIAS_NAME/></INDIVIDUAL_ALIAS>
      <INDIVIDUAL_DATE_OF_BIRTH><TYPE_OF_DATE>EXACT</TYPE_OF_DATE><YEAR>1970</YEAR></INDIVIDUAL_DATE_OF_BIRTH>
      <INDIVIDUAL_PLACE_OF_BIRTH><CITY>Springfield</CITY><COUNTRY>Freedonia</COUNTRY></INDIVIDUAL_PLACE_OF_BIRTH>
      <INDIVIDUAL_DOCUMENT>
        <TYPE_OF_DOCUMENT>Numero de passeport</TYPE_OF_DOCUMENT><NUMBER>X1234567</NUMBER>
      </INDIVIDUAL_DOCUMENT>
      <INDIVIDUAL_DOCUMENT>
        <TYPE_OF_DOCUMENT>National Identification
                          Number</TYPE_OF_DOCUMENT><NUMBER>NID-99</NUMBER>
      </INDIVIDUAL_DOCUMENT>
      <INDIVIDUAL_ADDRESS><COUNTRY>Freedonia</COUNTRY></INDIVIDUAL_ADDRESS>
    </INDIVIDUAL>
    <INDIVIDUAL>
      <DATAID>1002</DATAID>
      <FIRST_NAME>ANA</FIRST_NAME><SECOND_NAME>MORENO</SECOND_NAME>
      <UN_LIST_TYPE>DEMO</UN_LIST_TYPE>
      <INDIVIDUAL_DATE_OF_BIRTH><TYPE_OF_DATE>BETWEEN</TYPE_OF_DATE><FROM_YEAR>1980</FROM_YEAR><TO_YEAR>1982</TO_YEAR></INDIVIDUAL_DATE_OF_BIRTH>
    </INDIVIDUAL>
  </INDIVIDUALS>
  <ENTITIES>
    <ENTITY>
      <DATAID>2001</DATAID>
      <FIRST_NAME>AEROTEST LIMITED</FIRST_NAME>
      <UN_LIST_TYPE>DEMO</UN_LIST_TYPE>
      <ENTITY_ALIAS><QUALITY>Good</QUALITY><ALIAS_NAME>AEROTEST LTD</ALIAS_NAME></ENTITY_ALIAS>
      <ENTITY_ADDRESS><COUNTRY>Freedonia</COUNTRY></ENTITY_ADDRESS>
    </ENTITY>
  </ENTITIES>
</CONSOLIDATED_LIST>
"""

_UK_HEADER = ("Name 6,Name 1,Name 2,Name 3,Name 4,Name 5,Title,Name Non-Latin Script,"
              "Non-Latin Script Type,Non-Latin Script Language,DOB,Town of Birth,"
              "Country of Birth,Nationality,Passport Number,Passport Details,"
              "National Identification Number,National Identification Details,Position,"
              "Address 1,Address 2,Address 3,Address 4,Address 5,Address 6,Post/Zip Code,"
              "Country,Other Information,Group Type,Alias Type,Alias Quality,Regime,"
              "Listed On,UK Sanctions List Date Designated,Last Updated,Group ID")


def _uk_row(family, given, dob="", nat="", passport="", gtype="Individual",
            alias="Primary name", regime="DEMO", gid="7001"):
    cells = [""] * 36
    cells[0], cells[1] = family, given
    cells[10], cells[13], cells[14] = dob, nat, passport
    cells[26] = nat
    cells[28], cells[29], cells[31], cells[35] = gtype, alias, regime, gid
    return ",".join(f'"{c}"' for c in cells)


_FIX_UK = "\n".join([
    '"Last Updated","03/06/2026"',
    _UK_HEADER,
    # Group 7001: primary row carries no identifiers; a variant row does.
    _uk_row("RIVERA", "Juan", gid="7001"),
    _uk_row("RIVERA", "Juan Carlos", dob="12/03/1970", nat="Freedonia",
            passport="X1234567", alias="AKA", gid="7001"),
    # Group 7002: TWO primary rows — the live file has 297 such groups (one has 80).
    _uk_row("MORENO", "Ana", dob="01/01/1980", gid="7002"),
    _uk_row("MORENO", "Anna", alias="Primary name", gid="7002"),
    # Group 7003: NO primary row at all — the live file has two such groups.
    _uk_row("AEROTEST LIMITED", "", gtype="Entity", alias="AKA", gid="7003"),
    # Group 7004: a ship, which normalizes to VESSEL.
    _uk_row("SEA SPRITE", "", gtype="Ship", gid="7004"),
]) + "\n"


def check_parsers():
    """Exercise every shipped parser against a synthetic document reproducing its
    published schema. Returns per-parser pass/fail plus the reasons."""
    results = {}

    # --- OFAC: blank marker handling + identifiers mined from remarks
    recs = {r["uid"]: r for r in sources.parse_ofac_sdn(_FIX_OFAC)}
    juan = recs.get("OFAC-37", {})
    results["OFAC_SDN"] = {
        "records": len(recs),
        "checks": {
            "both records parsed": len(recs) == 2,
            "'-0-' treated as blank, not a value": recs.get("OFAC-36", {}).get("program") == "DEMO-PROG"
            and not recs.get("OFAC-36", {}).get("ids"),
            "entity type from sdn_type": juan.get("entity_type") == "INDIVIDUAL",
            "dob mined from remarks": juan.get("ids", {}).get("dob", "").startswith("12 MAR"),
            "passport mined from remarks": juan.get("ids", {}).get("passport") == "X1234567",
        },
    }

    # --- UN: name assembly, empty aliases, DOB shapes, messy document types
    un = {r["uid"]: r for r in sources.parse_un_consolidated(_FIX_UN, None)}
    juan, ana, ent = un.get("UN-1001", {}), un.get("UN-1002", {}), un.get("UN-2001", {})
    dtd_refused = False
    try:
        sources.parse_un_consolidated('<!DOCTYPE r [<!ENTITY a "AA">]><r>&a;</r>', None)
    except ValueError:
        dtd_refused = True
    results["UN_CONSOLIDATED"] = {
        "records": len(un),
        "checks": {
            "individuals and entities both parsed": len(un) == 3 and ent.get("entity_type") == "ENTITY",
            "split name parts assembled": juan.get("name") == "JUAN CARLOS RIVERA",
            "empty <ALIAS_NAME> dropped": juan.get("aliases") == ["J C RIVERA"],
            "DOB from bare YEAR": juan.get("ids", {}).get("dob") == "1970",
            "DOB from FROM/TO range": ana.get("ids", {}).get("dob") == "1980-1982",
            "passport matched across language variant": juan.get("ids", {}).get("passport") == "X1234567",
            "national id matched across embedded newline": juan.get("ids", {}).get("national_id") == "NID-99",
            "place of birth joined": juan.get("ids", {}).get("place_of_birth") == "SPRINGFIELD, FREEDONIA",
            "DTD/entity declaration refused": dtd_refused,
        },
    }

    # --- UK: the grouping contract, which is the whole game for this list
    uk = {r["uid"]: r for r in sources.parse_uk_ofsi(_FIX_UK, None)}
    juan, ana, aero, ship = uk.get("UK-7001", {}), uk.get("UK-7002", {}), uk.get("UK-7003", {}), uk.get("UK-7004", {})
    results["UK_OFSI"] = {
        "records": len(uk),
        "checks": {
            "one record per Group ID, not per name row": len(uk) == 4,
            "canonical name from the primary row": juan.get("name") == "Juan RIVERA",
            "other variants become aliases": juan.get("aliases") == ["Juan Carlos RIVERA"],
            "identifiers recovered from a non-primary row": juan.get("ids", {}).get("passport") == "X1234567",
            "two primary rows: first in file order wins": ana.get("name") == "Ana MORENO",
            "zero primary rows: falls back to first row": aero.get("name") == "AEROTEST LIMITED",
            "ship normalizes to VESSEL": ship.get("entity_type") == "VESSEL",
        },
    }

    for res in results.values():
        res["ok"] = all(res["checks"].values())
    return {"parsers": results, "ok": all(r["ok"] for r in results.values())}


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def render_report(dd, dl, fb, ing, pk, manifest):
    L = []; A = L.append
    A("# Validation Report — Watchlist Knowledge Base")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the pipeline over a "
      "seeded synthetic multi-list population with known ground truth. No real list data "
      "is represented. Numbers are emitted by `run_validation.py`, not authored.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['entities']:,} true entities · "
      f"{dd['records']:,} list records · git `{manifest['git_sha']}` · {manifest['generated_utc']}")
    A("")
    A(f"**Headline:** **{dd['false_merge_count']} false merges** (distinct parties wrongly "
      f"combined — must be 0, and is structurally guaranteed), auto-merge recall "
      f"**{dd['auto_merge_recall']:.4f}** on identifier-linked duplicates, dedup reduction "
      f"**{dd['dedup_reduction']:.1%}** ({dd['records']:,} records → {dd['resolved_entities']:,} "
      f"entities); **{dd['review_candidates']}** name-only pairs surfaced for analyst review.")
    A("")
    A("## 1. What this validates")
    A("The knowledge base ingests public consolidated lists, normalizes them to one "
      "schema, resolves the same party across lists, tracks changes between refreshes, "
      "and learns from false-positive outcomes. The safety-critical property is that "
      "entity resolution NEVER combines two distinct designated parties — a false merge "
      "would erase a designation from screening. Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Synthetic-population construction")
    A(f"{manifest['entities']:,} true entities, each appearing on 1-3 lists with name "
      "variance and a shared strong identifier; plus confusable distractors — pairs that "
      "share a distinctive surname token but carry DIFFERENT strong identifiers, which "
      "must not merge. Strong identifiers are unique per true entity, so no two distinct "
      "entities share one by accident.")
    A("")
    A("## 3. Entity resolution (dedup)")
    A(f"- **False merges (distinct parties combined): {dd['false_merge_count']}** — must be 0. "
      "Auto-merge fires only on a shared unique identifier, which is unique per party, so a "
      "false merge is structurally impossible.")
    A(f"- Auto-merge recall: {dd['auto_merge_recall']:.4f} of {dd['id_linked_entities']:,} "
      f"identifier-linked duplicates unified (of {dd['multi_list_entities']:,} multi-list "
      "entities total).")
    A(f"- Name-only duplicates (no shared identifier): surfaced as {dd['review_candidates']} "
      "analyst review candidates rather than auto-merged — a retained duplicate is harmless; "
      "an erased designation is not.")
    A(f"- Records {dd['records']:,} → resolved entities {dd['resolved_entities']:,} "
      f"({dd['dedup_reduction']:.1%} reduction)")
    if dd["false_merge_examples"]:
        A(f"- Example false merges (should be none): {dd['false_merge_examples']}")
    A("")
    A("## 4. Change detection (delta)")
    A(f"Planted {dl['planted']} → detected {dl['detected']}. Match: "
      f"**{'PASS' if dl['ok'] else 'FAIL'}**. This is the ongoing-monitoring evidence: "
      "added / removed (delisted) / amended designations are tracked between refreshes.")
    A("")
    A("## 5. False-positive feedback safety")
    A(f"Common tokens learned as generic: {fb['learned']}. Distinctive on-list token "
      f"`{fb['distinctive_token']}` correctly **{'BLOCKED' if fb['protected_ok'] else 'NOT blocked'}** "
      "from genericization. The loop can only clear more false positives, never make a "
      "true match clearable — gate **{}**.".format("PASS" if fb["protected_ok"] else "FAIL"))
    A("")
    A("## 6. Ingest degradation and parser self-test")
    A(f"All sources return None offline (graceful degrade, no exceptions): "
      f"**{ing['offline_all_none']}**. Sources shipping a live parser today: "
      f"{ing['configured_sources']} (others are registered with URL + licence + the "
      "normalized target; supply a parser to ingest them live).")
    A("")
    A("Each shipped parser is exercised against a synthetic document that reproduces its "
      "published schema — including the specific quirks the live files exhibit. The "
      "fixtures embed no real list data; the knowledge base redistributes nothing. Every "
      "check below is a build gate: a parser regression fails the run.")
    A("")
    A("| Parser | Records parsed | Checks | Result |")
    A("|---|---|---|---|")
    for name, res in pk["parsers"].items():
        passed = sum(1 for v in res["checks"].values() if v)
        A(f"| `{name}` | {res['records']} | {passed}/{len(res['checks'])} | "
          f"**{'PASS' if res['ok'] else 'FAIL'}** |")
    A("")
    for name, res in pk["parsers"].items():
        A(f"**{name}** — " + "; ".join(
            f"{chk} ({'ok' if ok else 'FAILED'})" for chk, ok in res["checks"].items()))
    A("")
    A("## 7. Limitations")
    A("- Three parsers are implemented and each was written against the live published "
      "document, not a guessed schema: OFAC SDN CSV, the UN consolidated XML, and the UK "
      "OFSI ConList CSV. The EU consolidated list is registered **without** a parser by "
      "design — its endpoint answers 403 unauthenticated, so no document is available to "
      "verify one against. Live fetch hits real endpoints; re-verify each parser against "
      "the current schema before reliance, since publishers change layouts without notice.")
    A("- The UK list publishes one row per *name variant*: the parser resolves rows to "
      "designated targets by `Group ID`. Parsing it row-per-target would inflate the "
      "watchlist roughly fourfold with duplicate parties — the self-test gates that.")
    A("- XML ingestion refuses any document declaring a DTD. `xml.etree.ElementTree` does "
      "not resolve external entities, but it does expand internal ones (the billion-laughs "
      "vector); refusing DTDs removes that exposure without a third-party dependency.")
    A("- Synthetic name variance and identifier structure model the shape of real "
      "cross-list variation, not its full messiness. Calibrate the dedup thresholds "
      "against a labelled sample before reliance (`tuning.md`).")
    A("- The KB assembles and resolves; designation and de-listing decisions are made by "
      "the issuing authorities, and screening decisions remain human.")
    A("")
    A("## 8. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} --entities {manifest['entities']}")
    A("```")
    A("")
    return "\n".join(L)


def write_evidence(out_dir, dd, dl, fb, ing, pk, entities, manifest, report):
    os.makedirs(out_dir, exist_ok=True)
    json.dump({"dedup": dd, "delta": dl, "feedback": fb, "ingest": ing, "parsers": pk,
               "manifest": manifest},
              open(os.path.join(out_dir, "metrics.json"), "w"), indent=2, default=str)
    with open(os.path.join(out_dir, "resolved-sample.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["uid", "name", "entity_type", "program", "sources", "merged_from"])
        for e in entities[:200]:
            w.writerow([e["uid"], e["name"], e["entity_type"], e["program"],
                        "|".join(e["sources"]), e["merged_from"]])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


def run_once(n_entities, seed):
    import random
    rng = random.Random(seed)
    rows = G.make_population(n_entities, rng)
    recs, true_id = to_records(rows)
    entities, _, review = dedup.resolve(recs)
    dd = score_dedup(entities, true_id, rows, review)
    dl = check_delta(entities, random.Random(seed + 1))
    fb = check_feedback(entities, random.Random(seed + 2))
    return entities, dd, dl, fb


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entities", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    entities, dd, dl, fb = run_once(args.entities, args.seed)
    ing = check_ingest()
    pk = check_parsers()
    print(f"\n=== watchlist KB (seed {args.seed}, {args.entities:,} entities) ===")
    print(f"false_merges {dd['false_merge_count']}  auto_merge_recall {dd['auto_merge_recall']:.4f}  "
          f"reduction {dd['dedup_reduction']:.4f}  review_candidates {dd['review_candidates']}")
    print(f"delta ok {dl['ok']} {dl['detected']}  feedback protected_ok {fb['protected_ok']}  "
          f"ingest offline_none {ing['offline_all_none']}")
    print("parser self-test: " + "  ".join(
        f"{k} {'PASS' if v['ok'] else 'FAIL'}" for k, v in pk["parsers"].items()))

    if args.trials:
        for t in range(args.trials):
            s = args.seed + 10 + t
            _, d2, l2, f2 = run_once(args.entities, s)
            print(f"  trial seed {s}: false_merges {d2['false_merge_count']} "
                  f"auto_merge_recall {d2['auto_merge_recall']:.4f} delta_ok {l2['ok']} fb_ok {f2['protected_ok']}")

    # ---- build gates ----
    fails = []
    if dd["false_merge_count"] > 0:
        fails.append(f"{dd['false_merge_count']} FALSE MERGES (distinct parties combined)")
    if dd["auto_merge_recall"] < MERGE_RECALL_FLOOR:
        fails.append(f"auto-merge recall {dd['auto_merge_recall']:.4f} < {MERGE_RECALL_FLOOR}")
    if not dl["ok"]:
        fails.append("delta detection mismatch")
    if not fb["protected_ok"]:
        fails.append("feedback genericized a distinctive on-list token")
    if not ing["offline_all_none"]:
        fails.append("ingest did not degrade gracefully offline")
    if not pk["ok"]:
        for name, res in pk["parsers"].items():
            for check, passed in res["checks"].items():
                if not passed:
                    fails.append(f"parser {name}: {check}")
    if fails:
        print("\nGATE FAILED:")
        for f in fails:
            print("  ", f)
        if dd["false_merge_examples"]:
            print("   false-merge examples:", dd["false_merge_examples"])
        return 1

    manifest = {"framework": "watchlist-knowledge-base", "seed": args.seed,
                "entities": args.entities, "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
    if not args.no_write and args.trials == 0:
        write_evidence(args.out, dd, dl, fb, ing, pk, entities, manifest,
                       render_report(dd, dl, fb, ing, pk, manifest))
        print(f"\nevidence written -> {args.out}/  (all gates PASSED)")
    else:
        print("\nall gates PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
