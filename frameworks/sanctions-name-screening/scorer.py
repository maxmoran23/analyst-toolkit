"""
Sanctions name-screening scorer — reference implementation.

Consumes an alert (a payment/customer party that an upstream filter already
matched to a watchlist entry) and returns a disposition with a NAMED rationale
and an auditable component breakdown. The full methodology — every weight,
threshold, and rule — is documented in METHODOLOGY.md; this file is its
executable form.

Design posture (the regulator-defensible default):
  * The engine NEVER auto-blocks and NEVER files. A likely true match is routed
    to a human with the evidence assembled.
  * The engine auto-clears an alert ONLY when it can NAME why it is a false
    positive — one of three provable patterns:
        1. generic-token-only   the match exists solely on common tokens
        2. type-incompatible    e.g. a corporate party matched a designated VESSEL
        3. named-discriminator  a hard identifier (country / DOB / nationality)
                                contradicts the list entry
  * It never clears an alert merely because a model score is low. "Low score,
    no nameable reason" stays in the analyst queue (LOW priority). That is the
    line between prioritization and unjustified clearance.

Everything is deterministic. Same inputs -> same disposition.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field, asdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.match import compare_names, NameMatch  # noqa: E402
from _lib.text_normalize import TokenStats  # noqa: E402

# Entity types. CRYPTO is matched on wallet string, not name, but appears here
# for type-concordance reasoning.
INDIVIDUAL, ENTITY, VESSEL, AIRCRAFT, CRYPTO, UNKNOWN = (
    "INDIVIDUAL", "ENTITY", "VESSEL", "AIRCRAFT", "CRYPTO", "UNKNOWN")

# Which type pairs are structurally INCOMPATIBLE — a match across them is, on its
# face, a false positive. (An individual is not a vessel; a vessel is not a
# company.) Same-type and any-UNKNOWN pairings are NOT listed here.
_INCOMPATIBLE = {
    frozenset({INDIVIDUAL, VESSEL}),
    frozenset({INDIVIDUAL, AIRCRAFT}),
    frozenset({INDIVIDUAL, ENTITY}),
    frozenset({INDIVIDUAL, CRYPTO}),
    frozenset({ENTITY, VESSEL}),
    frozenset({ENTITY, AIRCRAFT}),
    frozenset({ENTITY, CRYPTO}),
    frozenset({VESSEL, AIRCRAFT}),
    frozenset({VESSEL, CRYPTO}),
    frozenset({AIRCRAFT, CRYPTO}),
}

# Identifier fields, split by discriminating power. A STRONG identifier match is
# near-conclusive corroboration; a STRONG identifier MISMATCH is a clearing
# discriminator. WEAK fields corroborate/discriminate only in combination.
_STRONG_IDS = ("dob", "passport", "national_id", "registration", "imo",
               "tail_number", "wallet")
_WEAK_IDS = ("nationality", "country", "place_of_birth")


@dataclass
class Config:
    """Tunable operating point. Defaults are the conservative posture; recalibrate
    against a real labelled sample before production use (see tuning.md)."""
    generic_max_share: float = 0.005     # df-share above which a token is 'generic'
    escalate_name_floor: float = 0.60    # min name_score to escalate w/ strong IDs
    near_exact_name: float = 0.95        # name_score that cannot be auto-cleared
    review_high: float = 0.50            # match_likelihood -> HIGH analyst priority
    review_medium: float = 0.25          # match_likelihood -> MEDIUM


@dataclass
class Party:
    """The payment / customer party that triggered the alert."""
    name: str
    entity_type: str = UNKNOWN
    ids: dict = field(default_factory=dict)


@dataclass
class WatchlistEntry:
    uid: str
    name: str
    entity_type: str
    program: str = ""
    aliases: list = field(default_factory=list)
    ids: dict = field(default_factory=dict)


@dataclass
class Disposition:
    decision: str            # AUTO_CLEAR / ANALYST_REVIEW / ESCALATE
    priority: str            # HIGH / MEDIUM / LOW for ANALYST_REVIEW, else ""
    match_likelihood: float  # [0,1], used for ranking and threshold calibration
    reason: str              # the NAMED rationale (audit trail)
    components: dict         # full breakdown for review

    def as_row(self) -> dict:
        return {
            "decision": self.decision,
            "priority": self.priority,
            "match_likelihood": round(self.match_likelihood, 4),
            "reason": self.reason,
        }


def _type_concordance(a: str, b: str) -> float:
    if a == UNKNOWN or b == UNKNOWN:
        return 0.7  # cannot penalize on a missing type
    if a == b:
        return 1.0
    if frozenset({a, b}) in _INCOMPATIBLE:
        return 0.0
    return 0.5


def _best_name_match(party_name: str, entry: WatchlistEntry, stats: TokenStats,
                     generic_max_share: float = 0.005) -> NameMatch:
    """Compare the party name to the entry's primary name and every alias; keep
    the strongest. Sanctions entries carry strong and weak aliases and a real
    match may align with an alias rather than the primary name."""
    best = compare_names(party_name, entry.name, stats, generic_max_share)
    for alias in entry.aliases:
        cand = compare_names(party_name, alias, stats, generic_max_share)
        if cand.weighted_overlap > best.weighted_overlap:
            best = cand
    return best


def _identifier_assessment(party: Party, entry: WatchlistEntry):
    """Return (corroboration, discriminator) where corroboration is NONE/PARTIAL/
    STRONG and discriminator is None or a 'field: a != b' string naming the first
    contradicting hard identifier."""
    strong_hits = weak_hits = 0
    discriminator = None
    for fld in _STRONG_IDS:
        pv, ev = party.ids.get(fld), entry.ids.get(fld)
        if pv and ev:
            if str(pv).strip().upper() == str(ev).strip().upper():
                strong_hits += 1
            elif discriminator is None:
                discriminator = f"{fld}: {pv} != {ev}"
    for fld in _WEAK_IDS:
        pv, ev = party.ids.get(fld), entry.ids.get(fld)
        if pv and ev:
            if str(pv).strip().upper() == str(ev).strip().upper():
                weak_hits += 1
            elif discriminator is None and strong_hits == 0:
                discriminator = f"{fld}: {pv} != {ev}"
    if strong_hits >= 1 or weak_hits >= 2:
        corroboration = "STRONG"
    elif weak_hits == 1:
        corroboration = "PARTIAL"
    else:
        corroboration = "NONE"
    return corroboration, discriminator


def score_candidate(party: Party, entry: WatchlistEntry, stats: TokenStats,
                    config: Config = Config()) -> Disposition:
    """Disposition one alert (party x entry). See module docstring for posture."""
    nm = _best_name_match(party.name, entry, stats, config.generic_max_share)
    type_score = _type_concordance(party.entity_type, entry.entity_type)
    corroboration, discriminator = _identifier_assessment(party, entry)

    # name_score rewards matching BOTH the query's and the entry's informative
    # mass: a single incidental token of a long entry name is penalized on
    # coverage even if it is the party's whole name.
    name_score = nm.weighted_overlap * (0.4 + 0.6 * nm.coverage)

    # ---- match_likelihood: continuous score for ranking + calibration ----
    base = name_score * type_score
    if nm.only_generic:
        base = min(base, 0.05)
    if type_score == 0.0:
        base = min(base, 0.05)
    if discriminator and name_score < config.near_exact_name:
        base = min(base, 0.05)
    elif corroboration == "STRONG":
        base = base + (1 - base) * 0.40
    elif corroboration == "PARTIAL":
        base = base + (1 - base) * 0.15
    match_likelihood = max(0.0, min(1.0, base))

    components = {
        "name_score": round(name_score, 4),
        "weighted_overlap": round(nm.weighted_overlap, 4),
        "coverage": round(nm.coverage, 4),
        "char_sim": round(nm.char_sim, 4),
        "matched_tokens": nm.matched_tokens,
        "only_generic": nm.only_generic,
        "type_score": type_score,
        "corroboration": corroboration,
        "discriminator": discriminator,
        "entry_has_distinctive": nm.entry_has_distinctive,
    }

    # ---- disposition: categorical NAMED rules first, thresholds second ----
    # Auto-clear requires a nameable false-positive cause. Order matters: the
    # most defensible discriminator wins the reason line.
    #
    # Generic-token-only clear is gated on the entry HAVING a distinctive token
    # the party failed to match. If the designated entity's own name is entirely
    # generic, it cannot be ruled out by name — so it is NOT auto-cleared (it
    # routes to a human). This is what makes false-negative safety structural: a
    # true match's distinctive token aligns, so it never reaches this branch.
    if nm.only_generic and nm.entry_has_distinctive:
        toks = ", ".join(nm.matched_tokens) or "no informative tokens"
        missed = ", ".join(nm.entry_unmatched_distinctive) or "n/a"
        return Disposition("AUTO_CLEAR", "", match_likelihood,
                           f"Generic-token-only match ({toks}); the designated "
                           f"party's distinctive token(s) [{missed}] were not "
                           f"matched.", components)
    if type_score == 0.0:
        return Disposition("AUTO_CLEAR", "", match_likelihood,
                           f"Entity-type incompatible: party is {party.entity_type}, "
                           f"list entry is {entry.entity_type}.", components)
    if discriminator and name_score < config.near_exact_name:
        return Disposition("AUTO_CLEAR", "", match_likelihood,
                           f"Discriminating identifier contradicts the list entry "
                           f"({discriminator}).", components)

    # Not auto-clearable -> keep open. Escalate only with strong corroboration.
    if corroboration == "STRONG" and name_score >= config.escalate_name_floor:
        return Disposition("ESCALATE", "", match_likelihood,
                           f"Name aligns ({name_score:.2f}) and a hard identifier "
                           f"corroborates; likely true match — route to compliance "
                           f"officer.", components)

    if name_score >= config.review_high or match_likelihood >= config.review_high:
        prio = "HIGH"
    elif match_likelihood >= config.review_medium:
        prio = "MEDIUM"
    else:
        prio = "LOW"
    why = "Distinctive name overlap with insufficient identifier evidence to " \
          "confirm or clear" if not discriminator else \
          "Identifier conflict against a strong name match — manual reconciliation"
    return Disposition("ANALYST_REVIEW", prio, match_likelihood, why + ".", components)


# Convenience for ad-hoc CLI use: python scorer.py "ACME CAPITAL" ENTITY
if __name__ == "__main__":
    import json
    demo_list = [
        WatchlistEntry("OFAC-0001", "VENEZUELA CAPITAL HOLDINGS", ENTITY,
                       program="VENEZUELA", ids={"country": "VE"}),
        WatchlistEntry("OFAC-0002", "ROSOBORONEXPORT", ENTITY, program="RUSSIA-EO13662",
                       aliases=["ROSOBORON EXPORT"], ids={"country": "RU"}),
    ]
    stats = TokenStats.from_names([e.name for e in demo_list] +
                                  ["CAPITAL TRADING %d" % i for i in range(300)])
    name = sys.argv[1] if len(sys.argv) > 1 else "ACME CAPITAL PARTNERS"
    etype = sys.argv[2] if len(sys.argv) > 2 else ENTITY
    p = Party(name=name, entity_type=etype, ids={"country": "US"})
    for e in demo_list:
        d = score_candidate(p, e, stats)
        print(f"\nvs {e.name} [{e.uid}]")
        print(json.dumps({**d.as_row(), "components": d.components}, indent=2))
