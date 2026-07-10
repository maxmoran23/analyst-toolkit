"""
Validation harness for the QA / independent-testing attribute-sampling framework.

Runs plan-select-evaluate over a seeded population of controls whose true
deviation rates are known by construction, and checks the properties that
matter for a sampling engine a tester relies on:

  1. STRUCTURAL   no evaluation with observed deviations above the acceptance
                  number ever concludes CONTROL_EFFECTIVE, and every planted
                  control (a fully-deviant stratum the stratified sample must
                  hit more than acceptance-number times) concludes non-EFFECTIVE
                  across every replicate draw.
  2. DIRECTION    on populations deviating at 2-3x the tolerable rate, the
                  MEASURED rate of CONTROL_EFFECTIVE conclusions over replicate
                  samples must not exceed the design risk (plus a small margin).
  3. CROSS-CHECK  the UDL is recomputed by an independent brute-force exact
                  computation (direct math.comb summation for the binomial;
                  exact integer/Fraction arithmetic for the hypergeometric);
                  any divergence beyond tolerance fails the build.
  4. MONOTONE     the sample-size solver never returns a smaller sample for a
                  higher confidence or a tighter tolerable rate, and the
                  finite-population plan never exceeds the binomial plan.

All four are BUILD GATES: any breach exits non-zero. With --trials, every
trial seed is gated, not just the base seed.

Usage:
    python3 run_validation.py
    python3 run_validation.py --seed 42 --controls 12 --population 40000
    python3 run_validation.py --trials 6 --no-write
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import math
import os
import random
import subprocess
import sys
from collections import Counter
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from _lib import metrics, sampling  # noqa: E402
import engine as E  # noqa: E402
import generate_synthetic_data as G  # noqa: E402

DESIGN_CONFIDENCE = G.CONFIDENCE                    # 0.95 for every generated control
DESIGN_RISK = round(1.0 - DESIGN_CONFIDENCE, 6)     # alpha, the risk of over-reliance
FA_MARGIN = 0.05                                    # measured false-assurance gate margin
CROSSCHECK_TOL = 1e-9                               # UDL divergence tolerance
REPLICATES_FA = 50                                  # replicate draws per failing/planted control
REPLICATES_CAL = 200                                # draws per plan for at-tolerable calibration
SWEEP_CONFS = [0.90, 0.95, 0.975, 0.99]
SWEEP_TOLS = [0.02, 0.04, 0.06, 0.08, 0.10]
SWEEP_EXPECTED = 0.01


# ------------------------------------------------------------------ population

def generate(controls_n, population, seed):
    rng = random.Random(seed)
    out = []
    for i in range(controls_n):
        scenario = G.SCENARIO_CYCLE[i % len(G.SCENARIO_CYCLE)]
        ctl, items = G.make_control("CTRL-%03d" % i, population, scenario, rng)
        groups, labels = {}, []
        for j, (s, dev) in enumerate(items):
            groups.setdefault(s, []).append(j)
            labels.append(dev)
        out.append({"ctl": ctl, "groups": groups, "labels": labels,
                    "strata": [s for s, _ in items]})
    return out


# -------------------------------------------------------------------- main run

def run_controls(controls, seed, config):
    records = []
    for idx, c in enumerate(controls):
        ctl = c["ctl"]
        test = E.ControlTest(ctl["control_id"], ctl["name"], ctl["confidence"],
                             ctl["tolerable_rate"], ctl["expected_rate"], ctl["population"])
        p = E.plan(test, config)
        sel = E.select(p, seed=f"{seed}:main:{idx}", strata=c["groups"])
        k = sum(c["labels"][i] for i in sel.items)
        ev = E.evaluate(p, len(sel.items), k, config)
        records.append({"ctl": ctl, "plan": p, "sel": sel, "eval": ev,
                        "scenario": ctl["scenario"], "true_rate": ctl["true_rate"],
                        "strata": c["strata"]})
    return records


# ------------------------------------------- gates 1+2: replicates and planting

def measure_replicates(controls, records, seed, config, R=REPLICATES_FA):
    """Replicate draws on failing and planted controls. Returns measured
    false-assurance on failing populations, EFFECTIVE count on planted
    populations, structural breaches across every replicate evaluation, and a
    per-control table for the report."""
    fa_rows, breaches = [], 0
    failing_eff = failing_reps = planted_eff = planted_reps = 0
    planted_design_ok = True
    for idx, (c, rec) in enumerate(zip(controls, records)):
        scen = rec["scenario"]
        if scen not in ("failing", "planted"):
            continue
        p, ctl = rec["plan"], rec["ctl"]
        if scen == "planted":
            alloc = rec["sel"].allocations.get(ctl["planted_stratum"], 0)
            if alloc <= p.acceptance_number:
                planted_design_ok = False
        eff = 0
        for r in range(R):
            sel = E.select(p, seed=f"{seed}:rep:{idx}:{r}", strata=c["groups"])
            k = sum(c["labels"][i] for i in sel.items)
            ev = E.evaluate(p, len(sel.items), k, config)
            if ev.deviations > ev.acceptance_number and ev.conclusion == "CONTROL_EFFECTIVE":
                breaches += 1
            if ev.conclusion == "CONTROL_EFFECTIVE":
                eff += 1
        if scen == "failing":
            failing_eff += eff
            failing_reps += R
        else:
            planted_eff += eff
            planted_reps += R
        K_true = sum(c["labels"])
        exact_accept = sampling.hypergeom_cdf(p.acceptance_number, ctl["population"],
                                              K_true, p.sample_size)
        fa_rows.append({"control": ctl["control_id"], "scenario": scen,
                        "true_rate": ctl["true_rate"], "tolerable": ctl["tolerable_rate"],
                        "n": p.sample_size, "c": p.acceptance_number,
                        "exact_p_accept": round(exact_accept, 6),
                        "effective": eff, "replicates": R})
    return {"fa_rows": fa_rows, "breaches": breaches,
            "failing_effective": failing_eff, "failing_replicates": failing_reps,
            "planted_effective": planted_eff, "planted_replicates": planted_reps,
            "planted_design_ok": planted_design_ok}


# ------------------------------------ calibration: measured risk at the tolerable rate

def measure_calibration(records, seed, R=REPLICATES_CAL):
    """For each distinct plan, build a population deviating at EXACTLY the
    tolerable-rate count (K = ceil(N * tolerable)) and measure the acceptance
    rate over R fresh samples — the design risk, observed rather than asserted.
    Compared against the exact hypergeometric acceptance probability."""
    rows, seen = [], set()
    for rec in records:
        p, N = rec["plan"], rec["ctl"]["population"]
        key = (p.sample_size, p.acceptance_number, N, p.tolerable_rate)
        if key in seen:
            continue
        seen.add(key)
        K = math.ceil(N * p.tolerable_rate)
        rng = random.Random(f"{seed}:cal:{p.sample_size}:{p.acceptance_number}:{K}")
        devs = set(rng.sample(range(N), K))
        accepted = 0
        for _ in range(R):
            s = rng.sample(range(N), p.sample_size)
            if sum(1 for i in s if i in devs) <= p.acceptance_number:
                accepted += 1
        exact = sampling.hypergeom_cdf(p.acceptance_number, N, K, p.sample_size)
        rows.append({"n": p.sample_size, "c": p.acceptance_number,
                     "tolerable": p.tolerable_rate,
                     "exact_p_accept": round(exact, 4),
                     "measured_p_accept": round(accepted / R, 4), "replicates": R})
    max_gap = max(abs(r["measured_p_accept"] - r["exact_p_accept"]) for r in rows)
    return rows, round(max_gap, 4)


# ----------------------------------------- gate 3: independent UDL cross-check

def _bf_binom_cdf(k, n, p):
    """Brute-force exact binomial lower tail: direct math.comb summation —
    independent of the lgamma path in _lib/sampling."""
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    q = 1.0 - p
    return min(1.0, sum(math.comb(n, i) * (p ** i) * (q ** (n - i)) for i in range(k + 1)))


def _bf_binom_udl(n, k, confidence):
    alpha = 1.0 - confidence
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if _bf_binom_cdf(k, n, mid) <= alpha:
            hi = mid
        else:
            lo = mid
    return hi


def _exact_hyper_cdf(k, N, K, n) -> Fraction:
    """Brute-force exact hypergeometric lower tail as a rational number —
    integer combinatorics only, no floating point."""
    lo, hi = max(0, n - (N - K)), min(n, K)
    if k < lo:
        return Fraction(0)
    if k >= hi:
        return Fraction(1)
    num = sum(math.comb(K, i) * math.comb(N - K, n - i) for i in range(lo, k + 1))
    return Fraction(num, math.comb(N, n))


def _bf_hyper_udl_count(n, k, confidence, N):
    """Brute-force K*: smallest population deviation count rejected by the
    sample, via exact Fraction comparisons. UDL = (K* - 1) / N."""
    alpha = Fraction(1) - Fraction(confidence)
    hi = min(N, N - n + k + 1)
    if _exact_hyper_cdf(k, N, hi, n) > alpha:
        return N + 1  # nothing rejected -> UDL 1.0
    lo = k
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if _exact_hyper_cdf(k, N, mid, n) <= alpha:
            hi = mid
        else:
            lo = mid
    return hi


def crosscheck_udl(records):
    """Primary UDL (lgamma tails + bisection / integer search in _lib/sampling)
    vs an independent brute-force exact recomputation. Gate: max divergence
    <= CROSSCHECK_TOL and zero integer mismatches on the hypergeometric side."""
    rows, max_div, mismatches = [], 0.0, 0
    for n in (25, 60, 124, 200, 400):
        for k in (0, 1, 2, 5, 10):
            if k >= n:
                continue
            for conf in (0.90, 0.95, 0.99):
                u1 = sampling.upper_deviation_limit(n, k, conf)
                u2 = _bf_binom_udl(n, k, conf)
                d = abs(u1 - u2)
                max_div = max(max_div, d)
                rows.append({"method": "binomial", "n": n, "k": k, "confidence": conf,
                             "udl_primary": round(u1, 10), "udl_bruteforce": round(u2, 10),
                             "abs_divergence": f"{d:.3e}"})
    for rec in records:
        p, N = rec["plan"], rec["ctl"]["population"]
        n = rec["eval"].tested
        for k in {0, rec["eval"].deviations, p.acceptance_number, p.acceptance_number + 1}:
            if not 0 <= k < n:
                continue
            u1 = sampling.upper_deviation_limit(n, k, p.confidence, N)
            K1 = round(u1 * N) + 1
            K2 = _bf_hyper_udl_count(n, k, p.confidence, N)
            u2 = (K2 - 1) / N
            if K1 != K2:
                mismatches += 1
            cdf_div = abs(sampling.hypergeom_cdf(k, N, K2, n)
                          - float(_exact_hyper_cdf(k, N, K2, n)))
            max_div = max(max_div, abs(u1 - u2), cdf_div)
            rows.append({"method": "hypergeometric", "n": n, "k": k,
                         "confidence": p.confidence,
                         "udl_primary": round(u1, 10), "udl_bruteforce": round(u2, 10),
                         "abs_divergence": f"{max(abs(u1 - u2), cdf_div):.3e}"})
    return rows, max_div, mismatches


# ----------------------------------------------- gate 4: solver monotonicity

def monotonicity_sweep(population):
    """The sample-size solver across a (confidence x tolerable) grid, binomial
    and finite-population. Checks: n never decreases as confidence rises; n
    never increases as the tolerable rate loosens; the finite-population plan
    never exceeds the binomial plan."""
    rows, table = [], {}
    for method, pop in (("binomial", None), ("hypergeometric", population)):
        for cf in SWEEP_CONFS:
            for t in SWEEP_TOLS:
                ss = sampling.attribute_sample_size(cf, t, SWEEP_EXPECTED, pop)
                table[(method, cf, t)] = ss.n
                rows.append({"method": method, "confidence": cf, "tolerable_rate": t,
                             "expected_rate": SWEEP_EXPECTED, "n": ss.n,
                             "c": ss.acceptance_number,
                             "achieved_risk": round(ss.achieved_risk, 4)})
    violations = 0
    for method in ("binomial", "hypergeometric"):
        for t in SWEEP_TOLS:
            ns = [table[(method, cf, t)] for cf in SWEEP_CONFS]
            violations += sum(1 for a, b in zip(ns, ns[1:]) if b < a)
        for cf in SWEEP_CONFS:
            ns = [table[(method, cf, t)] for t in SWEEP_TOLS]
            violations += sum(1 for a, b in zip(ns, ns[1:]) if b > a)
    fpc_violations = sum(1 for cf in SWEEP_CONFS for t in SWEEP_TOLS
                         if table[("hypergeometric", cf, t)] > table[("binomial", cf, t)])
    return rows, violations, fpc_violations


# --------------------------------------------------- short-test demonstration

def short_test_demo(controls, records, seed, config):
    """Deliberately test fewer items than planned on one boundary control to
    exercise the INCONCLUSIVE path and its expand-sample guidance. Reported,
    not gated — the outcome is whatever the mathematics concludes."""
    for idx, rec in enumerate(records):
        if rec["scenario"] != "boundary":
            continue
        c, p = controls[idx], rec["plan"]
        tested = max(25, (p.sample_size * 2) // 5)
        sel = E.select(p, range(rec["ctl"]["population"]),
                       seed=f"{seed}:short:{idx}", sample_size=tested)
        k = sum(c["labels"][i] for i in sel.items)
        ev = E.evaluate(p, tested, k, config)
        return {"control": rec["ctl"]["control_id"], "planned_n": p.sample_size,
                "tested": tested, "deviations": k, "c": p.acceptance_number,
                "udl": round(ev.udl, 4), "tolerable": p.tolerable_rate,
                "conclusion": ev.conclusion, "rule": ev.rule, "expand_to": ev.expand_to}
    return None


# ------------------------------------------------------------------- analysis

def analyze(records, reps, cal_gap, xc_max, xc_mismatches, xc_cases,
            mono_violations, fpc_violations, mono_cells):
    n = len(records)
    concl = Counter(r["eval"].conclusion for r in records)
    by_scen = {}
    for r in records:
        by_scen.setdefault(r["scenario"], Counter())[r["eval"].conclusion] += 1
    main_breaches = sum(1 for r in records
                        if r["eval"].deviations > r["eval"].acceptance_number
                        and r["eval"].conclusion == "CONTROL_EFFECTIVE")
    plan_risk_breaches = sum(1 for r in records
                             if r["plan"].achieved_risk > DESIGN_RISK + 1e-12)
    planted_main_eff = sum(1 for r in records if r["scenario"] == "planted"
                           and r["eval"].conclusion == "CONTROL_EFFECTIVE")
    structural_breaches = main_breaches + reps["breaches"] + plan_risk_breaches
    n_evals = n + reps["failing_replicates"] + reps["planted_replicates"]
    fa_rate = (reps["failing_effective"] / reps["failing_replicates"]
               if reps["failing_replicates"] else 0.0)
    sizes = sorted(r["plan"].sample_size for r in records)
    items_total = sum(r["ctl"]["population"] for r in records)
    items_tested = sum(r["eval"].tested for r in records)
    gates = {
        "structural_over_acceptance": structural_breaches == 0,
        "planted_zero_effective": (reps["planted_effective"] + planted_main_eff == 0
                                   and reps["planted_design_ok"]),
        "false_assurance_within_design_risk": fa_rate <= DESIGN_RISK + FA_MARGIN,
        "udl_crosscheck": xc_max <= CROSSCHECK_TOL and xc_mismatches == 0,
        "solver_monotonicity": mono_violations == 0 and fpc_violations == 0,
    }
    return {"n_controls": n, "items_total": items_total, "items_tested": items_tested,
            "test_coverage": round(items_tested / items_total, 5),
            "conclusions": dict(concl),
            "by_scenario": {s: dict(c) for s, c in sorted(by_scen.items())},
            "n_evaluations": n_evals,
            "structural_breaches": structural_breaches,
            "planted_controls": sum(1 for r in records if r["scenario"] == "planted"),
            "planted_replicates": reps["planted_replicates"],
            "planted_effective": reps["planted_effective"] + planted_main_eff,
            "planted_design_ok": reps["planted_design_ok"],
            "failing_controls": sum(1 for r in records if r["scenario"] == "failing"),
            "failing_replicates": reps["failing_replicates"],
            "failing_effective": reps["failing_effective"],
            "false_assurance_measured": round(fa_rate, 4),
            "design_risk": DESIGN_RISK, "fa_limit": round(DESIGN_RISK + FA_MARGIN, 4),
            "crosscheck_cases": xc_cases,
            "crosscheck_max_divergence": xc_max,
            "crosscheck_hyper_mismatches": xc_mismatches,
            "monotonicity_cells": mono_cells,
            "monotonicity_violations": mono_violations,
            "fpc_violations": fpc_violations,
            "calibration_max_gap": cal_gap,
            "sample_size_min": sizes[0], "sample_size_median": sizes[len(sizes) // 2],
            "sample_size_max": sizes[-1],
            "gates": gates, "safety_ok": all(gates.values())}


def _git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=HERE, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------- report

def render_report(records, a, reps, cal_rows, mono_rows, demo, manifest):
    plan_rows = [{"control": r["ctl"]["control_id"], "scenario": r["scenario"],
                  "tolerable": r["plan"].tolerable_rate, "expected": r["plan"].expected_rate,
                  "n": r["plan"].sample_size, "c": r["plan"].acceptance_number,
                  "achieved_risk": round(r["plan"].achieved_risk, 4)}
                 for r in records]
    concl_rows = [{"control": r["ctl"]["control_id"], "scenario": r["scenario"],
                   "true_rate": r["true_rate"], "tested": r["eval"].tested,
                   "deviations": r["eval"].deviations, "c": r["eval"].acceptance_number,
                   "udl": round(r["eval"].udl, 4), "tolerable": r["eval"].tolerable_rate,
                   "conclusion": r["eval"].conclusion, "rule": r["eval"].rule}
                  for r in records]
    mono_show = [r for r in mono_rows if r["method"] == "hypergeometric"
                 and r["confidence"] in (0.90, 0.95, 0.99)]

    L = []
    A = L.append
    A("# Validation Report — QA / Independent-Testing Attribute-Sampling Framework")
    A("")
    A("> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running plan-select-evaluate "
      "over a seeded population of controls whose true deviation rates are known by "
      "construction. No real control, tester, or institution is represented (the "
      "fictional institution is Harborview Financial Group). Numbers are emitted by "
      "`run_validation.py`, not authored.")
    A("")
    A(f"**Run:** seed `{manifest['seed']}` · {manifest['controls']} controls · "
      f"{manifest['items_total']:,} items · git `{manifest['git_sha']}` · "
      f"{manifest['generated_utc']}")
    A("")
    A(f"**Headline:** UDL cross-check exact — max abs divergence "
      f"**{a['crosscheck_max_divergence']:.3e}** over {a['crosscheck_cases']} cases "
      f"(tolerance 1e-9, {a['crosscheck_hyper_mismatches']} integer mismatches); "
      f"**{a['structural_breaches']}** structural breaches across "
      f"{a['n_evaluations']:,} evaluations; measured false-assurance on failing "
      f"populations **{a['false_assurance_measured']:.4f}** "
      f"({a['failing_effective']}/{a['failing_replicates']}) vs design risk "
      f"{a['design_risk']:.0%}; solver monotonicity **{a['monotonicity_violations']}** "
      f"violations across {a['monotonicity_cells']} grid cells.")
    A("")
    A("## 1. Methodology summary")
    A("For each control the engine PLANS an exact attribute sample (smallest n and "
      "acceptance number c such that a population deviating at the tolerable rate is "
      "accepted with probability at most the design risk — exact hypergeometric, no "
      "lookup-table approximations), SELECTS it by seeded stratified random sampling, "
      "and EVALUATES the observed deviations into the exact one-sided upper deviation "
      "limit (UDL) and a named-rule conclusion. Observed deviations above the "
      "acceptance number can never conclude CONTROL_EFFECTIVE — that rule fires "
      "first. Full spec: `METHODOLOGY.md`.")
    A("")
    A("## 2. Population construction")
    A(f"{manifest['controls']} controls x {manifest['population_per_control']:,} labelled "
      "test items each, on a deterministic scenario cycle: clean (true rate 0.08-0.22x "
      "tolerable), failing (2-3x tolerable), boundary (0.75-1.10x), and planted (one "
      "whole stratum 100% deviant — the adversarial case the stratified sample cannot "
      "miss). The true rate is known to the generator and NEVER used by the engine — "
      "only the plan parameters and the drawn sample are.")
    A("")
    A("## 3. Sampling plans (exact solver)")
    A(metrics.markdown_table(plan_rows))
    A("")
    A(f"Every plan's achieved risk is at or below the {DESIGN_RISK:.0%} design risk "
      f"(confidence {DESIGN_CONFIDENCE:.0%}); sample sizes span "
      f"{a['sample_size_min']}-{a['sample_size_max']} items "
      f"(median {a['sample_size_median']}), testing {a['items_tested']:,} of "
      f"{a['items_total']:,} items ({a['test_coverage']:.2%}).")
    A("")
    A("## 4. Conclusions (per control)")
    A(metrics.markdown_table(concl_rows))
    A("")
    scen_bits = []
    for s, c in a["by_scenario"].items():
        parts = ", ".join(f"{v} {k}" for k, v in sorted(c.items()))
        scen_bits.append(f"{s}: {parts}")
    A("By scenario — " + "; ".join(scen_bits) + ".")
    A("")
    A("## 5. UDL cross-check (gate)")
    A(f"The primary UDL (log-gamma tails, bisection, integer search) was recomputed "
      f"for {a['crosscheck_cases']} cases by an independent brute-force exact path: "
      f"direct `math.comb` summation for the binomial bound, exact integer/Fraction "
      f"arithmetic for the hypergeometric bound. Max abs divergence "
      f"**{a['crosscheck_max_divergence']:.3e}** (tolerance 1e-9); hypergeometric "
      f"integer-count mismatches **{a['crosscheck_hyper_mismatches']}**. Full table: "
      f"`udl-crosscheck.csv`.")
    A("")
    A("## 6. Measured false-assurance — the direction gate")
    A(f"On the failing controls (true rate 2-3x tolerable), {REPLICATES_FA} independent "
      f"replicate samples were drawn per control and evaluated. CONTROL_EFFECTIVE "
      f"conclusions: **{a['failing_effective']}/{a['failing_replicates']}** "
      f"(measured false-assurance {a['false_assurance_measured']:.4f}; gate fails "
      f"above {a['fa_limit']:.2f} = design risk + margin).")
    A("")
    A(metrics.markdown_table(reps["fa_rows"]))
    A("")
    A(f"Calibration at the boundary: for each distinct plan, a population deviating at "
      f"EXACTLY the tolerable count was constructed and the acceptance rate measured "
      f"over {REPLICATES_CAL} fresh samples — the design risk observed rather than "
      f"asserted. Max |measured - exact| = **{a['calibration_max_gap']}** "
      f"(binomial sampling error at {REPLICATES_CAL} replicates; exact value from the "
      f"same hypergeometric tail the plan is built on).")
    A("")
    A(metrics.markdown_table(cal_rows))
    A("")
    A("## 7. Planted-deviation structural gate")
    A(f"{a['planted_controls']} planted controls carry a fully-deviant stratum sized so "
      f"stratified allocation must place more than the acceptance number of items in "
      f"it (design verified: {'yes' if a['planted_design_ok'] else 'NO'}). Across the "
      f"main run and {a['planted_replicates']} replicate draws: "
      f"**{a['planted_effective']}** CONTROL_EFFECTIVE conclusions (must be 0). "
      f"Combined with the rule-order guarantee, over-acceptance evaluations concluded "
      f"EFFECTIVE in **{a['structural_breaches']}** of {a['n_evaluations']:,} "
      f"evaluations.")
    A("")
    A("## 8. Sample-size solver monotonicity (gate)")
    A(f"The exact solver was swept over {a['monotonicity_cells']} grid cells "
      f"(confidence {SWEEP_CONFS} x tolerable {SWEEP_TOLS}, expected "
      f"{SWEEP_EXPECTED}, binomial and finite-population). Higher confidence or a "
      f"tighter tolerable rate never yields a smaller sample: "
      f"**{a['monotonicity_violations']}** violations. The finite-population plan "
      f"never exceeds the binomial plan: **{a['fpc_violations']}** violations. "
      f"Excerpt (hypergeometric, N={manifest['population_per_control']:,}):")
    A("")
    A(metrics.markdown_table(mono_show,
                             ["confidence", "tolerable_rate", "n", "c", "achieved_risk"]))
    A("")
    A("## 9. Short-test demonstration (INCONCLUSIVE path)")
    if demo:
        A(f"Control `{demo['control']}` was deliberately tested at {demo['tested']} of "
          f"its planned {demo['planned_n']} items: {demo['deviations']} deviation(s), "
          f"UDL {demo['udl']} vs tolerable {demo['tolerable']} -> "
          f"**{demo['conclusion']}** ({demo['rule']}"
          + (f", expand to {demo['expand_to']} items" if demo["expand_to"] else "")
          + "). A short test cannot silently pass: the UDL stays above the tolerable "
            "rate until enough items are tested, and the engine emits the exact "
            "expansion needed.")
    else:
        A("No boundary control present at this scale; demonstration skipped.")
    A("")
    A("## 10. Limitations")
    A("- Synthetic deviations are independent draws within strata; real control "
      "failures cluster (by processor, by period, by branch). Stratify on the "
      "clustering dimension and treat any cluster found as a finding to scope, not "
      "just a count.")
    A("- The engine quantifies SAMPLING risk only. Non-sampling risk — the tester "
      "misreading an item — is untouched by sample size and is managed by "
      "workpaper review, not by this engine.")
    A("- Conclusions are statistical statements routed to the tester; the engine "
      "never certifies a control, closes a test, or files a result. Tolerable rate, "
      "confidence, and expected rate are policy choices set and owned by the "
      "institution.")
    A("- A transparent reference implementation, not a production control.")
    A("")
    A("## 11. Reproduction")
    A("```bash")
    A(f"python3 run_validation.py --seed {manifest['seed']} --controls "
      f"{manifest['controls']} --population {manifest['population_per_control']}")
    A("```")
    A("")
    return "\n".join(L)


# ------------------------------------------------------------------- evidence

def write_evidence(out_dir, records, a, manifest, report, xc_rows, mono_rows):
    os.makedirs(out_dir, exist_ok=True)
    json.dump({"analysis": a, "manifest": manifest},
              open(os.path.join(out_dir, "metrics.json"), "w"), indent=2)
    with open(os.path.join(out_dir, "control-conclusions.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["control", "scenario", "true_rate", "confidence", "tolerable_rate",
                    "expected_rate", "n", "c", "achieved_risk", "tested", "deviations",
                    "udl", "conclusion", "rule"])
        for r in records:
            p, ev = r["plan"], r["eval"]
            w.writerow([r["ctl"]["control_id"], r["scenario"], r["true_rate"],
                        p.confidence, p.tolerable_rate, p.expected_rate, p.sample_size,
                        p.acceptance_number, round(p.achieved_risk, 6), ev.tested,
                        ev.deviations, round(ev.udl, 6), ev.conclusion, ev.rule])
    with open(os.path.join(out_dir, "sample-size-sweep.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["method", "confidence", "tolerable_rate",
                                           "expected_rate", "n", "c", "achieved_risk"])
        w.writeheader()
        w.writerows(mono_rows)
    with open(os.path.join(out_dir, "udl-crosscheck.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["method", "n", "k", "confidence",
                                           "udl_primary", "udl_bruteforce", "abs_divergence"])
        w.writeheader()
        w.writerows(xc_rows)
    with open(os.path.join(out_dir, "selection-log.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["control", "selection_seed", "item_id", "stratum"])
        for r in records:
            sel, strata = r["sel"], r["strata"]
            for i in sel.items:
                w.writerow([r["ctl"]["control_id"], sel.seed,
                            "%s-I%06d" % (r["ctl"]["control_id"], i), strata[i]])
    json.dump(manifest, open(os.path.join(out_dir, "run-manifest.json"), "w"), indent=2)
    open(os.path.join(out_dir, "VALIDATION-REPORT.md"), "w").write(report)


# ----------------------------------------------------------------------- main

def run_once(controls_n, population, seed, config):
    controls = generate(controls_n, population, seed)
    records = run_controls(controls, seed, config)
    reps = measure_replicates(controls, records, seed, config)
    cal_rows, cal_gap = measure_calibration(records, seed)
    xc_rows, xc_max, xc_mismatches = crosscheck_udl(records)
    mono_rows, mono_viol, fpc_viol = monotonicity_sweep(population)
    demo = short_test_demo(controls, records, seed, config)
    a = analyze(records, reps, cal_gap, xc_max, xc_mismatches, len(xc_rows),
                mono_viol, fpc_viol, len(mono_rows))
    return {"records": records, "reps": reps, "cal_rows": cal_rows,
            "xc_rows": xc_rows, "mono_rows": mono_rows, "demo": demo}, a


def _print_summary(a, seed, label=""):
    print(f"{label}crosscheck max_div {a['crosscheck_max_divergence']:.3e} "
          f"(mismatches {a['crosscheck_hyper_mismatches']})  "
          f"structural_breaches {a['structural_breaches']}  "
          f"planted_effective {a['planted_effective']}/{a['planted_replicates'] + a['planted_controls']}  "
          f"false_assurance {a['false_assurance_measured']:.4f} "
          f"(limit {a['fa_limit']:.2f})  mono_violations "
          f"{a['monotonicity_violations']}+{a['fpc_violations']}  "
          f"safety_ok {a['safety_ok']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--controls", type=int, default=12)
    ap.add_argument("--population", type=int, default=40000, help="test items per control")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--trials", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "evidence"))
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    config = E.Config()
    bundle, a = run_once(args.controls, args.population, args.seed, config)
    items_total = args.controls * args.population
    print(f"\n=== QA attribute sampling (seed {args.seed}, {args.controls} controls, "
          f"{items_total:,} items) ===")
    _print_summary(a, args.seed)
    print(f"conclusions {a['conclusions']}  items tested {a['items_tested']:,} "
          f"({a['test_coverage']:.2%} of population)")

    failed = not a["safety_ok"]
    if args.trials:
        for t in range(args.trials):
            s = args.seed + 1 + t
            _, at = run_once(args.controls, args.population, s, config)
            _print_summary(at, s, label=f"  trial seed {s}: ")
            failed = failed or not at["safety_ok"]

    # ---- safety build gate ----
    if failed:
        print("\nSAFETY GATE FAILED:")
        for gate, ok in a["gates"].items():
            if not ok:
                print(f"   {gate}")
        if args.trials:
            print("   (or a trial seed breached — see trial lines above)")
        return 1

    manifest = {"framework": "qa-sampling", "seed": args.seed, "controls": args.controls,
                "population_per_control": args.population, "items_total": items_total,
                "confidence": DESIGN_CONFIDENCE, "design_risk_floor": DESIGN_RISK,
                "false_assurance_margin": FA_MARGIN, "crosscheck_tolerance": CROSSCHECK_TOL,
                "git_sha": _git_sha(),
                "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                .strftime("%Y-%m-%d %H:%M UTC")}
    if not args.no_write and args.trials == 0:
        report = render_report(bundle["records"], a, bundle["reps"], bundle["cal_rows"],
                               bundle["mono_rows"], bundle["demo"], manifest)
        write_evidence(args.out, bundle["records"], a, manifest, report,
                       bundle["xc_rows"], bundle["mono_rows"])
        print(f"\nevidence written -> {args.out}/  (safety gate PASSED)")
    else:
        print("\nsafety gate PASSED (no evidence written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
