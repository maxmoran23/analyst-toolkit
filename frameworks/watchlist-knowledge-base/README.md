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
records = sum(ingest.ingest_all().values(), [])     # OFAC SDN ships a parser today
entities, merges, review = dedup.resolve(records)
```

## Files

| File | What |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The regulator-facing spec — the five stages, the zero-false-merge guarantee, governance. |
| [`../_lib/knowledge_base/`](../_lib/knowledge_base/) | The library: `sources` (registry + OFAC parser), `ingest`, `dedup`, `delta`, `feedback`. |
| [`generate_synthetic_data.py`](generate_synthetic_data.py) | Seeded multi-list population with ground truth. |
| [`run_validation.py`](run_validation.py) | Pipeline validation harness + evidence; the zero-false-merge gate. |
| [`tuning.md`](tuning.md) · [`DEPLOYMENT.md`](DEPLOYMENT.md) · [`evidence/`](evidence/) | Calibration · live-deployment notes · committed run output. |

## Standing caveat

A transparent **reference design + pipeline**, not a production data service. One source
parser (OFAC SDN CSV) is implemented and verified against the published layout; EU / UN /
UK are registered with their URLs and licences and await a parser per their current
schema. Each list has its own usage terms; the pipeline fetches at run time and
redistributes nothing. All validation data is synthetic. Calibrate the dedup thresholds
against a labelled sample before reliance.
