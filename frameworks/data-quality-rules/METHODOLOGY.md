# Methodology — Data-Quality Rules Engine (CDE fitness for screening)

The regulator-facing specification of the assessment and disposition logic.
Every input, rule, threshold, weight, and decision below exists as a named
construct in [`scorer.py`](scorer.py); that file is the executable form of this
document. The evidence that the logic performs as specified is in
[`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md), produced by
[`run_validation.py`](run_validation.py). Model-governance framing is shared
across the pillar in [`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** Before a customer file is allowed to feed sanctions
> screening or monitoring, this engine checks the fields those systems depend
> on — name, date of birth, country, ID number — plus whether the same person
> appears twice. Every check is a named rule with a written reason. Each
> critical field gets a grade; the file gets a verdict: pass, investigate, or
> block. The one unbreakable rule: if too many critical fields are broken, the
> file cannot pass — no averaging, no offsetting, no exceptions. And the
> engine never fixes or deletes data on its own; it hands people a precise
> defect list.

---

## 1. Problem framing and error posture

Screening and monitoring are downstream consumers of customer reference data.
A blank name is a customer who is never screened; a malformed date of birth
degrades match confidence; a wrong country code breaks jurisdiction rules; a
duplicate record splits one party's activity across two profiles. The
data-governance question — "is this feed fit to screen against?" — has the
same asymmetric error structure as the rest of this pillar:

- A **false negative** — passing a feed whose screening-critical fields are
  materially broken — silently degrades every downstream control. Its
  tolerated rate is **zero**: no feed with a screening-critical breach may
  ever be dispositioned FEED_PASS.
- A **false positive** — flagging a clean record, or investigating a feed
  that was fine — is operational cost.

The engine is an **assessment and routing** tool. It never blocks records,
repairs values, or approves a feed autonomously: BLOCK holds the feed for
data-governance review with the full defect list, and FEED_PASS is a named,
evidence-backed recommendation to the feed owner. No record is dropped or
silently repaired at any disposition.

---

## 2. Inputs

One extract row per customer record: `record_id`, `customer_id`, `full_name`,
`entity_type` (INDIVIDUAL / ENTITY), `dob` (ISO date; blank for entities),
`country`, `national_id`, `account_prefix` (`CC-NN` — country code + branch),
`onboarding_date`, `status` (ACTIVE / DORMANT / CLOSED), `last_refresh`. The
extract carries a fixed as-of batch date (`DEFAULT_ASOF`) so every assessment
is deterministic.

## 3. CDE inventory

Every rule binds to a critical data element with a documented criticality
weight. The screening-critical CDEs are the fields screening cannot work
without — plus record uniqueness itself (one party, one record). Weights feed
the composite score (§5); the screening-critical flag feeds the hard gate (§6).

| CDE | Screening-critical | Weight | Threshold (ceiling) | Rationale |
|---|---|---|---|---|
| `full_name` | yes | 1.00 | critical-defect rate > 0.5% | The primary screening key; a blank name on an active record is unscreenable. |
| `dob` | yes | 1.00 | critical-defect rate > 0.5% | Disambiguates name matches; malformed or impossible DOBs corrupt match confidence. |
| `country` | yes | 1.00 | critical-defect rate > 0.5% | Drives jurisdiction risk and geographic rules; drifted codes break both. |
| `national_id` | yes | 1.00 | critical-defect rate > 0.5% | Identifier corroboration for match adjudication; a failed check digit is actively wrong data. |
| `record_uniqueness` | yes | 1.00 | duplicate-record rate > 0.4% | A duplicated party splits activity across profiles and defeats aggregation-based monitoring. |
| `entity_type` | no | 0.40 | any-defect rate > 2% | Determines which field contracts apply. |
| `onboarding_date` | no | 0.40 | any-defect rate > 2% | Anchor for sequence checks and review cycles. |
| `account_prefix` | no | 0.30 | any-defect rate > 2% | Cross-field corroboration of country. |
| `last_refresh` | no | 0.50 | stale rate > 10% | Staleness proxy for the whole record's reliability. |

## 4. Rules

Each rule (via the shared `_lib/rules.py` mechanism) returns fired / severity /
detail and carries a severity class. A **CRITICAL** fire is this framework's
analogue of a typology hit in the transaction-monitoring framework: it feeds
the hard gate and can never be offset by the composite score.

| Rule | Dimension | CDE | Severity | Fires when |
|---|---|---|---|---|
| `name_missing_active` | COMPLETENESS | full_name | CRITICAL | `full_name` blank on an ACTIVE record |
| `name_missing_inactive` | COMPLETENESS | full_name | MINOR | `full_name` blank on a non-ACTIVE record |
| `dob_missing` | COMPLETENESS | dob | CRITICAL | blank DOB on an INDIVIDUAL |
| `entity_type_missing` | COMPLETENESS | entity_type | MINOR | `entity_type` blank or unrecognized |
| `onboarding_missing` | COMPLETENESS | onboarding_date | MINOR | `onboarding_date` blank |
| `id_missing` | COMPLETENESS | national_id | MINOR | `national_id` blank (screening loses corroboration but can still name-screen) |
| `dob_unparseable` | VALIDITY | dob | CRITICAL | DOB fails the strict ISO-format AND calendar parse (catches `1985-02-30` — format-valid, calendar-false) |
| `dob_out_of_range` | VALIDITY | dob | CRITICAL | DOB parses but is before 1900-01-01 or after the as-of date |
| `country_invalid` | VALIDITY | country | CRITICAL | country blank or not in the approved reference set (catches ISO-adjacent drift: `UK`, `EL`, retired `SU`/`YU`) |
| `id_format_invalid` | VALIDITY | national_id | CRITICAL | identifier fails the documented format or its position-weighted check digit |
| `dob_after_onboarding` | CONSISTENCY | dob | CRITICAL | DOB parses, is in range, but postdates onboarding — valid in format, impossible in sequence |
| `prefix_country_mismatch` | CONSISTENCY | account_prefix | MINOR | account-prefix country disagrees with a valid country field (suppressed when the country itself is invalid — one named cause per defect) |
| `entity_dob_conflict` | CONSISTENCY | entity_type | MINOR | ENTITY record carries a DOB |
| `refresh_stale` | TIMELINESS | last_refresh | MINOR | ACTIVE record with no parseable refresh, or refresh older than the policy horizon (365 days) |
| `duplicate_exact` | UNIQUENESS | record_uniqueness | CRITICAL | identical canonical name + DOB on a shared identifier |
| `duplicate_near` | UNIQUENESS | record_uniqueness | CRITICAL | near-duplicate names on a shared identifier (§4.1) |

### 4.1 Near-duplicate detection

Duplicate detection is **blocked on a shared national identifier** (the
`_lib/match` primitives do the name comparison). Two records sharing an
identifier are near-duplicates when their normalized names (accent-folded,
punctuation-stripped, via `_lib/text_normalize`) have the same token count and
every greedily-aligned token pair passes at least one of three tests, in order:

1. **Jaro-Winkler ≥ `near_dup_name_sim`** (default 0.85) — the character layer;
2. **equal Soundex class** — the phonetic fallback that holds transliteration
   variants (MOHAMMED / MUHAMMAD) sitting at the edge of a character threshold;
3. **Levenshtein distance ≤ 1** (tokens ≥ 3 chars) — holds short first-letter
   variants (OMAR / UMAR) that defeat both Jaro-Winkler (no shared prefix) and
   Soundex (the code keeps the first letter).

Records sharing an identifier with genuinely dissimilar names are NOT flagged
as duplicates — identifier collision is a separate control (§8). Every member
of a detected cluster is flagged; nothing is auto-merged.

## 5. Scorecard and composite score

Per CDE: `defect_rate` (records with any defect on that CDE / records),
`critical_rate` (critical defects only), `pass_rate = 1 − defect_rate`, and a
status — **OK**, **WARN** (screening-critical CDE above `warn_fraction` ×
ceiling, default 50%), or **BREACH** (over ceiling; screening-critical CDEs
gate on `critical_rate`, supporting CDEs on `defect_rate`). Per-dimension pass
rates aggregate records untouched by each dimension. The composite score is
the criticality-weighted mean of per-CDE pass rates:

```
composite = Σ (weight_c × pass_rate_c) / Σ weight_c
```

The composite ranks and trends feed health; it does **not** by itself pass a
feed — and it can never rescue one (§6).

## 6. Feed disposition (in firing order)

1. **Hard gate — evaluated first.** Any screening-critical CDE in BREACH →
   **BLOCK_FEED_TO_SCREENING**. The reason names every breaching CDE with its
   rate and ceiling. Because this branch precedes all pass logic, a breached
   feed can never be FEED_PASS regardless of its composite score — the gate is
   structural, not a weight. The feed and its full record-level defect list
   route to data-governance review; no record is dropped.
2. **Named investigation causes.** No breach, but: a screening-critical CDE in
   the WARN band, a supporting CDE over its ceiling, or the composite below
   `composite_floor` (0.98) → **INVESTIGATE**, with every cause named.
3. **FEED_PASS** — only on the provable named cause that every documented
   threshold is met: all screening-critical CDEs at or below the warn margin,
   all supporting CDEs within ceilings, staleness within policy, composite at
   or above the floor. The reason states each condition — auto-pass with a
   written, checkable justification, mirroring the named-cause auto-clear
   discipline used across this pillar.

### Why false-negative safety is structural

Every critical defect class is detected by a deterministic parser, reference
set, or arithmetic contract — not a statistical guess — so a planted critical
defect cannot evade the record-level rules. At the feed level, the BLOCK
branch is evaluated before any pass logic, so detected breaches cannot be
outweighed. The harness enforces both as build gates: recall floor 1.0 on
planted critical defects, and no feed with a planted screening-critical breach
may receive FEED_PASS.

---

## 7. Tunable constants

All in `scorer.Config`; defaults are the conservative posture. Recalibration in
[`tuning.md`](tuning.md).

| Constant | Default | Effect |
|---|---|---|
| `crit_ceiling` | 0.005 | Screening-critical CDE critical-defect rate that blocks the feed. |
| `dup_ceiling` | 0.004 | Duplicate-record rate that blocks the feed. |
| `warn_fraction` | 0.50 | Fraction of a ceiling at which the warn band starts. |
| `supporting_ceiling` | 0.02 | Supporting CDE any-defect rate that triggers investigation. |
| `staleness_ceiling` | 0.10 | Stale-record rate that triggers investigation. |
| `composite_floor` | 0.98 | Composite score required for FEED_PASS. |
| `staleness_horizon_days` | 365 | Policy refresh horizon for ACTIVE records. |
| `near_dup_name_sim` | 0.85 | Jaro-Winkler floor for near-duplicate names. |

The country reference set, the identifier format and check-digit contract, and
the DOB plausibility floor are named constants in `scorer.py` and are
themselves calibration points — a real deployment substitutes its documented
standards.

---

## 8. Governance and boundaries

Mapped to public guidance — SR 11-7 / OCC 2011-12 (conceptual soundness,
outcomes analysis, ongoing monitoring, limitations), the FFIEC BSA/AML
Examination Manual's expectation that institutions understand and test the
data feeding their screening and monitoring systems, and BCBS 239's principles
on accuracy, completeness, and timeliness of risk data aggregation — per the
shared [`../GOVERNANCE.md`](../GOVERNANCE.md).

Boundaries stated honestly: duplicate detection is identifier-blocked, so
same-party records holding *different* identifiers are out of scope (that is
an entity-resolution control); identifier collisions across dissimilar names
are likewise a separate control; the engine assesses one extract at a time and
does not trend across batches (the composite score is the input a trending
control would consume). The engine assesses and routes; accepting, holding, or
remediating a feed is a human decision, auditable through the named reason and
the per-record defect list.
