# Validation Report — Watchlist Knowledge Base

> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the pipeline over a seeded synthetic multi-list population with known ground truth. No real list data is represented. Numbers are emitted by `run_validation.py`, not authored.

**Run:** seed `42` · 3,000 true entities · 5,447 list records · git `c171ae4` · 2026-06-23 20:58 UTC

**Headline:** **0 false merges** (distinct parties wrongly combined — must be 0, and is structurally guaranteed), auto-merge recall **1.0000** on identifier-linked duplicates, dedup reduction **30.4%** (5,447 records → 3,793 entities); **467** name-only pairs surfaced for analyst review.

## 1. What this validates
The knowledge base ingests public consolidated lists, normalizes them to one schema, resolves the same party across lists, tracks changes between refreshes, and learns from false-positive outcomes. The safety-critical property is that entity resolution NEVER combines two distinct designated parties — a false merge would erase a designation from screening. Full spec: `METHODOLOGY.md`.

## 2. Synthetic-population construction
3,000 true entities, each appearing on 1-3 lists with name variance and a shared strong identifier; plus confusable distractors — pairs that share a distinctive surname token but carry DIFFERENT strong identifiers, which must not merge. Strong identifiers are unique per true entity, so no two distinct entities share one by accident.

## 3. Entity resolution (dedup)
- **False merges (distinct parties combined): 0** — must be 0. Auto-merge fires only on a shared unique identifier, which is unique per party, so a false merge is structurally impossible.
- Auto-merge recall: 1.0000 of 1,177 identifier-linked duplicates unified (of 1,486 multi-list entities total).
- Name-only duplicates (no shared identifier): surfaced as 467 analyst review candidates rather than auto-merged — a retained duplicate is harmless; an erased designation is not.
- Records 5,447 → resolved entities 3,793 (30.4% reduction)

## 4. Change detection (delta)
Planted {'added': 25, 'removed': 20, 'amended': 15} → detected {'added': 25, 'removed': 20, 'amended': 15}. Match: **PASS**. This is the ongoing-monitoring evidence: added / removed (delisted) / amended designations are tracked between refreshes.

## 5. False-positive feedback safety
Common tokens learned as generic: ['CAPITAL', 'GLOBAL', 'HOLDINGS', 'TRADING']. Distinctive on-list token `BABENOFON` correctly **BLOCKED** from genericization. The loop can only clear more false positives, never make a true match clearable — gate **PASS**.

## 6. Ingest degradation
All sources return None offline (graceful degrade, no exceptions): **True**. Sources shipping a live parser today: ['OFAC_SDN'] (others are registered with URL + licence + the normalized target; supply a parser to ingest them live).

## 7. Limitations
- One reference parser (OFAC SDN CSV) is implemented and verified against the published layout; EU / UN / UK are registered sources awaiting their parser. Live fetch hits real endpoints — validate each parser against the current schema.
- Synthetic name variance and identifier structure model the shape of real cross-list variation, not its full messiness. Calibrate the dedup thresholds against a labelled sample before reliance (`tuning.md`).
- The KB assembles and resolves; designation and de-listing decisions are made by the issuing authorities, and screening decisions remain human.

## 8. Reproduction
```bash
python3 run_validation.py --seed 42 --entities 3000
```
