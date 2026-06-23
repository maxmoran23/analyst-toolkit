"""
Synthetic multi-list watchlist generator for knowledge-base validation.

Builds records as they would arrive from several public lists (OFAC / EU / UN / UK),
with KNOWN ground truth (`true_entity_id`) so dedup can be scored:

  - Cross-list duplicates: one true entity appears on 2-3 lists with name variance and
    a shared strong identifier (passport / registration / IMO / wallet) — dedup SHOULD
    unify these.
  - List-only entities: appear on a single list.
  - Confusable distractors: two DIFFERENT true entities that share a distinctive
    surname token but carry DIFFERENT strong identifiers — dedup must NEVER merge them
    (the zero-false-merge test). Strong identifiers are unique per true entity by
    construction, so no two distinct entities ever share one by accident.

Seeded and deterministic.
"""
from __future__ import annotations

import argparse
import csv
import os
import random

GIVEN = ["IVAN", "MOHAMMED", "WEI", "MARIA", "SERGEI", "AHMED", "ANNA", "OMAR", "CHEN", "FATIMA"]
_CONS = "BCDFGHJKLMNPRSTVZ"
_VOW = "AEIOU"
GENERIC = ["TRADING", "HOLDINGS", "GROUP", "CAPITAL", "GLOBAL", "SHIPPING", "STAR", "OCEAN"]
COUNTRIES = ["RU", "IR", "KP", "SY", "VE", "CN", "AE", "BY"]
LISTS = ["OFAC_SDN", "EU_CFSP", "UN_CONSOLIDATED", "UK_OFSI"]
_VOWELS = "AEIOU"


def _distinct(rng, used=None):
    """A distinctive pseudo-word — a diverse consonant/vowel sequence over the full
    alphabet, so two DIFFERENT entities have low character similarity (and usually a
    different Soundex), while a same-entity vowel-variant keeps the consonant skeleton
    and stays similar. With `used`, guarantees uniqueness (real sanctioned entities do
    not share identical distinctive names; a synthetic collision would be an artificial
    false-merge pair)."""
    for _ in range(200):
        n = rng.randint(4, 6)
        w = "".join(rng.choice(_CONS) + rng.choice(_VOW) for _ in range(n))
        if rng.random() < 0.5:
            w += rng.choice(_CONS)
        w = w.upper()
        if used is None or w not in used:
            if used is not None:
                used.add(w)
            return w
    return w


def _vary(name, rng):
    """Light name variance for the same entity across lists: vowel transliteration on
    interior letters (Soundex-preserving), keeping the distinctive token recognisable."""
    chars = list(name)
    pos = [i for i in range(1, len(chars)) if chars[i] in _VOWELS]
    rng.shuffle(pos)
    for i in pos[: rng.randint(0, 1)]:
        chars[i] = rng.choice([v for v in _VOWELS if v != chars[i]])
    return "".join(chars)


def _strong_id(etype, tid):
    if etype == "INDIVIDUAL":
        return {"passport": "P%07d" % tid}
    if etype == "VESSEL":
        return {"imo": "%07d" % (1000000 + tid)}
    if etype == "CRYPTO":
        return {"wallet": "0x%012x" % tid}
    if etype == "AIRCRAFT":
        return {"tail_number": "EP-%05d" % tid}
    return {"registration": "REG%06d" % tid}


def _name(etype, rng, used):
    d = _distinct(rng, used)
    if etype == "INDIVIDUAL":
        return "%s %s" % (rng.choice(GIVEN), d), d
    return "%s %s" % (d, rng.choice(GENERIC)), d


def make_population(n_entities, rng, distractor_rate=0.06, name_only_rate=0.2):
    records = []
    used = set()
    tid = 0
    for _ in range(n_entities):
        tid += 1
        r = rng.random()
        etype = ("INDIVIDUAL" if r < 0.5 else "ENTITY" if r < 0.85 else
                 "VESSEL" if r < 0.93 else "AIRCRAFT" if r < 0.97 else "CRYPTO")
        base, distinct = _name(etype, rng, used)
        country = rng.choice(COUNTRIES)
        sid = _strong_id(etype, tid)
        nlists = rng.choices([1, 2, 3], [0.5, 0.3, 0.2])[0]
        lists = rng.sample(LISTS, nlists)
        share_id = rng.random() > name_only_rate  # some duplicates share only the name
        for k, L in enumerate(lists):
            ids = {"country": country}
            if k == 0 or share_id:
                ids.update(sid)
            if etype == "INDIVIDUAL":
                ids["dob"] = "19%02d-%02d-%02d" % (tid % 70, 1 + tid % 12, 1 + tid % 28)
            records.append({
                "uid": "%s-%06d-%d" % (L, tid, k), "name": _vary(base, rng) if k else base,
                "entity_type": etype, "program": "%s-PROG" % L[:3],
                "aliases": "", "source": L, "true_entity_id": tid,
                **{f"id_{f}": ids.get(f, "") for f in
                   ("dob", "nationality", "country", "place_of_birth", "passport",
                    "national_id", "registration", "imo", "tail_number", "wallet")},
            })
    # confusable distractors: same surname token, DIFFERENT strong id -> must NOT merge
    n_distract = int(n_entities * distractor_rate)
    for _ in range(n_distract):
        shared = _distinct(rng, used)  # unique vs all true entities; reused only by this pair
        for _ in range(2):
            tid += 1
            L = rng.choice(LISTS)
            records.append({
                "uid": "%s-%06d-0" % (L, tid), "name": "%s %s" % (rng.choice(GIVEN), shared),
                "entity_type": "INDIVIDUAL", "program": "%s-PROG" % L[:3], "aliases": "",
                "source": L, "true_entity_id": tid,
                **{f"id_{f}": "" for f in ("dob", "nationality", "country", "place_of_birth",
                                           "passport", "national_id", "registration", "imo",
                                           "tail_number", "wallet")},
                "id_passport": "P%07d" % tid,
                "id_dob": "19%02d-%02d-%02d" % (tid % 70, 1 + tid % 12, 1 + tid % 28),
                "id_country": rng.choice(COUNTRIES),
            })
    rng.shuffle(records)
    return records


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entities", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    rows = make_population(args.entities, rng)
    write_csv(os.path.join(args.out, "list_records.csv"), rows)
    print(f"records: {len(rows)} from {args.entities} true entities (+distractors) "
          f"-> {args.out}/list_records.csv   [seed={args.seed}]")


if __name__ == "__main__":
    main()
