"""
Seeded synthetic-population generator for the jurisdiction-risk framework.

Builds a population of FICTIONAL jurisdictions across five designed-risk strata. No
real country is represented — every jurisdiction is an invented code and name, so a
rating here is never a claim about any real place. The stratum is assigned from the
construction, independently of the engine's weighted formula, so agreement between the
designed stratum and the engine's tier is a real test rather than a tautology.

Strata:
  designed_low / designed_medium / designed_high — soft dimensions only, no hard
    designation. These validate DISCRIMINATION: mean score must rise across them.
  hard_high     — moderate soft dimensions PLUS one HIGH-floor designation (FATF grey
    list, EU high-risk, or INCSR primary concern). Their composite is deliberately not
    already HIGH, so the floor is doing the work. Gate: never rated below HIGH.
  hard_critical — moderate/elevated soft dimensions PLUS one CRITICAL-floor designation
    (FATF black list or a comprehensive sanctions program). Gate: never below CRITICAL.
"""
from __future__ import annotations

FIELDS = [
    "code", "name", "stratum", "cpi_score", "basel_score", "wgi_rule_of_law_pct",
    "wgi_control_corruption_pct", "secrecy_score", "organized_crime_score",
    "terrorism_score", "instability_score", "comprehensive_sanctions",
    "fatf_blacklist", "fatf_greylist", "eu_high_risk", "incsr_primary_concern",
    "missing",
]

# Per-stratum raw-input ranges (inclusive). cpi/wgi are "goodness" scales (higher =
# cleaner/better); basel and the *_score fields are "risk" scales (higher = worse).
BANDS = {
    "designed_low": dict(cpi=(74, 90), basel=(1.0, 3.4), rol=(74, 95), coc=(72, 94),
                         secrecy=(10, 34), oc=(5, 30), terror=(2, 20), instab=(5, 30)),
    "designed_medium": dict(cpi=(44, 60), basel=(3.8, 5.6), rol=(44, 62), coc=(42, 60),
                            secrecy=(38, 56), oc=(34, 52), terror=(14, 32), instab=(28, 46)),
    "designed_high": dict(cpi=(18, 37), basel=(6.0, 8.6), rol=(8, 34), coc=(10, 34),
                          secrecy=(60, 86), oc=(55, 82), terror=(30, 66), instab=(50, 86)),
    # Hard strata: soft inputs kept moderate/low so the floor — not the composite — is
    # what lifts the tier. That makes the floor gate a genuine test.
    "hard_high": dict(cpi=(46, 66), basel=(3.2, 5.2), rol=(46, 66), coc=(44, 64),
                      secrecy=(30, 52), oc=(28, 48), terror=(10, 28), instab=(24, 44)),
    "hard_critical": dict(cpi=(38, 60), basel=(4.0, 6.0), rol=(38, 60), coc=(36, 58),
                          secrecy=(40, 62), oc=(38, 58), terror=(18, 40), instab=(34, 56)),
}

# Population mix across strata.
MIX = [("designed_low", 0.30), ("designed_medium", 0.30), ("designed_high", 0.20),
       ("hard_high", 0.12), ("hard_critical", 0.08)]

HIGH_FLOOR_FLAGS = ["fatf_greylist", "eu_high_risk", "incsr_primary_concern"]
CRIT_FLOOR_FLAGS = ["fatf_blacklist", "comprehensive_sanctions"]


def _u(rng, lo, hi, ndigits=1):
    return round(rng.uniform(lo, hi), ndigits)


def _blank_flags():
    return {f: 0 for f in
            ("comprehensive_sanctions", "fatf_blacklist", "fatf_greylist",
             "eu_high_risk", "incsr_primary_concern")}


def _make_one(idx, stratum, rng):
    b = BANDS[stratum]
    flags = _blank_flags()
    missing = []
    if stratum == "hard_high":
        flags[rng.choice(HIGH_FLOOR_FLAGS)] = 1
    elif stratum == "hard_critical":
        flags[rng.choice(CRIT_FLOOR_FLAGS)] = 1
    # A small share of jurisdictions is missing one context dimension — exercises the
    # engine's exclude-and-renormalize path rather than scoring an absent dimension.
    if rng.random() < 0.08:
        missing = [rng.choice(["organized_crime", "terrorism", "instability"])]
    row = {
        "code": f"J{idx:04d}", "name": f"Jurisdiction {idx:04d}", "stratum": stratum,
        "cpi_score": _u(rng, *b["cpi"]), "basel_score": _u(rng, *b["basel"], 2),
        "wgi_rule_of_law_pct": _u(rng, *b["rol"]),
        "wgi_control_corruption_pct": _u(rng, *b["coc"]),
        "secrecy_score": _u(rng, *b["secrecy"]),
        "organized_crime_score": _u(rng, *b["oc"]),
        "terrorism_score": _u(rng, *b["terror"]),
        "instability_score": _u(rng, *b["instab"]),
        "missing": "|".join(missing),
    }
    row.update(flags)
    return row


def make_jurisdictions(n, rng):
    """Return n synthetic jurisdiction rows across the designed strata (deterministic
    for a given rng)."""
    counts = [(s, int(round(n * frac))) for s, frac in MIX]
    # absorb rounding drift into the largest stratum
    drift = n - sum(c for _, c in counts)
    counts[0] = (counts[0][0], counts[0][1] + drift)
    rows = []
    idx = 1
    for stratum, c in counts:
        for _ in range(c):
            rows.append(_make_one(idx, stratum, rng))
            idx += 1
    rng.shuffle(rows)
    return rows


if __name__ == "__main__":
    import random
    sample = make_jurisdictions(12, random.Random(42))
    for r in sample:
        print(r["code"], r["stratum"], "basel", r["basel_score"], "cpi", r["cpi_score"],
              "flags", {k: v for k, v in r.items() if k in _blank_flags() and v})
