"""
New-product / new-activity (NPA) product-risk engine — reference implementation.

Scores a proposed product or service before launch: a 0-100 composite over nine
documented risk factors, a LOW / MEDIUM / HIGH tier, mandatory raise-only FLOORS,
and a ROUTING MAP that names the approval route, the mandatory pre-launch
conditions, and the post-launch review interval. The full methodology — every
factor, weight, band, floor, prohibited attribute, and route, in firing order —
is in METHODOLOGY.md; this file is its executable form.

Design posture:
  * Transparent weighted composite of documented factors; no black box.
  * MONOTONIC by construction — worsening any single factor never lowers the
    score (a non-negative weighted sum; floors only raise the tier).
  * FLOOR rules are the assessment analogue of false-negative safety: a
    sanctions-exposed jurisdiction or asset, or digital-asset custody the firm
    has never operated, force at least HIGH; a new client segment combined with
    a new geography forces at least MEDIUM. The validation harness enforces
    "no floor-triggered product tiered LOW" as a build gate.
  * PROHIBITED attributes come from a documented list and are never scored
    around: the product routes to REFER_PROHIBITED regardless of its composite.
  * The engine NEVER approves. It tiers, routes, and names conditions; the
    approval decision belongs to the committee, i.e. to humans.

Deterministic: same proposal -> same assessment.
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
    "fincrime_exposure": 0.18,      # product-inherent laundering surface
    "jurisdiction_footprint": 0.16,
    "asset_settlement_type": 0.13,
    "client_segment": 0.12,
    "novelty_to_firm": 0.12,
    "third_party_dependency": 0.09,
    "delivery_channel": 0.08,
    "model_ai_reliance": 0.07,
    "data_privacy_surface": 0.05,
}

# --- factor reference tables (illustrative; configure from your own methodology) ---
# Jurisdiction buckets. The assignments below are ILLUSTRATIVE examples only; a
# deployment sources these from its country-risk methodology, the current
# sanctions programs, and the current FATF lists, all of which move over time.
JURISDICTION_BUCKET_SCORE = {
    "PROHIBITED": 100, "SANCTIONS_EXPOSED": 95, "ELEVATED": 72,
    "STANDARD": 28, "LOW": 12,
}
JURISDICTION_BUCKET = {
    "KP": "PROHIBITED", "IR": "PROHIBITED", "SY": "PROHIBITED", "CU": "PROHIBITED",
    "RU": "SANCTIONS_EXPOSED", "BY": "SANCTIONS_EXPOSED", "VE": "SANCTIONS_EXPOSED",
    "MM": "SANCTIONS_EXPOSED",
    "AE": "ELEVATED", "TR": "ELEVATED", "PA": "ELEVATED", "HK": "ELEVATED",
    "US": "STANDARD", "GB": "STANDARD", "DE": "STANDARD", "SG": "STANDARD",
    "FR": "STANDARD", "JP": "STANDARD",
    "CA": "LOW", "AU": "LOW", "NL": "LOW", "NZ": "LOW",
}
CLIENT_SEGMENT_RISK = {
    "RETAIL": 25, "INSTITUTIONAL": 30, "HNW": 55,
    "NON_RESIDENT": 70, "UNREGULATED_ENTITY": 85,
}
DELIVERY_CHANNEL_RISK = {"BRANCH": 15, "ONLINE": 45, "INTERMEDIATED": 65, "API": 75}
ASSET_SETTLEMENT_RISK = {
    "FIAT": 25, "SECURITIES": 35, "DERIVATIVES": 55, "PHYSICAL": 60,
    "DIGITAL_ASSET": 85,
}
NOVELTY_RISK = {"EXISTING": 10, "ADJACENT": 45, "NEW_CAPABILITY": 80}
THIRD_PARTY_RISK = {"NONE": 5, "REGULATED": 40, "UNREGULATED": 80}
MODEL_AI_RISK = {"NONE": 5, "ASSISTIVE": 40, "AUTONOMOUS_DECISIONING": 85}

# The fincrime_exposure factor is itself a documented mix of three product-inherent
# inputs (each monotone in risk): cash intensity, anonymity features, cross-border
# reach. The mix weights are part of the methodology.
FINCRIME_MIX = {"cash_intensity": 0.40, "anonymity_features": 0.35, "cross_border_reach": 0.25}

# Jurisdiction buckets that force the sanctions-exposure floor.
SANCTIONS_FLOOR_BUCKETS = {"SANCTIONS_EXPOSED", "PROHIBITED"}

# Routing map: tier -> named approval route (checked AFTER the prohibited gate).
ROUTE_BY_TIER = {
    "LOW": "STANDARD_APPROVAL",
    "MEDIUM": "ENHANCED_REVIEW",
    "HIGH": "FULL_COMMITTEE",
}


@dataclass
class Config:
    low_band: float = 35.0     # score < low_band  -> LOW
    high_band: float = 60.0    # score >= high_band -> HIGH
    hard_floor: str = "HIGH"   # sanctions exposure / digital-asset custody novelty
    combo_floor: str = "MEDIUM"  # new segment + new geography combined
    fincrime_condition_threshold: float = 40.0   # sub-score that triggers the
                                                 # monitoring-coverage condition
    privacy_condition_threshold: float = 0.6
    review_days: dict = field(default_factory=lambda: {"HIGH": 90, "MEDIUM": 180, "LOW": 365})


@dataclass
class Product:
    """A product / activity proposal as submitted to the approval process."""
    product_id: str
    client_segment: str = "RETAIL"
    target_jurisdictions: list = field(default_factory=list)
    delivery_channel: str = "BRANCH"
    asset_settlement_type: str = "FIAT"
    novelty_to_firm: str = "EXISTING"
    third_party_dependency: str = "NONE"
    data_privacy_surface: float = 0.0    # 0 minimal .. 1 broad personal-data surface
    cash_intensity: float = 0.0          # 0 .. 1
    anonymity_features: bool = False     # pseudonymous / weakly-attributed transfers possible
    cross_border_reach: float = 0.0      # 0 .. 1
    model_ai_reliance: str = "NONE"
    involves_custody: bool = False       # firm holds the asset for the client
    sanctions_exposed_asset: bool = False  # settlement asset with documented
                                           # sanctions-evasion exposure
    new_client_segment: bool = False     # segment the firm does not currently serve
    new_geography: bool = False          # jurisdiction the firm does not currently serve
    # Prohibited-list attributes (documented; never scored around):
    anonymity_enhanced_instrument: bool = False  # mixer-integrated / privacy-coin settlement
    bearer_negotiable_feature: bool = False      # bearer-share / bearer-negotiable design


@dataclass
class Assessment:
    score: float             # 0-100
    tier: str                # LOW / MEDIUM / HIGH
    routing: str             # STANDARD_APPROVAL / ENHANCED_REVIEW / FULL_COMMITTEE / REFER_PROHIBITED
    factor_scores: dict
    floors_applied: list
    prohibited_attributes: list
    conditions: list         # named mandatory pre-launch conditions
    post_launch_review_days: int  # 0 when REFER_PROHIBITED (no launch path)
    reason: str

    def as_row(self) -> dict:
        return {"score": round(self.score, 2), "tier": self.tier, "routing": self.routing,
                "floors_applied": ",".join(self.floors_applied),
                "prohibited_attributes": ",".join(self.prohibited_attributes),
                "conditions": "; ".join(self.conditions),
                "post_launch_review_days": self.post_launch_review_days,
                "reason": self.reason}


def _jurisdiction_score(code: str) -> float:
    return JURISDICTION_BUCKET_SCORE[JURISDICTION_BUCKET.get(code, "STANDARD")]


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def factor_scores(p: Product) -> dict:
    """Each factor mapped to a common 0-100 sub-score. Monotone in the underlying
    risk of every input."""
    jurisdiction = max((_jurisdiction_score(j) for j in p.target_jurisdictions), default=28.0)
    fincrime = 100.0 * (
        FINCRIME_MIX["cash_intensity"] * _clamp01(p.cash_intensity)
        + FINCRIME_MIX["anonymity_features"] * (1.0 if p.anonymity_features else 0.0)
        + FINCRIME_MIX["cross_border_reach"] * _clamp01(p.cross_border_reach)
    )
    return {
        "fincrime_exposure": fincrime,
        "jurisdiction_footprint": jurisdiction,
        "asset_settlement_type": ASSET_SETTLEMENT_RISK.get(p.asset_settlement_type, 40),
        "client_segment": CLIENT_SEGMENT_RISK.get(p.client_segment, 40),
        "novelty_to_firm": NOVELTY_RISK.get(p.novelty_to_firm, 45),
        "third_party_dependency": THIRD_PARTY_RISK.get(p.third_party_dependency, 40),
        "delivery_channel": DELIVERY_CHANNEL_RISK.get(p.delivery_channel, 45),
        "model_ai_reliance": MODEL_AI_RISK.get(p.model_ai_reliance, 40),
        "data_privacy_surface": 100.0 * _clamp01(p.data_privacy_surface),
    }


def score_features(feats: dict) -> float:
    """Pure feature -> composite score (0-100). The monotonicity property is tested
    against this function; it is also the unit a deployment exposes as a tool."""
    return weighted_composite(feats, WEIGHTS)


def prohibited_attributes(p: Product) -> list:
    """The documented prohibited list, checked first and never scored around.
    Any hit routes the proposal to REFER_PROHIBITED."""
    hits = []
    if any(JURISDICTION_BUCKET.get(j) == "PROHIBITED" for j in p.target_jurisdictions):
        hits.append("prohibited-jurisdiction target market")
    if p.anonymity_enhanced_instrument:
        hits.append("anonymity-enhanced instrument")
    if p.bearer_negotiable_feature:
        hits.append("bearer-negotiable feature")
    return hits


def _floors(p: Product, config: Config):
    """Mandatory minimum tiers, in documented firing order. Each can only raise
    the tier."""
    applied = []
    floor = "LOW"
    if any(JURISDICTION_BUCKET.get(j) in SANCTIONS_FLOOR_BUCKETS for j in p.target_jurisdictions):
        floor = tier_max(floor, config.hard_floor, TIER_ORDER)
        applied.append("sanctions-exposed jurisdiction")
    if p.sanctions_exposed_asset:
        floor = tier_max(floor, config.hard_floor, TIER_ORDER)
        applied.append("sanctions-exposed asset")
    if (p.asset_settlement_type == "DIGITAL_ASSET" and p.involves_custody
            and p.novelty_to_firm == "NEW_CAPABILITY"):
        floor = tier_max(floor, config.hard_floor, TIER_ORDER)
        applied.append("digital-asset custody novelty")
    if p.new_client_segment and p.new_geography:
        floor = tier_max(floor, config.combo_floor, TIER_ORDER)
        applied.append("new-segment plus new-geography combination")
    return floor, applied


def _conditions(p: Product, feats: dict, tier: str, config: Config) -> list:
    """Named mandatory pre-launch conditions, in documented firing order."""
    conds = []
    elevated_geo = any(JURISDICTION_BUCKET.get(j, "STANDARD")
                       in {"ELEVATED", "SANCTIONS_EXPOSED", "PROHIBITED"}
                       for j in p.target_jurisdictions)
    if elevated_geo or p.sanctions_exposed_asset or p.cross_border_reach >= 0.5:
        conds.append("sanctions screening-coverage confirmation")
    if feats["fincrime_exposure"] >= config.fincrime_condition_threshold:
        conds.append("monitoring-rule coverage check")
    if p.asset_settlement_type == "DIGITAL_ASSET":
        conds.append("digital-asset control review")
    if p.third_party_dependency == "UNREGULATED":
        conds.append("third-party due-diligence completion")
    if p.model_ai_reliance == "AUTONOMOUS_DECISIONING":
        conds.append("model-risk validation signoff")
    if p.data_privacy_surface >= config.privacy_condition_threshold:
        conds.append("data-privacy assessment")
    conds.append(f"post-launch review at {config.review_days[tier]} days")
    return conds


def assess(p: Product, config: Config = Config()) -> Assessment:
    feats = factor_scores(p)
    score = score_features(feats)
    base_tier = band(score, [config.low_band, config.high_band], TIER_ORDER)
    floor, applied = _floors(p, config)
    tier = tier_max(base_tier, floor, TIER_ORDER)

    prohibited = prohibited_attributes(p)
    if prohibited:
        # Never scored around: prohibited attributes dominate the routing and
        # force the tier to HIGH for the record.
        tier = "HIGH"
        routing = "REFER_PROHIBITED"
        review_days = 0
        conditions = []
    else:
        routing = ROUTE_BY_TIER[tier]
        review_days = config.review_days[tier]
        conditions = _conditions(p, feats, tier, config)

    top = sorted(feats.items(), key=lambda kv: kv[1] * WEIGHTS[kv[0]], reverse=True)[:3]
    drivers = ", ".join(f"{k} ({int(v)})" for k, v in top)
    reason = f"Composite {score:.0f}/100 -> {base_tier}. Top drivers: {drivers}."
    if applied and TIER_ORDER.index(tier) > TIER_ORDER.index(base_tier) and not prohibited:
        reason += f" Raised to {tier} by mandatory floor: {', '.join(applied)}."
    if prohibited:
        reason += (f" PROHIBITED attribute present ({', '.join(prohibited)}) -> "
                   "REFER_PROHIBITED; not scored around.")
    else:
        reason += f" Routing: {routing}."
    return Assessment(score=score, tier=tier, routing=routing, factor_scores=feats,
                      floors_applied=applied, prohibited_attributes=prohibited,
                      conditions=conditions, post_launch_review_days=review_days,
                      reason=reason)


if __name__ == "__main__":
    import json
    examples = [
        Product("NPA-1", client_segment="RETAIL", target_jurisdictions=["CA"],
                delivery_channel="BRANCH", asset_settlement_type="FIAT",
                novelty_to_firm="EXISTING"),
        Product("NPA-2", client_segment="INSTITUTIONAL", target_jurisdictions=["DE", "AE"],
                delivery_channel="INTERMEDIATED", asset_settlement_type="DERIVATIVES",
                novelty_to_firm="ADJACENT", third_party_dependency="REGULATED",
                cross_border_reach=0.6, model_ai_reliance="ASSISTIVE"),
        Product("NPA-3", client_segment="HNW", target_jurisdictions=["SG"],
                delivery_channel="API", asset_settlement_type="DIGITAL_ASSET",
                novelty_to_firm="NEW_CAPABILITY", involves_custody=True,
                third_party_dependency="UNREGULATED", cash_intensity=0.2,
                cross_border_reach=0.7, data_privacy_surface=0.7),
        Product("NPA-4", client_segment="NON_RESIDENT", target_jurisdictions=["GB", "IR"],
                delivery_channel="ONLINE", asset_settlement_type="DIGITAL_ASSET",
                anonymity_enhanced_instrument=True),
    ]
    for p in examples:
        a = assess(p)
        print(f"\n{p.product_id}:")
        print(json.dumps(a.as_row(), indent=2))
