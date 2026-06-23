"""
Content-relevance scoring for adverse-media screening.

A media hit can be a false positive two ways. The first — the article is about a
different person with the same name — is the entity-resolution problem solved by
`match` / `text_normalize` and reused as-is. This module handles the second: the
article is about the subject but is not materially adverse. Relevance is a function
of the adverse CATEGORY, the subject's ROLE in the story (perpetrator vs victim vs
passing mention), and RECENCY. Pure standard library.

The category severities and role weights are illustrative starting points; a
deployment calibrates them against its risk appetite and its media-classification
taxonomy.
"""
from __future__ import annotations

# Adverse-category base severity in [0,1]. non_adverse is the "this article is not
# negative news" class (a press release, a routine filing, a positive mention).
ADVERSE_SEVERITY = {
    "terrorism_financing": 1.00,
    "trafficking": 0.95,
    "sanctions_evasion": 1.00,
    "money_laundering": 0.92,
    "organized_crime": 0.90,
    "fraud": 0.85,
    "corruption_bribery": 0.85,
    "tax_evasion": 0.70,
    "regulatory_enforcement": 0.60,
    "litigation_civil": 0.40,
    "negative_general": 0.30,
    "non_adverse": 0.00,
}

# How the subject figures in the story. Only a perpetrator/alleged role carries
# real financial-crime risk for the subject; a victim or passing mention does not.
ROLE_WEIGHT = {
    "perpetrator": 1.00,
    "alleged": 0.85,
    "associate": 0.55,
    "unknown": 0.50,
    "victim": 0.20,
    "mentioned": 0.15,
}

LOW_ROLES = frozenset({"victim", "mentioned"})


def category_severity(category: str) -> float:
    return ADVERSE_SEVERITY.get(category, 0.30)


def is_non_adverse(category: str) -> bool:
    return category_severity(category) <= 0.0


def is_low_role(role: str) -> bool:
    """Roles that carry no perpetrator risk for the subject (victim / passing
    mention). A genuine adverse-media true positive is a perpetrator or alleged
    role, so clearing these can never drop a true positive."""
    return role in LOW_ROLES


def recency_decay(age_days: float, halflife_days: float = 1095.0) -> float:
    """Exponential recency weight in (0,1]; defaults to a ~3-year half-life. Recent
    news weighs ~1.0; a 6-year-old item weighs ~0.25."""
    if age_days <= 0:
        return 1.0
    return 0.5 ** (age_days / halflife_days)


def relevance_score(category: str, role: str, age_days: float,
                    source_reliability: float = 1.0,
                    halflife_days: float = 1095.0) -> float:
    """Combined materiality of an adverse-media hit in [0,1]: how serious, how
    centrally the subject is implicated, and how recent — scaled by source
    reliability."""
    return (category_severity(category)
            * ROLE_WEIGHT.get(role, 0.5)
            * recency_decay(age_days, halflife_days)
            * max(0.0, min(1.0, source_reliability)))
