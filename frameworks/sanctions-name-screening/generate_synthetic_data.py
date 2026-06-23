"""
Synthetic data generator for sanctions name-screening validation.

Produces two CSVs with KNOWN ground truth:
  watchlist.csv  — a synthetic SDN-like list (names, entity types, identifiers)
  alerts.csv     — alerts a screening filter would raise, each one a (party x
                   entry) pair that collides on at least one token, labelled
                   with whether it is a true match and, for false positives,
                   WHY it is one.

Everything is invented and seeded. No real person, entity, vessel, or list entry
is represented. Re-running with the same --seed reproduces byte-identical files,
which is what lets an independent reviewer reproduce the validation numbers.

The alert population is built to mirror the real shape of sanctions screening:
the overwhelming majority are false positives, dominated by collisions on common
tokens, with a thin band of genuine matches. Each false positive is one of four
categories so the validation can report a per-category clear rate:

  generic      collision on common token(s) only (CAPITAL, ROAD, TRADING ...)
  type         party type structurally incompatible with the designated entity
  discriminator a distinctive-token overlap cleared by a contradicting hard ID
  weak         genuine partial distinctive overlap, no identifiers either way —
               the irreducible cases that need a human

True matches come in three flavours so the score distribution is realistic:
  corroborated  matching hard identifier + clean name  -> should ESCALATE
  name_only     no identifiers, clean name             -> ANALYST_REVIEW (HIGH)
  noisy         no identifiers, transliteration noise   -> the ones a naive score
                                                           threshold would wrongly
                                                           clear (FN risk)
"""
from __future__ import annotations

import argparse
import csv
import os
import random

GENERIC_TOKENS = [
    "CAPITAL", "TRADING", "ROAD", "GLOBAL", "EXPRESS", "GENERAL", "STAR",
    "PEARL", "OCEAN", "UNITED", "NATIONAL", "PETROLEUM", "SHIPPING", "LOGISTICS",
    "INVESTMENT", "FINANCE", "EASTERN", "WESTERN", "GULF", "PACIFIC", "ORIENT",
    "CONSTRUCTION", "ENERGY", "MARINE", "AVIATION", "METALS", "TEXTILE",
]
_VOWELS = "AEIOU"
GIVEN_NAMES = [
    "IVAN", "MOHAMMED", "ALI", "JOHN", "MARIA", "AHMED", "SERGEI", "WEI",
    "ABDUL", "HASSAN", "DMITRI", "FATIMA", "OMAR", "VLADIMIR", "CHEN", "JOSE",
    "VIKTOR", "RASHID", "YUSUF", "ANNA",
]
COUNTRIES = ["RU", "IR", "KP", "SY", "VE", "CU", "CN", "MM", "BY", "AF"]
CLEAN_COUNTRIES = ["US", "GB", "DE", "CA", "FR", "AE", "SG", "JP", "AU", "NL"]
PROGRAMS = ["RUSSIA-EO14024", "IRAN", "DPRK", "SYRIA", "VENEZUELA", "CUBA",
            "SDNTK", "NPWMD", "GLOMAG"]

_SYL_A = ["zar", "vol", "nor", "kre", "tash", "bur", "lan", "qom", "drav", "sev",
          "mor", "kal", "rus", "ten", "pol", "var", "gor", "shi", "dan", "fer"]
_SYL_B = ["kov", "ova", "ian", "zin", "dar", "neft", "stroy", "export", "tech",
          "oil", "gaz", "bank", "trans", "prom", "invest", "mash", "grad", "sk"]


def _distinct(rng: random.Random) -> str:
    """A pseudo-word that looks like a distinctive surname / brand and is GENUINELY
    rare in the corpus. Three syllables give a ~7,200-token space, so across a few
    thousand entries each distinctive token appears only once or twice — like a
    real sanctions token (ROSOBORONEXPORT, NUCTECH), and well below the genericness
    df-share floor. A 2-syllable space (360) collided badly and produced fake
    'generic' distinctive tokens."""
    return (rng.choice(_SYL_A) + rng.choice(_SYL_B) + rng.choice(_SYL_A)).upper()


def _blank_ids() -> dict:
    return {k: "" for k in ("dob", "nationality", "country", "place_of_birth",
                            "passport", "national_id", "registration", "imo",
                            "tail_number", "wallet")}


def _dob(rng):
    return "%04d-%02d-%02d" % (rng.randint(1948, 1992), rng.randint(1, 12), rng.randint(1, 28))


def make_watchlist(n: int, rng: random.Random) -> list[dict]:
    entries = []
    for i in range(n):
        r = rng.random()
        ids = _blank_ids()
        if r < 0.50:  # INDIVIDUAL
            etype = "INDIVIDUAL"
            surname = _distinct(rng)
            name = "%s %s" % (rng.choice(GIVEN_NAMES), surname)
            ids["dob"] = _dob(rng)
            ids["nationality"] = rng.choice(COUNTRIES)
            ids["country"] = ids["nationality"]
            if rng.random() < 0.4:
                ids["passport"] = "P%07d" % rng.randint(0, 9_999_999)
            aliases = [name.split(" ")[0] + " " + _distinct(rng)] if rng.random() < 0.2 else []
        elif r < 0.85:  # ENTITY
            etype = "ENTITY"
            distinct = _distinct(rng)
            generic = rng.choice(GENERIC_TOKENS)
            name = "%s %s" % (distinct, generic)
            ids["country"] = rng.choice(COUNTRIES)
            if rng.random() < 0.5:
                ids["registration"] = "REG%06d" % rng.randint(0, 999_999)
            aliases = [distinct + " " + rng.choice(GENERIC_TOKENS)] if rng.random() < 0.3 else []
        elif r < 0.93:  # VESSEL
            etype = "VESSEL"
            name = "%s %s" % (_distinct(rng), rng.choice(["STAR", "PEARL", "OCEAN", "PRIDE"]))
            ids["imo"] = "IMO%07d" % rng.randint(1_000_000, 9_999_999)
            ids["country"] = rng.choice(COUNTRIES)
            aliases = []
        elif r < 0.97:  # AIRCRAFT
            etype = "AIRCRAFT"
            name = "%s AVIATION" % _distinct(rng)
            ids["tail_number"] = "EP-%s" % "".join(rng.choice("ABCDEFGHJK") for _ in range(3))
            ids["country"] = rng.choice(COUNTRIES)
            aliases = []
        else:  # CRYPTO
            etype = "CRYPTO"
            name = "%s WALLET" % _distinct(rng)
            ids["wallet"] = "0x" + "".join(rng.choice("0123456789abcdef") for _ in range(12))
            aliases = []
        entries.append({
            "uid": "SDN-%05d" % i,
            "name": name,
            "entity_type": etype,
            "program": rng.choice(PROGRAMS),
            "aliases": "|".join(aliases),
            **ids,
        })
    return entries


def _entry_distinct_tokens(entry: dict) -> list[str]:
    """The entry's genuinely distinctive tokens — excludes both business generics
    (CAPITAL, ROAD) and common given names (IVAN, MOHAMMED), since a match on a
    given name alone is non-discriminating. Keeps the 'weak' and 'discriminator'
    synthetic categories anchored on a truly rare token, so their clear rates
    report cleanly."""
    from _lib.text_normalize import tokens  # local import; path set by caller
    return [t for t in tokens(entry["name"])
            if t not in GENERIC_TOKENS and t not in GIVEN_NAMES]


def _entry_generic_tokens(entry: dict) -> list[str]:
    from _lib.text_normalize import tokens
    return [t for t in tokens(entry["name"]) if t in GENERIC_TOKENS]


def _noise(name: str, rng: random.Random) -> str:
    """Transliteration-style noise: swap 1-3 INTERIOR vowels for other vowels
    (ABDULLAH -> ABDALLAH). This is deliberately Soundex-preserving — vowels are
    uncoded and the first letter is never touched — so the distinctive token
    still phonetically aligns and a true match can never be lost to "no tokens
    matched". It lowers the string-similarity (Jaro-Winkler) score, which is what
    puts these matches in the harder-to-score band, without ever breaking the
    match itself. Models real transliteration variance, where vowels move and
    consonant skeletons hold."""
    chars = list(name)
    positions = [i for i in range(1, len(chars)) if chars[i] in _VOWELS]
    rng.shuffle(positions)
    for i in positions[: rng.randint(1, 3)]:
        chars[i] = rng.choice([v for v in _VOWELS if v != chars[i]])
    return "".join(chars)


def make_alerts(n: int, watchlist: list[dict], rng: random.Random,
                true_rate: float = 0.02) -> list[dict]:
    ent = [e for e in watchlist if e["entity_type"] == "ENTITY"]
    ind = [e for e in watchlist if e["entity_type"] == "INDIVIDUAL"]
    nonbiz = [e for e in watchlist if e["entity_type"] in ("VESSEL", "AIRCRAFT", "CRYPTO")]
    named = [e for e in watchlist if _entry_distinct_tokens(e)]

    alerts = []
    for i in range(n):
        aid = "ALR-%07d" % i
        ids = _blank_ids()
        if rng.random() < true_rate:
            # ---- TRUE MATCH ----
            entry = rng.choice(named)
            flavour = rng.random()
            base_name = entry["name"] if not entry["aliases"] or rng.random() < 0.7 \
                else rng.choice(entry["aliases"].split("|"))
            if flavour < 0.60:  # corroborated
                party_name = base_name
                for f in ("dob", "country", "nationality", "registration", "imo",
                          "tail_number", "wallet"):
                    if entry.get(f):
                        ids[f] = entry[f]  # matching identifier (never contradicting)
                        break
            elif flavour < 0.85:  # name_only
                party_name = base_name
            else:  # noisy, no ids
                party_name = _noise(base_name, rng)
            alerts.append({"alert_id": aid, "party_name": party_name,
                           "party_type": entry["entity_type"], **_party_id_row(ids),
                           "entry_uid": entry["uid"], "label": 1, "fp_category": ""})
            continue

        # ---- FALSE POSITIVE ----
        cat = rng.random()
        if cat < 0.70:  # generic collision
            entry = rng.choice(ent)
            gens = _entry_generic_tokens(entry) or [rng.choice(GENERIC_TOKENS)]
            party_name = "%s %s" % (_distinct(rng), rng.choice(gens))
            ptype = "ENTITY"
            fpc = "generic"
        elif cat < 0.82:  # entity-type mismatch
            entry = rng.choice(nonbiz) if nonbiz else rng.choice(ent)
            toks = _entry_distinct_tokens(entry) + _entry_generic_tokens(entry)
            share = rng.choice(toks) if toks else rng.choice(GENERIC_TOKENS)
            party_name = "%s %s" % (share, rng.choice(["TRADING", "LLC GROUP", "PARTNERS"]))
            ptype = "ENTITY"
            fpc = "type"
        elif cat < 0.92:  # identifier-discriminated
            entry = rng.choice(named)
            dts = _entry_distinct_tokens(entry)
            share = rng.choice(dts)
            if entry["entity_type"] == "INDIVIDUAL":
                party_name = "%s %s" % (rng.choice(GIVEN_NAMES), share)
                ptype = "INDIVIDUAL"
                ids["dob"] = _dob(rng)  # different DOB
                if entry.get("nationality"):
                    ids["nationality"] = rng.choice(CLEAN_COUNTRIES)
            else:
                party_name = "%s %s" % (share, rng.choice(GENERIC_TOKENS))
                ptype = "ENTITY"
                ids["country"] = rng.choice(CLEAN_COUNTRIES)  # different country
            fpc = "discriminator"
        else:  # weak residual — distinctive overlap, no identifiers
            entry = rng.choice(named)
            dts = _entry_distinct_tokens(entry)
            share = rng.choice(dts)
            if entry["entity_type"] == "INDIVIDUAL":
                party_name = "%s %s" % (rng.choice(GIVEN_NAMES), share)
                ptype = "INDIVIDUAL"
            else:
                party_name = "%s %s" % (share, rng.choice(GENERIC_TOKENS))
                ptype = "ENTITY"
            # a minority share the entry country (weak, non-clearing corroboration)
            if rng.random() < 0.3 and entry.get("country"):
                ids["country"] = entry["country"]
            fpc = "weak"

        alerts.append({"alert_id": aid, "party_name": party_name, "party_type": ptype,
                       **_party_id_row(ids), "entry_uid": entry["uid"],
                       "label": 0, "fp_category": fpc})
    return alerts


def _party_id_row(ids: dict) -> dict:
    return {"party_" + k: v for k, v in ids.items()}


def write_csv(path: str, rows: list[dict]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--watchlist", type=int, default=4000)
    ap.add_argument("--alerts", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    wl = make_watchlist(args.watchlist, rng)
    al = make_alerts(args.alerts, wl, rng)
    write_csv(os.path.join(args.out, "watchlist.csv"), wl)
    write_csv(os.path.join(args.out, "alerts.csv"), al)
    tp = sum(a["label"] for a in al)
    print(f"watchlist: {len(wl)} entries -> {args.out}/watchlist.csv")
    print(f"alerts:    {len(al)} ({tp} true matches, {len(al)-tp} false positives) "
          f"-> {args.out}/alerts.csv   [seed={args.seed}]")


if __name__ == "__main__":
    main()
