# Validation Report — Adverse-Media-Screening Framework

> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the reference scorer over a seeded, fully synthetic population. No real person or article is represented. Numbers are emitted by `run_validation.py`, not authored.

**Run:** seed `42` · 8,000 subjects · 50,000 hits · git `6d2ef9d` · 2026-06-23 13:12 UTC

**Headline:** recall on genuine adverse matches **1.0000** (false negatives: **0**), false-positive reduction **79.9%**, human review volume cut by **76.0%** (50,000 hits → 12,018 to a human).

## 1. Methodology summary
Each media hit is dispositioned AUTO_CLEAR / ANALYST_REVIEW / ESCALATE on two axes — is it the right party (entity resolution, reusing the sanctions name-matching engine), and is it materially adverse (category, role, recency). Auto-clears only on a named cause; never auto-clears a confirmed match on material adverse content. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
50,000 hits across 8,000 subjects (a mix of common and distinctive names); ~5% genuine adverse matches. False positives span wrong-party, non-adverse, low-role, stale, and the common-name-ambiguous residual — common-name matches with no identifier, which cannot be cleared OR confirmed and must go to a human.

## 3. Operating-point results
- **Recall (adverse matches retained): 1.0000** — **false negatives: 0**
- False-positive reduction (specificity): 0.7991
- Precision of the retained queue: 0.2054
- Confusion — TP 2,468 · FP 9,550 · TN 37,982 · FN 0

| Disposition | Count | Share |
| --- | --- | --- |
| AUTO_CLEAR | 37,982 | 76.0% |
| ANALYST_REVIEW | 10,571 | 21.1% |
| ESCALATE | 1,447 | 2.9% |

Analyst-review priority — HIGH 3,361 · MEDIUM 6,687 · LOW 523.

## 4. Per-category false-positive clear rate
The `common_name_ambiguous` band — a common-name match with no identifier — is deliberately NOT auto-cleared: it cannot be resolved without more information, so it is the irreducible queue a human must work. The other categories clear on a named, provable cause.

| fp_category | count | auto_cleared | clear_rate |
| --- | --- | --- | --- |
| wrong_entity | 14278 | 14278 | 1.0 |
| not_adverse | 11989 | 11989 | 1.0 |
| low_role | 6043 | 6043 | 1.0 |
| stale_immaterial | 5672 | 5672 | 1.0 |
| common_name_ambiguous | 9550 | 0 | 0.0 |

## 5. Threshold-sensitivity analysis
A naive policy auto-clearing on the combined score `<= T`, for comparison. The deployed policy clears only on a named cause, holding recall at 1.0 by construction while a bare threshold leaks true matches as it rises.

| threshold | fp_cleared | fp_clear_rate | fn_leaked | recall |
| --- | --- | --- | --- | --- |
| 0.0 | 11989 | 0.2522 | 0 | 1.0 |
| 0.05 | 17713 | 0.3727 | 0 | 1.0 |
| 0.1 | 37982 | 0.7991 | 5 | 0.998 |
| 0.15 | 37982 | 0.7991 | 259 | 0.8951 |
| 0.2 | 37982 | 0.7991 | 657 | 0.7338 |
| 0.3 | 37982 | 0.7991 | 998 | 0.5956 |
| 0.4 | 44171 | 0.9293 | 1021 | 0.5863 |
| 0.5 | 47532 | 1.0 | 1021 | 0.5863 |
| 0.6 | 47532 | 1.0 | 1021 | 0.5863 |
| 0.7 | 47532 | 1.0 | 1117 | 0.5474 |
| 0.8 | 47532 | 1.0 | 1739 | 0.2954 |

## 6. False-negative safety argument
1. Of 2,468 genuine adverse matches, **0 were auto-cleared** — recall 1.0000.
2. Safety is structural: a genuine adverse match is a name-match on materially adverse content with the subject as a perpetrator/alleged actor, so it cannot satisfy any of the four clear causes (wrong-entity, non-adverse, low-role, stale-immaterial). A common-name match with no identifier is never cleared — it is routed to review precisely because it cannot be safely resolved.
3. Enforced as a build gate — `run_validation.py` exits non-zero if any genuine adverse match is auto-cleared.

## 7. Volume / funnel impact
50,000 hits → 37,982 auto-cleared (76.0%) → 12,018 to a human (24.0%), with recall held at 1.0. FP reduction is bounded by the common-name-ambiguous residual, which is left open by design rather than cleared — the honest outcome for unidentifiable matches.

## 8. Limitations
- Synthetic data models the two false-positive axes (wrong party, non-material content), not the full nuance of real news text or a real media classifier. Category and role here are taken as given; in production they come from an upstream NLP classifier whose own error rate compounds. Calibrate against a labelled sample (`tuning.md`).
- The engine dispositions screening hits; the enhanced-review / exit / SAR decision is a documented human action.
- A transparent reference implementation, not a production control.

## 9. Reproduction
```bash
python3 run_validation.py --seed 42 --subjects 8000 --hits 50000
```
