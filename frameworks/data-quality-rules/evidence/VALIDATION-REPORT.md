# Validation Report — Data-Quality Rules Framework (CDE fitness for screening)

> ILLUSTRATIVE / SYNTHETIC. Every figure is produced by running the reference engine over a seeded, fully synthetic Harborview Financial Group customer extract. No real customer or record is represented. Numbers are emitted by `run_validation.py`, not authored; re-run it to reproduce them.

**Run:** seed `42` · 50,000 records · 5 scenario feeds x 10,000 · git `d2f4ef1` · 2026-07-10 05:09 UTC

**Headline:** recall on planted critical defects **1.0000** (missed: **0** of 2,750), false-flag rate on clean records **0.0000%** (0 of 42,250, including the adversarial-benign edge cases), and no critical-breach feed passed — the contaminated main feed was correctly dispositioned **BLOCK_FEED_TO_SCREENING** while the conformant scenario feed passed.

## 1. Methodology summary
The engine evaluates named data-quality rules across five dimensions (COMPLETENESS, VALIDITY, CONSISTENCY, UNIQUENESS, TIMELINESS), each rule bound to a critical data element with a documented criticality weight. It produces a per-CDE scorecard, a record-level defect list with named rule and severity, and a feed disposition: FEED_PASS only on the provable named cause that every documented threshold is met; INVESTIGATE on named warn-band or supporting-CDE causes; BLOCK_FEED_TO_SCREENING whenever any screening-critical CDE breaches its ceiling — a hard gate no weighted score can override. The engine never drops or repairs a record. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
50,000 extract records with deterministic per-class plant counts: 2,750 critical defects across 8 classes, 5,000 minor defects, and 42,250 clean records — of which 3,000 are adversarial-BENIGN edge cases (accented/hyphenated names, leap-day and boundary DOBs, refresh just inside the horizon) that must NOT be flagged. Adversarial plants include format-valid-calendar-false DOBs, DOBs valid in format but impossible in sequence, ISO-adjacent-but-wrong country codes, and transliterated near-duplicate pairs sharing an identifier.

## 3. Operating-point results
- **Recall on planted critical defects: 1.0000** — **missed: 0**
- False-flag rate on clean records: 0.0000% (0 of 42,250)
- Precision of the critical flag: 1.0000 · specificity 1.0000
- Confusion (critical flag) — TP 2,750 · FP 0 · TN 47,250 · FN 0
- Weighted composite DQ score of the main feed: 0.9834 · disposition **BLOCK_FEED_TO_SCREENING**

Field-level scorecard (per CDE):

| cde | screening_critical | weight | defect_rate | critical_rate | pass_rate | ceiling | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_name | yes | 1.0 | 0.018 | 0.008 | 0.982 | 0.005 | BREACH |
| dob | yes | 1.0 | 0.019 | 0.019 | 0.981 | 0.005 | BREACH |
| country | yes | 1.0 | 0.01 | 0.01 | 0.99 | 0.005 | BREACH |
| national_id | yes | 1.0 | 0.0178 | 0.008 | 0.9822 | 0.005 | BREACH |
| record_uniqueness | yes | 1.0 | 0.01 | 0.01 | 0.99 | 0.004 | BREACH |
| entity_type | no | 0.4 | 0.0187 | 0.0 | 0.9813 | 0.02 | OK |
| onboarding_date | no | 0.4 | 0.0095 | 0.0 | 0.9905 | 0.02 | OK |
| account_prefix | no | 0.3 | 0.012 | 0.0 | 0.988 | 0.02 | OK |
| last_refresh | no | 0.5 | 0.04 | 0.0 | 0.96 | 0.1 | OK |

Per-dimension pass rates:

| dimension | pass_rate |
| --- | --- |
| COMPLETENESS | 0.947 |
| VALIDITY | 0.9716 |
| CONSISTENCY | 0.9764 |
| UNIQUENESS | 0.99 |
| TIMELINESS | 0.96 |

## 4. Per-category detection
Critical classes — every planted defect must be caught at critical severity (this is the gate):

| class | planted | detected | detection_rate | detected_by |
| --- | --- | --- | --- | --- |
| null_name_active | 400 | 400 | 1.0 | name_missing_active |
| missing_dob | 250 | 250 | 1.0 | dob_missing |
| malformed_dob | 400 | 400 | 1.0 | dob_unparseable |
| impossible_dob_sequence | 300 | 300 | 1.0 | dob_after_onboarding, dob_out_of_range |
| country_drift | 500 | 500 | 1.0 | country_invalid |
| invalid_id_checksum | 400 | 400 | 1.0 | id_format_invalid |
| exact_dup | 250 | 250 | 1.0 | duplicate_exact |
| near_dup_shared_id | 250 | 250 | 1.0 | duplicate_near |

Minor classes — flagged at minor severity for the remediation queue; deliberately NOT part of the hard gate:

| class | planted | detected | detection_rate | detected_by |
| --- | --- | --- | --- | --- |
| null_name_inactive | 500 | 500 | 1.0 | name_missing_inactive |
| missing_supporting | 1500 | 1500 | 1.0 | entity_type_missing, id_missing |
| prefix_country_mismatch | 600 | 600 | 1.0 | prefix_country_mismatch |
| entity_dob_conflict | 400 | 400 | 1.0 | entity_dob_conflict |
| stale_refresh | 2000 | 2000 | 1.0 | refresh_stale |

## 5. Threshold-sensitivity analysis (near-duplicate name similarity)
A NAME-SIMILARITY-ONLY near-duplicate detector (phonetic and single-edit fallbacks disabled), for comparison. The deployed detector pairs the Jaro-Winkler threshold with a per-token Soundex fallback (holds MOHAMMED/MUHAMMAD) and a single-edit tolerance (holds OMAR/UMAR, which defeats both Jaro-Winkler and Soundex), keeping recall at 1.0 at the default threshold (0.85). Similarity-only leaks transliterated pairs as the threshold rises; false pairs stay at zero throughout because duplicate detection is blocked on a shared identifier.

| threshold | near_dup_detected | near_dup_recall | exact_dup_recall | false_pair_records |
| --- | --- | --- | --- | --- |
| 0.7 | 250 | 1.0 | 1.0 | 0 |
| 0.75 | 250 | 1.0 | 1.0 | 0 |
| 0.8 | 246 | 0.984 | 1.0 | 0 |
| 0.85 | 220 | 0.88 | 1.0 | 0 |
| 0.88 | 204 | 0.816 | 1.0 | 0 |
| 0.9 | 180 | 0.72 | 1.0 | 0 |
| 0.92 | 110 | 0.44 | 1.0 | 0 |
| 0.95 | 48 | 0.192 | 1.0 | 0 |
| 0.98 | 0 | 0.0 | 1.0 | 0 |

## 6. False-negative safety argument
**Statistical bound.** 0 misses were observed among 2,750 labelled planted critical defects. Observing zero failures is not a guarantee of a zero failure rate: the exact one-sided 95% Clopper-Pearson upper bound on the miss rate is **0.1089%** (recall at least **99.8911%**) *on this synthetic population*. The bound is a property of the sample size, not a promise about live data — it tightens only by testing more true cases.

1. Of 2,750 planted critical defects, **0 were missed** — recall 1.0000. Every class is caught by a deterministic parser or rule, not a statistical guess: blank-name and blank-DOB checks, a strict ISO/calendar date parse, the approved country reference set, the identifier check-digit contract, the DOB/onboarding ordering test, and identifier-blocked duplicate detection with phonetic and single-edit fallbacks.
2. The feed-level gate is structural: the BLOCK branch is evaluated before any pass logic, so a screening-critical breach can never be outweighed by a high composite score. FEED_PASS is only reachable when every screening-critical CDE is at or below its warn threshold.
3. Both are enforced as build gates — `run_validation.py` exits non-zero if any planted critical defect goes undetected, if any feed with a planted screening-critical breach receives FEED_PASS, or if the scenario grid below deviates from its expected outcomes.

Feed-disposition scenario grid (deterministic plant counts, so expected outcomes are stable across seeds):

| feed | records | expected | disposition | composite | outcome |
| --- | --- | --- | --- | --- | --- |
| clean | 10000 | FEED_PASS | FEED_PASS | 1.0 | OK |
| minor_degraded | 10000 | INVESTIGATE | INVESTIGATE | 0.989 | OK |
| warn_band | 10000 | INVESTIGATE | INVESTIGATE | 0.9995 | OK |
| critical_breach | 10000 | BLOCK_FEED_TO_SCREENING | BLOCK_FEED_TO_SCREENING | 0.9961 | OK |
| dup_contaminated | 10000 | BLOCK_FEED_TO_SCREENING | BLOCK_FEED_TO_SCREENING | 0.9976 | OK |

## 7. Volume / remediation impact
50,000 records → 42,250 clean pass-through (84.5%) → 7,750 routed to the remediation queue (15.5%: 2,750 with a critical defect, 5,000 minor-only), each with a named rule and detail string. The feed disposition routes the FEED; the defect list routes the RECORDS. Nothing is dropped or silently repaired.

## 8. Limitations
- Synthetic data models the failure shapes of a customer extract (nulls, format drift, impossible sequences, re-onboarded duplicates), not the full richness of a production golden source. Recalibrate ceilings and the similarity threshold on your own profiled extracts (`tuning.md`).
- Duplicate detection is blocked on a shared national identifier; same-party pairs holding DIFFERENT identifiers, and identifier collisions across dissimilar names, are separate controls outside this engine's scope and are not claimed.
- The reference set, identifier contract, and policy horizon are illustrative stand-ins for the institution's documented standards.
- The engine assesses and routes; it never blocks records, repairs values, or approves a feed autonomously — FEED_PASS is a named, evidence-backed recommendation to the data-governance owner.
- This is a transparent reference implementation, not a production control.

## 9. Reproduction
```bash
python3 run_validation.py --seed 42 --records 50000
```
Same seed → identical extract → identical numbers.
