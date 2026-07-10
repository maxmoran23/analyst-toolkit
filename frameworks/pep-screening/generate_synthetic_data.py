"""
Synthetic data generator for PEP-screening validation.

Produces two CSVs with KNOWN ground truth:
  pep_list.csv  — a fictional politically-exposed-person list (invented officials
                  of invented countries; tiers, status, step-down years,
                  jurisdiction buckets, adverse flags)
  alerts.csv    — alerts a screening filter would raise, each a (customer x
                  entry) pair, labelled with whether it is a genuine IN-SCOPE
                  PEP match and, for false positives, WHY it is one.

Everything is invented and seeded. Countries, offices, and people are all
fictional — no real person, official, or state is represented. Re-running with
the same --seed reproduces byte-identical files.

The population mirrors real PEP screening: the large majority of alerts are
false positives across two axes — wrong party, or an out-of-scope entry.

False-positive categories (label 0):
  wrong_party_common_name  a different person sharing a common name; DOB and
                           nationality both contradict the entry
  wrong_party_translit     a different person under a transliteration-variant
                           spelling of a distinctive name; both identifiers
                           contradict
  generic_token            a collision on a common given name only; the entry's
                           distinctive surname went unmatched
  out_of_scope_former      the entry is a former TIER_3/RCA past its step-down
                           horizon with no adverse indicator (a minority share
                           the entry's nationality — weak corroboration — and
                           must NOT be cleared)
  common_name_ambiguous    a common-name match with no identifiers either way —
                           cannot be cleared OR confirmed; the irreducible band
                           a human must work

True-match flavours (label 1 — right party AND in-scope; none can be cleared):
  corroborated_current  current PEP, DOB + nationality corroborate  -> escalate
  noisy_t1_current      current TIER_1 under transliteration noise, no
                        identifiers — the adversarial plant a naive score
                        threshold would wrongly clear
  common_name_true      the customer genuinely IS the common-named PEP
                        (corroborated 60% of the time; never clearable either way)
  rca_true              relative/close associate under a DIFFERENT surname,
                        current or within the RCA horizon
  former_within_horizon former TIER_3 still inside the 5-year horizon
  former_senior         former TIER_1/TIER_2 — never fully decays
  adverse_former        former TIER_3/RCA past the horizon BUT adverse-flagged —
                        step-down is suspended
"""
from __future__ import annotations

import argparse
import csv
import os
import random

# ---- fictional geography: ILLUSTRATIVE corruption-risk buckets --------------
# All countries are invented. Bucket membership is illustrative by design —
# real corruption-risk indices move; a deployment maintains its own mapping.
COUNTRY_BUCKETS = {
    "KORVANIA": "HIGH", "ZEMBRATA": "HIGH", "TASHKUVAN": "HIGH", "BALDURIA": "HIGH",
    "NORVENIA": "MEDIUM", "DRAVELLIA": "MEDIUM", "ARBEQUIA": "MEDIUM", "QUELLARA": "MEDIUM",
    "MERIDONIA": "LOW", "VESTMARLAND": "LOW", "SOLVENNIA": "LOW", "THALASSIA": "LOW",
}
COUNTRIES = list(COUNTRY_BUCKETS)

# ---- fictional offices per prominence tier ----------------------------------
TIER1_POSITIONS = ["PRESIDENT", "PRIME MINISTER", "FINANCE MINISTER",
                   "DEFENSE MINISTER", "CENTRAL BANK GOVERNOR", "CHIEF JUSTICE",
                   "ARMY CHIEF OF STAFF"]
TIER2_POSITIONS = ["DEPUTY MINISTER", "AMBASSADOR", "STATE OIL COMPANY CEO",
                   "STATE RAILWAY DIRECTOR GENERAL", "SENIOR PARTY SECRETARY",
                   "SUPREME COURT JUDGE", "NATIONAL POLICE COMMISSIONER"]
TIER3_POSITIONS = ["PROVINCIAL GOVERNOR", "MAYOR", "REGIONAL COUNCILLOR",
                   "CUSTOMS DISTRICT DIRECTOR", "MUNICIPAL TREASURER",
                   "DISTRICT JUDGE"]
RCA_RELATIONSHIPS = ["SPOUSE", "SIBLING", "ADULT CHILD", "BUSINESS ASSOCIATE"]

# ---- names -------------------------------------------------------------------
# Common names: small pools reused across many entries, so every token lands
# above the genericness df-share floor — the Kim/Park/Mohammed/Garcia problem.
COMMON_GIVEN = ["DAVID", "MARIA", "JAMES", "SUSAN", "OMAR", "MEI", "CARLOS", "ANNA"]
COMMON_SURNAME = ["KIM", "PARK", "MOHAMMED", "GARCIA", "CHEN", "SILVA", "KHAN", "SANTOS"]
# Given names for distinctive-surname entries — also generic by frequency.
GIVEN = ["TARIQ", "INGRID", "KWAME", "PRIYA", "DMITRI", "LEILA", "MATEO", "YUKI",
         "SVEN", "AMARA", "VIKTOR", "NADIA", "OLUSEGUN", "HANNE", "RAVI"]
_VOWELS = "AEIOU"
# 3-syllable surname space (~7,200 combinations) keeps each distinctive token
# at df-share well below the genericness floor (same design as the sanctions
# generator, where a smaller space produced fake-generic collisions).
_SYL_A = ["zar", "vol", "nor", "kre", "tash", "bur", "lan", "qom", "drav", "sev",
          "mor", "kal", "rus", "ten", "pol", "var", "gor", "shi", "dan", "fer"]
_SYL_B = ["kov", "ova", "ian", "zin", "dar", "neft", "stroy", "mir", "tek",
          "gal", "bek", "ran", "sol", "mun", "vash", "dor", "lin", "sk"]


def _distinct(rng: random.Random) -> str:
    return (rng.choice(_SYL_A) + rng.choice(_SYL_B) + rng.choice(_SYL_A)).upper()


def _dob(rng: random.Random) -> str:
    return "%04d-%02d-%02d" % (rng.randint(1940, 1990), rng.randint(1, 12), rng.randint(1, 28))


def _noise(name: str, rng: random.Random) -> str:
    """Transliteration-style noise: swap 1-3 INTERIOR vowels for other vowels
    (ABDULLAH -> ABDALLAH). Deliberately Soundex-preserving — vowels are uncoded
    and the first letter is never touched — so the distinctive token still
    phonetically aligns and a true match can never be lost to "no tokens
    matched". It models real transliteration variance, where vowels move and
    consonant skeletons hold."""
    chars = list(name)
    positions = [i for i in range(1, len(chars)) if chars[i] in _VOWELS]
    rng.shuffle(positions)
    for i in positions[: rng.randint(1, 3)]:
        chars[i] = rng.choice([v for v in _VOWELS if v != chars[i]])
    return "".join(chars)


def _other_country(rng: random.Random, not_this: str) -> str:
    c = rng.choice(COUNTRIES)
    while c == not_this:
        c = rng.choice(COUNTRIES)
    return c


def _other_dob(rng: random.Random, not_this: str) -> str:
    d = _dob(rng)
    while d == not_this:
        d = _dob(rng)
    return d


# --------------------------------------------------------------------------- #
# PEP list
# --------------------------------------------------------------------------- #
def make_peps(n: int, rng: random.Random) -> list[dict]:
    peps = []
    for i in range(n):
        roll = rng.random()
        principal_tier = ""
        principal_name = ""
        relationship = ""
        if roll < 0.08:
            tier = "TIER_1"; position = rng.choice(TIER1_POSITIONS)
        elif roll < 0.30:
            tier = "TIER_2"; position = rng.choice(TIER2_POSITIONS)
        elif roll < 0.75:
            tier = "TIER_3"; position = rng.choice(TIER3_POSITIONS)
        else:
            tier = "RCA"
            relationship = rng.choice(RCA_RELATIONSHIPS)
            principal_tier = rng.choices(["TIER_1", "TIER_2", "TIER_3"],
                                         weights=[0.15, 0.35, 0.50])[0]
            principal_name = "%s %s" % (rng.choice(GIVEN), _distinct(rng))
            position = "%s OF %s" % (relationship, principal_name)

        # RCAs always carry their OWN name under a DIFFERENT surname than the
        # principal — the adversarial shape that defeats principal-surname matching.
        common = tier != "RCA" and rng.random() < 0.25
        if common:
            name = "%s %s" % (rng.choice(COMMON_GIVEN), rng.choice(COMMON_SURNAME))
        else:
            name = "%s %s" % (rng.choice(GIVEN), _distinct(rng))

        status = "CURRENT" if rng.random() < 0.55 else "FORMER"
        years = rng.randint(1, 30) if status == "FORMER" else 0
        country = rng.choice(COUNTRIES)
        aliases = [_noise(name, rng)] if (not common and rng.random() < 0.20) else []
        peps.append({
            "pep_id": "PEP-%06d" % i, "name": name, "tier": tier,
            "position": position, "country": country,
            "jurisdiction_risk": COUNTRY_BUCKETS[country],
            "status": status, "years_since_left": years,
            "principal_tier": principal_tier, "principal_name": principal_name,
            "relationship": relationship,
            "adverse_flag": 1 if rng.random() < 0.06 else 0,
            "dob": _dob(rng), "aliases": "|".join(aliases),
            "name_class": "common" if common else "distinctive",
        })
    return peps


def _rca_horizon(p: dict) -> float:
    return 0.5 * (10.0 if p["principal_tier"] in ("TIER_1", "TIER_2") else 5.0)


def _beyond_horizon(p: dict) -> bool:
    if p["status"] != "FORMER" or p["tier"] not in ("TIER_3", "RCA"):
        return False
    horizon = 5.0 if p["tier"] == "TIER_3" else _rca_horizon(p)
    return p["years_since_left"] > horizon


def build_pools(peps: list[dict]) -> dict:
    """Deterministic entry pools per alert flavour, so every label is
    constructed against a known in-scope / out-of-scope ground truth."""
    return {
        "current_distinct": [p for p in peps if p["status"] == "CURRENT"
                             and p["tier"] != "RCA" and p["name_class"] == "distinctive"],
        "t1_current_distinct": [p for p in peps if p["tier"] == "TIER_1"
                                and p["status"] == "CURRENT"
                                and p["name_class"] == "distinctive"],
        "common_current": [p for p in peps if p["status"] == "CURRENT"
                           and p["name_class"] == "common"],
        "rca_in_scope": [p for p in peps if p["tier"] == "RCA"
                         and (p["status"] == "CURRENT"
                              or (p["status"] == "FORMER" and p["years_since_left"] <= 2))],
        "t3_former_within": [p for p in peps if p["tier"] == "TIER_3"
                             and p["status"] == "FORMER"
                             and 1 <= p["years_since_left"] <= 4],
        "senior_former": [p for p in peps if p["tier"] in ("TIER_1", "TIER_2")
                          and p["status"] == "FORMER"],
        "out_of_scope": [p for p in peps if _beyond_horizon(p) and not p["adverse_flag"]],
        "adverse_out": [p for p in peps if _beyond_horizon(p) and p["adverse_flag"]],
        "distinct_any": [p for p in peps if p["name_class"] == "distinctive"],
    }


# --------------------------------------------------------------------------- #
# Alerts
# --------------------------------------------------------------------------- #
def make_alerts(n: int, peps: list[dict], rng: random.Random,
                true_rate: float = 0.04) -> list[dict]:
    pools = build_pools(peps)

    alerts = []
    for i in range(n):
        aid = "PEPALR-%07d" % i
        dob = nat = ""
        if rng.random() < true_rate:
            # ---- TRUE, IN-SCOPE MATCH (label 1) ----
            f = rng.random()
            if f < 0.30:  # corroborated_current
                p = rng.choice(pools["current_distinct"])
                name = p["name"]
                dob, nat = p["dob"], p["country"]
            elif f < 0.42:  # noisy_t1_current (adversarial: no identifiers)
                p = rng.choice(pools["t1_current_distinct"])
                name = _noise(p["name"], rng)
            elif f < 0.57:  # common_name_true
                p = rng.choice(pools["common_current"])
                name = p["name"]
                if rng.random() < 0.60:
                    dob, nat = p["dob"], p["country"]
            elif f < 0.70:  # rca_true (different surname than principal)
                p = rng.choice(pools["rca_in_scope"])
                name = p["name"]
                if rng.random() < 0.50:
                    dob = p["dob"]
            elif f < 0.82:  # former_within_horizon (TIER_3, 1-4 years out)
                p = rng.choice(pools["t3_former_within"])
                name = p["name"]
                if rng.random() < 0.50:
                    dob = p["dob"]
            elif f < 0.94:  # former_senior (TIER_1/TIER_2 — never fully decays)
                p = rng.choice(pools["senior_former"])
                name = p["name"]
                if rng.random() < 0.50:
                    dob, nat = p["dob"], p["country"]
            else:  # adverse_former (past horizon BUT adverse-flagged)
                p = rng.choice(pools["adverse_out"])
                name = p["name"]
                if rng.random() < 0.50:
                    dob = p["dob"]
            label, neg = 1, ""
        else:
            # ---- FALSE POSITIVE (label 0) ----
            roll = rng.random()
            if roll < 0.26:  # wrong_party_common_name
                p = rng.choice(pools["common_current"])
                name = p["name"]
                dob = _other_dob(rng, p["dob"])
                nat = _other_country(rng, p["country"])
                neg = "wrong_party_common_name"
            elif roll < 0.38:  # wrong_party_translit
                p = rng.choice(pools["distinct_any"])
                name = _noise(p["name"], rng)
                dob = _other_dob(rng, p["dob"])
                nat = _other_country(rng, p["country"])
                neg = "wrong_party_translit"
            elif roll < 0.64:  # out_of_scope_former
                p = rng.choice(pools["out_of_scope"])
                name = p["name"]
                # a minority share the entry's nationality — weak corroboration
                # that must BLOCK the status clear (routes to a human instead)
                nat = p["country"] if rng.random() < 0.15 else _other_country(rng, p["country"])
                neg = "out_of_scope_former"
            elif roll < 0.88:  # generic_token (given-name-only collision)
                p = rng.choice(pools["distinct_any"])
                given = p["name"].split(" ")[0]
                name = "%s %s" % (given, _distinct(rng))
                nat = _other_country(rng, p["country"])
                neg = "generic_token"
            else:  # common_name_ambiguous (no identifiers either way)
                p = rng.choice(pools["common_current"])
                name = p["name"]
                neg = "common_name_ambiguous"
            label = 0

        alerts.append({"alert_id": aid, "customer_name": name, "customer_dob": dob,
                       "customer_nationality": nat, "pep_id": p["pep_id"],
                       "label": label, "neg_category": neg})
    return alerts


def write_csv(path: str, rows: list[dict]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--peps", type=int, default=8000)
    ap.add_argument("--alerts", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    peps = make_peps(args.peps, rng)
    alerts = make_alerts(args.alerts, peps, rng)
    write_csv(os.path.join(args.out, "pep_list.csv"), peps)
    write_csv(os.path.join(args.out, "alerts.csv"), alerts)
    t = sum(a["label"] for a in alerts)
    print(f"pep list: {len(peps)} entries -> {args.out}/pep_list.csv")
    print(f"alerts:   {len(alerts)} ({t} true in-scope matches, {len(alerts)-t} "
          f"false positives) -> {args.out}/alerts.csv   [seed={args.seed}]")


if __name__ == "__main__":
    main()
