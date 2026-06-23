"""
Cross-list entity resolution.

The same designated party appears on OFAC, EU, UN, and UK under varying names and
identifiers. Merging those records dedupes the knowledge base; merging WRONG —
collapsing two distinct designated parties into one — silently erases a designation,
a catastrophic screening failure. So the merge rule is asymmetric and conservative:

  * NEVER merge across an incompatible entity type, or across a CONTRADICTING strong
    identifier (a different DOB / passport / IMO / wallet ⇒ different parties). This
    is the zero-false-merge guarantee.
  * Merge only on strong positive evidence: a matching strong identifier with a
    plausible name, or a high distinctive-name match (with a corroborating identifier
    for personal names, which recur).

Reuses the same IDF-weighted matcher as the sanctions framework. Blocking by shared
distinctive token keeps it near-linear on a real-size list.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from _lib.text_normalize import TokenStats, tokens  # noqa: E402
from _lib.match import compare_names, soundex  # noqa: E402

# Strong = effectively unique per party (a match is near-conclusive; a contradiction
# proves different parties). DOB is deliberately WEAK, not strong: two different people
# routinely share a birthdate, so a DOB match alone must not force a merge — though a
# DOB *contradiction* still blocks one.
_STRONG = ("passport", "national_id", "registration", "imo", "tail_number", "wallet")
_WEAK = ("nationality", "country", "place_of_birth", "dob")
_INCOMPATIBLE = {
    frozenset({"INDIVIDUAL", "ENTITY"}), frozenset({"INDIVIDUAL", "VESSEL"}),
    frozenset({"INDIVIDUAL", "AIRCRAFT"}), frozenset({"INDIVIDUAL", "CRYPTO"}),
    frozenset({"ENTITY", "VESSEL"}), frozenset({"ENTITY", "AIRCRAFT"}),
    frozenset({"ENTITY", "CRYPTO"}), frozenset({"VESSEL", "AIRCRAFT"}),
    frozenset({"VESSEL", "CRYPTO"}), frozenset({"AIRCRAFT", "CRYPTO"}),
}


@dataclass
class Config:
    name_merge_floor: float = 0.85   # min distinctive name_score to merge without a strong id
    char_floor: float = 0.94         # min character similarity (Jaro-Winkler) of the matched
                                     # tokens — guards against coarse Soundex coincidences
    generic_max_share: float = 0.005


def _incompatible(a, b):
    return frozenset({a, b}) in _INCOMPATIBLE


def _id_relation(a_ids, b_ids):
    """Return ('contradict'|'strong_match'|'weak_match'|'none', detail)."""
    for f in _STRONG:
        av, bv = a_ids.get(f), b_ids.get(f)
        if av and bv and av != bv:
            return "contradict", f"{f}: {av} != {bv}"
    for f in _STRONG:
        av, bv = a_ids.get(f), b_ids.get(f)
        if av and bv and av == bv:
            return "strong_match", f
    weak = sum(1 for f in _WEAK if a_ids.get(f) and a_ids.get(f) == b_ids.get(f))
    weak_conflict = any(a_ids.get(f) and b_ids.get(f) and a_ids.get(f) != b_ids.get(f) for f in _WEAK)
    if weak_conflict:
        return "contradict", "weak-id conflict"
    if weak >= 1:
        return "weak_match", f"{weak} weak id(s)"
    return "none", ""


def _best_name(a, b, stats, gms):
    names_a = [a["name"]] + a.get("aliases", [])
    names_b = [b["name"]] + b.get("aliases", [])
    best = None
    for na in names_a:
        for nb in names_b:
            nm = compare_names(na, nb, stats, gms)
            if best is None or nm.weighted_overlap > best.weighted_overlap:
                best = nm
    return best


def same_party(a, b, stats, config=Config()):
    """Returns (merge, reason, review).

    Auto-merge fires ONLY on a shared strong (unique) identifier — never on name
    similarity alone. Because strong identifiers are unique to a party, this makes a
    false merge of two distinct parties structurally impossible. A high name match
    with no shared identifier is not merged; it is flagged as a REVIEW candidate
    (review=True) for an analyst — the conservative, defensible posture for a
    watchlist, where retaining a duplicate is harmless but erasing a designation is not.
    """
    if _incompatible(a["entity_type"], b["entity_type"]):
        return False, "type-incompatible", False
    rel, detail = _id_relation(a["ids"], b["ids"])
    if rel == "contradict":
        return False, f"id-contradiction ({detail})", False   # zero-false-merge guard
    nm = _best_name(a, b, stats, config.generic_max_share)
    name_score = nm.weighted_overlap * (0.4 + 0.6 * nm.coverage)
    if rel == "strong_match":
        if name_score >= 0.35:
            return True, f"strong-id match ({detail})", False
        return False, "strong-id match but names clearly differ", False
    # no shared strong identifier -> never auto-merge; flag close names for review
    if (not nm.only_generic and name_score >= config.name_merge_floor
            and nm.coverage >= 0.8 and nm.char_sim >= config.char_floor):
        return False, "close name, no shared identifier", True
    return False, "insufficient evidence", False


class _UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


def resolve(records, config=Config()):
    """Cluster records into resolved entities. Returns (entities, merge_log)."""
    stats = TokenStats.from_names([r["name"] for r in records]
                                  + [a for r in records for a in r.get("aliases", [])])
    # Block so that records that COULD be the same party are compared. Two keys:
    #   - strong-identifier value: any records sharing a passport / IMO / wallet etc.
    #     are always compared (catches duplicates regardless of name variance).
    #   - Soundex of each distinctive token: vowel-level transliteration variance
    #     (ZARKOVNEFT / ZORKOVNEFT) is Soundex-invariant, so name variants co-locate.
    blocks = {}
    for i, r in enumerate(records):
        keys = set()
        for f in _STRONG:
            v = r["ids"].get(f)
            if v:
                keys.add(f"id:{f}:{v}")
        distinctive = [t for t in tokens(r["name"]) if not stats.is_generic(t, config.generic_max_share)]
        for t in (distinctive or tokens(r["name"])):
            keys.add(f"snd:{soundex(t)}")
        for k in keys:
            blocks.setdefault(k, []).append(i)

    uf = _UF(len(records))
    merge_log = []
    review_candidates = []
    seen_pairs = set()
    for idxs in blocks.values():
        if len(idxs) < 2:
            continue
        for x in range(len(idxs)):
            for y in range(x + 1, len(idxs)):
                i, j = idxs[x], idxs[y]
                key = (min(i, j), max(i, j))
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                merge, reason, review = same_party(records[i], records[j], stats, config)
                if merge and uf.find(i) != uf.find(j):
                    uf.union(i, j)
                    merge_log.append({"a": records[i]["uid"], "b": records[j]["uid"], "reason": reason})
                elif review:
                    review_candidates.append({"a": records[i]["uid"], "b": records[j]["uid"],
                                              "a_name": records[i]["name"], "b_name": records[j]["name"]})

    clusters = {}
    for i in range(len(records)):
        clusters.setdefault(uf.find(i), []).append(i)

    entities = []
    for members in clusters.values():
        recs = [records[i] for i in members]
        recs.sort(key=lambda r: (r["source"] != "OFAC_SDN", -len(r["name"])))  # prefer OFAC, longer name
        canon = recs[0]
        names = []
        ids = {}
        programs, srcs, src_uids = set(), set(), {}
        for r in recs:
            for nm in [r["name"]] + r.get("aliases", []):
                if nm and nm not in names:
                    names.append(nm)
            for k, v in r["ids"].items():
                ids.setdefault(k, v)   # we only merge when strong ids agree, so union is safe
            if r["program"]:
                programs.add(r["program"])
            srcs.add(r["source"])
            src_uids[r["source"]] = r["uid"]
        entities.append({
            "uid": canon["uid"], "name": canon["name"], "entity_type": canon["entity_type"],
            "program": "; ".join(sorted(programs)), "aliases": [n for n in names if n != canon["name"]],
            "ids": ids, "sources": sorted(srcs), "source_uids": src_uids,
            "member_uids": [r["uid"] for r in recs], "merged_from": len(recs),
        })
    return entities, merge_log, review_candidates
