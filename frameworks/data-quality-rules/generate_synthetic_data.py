"""
Synthetic data generator for data-quality validation.

Produces one CSV with KNOWN ground truth:
  records.csv — a synthetic Harborview Financial Group customer/account
                extract, one row per record, labelled with its defect class.

Everything is invented and seeded; re-running with the same --seed reproduces
byte-identical files. Class COUNTS are deterministic (planted as exact
round(n * share) schedules, then shuffled), so per-class rates are stable
across seeds — only record content varies.

Defect classes:

CRITICAL (label 1 — every one must be detected at critical severity):
  null_name_active         blank full_name on an ACTIVE record
  missing_dob              blank DOB on an ACTIVE INDIVIDUAL
  malformed_dob            DOB fails the ISO/calendar parse (includes the
                           adversarial '1985-02-30' — format-valid, calendar-false)
  impossible_dob_sequence  DOB parses but is impossible: postdates onboarding,
                           or sits in the future (adversarial: valid in format)
  country_drift            ISO-adjacent-but-wrong country code (UK, EL, SU, ...)
  invalid_id_checksum      national identifier fails format or check digit
  exact_dup                identical name/DOB/identifier pair (both records labelled)
  near_dup_shared_id       transliterated-name pair sharing an identifier
                           (both records labelled — the adversarial re-onboard)

MINOR (label 0, named class — flagged at minor severity, not gate-relevant):
  null_name_inactive       blank full_name on a CLOSED record
  missing_supporting       blank entity_type / onboarding_date / national_id
  prefix_country_mismatch  account prefix disagrees with the country field
  entity_dob_conflict      ENTITY record carrying a date of birth
  stale_refresh            last refresh beyond the policy horizon

CLEAN (label 0):
  clean                    fully conformant record
  clean_edge               adversarial-BENIGN: accented / hyphenated /
                           apostrophe names, leap-day DOBs, boundary dates,
                           refresh just inside the horizon — records that must
                           NOT be flagged (they test the false-flag rate)
"""
from __future__ import annotations

import argparse
import csv
import datetime
import os
import random

# Must match scorer.DEFAULT_ASOF — the extract's deterministic batch date.
ASOF = datetime.date(2026, 6, 30)

# Must be a subset of scorer.COUNTRY_REF.
VALID_COUNTRIES = ["US", "GB", "DE", "FR", "CA", "SG", "AE", "JP", "AU", "CH",
                   "NL", "ES", "IT", "BR", "MX", "IN", "ZA", "SE", "NO", "IE",
                   "HK", "KR", "PL", "PT", "BE", "AT", "DK", "FI", "NZ", "LU"]
# ISO-adjacent-but-wrong: none of these are in scorer.COUNTRY_REF. UK is the
# classic (GB is the ISO code); EL is the EU-internal Greece code; SU/YU/BU/ZR
# are retired; the rest are user-assigned or transposition junk.
DRIFT_COUNTRIES = ["UK", "EL", "SU", "YU", "BU", "ZR", "XX", "ZZ", "QQ", "ED"]

FIRST = ["JAMES", "MARIA", "WEI", "AISHA", "CARLOS", "YUKI", "MOHAMMED",
         "ELENA", "PRIYA", "JOHAN", "FATIMA", "DAVID", "HUSSEIN", "INGRID",
         "KENJI", "AMARA", "PABLO", "NADIA", "VIKTOR", "CHLOE", "OMAR",
         "SOFIA", "ALEKSANDR", "MEI", "YUSUF", "HANNAH", "TARIQ", "LENA",
         "DIEGO", "KATHERINE"]
LAST = ["OKONKWO", "SILVA", "MULLER", "TANAKA", "AL-RASHID", "IVANOV",
        "GARCIA", "NAKAMURA", "HANSSON", "KOWALSKI", "REYES", "SCHMIDT",
        "HAIDARI", "FERREIRA", "LINDQVIST", "MORETTI", "KARIMI", "JOHANSSON",
        "DUBOIS", "PETROV", "YAMAMOTO", "NGUYEN", "HASSAN", "VARGAS",
        "ANDERSEN", "ROSSI", "KHAN", "COSTA", "BERGSTROM", "WATANABE"]
EDGE_FIRST = ["JOSÉ", "FRANÇOIS", "BJÖRN", "ANNE-MARIE", "ZOË", "RENÉE"]
EDGE_LAST = ["MÜLLER", "MUÑOZ", "O'BRIEN", "ØSTERGAARD", "DA-COSTA", "N'DIAYE"]
ENTITY_A = ["MERIDIAN", "HARBORVIEW", "ATLANTIC", "CRESTLINE", "NORTHGATE",
            "BLUEWATER", "IRONWOOD", "SUMMIT", "LAKESHORE", "PINNACLE"]
ENTITY_B = ["LOGISTICS", "TEXTILES", "COMMODITIES", "FREIGHT", "CONSULTING",
            "MARINE SUPPLY", "AGRO EXPORTS", "COMPONENTS", "MEDIA", "FOODS"]
ENTITY_SUFFIX = ["LTD", "LLC", "GMBH", "SA", "PTE", "BV"]

# Transliteration variants for near-duplicate plants. Each pair is also
# Soundex-equal, which is exactly why the engine's phonetic fallback exists.
TRANSLIT = {
    "MOHAMMED": "MUHAMMAD", "HUSSEIN": "HUSAYN", "ALEKSANDR": "ALEXANDER",
    "YUSUF": "YOUSSEF", "KATHERINE": "KATHRYN", "AISHA": "AYESHA",
    "OMAR": "UMAR", "FATIMA": "FATIMAH", "VIKTOR": "VICTOR",
    "HASSAN": "HASAN", "PETROV": "PETROFF", "IVANOV": "IVANOFF",
    "KARIMI": "KAREEMI", "AL-RASHID": "AL RASHEED", "TARIQ": "TARIK",
}
VOWELS = "AEIOU"

# Deterministic defect-mix profiles (shares of the population; classes absent
# from a profile contribute zero; the remainder is 'clean'). Duplicate classes
# are planted as PAIRS, so their share is consumed two records at a time.
PROFILES = {
    # the main validation extract — heavy enough to breach every
    # screening-critical ceiling, so the correct disposition is BLOCK
    "standard": {
        "clean_edge": 0.060,
        "null_name_active": 0.008, "missing_dob": 0.005, "malformed_dob": 0.008,
        "impossible_dob_sequence": 0.006, "country_drift": 0.010,
        "invalid_id_checksum": 0.008, "exact_dup": 0.005,
        "near_dup_shared_id": 0.005,
        "null_name_inactive": 0.010, "missing_supporting": 0.030,
        "prefix_country_mismatch": 0.012, "entity_dob_conflict": 0.008,
        "stale_refresh": 0.040,
    },
    # fully conformant feed (incl. adversarial-benign edges) -> FEED_PASS
    "clean": {"clean_edge": 0.080},
    # staleness over its ceiling, everything else within -> INVESTIGATE
    "minor_degraded": {"clean_edge": 0.050, "stale_refresh": 0.120,
                       "missing_supporting": 0.015,
                       "prefix_country_mismatch": 0.010},
    # one screening-critical CDE inside the warn band -> INVESTIGATE
    "warn_band": {"clean_edge": 0.050, "country_drift": 0.0035},
    # screening-critical breach (country + uniqueness) -> BLOCK
    "critical_breach": {"clean_edge": 0.050, "country_drift": 0.020,
                        "near_dup_shared_id": 0.006},
    # uniqueness-only breach -> BLOCK
    "dup_contaminated": {"clean_edge": 0.050, "near_dup_shared_id": 0.012,
                         "exact_dup": 0.004},
}
CRITICAL_CLASSES = ("null_name_active", "missing_dob", "malformed_dob",
                    "impossible_dob_sequence", "country_drift",
                    "invalid_id_checksum", "exact_dup", "near_dup_shared_id")
DUP_CLASSES = ("exact_dup", "near_dup_shared_id")


def make_national_id(serial: int) -> str:
    """Valid identifier under the documented contract — must match
    scorer.id_check: 'HV' + 7 digits + position-weighted check digit."""
    body = "%07d" % serial
    chk = sum((i + 1) * int(d) for i, d in enumerate(body)) % 10
    return f"HV{body}{chk}"


def _iso(d: datetime.date) -> str:
    return d.isoformat()


def _rand_date(rng, lo: datetime.date, hi: datetime.date) -> datetime.date:
    return lo + datetime.timedelta(days=rng.randint(0, (hi - lo).days))


def _clean_record(rng, serial: int) -> dict:
    """A fully conformant base record; defect classes mutate a copy of this."""
    is_ind = rng.random() < 0.80
    country = rng.choice(VALID_COUNTRIES)
    onboarding = _rand_date(rng, datetime.date(2006, 1, 1), datetime.date(2025, 12, 1))
    rec = {
        "full_name": (f"{rng.choice(FIRST)} {rng.choice(LAST)}" if is_ind
                      else f"{rng.choice(ENTITY_A)} {rng.choice(ENTITY_B)} "
                           f"{rng.choice(ENTITY_SUFFIX)}"),
        "entity_type": "INDIVIDUAL" if is_ind else "ENTITY",
        "dob": _iso(_rand_date(rng, datetime.date(1940, 1, 1),
                               datetime.date(2005, 12, 31))) if is_ind else "",
        "country": country,
        "national_id": make_national_id(serial),
        "account_prefix": f"{country}-{rng.randint(10, 99)}",
        "onboarding_date": _iso(onboarding),
        "status": rng.choices(["ACTIVE", "DORMANT", "CLOSED"],
                              [0.78, 0.12, 0.10])[0],
        "last_refresh": _iso(ASOF - datetime.timedelta(days=rng.randint(0, 300))),
    }
    return rec


def _edge_record(rng, serial: int) -> dict:
    """Adversarial-BENIGN: conformant records built to trip a sloppy engine —
    accents/hyphens/apostrophes the normalizer must fold, leap-day and
    boundary DOBs the parser must accept, refresh just inside the horizon."""
    rec = _clean_record(rng, serial)
    flavor = rng.choice(["accent_name", "leap_dob", "floor_dob",
                         "refresh_edge", "rare_country"])
    if flavor == "accent_name":
        rec["entity_type"] = "INDIVIDUAL"
        rec["full_name"] = f"{rng.choice(EDGE_FIRST)} {rng.choice(EDGE_LAST)}"
        if not rec["dob"]:
            rec["dob"] = "1979-07-19"
    elif flavor == "leap_dob":
        rec["entity_type"] = "INDIVIDUAL"
        rec["dob"] = rng.choice(["1988-02-29", "2000-02-29", "1996-02-29"])
    elif flavor == "floor_dob":
        rec["entity_type"] = "INDIVIDUAL"
        rec["dob"] = "1900-01-01"   # exactly on the plausibility floor
    elif flavor == "refresh_edge":
        rec["status"] = "ACTIVE"
        rec["last_refresh"] = _iso(ASOF - datetime.timedelta(days=360))
    else:
        rec["country"] = rng.choice(["LU", "NZ", "FI", "PT"])
        rec["account_prefix"] = f"{rec['country']}-{rng.randint(10, 99)}"
    return rec


def _transliterate(name: str, rng) -> str:
    """Perturb exactly one token: dictionary transliteration when available,
    else a mechanical Soundex-preserving edit (vowel swap, doubled-letter
    collapse, PH->F). Single-token, phonetics-preserving — the realistic
    re-onboard variant a naive exact-match dedupe misses."""
    toks = name.split(" ")
    for i, t in enumerate(toks):
        if t in TRANSLIT:
            toks[i] = TRANSLIT[t]
            return " ".join(toks)
    # mechanical fallback on the longest token
    i = max(range(len(toks)), key=lambda k: len(toks[k]))
    t = toks[i]
    if "PH" in t:
        toks[i] = t.replace("PH", "F", 1)
    elif any(t[j] == t[j + 1] for j in range(len(t) - 1)):
        for j in range(len(t) - 1):
            if t[j] == t[j + 1]:
                toks[i] = t[:j] + t[j + 1:]
                break
    else:
        # swap an internal vowel (position > 0 so the Soundex head survives)
        pos = [j for j in range(1, len(t)) if t[j] in VOWELS]
        j = pos[rng.randrange(len(pos))] if pos else len(t) - 1
        repl = "E" if t[j] != "E" else "A"
        toks[i] = t[:j] + repl + t[j + 1:]
    return " ".join(toks)


def _apply_class(rec: dict, cls: str, rng) -> dict:
    if cls in ("clean", "clean_edge"):
        return rec
    if cls == "null_name_active":
        rec["full_name"] = ""
        rec["status"] = "ACTIVE"
    elif cls == "null_name_inactive":
        rec["full_name"] = ""
        rec["status"] = "CLOSED"
    elif cls == "missing_dob":
        rec["entity_type"] = "INDIVIDUAL"
        rec["status"] = "ACTIVE"
        rec["dob"] = ""
    elif cls == "malformed_dob":
        rec["entity_type"] = "INDIVIDUAL"
        rec["dob"] = rng.choice([
            "1985-02-30", "1990-11-31", "1979-13-07",   # format-valid, calendar-false
            "07/04/1985", "19851207", "1985-6-1", "1985.06.01",
        ])
    elif cls == "impossible_dob_sequence":
        rec["entity_type"] = "INDIVIDUAL"
        ob = _rand_date(rng, datetime.date(2006, 1, 1), datetime.date(2018, 12, 31))
        rec["onboarding_date"] = _iso(ob)
        if rng.random() < 0.6:   # DOB after onboarding (parses, in range)
            span = (ASOF - ob).days - 1
            rec["dob"] = _iso(ob + datetime.timedelta(days=rng.randint(30, max(31, span))))
        else:                    # DOB in the future
            rec["dob"] = _iso(ASOF + datetime.timedelta(days=rng.randint(30, 900)))
    elif cls == "country_drift":
        rec["country"] = rng.choice(DRIFT_COUNTRIES)
        valid = rng.choice(VALID_COUNTRIES)
        rec["account_prefix"] = f"{valid}-{rng.randint(10, 99)}"
    elif cls == "invalid_id_checksum":
        good = rec["national_id"]
        variant = rng.choice(["chk", "prefix", "short", "letter"])
        if variant == "chk":
            rec["national_id"] = good[:-1] + str((int(good[-1]) + 1) % 10)
        elif variant == "prefix":
            rec["national_id"] = "HB" + good[2:]
        elif variant == "short":
            rec["national_id"] = good[:8]
        else:
            rec["national_id"] = good[:4] + "O" + good[5:]
    elif cls == "missing_supporting":
        field = rng.choice(["entity_type", "onboarding_date", "national_id"])
        rec[field] = ""
    elif cls == "prefix_country_mismatch":
        other = rng.choice([c for c in VALID_COUNTRIES if c != rec["country"]])
        rec["account_prefix"] = f"{other}-{rng.randint(10, 99)}"
    elif cls == "entity_dob_conflict":
        rec["entity_type"] = "ENTITY"
        rec["full_name"] = (f"{rng.choice(ENTITY_A)} {rng.choice(ENTITY_B)} "
                            f"{rng.choice(ENTITY_SUFFIX)}")
        rec["dob"] = _iso(_rand_date(rng, datetime.date(1960, 1, 1),
                                     datetime.date(2000, 12, 31)))
    elif cls == "stale_refresh":
        rec["status"] = "ACTIVE"
        rec["last_refresh"] = _iso(ASOF - datetime.timedelta(days=rng.randint(400, 1500)))
    else:
        raise ValueError(f"unknown defect class: {cls}")
    return rec


def make_records(n: int, rng: random.Random, mix: dict) -> list:
    """Generate n extract rows with the given defect mix. Class counts are
    deterministic: round(n * share) records per class (duplicate classes in
    pairs), remainder clean, order shuffled."""
    jobs = []
    slots = 0
    for cls, share in mix.items():
        if cls in DUP_CLASSES:
            pairs = int(round(n * share)) // 2
            jobs += [cls] * pairs
            slots += pairs * 2
        else:
            count = int(round(n * share))
            jobs += [cls] * count
            slots += count
    jobs += ["clean"] * (n - slots)
    rng.shuffle(jobs)

    rows, serial = [], 0

    def emit(rec: dict, cls: str):
        rid = len(rows)
        rows.append({"record_id": "REC-%07d" % rid,
                     "customer_id": "CUS-%07d" % rid, **rec,
                     "label": 1 if cls in CRITICAL_CLASSES else 0,
                     "category": cls})

    for cls in jobs:
        serial += 1
        if cls == "exact_dup":
            base = _clean_record(rng, serial)
            emit(dict(base), cls)
            emit(dict(base), cls)   # identical natural key, new record/customer id
        elif cls == "near_dup_shared_id":
            base = _clean_record(rng, serial)
            base["entity_type"] = "INDIVIDUAL"
            base["full_name"] = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
            if not base["dob"]:
                base["dob"] = "1982-04-11"
            emit(dict(base), cls)
            variant = dict(base)
            variant["full_name"] = _transliterate(base["full_name"], rng)
            variant["onboarding_date"] = _iso(_rand_date(
                rng, datetime.date(2019, 1, 1), datetime.date(2025, 12, 1)))
            emit(variant, cls)      # same national_id — the shared-identifier block
        elif cls == "clean_edge":
            emit(_edge_record(rng, serial), cls)
        else:
            emit(_apply_class(_clean_record(rng, serial), cls, rng), cls)
    return rows


def write_csv(path: str, rows: list):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--records", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--profile", default="standard", choices=sorted(PROFILES))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    rows = make_records(args.records, rng, PROFILES[args.profile])
    write_csv(os.path.join(args.out, "records.csv"), rows)
    crit = sum(r["label"] for r in rows)
    minor = sum(1 for r in rows if r["label"] == 0
                and r["category"] not in ("clean", "clean_edge"))
    print(f"records: {len(rows)} ({crit} critical-defect, {minor} minor-defect, "
          f"{len(rows) - crit - minor} clean) -> {args.out}/records.csv   "
          f"[seed={args.seed} profile={args.profile}]")


if __name__ == "__main__":
    main()
