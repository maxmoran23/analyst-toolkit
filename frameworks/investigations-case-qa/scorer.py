"""
Investigations case-file QA engine — reference implementation.

Consumes a COMPLETED financial-crime investigation case file (a structured record
of what the investigator documented: scope, evidence, disposition rationale,
timeline, escalation posture, narrative structure) and returns a second-line QA
disposition with a NAMED rationale. The full methodology is in METHODOLOGY.md;
this file is its executable form.

Design posture (parallel to the screening and monitoring frameworks):
  * The engine NEVER reopens, overrides, or re-decides the investigative
    disposition, never files anything, and never auto-approves a deficient file.
    It grades the FILE, not the customer, and routes the result to humans.
  * QA_PASS is granted only on a PROVABLE named basis: every critical and major
    structural check demonstrably clean. It is never granted on score alone.
  * ANY CRITICAL deficiency — an unsupported disposition, a disposition that
    contradicts the evidence, a missed escalation trigger, a missing mandatory
    element, or a no-finding closure over unreviewed scope — makes QA_PASS
    unreachable regardless of the quality score. This is a hard gate in the
    disposition logic, not a weight.

Critical-deficiency safety is therefore structural: the QA_PASS branch is only
reachable when zero critical checks have fired. The validation harness enforces
this as a build gate (every planted critical deficiency detected; zero
critical-deficient cases passed).

Everything is deterministic. Same case record -> same QA disposition.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.aggregations import clamp  # noqa: E402
from _lib.rules import Rule, RuleSet  # noqa: E402
from _lib.scoring import weighted_composite  # noqa: E402

# --- policy reference tables (illustrative; a deployment substitutes its own) ---
CASE_TYPES = ["STRUCTURING", "FUNNEL_ACCOUNT", "LAYERING_PASSTHROUGH",
              "SANCTIONS_REFERRAL", "FRAUD_REFERRAL"]
SLA_DAYS = {  # policy SLA, alert receipt -> case completion
    "STRUCTURING": 30, "FUNNEL_ACCOUNT": 45, "LAYERING_PASSTHROUGH": 45,
    "SANCTIONS_REFERRAL": 20, "FRAUD_REFERRAL": 30,
}
MIN_LOOKBACK_DAYS = {  # policy minimum review lookback per case type
    "STRUCTURING": 90, "FUNNEL_ACCOUNT": 180, "LAYERING_PASSTHROUGH": 180,
    "SANCTIONS_REFERRAL": 90, "FRAUD_REFERRAL": 60,
}

DISPOSITION_CLEARED = "CLOSED_NO_FINDING"
DISPOSITION_ESCALATED = "ESCALATED_WITH_FINDING"

# QA dimensions and their weights in the 0-100 quality composite (sum 1.0).
DIM_WEIGHTS = {
    "completeness": 0.25,
    "evidence_support": 0.25,
    "consistency": 0.20,
    "narrative_quality": 0.20,
    "timeliness": 0.10,
}
# Per-fired-check deduction from the 100-point dimension sub-score, by severity
# class. A CRITICAL zeroes its dimension; the DISPOSITION gate, not the score,
# is what makes a critical un-passable.
DEDUCTION = {"CRITICAL": 100.0, "MAJOR": 45.0, "MINOR": 15.0}


@dataclass
class Config:
    """Tunable operating point. Defaults are the conservative posture; recalibrate
    against a labelled sample of your own QA outcomes before reliance (tuning.md)."""
    pass_score: float = 85.0          # quality score required for QA_PASS (with no critical/major)
    sla_material_multiple: float = 1.5  # SLA overrun beyond this multiple is a MAJOR breach


@dataclass
class CaseFile:
    """A completed investigation case record, as structured fields. Narrative
    elements are represented as structural presence indicators — the QA engine
    checks that the file is complete, supported, consistent, timely, and
    structurally narrated; it does not judge prose quality."""
    case_id: str
    case_type: str = "STRUCTURING"
    # completeness elements
    subject_identified: bool = True        # subject identification documented
    account_scope_documented: bool = True  # accounts in scope enumerated
    lookback_days: int = 0                 # review lookback (0 = absent)
    scope_elements_total: int = 0          # scope elements the case type requires
    scope_elements_reviewed: int = 0       # scope elements actually reviewed
    # evidence
    evidence_item_count: int = 0
    evidence_source_types: list = field(default_factory=list)  # e.g. transaction_records, kyc_file
    corroborated_typology: bool = False    # evidence on file corroborates the alert typology
    # disposition
    disposition: str = DISPOSITION_CLEARED  # CLOSED_NO_FINDING / ESCALATED_WITH_FINDING
    rationale_claim_count: int = 0          # discrete claims in the disposition rationale
    rationale_cited_count: int = 0          # claims referencing >=1 documented evidence item
    # escalation posture
    escalation_trigger_count: int = 0       # documented facts that require escalation per policy
    escalation_flag: bool = False           # the case record's escalation indicator
    # timeline milestones
    alert_to_open_days: int = 0
    open_to_complete_days: int = 0
    # narrative structure
    chronology_present: bool = True
    missing_5w: list = field(default_factory=list)          # among who/what/when/where/why
    empty_narrative_fields: list = field(default_factory=list)  # mandatory narrative fields left empty


@dataclass
class QAReview:
    disposition: str          # QA_PASS / REMEDIATE / REWORK_AND_ESCALATE
    quality_score: float      # 0-100 weighted composite, for ranking and calibration
    dimension_scores: dict    # per-dimension 0-100 sub-scores
    deficiencies: list        # [{check, dimension, severity_class, detail}]
    reason: str               # the NAMED rationale (audit trail)

    def as_row(self) -> dict:
        return {"disposition": self.disposition,
                "quality_score": round(self.quality_score, 2),
                "deficiencies": ";".join(d["check"] for d in self.deficiencies),
                "reason": self.reason}


# ---------------------------------------------------------------------------
# Named QA checks (see METHODOLOGY.md section 4). A check tagged with a
# deficiency class (the Rule tag) is CRITICAL — the signal that a case cannot
# be QA_PASS. Untagged checks are MAJOR or MINOR per SEVERITY_CLASS below.
# ---------------------------------------------------------------------------
def _missing_mandatory(f):
    missing = []
    if not f["subject_identified"]:
        missing.append("subject identification")
    if not f["account_scope_documented"]:
        missing.append("account scope")
    if f["lookback_days"] <= 0:
        missing.append("lookback period")
    if f["rationale_claim_count"] <= 0:
        missing.append("disposition rationale")
    fired = bool(missing)
    sev = clamp(0.85 + 0.05 * len(missing)) if fired else 0.0
    return fired, sev, "mandatory element(s) absent: " + ", ".join(missing)


def _lookback_below(f):
    lb, pol = f["lookback_days"], f["min_lookback"]
    fired = 0 < lb < pol
    sev = clamp(0.35 + 0.35 * (1 - lb / pol)) if fired else 0.0
    return fired, sev, f"lookback {lb}d below the {pol}d policy minimum for {f['case_type']}"


def _unsupported(f):
    claims, cited = f["rationale_claim_count"], f["rationale_cited_count"]
    uncited = claims - cited
    fired = claims > 0 and uncited > 0
    sev = clamp(0.70 + 0.30 * uncited / claims) if fired else 0.0
    return fired, sev, (f"{uncited} of {claims} disposition-rationale claims reference "
                        f"no documented evidence item")


def _unreviewed_clear(f):
    total, reviewed = f["scope_elements_total"], f["scope_elements_reviewed"]
    un = total - reviewed
    fired = f["disposition"] == DISPOSITION_CLEARED and un > 0
    sev = clamp(0.70 + 0.30 * un / total) if fired and total else (1.0 if fired else 0.0)
    return fired, sev, (f"closed as no-finding with {un} of {total} scope elements "
                        f"unreviewed — the clearance cannot be supported")


def _single_source(f):
    n, kinds = f["evidence_item_count"], len(set(f["evidence_source_types"]))
    fired = n >= 1 and kinds == 1
    return fired, (0.20 if fired else 0.0), \
        f"all {n} evidence items drawn from a single source type (no corroborating source)"


def _contradiction(f):
    fired = f["corroborated_typology"] and f["disposition"] == DISPOSITION_CLEARED
    return fired, (1.0 if fired else 0.0), \
        (f"corroborated {f['case_type']} evidence on file, yet the case is closed "
         f"as no-finding — disposition contradicts the evidence severity")


def _missed_escalation(f):
    n = f["escalation_trigger_count"]
    fired = n >= 1 and not f["escalation_flag"]
    sev = clamp(0.80 + 0.10 * n) if fired else 0.0
    return fired, sev, f"{n} documented escalation trigger(s) present with no escalation flagged"


def _escalation_wo_trigger(f):
    fired = f["escalation_flag"] and f["escalation_trigger_count"] == 0
    return fired, (0.15 if fired else 0.0), \
        "escalation flagged with no documented trigger on file"


def _sla_material(f):
    total, sla, mult = f["total_days"], f["sla_days"], f["sla_material_multiple"]
    ratio = total / sla if sla else 0.0
    fired = ratio > mult
    sev = clamp(0.45 + 0.15 * (ratio - mult)) if fired else 0.0
    return fired, sev, f"completed in {total}d against a {sla}d SLA ({ratio:.1f}x — material breach)"


def _sla_minor(f):
    total, sla, mult = f["total_days"], f["sla_days"], f["sla_material_multiple"]
    fired = sla < total <= sla * mult
    return fired, (0.25 if fired else 0.0), \
        f"completed in {total}d against a {sla}d SLA (within the material-breach tolerance)"


def _incomplete_5w(f):
    m = f["missing_5w"]
    fired = bool(m)
    sev = clamp(0.35 + 0.08 * len(m)) if fired else 0.0
    return fired, sev, f"narrative missing {'/'.join(m)} coverage"


def _missing_chronology(f):
    fired = not f["chronology_present"]
    return fired, (0.45 if fired else 0.0), "no chronology of events in the narrative"


def _empty_narrative(f):
    e = f["empty_narrative_fields"]
    fired = bool(e)
    sev = clamp(0.35 + 0.10 * len(e)) if fired else 0.0
    return fired, sev, "mandatory narrative field(s) empty: " + ", ".join(e)


# The Rule tag names the CRITICAL deficiency class; untagged checks are graded
# by SEVERITY_CLASS. RuleSet.typology_hits() therefore returns exactly the fired
# critical deficiencies — the structural no-pass signal.
CHECKS = RuleSet([
    Rule("missing_mandatory_element", _missing_mandatory, "MISSING_MANDATORY_ELEMENT"),
    Rule("lookback_below_policy", _lookback_below, ""),
    Rule("unsupported_disposition", _unsupported, "UNSUPPORTED_DISPOSITION"),
    Rule("cleared_with_unreviewed_scope", _unreviewed_clear, "CLEARED_UNREVIEWED_SCOPE"),
    Rule("single_source_evidence", _single_source, ""),
    Rule("contradictory_disposition", _contradiction, "DISPOSITION_CONTRADICTION"),
    Rule("missed_escalation", _missed_escalation, "MISSED_ESCALATION"),
    Rule("escalation_without_trigger", _escalation_wo_trigger, ""),
    Rule("sla_breach_material", _sla_material, ""),
    Rule("sla_breach_minor", _sla_minor, ""),
    Rule("incomplete_5w", _incomplete_5w, ""),
    Rule("missing_chronology", _missing_chronology, ""),
    Rule("empty_narrative_field", _empty_narrative, ""),
])

DIMENSION = {
    "missing_mandatory_element": "completeness",
    "lookback_below_policy": "completeness",
    "unsupported_disposition": "evidence_support",
    "cleared_with_unreviewed_scope": "evidence_support",
    "single_source_evidence": "evidence_support",
    "contradictory_disposition": "consistency",
    "missed_escalation": "consistency",
    "escalation_without_trigger": "consistency",
    "sla_breach_material": "timeliness",
    "sla_breach_minor": "timeliness",
    "incomplete_5w": "narrative_quality",
    "missing_chronology": "narrative_quality",
    "empty_narrative_field": "narrative_quality",
}
SEVERITY_CLASS = {
    "missing_mandatory_element": "CRITICAL",
    "lookback_below_policy": "MAJOR",
    "unsupported_disposition": "CRITICAL",
    "cleared_with_unreviewed_scope": "CRITICAL",
    "single_source_evidence": "MINOR",
    "contradictory_disposition": "CRITICAL",
    "missed_escalation": "CRITICAL",
    "escalation_without_trigger": "MINOR",
    "sla_breach_material": "MAJOR",
    "sla_breach_minor": "MINOR",
    "incomplete_5w": "MAJOR",
    "missing_chronology": "MAJOR",
    "empty_narrative_field": "MAJOR",
}


def review_case(case: CaseFile, config: Config = Config()) -> QAReview:
    f = {
        "case_type": case.case_type,
        "subject_identified": case.subject_identified,
        "account_scope_documented": case.account_scope_documented,
        "lookback_days": case.lookback_days,
        "min_lookback": MIN_LOOKBACK_DAYS.get(case.case_type, 90),
        "scope_elements_total": case.scope_elements_total,
        "scope_elements_reviewed": case.scope_elements_reviewed,
        "evidence_item_count": case.evidence_item_count,
        "evidence_source_types": case.evidence_source_types,
        "corroborated_typology": case.corroborated_typology,
        "disposition": case.disposition,
        "rationale_claim_count": case.rationale_claim_count,
        "rationale_cited_count": case.rationale_cited_count,
        "escalation_trigger_count": case.escalation_trigger_count,
        "escalation_flag": case.escalation_flag,
        "total_days": case.alert_to_open_days + case.open_to_complete_days,
        "sla_days": SLA_DAYS.get(case.case_type, 30),
        "sla_material_multiple": config.sla_material_multiple,
        "chronology_present": case.chronology_present,
        "missing_5w": case.missing_5w,
        "empty_narrative_fields": case.empty_narrative_fields,
    }

    results = CHECKS.evaluate(f)
    fired = RuleSet.fired(results)
    criticals = RuleSet.typology_hits(results)  # tagged == CRITICAL deficiency class
    majors = [r for r in fired if SEVERITY_CLASS[r.name] == "MAJOR"]
    minors = [r for r in fired if SEVERITY_CLASS[r.name] == "MINOR"]

    dim_scores = {d: 100.0 for d in DIM_WEIGHTS}
    for r in fired:
        dim_scores[DIMENSION[r.name]] = max(
            0.0, dim_scores[DIMENSION[r.name]] - DEDUCTION[SEVERITY_CLASS[r.name]])
    score = weighted_composite(dim_scores, DIM_WEIGHTS)

    deficiencies = [{"check": r.name, "dimension": DIMENSION[r.name],
                     "severity_class": SEVERITY_CLASS[r.name], "detail": r.detail}
                    for r in fired]

    # ---- QA disposition, in firing order (METHODOLOGY.md section 6) ----
    # 1. ANY critical deficiency -> the case cannot pass QA, regardless of score.
    if criticals:
        classes = "/".join(sorted({r.typology for r in criticals}))
        details = "; ".join(r.detail for r in criticals)
        return QAReview("REWORK_AND_ESCALATE", score, dim_scores, deficiencies,
                        f"Critical deficiency ({classes}): {details}. Return to the "
                        f"investigator for rework and route the QA finding to the "
                        f"investigations supervisor.")
    # 2. Major deficiencies (no critical) -> targeted remediation.
    if majors:
        details = "; ".join(r.detail for r in majors)
        return QAReview("REMEDIATE", score, dim_scores, deficiencies,
                        f"Major deficiency(ies): {details}. Return to the investigator "
                        f"for correction; no critical deficiency present.")
    # 3. Score below the pass threshold (no critical or major) -> remediation.
    if score < config.pass_score:
        details = "; ".join(r.detail for r in minors) or "accumulated minor findings"
        return QAReview("REMEDIATE", score, dim_scores, deficiencies,
                        f"Quality score {score:.0f} below the {config.pass_score:.0f} "
                        f"pass threshold — {details}.")
    # 4. QA_PASS, only on the provable named basis.
    reason = ("Every critical and major QA check is provably clean: mandatory "
              "elements complete, all disposition-rationale claims evidence-cited, "
              "disposition consistent with the evidence on file, escalation posture "
              "correct, no material SLA breach, narrative structurally complete.")
    if minors:
        reason += " Advisory (minor) observations: " + "; ".join(r.detail for r in minors) + "."
    return QAReview("QA_PASS", score, dim_scores, deficiencies, reason)


if __name__ == "__main__":
    import json
    clean = CaseFile(
        "CASE-0001", case_type="STRUCTURING", lookback_days=120,
        scope_elements_total=5, scope_elements_reviewed=5, evidence_item_count=6,
        evidence_source_types=["transaction_records", "kyc_file", "open_source"],
        disposition=DISPOSITION_CLEARED, rationale_claim_count=4, rationale_cited_count=4,
        alert_to_open_days=2, open_to_complete_days=18)
    hidden_contradiction = CaseFile(
        "CASE-0002", case_type="FUNNEL_ACCOUNT", lookback_days=200,
        scope_elements_total=6, scope_elements_reviewed=6, evidence_item_count=9,
        evidence_source_types=["transaction_records", "account_statements", "kyc_file"],
        corroborated_typology=True,  # evidence corroborates the funnel pattern...
        disposition=DISPOSITION_CLEARED,  # ...yet the case is closed as no-finding
        rationale_claim_count=5, rationale_cited_count=5,
        alert_to_open_days=3, open_to_complete_days=30)
    for c in (clean, hidden_contradiction):
        r = review_case(c)
        print(f"\n{c.case_id}:")
        print(json.dumps({**r.as_row(), "dimension_scores": r.dimension_scores}, indent=2))
