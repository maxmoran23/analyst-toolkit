"""
Synthetic data generator for investigations case-file QA validation.

Produces cases.csv with KNOWN ground truth: completed investigation case files
labelled with whether they carry a planted CRITICAL deficiency and, for every
case, the construction category. Everything is invented and seeded; re-running
with the same --seed reproduces byte-identical files.

The population mirrors the real shape of a second-line QA queue: most files are
clean or carry only correctable issues, with a thin band of files that must
never pass QA. The plants are ADVERSARIAL by design — each is an
otherwise-pristine, well-scored file hiding exactly one critical defect, so a
score-only policy would pass it and only the named check catches it.

Non-critical categories (label 0):
  clean            fully compliant file            -> should QA_PASS
  minor_findings   1-2 MINOR issues only           -> QA_PASS with advisory notes
  major_findings   1-2 MAJOR issues, no critical   -> REMEDIATE (never REWORK)

Critical plants (label 1, each names its expected check):
  plant_uncited_disposition   complete-looking file whose disposition rationale
                              cites zero (or too few) documented evidence items
  plant_hidden_contradiction  corroborated typology evidence on file, closed as
                              no-finding — pristine everywhere else
  plant_missed_escalation     documented escalation-trigger facts, closed as
                              normal with no escalation flagged
  plant_missing_mandatory     one mandatory element absent (subject ID, account
                              scope, lookback, or disposition rationale)
  plant_unreviewed_scope      closed as no-finding with scope elements left
                              unreviewed
"""
from __future__ import annotations

import argparse
import csv
import os
import random
import sys

# Policy tables are shared with the engine so constructed timelines/lookbacks sit
# where intended relative to policy. Ground truth stays construction-based: the
# label and category are assigned by HOW the case is built, never by the engine.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scorer import (CASE_TYPES, DISPOSITION_CLEARED, DISPOSITION_ESCALATED,  # noqa: E402
                    MIN_LOOKBACK_DAYS, SLA_DAYS)

CASE_TYPE_WEIGHTS = [0.30, 0.20, 0.15, 0.15, 0.20]
SOURCE_TYPES = ["transaction_records", "account_statements", "kyc_file",
                "open_source", "negative_news_search", "internal_referral",
                "correspondence"]
FIVE_W = ["who", "what", "when", "where", "why"]
NARRATIVE_FIELDS = ["case_background", "activity_reviewed", "conclusion"]

CATEGORIES = ["clean", "minor_findings", "major_findings",
              "plant_uncited_disposition", "plant_hidden_contradiction",
              "plant_missed_escalation", "plant_missing_mandatory",
              "plant_unreviewed_scope"]
CATEGORY_WEIGHTS = [0.55, 0.15, 0.12, 0.036, 0.036, 0.036, 0.036, 0.036]

MINOR_ISSUES = ["single_source", "sla_minor", "escalation_without_trigger"]
MAJOR_ISSUES = ["lookback_short", "sla_material", "missing_5w",
                "no_chronology", "empty_narrative"]
MANDATORY_ELEMENTS = ["subject", "account_scope", "lookback", "rationale"]

EXPECTED_CHECK = {
    "plant_uncited_disposition": "unsupported_disposition",
    "plant_hidden_contradiction": "contradictory_disposition",
    "plant_missed_escalation": "missed_escalation",
    "plant_missing_mandatory": "missing_mandatory_element",
    "plant_unreviewed_scope": "cleared_with_unreviewed_scope",
}


def _clean_base(cid, rng, force_cleared=False):
    """A fully compliant case file. Escalated files (a finding, routed onward)
    are a realistic share of the closed-case population."""
    ct = rng.choices(CASE_TYPES, CASE_TYPE_WEIGHTS)[0]
    sla = SLA_DAYS[ct]
    escalated = (not force_cleared) and rng.random() < 0.15
    a2o = rng.randint(1, 5)
    total = max(a2o + 1, int(sla * rng.uniform(0.40, 0.95)))
    scope_total = rng.randint(3, 8)
    c = {
        "case_id": cid, "case_type": ct,
        "subject_identified": 1, "account_scope_documented": 1,
        "lookback_days": int(MIN_LOOKBACK_DAYS[ct] * rng.uniform(1.0, 1.8)),
        "scope_elements_total": scope_total, "scope_elements_reviewed": scope_total,
        "evidence_item_count": rng.randint(3, 10),
        "evidence_source_types": "|".join(rng.sample(SOURCE_TYPES, rng.randint(2, 4))),
        "corroborated_typology": 0,
        "disposition": DISPOSITION_CLEARED,
        "rationale_claim_count": rng.randint(2, 6),
        "rationale_cited_count": 0,  # set below == claims
        "escalation_trigger_count": 0, "escalation_flag": 0,
        "alert_to_open_days": a2o, "open_to_complete_days": total - a2o,
        "chronology_present": 1, "missing_5w": "", "empty_narrative_fields": "",
    }
    c["rationale_cited_count"] = c["rationale_claim_count"]
    if escalated:
        c["disposition"] = DISPOSITION_ESCALATED
        c["corroborated_typology"] = 1 if rng.random() < 0.7 else 0
        c["escalation_trigger_count"] = rng.randint(1, 3)
        c["escalation_flag"] = 1
    return c


def _set_total_days(c, total, rng):
    a2o = rng.randint(1, 5)
    c["alert_to_open_days"] = a2o
    c["open_to_complete_days"] = max(1, total - a2o)


def _apply_minor(c, issue, rng):
    sla = SLA_DAYS[c["case_type"]]
    if issue == "single_source":
        c["evidence_source_types"] = rng.choice(SOURCE_TYPES)
    elif issue == "sla_minor":
        _set_total_days(c, int(sla * rng.uniform(1.05, 1.45)), rng)
    else:  # escalation_without_trigger (only constructed on cleared files)
        c["escalation_flag"] = 1
        c["escalation_trigger_count"] = 0


def _apply_major(c, issue, rng):
    ct, sla = c["case_type"], SLA_DAYS[c["case_type"]]
    if issue == "lookback_short":
        c["lookback_days"] = max(1, int(MIN_LOOKBACK_DAYS[ct] * rng.uniform(0.30, 0.85)))
    elif issue == "sla_material":
        _set_total_days(c, int(sla * rng.uniform(1.60, 2.60)), rng)
    elif issue == "missing_5w":
        c["missing_5w"] = "|".join(rng.sample(FIVE_W, rng.randint(1, 2)))
    elif issue == "no_chronology":
        c["chronology_present"] = 0
    else:  # empty_narrative
        c["empty_narrative_fields"] = "|".join(
            rng.sample(NARRATIVE_FIELDS, rng.randint(1, 2)))


def make_cases(n, rng):
    out = []
    for i in range(n):
        cid = "CASE-%07d" % i
        cat = rng.choices(CATEGORIES, CATEGORY_WEIGHTS)[0]

        if cat == "clean":
            c = _clean_base(cid, rng)
        elif cat == "minor_findings":
            # cleared base so the escalation_without_trigger minor never
            # collides with a genuine escalation posture
            c = _clean_base(cid, rng, force_cleared=True)
            for issue in rng.sample(MINOR_ISSUES, rng.randint(1, 2)):
                _apply_minor(c, issue, rng)
        elif cat == "major_findings":
            c = _clean_base(cid, rng, force_cleared=True)
            for issue in rng.sample(MAJOR_ISSUES, rng.randint(1, 2)):
                _apply_major(c, issue, rng)
        else:
            # ---- adversarial critical plants: pristine except ONE defect ----
            c = _clean_base(cid, rng, force_cleared=True)
            if cat == "plant_uncited_disposition":
                # 70% cite zero evidence, 30% cite only some claims
                claims = c["rationale_claim_count"]
                c["rationale_cited_count"] = 0 if rng.random() < 0.70 \
                    else rng.randint(1, claims - 1)
            elif cat == "plant_hidden_contradiction":
                c["corroborated_typology"] = 1
            elif cat == "plant_missed_escalation":
                c["escalation_trigger_count"] = rng.randint(1, 3)
                c["escalation_flag"] = 0
            elif cat == "plant_missing_mandatory":
                which = rng.choice(MANDATORY_ELEMENTS)
                if which == "subject":
                    c["subject_identified"] = 0
                elif which == "account_scope":
                    c["account_scope_documented"] = 0
                elif which == "lookback":
                    c["lookback_days"] = 0
                else:  # rationale
                    c["rationale_claim_count"] = 0
                    c["rationale_cited_count"] = 0
            else:  # plant_unreviewed_scope
                total = c["scope_elements_total"]
                c["scope_elements_reviewed"] = total - rng.randint(1, min(3, total - 1))
            # cosmetic noise on a quarter of plants — they still look well-worked
            if rng.random() < 0.25:
                c["evidence_source_types"] = rng.choice(SOURCE_TYPES)

        c["label"] = 1 if cat.startswith("plant_") else 0
        c["category"] = cat
        c["expected_check"] = EXPECTED_CHECK.get(cat, "")
        out.append(c)
    return out


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cases", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    args = ap.parse_args()
    rng = random.Random(args.seed)
    rows = make_cases(args.cases, rng)
    write_csv(os.path.join(args.out, "cases.csv"), rows)
    crit = sum(r["label"] for r in rows)
    print(f"cases: {len(rows)} ({crit} critical-deficient plants, "
          f"{len(rows) - crit} non-critical) -> {args.out}/cases.csv   [seed={args.seed}]")


if __name__ == "__main__":
    main()
