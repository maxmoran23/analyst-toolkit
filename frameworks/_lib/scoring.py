"""
Weighted-composite scoring, tier banding, and monotonicity checking for
risk-rating models. Pure standard library.

A risk rating is a different kind of model from a triage classifier: its output is
a continuous score and an ordinal tier, and the properties that matter are
monotonicity (more risk never lowers the score), banding stability, and respect for
mandatory floors. These helpers express those mechanics once so a rating engine
(customer risk rating now, others later) reads cleanly and is validated the same way.
"""
from __future__ import annotations


def weighted_composite(factor_scores: dict, weights: dict) -> float:
    """Weighted average of per-factor sub-scores (each on a common 0-100 scale).
    Weights need not sum to 1 — they are normalized — so a reviewer can read each
    weight as a relative importance. Missing factors contribute 0."""
    total_w = sum(weights.values())
    if total_w <= 0:
        return 0.0
    return sum(factor_scores.get(f, 0.0) * w for f, w in weights.items()) / total_w


def band(score: float, thresholds, labels) -> str:
    """Map a score to an ordinal label. `thresholds` ascending, len(labels) ==
    len(thresholds) + 1. e.g. band(50, [34, 67], ["LOW","MEDIUM","HIGH"]) -> MEDIUM
    (34 <= 50 < 67)."""
    for i, t in enumerate(thresholds):
        if score < t:
            return labels[i]
    return labels[-1]


def tier_max(a: str, b: str, order) -> str:
    """The higher of two ordinal tiers, per `order` (ascending). Used to apply a
    floor: a rule can only raise a tier, never lower it."""
    return a if order.index(a) >= order.index(b) else b


def check_monotonic(score_fn, base_features: dict, factor: str, ascending_values):
    """Property test: vary one factor over an ascending sequence of values (all
    other features held at `base_features`) and confirm the score never decreases.
    `score_fn` takes a feature dict and returns a float. Returns (ok, detail)."""
    prev = None
    for v in ascending_values:
        feats = dict(base_features)
        feats[factor] = v
        s = score_fn(feats)
        if prev is not None and s < prev - 1e-9:
            return False, f"{factor}: score fell from {prev:.2f} to {s:.2f} at value {v!r}"
        prev = s
    return True, None
