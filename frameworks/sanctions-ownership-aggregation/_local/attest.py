"""Reproducibility attestations and exact binomial upper bounds."""

from __future__ import annotations

import hashlib
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


def _binomial_cdf(k: int, n: int, p: float) -> float:
    if k >= n:
        return 1.0
    if p <= 0:
        return 1.0
    if p >= 1:
        return 0.0
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson_upper(events: int, trials: int, confidence: float = 0.95) -> float:
    """Exact one-sided upper confidence bound via inversion of the binomial CDF."""
    if trials <= 0 or not 0 <= events <= trials:
        raise ValueError("require 0 <= events <= trials and trials > 0")
    if events == trials:
        return 1.0
    alpha = 1.0 - confidence
    if events == 0:
        return 1.0 - alpha ** (1.0 / trials)
    low, high = events / trials, 1.0
    for _ in range(100):
        middle = (low + high) / 2
        if _binomial_cdf(events, trials, middle) > alpha:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def bound_sentence(events: int, trials: int, confidence: float = 0.95) -> str:
    upper = clopper_pearson_upper(events, trials, confidence)
    return (
        f"Observed {events} auto-clear false negatives in {trials} labelled TRUE blocked-by-ownership candidates; "
        f"the exact one-sided {confidence:.0%} Clopper-Pearson upper bound is {upper:.6f}. "
        "This bound is a property of the validation sample size, not a claim of a zero population rate."
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def runtime_provenance() -> dict[str, str]:
    return {
        "interpreter": sys.executable,
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
    }
