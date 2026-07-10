"""
Jurisdiction risk-rating engine — reference implementation.

Produces a 0-100 inherent-risk score and a LOW / MEDIUM / HIGH / CRITICAL tier for a
country or territory from a documented weighted composite of seven public-index
dimensions, with mandatory FLOORS driven by categorical status designations that a
flattering index can never talk down. The full methodology — every dimension, weight,
band, normalization, and floor — is in METHODOLOGY.md; the public sources each
dimension is drawn from are in SOURCE-LIBRARY.md; this file is the executable form.

Design posture:
  * Transparent weighted composite of documented dimensions; no black box.
  * MONOTONIC by construction — raising any single dimension sub-score never lowers
    the composite (a non-negative weighted sum; floors only raise the tier).
  * FLOOR rules are the analogue of false-negative safety: a comprehensive sanctions
    program or a FATF "black list" designation forces CRITICAL; a FATF "grey list"
    listing, an EU high-risk-third-country designation, or an INCSR
    "primary-money-laundering-concern" listing forces at least HIGH. The validation
    harness enforces "no hard-designated jurisdiction rated below its floor" as a
    build gate.
  * The engine RATES INHERENT GEOGRAPHIC RISK; it does not decide whether to enter,
    exit, bank, or de-risk a market, and it is not a political judgement about a
    country. A human owns any action taken on the rating.

Deterministic: same inputs -> same rating.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.scoring import weighted_composite, band, tier_max  # noqa: E402

TIER_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Documented dimension weights (relative importance; normalized in the composite).
# The seven dimensions map onto the public indices catalogued in SOURCE-LIBRARY.md.
WEIGHTS = {
    "aml_cft": 0.30,          # Basel AML Index (continuous); FATF/EU/INCSR handled as floors
    "corruption": 0.22,       # Transparency International CPI + WGI control of corruption
    "governance": 0.16,       # World Bank WGI rule of law
    "secrecy": 0.14,          # Tax Justice Financial Secrecy Index
    "organized_crime": 0.08,  # Global Organized Crime Index
    "terrorism": 0.05,        # Global Terrorism Index
    "instability": 0.05,      # Fragile States Index / political instability
}


@dataclass
class Config:
    # Tier bands over the 0-100 composite. Three thresholds, four tiers.
    med_band: float = 40.0    # score < med_band  -> LOW
    high_band: float = 60.0   # med_band <= score < high_band -> MEDIUM
    crit_band: float = 80.0   # high_band <= score < crit_band -> HIGH; >= crit_band -> CRITICAL
    high_floor: str = "HIGH"
    critical_floor: str = "CRITICAL"


@dataclass
class Jurisdiction:
    code: str
    name: str = ""
    # Raw public-index inputs (as pulled; the engine normalizes them below).
    cpi_score: float = 50.0                 # Transparency Intl CPI: 0-100, higher = cleaner
    basel_score: float = 5.0                # Basel AML Index: 0-10, higher = worse
    wgi_rule_of_law_pct: float = 50.0       # WGI rule-of-law percentile: 0-100, higher = better
    wgi_control_corruption_pct: float = 50.0  # WGI control-of-corruption percentile
    secrecy_score: float = 40.0             # Financial Secrecy: 0-100, higher = more secret
    organized_crime_score: float = 40.0     # Organized-crime risk: 0-100, higher = worse
    terrorism_score: float = 20.0           # Terrorism risk: 0-100, higher = worse
    instability_score: float = 30.0         # Instability/fragility: 0-100, higher = worse
    # Categorical hard-risk designations (drive floors, never the weighted mean).
    comprehensive_sanctions: bool = False
    fatf_blacklist: bool = False            # FATF "call for action"
    fatf_greylist: bool = False             # FATF "increased monitoring"
    eu_high_risk: bool = False              # EU list of high-risk third countries
    incsr_primary_concern: bool = False     # INCSR "primary money-laundering concern"
    missing: list = field(default_factory=list)  # dimensions with no data (excluded, not scored)


@dataclass
class Rating:
    score: float            # 0-100
    tier: str               # LOW / MEDIUM / HIGH / CRITICAL
    dimension_scores: dict
    floors_applied: list
    dimensions_scored: int
    reason: str

    def as_row(self) -> dict:
        return {"score": round(self.score, 2), "tier": self.tier,
                "dimensions_scored": self.dimensions_scored,
                "floors_applied": ",".join(self.floors_applied), "reason": self.reason}


def _clip(x: float) -> float:
    return max(0.0, min(100.0, x))


def dimension_scores(j: Jurisdiction) -> dict:
    """Normalize each raw index onto a common 0-100 RISK scale (higher = more risk),
    stating each conversion. Monotone in the underlying risk of every input. A
    dimension named in `j.missing` is dropped so it is excluded from the composite
    rather than scored as a value."""
    corruption = ( (100.0 - j.cpi_score) + (100.0 - j.wgi_control_corruption_pct) ) / 2.0
    scores = {
        "aml_cft": _clip(j.basel_score * 10.0),
        "corruption": _clip(corruption),
        "governance": _clip(100.0 - j.wgi_rule_of_law_pct),
        "secrecy": _clip(j.secrecy_score),
        "organized_crime": _clip(j.organized_crime_score),
        "terrorism": _clip(j.terrorism_score),
        "instability": _clip(j.instability_score),
    }
    for m in j.missing:
        scores.pop(m, None)
    return scores


def score_features(feats: dict) -> float:
    """Pure feature -> composite score (0-100), renormalized across only the
    dimensions present. The monotonicity property is tested against this function;
    it is also the unit a deployment exposes as a tool."""
    weights = {k: WEIGHTS[k] for k in feats if k in WEIGHTS}
    return weighted_composite(feats, weights)


def _floors(j: Jurisdiction, config: Config):
    """Mandatory minimum tiers from categorical designations. Each can only raise."""
    applied = []
    floor = "LOW"
    if j.comprehensive_sanctions:
        floor = tier_max(floor, config.critical_floor, TIER_ORDER); applied.append("comprehensive sanctions program")
    if j.fatf_blacklist:
        floor = tier_max(floor, config.critical_floor, TIER_ORDER); applied.append("FATF black list (call for action)")
    if j.fatf_greylist:
        floor = tier_max(floor, config.high_floor, TIER_ORDER); applied.append("FATF grey list (increased monitoring)")
    if j.eu_high_risk:
        floor = tier_max(floor, config.high_floor, TIER_ORDER); applied.append("EU high-risk third country")
    if j.incsr_primary_concern:
        floor = tier_max(floor, config.high_floor, TIER_ORDER); applied.append("INCSR primary money-laundering concern")
    return floor, applied


def rate(j: Jurisdiction, config: Config = Config()) -> Rating:
    feats = dimension_scores(j)
    score = score_features(feats)
    base_tier = band(score, [config.med_band, config.high_band, config.crit_band], TIER_ORDER)
    floor, applied = _floors(j, config)
    tier = tier_max(base_tier, floor, TIER_ORDER)

    present_w = {k: WEIGHTS[k] for k in feats}
    top = sorted(feats.items(), key=lambda kv: kv[1] * present_w[kv[0]], reverse=True)[:3]
    drivers = ", ".join(f"{k} ({int(v)})" for k, v in top)
    reason = (f"Composite {score:.0f}/100 on {len(feats)} of {len(WEIGHTS)} dimensions "
              f"-> {base_tier}. Top drivers: {drivers}.")
    if applied and TIER_ORDER.index(tier) > TIER_ORDER.index(base_tier):
        reason += f" Raised to {tier} by hard-risk override: {', '.join(applied)}."
    return Rating(score=score, tier=tier, dimension_scores=feats,
                  floors_applied=applied, dimensions_scored=len(feats), reason=reason)


if __name__ == "__main__":
    import json
    examples = [
        Jurisdiction("XA", "Aldoria (clean)", cpi_score=82, basel_score=2.8,
                     wgi_rule_of_law_pct=88, wgi_control_corruption_pct=85,
                     secrecy_score=25, organized_crime_score=20, terrorism_score=8,
                     instability_score=15),
        Jurisdiction("XB", "Borland (mixed)", cpi_score=48, basel_score=5.2,
                     wgi_rule_of_law_pct=52, wgi_control_corruption_pct=50,
                     secrecy_score=55, organized_crime_score=45, terrorism_score=25,
                     instability_score=40),
        Jurisdiction("XC", "Calderia (grey-listed)", cpi_score=34, basel_score=6.4,
                     wgi_rule_of_law_pct=22, wgi_control_corruption_pct=28,
                     secrecy_score=68, organized_crime_score=60, terrorism_score=35,
                     instability_score=55, fatf_greylist=True),
        Jurisdiction("XD", "Doravia (sanctioned)", cpi_score=20, basel_score=8.1,
                     wgi_rule_of_law_pct=8, wgi_control_corruption_pct=10,
                     secrecy_score=80, organized_crime_score=78, terrorism_score=70,
                     instability_score=85, comprehensive_sanctions=True),
    ]
    for j in examples:
        r = rate(j)
        print(f"\n{j.code} — {j.name}:")
        print(json.dumps(r.as_row(), indent=2))
