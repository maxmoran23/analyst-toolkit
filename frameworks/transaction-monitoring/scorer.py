"""
Transaction-monitoring alert-scoring engine — reference implementation.

Consumes a TM alert (a customer plus a window of aggregated transaction features
that tripped a monitoring rule) and returns a disposition with a NAMED rationale.
The full methodology is in METHODOLOGY.md; this file is its executable form.

Design posture (parallel to the sanctions framework, same conservative stance):
  * The engine NEVER auto-files a SAR and never auto-closes an alert that shows a
    recognised laundering typology.
  * It auto-CLOSES an alert only on a NAMED benign cause, and only when NO typology
    rule has fired:
        within_profile      activity is within the customer's expected baseline
        documented_context  the firing rule is explained by the customer's
                            documented business (e.g. import/export → geography)
        below_typology      a typology indicator is present but below its pattern
                            threshold (e.g. 2 near-threshold deposits; structuring
                            requires >=3)
  * Anything with a typology hit is kept open — escalated if strong, else routed to
    an analyst. Unexplained deviation with no typology is also kept open.

False-negative safety is structural: a genuinely suspicious case fires a typology
rule, so it can never reach an auto-close branch. The validation harness enforces
this as a build gate.

Everything is deterministic. Same inputs -> same disposition.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.aggregations import ratio_to_expected, saturating, clamp  # noqa: E402
from _lib.rules import Rule, RuleSet  # noqa: E402

CTR_THRESHOLD = 10000.0   # reporting threshold the structuring rule sits under
SIG_AMOUNT = 50000.0      # throughput above which pass-through is material

# Which non-typology rules a documented business type legitimately explains. A
# fired non-typology rule that is fully explained does not, on its own, keep an
# alert open.
EXPLAINS = {
    "import_export": {"geo_risk", "velocity_spike"},
    "cash_intensive": {"velocity_spike"},
    "remittance": {"geo_risk", "velocity_spike"},
    "payroll": {"velocity_spike"},
    "": set(),
}
RISK_AMP = {"LOW": 1.0, "MEDIUM": 1.08, "HIGH": 1.20}


@dataclass
class Config:
    """Tunable operating point. Defaults are the conservative posture; recalibrate
    against a labelled sample before production use (see tuning.md)."""
    escalate_severity: float = 0.60   # typology severity at/above which to escalate
    within_tol: float = 1.50          # amount/count ratio treated as 'on profile'
    context_tol: float = 3.00         # deviation a documented context tolerates
    soft_severity_floor: float = 0.30  # non-typology severity below this is 'minor'
    review_high: float = 0.50         # suspicion_score -> HIGH analyst priority
    review_medium: float = 0.25       # suspicion_score -> MEDIUM


@dataclass
class CustomerProfile:
    customer_id: str
    segment: str = "RETAIL"            # RETAIL / SMB / CORPORATE / MSB
    risk_rating: str = "LOW"           # LOW / MEDIUM / HIGH
    expected_amount: float = 0.0       # expected total throughput over the window
    expected_count: float = 0.0        # expected transaction count over the window
    home_country: str = ""
    business_type: str = ""            # "" / import_export / cash_intensive / remittance / payroll


@dataclass
class Alert:
    alert_id: str
    customer_id: str
    window_days: int = 30
    total_in: float = 0.0
    total_out: float = 0.0
    txn_count: int = 0
    near_threshold_count: int = 0      # deposits just under CTR_THRESHOLD
    distinct_in_cp: int = 0            # distinct inbound counterparties
    distinct_out_cp: int = 0           # distinct outbound counterparties
    passthrough_ratio: float = 0.0     # min(in,out)/max(in,out) over the window
    same_day: bool = False             # in and out occur same-day (pass-through timing)
    high_risk_geo_fraction: float = 0.0  # fraction of value to/from higher-risk geos


@dataclass
class Disposition:
    decision: str            # AUTO_CLOSE / ANALYST_REVIEW / ESCALATE
    priority: str            # HIGH / MEDIUM / LOW for ANALYST_REVIEW, else ""
    suspicion_score: float   # [0,1], for ranking and calibration
    reason: str              # the NAMED rationale (audit trail)
    components: dict

    def as_row(self) -> dict:
        return {"decision": self.decision, "priority": self.priority,
                "suspicion_score": round(self.suspicion_score, 4), "reason": self.reason}


# ---------------------------------------------------------------------------
# Typology and risk rules (see METHODOLOGY.md §4)
# ---------------------------------------------------------------------------
def _structuring(f):
    n = f["near_threshold_count"]
    fired = n >= 3
    sev = clamp(0.55 + 0.10 * (n - 3)) if fired else 0.0
    return fired, sev, f"{n} deposits just under the {int(CTR_THRESHOLD):,} reporting threshold"


def _funnel(f):
    din, dout = f["distinct_in_cp"], f["distinct_out_cp"]
    concentrated = f["total_in"] > 0 and f["total_out"] >= 0.6 * f["total_in"]
    fired = din >= 5 and dout <= 2 and concentrated
    sev = clamp(0.50 + 0.05 * (din - 5)) if fired else 0.0
    return fired, sev, f"{din} inbound sources concentrated into {dout} outbound destination(s)"


def _passthrough(f):
    r = f["passthrough_ratio"]
    fired = r >= 0.80 and f["same_day"] and f["total_in"] >= SIG_AMOUNT
    sev = clamp(0.40 + 0.5 * (r - 0.80) / 0.20) if fired else 0.0
    return fired, sev, f"{r:.0%} of inflow moved out same-day"


def _velocity(f):  # non-typology deviation signal
    cr = f["count_ratio"]
    fired = cr >= 3.0
    sev = clamp(0.20 + saturating(cr - 3.0, 6.0)) if fired else 0.0
    return fired, sev, f"transaction count {cr:.1f}x the customer baseline"


def _geo(f):  # non-typology risk factor
    g = f["high_risk_geo_fraction"]
    fired = g >= 0.50
    sev = clamp(0.25 + 0.35 * g) if fired else 0.0
    return fired, sev, f"{g:.0%} of value to/from higher-risk jurisdictions"


RULES = RuleSet([
    Rule("structuring", _structuring, "STRUCTURING"),
    Rule("funnel", _funnel, "FUNNEL_ACCOUNT"),
    Rule("rapid_passthrough", _passthrough, "LAYERING_PASSTHROUGH"),
    Rule("velocity_spike", _velocity, ""),
    Rule("geo_risk", _geo, ""),
])


def _near_misses(f) -> list:
    """Typology indicators present but below their pattern threshold — the basis
    for a 'below_typology' auto-close, each named for the audit trail."""
    out = []
    n = f["near_threshold_count"]
    if 1 <= n <= 2:
        out.append(f"{n} near-threshold deposit(s) — below the structuring pattern (requires 3+)")
    if 3 <= f["distinct_in_cp"] <= 4 and f["distinct_out_cp"] <= 2:
        out.append(f"{f['distinct_in_cp']} inbound sources — below the funnel pattern (requires 5+)")
    if 0.60 <= f["passthrough_ratio"] < 0.80:
        out.append(f"{f['passthrough_ratio']:.0%} pass-through — below the layering threshold (80%+)")
    return out


def score_alert(alert: Alert, profile: CustomerProfile,
                config: Config = Config()) -> Disposition:
    throughput = alert.total_in + alert.total_out
    amount_ratio = ratio_to_expected(throughput, profile.expected_amount)
    count_ratio = ratio_to_expected(alert.txn_count, profile.expected_count)

    f = {
        "near_threshold_count": alert.near_threshold_count,
        "distinct_in_cp": alert.distinct_in_cp,
        "distinct_out_cp": alert.distinct_out_cp,
        "total_in": alert.total_in, "total_out": alert.total_out,
        "passthrough_ratio": alert.passthrough_ratio, "same_day": alert.same_day,
        "high_risk_geo_fraction": alert.high_risk_geo_fraction,
        "amount_ratio": amount_ratio, "count_ratio": count_ratio,
    }

    results = RULES.evaluate(f)
    fired = RuleSet.fired(results)
    typ_hits = RuleSet.typology_hits(results)
    sev = RuleSet.max_severity(results)

    deviation_mag = saturating(max(0.0, amount_ratio - 1) + max(0.0, count_ratio - 1), 3.0)
    score = clamp(max(sev, deviation_mag))
    if typ_hits:
        score = clamp(score + 0.15 * min(len(typ_hits), 2))
    score = clamp(score * RISK_AMP.get(profile.risk_rating, 1.0))

    components = {
        "amount_ratio": round(amount_ratio, 3) if amount_ratio != float("inf") else "inf",
        "count_ratio": round(count_ratio, 3) if count_ratio != float("inf") else "inf",
        "max_severity": round(sev, 3),
        "fired_rules": [r.name for r in fired],
        "typology_hits": [r.typology for r in typ_hits],
        "business_type": profile.business_type,
        "risk_rating": profile.risk_rating,
    }

    # ---- disposition: typology hits keep an alert open; auto-close needs a named
    # benign cause and NO typology hit (the false-negative safety boundary) ----
    if typ_hits:
        names = ", ".join(r.detail for r in typ_hits)
        if sev >= config.escalate_severity:
            return Disposition("ESCALATE", "", score,
                               f"Recognised typology ({'/'.join(sorted({r.typology for r in typ_hits}))}): "
                               f"{names}. Route to investigation for a SAR decision.", components)
        return Disposition("ANALYST_REVIEW", "HIGH", score,
                           f"Emerging typology pattern ({names}) below the escalation "
                           f"threshold — manual review.", components)

    # no typology hits -> eligible for a named auto-close
    throughput_ok = amount_ratio <= config.context_tol
    moderate = throughput_ok and count_ratio <= config.context_tol
    nontyp = [r for r in fired if not r.typology]
    explained = bool(nontyp) and all(r.name in EXPLAINS.get(profile.business_type, set())
                                     for r in nontyp)
    near = _near_misses(f)

    if amount_ratio <= config.within_tol and count_ratio <= config.within_tol \
            and sev < config.soft_severity_floor:
        return Disposition("AUTO_CLOSE", "", score,
                           "Activity within the customer's expected profile; no "
                           "typology pattern and deviation within tolerance.", components)
    # documented context gates on throughput only, not transaction count: a
    # cash-intensive or remittance business legitimately runs a high COUNT, which
    # is the very deviation the documented profile explains.
    if explained and throughput_ok:
        return Disposition("AUTO_CLOSE", "", score,
                           f"Firing signal(s) [{', '.join(r.name for r in nontyp)}] are "
                           f"consistent with the customer's documented "
                           f"{profile.business_type} profile; no typology pattern.", components)
    if near and moderate:
        return Disposition("AUTO_CLOSE", "", score,
                           f"Sub-threshold indicator only — {'; '.join(near)}.", components)

    # unexplained deviation with no typology -> keep open, ranked
    if score >= config.review_high:
        prio = "HIGH"
    elif score >= config.review_medium:
        prio = "MEDIUM"
    else:
        prio = "LOW"
    return Disposition("ANALYST_REVIEW", prio, score,
                       "Activity deviates from the expected profile without a "
                       "documented explanation or a typology pattern — manual review.",
                       components)


if __name__ == "__main__":
    import json
    prof = CustomerProfile("CUST-1", segment="RETAIL", risk_rating="LOW",
                           expected_amount=20000, expected_count=15, business_type="")
    # textbook structuring
    a = Alert("ALR-1", "CUST-1", total_in=46000, total_out=0, txn_count=5,
              near_threshold_count=5)
    d = score_alert(a, prof)
    print(json.dumps({**d.as_row(), "components": d.components}, indent=2))
