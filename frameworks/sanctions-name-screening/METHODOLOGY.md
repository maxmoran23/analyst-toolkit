# Methodology — Sanctions Name-Screening Disposition Engine

This is the regulator-facing specification of the scoring and disposition logic.
Every input, component, weight, threshold, and decision rule below exists as a
named constant or branch in [`scorer.py`](scorer.py); that file is the executable
form of this document, and the two are kept in step. The validation evidence that
the logic performs as specified is in [`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md),
produced by [`run_validation.py`](run_validation.py) over a seeded synthetic
population.

> **In plain terms:** A sanctions filter throws an alert whenever a payment or
> customer shares a word with a name on a sanctions list. Almost all of these are
> coincidences — a company called "Harborview **Capital**" trips on a sanctioned
> entity that also contains "Capital". This engine reads each alert and sorts it
> into three buckets: *clear it* (only when it can state a concrete reason the
> match is false), *send it to an analyst* (ranked by how concerning it is), or
> *escalate it* (name and identifiers both line up). It never blocks a payment or
> files a report on its own — a person always makes that call.

---

## 1. Problem framing and error posture

A sanctions screening filter flags an alert when a payment- or customer-party name
shares one or more tokens with a watchlist entry. In production the overwhelming
majority — often 95–99% — are false positives driven by common-token collisions.
The institution must disposition every alert; the volume is the operational
problem (the ~50,000-per-month backlog), and the discipline is the regulatory one.

The two error types are not symmetric:

- A **false negative** — clearing an alert that is a genuine sanctions match — is
  a regulatory and legal failure (a potential prohibited transaction processed,
  an OFAC violation). Its tolerated rate is **zero**.
- A **false positive** — keeping a non-match in the review queue — is operational
  cost. Reducing it is the value the engine delivers, but never at the expense of
  the line above.

The engine is therefore built as a **false-positive suppression and
prioritization** tool, not an auto-decision tool. It is calibrated to a
conservative operating point and its safety property (never auto-clear a true
match) is enforced structurally and as a build gate, not assumed.

---

## 2. Inputs

Each alert is a **(party, entry)** pair the upstream filter produced.

**Party** (the screened payment/customer party): a `name`, an `entity_type`
(`INDIVIDUAL` / `ENTITY` / `VESSEL` / `AIRCRAFT` / `CRYPTO` / `UNKNOWN`), and a
sparse `ids` map — any of `dob`, `nationality`, `country`, `place_of_birth`,
`passport`, `national_id`, `registration`, `imo`, `tail_number`, `wallet`. Wire
and payment messages are identifier-poor, so most fields are usually absent.

**Watchlist entry** (the designated party): `uid`, `name`, `entity_type`,
`program`, a list of `aliases` (strong and weak AKAs), and the same `ids` map.

---

## 3. Normalization and tokenization

Names are normalized deterministically (`_lib/text_normalize.normalize`): accents
folded to ASCII, uppercased, punctuation stripped, whitespace collapsed. Tokens
are split on whitespace; tokens below 2 characters and **structural tokens**
(corporate form — LTD, LLC, GMBH, JSC… — and honorifics/connectors — MR, SHEIKH,
VON, AL…) are dropped before matching so they never anchor a match.

### Token informativeness (the CAPITAL/ROAD defuser)

Each token carries a weight equal to its **inverse document frequency (IDF)** over
the watchlist corpus, smoothed as `idf(t) = ln((N+1)/(df(t)+1)) + 1`. A token
appearing in many entries (CAPITAL, TRADING) is near the floor; a rare token
(ROSOBORONEXPORT) is near the ceiling. A token is classified **generic** when it
is structural, or when its **document-frequency share** `df(t)/N` meets or exceeds
`generic_max_share` (default **0.005** — present in ≥0.5% of entries).

> Document-frequency *share* is used, not an IDF percentile, because it is
> corpus-size invariant: a token in 1.3% of a 4,000-name list is in 1.3% of a
> 400,000-name list, so the threshold holds as the reference set scales. For
> production, `generic_max_share` should be calibrated against the screened
> *population* (the institution's own customer/payment names), where genericness
> is most accurately measured. See [`tuning.md`](tuning.md).

---

## 4. Scoring components

For each (party, entry) the engine computes three components, then a continuous
`match_likelihood` used for ranking and calibration. The party name is compared
against the entry's primary name **and every alias**; the strongest alignment is
kept (a true match may align to an AKA, not the primary name).

### 4.1 Name score

Token alignment is greedy: a party token aligns to an entry token if they are
equal, share a Soundex phonetic class, or have Jaro-Winkler similarity ≥ 0.88
(Soundex backstops transliteration variance such as ABDULLAH/ABDALLAH; Jaro-Winkler
is the record-linkage standard for proper nouns). From the aligned set:

- `weighted_overlap` = IDF mass of aligned tokens ÷ IDF mass of the **party** name
  (how much of the party's informative content matched).
- `coverage` = IDF mass of aligned tokens ÷ IDF mass of the **entry** name (how
  much of the *designated* name matched — a single incidental token of a long
  entry name scores low here even if it is the party's whole name).

```
name_score = weighted_overlap × (0.4 + 0.6 × coverage)
```

The 0.4/0.6 split requires a strong match to cover most of *both* names' informative
mass; it floors a single-token incidental overlap. A match built only from generic
tokens yields a low `weighted_overlap` and the `only_generic` flag (see §4.4).

### 4.2 Entity-type concordance

```
type_score = 1.0   same type
           = 0.7   either side UNKNOWN (cannot penalize a missing type)
           = 0.0   structurally incompatible (e.g. INDIVIDUAL vs VESSEL,
                   ENTITY vs INDIVIDUAL, CRYPTO vs anything non-crypto)
           = 0.5   otherwise
```

A corporate party matching a designated *vessel* on a shared token is, on its face,
a false positive. Incompatible pairs are enumerated explicitly in `scorer.py`
(`_INCOMPATIBLE`).

### 4.3 Identifier corroboration and discrimination

Identifier fields split by discriminating power. **Strong**: `dob`, `passport`,
`national_id`, `registration`, `imo`, `tail_number`, `wallet`. **Weak**:
`nationality`, `country`, `place_of_birth`. Comparing the fields present on both
sides:

- `corroboration` = **STRONG** if ≥1 strong field matches or ≥2 weak fields match;
  **PARTIAL** if exactly 1 weak field matches; else **NONE**.
- `discriminator` = the first **strong** field that is present on both sides and
  *contradicts* (or, absent any strong field, the first contradicting weak field).
  A discriminator is the named fact that clears a false positive — a different
  date of birth, a different nationality.

### 4.4 Match likelihood

A single continuous score in [0,1] for ranking and threshold calibration:

```
base = name_score × type_score
if only_generic:                         base = min(base, 0.05)
if type_score == 0:                      base = min(base, 0.05)
if discriminator and name_score < 0.95:  base = min(base, 0.05)      # near_exact_name
elif corroboration == STRONG:            base = base + (1 − base) × 0.40
elif corroboration == PARTIAL:           base = base + (1 − base) × 0.15
match_likelihood = clamp(base, 0, 1)
```

The likelihood is a ranking/calibration aid. It does **not** by itself decide a
clearance — that is the role of the named rules in §5.

---

## 5. Disposition rules (in firing order)

Categorical, **named** rules fire first; the score only ranks what survives them.
Auto-clear requires a nameable, provable false-positive cause — never a low score
alone. Order matters: the most defensible cause is stated as the reason.

1. **AUTO_CLEAR — generic-token-only.** Fires when every aligned token is generic
   **and the entry carries at least one distinctive token the party did not match**.
   The reason names the matched generic tokens and the unmatched distinctive
   token(s). The second condition is the structural false-negative guard: if the
   designated entity's *own* name is entirely generic, it cannot be ruled out by
   name and is **not** cleared here — it falls through to review.

2. **AUTO_CLEAR — entity-type incompatible.** Fires when `type_score == 0`. The
   reason names both types.

3. **AUTO_CLEAR — named discriminator.** Fires when a discriminating identifier
   contradicts the entry **and** `name_score < 0.95` (`near_exact_name`). The
   near-exact guard means an *exact* full-name match is never cleared by a single
   conflicting field — that becomes an analyst reconciliation, not a clearance.

4. **ESCALATE — likely true match.** Fires when `corroboration == STRONG` and
   `name_score ≥ 0.60` (`escalate_name_floor`). Routed to a compliance officer
   with the evidence assembled. The engine still does not block or file.

5. **ANALYST_REVIEW — everything else**, priority-ranked: **HIGH** if
   `name_score ≥ 0.50` or `match_likelihood ≥ 0.50` (`review_high`); **MEDIUM** if
   `match_likelihood ≥ 0.25` (`review_medium`); else **LOW**. This is the
   irreducible band — genuine name overlap with insufficient identifier evidence
   to confirm or clear, worked riskiest-first.

### Why false-negative safety is structural

A true match — the party *is* the designated entity — has a distinctive name that
aligns (transliteration variance is vowel-class, which the Soundex backstop
re-aligns), a compatible entity type, and identifiers that either corroborate or
are absent (never contradict). It therefore satisfies **none** of the three
auto-clear causes: it is not generic-only against an entry with an unmatched
distinctive token, its type is not incompatible, and it has no contradicting
identifier. Auto-clear is reachable only by a provable false-positive cause a true
match cannot exhibit. The validation harness enforces this as a build gate
(recall floor 1.0; any auto-cleared true match fails the build).

---

## 6. Tunable constants (the operating point)

All live in `scorer.Config`; defaults are the conservative posture. Recalibration
procedure is in [`tuning.md`](tuning.md).

| Constant | Default | Effect |
|---|---|---|
| `generic_max_share` | 0.005 | df-share at/above which a token is generic. Higher → more tokens treated as generic → more aggressive clearing. |
| `escalate_name_floor` | 0.60 | Min `name_score` to escalate with strong corroboration. |
| `near_exact_name` | 0.95 | `name_score` at/above which a discriminator cannot auto-clear. |
| `review_high` | 0.50 | `match_likelihood` / `name_score` for HIGH analyst priority. |
| `review_medium` | 0.25 | `match_likelihood` for MEDIUM analyst priority. |

---

## 7. Model-governance framing (SR 11-7)

Mapped to public guidance — Federal Reserve / OCC **SR 11-7** and **OCC Bulletin
2011-12** (model risk management), the **FFIEC BSA/AML Examination Manual**
(screening program expectations), and **Wolfsberg Group** guidance on sanctions
screening control effectiveness and threshold testing. Generic and public; no
institution-specific policy. See the shared [`../GOVERNANCE.md`](../GOVERNANCE.md)
for the full framing.

- **Conceptual soundness.** Every component, weight, threshold, and rule is
  documented here and implemented transparently in pure-readable Python — no black
  box. The matching approach (IDF-weighted token similarity, phonetic backstop,
  identifier corroboration) follows established record-linkage and screening
  practice.
- **Outcomes analysis.** `run_validation.py` computes recall, false-positive
  reduction, per-category clear rates, a threshold-sensitivity sweep, and a
  volume funnel over a labelled synthetic population, reproducibly from seed. An
  independent reviewer re-runs it to reproduce every number.
- **Ongoing monitoring.** The recall floor is a build-gate invariant; the
  multi-seed stability run shows the result is not a single-seed artifact;
  `tuning.md` defines the recalibration cadence and procedure.
- **Limitations and assumptions.** Stated in the validation report's Limitations
  section: synthetic data models the *shape* of screening, not the full messiness
  of real wire text; the engine scores and prioritizes but does not decide; this
  is a transparent reference implementation, not a production control — a
  deployment recalibrates against the institution's own labelled data.

---

## 8. Boundaries

The engine **scores and routes**. It does not block payments, does not file
reports, and does not make a clearance decision a regulator would hold the
institution to without human review. A confirmed match is a human compliance-officer
action. A cleared alert is auditable by its named reason and its component
breakdown; nothing is cleared that cannot be explained.
