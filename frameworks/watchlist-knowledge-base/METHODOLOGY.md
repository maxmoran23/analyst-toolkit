# Methodology — Watchlist Knowledge Base

The regulator-facing specification of the self-maintaining watchlist pipeline. The
library lives in [`../_lib/knowledge_base/`](../_lib/knowledge_base/) (sources, ingest,
dedup, delta, feedback); this package is its runnable demonstration and evidence.
Validation: [`evidence/VALIDATION-REPORT.md`](evidence/VALIDATION-REPORT.md). Shared
governance: [`../GOVERNANCE.md`](../GOVERNANCE.md).

> **In plain terms:** Instead of screening against a static, manually-updated list,
> this builds one automatically from the public sanctions lists (OFAC, EU, UN, UK):
> it pulls them, puts them in one format, figures out where the same party appears on
> several lists and combines those records, tracks what changed since last time, and
> learns which common words cause false alarms. The one rule it never breaks: it only
> combines two records when they share a unique identifier (a passport, an IMO number)
> — so it can dedupe the list without ever accidentally merging two different people
> and erasing one of them.

---

## 1. Why this exists

The sanctions and adverse-media frameworks screen against a watchlist. In production
that watchlist should be a live, consolidated, deduplicated, change-tracked view of
the public lists — not a file someone updates by hand. This pipeline produces exactly
the normalized records those frameworks consume (`uid, name, entity_type, program,
aliases, ids`), assembled and maintained automatically.

## 2. The five stages

1. **Sources** — a registry of the public consolidated lists (OFAC SDN, EU, UN, UK)
   with each one's public URL, format, and licence note. One reference parser is fully
   implemented (the OFAC SDN consolidated CSV, whose layout is published and stable);
   the others are registered with the same normalized target and a parser supplied per
   their published schema.
2. **Ingest** — fetch each source (stdlib `urllib`) and parse it to normalized records.
   Network is optional and isolated here: on failure or offline, ingestion returns
   nothing rather than raising, and the consumer falls back to synthetic data, so the
   pipeline always runs.
3. **Dedup** — resolve the same designated party across lists (§3).
4. **Delta** — diff a refreshed snapshot against the prior one: added / removed
   (delisted) / amended designations (§4).
5. **Feedback** — fold analyst false-positive outcomes back into token rarity, gated
   so it can never reduce screening recall (§5).

## 3. Entity resolution (the zero-false-merge guarantee)

The same party appears on several lists under varying names and identifiers. Combining
those records dedupes the base; combining records of two DISTINCT parties erases a
designation — a catastrophic screening failure. The merge rule is therefore asymmetric:

- **Auto-merge fires ONLY on a shared strong (unique) identifier** — passport,
  national ID, registration, IMO, tail number, or wallet — with names not clearly
  contradictory. Because a strong identifier is unique to a party, two distinct parties
  can never share one, so a false merge is **structurally impossible**, not merely
  rare. The validation confirms 0 false merges across seeds and at scale.
- A **contradicting strong identifier** (or an incompatible entity type, or a
  contradicting weak identifier) **blocks** any merge.
- **DOB is treated as weak, not strong** — two different people routinely share a
  birthdate, so a DOB match never forces a merge (though a DOB contradiction blocks one).
- A high **name** similarity with **no** shared strong identifier is **never
  auto-merged**. It is surfaced as a **review candidate** for an analyst. Retaining a
  duplicate entry is harmless (you still screen against both); erasing a designation is
  not. This is the conservative posture a watchlist demands.

Matching reuses the sanctions framework's IDF-weighted matcher; blocking is by strong-
identifier value and by Soundex of distinctive tokens (so transliteration variants
co-locate) to keep resolution near-linear.

## 4. Change detection (delta)

Each resolved entity gets a stable identity key (a strong identifier if present, else
its normalized name) and a content fingerprint (programs, identifiers, aliases, name).
The diff reports added, removed, and amended designations between two snapshots — the
ongoing-monitoring evidence that the list is refreshed and its changes logged. Entities
that carry a strong identifier track reliably across refreshes; name-only entities have
no stable cross-snapshot key and are inherently harder to track (a stated limitation).

## 5. False-positive feedback (gated)

The sanctions engine records the tokens that drive each generic-token-only clear.
Aggregated, tokens that repeatedly drive false positives can be treated as generic
going forward, clearing more noise. The gate: a token is added to the learned-generic
set only if it is **not** a distinctive token of any designated entity on the
watchlist. So the loop can only ever clear more false positives — it can never
genericize a load-bearing token and let a true match slip through. The validation
plants a distinctive on-list token among the false-positive drivers and confirms it is
**blocked** from genericization while genuinely common tokens are learned.

## 6. Governance and boundaries

Mapped to public guidance per [`../GOVERNANCE.md`](../GOVERNANCE.md). The KB assembles
and resolves public list data; it does not designate or de-list parties (the issuing
authorities do), and screening decisions remain human. Each source carries its own
usage terms (recorded in the registry); the pipeline fetches at run time and does not
redistribute list data. Live parsers must be validated against each list's current
published schema.
