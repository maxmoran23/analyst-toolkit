# Methodology — Adverse-Media Screening Disposition Engine

The regulator-facing specification of the scoring and disposition logic. Every input,
component, threshold, and rule below exists as a named construct in
[`scorer.py`](scorer.py); that file is the executable form. Evidence:
[`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md). Shared governance:
[`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** A negative-news screening tool flags an article whenever
> someone with a name like your customer's appears in it. Most flags are wrong two
> ways: the article is about a *different* person with the same name, or it's about
> your customer but isn't actually bad news (a press release, or they're the
> *victim*, or it's ancient history). This engine sorts each flag — clear it (only
> with a concrete reason), review it, or escalate it (a confirmed match on serious
> recent wrongdoing). The one thing it won't do is auto-clear a flag it can't
> resolve: a plain "John Smith" match with no date of birth or country goes to a
> person, because it might really be them.

---

## 1. Problem framing and the two false-positive axes

A media-screening tool surfaces articles whose subject name matches a customer. The
large majority are false positives on one of two axes:

- **Entity axis** — the article is about a *different* party with a similar name
  (the same name-collision problem as sanctions screening).
- **Relevance axis** — the article is about the customer but is not materially
  adverse: a non-negative item, a victim/passing-mention role, or stale minor news.

Error costs are asymmetric, as in the other frameworks: a **false negative**
(clearing a genuine adverse match on a customer) is a due-diligence failure with
zero tolerance; a **false positive** (keeping a non-match in the queue) is
operational cost.

## 2. Inputs

**Subject** (the customer): `name`, `entity_type`, sparse `ids` (country, dob, …).
**MediaHit**: `article_name` (name as it appears in the article), `category` (the
adverse category from the media classifier), `role` (perpetrator / alleged /
associate / victim / mentioned), `age_days`, sparse `article_ids`,
`source_reliability`.

## 3. Entity resolution (reused from sanctions)

The customer name is compared to the article subject name with the same IDF-weighted
matcher the sanctions framework uses (`_lib/match`, `_lib/text_normalize`):
`name_score = weighted_overlap × (0.4 + 0.6 × coverage)`. Identifiers are compared to
classify a contradiction as a **strong** discriminator (DOB / passport / national-id
/ registration) or a **weak** one (country / nationality), and to record positive
corroboration.

`entity_strength` ∈ [0,1] = `name_score`, boosted by a corroborating identifier, and
**capped at 0.5 for a common-name match with no corroborating identifier** — a match
on a common name alone is only moderate confidence, because it could be a different
person of the same name.

## 4. Relevance (new — `_lib/relevance`)

`relevance = category_severity × role_weight × recency_decay × source_reliability`,
each in [0,1]. Category severities run from terrorism-financing / sanctions-evasion
(1.0) down through money-laundering (0.92), fraud / corruption (0.85), tax evasion
(0.70), regulatory enforcement (0.60), civil litigation (0.40), general negative
(0.30), to non-adverse (0.0). Role weights: perpetrator 1.0, alleged 0.85, associate
0.55, victim 0.20, mentioned 0.15. Recency uses a ~3-year half-life.

`combined = entity_strength × relevance` is the ranking score: a serious article
about a different person scores low (low entity_strength), and a positive article
about the customer scores low (zero relevance).

## 5. Disposition rules (in firing order)

Named clear causes first; the combined score only ranks what survives.

1. **AUTO_CLEAR — wrong_entity.** Fires on positive proof of a different party: a
   contradicting **strong** identifier (clears even an exact name), a contradicting
   **weak** identifier on a non-exact name, or essentially no name overlap
   (`name_score < 0.15`). A bare common-name match with no identifier is **not**
   cleared here.
2. **AUTO_CLEAR — not_adverse.** The category is non-adverse (no negative news).
3. **AUTO_CLEAR — low_role.** The subject is a victim or passing mention, not a
   perpetrator — no adverse-conduct risk to the customer.
4. **AUTO_CLEAR — stale_immaterial.** Older than `stale_days` (5 years) and below the
   materiality severity (≤ 0.45 — civil litigation / general negative).
5. **ESCALATE.** `entity_strength ≥ match_floor` (0.55) and `relevance ≥
   escalate_relevance` (0.50) — a confirmed match on material, recent adverse
   content; routed for enhanced review.
6. **ANALYST_REVIEW** — everything else, priority by `combined` (HIGH ≥ 0.40,
   MEDIUM ≥ 0.18, else LOW). This includes the **common-name-ambiguous** residual: a
   common-name match on adverse content with no identifier, which can be neither
   cleared nor confirmed and must be worked by a human.

### Why false-negative safety is structural

A genuine adverse match is a name-match on materially adverse content with the
subject as a perpetrator or alleged actor. It therefore satisfies **none** of the
four clear causes: it is not wrong-entity (the name matches and no identifier
contradicts), not non-adverse, not low-role, and not stale-immaterial. The
unidentifiable common-name case is routed to review, never cleared. The validation
harness enforces this as a build gate (recall floor 1.0).

## 6. Tunable constants

`scorer.Config`: `match_floor` (0.55), `escalate_relevance` (0.50), `stale_days`
(1825), `immaterial_max_severity` (0.45), `near_exact_name` (0.95),
`generic_max_share` (0.005), review bands. The category severities, role weights, and
recency half-life in `_lib/relevance` are the deeper calibration surface. See
[`tuning.md`](tuning.md).

## 7. Governance and boundaries

Mapped to public guidance per [`../GOVERNANCE.md`](../GOVERNANCE.md) (SR 11-7, FFIEC,
FATF, Wolfsberg). The engine dispositions screening hits; the enhanced-review, exit,
or SAR decision is a documented human action. Note the dependency: `category` and
`role` come from an upstream media classifier whose own error rate compounds with
this engine's — a real deployment validates that classifier as part of the model.
