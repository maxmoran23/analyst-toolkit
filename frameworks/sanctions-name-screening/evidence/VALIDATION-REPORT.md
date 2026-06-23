# Validation Report — Sanctions Name-Screening Framework

> ILLUSTRATIVE / SYNTHETIC. Every figure below is produced by running the reference scorer over a seeded, fully synthetic population. No real person, entity, vessel, or list entry is represented. Numbers are emitted by `run_validation.py`, not authored; re-run it to reproduce them.

**Run:** seed `42` · 4,000 watchlist entries · 50,000 alerts · git `ad43c39` · 2026-06-23 06:09 UTC

**Headline:** recall on true matches **1.0000** (false negatives: **0**), false-positive reduction **92.2%**, human review volume cut by **90.4%** (50,000 alerts → 4,801 to a human).

## 1. Methodology summary
The engine dispositions each alert (a payment/customer party an upstream filter matched to a watchlist entry) as AUTO_CLEAR, ANALYST_REVIEW, or ESCALATE. It auto-clears only on a *named, provable* false-positive cause (generic-token-only, entity-type-incompatible, or a contradicting hard identifier) and never auto-blocks or files. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
50,000 alerts against 4,000 watchlist entries. True matches are ~2% of volume, mirroring the false-positive dominance of real screening. Every false positive carries a category so clear rates can be checked against a known cause; true matches come in corroborated, name-only, and transliteration-noisy flavours. The noisy flavour is adversarial by design — vowel-shifted names engineered to score lower — and is the band a naive threshold would wrongly clear.

## 3. Operating-point results (deployed named-reason policy)
- **Recall (true-match retention): 1.0000** — **false negatives: 0**
- False-positive reduction (specificity): 0.9224
- Precision of the retained queue: 0.2077
- Confusion — TP 997 · FP 3,804 · TN 45,199 · FN 0

| Disposition | Count | Share |
| --- | --- | --- |
| AUTO_CLEAR | 45,199 | 90.4% |
| ANALYST_REVIEW | 4,508 | 9.0% |
| ESCALATE | 293 | 0.6% |

Analyst-review priority split — HIGH 3,496 · MEDIUM 1,012 · LOW 0.

## 4. Per-category false-positive clear rate
Did the engine clear each false-positive type for the right named reason? The `weak` residual — genuine partial overlap with no identifiers either way — is deliberately *not* auto-cleared; it is the irreducible band that needs a human.

| fp_category | count | auto_cleared | clear_rate |
| --- | --- | --- | --- |
| generic | 34334 | 34108 | 0.9934 |
| type | 5892 | 5892 | 1.0 |
| discriminator | 4827 | 4624 | 0.9579 |
| weak | 3950 | 575 | 0.1456 |

## 5. Threshold-sensitivity analysis
A naive policy that auto-cleared on `match_likelihood <= T` alone, for comparison. It shows how much false-positive reduction each threshold buys and the false-negative leakage it costs. On this clean synthetic data a threshold in the low band (T≈0.15–0.3) can match the deployed reduction at recall 1.0 — but pushing past it (T≥0.4) immediately begins leaking true matches. The named-reason policy is preferred over that band not for a higher number but for two reasons a single threshold cannot give: every clearance carries an individual, auditable cause (a threshold clear is justified only by 'the score was below T', which does not survive an exam), and on real data, where score distributions overlap far more than here, the same threshold leaks true matches while the named gate does not.

| threshold | fp_cleared | fp_clear_rate | fn_leaked | recall |
| --- | --- | --- | --- | --- |
| 0.0 | 9894 | 0.2019 | 0 | 1.0 |
| 0.05 | 45047 | 0.9193 | 0 | 1.0 |
| 0.1 | 45047 | 0.9193 | 0 | 1.0 |
| 0.15 | 45199 | 0.9224 | 0 | 1.0 |
| 0.2 | 45199 | 0.9224 | 0 | 1.0 |
| 0.3 | 45199 | 0.9224 | 0 | 1.0 |
| 0.4 | 45199 | 0.9224 | 1 | 0.999 |
| 0.5 | 46202 | 0.9428 | 10 | 0.99 |
| 0.6 | 48201 | 0.9836 | 10 | 0.99 |
| 0.7 | 48324 | 0.9861 | 10 | 0.99 |
| 0.8 | 48395 | 0.9876 | 11 | 0.989 |
| 0.9 | 48421 | 0.9881 | 13 | 0.987 |
| 0.95 | 48421 | 0.9881 | 13 | 0.987 |

## 6. False-negative safety argument
1. Of 997 planted true matches, **0 were auto-cleared** — recall 1.0000.
2. Safety is structural, not threshold-dependent: auto-clear fires only on a named, provable false-positive cause. A true match has a distinctive name that aligns (transliteration noise is vowel-only, preserving the phonetic/Soundex key), a compatible entity type, and no contradicting identifier — so it can exhibit none of the three clearing causes.
3. The threshold sweep (Section 5) shows recall holding at 1.0 across the whole low-threshold band the deployed policy operates in, then degrading only when a bare threshold is pushed higher — so the operating point sits on a plateau, not a cliff edge.
4. This recall floor is enforced as a build gate — `run_validation.py` exits non-zero if any true match is auto-cleared.

## 7. Volume / funnel impact
50,000 alerts → 45,199 auto-cleared (90.4%) → 4,801 to a human (9.6%). At the real ~50k/month scale this is the difference between an unworkable queue and a triaged one — achieved with the recall floor held at 1.0.

## 8. Limitations
- Synthetic data models the *shape* of screening (token collisions, identifier discriminators, transliteration), not the full messiness of real wire text. Calibrate against a labelled sample of your own before reliance (`tuning.md`).
- The engine scores and prioritizes; it does not decide. A confirmed match is a human compliance-officer action.
- This is a transparent reference implementation chosen for auditability, not a production control. A real deployment swaps internals and recalibrates the operating point; the scoring *contract* in `METHODOLOGY.md` is what travels.
- Names corrupted past fuzzy-match recognition (beyond realistic transliteration variance) are a data-quality concern upstream of the engine, not modelled here.

## 9. Reproduction
```bash
python3 generate_synthetic_data.py --seed 42 --watchlist 4000 --alerts 50000
python3 run_validation.py --seed 42 --watchlist 4000 --alerts 50000
```
Same seed → identical population → identical metrics. Fingerprint in `evidence/run-manifest.json`.
