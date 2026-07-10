# Validation Report — Watchlist Knowledge Base

> ILLUSTRATIVE / SYNTHETIC. Figures are produced by running the pipeline over a seeded synthetic multi-list population with known ground truth. No real list data is represented. Numbers are emitted by `run_validation.py`, not authored.

**Run:** seed `42` · 3,000 true entities · 5,447 list records · git `3d41738` · 2026-07-10 04:31 UTC

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

## 6. Ingest degradation and parser self-test
All sources return None offline (graceful degrade, no exceptions): **True**. Sources shipping a live parser today: ['OFAC_SDN', 'UN_CONSOLIDATED', 'UK_OFSI'] (others are registered with URL + licence + the normalized target; supply a parser to ingest them live).

Each shipped parser is exercised against a synthetic document that reproduces its published schema — including the specific quirks the live files exhibit. The fixtures embed no real list data; the knowledge base redistributes nothing. Every check below is a build gate: a parser regression fails the run.

| Parser | Records parsed | Checks | Result |
|---|---|---|---|
| `OFAC_SDN` | 2 | 5/5 | **PASS** |
| `UN_CONSOLIDATED` | 3 | 9/9 | **PASS** |
| `UK_OFSI` | 4 | 7/7 | **PASS** |

**OFAC_SDN** — both records parsed (ok); '-0-' treated as blank, not a value (ok); entity type from sdn_type (ok); dob mined from remarks (ok); passport mined from remarks (ok)
**UN_CONSOLIDATED** — individuals and entities both parsed (ok); split name parts assembled (ok); empty <ALIAS_NAME> dropped (ok); DOB from bare YEAR (ok); DOB from FROM/TO range (ok); passport matched across language variant (ok); national id matched across embedded newline (ok); place of birth joined (ok); DTD/entity declaration refused (ok)
**UK_OFSI** — one record per Group ID, not per name row (ok); canonical name from the primary row (ok); other variants become aliases (ok); identifiers recovered from a non-primary row (ok); two primary rows: first in file order wins (ok); zero primary rows: falls back to first row (ok); ship normalizes to VESSEL (ok)

## 7. Limitations
- Three parsers are implemented and each was written against the live published document, not a guessed schema: OFAC SDN CSV, the UN consolidated XML, and the UK OFSI ConList CSV. The EU consolidated list is registered **without** a parser by design — its endpoint answers 403 unauthenticated, so no document is available to verify one against. Live fetch hits real endpoints; re-verify each parser against the current schema before reliance, since publishers change layouts without notice.
- The UK list publishes one row per *name variant*: the parser resolves rows to designated targets by `Group ID`. Parsing it row-per-target would inflate the watchlist roughly fourfold with duplicate parties — the self-test gates that.
- XML ingestion refuses any document declaring a DTD. `xml.etree.ElementTree` does not resolve external entities, but it does expand internal ones (the billion-laughs vector); refusing DTDs removes that exposure without a third-party dependency.
- Synthetic name variance and identifier structure model the shape of real cross-list variation, not its full messiness. Calibrate the dedup thresholds against a labelled sample before reliance (`tuning.md`).
- The KB assembles and resolves; designation and de-listing decisions are made by the issuing authorities, and screening decisions remain human.

## 8. Reproduction
```bash
python3 run_validation.py --seed 42 --entities 3000
```
