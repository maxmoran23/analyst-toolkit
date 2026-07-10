# Validation Report — PEP-Screening Framework

> ILLUSTRATIVE / SYNTHETIC. Every figure below is produced by running the reference scorer over a seeded, fully synthetic population. All officials, countries, and offices are fictional; no real person is represented. Numbers are emitted by `run_validation.py`, not authored; re-run it to reproduce them.

**Run:** seed `42` · 8,000 PEP-list entries · 50,000 alerts · git `7e2eb3f` · 2026-07-09 22:00 UTC

**Headline:** recall on genuine in-scope PEP matches **1.0000** (false negatives: **0**), false-positive reduction **84.1%**, human review volume cut by **80.7%** (50,000 alerts → 9,631 to a human).

## 1. Methodology summary
Each alert (a customer an upstream filter matched to a PEP-list entry) is dispositioned AUTO_CLEAR / ANALYST_REVIEW / ESCALATE_ENHANCED_REVIEW on two axes — is it the right party (IDF-weighted name matching plus DOB/nationality corroboration), and does the entry carry material PEP risk (prominence tier x status decay x jurisdiction bucket). Auto-clears only on a named cause (wrong_party, generic_token_only, out_of_scope_status); never clears any current PEP match, any TIER_1/TIER_2 match, or any corroborated match. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
50,000 alerts against 8,000 fictional PEP-list entries (invented officials of invented countries). True in-scope matches are ~4% of volume. Every false positive carries a category; adversarial plants include transliteration-noisy current TIER_1 matches, common-name true PEPs, RCAs under different surnames, former officials still inside the step-down horizon, and adverse-flagged entries past it — the cases designed to defeat the clearing rules.

## 3. Operating-point results (deployed named-reason policy)
- **Recall (in-scope match retention): 1.0000** — **false negatives: 0**
- False-positive reduction (specificity): 0.8414
- Precision of the retained queue: 0.2098
- Confusion — TP 2,021 · FP 7,610 · TN 40,369 · FN 0

| Disposition | Count | Share |
| --- | --- | --- |
| AUTO_CLEAR | 40,369 | 80.7% |
| ANALYST_REVIEW | 8,916 | 17.8% |
| ESCALATE_ENHANCED_REVIEW | 715 | 1.4% |

Analyst-review priority split — HIGH 1,364 · MEDIUM 5,457 · LOW 2,095.

## 4. Per-category false-positive clear rate
Did the engine clear each false-positive type for the right named reason? The `common_name_ambiguous` band — a common-name match with no identifier either way — is deliberately NOT auto-cleared: it cannot be resolved without more information. The `out_of_scope_former` clear rate is below 1.0 by design: the minority of those alerts whose nationality corroborates the entry are routed to a human, because a corroborated identity match on a list entry is never auto-cleared.

| neg_category | count | auto_cleared | clear_rate |
| --- | --- | --- | --- |
| wrong_party_common_name | 12520 | 12520 | 1.0 |
| wrong_party_translit | 5762 | 5762 | 1.0 |
| generic_token | 11487 | 11433 | 0.9953 |
| out_of_scope_former | 12485 | 10654 | 0.8533 |
| common_name_ambiguous | 5725 | 0 | 0.0 |

## 5. Threshold-sensitivity analysis
A naive policy that auto-cleared on `combined <= T` alone, for comparison. The first true matches a bare threshold clears are exactly the ones the step-down design protects: formerly senior officials whose materiality has decayed to a low — but deliberately non-zero — value. The named-reason policy holds recall at 1.0 by construction; every clearance it makes carries an individual, auditable cause.

| threshold | fp_cleared | fp_clear_rate | fn_leaked | recall |
| --- | --- | --- | --- | --- |
| 0.0 | 17125 | 0.3569 | 0 | 1.0 |
| 0.02 | 22713 | 0.4734 | 0 | 1.0 |
| 0.05 | 36498 | 0.7607 | 20 | 0.9901 |
| 0.1 | 40981 | 0.8541 | 148 | 0.9268 |
| 0.15 | 42043 | 0.8763 | 259 | 0.8718 |
| 0.2 | 43488 | 0.9064 | 420 | 0.7922 |
| 0.3 | 46468 | 0.9685 | 684 | 0.6616 |
| 0.4 | 47787 | 0.996 | 1027 | 0.4918 |
| 0.5 | 47970 | 0.9998 | 1330 | 0.3419 |
| 0.6 | 47972 | 0.9999 | 1634 | 0.1915 |
| 0.7 | 47974 | 0.9999 | 1703 | 0.1573 |
| 0.8 | 47978 | 1.0 | 1913 | 0.0534 |

## 6. False-negative safety argument
1. Of 2,021 genuine in-scope PEP matches, **0 were auto-cleared** — recall 1.0000.
2. Safety is structural: a genuine in-scope match cannot exhibit any clearing cause. Its identifiers corroborate or are absent — never doubly contradict — so `wrong_party` cannot fire; its distinctive token aligns (transliteration noise is vowel-only, preserving the phonetic key), and a fully common-named entry has no unmatched distinctive token, so `generic_token_only` cannot fire; and it is in scope — current, TIER_1/TIER_2 (no horizon exists), within the horizon, or adverse-flagged — so `out_of_scope_status` cannot fire.
3. The sweep (Section 5) shows what the deployed policy refuses to do: a bare threshold starts leaking decayed-but-in-scope senior matches almost immediately, because "low combined score" and "safe to clear" are not the same claim.
4. Enforced as a build gate — `run_validation.py` exits non-zero if any in-scope match is auto-cleared.

## 7. Volume / funnel impact
50,000 alerts → 40,369 auto-cleared (80.7%) → 9,631 to a human (19.3%), with recall held at 1.0. FP reduction is bounded by the common-name-ambiguous residual and the corroborated out-of-scope band, both left open by design — the honest outcome for matches that cannot be proven false.

## 8. Limitations
- Synthetic data models the shape of PEP screening (name collisions, transliteration, tier/status/jurisdiction structure), not the messiness of real list vendors' data. Tier assignments, step-down horizons, and jurisdiction buckets here are ILLUSTRATIVE; a deployment sets them from its own policy and recalibrates on labelled alerts (`tuning.md`).
- The engine dispositions screening alerts; the onboarding, enhanced-review, or exit decision is a documented human action. It never approves or blocks a relationship.
- Tier, status, and adverse flags are taken as given from the list; a real deployment validates the upstream list vendor's accuracy alongside this engine.
- A transparent reference implementation chosen for auditability, not a production control.

## 9. Reproduction
```bash
python3 generate_synthetic_data.py --seed 42 --peps 8000 --alerts 50000
python3 run_validation.py --seed 42 --peps 8000 --alerts 50000
```
Same seed → identical population → identical metrics. Fingerprint in `evidence/run-manifest.json`.
