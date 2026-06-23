"""
On-chain KYT address-risk scoring engine — reference implementation.

Consumes the exposure features of a blockchain address (its strongest tainted-path
connection to an illicit entity, as a chain-analytics layer would compute via
`_lib/graph`) and dispositions it with a NAMED rationale. Full methodology in
METHODOLOGY.md; this file is its executable form.

A KYT flag is a false positive (or low-risk) several provable ways, and the engine
names which:
  benign_category      the "exposure" is to a licensed exchange / blue-chip DeFi /
                       merchant — not illicit at all
  broken_intermediary  illicit funds reach the address only THROUGH a commingling
                       service (CEX); attribution is broken downstream
  de_minimis           the traceable value share is below materiality
  diluted_distant      the illicit source is too many hops away / the exposure has
                       decayed below an actionable level

Design posture (same conservative stance as the other frameworks):
  * Auto-clears only on a named, provable cause; never on a low score alone.
  * Never auto-clears material, proximate, unbroken exposure to a serious illicit
    category -> false-negative safety is structural.
  * Escalates such exposure for investigation / a SAR or freeze decision; it does
    not itself freeze funds or file.

Deterministic. Same inputs -> same disposition.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.aggregations import clamp  # noqa: E402

# Illicit-category severities (0..1). Benign categories are 0 — exposure to them is
# not risk. Illustrative; configure against your chain-analytics taxonomy.
CATEGORY_SEVERITY = {
    "sanctioned_address": 1.00, "terrorism_financing": 1.00, "ransomware": 0.95,
    "darknet_market": 0.95, "mixer": 0.92, "stolen_funds": 0.88, "fraud_proceeds": 0.80,
    "scam": 0.78, "high_risk_exchange": 0.60, "gambling": 0.40, "unhosted_wallet": 0.30,
    # benign — exposure to these is not illicit
    "licensed_exchange": 0.0, "defi_bluechip": 0.0, "merchant_processor": 0.0,
    "mining_pool": 0.0, "none": 0.0,
}


@dataclass
class Config:
    deminimis_fraction: float = 0.02     # value share below which exposure is immaterial
    max_actionable_hops: int = 4         # beyond this the trail is too remote
    dilution_floor: float = 0.04         # exposure below this is too decayed to action
    escalate_floor: float = 0.30         # exposure at/above which to escalate
    review_high: float = 0.12
    review_medium: float = 0.05


@dataclass
class AddressAlert:
    address: str
    top_category: str            # illicit (or benign) category of the strongest exposure
    exposure: float              # propagated taint risk in [0,1] (from _lib/graph)
    hops: object = None          # int hops to the seed, or None if unexposed
    amount_fraction: float = 0.0  # value share traceable to the source, [0,1]
    via_breaker: bool = False    # reachable from illicit funds only through a CEX
    direction: str = "inbound"   # inbound (received from) / outbound (sent to)


@dataclass
class Disposition:
    decision: str
    priority: str
    risk: float
    reason: str
    components: dict

    def as_row(self) -> dict:
        return {"decision": self.decision, "priority": self.priority,
                "risk": round(self.risk, 4), "reason": self.reason}


def score_address(a: AddressAlert, config: Config = Config()) -> Disposition:
    sev = CATEGORY_SEVERITY.get(a.top_category, 0.30)
    risk = clamp(a.exposure)  # exposure already encodes severity x decay^hops x fraction
    components = {
        "top_category": a.top_category, "category_severity": sev,
        "exposure": round(a.exposure, 4), "hops": a.hops,
        "amount_fraction": round(a.amount_fraction, 4), "via_breaker": a.via_breaker,
        "direction": a.direction,
    }

    # ---- named clear causes first; risk only ranks what survives ----
    if sev <= 0.0:
        return Disposition("AUTO_CLEAR", "", risk,
                           f"Exposure is to a benign category ({a.top_category}); not "
                           "illicit.", components)
    if a.via_breaker:
        return Disposition("AUTO_CLEAR", "", risk,
                           "Illicit funds reach the address only through a commingling "
                           "service; attribution is broken downstream.", components)
    if a.amount_fraction < config.deminimis_fraction:
        return Disposition("AUTO_CLEAR", "", risk,
                           f"De-minimis traceable value ({a.amount_fraction:.1%} of "
                           "volume); below materiality.", components)
    if a.hops is None or a.hops > config.max_actionable_hops or a.exposure < config.dilution_floor:
        h = "no traceable path" if a.hops is None else f"{a.hops} hops, exposure {a.exposure:.3f}"
        return Disposition("AUTO_CLEAR", "", risk,
                           f"Illicit source too remote ({h}); exposure decayed below an "
                           "actionable level.", components)

    # material, proximate, unbroken exposure -> keep open
    if a.exposure >= config.escalate_floor:
        return Disposition("ESCALATE", "", risk,
                           f"Material {a.direction} exposure to {a.top_category} "
                           f"({a.hops} hops, {a.amount_fraction:.0%} of volume); route for "
                           "investigation / SAR or freeze decision.", components)
    if risk >= config.review_high:
        prio = "HIGH"
    elif risk >= config.review_medium:
        prio = "MEDIUM"
    else:
        prio = "LOW"
    return Disposition("ANALYST_REVIEW", prio, risk,
                       f"Exposure to {a.top_category} ({a.hops} hops) below the "
                       "escalation level but not clearable — manual review.", components)


if __name__ == "__main__":
    import json
    from _lib.graph import address_exposure
    # demonstrate composing the graph layer with the disposition engine
    edges = [("SEED", "n1", 0.9), ("n1", "TGT", 0.9)]            # 2-hop from a mixer
    ex = address_exposure(edges, {"SEED": CATEGORY_SEVERITY["mixer"]}, "TGT")
    alert = AddressAlert("0xTGT", "mixer", ex["exposure"], ex["hops"],
                         amount_fraction=0.81, via_breaker=ex["via_breaker"])
    print(json.dumps(score_address(alert).as_row(), indent=2))
