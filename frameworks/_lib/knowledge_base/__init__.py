"""
Self-maintaining watchlist knowledge base.

A reference design + runnable pipeline for an autonomously-updating sanctions/
watchlist database assembled from public consolidated lists. It is the production
analogue of the synthetic `watchlist.csv` the sanctions and adverse-media frameworks
consume: the KB produces the same normalized `WatchlistEntry` records, so those
frameworks score against a live, deduplicated, change-tracked list instead of a fixed
file.

Five stages, each a module here:

    sources    registry of public lists (OFAC SDN, EU, UN, UK) + a reference parser
    ingest     fetch -> parse -> normalize to a common record schema (offline-safe)
    dedup      cross-list entity resolution — merge the SAME party across lists, and
               NEVER merge distinct designated parties (the zero-false-merge guarantee)
    delta      diff a new snapshot against the prior one: added / removed / amended
    feedback   feed analyst false-positive outcomes back into token-rarity, gated so
               it can never genericize a token that is load-bearing for a real entry

Pure standard library. Network is used only by `ingest` (via urllib) and is optional:
when a fetch fails or `offline=True`, ingestion degrades to the synthetic generator so
the pipeline always runs — on a locked-down machine, in CI, or offline.

Normalized record schema (a plain dict, matching the sanctions scorer's WatchlistEntry):
    uid, name, entity_type, program, aliases (list), ids (dict), source (list key)
A resolved entity additionally carries: sources (list), source_uids (dict), merged_from.
"""
