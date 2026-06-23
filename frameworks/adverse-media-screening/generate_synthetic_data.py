"""
Synthetic data generator for adverse-media-screening validation.

Produces two CSVs with KNOWN ground truth:
  subjects.csv  — customers being screened (a mix of common and distinctive names)
  hits.csv      — media hits a screening tool surfaced for a subject, labelled with
                  whether the hit is a genuine, material adverse-media match and, for
                  false positives, WHY it is one.

Everything is invented and seeded. The population mirrors adverse-media screening:
the large majority of hits are false positives across two axes — wrong party, or
the article is not materially adverse.

False-positive categories:
  wrong_entity            a different party (same/similar name, contradicting hard id)
  not_adverse             the article is non-negative news
  low_role                the subject is a victim / passing mention, not a perpetrator
  stale_immaterial        old news in a minor category
  common_name_ambiguous   a common-name match with no identifier — cannot be cleared
                          OR confirmed; the irreducible band a human must work

True-adverse flavours (both name-match + materially adverse + perpetrator/alleged,
so neither can be auto-cleared):
  clear_adverse  strong match + serious recent content -> ESCALATE
  emerging       match + adverse but weaker -> ANALYST_REVIEW
"""
from __future__ import annotations

import argparse
import csv
import os
import random

COMMON_NAMES = ["JOHN SMITH", "MARIA GARCIA", "WEI CHEN", "MOHAMMED ALI",
                "DAVID JONES", "ANNA MULLER", "JOSE GONZALEZ", "LI WANG"]
GIVEN = ["DMITRI", "RACHEL", "OLUWASEUN", "INGRID", "TARIQ", "SVEN", "PRIYA", "KWAME"]
_SA = ["zar", "vol", "nor", "kre", "tash", "bur", "qom", "drav", "sev", "mor"]
_SB = ["kovsky", " stein".strip(), "enko", "adze", "oglu", "sson", "mann", "opoulos"]
COUNTRIES = ["US", "GB", "DE", "RU", "AE", "NG", "IN", "BR", "SG", "ZA"]
SERIOUS = ["money_laundering", "fraud", "corruption_bribery", "organized_crime", "sanctions_evasion"]
MODERATE = ["regulatory_enforcement", "tax_evasion", "fraud"]
MINOR = ["litigation_civil", "negative_general"]


def _distinctive(rng):
    return "%s %s%s" % (rng.choice(GIVEN), rng.choice(_SA).upper(), rng.choice(_SB).upper())


def _dob(rng):
    return "%04d-%02d-%02d" % (rng.randint(1950, 1995), rng.randint(1, 12), rng.randint(1, 28))


def make_subjects(n, rng):
    out = []
    for i in range(n):
        common = rng.random() < 0.40
        name = rng.choice(COMMON_NAMES) if common else _distinctive(rng)
        out.append({"subject_id": "SUBJ-%06d" % i, "name": name, "entity_type": "INDIVIDUAL",
                    "name_class": "common" if common else "distinctive",
                    "country": rng.choice(COUNTRIES), "dob": _dob(rng)})
    return out


def make_hits(n, subjects, rng, true_rate=0.05):
    common = [s for s in subjects if s["name_class"] == "common"]
    arts = lambda: {"country": "", "dob": "", "passport": ""}
    hits = []
    for i in range(n):
        hid = "AMHIT-%07d" % i
        art = arts()
        if rng.random() < true_rate:
            s = rng.choice(subjects)
            clear = rng.random() < 0.60
            name = s["name"]
            if clear:
                cat = rng.choice(SERIOUS); role = "perpetrator"; age = rng.randint(20, 360)
                # corroborate so common names can be confirmed (-> escalate)
                art["country"] = s["country"]
                if s["name_class"] == "common":
                    art["dob"] = s["dob"]
            else:  # emerging — weaker; no contradicting id, never stale-minor
                cat = rng.choice(MODERATE); role = rng.choice(["perpetrator", "alleged"])
                age = rng.randint(400, 1500)
            label, fpc = 1, ""
        else:
            roll = rng.random()
            s = rng.choice(subjects)
            name = s["name"]
            if roll < 0.30:                              # wrong_entity (contradicting strong id)
                cat = rng.choice(SERIOUS); role = "perpetrator"; age = rng.randint(20, 800)
                d = _dob(rng)
                while d == s["dob"]:
                    d = _dob(rng)
                art["dob"] = d                            # different person, same name
                fpc = "wrong_entity"
            elif roll < 0.55:                            # not_adverse
                cat = "non_adverse"; role = "mentioned"; age = rng.randint(5, 400); fpc = "not_adverse"
            elif roll < 0.68:                            # low_role
                cat = rng.choice(SERIOUS); role = rng.choice(["victim", "mentioned"])
                age = rng.randint(10, 400); fpc = "low_role"
            elif roll < 0.80:                            # stale_immaterial
                cat = rng.choice(MINOR); role = "perpetrator"; age = rng.randint(2200, 4000)
                fpc = "stale_immaterial"
            else:                                        # common_name_ambiguous (no id)
                s = rng.choice(common) if common else s
                name = s["name"]
                cat = rng.choice(SERIOUS); role = "perpetrator"; age = rng.randint(20, 500)
                fpc = "common_name_ambiguous"  # no identifiers on the article -> cannot resolve
            label = 0
        hits.append({"hit_id": hid, "subject_id": s["subject_id"], "article_name": name,
                     "category": cat, "role": role, "age_days": age,
                     "art_country": art["country"], "art_dob": art["dob"],
                     "art_passport": art["passport"], "source_reliability": 1.0,
                     "label": label, "fp_category": fpc})
    return hits


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--subjects", type=int, default=8000)
    ap.add_argument("--hits", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    subj = make_subjects(args.subjects, rng)
    hits = make_hits(args.hits, subj, rng)
    write_csv(os.path.join(args.out, "subjects.csv"), subj)
    write_csv(os.path.join(args.out, "hits.csv"), hits)
    t = sum(h["label"] for h in hits)
    print(f"subjects: {len(subj)} -> {args.out}/subjects.csv")
    print(f"hits:     {len(hits)} ({t} true adverse, {len(hits)-t} false positives) "
          f"-> {args.out}/hits.csv   [seed={args.seed}]")


if __name__ == "__main__":
    main()
