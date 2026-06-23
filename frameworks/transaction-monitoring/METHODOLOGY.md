# Methodology — Transaction-Monitoring Alert-Scoring Engine

The regulator-facing specification of the scoring and disposition logic. Every
input, rule, threshold, and decision below exists as a named construct in
[`scorer.py`](scorer.py); that file is the executable form of this document. The
evidence that the logic performs as specified is in
[`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md), produced by
[`run_validation.py`](run_validation.py). Model-governance framing is shared across
the pillar in [`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** A transaction-monitoring system raises an alert whenever a
> customer's activity trips a rule — a burst of cash deposits, money flowing
> straight through an account, lots of transfers from many sources into one. Most
> alerts are a normal customer doing a normal thing that happens to look like a
> rule. This engine reads each alert against what's *normal for that customer* and
> their documented business, then sorts it: *close it* (only with a concrete benign
> reason and only if no laundering pattern is present), *review it* (ranked), or
> *escalate it* (a clear laundering pattern). It never closes an alert that shows a
> real pattern, and never files a SAR — a person does that.

---

## 1. Problem framing and error posture

A monitoring system flags an alert when a rule fires over a window of a customer's
transactions. The large majority are false positives — normal behaviour that
resembles a rule. The institution must disposition every one; the volume is the
operational problem, the discipline is the regulatory one. The error costs are
asymmetric, exactly as in sanctions screening:

- A **false negative** — closing a genuinely suspicious alert — is a regulatory
  failure (a missed SAR, unreported laundering). Its tolerated rate is **zero**.
- A **false positive** — keeping a benign alert in the queue — is operational cost.

The engine is a **false-positive suppression and prioritization** tool. It is not
an auto-decision tool: it never files a SAR and never closes an alert that exhibits
a recognised laundering typology.

---

## 2. Inputs

**Customer profile** (the baseline): `segment` (RETAIL / SMB / CORPORATE / MSB),
`risk_rating` (LOW / MEDIUM / HIGH), `expected_amount` (expected throughput over the
window), `expected_count` (expected transaction count), `home_country`,
`business_type` (documented activity — import_export / cash_intensive / remittance /
payroll, or none).

**Alert** (a window of aggregated activity that fired a rule): `total_in`,
`total_out`, `txn_count`, `near_threshold_count` (deposits just under the reporting
threshold), `distinct_in_cp` / `distinct_out_cp` (counterparty counts),
`passthrough_ratio`, `same_day`, `high_risk_geo_fraction`.

---

## 3. Deviation features

Behavioural monitoring measures activity *relative to a baseline*:

- `amount_ratio = (total_in + total_out) / expected_amount` — throughput vs expected.
- `count_ratio = txn_count / expected_count` — transaction count vs expected.

A ratio near 1.0 is on profile; a high ratio is deviation. When no baseline exists
the activity is treated as maximally anomalous.

---

## 4. Rules

Each rule (in [`scorer.py`](scorer.py), via the shared `_lib/rules.py` mechanism)
returns fired / severity / detail and, for the laundering patterns, a **typology
tag**. A typology tag is the signal that an alert cannot be auto-closed.

| Rule | Typology | Fires when | Severity |
|---|---|---|---|
| `structuring` | STRUCTURING | ≥3 deposits just under the $10,000 reporting threshold | 0.55 + 0.10·(n−3) |
| `funnel` | FUNNEL_ACCOUNT | ≥5 inbound counterparties, ≤2 outbound, ≥60% of inflow moved out | 0.50 + 0.05·(in−5) |
| `rapid_passthrough` | LAYERING_PASSTHROUGH | pass-through ratio ≥80%, same-day, throughput ≥ $50,000 | 0.40 + scaled |
| `velocity_spike` | — (deviation) | transaction count ≥3× the customer baseline | mild, saturating |
| `geo_risk` | — (risk factor) | ≥50% of value to/from higher-risk jurisdictions | 0.25 + 0.35·fraction |

`velocity_spike` and `geo_risk` carry **no** typology — they raise the score and
priority but do not, alone, keep an alert open, and they can be explained away by a
documented business (§6).

## 5. Suspicion score

A continuous [0,1] score for ranking and calibration:

```
deviation_mag = saturating( max(0, amount_ratio−1) + max(0, count_ratio−1), scale=3 )
score = max( max_rule_severity, deviation_mag )
if any typology fired:  score += 0.15 × min(typology_count, 2)
score ×= risk_amplifier   (LOW 1.00 / MEDIUM 1.08 / HIGH 1.20)
score = clamp(score, 0, 1)
```

The score ranks the queue; it does **not** by itself close an alert.

## 6. Disposition rules (in firing order)

1. **A typology fired** → the alert is kept open:
   - **ESCALATE** if the maximum typology severity ≥ `escalate_severity` (0.60) —
     a clear pattern, routed to investigation for a SAR decision.
   - **ANALYST_REVIEW (HIGH)** otherwise — an emerging pattern at the edge of the
     threshold, kept for a human.
2. **No typology fired** → eligible for a NAMED auto-close:
   - **within_profile** — `amount_ratio ≤ 1.5` and `count_ratio ≤ 1.5` and severity
     below the soft floor (0.30). Reason: within expected profile.
   - **documented_context** — every fired non-typology rule is one the customer's
     `business_type` explains (import_export → geography; cash_intensive → velocity;
     etc.) and throughput is within `context_tol` (3.0). Gated on throughput, **not**
     on transaction count — a cash business legitimately runs a high count, which is
     the deviation the documented profile explains.
   - **below_typology** — a typology indicator is present but below its pattern
     threshold (e.g. 2 near-threshold deposits; structuring requires 3+), with
     moderate deviation. Reason names the sub-threshold indicator.
3. **Otherwise** → **ANALYST_REVIEW**, priority by score (HIGH ≥0.50, MEDIUM ≥0.25,
   else LOW). This is the irreducible band — unexplained deviation with no typology
   and no documented reason. It is deliberately **not** auto-closed.

### Why false-negative safety is structural

A genuinely suspicious alert fires a typology rule (structuring, funnel, or
pass-through). The auto-close branches are reached **only when no typology has
fired**. A suspicious alert therefore cannot be auto-closed regardless of its
score. The validation harness enforces this as a build gate (recall floor 1.0; any
auto-closed suspicious alert fails the build).

---

## 7. Tunable constants

All in `scorer.Config`; defaults are the conservative posture. Recalibration in
[`tuning.md`](tuning.md).

| Constant | Default | Effect |
|---|---|---|
| `escalate_severity` | 0.60 | Typology severity at/above which to escalate vs review. |
| `within_tol` | 1.50 | Deviation ratio treated as on-profile. |
| `context_tol` | 3.00 | Throughput deviation a documented context tolerates. |
| `soft_severity_floor` | 0.30 | Non-typology severity below which a signal is minor. |
| `review_high` / `review_medium` | 0.50 / 0.25 | Analyst priority bands. |

The rule thresholds (structuring count, funnel fan-in, pass-through ratio, the
$10,000 reporting threshold, the $50,000 materiality floor) are named constants in
`scorer.py` and are themselves calibration points.

---

## 8. Governance and boundaries

Mapped to public guidance — SR 11-7 / OCC 2011-12, the FFIEC BSA/AML Examination
Manual, and the Wolfsberg Group statements on monitoring and threshold testing — per
the shared [`../GOVERNANCE.md`](../GOVERNANCE.md). The engine scores and routes; it
does not file SARs and does not close alerts of record without human review. A
typology hit is a human investigation decision; every auto-closed alert is auditable
by its named reason and component breakdown.
