"""
Customer risk-rating engine — reference implementation.

Produces a 0-100 risk score and a LOW / MEDIUM / HIGH tier for a customer from a
documented set of weighted risk factors, with mandatory FLOORS that prevent a
known-high-risk customer being rated low. The full methodology — every factor,
weight, band, and floor — is in METHODOLOGY.md; this file is its executable form.

Design posture:
  * Transparent weighted composite of documented factors; no black box.
  * MONOTONIC by construction — raising any single risk factor never lowers the
    score (a non-negative weighted sum; floors only raise the tier).
  * FLOOR rules are the rating analogue of false-negative safety: a PEP can never
    be LOW; a sanctions / high-risk-jurisdiction nexus, a prior SAR, or confirmed
    adverse media force at least HIGH. The validation harness enforces "no
    hard-risk customer rated LOW" as a build gate.
  * The engine RATES; it does not decide onboarding. A rating drives the intensity
    of due diligence and monitoring; a human owns the relationship decision.

Deterministic: same inputs -> same rating.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.scoring import weighted_composite, band, tier_max  # noqa: E402

TIER_ORDER = ["LOW", "MEDIUM", "HIGH"]

# Documented factor weights (relative importance; normalized in the composite).
WEIGHTS = {
    "geography": 0.22,
    "products": 0.18,
    "customer_type": 0.15,
    "negative_history": 0.13,   # confirmed adverse media / prior SAR
    "pep": 0.12,
    "channel": 0.08,
    "ownership_opacity": 0.07,
    "expected_activity": 0.05,
}

# --- factor reference tables (illustrative; configure from your own methodology) ---
# Country risk buckets. The assignments below are ILLUSTRATIVE examples only; a
# deployment sources these from its country-risk methodology and the current FATF
# lists, which move over time.
COUNTRY_BUCKET_SCORE = {"HIGH": 100, "ELEVATED": 78, "STANDARD": 25, "LOW": 10}
COUNTRY_TIER = {
    "IR": "HIGH", "KP": "HIGH", "SY": "HIGH", "AF": "HIGH", "MM": "ELEVATED",
    "RU": "ELEVATED", "AE": "ELEVATED", "PA": "ELEVATED",
    "US": "STANDARD", "GB": "STANDARD", "DE": "STANDARD", "SG": "STANDARD",
    "FR": "STANDARD", "JP": "STANDARD", "CA": "LOW", "AU": "LOW", "NL": "LOW",
}
CUSTOMER_TYPE_RISK = {
    "INDIVIDUAL": 20, "SMB": 35, "CORPORATE": 30, "TRUST": 60,
    "MSB": 80, "NBFI": 68, "SHELL": 90,
}
PRODUCT_RISK = {
    "retail_deposit": 15, "lending": 25, "wire": 50, "trade_finance": 65,
    "private_banking": 70, "cash": 72, "crypto": 85, "correspondent": 92,
}
CHANNEL_RISK = {"FACE_TO_FACE": 15, "REMOTE": 60}

HIGH_GEO_BUCKETS = {"HIGH"}   # a nexus to these forces at least HIGH


@dataclass
class Config:
    low_band: float = 34.0    # score < low_band -> LOW
    high_band: float = 55.0   # score >= high_band -> HIGH
    pep_floor: str = "MEDIUM"
    high_risk_floor: str = "HIGH"


@dataclass
class Customer:
    customer_id: str
    customer_type: str = "INDIVIDUAL"
    domicile_country: str = "US"
    operating_countries: list = field(default_factory=list)
    products: list = field(default_factory=list)
    channel: str = "FACE_TO_FACE"
    pep: bool = False
    adverse_media: bool = False     # confirmed negative news
    prior_sar: bool = False
    ownership_opacity: float = 0.0  # 0 transparent .. 1 nominee/opaque
    expected_activity_intensity: float = 0.0  # 0 .. 1 vs stated purpose


@dataclass
class Rating:
    score: float            # 0-100
    tier: str               # LOW / MEDIUM / HIGH
    factor_scores: dict
    floors_applied: list
    reason: str

    def as_row(self) -> dict:
        return {"score": round(self.score, 2), "tier": self.tier,
                "floors_applied": ",".join(self.floors_applied), "reason": self.reason}


def _country_score(code: str) -> float:
    return COUNTRY_BUCKET_SCORE[COUNTRY_TIER.get(code, "STANDARD")]


def factor_scores(c: Customer) -> dict:
    """Each factor mapped to a common 0-100 sub-score. Monotone in the underlying
    risk of every input."""
    geos = [c.domicile_country] + list(c.operating_countries)
    geography = max((_country_score(g) for g in geos), default=25.0)
    products = max((PRODUCT_RISK.get(p, 30) for p in c.products), default=15.0)
    return {
        "geography": geography,
        "products": products,
        "customer_type": CUSTOMER_TYPE_RISK.get(c.customer_type, 30),
        "negative_history": 100.0 if c.prior_sar else (80.0 if c.adverse_media else 0.0),
        "pep": 100.0 if c.pep else 0.0,
        "channel": CHANNEL_RISK.get(c.channel, 30),
        "ownership_opacity": 100.0 * max(0.0, min(1.0, c.ownership_opacity)),
        "expected_activity": 100.0 * max(0.0, min(1.0, c.expected_activity_intensity)),
    }


def score_features(feats: dict) -> float:
    """Pure feature -> composite score (0-100). The monotonicity property is tested
    against this function; it is also the unit a deployment exposes as a tool."""
    return weighted_composite(feats, WEIGHTS)


def _floors(c: Customer, config: Config):
    """Mandatory minimum tiers. Each can only raise the rating."""
    applied = []
    floor = "LOW"
    geos = [c.domicile_country] + list(c.operating_countries)
    if any(COUNTRY_TIER.get(g) in HIGH_GEO_BUCKETS for g in geos):
        floor = tier_max(floor, config.high_risk_floor, TIER_ORDER); applied.append("high-risk-jurisdiction nexus")
    if c.prior_sar:
        floor = tier_max(floor, config.high_risk_floor, TIER_ORDER); applied.append("prior SAR")
    if c.adverse_media:
        floor = tier_max(floor, config.high_risk_floor, TIER_ORDER); applied.append("confirmed adverse media")
    if c.customer_type == "SHELL" and c.ownership_opacity >= 0.6:
        floor = tier_max(floor, config.high_risk_floor, TIER_ORDER); applied.append("opaque shell structure")
    if c.pep:
        floor = tier_max(floor, config.pep_floor, TIER_ORDER); applied.append("PEP")
    return floor, applied


def rate(c: Customer, config: Config = Config()) -> Rating:
    feats = factor_scores(c)
    score = score_features(feats)
    base_tier = band(score, [config.low_band, config.high_band], TIER_ORDER)
    floor, applied = _floors(c, config)
    tier = tier_max(base_tier, floor, TIER_ORDER)

    top = sorted(feats.items(), key=lambda kv: kv[1] * WEIGHTS[kv[0]], reverse=True)[:3]
    drivers = ", ".join(f"{k} ({int(v)})" for k, v in top)
    reason = f"Composite {score:.0f}/100 -> {base_tier}. Top drivers: {drivers}."
    if applied and TIER_ORDER.index(tier) > TIER_ORDER.index(base_tier):
        reason += f" Raised to {tier} by mandatory floor: {', '.join(applied)}."
    return Rating(score=score, tier=tier, factor_scores=feats,
                  floors_applied=applied, reason=reason)


if __name__ == "__main__":
    import json
    examples = [
        Customer("C1", customer_type="INDIVIDUAL", domicile_country="CA",
                 products=["retail_deposit"], channel="FACE_TO_FACE"),
        Customer("C2", customer_type="CORPORATE", domicile_country="DE",
                 operating_countries=["AE"], products=["wire", "trade_finance"],
                 channel="REMOTE", ownership_opacity=0.4),
        Customer("C3", customer_type="INDIVIDUAL", domicile_country="US",
                 products=["private_banking"], pep=True),
        Customer("C4", customer_type="MSB", domicile_country="US",
                 operating_countries=["IR"], products=["crypto", "wire"], prior_sar=True),
    ]
    for c in examples:
        r = rate(c)
        print(f"\n{c.customer_id}:")
        print(json.dumps(r.as_row(), indent=2))
