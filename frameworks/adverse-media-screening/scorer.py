"""
Adverse-media screening scorer — reference implementation.

Consumes a media hit (a news item a screening tool surfaced because its subject name
matched a customer) and dispositions it with a NAMED rationale. The full methodology
is in METHODOLOGY.md; this file is its executable form.

A media hit is a false positive two independent ways, and the engine names which:
  wrong_entity     the article is about a DIFFERENT party with a similar name
                   (the sanctions name-collision problem; reuses _lib.match)
  not_adverse      the article is about the subject but is not negative news
  low_role         the subject appears as a victim or passing mention, not a
                   perpetrator
  stale_immaterial old news in a minor category, below materiality

Design posture (same conservative stance as the other frameworks):
  * Auto-clears only on a named, provable cause; never on a low score alone.
  * Never auto-clears a hit that is a strong entity match AND materially adverse
    with the subject as perpetrator — a true positive cannot satisfy any of the
    four clear causes, so false-negative safety is structural.
  * Escalates a confirmed match on serious recent adverse content for enhanced
    review; it does not itself make an exit / SAR / EDD decision.

Deterministic. Same inputs -> same disposition.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.match import compare_names  # noqa: E402
from _lib.relevance import (relevance_score, category_severity, is_non_adverse,  # noqa: E402
                            is_low_role)

_STRONG_IDS = ("dob", "passport", "national_id", "registration")
_WEAK_IDS = ("nationality", "country", "place_of_birth")


@dataclass
class Config:
    generic_max_share: float = 0.005
    near_exact_name: float = 0.95
    match_floor: float = 0.55         # entity strength to escalate
    escalate_relevance: float = 0.50  # relevance to escalate
    stale_days: float = 1825.0        # > 5 years
    immaterial_max_severity: float = 0.45  # categories clearable when stale
    review_high: float = 0.40
    review_medium: float = 0.18


@dataclass
class Subject:
    name: str
    entity_type: str = "INDIVIDUAL"
    ids: dict = field(default_factory=dict)


@dataclass
class MediaHit:
    hit_id: str
    article_name: str            # the name as it appears in the article
    category: str                # adverse category (per the media classifier)
    role: str                    # perpetrator / alleged / associate / victim / mentioned
    age_days: float = 0.0
    article_ids: dict = field(default_factory=dict)
    source_reliability: float = 1.0


@dataclass
class Disposition:
    decision: str            # AUTO_CLEAR / ANALYST_REVIEW / ESCALATE
    priority: str
    relevance: float         # [0,1] content materiality
    entity_strength: float   # [0,1] confidence the hit is about the subject
    combined: float          # entity_strength * relevance, for ranking
    reason: str
    components: dict

    def as_row(self) -> dict:
        return {"decision": self.decision, "priority": self.priority,
                "entity_strength": round(self.entity_strength, 4),
                "relevance": round(self.relevance, 4), "combined": round(self.combined, 4),
                "reason": self.reason}


def _identifier_check(subject_ids, article_ids):
    """Compare subject and article identifiers. Returns (corroborated, strong_disc,
    weak_disc). A STRONG discriminator (a contradicting DOB / passport / national-id
    / registration) conclusively proves a different party; a WEAK discriminator
    (country / nationality) only does so when the name is not an exact match.
    Article identifiers are often sparse."""
    corroborated = False
    strong_disc = weak_disc = None
    for fld in _STRONG_IDS:
        sv, av = subject_ids.get(fld), article_ids.get(fld)
        if sv and av:
            if str(sv).strip().upper() == str(av).strip().upper():
                corroborated = True
            elif strong_disc is None:
                strong_disc = f"{fld}: {sv} != {av}"
    for fld in _WEAK_IDS:
        sv, av = subject_ids.get(fld), article_ids.get(fld)
        if sv and av:
            if str(sv).strip().upper() == str(av).strip().upper():
                corroborated = True
            elif weak_disc is None:
                weak_disc = f"{fld}: {sv} != {av}"
    return corroborated, strong_disc, weak_disc


def score_hit(subject: Subject, hit: MediaHit, stats, config: Config = Config()) -> Disposition:
    nm = compare_names(subject.name, hit.article_name, stats, config.generic_max_share)
    name_score = nm.weighted_overlap * (0.4 + 0.6 * nm.coverage)
    corroborated, strong_disc, weak_disc = _identifier_check(subject.ids, hit.article_ids)
    discriminator = strong_disc or weak_disc

    entity_strength = name_score
    if corroborated:
        entity_strength = entity_strength + (1 - entity_strength) * 0.4
    # a match on a common name alone, with no corroborating identifier, is only
    # moderate confidence — it could be a different person of the same name.
    if nm.only_generic and not corroborated:
        entity_strength = min(entity_strength, 0.5)

    # wrong-entity clear only on positive proof of a different party: a contradicting
    # strong identifier (even against an exact name), a contradicting weak identifier
    # against a non-exact name, or essentially no name overlap. A bare common-name
    # match with no identifier is NOT cleared — it goes to review.
    no_name_match = name_score < 0.15
    wrong_entity = (no_name_match or strong_disc is not None
                    or (weak_disc is not None and name_score < config.near_exact_name))
    if wrong_entity:
        entity_strength = min(entity_strength, 0.1)

    rel = relevance_score(hit.category, hit.role, hit.age_days, hit.source_reliability)
    combined = entity_strength * rel

    components = {
        "name_score": round(name_score, 4),
        "only_generic": nm.only_generic,
        "matched_tokens": nm.matched_tokens,
        "discriminator": discriminator,
        "corroborated": corroborated,
        "category": hit.category, "category_severity": category_severity(hit.category),
        "role": hit.role, "age_days": hit.age_days,
    }

    # ---- disposition: named clear causes first; combined score only ranks ----
    if wrong_entity:
        if no_name_match:
            why = "the article subject's name does not materially match the customer"
        elif strong_disc:
            why = f"a strong identifier contradicts ({strong_disc})"
        else:
            why = f"an identifier contradicts on a non-exact name ({weak_disc})"
        return Disposition("AUTO_CLEAR", "", rel, entity_strength, combined,
                           f"Different party — {why}; the article is not about this customer.",
                           components)
    if is_non_adverse(hit.category):
        return Disposition("AUTO_CLEAR", "", rel, entity_strength, combined,
                           "Article is not adverse (non-negative category); no "
                           "financial-crime relevance.", components)
    if is_low_role(hit.role):
        return Disposition("AUTO_CLEAR", "", rel, entity_strength, combined,
                           f"Subject appears as '{hit.role}', not as a perpetrator; "
                           "no adverse-conduct risk to this customer.", components)
    if hit.age_days > config.stale_days and category_severity(hit.category) <= config.immaterial_max_severity:
        return Disposition("AUTO_CLEAR", "", rel, entity_strength, combined,
                           f"Stale ({hit.age_days/365:.0f}+ years) and below materiality "
                           f"({hit.category}); not actionable.", components)

    # kept open
    if entity_strength >= config.match_floor and rel >= config.escalate_relevance:
        return Disposition("ESCALATE", "", rel, entity_strength, combined,
                           f"Confirmed match on material adverse content "
                           f"({hit.category}, {hit.role}); route for enhanced review.",
                           components)
    if combined >= config.review_high:
        prio = "HIGH"
    elif combined >= config.review_medium:
        prio = "MEDIUM"
    else:
        prio = "LOW"
    return Disposition("ANALYST_REVIEW", prio, rel, entity_strength, combined,
                       "Plausible match on adverse content with insufficient "
                       "confidence to confirm or clear — manual review.", components)


if __name__ == "__main__":
    import json
    from _lib.text_normalize import TokenStats
    corpus = ["JOHN SMITH"] * 40 + ["MARIA GARCIA"] * 30 + ["DMITRI VOLKOVSKY", "ACME LOGISTICS"]
    stats = TokenStats.from_names(corpus)
    subj = Subject("DMITRI VOLKOVSKY", "INDIVIDUAL", {"country": "RU", "dob": "1970-01-01"})
    hits = [
        MediaHit("h1", "DMITRI VOLKOVSKY", "money_laundering", "perpetrator", age_days=60,
                 article_ids={"country": "RU"}),
        MediaHit("h2", "JOHN SMITH", "fraud", "perpetrator", age_days=30),  # wrong entity
        MediaHit("h3", "DMITRI VOLKOVSKY", "non_adverse", "mentioned", age_days=10),
    ]
    for h in hits:
        d = score_hit(subj, h, stats)
        print(f"\n{h.hit_id} ({h.article_name} / {h.category}/{h.role}):")
        print(json.dumps(d.as_row(), indent=2))
