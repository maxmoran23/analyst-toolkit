"""
Data-quality rules engine for the critical data elements (CDEs) feeding
financial-crime systems — reference implementation.

Screening, monitoring, and regulatory reporting are only as good as the
name / date-of-birth / country / identifier fields they consume. This engine
answers the data-governance team's recurring question — "is this feed fit to
screen against?" — with named, auditable rules across five dimensions:

    COMPLETENESS   null/blank mandatory fields
    VALIDITY       format and domain (date parseable and in range, country in
                   the approved reference set, identifier format + check digit)
    CONSISTENCY    cross-field agreement (country vs account prefix, DOB vs
                   onboarding-date ordering, entity type vs field expectations)
    UNIQUENESS     duplicate customer records — exact natural-key duplicates and
                   near-duplicates (name similarity + shared identifier)
    TIMELINESS     staleness — last refresh beyond the policy horizon

Design posture (parallel to the other frameworks, same conservative stance):
  * Every rule binds to a CDE with a documented criticality weight; the
    screening-critical CDEs (full name, DOB, country, national identifier, and
    record uniqueness itself) carry the highest weight AND a hard gate.
  * The feed disposition is FEED_PASS / INVESTIGATE / BLOCK_FEED_TO_SCREENING.
    Any screening-critical CDE breaching its documented threshold means the
    feed can NEVER be FEED_PASS — a structural gate, not a weighted score.
  * FEED_PASS is granted only on a provable named cause (every documented
    threshold met, listed). BLOCK routes the feed and its full defect list to
    data-governance review; the engine never silently drops a record.

False-negative safety is structural: every critical defect class is detected
by a deterministic parser/rule, and the BLOCK branch is evaluated before any
pass logic, so a feed whose screening-critical defect rate breaches its
ceiling cannot reach FEED_PASS regardless of its composite score. The
validation harness enforces this as a build gate.

Everything is deterministic. Same extract -> same scorecard and disposition.
"""
from __future__ import annotations

import datetime
import os
import re
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _lib.rules import Rule, RuleSet          # noqa: E402
from _lib.match import jaro_winkler, levenshtein, soundex  # noqa: E402
from _lib.text_normalize import normalize     # noqa: E402

# The extract carries a fixed as-of date so every run is deterministic; the
# generator uses the same constant (a real deployment passes the batch date).
DEFAULT_ASOF = "2026-06-30"
DOB_FLOOR = datetime.date(1900, 1, 1)   # DOB before this is out of plausible range

# The institution's approved country reference set (ISO 3166-1 alpha-2 subset).
# Anything outside this set — including ISO-adjacent-but-wrong codes such as
# "UK" (GB is the ISO code), "EL", or retired codes ("SU", "YU", "BU") — is
# country drift: the record cannot be reliably jurisdiction-screened.
COUNTRY_REF = frozenset({
    "US", "GB", "DE", "FR", "CA", "SG", "AE", "JP", "AU", "CH", "NL", "ES",
    "IT", "BR", "MX", "IN", "ZA", "SE", "NO", "IE", "HK", "KR", "PL", "PT",
    "BE", "AT", "DK", "FI", "NZ", "LU", "CZ", "GR", "HU", "TR", "SA", "QA",
    "KW", "TH", "MY", "ID", "PH", "VN", "CL", "CO", "PE", "AR", "IL", "EG",
    "MA", "KE", "NG",
})

# National identifier contract: "HV" + 7 digits + 1 check digit, where the
# check digit is the position-weighted sum of the 7 body digits mod 10.
ID_RE = re.compile(r"^HV(\d{7})(\d)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")   # extract contract: ISO, zero-padded
PREFIX_RE = re.compile(r"^([A-Z]{2})-\d{2}$")  # account prefix: country + branch

CRITICAL, MINOR = "CRITICAL", "MINOR"

# CDE inventory: criticality weight + whether the CDE is screening-critical
# (full table with rationale in METHODOLOGY.md §3). record_uniqueness is the
# customer record itself as a data element: one party, one record.
CDE_WEIGHTS = {
    "full_name": 1.00, "dob": 1.00, "country": 1.00, "national_id": 1.00,
    "record_uniqueness": 1.00,
    "entity_type": 0.40, "onboarding_date": 0.40, "account_prefix": 0.30,
    "last_refresh": 0.50,
}
SCREENING_CRITICAL = ("full_name", "dob", "country", "national_id",
                      "record_uniqueness")

# rule name -> (dimension, CDE it binds to, severity class)
RULE_META = {
    "name_missing_active":     ("COMPLETENESS", "full_name",       CRITICAL),
    "name_missing_inactive":   ("COMPLETENESS", "full_name",       MINOR),
    "dob_missing":             ("COMPLETENESS", "dob",             CRITICAL),
    "entity_type_missing":     ("COMPLETENESS", "entity_type",     MINOR),
    "onboarding_missing":      ("COMPLETENESS", "onboarding_date", MINOR),
    "id_missing":              ("COMPLETENESS", "national_id",     MINOR),
    "dob_unparseable":         ("VALIDITY",     "dob",             CRITICAL),
    "dob_out_of_range":        ("VALIDITY",     "dob",             CRITICAL),
    "country_invalid":         ("VALIDITY",     "country",         CRITICAL),
    "id_format_invalid":       ("VALIDITY",     "national_id",     CRITICAL),
    "dob_after_onboarding":    ("CONSISTENCY",  "dob",             CRITICAL),
    "prefix_country_mismatch": ("CONSISTENCY",  "account_prefix",  MINOR),
    "entity_dob_conflict":     ("CONSISTENCY",  "entity_type",     MINOR),
    "refresh_stale":           ("TIMELINESS",   "last_refresh",    MINOR),
    "duplicate_exact":         ("UNIQUENESS",   "record_uniqueness", CRITICAL),
    "duplicate_near":          ("UNIQUENESS",   "record_uniqueness", CRITICAL),
}


def id_check(nid: str) -> bool:
    """True when the identifier matches the documented format AND its check
    digit verifies (position-weighted digit sum mod 10)."""
    m = ID_RE.match(nid)
    if not m:
        return False
    body, chk = m.group(1), int(m.group(2))
    return chk == sum((i + 1) * int(d) for i, d in enumerate(body)) % 10


def parse_iso(s: str):
    """Strict extract-contract date parse: ISO zero-padded AND a real calendar
    date. '1985-02-30' passes the format regex but fails the calendar — the
    adversarial case a naive regex check waves through. None on failure."""
    s = (s or "").strip()
    if not DATE_RE.match(s):
        return None
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


@dataclass
class Config:
    """Tunable operating point. Defaults are the conservative posture;
    recalibrate against your own labelled extracts before reliance (tuning.md)."""
    crit_ceiling: float = 0.005        # screening-critical CDE critical-defect rate ceiling
    dup_ceiling: float = 0.004         # duplicate-record rate ceiling (record_uniqueness)
    warn_fraction: float = 0.5         # warn band starts at warn_fraction * ceiling
    supporting_ceiling: float = 0.02   # supporting CDE any-defect rate ceiling
    staleness_ceiling: float = 0.10    # stale-record rate ceiling (last_refresh)
    composite_floor: float = 0.98      # weighted composite score required for FEED_PASS
    staleness_horizon_days: int = 365  # policy refresh horizon for ACTIVE records
    near_dup_name_sim: float = 0.85    # Jaro-Winkler floor for near-duplicate names


@dataclass
class Record:
    """One row of the customer/account extract under assessment."""
    record_id: str
    customer_id: str = ""
    full_name: str = ""
    entity_type: str = ""       # INDIVIDUAL / ENTITY
    dob: str = ""               # ISO date; blank for ENTITY records
    country: str = ""
    national_id: str = ""
    account_prefix: str = ""    # "CC-NN" — country code + branch number
    onboarding_date: str = ""
    status: str = "ACTIVE"      # ACTIVE / DORMANT / CLOSED
    last_refresh: str = ""


# ---------------------------------------------------------------------------
# Per-record rules (see METHODOLOGY.md §4). Each returns (fired, severity,
# detail); severity class and CDE binding live in RULE_META. The RuleSet
# 'typology' tag is reused as the severity class: a CRITICAL fire is the
# signal that feeds the hard gate, exactly as a typology hit blocks auto-close
# in the transaction-monitoring framework.
# ---------------------------------------------------------------------------
def _name_missing_active(f):
    fired = f["name_blank"] and f["status"] == "ACTIVE"
    return fired, 1.0, "full_name blank on an ACTIVE record — cannot be name-screened"


def _name_missing_inactive(f):
    fired = f["name_blank"] and f["status"] != "ACTIVE"
    return fired, 0.4, f"full_name blank on a {f['status']} record"


def _dob_missing(f):
    fired = f["entity_type"] == "INDIVIDUAL" and not f["dob_raw"]
    return fired, 1.0, "date of birth blank on an INDIVIDUAL record"


def _entity_type_missing(f):
    fired = f["entity_type"] not in ("INDIVIDUAL", "ENTITY")
    return fired, 0.4, f"entity_type blank or unrecognized ('{f['entity_type']}')"


def _onboarding_missing(f):
    fired = not f["onboarding_raw"]
    return fired, 0.4, "onboarding_date blank"


def _id_missing(f):
    fired = not f["nid"]
    return fired, 0.4, "national identifier blank — screening loses identifier corroboration"


def _dob_unparseable(f):
    fired = bool(f["dob_raw"]) and f["dob"] is None
    return fired, 1.0, f"date of birth '{f['dob_raw']}' fails the ISO-format/calendar parse"


def _dob_out_of_range(f):
    d = f["dob"]
    fired = d is not None and (d < DOB_FLOOR or d > f["asof"])
    detail = f"date of birth {d} outside the plausible range ({DOB_FLOOR} .. as-of {f['asof']})" \
        if d else ""
    return fired, 1.0, detail


def _country_invalid(f):
    c = f["country"]
    fired = c not in COUNTRY_REF
    return fired, 1.0, (f"country code '{c}' not in the approved reference set"
                        if c else "country blank")


def _id_format_invalid(f):
    nid = f["nid"]
    fired = bool(nid) and not id_check(nid)
    return fired, 1.0, f"national identifier '{nid}' fails the format/check-digit contract"


def _dob_after_onboarding(f):
    d, ob = f["dob"], f["onboarding"]
    fired = (d is not None and ob is not None and d > ob and d <= f["asof"])
    detail = f"date of birth {d} postdates onboarding {ob} — format-valid but impossible in sequence" \
        if fired else ""
    return fired, 1.0, detail


def _prefix_country_mismatch(f):
    pc = f["prefix_country"]
    fired = (f["country"] in COUNTRY_REF and pc is not None
             and pc != f["country"])
    return fired, 0.4, (f"account prefix country '{pc}' disagrees with country "
                        f"field '{f['country']}'")


def _entity_dob_conflict(f):
    fired = f["entity_type"] == "ENTITY" and bool(f["dob_raw"])
    return fired, 0.3, "ENTITY record carries a date of birth"


def _refresh_stale(f):
    if f["status"] != "ACTIVE":
        return False, 0.0, ""
    r = f["refresh"]
    if r is None:
        return True, 0.4, "no parseable last_refresh on an ACTIVE record"
    age = (f["asof"] - r).days
    fired = age > f["horizon_days"]
    return fired, 0.4, f"last refresh {age} days old (policy horizon {f['horizon_days']})"


RULES = RuleSet([
    Rule("name_missing_active", _name_missing_active, CRITICAL),
    Rule("name_missing_inactive", _name_missing_inactive, ""),
    Rule("dob_missing", _dob_missing, CRITICAL),
    Rule("entity_type_missing", _entity_type_missing, ""),
    Rule("onboarding_missing", _onboarding_missing, ""),
    Rule("id_missing", _id_missing, ""),
    Rule("dob_unparseable", _dob_unparseable, CRITICAL),
    Rule("dob_out_of_range", _dob_out_of_range, CRITICAL),
    Rule("country_invalid", _country_invalid, CRITICAL),
    Rule("id_format_invalid", _id_format_invalid, CRITICAL),
    Rule("dob_after_onboarding", _dob_after_onboarding, CRITICAL),
    Rule("prefix_country_mismatch", _prefix_country_mismatch, ""),
    Rule("entity_dob_conflict", _entity_dob_conflict, ""),
    Rule("refresh_stale", _refresh_stale, ""),
])


def _features(rec: Record, config: Config, asof: datetime.date) -> dict:
    prefix_m = PREFIX_RE.match(rec.account_prefix.strip())
    return {
        "name_blank": not rec.full_name.strip(),
        "status": rec.status.strip(),
        "entity_type": rec.entity_type.strip(),
        "dob_raw": rec.dob.strip(),
        "dob": parse_iso(rec.dob),
        "onboarding_raw": rec.onboarding_date.strip(),
        "onboarding": parse_iso(rec.onboarding_date),
        "country": rec.country.strip().upper(),
        "prefix_country": prefix_m.group(1) if prefix_m else None,
        "nid": rec.national_id.strip(),
        "refresh": parse_iso(rec.last_refresh),
        "asof": asof,
        "horizon_days": config.staleness_horizon_days,
    }


def assess_record(rec: Record, config: Config = Config(),
                  asof: datetime.date = None) -> list:
    """Evaluate all per-record rules. Returns the record's defect list:
    [{record_id, rule, dimension, cde, severity, detail}]. UNIQUENESS is a
    population-level pass (find_duplicates) and is not evaluated here."""
    asof = asof or parse_iso(DEFAULT_ASOF)
    results = RULES.evaluate(_features(rec, config, asof))
    out = []
    for r in RuleSet.fired(results):
        dim, cde, sev = RULE_META[r.name]
        out.append({"record_id": rec.record_id, "rule": r.name, "dimension": dim,
                    "cde": cde, "severity": sev, "detail": r.detail})
    return out


# ---------------------------------------------------------------------------
# UNIQUENESS — duplicate detection (population-level pass)
# ---------------------------------------------------------------------------
def _canon(name: str) -> str:
    """Order-insensitive canonical form: normalized (accent-folded, punctuation
    stripped) tokens, sorted and re-joined."""
    return " ".join(sorted(normalize(name).split()))


def names_near(a: str, b: str, sim: float, use_fallback: bool = True) -> bool:
    """True when two names are near-duplicates: same token count, every token
    greedily aligned to a partner with Jaro-Winkler >= sim OR (when
    use_fallback) an equal Soundex class or a single-character edit. The
    fallbacks are what hold transliteration variants that sit at the edge of a
    character-similarity threshold: Soundex holds MOHAMMED / MUHAMMAD, and the
    single-edit tolerance holds short first-letter variants like OMAR / UMAR,
    which defeat BOTH Jaro-Winkler (no shared prefix) and Soundex (the code
    keeps the first letter)."""
    ta, tb = normalize(a).split(), normalize(b).split()
    if not ta or not tb or len(ta) != len(tb):
        return False
    used = set()
    for qt in ta:
        best = None
        for idx, lt in enumerate(tb):
            if idx in used:
                continue
            s = jaro_winkler(qt, lt)
            if best is None or s > best[1]:
                best = (idx, s, lt)
        idx, s, lt = best
        if s < sim and not (use_fallback and (
                soundex(qt) == soundex(lt)
                or (len(qt) >= 3 and levenshtein(qt, lt) <= 1))):
            return False
        used.add(idx)
    return True


def find_duplicates(records, config: Config = Config(), sim: float = None,
                    use_fallback: bool = True) -> dict:
    """Detect duplicate customer records, blocked on a shared national
    identifier. Returns {record_id: {rule, detail}} covering every member of a
    detected cluster.

      duplicate_exact  same canonical name AND same DOB string on a shared id
      duplicate_near   name similarity >= threshold (or phonetic-equal) on a
                       shared id — the transliterated re-onboard signature

    Records sharing an identifier whose names are NOT similar are left
    unflagged here (identifier collision is a separate control — see
    METHODOLOGY.md limitations)."""
    sim = config.near_dup_name_sim if sim is None else sim
    by_id = {}
    for rec in records:
        nid = rec.national_id.strip()
        if nid:
            by_id.setdefault(nid, []).append(rec)

    flagged = {}
    for nid, group in by_id.items():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                ca, cb = _canon(a.full_name), _canon(b.full_name)
                if ca and ca == cb and a.dob.strip() == b.dob.strip():
                    rule = "duplicate_exact"
                    detail = (f"identical name/DOB on shared identifier {nid} "
                              f"({a.record_id} = {b.record_id})")
                elif names_near(a.full_name, b.full_name, sim, use_fallback):
                    rule = "duplicate_near"
                    detail = (f"near-duplicate names ('{a.full_name}' ~ "
                              f"'{b.full_name}') on shared identifier {nid}")
                else:
                    continue
                dim, cde, sev = RULE_META[rule]
                for rec in (a, b):
                    prev = flagged.get(rec.record_id)
                    if prev is None or (prev["rule"] == "duplicate_near"
                                        and rule == "duplicate_exact"):
                        flagged[rec.record_id] = {
                            "record_id": rec.record_id, "rule": rule,
                            "dimension": dim, "cde": cde, "severity": sev,
                            "detail": detail}
    return flagged


# ---------------------------------------------------------------------------
# Feed assessment — scorecard + disposition
# ---------------------------------------------------------------------------
@dataclass
class FeedAssessment:
    feed_id: str
    disposition: str      # FEED_PASS / INVESTIGATE / BLOCK_FEED_TO_SCREENING
    reason: str           # the NAMED rationale (audit trail)
    composite_score: float
    per_cde: dict         # cde -> rates, ceiling, status
    per_dimension: dict   # dimension -> pass rate
    defects: list         # full record-level defect list
    n_records: int
    dup_records: int

    def as_row(self) -> dict:
        return {"feed_id": self.feed_id, "disposition": self.disposition,
                "composite_score": round(self.composite_score, 4),
                "reason": self.reason}


def assess_feed(records, config: Config = Config(),
                asof_str: str = DEFAULT_ASOF, feed_id: str = "FEED") -> FeedAssessment:
    asof = parse_iso(asof_str)
    n = len(records)

    defects = []
    for rec in records:
        defects.extend(assess_record(rec, config, asof))
    dup_flags = find_duplicates(records, config)
    defects.extend(dup_flags.values())

    # roll up: per-CDE defective record sets (any severity, and critical-only)
    cde_any, cde_crit, dim_any = {}, {}, {}
    for d in defects:
        cde_any.setdefault(d["cde"], set()).add(d["record_id"])
        if d["severity"] == CRITICAL:
            cde_crit.setdefault(d["cde"], set()).add(d["record_id"])
        dim_any.setdefault(d["dimension"], set()).add(d["record_id"])

    per_cde = {}
    for cde, weight in CDE_WEIGHTS.items():
        any_n = len(cde_any.get(cde, ()))
        crit_n = len(cde_crit.get(cde, ()))
        any_rate = any_n / n if n else 0.0
        crit_rate = crit_n / n if n else 0.0
        screening = cde in SCREENING_CRITICAL
        if cde == "record_uniqueness":
            ceiling = config.dup_ceiling
        elif screening:
            ceiling = config.crit_ceiling
        elif cde == "last_refresh":
            ceiling = config.staleness_ceiling
        else:
            ceiling = config.supporting_ceiling
        gate_rate = crit_rate if screening else any_rate
        if gate_rate > ceiling:
            status = "BREACH"
        elif screening and gate_rate > config.warn_fraction * ceiling:
            status = "WARN"
        else:
            status = "OK"
        per_cde[cde] = {
            "weight": weight, "screening_critical": screening,
            "defective": any_n, "defect_rate": round(any_rate, 4),
            "critical_defective": crit_n, "critical_rate": round(crit_rate, 4),
            "pass_rate": round(1 - any_rate, 4), "ceiling": ceiling,
            "status": status,
        }

    per_dimension = {
        dim: round(1 - len(dim_any.get(dim, ())) / n, 4) if n else 1.0
        for dim in ("COMPLETENESS", "VALIDITY", "CONSISTENCY", "UNIQUENESS",
                    "TIMELINESS")
    }

    total_w = sum(CDE_WEIGHTS.values())
    composite = sum(w * per_cde[c]["pass_rate"]
                    for c, w in CDE_WEIGHTS.items()) / total_w if n else 1.0

    # ---- disposition, in firing order (METHODOLOGY.md §6). The hard gate is
    # evaluated FIRST: a screening-critical breach can never be argued away by
    # the composite score or any weighting. ----
    breaches = [c for c in SCREENING_CRITICAL if per_cde[c]["status"] == "BREACH"]
    if breaches:
        parts = ", ".join(
            f"{c} critical-defect rate {per_cde[c]['critical_rate']:.4f}"
            f" > ceiling {per_cde[c]['ceiling']:.4f}" for c in breaches)
        disposition = "BLOCK_FEED_TO_SCREENING"
        reason = (f"Screening-critical CDE threshold breach — {parts}. Feed held "
                  f"from the screening pipeline and routed to data-governance "
                  f"review with the full defect list; no record is dropped or "
                  f"silently repaired.")
    else:
        causes = []
        warns = [c for c in SCREENING_CRITICAL if per_cde[c]["status"] == "WARN"]
        if warns:
            causes.append("screening-critical CDE(s) in the warn band: " +
                          ", ".join(f"{c} at {per_cde[c]['critical_rate']:.4f}"
                                    for c in warns))
        sup_breach = [c for c in CDE_WEIGHTS if c not in SCREENING_CRITICAL
                      and per_cde[c]["status"] == "BREACH"]
        for c in sup_breach:
            causes.append(f"supporting CDE {c} defect rate "
                          f"{per_cde[c]['defect_rate']:.4f} > ceiling "
                          f"{per_cde[c]['ceiling']:.4f}")
        if composite < config.composite_floor:
            causes.append(f"composite DQ score {composite:.4f} below the "
                          f"pass floor {config.composite_floor:.2f}")
        if causes:
            disposition = "INVESTIGATE"
            reason = ("Feed routed to data-governance investigation — " +
                      "; ".join(causes) + ". No hard screening-critical breach.")
        else:
            disposition = "FEED_PASS"
            reason = (f"All documented thresholds met (the named provable cause): "
                      f"every screening-critical CDE critical-defect rate at or "
                      f"below {config.warn_fraction:.0%} of its ceiling, all "
                      f"supporting CDEs within ceilings, staleness within policy, "
                      f"composite {composite:.4f} >= floor "
                      f"{config.composite_floor:.2f}.")

    return FeedAssessment(feed_id=feed_id, disposition=disposition, reason=reason,
                          composite_score=composite, per_cde=per_cde,
                          per_dimension=per_dimension, defects=defects,
                          n_records=n, dup_records=len(dup_flags))


if __name__ == "__main__":
    import json
    demo = [
        Record("REC-1", "CUS-1", "MOHAMMED AL-RASHID", "INDIVIDUAL", "1975-03-12",
               "AE", "HV00012340", "AE-14", "2015-06-01", "ACTIVE", "2026-04-20"),
        Record("REC-2", "CUS-2", "MUHAMMAD AL RASHEED", "INDIVIDUAL", "1975-03-12",
               "AE", "HV00012340", "AE-14", "2019-02-11", "ACTIVE", "2026-04-20"),
        Record("REC-3", "CUS-3", "ELENA PETROVA", "INDIVIDUAL", "1988-02-30",
               "UK", "HV00045676", "GB-22", "2020-09-15", "ACTIVE", "2026-05-02"),
    ]
    fa = assess_feed(demo, feed_id="DEMO")
    print(json.dumps({**fa.as_row(),
                      "defects": fa.defects,
                      "per_dimension": fa.per_dimension}, indent=2))
