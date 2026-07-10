"""
QA / independent-testing attribute-sampling engine — reference implementation.

Where the other frameworks score alerts and tune rules, this one answers the
tester's three questions for a test of controls: how many items do I test (PLAN),
which ones (SELECT), and what may I conclude from the deviations I find
(EVALUATE). The full methodology is in METHODOLOGY.md; this file is its
executable form. It is a thin, domain-framed layer over `_lib/sampling.py` —
exact binomial and hypergeometric tail mathematics in place of the printed
lookup tables this work is usually done from.

The three stages:
  * PLAN      — exact sample-size solver from (confidence, tolerable deviation
                rate, expected deviation rate), hypergeometric when the
                population is finite; emits the acceptance number and the
                achieved risk of over-reliance.
  * SELECT    — seeded random or stratified selection over the population;
                reproducible from seed, with a selection log.
  * EVALUATE  — from observed deviations, the exact one-sided upper deviation
                limit (UDL) at the stated confidence, and a named-rule
                conclusion routed to the tester.

The safety posture: if observed deviations exceed the acceptance number the
conclusion can NEVER be CONTROL_EFFECTIVE — that rule fires first and is
structural. The engine never certifies a control, closes a test, or files a
result: every conclusion carries the exact statistical statement and routes to
the tester, who owns the judgment and the workpaper.

Deterministic. Same inputs and seed -> same plan, same selection, same conclusion.
"""
from __future__ import annotations

import os
import random
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib import sampling  # noqa: E402


@dataclass
class Config:
    max_acceptance: int = 1000   # solver search bound on the acceptance number


@dataclass
class ControlTest:
    """A test-of-controls request: the parameters the tester states up front."""
    control: str
    description: str
    confidence: float = 0.95         # 1 - risk of over-reliance (policy choice)
    tolerable_rate: float = 0.05     # max deviation rate consistent with reliance
    expected_rate: float = 0.01      # anticipated population deviation rate
    population: int | None = None    # finite population size, when known


@dataclass
class SamplingPlan:
    control: str
    confidence: float
    tolerable_rate: float
    expected_rate: float
    population: int | None
    sample_size: int
    acceptance_number: int
    achieved_risk: float     # P(accept | population exactly at tolerable) <= 1-confidence
    method: str              # "binomial" / "hypergeometric"

    def as_row(self) -> dict:
        return {"control": self.control, "confidence": self.confidence,
                "tolerable_rate": self.tolerable_rate, "expected_rate": self.expected_rate,
                "n": self.sample_size, "c": self.acceptance_number,
                "achieved_risk": round(self.achieved_risk, 4), "method": self.method}


@dataclass
class Selection:
    control: str
    seed: str
    method: str              # "simple-random" / "stratified"
    items: list              # selected item ids, per-stratum sorted — the selection log
    allocations: dict        # stratum -> items allocated


@dataclass
class Evaluation:
    control: str
    tested: int
    deviations: int
    acceptance_number: int
    udl: float
    tolerable_rate: float
    confidence: float
    conclusion: str          # CONTROL_EFFECTIVE / INCONCLUSIVE / CONTROL_INEFFECTIVE
    rule: str                # the named rule that fired
    statement: str           # the exact statistical statement routed to the tester
    expand_to: int | None    # INCONCLUSIVE only: total sample size that could conclude

    def as_row(self) -> dict:
        return {"control": self.control, "tested": self.tested,
                "deviations": self.deviations, "c": self.acceptance_number,
                "udl": round(self.udl, 4), "tolerable_rate": self.tolerable_rate,
                "conclusion": self.conclusion, "rule": self.rule,
                "expand_to": self.expand_to}


def plan(test: ControlTest, config: Config = Config()) -> SamplingPlan:
    """PLAN: exact sample size and acceptance number for the stated parameters.
    No lookup-table approximations — the solver inverts the exact tail."""
    ss = sampling.attribute_sample_size(test.confidence, test.tolerable_rate,
                                        test.expected_rate, test.population,
                                        config.max_acceptance)
    return SamplingPlan(control=test.control, confidence=test.confidence,
                        tolerable_rate=test.tolerable_rate, expected_rate=test.expected_rate,
                        population=test.population, sample_size=ss.n,
                        acceptance_number=ss.acceptance_number,
                        achieved_risk=ss.achieved_risk, method=ss.method)


def _allocate(sizes: dict, n: int) -> dict:
    """Proportional largest-remainder allocation of n across strata, minimum one
    item per non-empty stratum when n allows. Deterministic (strata processed in
    sorted order)."""
    total = sum(sizes.values())
    order = sorted(s for s in sizes if sizes[s] > 0)
    if n >= total:
        return {s: sizes[s] for s in order}
    raw = {s: n * sizes[s] / total for s in order}
    alloc = {s: min(int(raw[s]), sizes[s]) for s in order}
    if n >= len(order):
        for s in order:
            if alloc[s] == 0:
                alloc[s] = 1
    diff = n - sum(alloc.values())
    if diff > 0:
        by_rem = sorted(order, key=lambda s: (-(raw[s] - int(raw[s])), s))
        i = 0
        while diff > 0:
            s = by_rem[i % len(by_rem)]
            if alloc[s] < sizes[s]:
                alloc[s] += 1
                diff -= 1
            i += 1
    while diff < 0:
        s = max(order, key=lambda t: (alloc[t], t))
        if alloc[s] <= 1:
            break
        alloc[s] -= 1
        diff += 1
    return alloc


def select(p: SamplingPlan, item_ids=None, seed=0, strata=None,
           sample_size: int | None = None) -> Selection:
    """SELECT: seeded, reproducible selection of the planned sample.

    `strata` is either None (simple random over `item_ids`), a mapping
    {stratum -> list of item ids} (pre-grouped), or a list of stratum labels
    parallel to `item_ids`. Stratified selection allocates proportionally
    (largest remainder, minimum one per stratum) and samples within each
    stratum. Same seed -> identical selection; the returned items ARE the
    selection log."""
    n = sample_size if sample_size is not None else p.sample_size
    rng = random.Random(seed)
    if strata is None:
        pool = list(item_ids)
        take = min(n, len(pool))
        items = sorted(rng.sample(pool, take))
        return Selection(p.control, str(seed), "simple-random", items, {"all": take})
    if isinstance(strata, dict):
        groups = strata
    else:
        groups = {}
        for i, s in zip(item_ids, strata):
            groups.setdefault(s, []).append(i)
    alloc = _allocate({s: len(g) for s, g in groups.items()}, n)
    items = []
    for s in sorted(alloc):
        items.extend(sorted(rng.sample(groups[s], alloc[s])))
    return Selection(p.control, str(seed), "stratified", items, alloc)


def evaluate(p: SamplingPlan, tested: int, deviations: int,
             config: Config = Config()) -> Evaluation:
    """EVALUATE: the exact UDL and a named-rule conclusion, in firing order.

    R1 OVER_ACCEPTANCE       deviations > acceptance number -> CONTROL_INEFFECTIVE.
                             Fires first; past this line the conclusion can never
                             be CONTROL_EFFECTIVE (structural).
    R2 UDL_WITHIN_TOLERABLE  UDL <= tolerable rate -> CONTROL_EFFECTIVE.
    R3 UDL_EXCEEDS_TOLERABLE otherwise -> INCONCLUSIVE, with expand-sample
                             guidance (re-solve the plan at the observed rate).

    The conclusion routes to the tester with the exact statement — the engine
    never certifies."""
    udl = sampling.upper_deviation_limit(tested, deviations, p.confidence, p.population)
    scope = (f"{deviations} deviation(s) in {tested} items"
             + (f", population {p.population:,}" if p.population else ""))
    if deviations > p.acceptance_number:
        conclusion, rule, expand_to = "CONTROL_INEFFECTIVE", "OVER_ACCEPTANCE", None
        statement = (f"Observed deviations exceed the acceptance number "
                     f"({deviations} > {p.acceptance_number}); UDL {udl:.4f} vs tolerable "
                     f"{p.tolerable_rate:.4f} ({scope}). The sample does not support "
                     f"reliance on the control.")
    elif udl <= p.tolerable_rate:
        conclusion, rule, expand_to = "CONTROL_EFFECTIVE", "UDL_WITHIN_TOLERABLE", None
        statement = (f"With {p.confidence:.0%} confidence the population deviation rate "
                     f"does not exceed {udl:.4f}, within the tolerable {p.tolerable_rate:.4f} "
                     f"({scope}). The sample supports reliance on the control.")
    else:
        conclusion, rule = "INCONCLUSIVE", "UDL_EXCEEDS_TOLERABLE"
        observed_rate = deviations / tested if tested else 1.0
        expand_to = None
        if observed_rate < p.tolerable_rate:
            try:
                bigger = sampling.attribute_sample_size(
                    p.confidence, p.tolerable_rate, observed_rate, p.population,
                    config.max_acceptance)
                if bigger.n > tested:
                    expand_to = bigger.n
            except ValueError:
                expand_to = None
        guidance = (f"expand testing to {expand_to} items total" if expand_to else
                    "expansion cannot demonstrate effectiveness at the observed rate")
        statement = (f"With {p.confidence:.0%} confidence the population deviation rate "
                     f"may reach {udl:.4f}, above the tolerable {p.tolerable_rate:.4f} "
                     f"({scope}); {guidance}.")
    return Evaluation(control=p.control, tested=tested, deviations=deviations,
                      acceptance_number=p.acceptance_number, udl=udl,
                      tolerable_rate=p.tolerable_rate, confidence=p.confidence,
                      conclusion=conclusion, rule=rule, statement=statement,
                      expand_to=expand_to)


if __name__ == "__main__":
    import json
    test = ControlTest("wire-callback", "wire-callback verification completed",
                       confidence=0.95, tolerable_rate=0.05, expected_rate=0.01,
                       population=12000)
    p = plan(test)
    sel = select(p, range(12000), seed=7)
    ev = evaluate(p, len(sel.items), 1)   # the tester found 1 deviation
    print(json.dumps({"plan": p.as_row(), "selected": len(sel.items),
                      "evaluation": ev.as_row(), "statement": ev.statement}, indent=2))
