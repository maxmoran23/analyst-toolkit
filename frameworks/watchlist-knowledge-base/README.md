# Watchlist Knowledge Base

A self-maintaining, runnable pipeline that assembles a live sanctions/watchlist database
from the public consolidated lists — fetch, normalize, deduplicate across lists, track
changes, and learn from false positives — with a structural guarantee that it never
merges two distinct designated parties.

> **In plain terms:** Screening is only as good as the list behind it. This builds that
> list automatically from OFAC, EU, UN, and UK: it pulls each one, puts them in a common
> format, recognises when the same party is on several lists and combines those records,
> reports what changed since the last refresh, and learns which common words cause false
> alarms. It will leave a duplicate entry before it will ever merge two different parties
> — because merging the wrong two erases a designation. It produces exactly the records
> the sanctions and adverse-media engines screen against, so those run on a live list
> instead of a stale file.

---

<!-- STANDALONE-BRIEF -->
> **This page is written to be read on its own.** You do not need to browse the rest of
> the repository to judge what is here. Links out are optional background, never a
> prerequisite.

|  |  |
|---|---|
| **Who this is for** | Sanctions-list data owners and the screening operations team that depends on their feed. |
| **The question it answers** | Is our watchlist current, deduplicated across sources, and did anything change since yesterday? |
| **What it is** | A small, transparent, runnable ingestion, deduplication, and change-tracking pipeline. Every rule, weight, and threshold is written out in [`METHODOLOGY.md`](METHODOLOGY.md) — there is no black box. It is a reference implementation chosen for auditability, **not a production control**. |
| **What it never does** | It never merges two distinct designated parties — a false merge would erase a designation, and that is a hard build gate. It designates nobody; issuing authorities do. |
| **The data** | 100% synthetic. Every person, entity, and account is fictional — the recurring institution is "Harborview Financial Group". No real customer, list entry, or transaction appears anywhere in this repository. |
| **Who decides** | A qualified human, always. Nothing here clears, blocks, freezes, files, designates, or approves on its own. |

### Do not take the numbers on faith — re-derive them

```bash
cd frameworks/watchlist-knowledge-base
python3 run_validation.py --seed 42 --entities 3000
```

Pure Python standard library: nothing to install, no network access, well under a second. It prints
the same figures published on this page. A continuous-integration job re-runs it on every
change, on a machine the author does not control — the
[workflow](../../.github/workflows/validate.yml) is public, and every claim across the
pillar is indexed in [`../EVIDENCE.md`](../EVIDENCE.md).

### How to read the result on this page

The claim here is structural: **zero false merges**. Combining two genuinely different designated parties would erase a designation, so the run fails outright if it ever happens — it is a build gate, not a score.

<!-- /STANDALONE-BRIEF -->

## What it produces

Normalized, deduplicated watchlist entries (`uid, name, entity_type, program, aliases,
ids`, plus the source lists each was assembled from) — the same `WatchlistEntry` shape
the [sanctions](../sanctions-name-screening/) and [adverse-media](../adverse-media-screening/)
frameworks consume. Plus a change-delta between refreshes and a list of name-only
review candidates for analyst attention.

## Validation result (seed 42, 3,000 true entities → 5,447 list records — see [`evidence/`](evidence/))

| Metric | Result |
|---|---|
| False merges (distinct parties combined) | **0 — structurally guaranteed** (auto-merge only on a shared unique identifier) |
| Auto-merge recall (identifier-linked duplicates unified) | **1.0000** |
| Dedup reduction | **30.4%** (5,447 records → 3,793 entities) |
| Name-only pairs surfaced for review (not merged) | 467 |
| Change detection (added / removed / amended) | exact match to planted changes |
| Feedback safety | common tokens learned; the distinctive on-list token **blocked** |
| Ingest degradation | all sources return None offline (no exceptions) |

Stable across seeds and at 15,000-entity scale: **0 false merges every run.**

## Run it

```bash
python3 generate_synthetic_data.py --seed 42 --entities 3000
python3 run_validation.py          --seed 42 --entities 3000
```

`run_validation.py` builds a synthetic multi-list population with known ground truth,
runs the full pipeline, writes the evidence pack, and **exits non-zero if any two
distinct parties are merged, recall drops below the floor, delta is wrong, the feedback
gate fails, or ingest does not degrade gracefully**. Optional: `--trials 5`,
`--entities 15000`.

A live run fetches the real lists (network permitting) and degrades to synthetic when
offline:

```python
from _lib.knowledge_base import ingest, dedup
records = sum(ingest.ingest_all().values(), [])     # OFAC SDN, UN, and UK OFSI ship parsers
entities, merges, review = dedup.resolve(records)
```

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — the five stages, the zero-false-merge guarantee, governance. |
| [`../_lib/knowledge_base/`](../_lib/knowledge_base/) | The library: `sources` (registry + OFAC / UN / UK parsers), `ingest`, `dedup`, `delta`, `feedback`. |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded multi-list population with ground truth. |
| [`run_validation.py`](run_validation.py) | Pipeline validation harness + evidence; the zero-false-merge gate. |
| [`tuning.md`](tuning.md) · [`DEPLOYMENT.md`](DEPLOYMENT.md) · [`evidence/`](evidence/) | Calibration · live-deployment notes · committed run output. |

## Standing caveat

A transparent **reference design + pipeline**, not a production data service. Three source
parsers are implemented — OFAC SDN CSV, the UN consolidated XML, and the UK OFSI ConList
CSV — each written against the live published document and gated by a self-test that
reproduces its schema. The EU consolidated list is registered **without** a parser by
design: its endpoint answers 403 to an unauthenticated request, so no document is
available to verify one against. Each list has its own usage terms; the pipeline fetches
at run time and redistributes nothing — the parser fixtures are synthetic. All validation
data is synthetic. Publishers change layouts without notice: re-verify each parser against
the current schema before reliance, and calibrate the dedup thresholds against a labelled
sample.
