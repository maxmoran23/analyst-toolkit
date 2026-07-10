# Methodology — PEP Screening Disposition Engine

The regulator-facing specification of the scoring and disposition logic. Every
input, weight, threshold, and decision rule below exists as a named constant or
branch in [`scorer.py`](scorer.py); that file is the executable form of this
document, and the two are kept in step. Validation evidence:
[`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md), produced by
[`run_validation.py`](run_validation.py) over a seeded synthetic population.
Shared governance: [`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** A PEP filter raises an alert whenever a customer's name
> resembles a name on a politically-exposed-person list. Most alerts are wrong
> two ways: it's a *different* person who shares the name (Kim, Park, Mohammed,
> Garcia — or a transliteration variant), or it's the right person but the
> listing no longer matters (a minor local official who left office a decade
> ago). This engine sorts each alert — clear it (only with written proof),
> review it, or escalate it (a confirmed match on someone the institution must
> treat as high risk). Two things it refuses to do: clear a bare common-name
> match it cannot resolve, and status-clear anyone who was ever senior — a
> former head of state's risk is lowered, never zeroed.

---

## 1. Problem framing and the two false-positive axes

A PEP screening filter flags a customer whose name matches a list entry. The
large majority of alerts are false positives on one of two axes:

- **Party axis** — the customer is a *different* person with a similar name.
  The dominant driver is common names, compounded by transliteration variance;
  a name alone rarely identifies a person.
- **Scope axis** — the customer may well be the listed person, but the entry
  carries no current PEP risk: a former low-prominence official far past the
  documented step-down horizon with no adverse indicator.

Error costs are asymmetric, as across this pillar: a **false negative**
(clearing a customer who is a current or materially exposed PEP) is a
customer-due-diligence failure with zero tolerance; a **false positive**
(keeping a non-match open) is operational cost. The engine is a
false-positive suppression and prioritization tool, never an auto-decision
tool: it routes to humans and its safety property is enforced as a build gate.

## 2. Inputs

Each alert is a **(customer, entry)** pair the upstream filter produced.

**Customer**: `name`, sparse identifiers `dob`, `nationality` (KYC records are
often identifier-poor relative to the list).

**PEP-list entry**: `pep_id`, `name`, `aliases`, `tier` (TIER_1 / TIER_2 /
TIER_3 / RCA), `position`, `country` (of the position held),
`jurisdiction_risk` (HIGH / MEDIUM / LOW bucket), `status` (CURRENT / FORMER),
`years_since_left`, `principal_tier` (for RCA entries), `adverse_flag`
(a documented adverse indicator), `dob`.

## 3. Axis A — entity resolution (match strength)

The customer name is compared to the entry's primary name **and every alias**
with the same IDF-weighted matcher the sanctions framework uses (`_lib/match`,
`_lib/text_normalize`): tokens align on equality, shared Soundex class, or
Jaro-Winkler ≥ 0.88, and each aligned token contributes weight proportional to
its corpus rarity. A token is **generic** when its document-frequency share
meets `generic_max_share` (0.005) — the Kim/Park/Mohammed/Garcia band.

```
name_score = weighted_overlap × (0.4 + 0.6 × coverage)
```

Identifiers are then compared. **Strong field:** `dob` — a match is STRONG
corroboration. **Weak field:** customer `nationality` vs the entry's position
`country` — a match is WEAK corroboration. Absent fields assert nothing.

`match_strength` ∈ [0,1] starts at `name_score`, boosted by corroboration
(+40% of headroom for STRONG, +15% for WEAK), and is **capped at 0.5 for a
common-name match without strong corroboration** (`common_name_cap`) — a match
built entirely from common tokens is moderate confidence at best, because
thousands of people share it. A proven wrong party is floored near zero.

## 4. Axis B — PEP materiality (prominence × status × jurisdiction)

```
materiality = tier_weight × status_decay × jurisdiction_weight
```

### 4.1 Prominence tiers

| Tier | Who | Weight |
|---|---|---|
| TIER_1 | Heads of state/government, ministers, top military and judiciary, central bank governors | 1.00 |
| TIER_2 | Senior officials, state-owned-enterprise executives, senior party officials, ambassadors | 0.80 |
| TIER_3 | Mid-level and regional officials (governors, mayors, district judges, customs directors) | 0.55 |
| RCA | Relatives and close associates | 0.60 × the principal's tier weight |

An RCA inherits a fraction (`RCA_FRACTION` = 0.60) of its principal's weight:
exposure is derivative, not personal. An RCA of an unstated principal tier is
treated as TIER_3-derived (the floor).

### 4.2 Status decay ("once senior, lower but never zero")

CURRENT status is always 1.0. FORMER decays linearly with years since leaving
office:

| Tier | Decay | Step-down horizon |
|---|---|---|
| TIER_1 | `max(0.40, 1 − y/10)` | none — never fully decays (floor 0.40) |
| TIER_2 | `max(0.15, 1 − y/10)` | none — never fully decays (floor 0.15) |
| TIER_3 | `max(0, 1 − y/5)` | **5 years** — fully out of scope past it |
| RCA | `max(0, 1 − y/h)`, `h` = half the principal-tier horizon | 5 years (TIER_1/TIER_2 principal) or 2.5 years (TIER_3 principal) — RCA decays faster |

A documented **adverse indicator suspends step-down**: decay is floored at 0.5
(`ADVERSE_DECAY_FLOOR`) whatever the elapsed years — time out of office does
not de-risk an entry carrying live adverse information. The horizons are
illustrative policy parameters; public guidance treats "once a PEP, always a
PEP" as a risk-based question, and a deployment documents its own horizons
(see `tuning.md`).

### 4.3 Jurisdiction bucket

`jurisdiction_weight`: HIGH 1.00, MEDIUM 0.75, LOW 0.55; an unknown bucket
defaults to HIGH (conservative). The bucket assignment (country →
HIGH/MEDIUM/LOW corruption-risk) is **ILLUSTRATIVE by design** — public
corruption indices move — and lives in upstream configuration, not in the
engine. The synthetic population uses invented countries precisely so no real
jurisdiction is scored.

`combined = match_strength × materiality` is the ranking score: a strong match
on an out-of-scope entry scores low, and a weak match on a sitting minister
scores low — but neither score, by itself, clears anything.

## 5. Disposition rules (in firing order)

Named clear causes first; the combined score only ranks what survives. Three
matches are **never** auto-cleared, whatever else holds: any CURRENT-status
match, any TIER_1/TIER_2 match (no step-down horizon exists for them), and any
match with a corroborated identifier.

1. **AUTO_CLEAR — wrong_party (identifier proof).** Fires when the date of
   birth AND the nationality **both** contradict the entry. Two independent
   contradictions prove a different person, so this clears even an exact name.
   A single conflicting field never clears — that is a reconciliation for an
   analyst, not a clearance.
2. **AUTO_CLEAR — generic_token_only.** Fires when every aligned token is
   generic **and the entry carries a distinctive token the customer did not
   match**, with no corroboration. The second condition is the structural
   false-negative guard carried over from the sanctions framework: an entry
   whose *own* name is entirely common tokens cannot be ruled out by name and
   is **not** cleared here — it falls through to review.
3. **AUTO_CLEAR — wrong_party (zero distinctive-token overlap).** Fires when
   `name_score < 0.15` with no corroboration — no material name match exists.
4. **AUTO_CLEAR — out_of_scope_status.** Fires only for a FORMER TIER_3 or RCA
   entry **beyond its documented step-down horizon**, with **no adverse
   indicator** and **no corroboration**. The cause is status-based — even if
   the customer is the listed person, the entry carries no current PEP risk.
   Corroborated identity on a list entry still goes to a human, by rule.
5. **ESCALATE_ENHANCED_REVIEW.** `corroboration == STRONG`, `match_strength ≥
   0.60` (`escalate_strength`), and `materiality ≥ 0.40`
   (`escalate_materiality`) — a DOB-corroborated match on a materially exposed
   entry, routed for enhanced review with the evidence assembled.
6. **ANALYST_REVIEW — everything else**, priority by `combined` (HIGH ≥ 0.35,
   MEDIUM ≥ 0.15, else LOW). This includes the **common_name_ambiguous**
   residual (a common-name match with no identifier, which can be neither
   cleared nor confirmed), single-identifier conflicts, adverse-flagged
   entries, and uncorroborated matches on current or senior entries.

### Why false-negative safety is structural

A genuine in-scope PEP match is the right party on an entry that still carries
PEP risk. It can satisfy none of the four clear causes: its identifiers
corroborate or are absent, never doubly contradicting (rule 1); its distinctive
token aligns — transliteration variance is vowel-class and the Soundex backstop
re-aligns it — and a fully common-named entry has no unmatched distinctive
token (rules 2–3); and it is in scope — CURRENT, TIER_1/TIER_2 (no horizon
exists), within the horizon, or adverse-flagged — so the status clear cannot
fire (rule 4). The validation harness enforces this as a build gate (recall
floor 1.0; any auto-cleared in-scope match fails the build).

## 6. Tunable constants (the operating point)

`scorer.Config` and the Axis B module constants; defaults are the conservative
posture. Recalibration procedure in [`tuning.md`](tuning.md).

| Constant | Default | Effect |
|---|---|---|
| `generic_max_share` | 0.005 | df-share at/above which a name token is generic. |
| `no_name_match` | 0.15 | `name_score` below which no material name match exists. |
| `common_name_cap` | 0.50 | strength ceiling for an uncorroborated common-name match. |
| `escalate_strength` / `escalate_materiality` | 0.60 / 0.40 | the two escalation floors. |
| `review_high` / `review_medium` | 0.35 / 0.15 | analyst priority bands on `combined`. |
| `TIER_WEIGHT`, `RCA_FRACTION` | 1.0/0.8/0.55, 0.60 | prominence weights. |
| `TIER1_FLOOR` / `TIER2_FLOOR` | 0.40 / 0.15 | the never-zero floors for former senior officials. |
| `TIER3_HORIZON_YEARS`, `RCA_HORIZON_FACTOR` | 5.0, 0.5 | the documented step-down horizons. |
| `ADVERSE_DECAY_FLOOR` | 0.5 | decay floor when an adverse indicator is present. |
| `JURISDICTION_WEIGHT` | 1.0/0.75/0.55 | ILLUSTRATIVE bucket weights. |

## 7. Model-governance framing (SR 11-7)

Mapped to public guidance — Federal Reserve / OCC **SR 11-7** and **OCC
Bulletin 2011-12** (model risk management), the **FFIEC BSA/AML Examination
Manual** (customer-due-diligence and screening expectations, including the
risk-based treatment of politically exposed persons), and **FATF
Recommendation 12** (PEP measures; the source of the tier / current-vs-former /
RCA structure). Generic and public; no institution-specific policy. See the
shared [`../GOVERNANCE.md`](../GOVERNANCE.md).

- **Conceptual soundness.** Every tier weight, decay horizon, bucket weight,
  threshold, and rule is documented here and implemented transparently in
  pure-readable Python. The matching approach (IDF-weighted token similarity,
  phonetic backstop, identifier corroboration) is established record-linkage
  practice; the materiality axis follows the risk-based PEP treatment public
  guidance describes.
- **Outcomes analysis.** `run_validation.py` computes recall, false-positive
  reduction, per-category clear rates, the threshold sweep, and the volume
  funnel over a labelled synthetic population, reproducibly from seed.
- **Ongoing monitoring.** The recall floor is a build-gate invariant; the
  multi-seed stability run shows the result is not a single-seed artifact;
  `tuning.md` defines the recalibration cadence, including re-review of the
  step-down horizons as policy parameters.
- **Limitations and assumptions.** Stated in the validation report: tier,
  status, and adverse flags are taken as given from the list vendor, whose own
  accuracy must be validated alongside this engine; horizons and buckets are
  illustrative; the engine routes, a human decides.

## 8. Boundaries

The engine **scores and routes**. It does not onboard, approve, block, or exit
a relationship, and it does not decide that a customer is or is not a PEP — a
confirmed match and the risk-acceptance decision are documented human actions.
A cleared alert is auditable by its named reason and full component breakdown;
nothing is cleared that cannot be explained. The disposition label
ESCALATE_ENHANCED_REVIEW routes a case into the institution's enhanced-review
process; it does not perform that review.
