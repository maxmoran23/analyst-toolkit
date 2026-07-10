"""
PEP screening scorer — reference implementation.

Consumes an alert (a customer an upstream screening filter matched to a
politically-exposed-person list entry) and dispositions it with a NAMED
rationale. The full methodology — every tier weight, decay horizon, and rule —
is documented in METHODOLOGY.md; this file is its executable form.

A PEP alert is a false positive on two independent axes, and the engine names
which:
  wrong_party         the customer is a DIFFERENT person who shares a name with
                      the list entry (the common-name / transliteration problem;
                      reuses _lib.match)
  generic_token_only  the match exists solely on common name tokens while the
                      entry's distinctive token went unmatched
  out_of_scope_status a former low-prominence official far past the documented
                      step-down horizon with no adverse indicator — even if it
                      IS the person, the entry carries no current PEP risk

Design posture (same conservative stance as the other frameworks):
  * Auto-clears only on a named, provable cause; never on a low score alone.
  * NEVER auto-clears: any current PEP match, any TIER_1/TIER_2 match (once
    senior, materiality is lowered but never zero), or any match with a
    corroborated identifier — those always reach a human.
  * A common-name match with no corroborating identifier is capped at moderate
    confidence and routed to review; it can be neither cleared nor confirmed.
  * Escalates a corroborated match on a materially exposed entry for enhanced
    review; the engine never approves, blocks, or closes a relationship itself.

Deterministic. Same inputs -> same disposition.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.match import compare_names, NameMatch  # noqa: E402
from _lib.text_normalize import TokenStats  # noqa: E402

# Prominence tiers. RCA = relative or close associate of a principal PEP; it
# inherits a fraction of the principal's tier weight and decays faster.
TIER_1, TIER_2, TIER_3, RCA = "TIER_1", "TIER_2", "TIER_3", "RCA"
CURRENT, FORMER = "CURRENT", "FORMER"

# ---- Axis B constants (prominence x status x jurisdiction) -----------------
TIER_WEIGHT = {TIER_1: 1.00, TIER_2: 0.80, TIER_3: 0.55}
RCA_FRACTION = 0.60          # an RCA inherits this fraction of the principal's tier weight
SENIOR_DECAY_YEARS = 10.0    # window over which a former TIER_1/TIER_2 decays toward its floor
TIER1_FLOOR = 0.40           # a former head of state never decays below this — "once senior,
TIER2_FLOOR = 0.15           #  lower but never zero"; same idea, lower floor, for TIER_2
TIER3_HORIZON_YEARS = 5.0    # documented step-down horizon; a former TIER_3 fully decays past it
RCA_HORIZON_FACTOR = 0.5     # RCA horizon = half the principal-tier horizon (RCA decays faster)
ADVERSE_DECAY_FLOOR = 0.5    # a documented adverse indicator suspends step-down at this floor

# ILLUSTRATIVE corruption-risk bucket weights. The bucket assignment
# (country -> HIGH/MEDIUM/LOW) is upstream configuration and moves as public
# indices move; the engine consumes the bucket, not a country table. An
# unknown bucket defaults to the conservative HIGH weight.
JURISDICTION_WEIGHT = {"HIGH": 1.00, "MEDIUM": 0.75, "LOW": 0.55}


@dataclass
class Config:
    """Tunable operating point. Defaults are the conservative posture;
    recalibrate against a real labelled sample before production use (tuning.md)."""
    generic_max_share: float = 0.005   # df-share above which a name token is 'generic'
    no_name_match: float = 0.15        # name_score below which no material name match exists
    common_name_cap: float = 0.50      # strength ceiling for an uncorroborated common-name match
    escalate_strength: float = 0.60    # min match_strength to escalate
    escalate_materiality: float = 0.40 # min materiality to escalate
    review_high: float = 0.35          # combined -> HIGH analyst priority
    review_medium: float = 0.15        # combined -> MEDIUM


@dataclass
class Customer:
    """The screened customer that triggered the alert. KYC records are often
    identifier-sparse relative to the list entry."""
    name: str
    dob: str = ""
    nationality: str = ""


@dataclass
class PepEntry:
    """A politically-exposed-person list entry (all entries here are fictional)."""
    pep_id: str
    name: str
    tier: str                     # TIER_1 / TIER_2 / TIER_3 / RCA
    position: str = ""
    country: str = ""             # country of the position held
    jurisdiction_risk: str = ""   # HIGH / MEDIUM / LOW corruption-risk bucket (ILLUSTRATIVE)
    status: str = CURRENT         # CURRENT / FORMER
    years_since_left: float = 0.0
    principal_tier: str = ""      # for RCA entries: the principal's tier
    adverse_flag: bool = False    # a documented adverse indicator on the entry
    dob: str = ""
    aliases: list = field(default_factory=list)


@dataclass
class Disposition:
    decision: str            # AUTO_CLEAR / ANALYST_REVIEW / ESCALATE_ENHANCED_REVIEW
    priority: str            # HIGH / MEDIUM / LOW for ANALYST_REVIEW, else ""
    match_strength: float    # [0,1] confidence the customer is the listed person (Axis A)
    materiality: float       # [0,1] how much PEP risk the entry itself carries (Axis B)
    combined: float          # match_strength * materiality, for ranking
    reason: str              # the NAMED rationale (audit trail)
    components: dict         # full breakdown for review

    def as_row(self) -> dict:
        return {"decision": self.decision, "priority": self.priority,
                "match_strength": round(self.match_strength, 4),
                "materiality": round(self.materiality, 4),
                "combined": round(self.combined, 4), "reason": self.reason}


# --------------------------------------------------------------------------- #
# Axis B — PEP materiality: prominence tier x status decay x jurisdiction
# --------------------------------------------------------------------------- #
def tier_weight(tier: str, principal_tier: str = "") -> float:
    """Prominence weight. An RCA inherits RCA_FRACTION of the principal's tier
    weight (an unstated principal tier is treated as TIER_3, the floor)."""
    if tier == RCA:
        return RCA_FRACTION * TIER_WEIGHT.get(principal_tier or TIER_3, TIER_WEIGHT[TIER_3])
    return TIER_WEIGHT[tier]


def step_down_horizon(tier: str, principal_tier: str = "") -> float | None:
    """Years after leaving office at which a FORMER entry falls out of scope.
    Only TIER_3 and RCA have a horizon; TIER_1/TIER_2 return None — a formerly
    senior official is never status-cleared. RCA decays faster: half the
    principal-tier horizon (the senior decay window for TIER_1/TIER_2
    principals, the TIER_3 horizon otherwise)."""
    if tier == TIER_3:
        return TIER3_HORIZON_YEARS
    if tier == RCA:
        base = SENIOR_DECAY_YEARS if principal_tier in (TIER_1, TIER_2) else TIER3_HORIZON_YEARS
        return RCA_HORIZON_FACTOR * base
    return None


def status_decay(tier: str, status: str, years_since_left: float,
                 principal_tier: str = "") -> float:
    """Status multiplier in [0,1]. CURRENT is always 1.0. FORMER decays linearly:
    TIER_1/TIER_2 toward a non-zero floor over SENIOR_DECAY_YEARS ("once senior,
    lower but never zero"); TIER_3/RCA to zero at their documented horizon."""
    if status == CURRENT:
        return 1.0
    y = max(0.0, years_since_left)
    if tier == TIER_1:
        return max(TIER1_FLOOR, 1.0 - y / SENIOR_DECAY_YEARS)
    if tier == TIER_2:
        return max(TIER2_FLOOR, 1.0 - y / SENIOR_DECAY_YEARS)
    horizon = step_down_horizon(tier, principal_tier)
    return max(0.0, 1.0 - y / horizon)


def pep_materiality(entry: PepEntry) -> tuple[float, dict]:
    """Axis B: materiality = tier_weight x status_decay x jurisdiction_weight.
    A documented adverse indicator suspends step-down (decay floored at
    ADVERSE_DECAY_FLOOR): time out of office does not de-risk an entry that
    carries live adverse information."""
    tw = tier_weight(entry.tier, entry.principal_tier)
    decay = status_decay(entry.tier, entry.status, entry.years_since_left,
                         entry.principal_tier)
    if entry.adverse_flag:
        decay = max(decay, ADVERSE_DECAY_FLOOR)
    jw = JURISDICTION_WEIGHT.get(entry.jurisdiction_risk, JURISDICTION_WEIGHT["HIGH"])
    mat = tw * decay * jw
    return mat, {"tier": entry.tier, "tier_weight": round(tw, 4),
                 "status": entry.status, "years_since_left": entry.years_since_left,
                 "status_decay": round(decay, 4),
                 "jurisdiction_risk": entry.jurisdiction_risk or "UNKNOWN",
                 "jurisdiction_weight": jw, "adverse_flag": entry.adverse_flag}


# --------------------------------------------------------------------------- #
# Axis A — entity resolution: name match + identifier corroboration
# --------------------------------------------------------------------------- #
def _best_name_match(customer_name: str, entry: PepEntry, stats: TokenStats,
                     generic_max_share: float) -> NameMatch:
    """Compare the customer name to the entry's primary name and every alias;
    keep the strongest. PEP-list entries carry transliteration AKAs and a real
    match may align with an alias rather than the primary name."""
    best = compare_names(customer_name, entry.name, stats, generic_max_share)
    for alias in entry.aliases:
        cand = compare_names(customer_name, alias, stats, generic_max_share)
        if cand.weighted_overlap > best.weighted_overlap:
            best = cand
    return best


def _identifier_check(customer: Customer, entry: PepEntry):
    """Compare the customer's identifiers to the list entry's. DOB is the strong
    field; nationality vs the entry's position country is the weak one. Returns
    (corroboration, dob_mismatch, nationality_mismatch) where corroboration is
    STRONG (DOB matches) / WEAK (nationality matches) / NONE. KYC and list
    records are both sparse, so absent fields assert nothing."""
    corroboration = "NONE"
    dob_mismatch = nationality_mismatch = False
    if customer.dob and entry.dob:
        if customer.dob.strip() == entry.dob.strip():
            corroboration = "STRONG"
        else:
            dob_mismatch = True
    if customer.nationality and entry.country:
        if customer.nationality.strip().upper() == entry.country.strip().upper():
            if corroboration != "STRONG":
                corroboration = "WEAK"
        else:
            nationality_mismatch = True
    return corroboration, dob_mismatch, nationality_mismatch


# --------------------------------------------------------------------------- #
# Disposition
# --------------------------------------------------------------------------- #
def score_alert(customer: Customer, entry: PepEntry, stats: TokenStats,
                config: Config = Config()) -> Disposition:
    """Disposition one alert (customer x PEP-list entry). See module docstring."""
    nm = _best_name_match(customer.name, entry, stats, config.generic_max_share)
    name_score = nm.weighted_overlap * (0.4 + 0.6 * nm.coverage)
    corroboration, dob_mismatch, nationality_mismatch = _identifier_check(customer, entry)

    # wrong-party proof requires BOTH identifiers to contradict — a single
    # conflicting field against a matching name is a reconciliation, not a
    # clearance. (The zero-name-overlap form is rule 3 below.)
    wrong_party_ids = dob_mismatch and nationality_mismatch

    # ---- Axis A: match strength -------------------------------------------
    strength = name_score
    if corroboration == "STRONG":
        strength = strength + (1 - strength) * 0.40
    elif corroboration == "WEAK":
        strength = strength + (1 - strength) * 0.15
    # a match on a common name alone, with no strong corroborating identifier,
    # is only moderate confidence — thousands of people share it.
    if nm.only_generic and corroboration != "STRONG":
        strength = min(strength, config.common_name_cap)
    if wrong_party_ids or name_score < config.no_name_match:
        strength = min(strength, 0.05)
    strength = max(0.0, min(1.0, strength))

    # ---- Axis B: PEP materiality ------------------------------------------
    mat, mat_components = pep_materiality(entry)
    combined = strength * mat
    horizon = step_down_horizon(entry.tier, entry.principal_tier)

    components = {
        "name_score": round(name_score, 4),
        "only_generic": nm.only_generic,
        "matched_tokens": nm.matched_tokens,
        "corroboration": corroboration,
        "dob_mismatch": dob_mismatch,
        "nationality_mismatch": nationality_mismatch,
        **mat_components,
    }

    # ---- disposition: named clear causes first; combined score only ranks ----
    # 1. wrong_party (identifier proof). Both hard fields contradict — this
    #    clears even an exact name, because two independent contradictions
    #    prove a different person.
    if wrong_party_ids:
        return Disposition(
            "AUTO_CLEAR", "", strength, mat, combined,
            f"Wrong party — date of birth ({customer.dob} != {entry.dob}) AND "
            f"nationality ({customer.nationality} != {entry.country}) both "
            f"contradict the list entry; the customer is not the listed person.",
            components)
    # 2. generic_token_only. Every aligned token is common AND the entry's own
    #    distinctive token went unmatched — gated exactly as in the sanctions
    #    framework: an entry whose whole name is common tokens cannot be ruled
    #    out by name and is NOT cleared here. Any corroboration blocks the clear.
    if nm.only_generic and nm.entry_has_distinctive and corroboration == "NONE":
        toks = ", ".join(nm.matched_tokens) or "no informative tokens"
        missed = ", ".join(nm.entry_unmatched_distinctive) or "n/a"
        return Disposition(
            "AUTO_CLEAR", "", strength, mat, combined,
            f"Generic-token-only match ({toks}); the listed person's distinctive "
            f"token(s) [{missed}] were not matched.", components)
    # 3. wrong_party (zero distinctive-token overlap). No material name match
    #    exists at all. Corroborated oddities still go to a human.
    if name_score < config.no_name_match and corroboration == "NONE":
        return Disposition(
            "AUTO_CLEAR", "", strength, mat, combined,
            "Wrong party — the customer's name does not materially match the "
            "list entry (zero distinctive-token overlap).", components)
    # 4. out_of_scope_status. Former TIER_3/RCA beyond the documented step-down
    #    horizon with no adverse indicator. Never fires for CURRENT status, for
    #    TIER_1/TIER_2 (no horizon exists), or when any identifier corroborates —
    #    a corroborated identity match on a list entry always reaches a human.
    if (entry.tier in (TIER_3, RCA) and entry.status == FORMER
            and horizon is not None and entry.years_since_left > horizon
            and not entry.adverse_flag and corroboration == "NONE"):
        return Disposition(
            "AUTO_CLEAR", "", strength, mat, combined,
            f"Out-of-scope status — former {entry.tier} "
            f"({entry.position or 'position'}, left {entry.years_since_left:.0f} "
            f"years ago, past the {horizon:.1f}-year step-down horizon) with no "
            f"adverse indicator; the entry carries no current PEP risk.",
            components)

    # kept open
    if (corroboration == "STRONG" and strength >= config.escalate_strength
            and mat >= config.escalate_materiality):
        return Disposition(
            "ESCALATE_ENHANCED_REVIEW", "", strength, mat, combined,
            f"Corroborated match (DOB) on a materially exposed entry "
            f"({entry.tier}, {entry.status}, {entry.jurisdiction_risk or 'UNKNOWN'} "
            f"jurisdiction); route for enhanced review.", components)

    if combined >= config.review_high:
        prio = "HIGH"
    elif combined >= config.review_medium:
        prio = "MEDIUM"
    else:
        prio = "LOW"
    if entry.adverse_flag:
        why = ("Match on an entry carrying a documented adverse indicator — "
               "status step-down is suspended; manual review.")
    elif nm.only_generic:
        why = ("Common-name match with no identifier evidence to confirm or "
               "clear — manual review.")
    else:
        why = ("Plausible match with insufficient identifier evidence to "
               "confirm or clear — manual review.")
    return Disposition("ANALYST_REVIEW", prio, strength, mat, combined, why, components)


# Convenience for ad-hoc CLI use: python3 scorer.py "DAVID KIM"
if __name__ == "__main__":
    import json
    demo_list = [
        PepEntry("PEP-0001", "DAVID KIM", TIER_2, position="AMBASSADOR",
                 country="KORVANIA", jurisdiction_risk="HIGH", status=CURRENT,
                 dob="1961-04-19"),
        PepEntry("PEP-0002", "TARIQ VOLNEFTAR", TIER_3, position="PROVINCIAL GOVERNOR",
                 country="MERIDONIA", jurisdiction_risk="LOW", status=FORMER,
                 years_since_left=9, dob="1955-08-02"),
    ]
    stats = TokenStats.from_names([e.name for e in demo_list]
                                  + ["DAVID KIM"] * 40 + ["MARIA GARCIA"] * 40)
    name = sys.argv[1] if len(sys.argv) > 1 else "DAVID KIM"
    cust = Customer(name=name, dob="1975-01-30", nationality="SOLVENNIA")
    for e in demo_list:
        d = score_alert(cust, e, stats)
        print(f"\nvs {e.name} [{e.pep_id}] ({e.tier}/{e.status})")
        print(json.dumps({**d.as_row(), "components": d.components}, indent=2, default=str))
