"""
Deviation and window statistics for behavioral scoring.

Where name screening asks "do these strings refer to the same entity?", behavioral
monitoring asks "is this activity abnormal *for this customer*?" — a question with
no meaning without a baseline. These helpers express activity relative to a
reference: the customer's own history (z-score, ratio-to-expected) and the peer
group (percentile rank). Pure standard library; no numpy.
"""
from __future__ import annotations

import math


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    """a / b, returning `default` when b is zero rather than raising."""
    return a / b if b else default


def ratio_to_expected(value: float, expected: float) -> float:
    """How many times the expected level the value is. 1.0 == on profile.
    When no baseline exists (expected == 0) a positive value is maximally
    anomalous; the caller decides how to treat `inf`."""
    if expected:
        return value / expected
    return float("inf") if value > 0 else 1.0


def zscore(value: float, mean: float, std: float) -> float:
    """Standard score against a baseline mean/std. 0 when std is 0 (no spread to
    deviate from)."""
    return safe_div(value - mean, std, 0.0)


def pct_rank(value: float, population) -> float:
    """Fraction of the population at or below `value`, in [0,1]. Empty population
    returns 0.5 (no information)."""
    pop = list(population)
    if not pop:
        return 0.5
    return sum(1 for x in pop if x <= value) / len(pop)


def ewma(series, alpha: float = 0.3) -> float:
    """Exponentially-weighted moving average — recent observations weighted more.
    Useful for a decaying baseline. Empty series returns 0.0."""
    it = iter(series)
    try:
        acc = float(next(it))
    except StopIteration:
        return 0.0
    for x in it:
        acc = alpha * float(x) + (1 - alpha) * acc
    return acc


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def near_threshold_count(amounts, threshold: float, band: float = 0.15) -> int:
    """Count amounts sitting just under a reporting threshold — the structuring
    signature. `band` is the fraction below the threshold that counts as 'just
    under' (default 15%: e.g. $8,500-$9,999 against a $10,000 threshold)."""
    lo = threshold * (1 - band)
    return sum(1 for a in amounts if lo <= a < threshold)


def saturating(value: float, scale: float) -> float:
    """Map a non-negative magnitude into [0,1) with diminishing returns:
    value/(value+scale). `scale` is the value at which the output reaches 0.5.
    Keeps a single large deviation from dominating a bounded score."""
    if value <= 0:
        return 0.0
    return value / (value + scale)
