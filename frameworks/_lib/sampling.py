"""
Exact attribute-sampling mathematics for independent testing and QA.

The classic audit question — how many items do I test, and what may I conclude
from the deviations I find — is usually answered from printed lookup tables.
Those tables are discretized snapshots of exact probability statements; this
module computes the statements themselves, so a sampling plan and its evaluation
are reproducible from stated parameters rather than from a table edition.

Vocabulary (attribute sampling for tests of controls):

  confidence        1 - risk of over-reliance: the required probability that the
                    plan rejects reliance on a population deviating at the
                    tolerable rate.
  tolerable_rate    the maximum population deviation rate the tester can accept
                    and still rely on the control.
  expected_rate     the deviation rate anticipated in the population; it drives
                    the acceptance number (the deviations the plan can absorb
                    without rejecting reliance).
  acceptance number c — the plan rejects reliance when observed deviations > c.
  UDL               the one-sided upper deviation limit: the largest population
                    deviation rate the sample does not reject at the stated
                    confidence (exact Clopper-Pearson upper bound; exact
                    hypergeometric inversion when the population is finite).

Everything is exact — direct tail summation, integer search, bisection — with no
normal approximations and no lookup tables. Pure standard library.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


# --------------------------------------------------------------- exact tails

def _log_comb(a: int, b: int) -> float:
    return math.lgamma(a + 1) - math.lgamma(b + 1) - math.lgamma(a - b + 1)


def binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k) for X ~ Binomial(n, p): exact summation of the lower tail.
    In attribute sampling this is the probability of observing at most k
    deviations in n items when the population deviates at rate p."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    lp, lq = math.log(p), math.log1p(-p)
    total = 0.0
    for i in range(k + 1):
        total += math.exp(_log_comb(n, i) + i * lp + (n - i) * lq)
    return min(total, 1.0)


def binom_tail(k: int, n: int, p: float) -> float:
    """P(X >= k) — the exact binomial upper tail."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return max(0.0, 1.0 - binom_cdf(k - 1, n, p))


def hypergeom_cdf(k: int, N: int, K: int, n: int) -> float:
    """P(X <= k) for X ~ Hypergeometric(N, K, n): at most k deviations in a
    sample of n drawn WITHOUT replacement from a population of N containing K
    deviations. Exact summation over the support."""
    if not (0 <= K <= N and 0 <= n <= N):
        raise ValueError("require 0 <= K <= N and 0 <= n <= N")
    lo, hi = max(0, n - (N - K)), min(n, K)
    if k < lo:
        return 0.0
    if k >= hi:
        return 1.0
    lden = _log_comb(N, n)
    total = 0.0
    for i in range(lo, k + 1):
        total += math.exp(_log_comb(K, i) + _log_comb(N - K, n - i) - lden)
    return min(total, 1.0)


def hypergeom_tail(k: int, N: int, K: int, n: int) -> float:
    """P(X >= k) — the exact hypergeometric upper tail."""
    lo = max(0, n - (N - K))
    if k <= lo:
        return 1.0
    if k > min(n, K):
        return 0.0
    return max(0.0, 1.0 - hypergeom_cdf(k - 1, N, K, n))


# ------------------------------------------------- attribute sample-size solver

@dataclass(frozen=True)
class SampleSize:
    n: int                  # items to test
    acceptance_number: int  # c — reject reliance when observed deviations > c
    achieved_risk: float    # P(accept | population exactly at the tolerable rate) <= 1-confidence
    method: str             # "binomial" or "hypergeometric"


def _accept_prob(c: int, n: int, tolerable_rate: float, population) -> float:
    """P(observed <= c) when the population deviates at the tolerable rate —
    the risk of over-reliance realized by the plan (n, c). For a finite
    population the tolerable-rate hypothesis is the SMALLEST deviation count
    still at or above the rate (ceil), the hardest such population to detect."""
    if population is None:
        return binom_cdf(c, n, tolerable_rate)
    K = math.ceil(population * tolerable_rate)
    return hypergeom_cdf(c, population, K, n)


def _min_n(c: int, alpha: float, tolerable_rate: float, population) -> int | None:
    """Smallest n with acceptance probability <= alpha at the tolerable rate.
    The acceptance probability is non-increasing in n, so double then bisect.
    Returns None when even a census cannot achieve it (finite population whose
    tolerable deviation count does not exceed c)."""
    cap = population
    hi = max(2 * (c + 1), 4)
    if cap is not None:
        hi = min(hi, cap)
    while _accept_prob(c, hi, tolerable_rate, population) > alpha:
        if cap is not None and hi >= cap:
            return None
        hi = hi * 2 if cap is None else min(hi * 2, cap)
    lo = c  # accept prob at n == c is 1 > alpha
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if _accept_prob(c, mid, tolerable_rate, population) <= alpha:
            hi = mid
        else:
            lo = mid
    return hi


def attribute_sample_size(confidence: float, tolerable_rate: float,
                          expected_rate: float = 0.0, population: int | None = None,
                          max_acceptance: int = 1000) -> SampleSize:
    """Exact attribute-sampling plan: the smallest (n, c) such that a population
    deviating at the tolerable rate is accepted with probability at most
    1 - confidence, while the acceptance number can absorb the expected
    deviations (c >= n * expected_rate). Binomial by default; exact
    hypergeometric (finite-population correction) when `population` is given.
    Raises ValueError when expected_rate >= tolerable_rate — no sample size can
    separate them."""
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    if not 0.0 < tolerable_rate < 1.0:
        raise ValueError("tolerable_rate must be in (0, 1)")
    if expected_rate < 0.0 or expected_rate >= tolerable_rate:
        raise ValueError("expected_rate must satisfy 0 <= expected < tolerable — "
                         "otherwise no sample size can distinguish them")
    if population is not None and population < 1:
        raise ValueError("population must be a positive integer")
    alpha = 1.0 - confidence
    for c in range(max_acceptance + 1):
        n_c = _min_n(c, alpha, tolerable_rate, population)
        if n_c is None:
            raise ValueError("population too small to test the tolerable rate at "
                             "this confidence (census still accepts)")
        if c >= n_c * expected_rate:
            return SampleSize(n=n_c, acceptance_number=c,
                              achieved_risk=_accept_prob(c, n_c, tolerable_rate, population),
                              method="hypergeometric" if population is not None else "binomial")
    raise ValueError(f"no plan found with acceptance number <= {max_acceptance}")


# ----------------------------------------------- one-sided upper deviation limit

def upper_deviation_limit(n: int, k: int, confidence: float,
                          population: int | None = None) -> float:
    """The exact one-sided upper deviation limit (UDL): the largest population
    deviation rate NOT rejected by observing k deviations in n items, at the
    stated confidence.

    Infinite population (binomial): the exact Clopper-Pearson upper bound — the
    smallest p with P(X <= k | n, p) <= 1 - confidence, found by bisection
    (the CDF is continuous and strictly decreasing in p).

    Finite population (hypergeometric): exact inversion over the integer count
    of population deviations. K* is the smallest count whose acceptance
    probability P(X <= k | N, K, n) falls to 1 - confidence or below; every
    count >= K* is rejected, so the limit is (K* - 1) / N. A census (n == N)
    collapses to exactly k / N."""
    if n < 1:
        raise ValueError("n must be >= 1")
    if not 0 <= k <= n:
        raise ValueError("require 0 <= k <= n")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    alpha = 1.0 - confidence
    if population is None:
        if k >= n:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if binom_cdf(k, n, mid) <= alpha:
                hi = mid
            else:
                lo = mid
        return hi
    N = population
    if n > N:
        raise ValueError("sample cannot exceed the population")
    # smallest K in [k, N] with P(X <= k | N, K, n) <= alpha; monotone in K
    hi_k = min(N, N - n + k + 1)
    if hypergeom_cdf(k, N, hi_k, n) > alpha:
        return 1.0  # nothing rejected (e.g. fully-deviant sample)
    lo_k = k        # cdf == 1 at K == k, never <= alpha
    while hi_k - lo_k > 1:
        mid = (lo_k + hi_k) // 2
        if hypergeom_cdf(k, N, mid, n) <= alpha:
            hi_k = mid
        else:
            lo_k = mid
    return (hi_k - 1) / N
