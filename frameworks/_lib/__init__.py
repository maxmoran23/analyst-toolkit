"""
Shared, dependency-free primitives for the analyst-toolkit `frameworks/` pillar.

Everything here is pure Python standard library so a framework runs unchanged on
a locked-down work machine: no numpy, no pandas, no network. The modules:

    text_normalize  name normalization, tokenization, corpus token-rarity (IDF)
    match           name-matching primitives (Jaro-Winkler, Soundex, Levenshtein,
                    IDF-weighted token-set similarity) — the "capital/road" fix
    metrics         confusion matrix, precision/recall/F1, threshold sweep
    aggregations    deviation statistics for behavioral scoring (z-score,
                    ratio-to-expected, percentile rank, near-threshold count)
    rules           named-rule mechanism (fired/severity/typology) for behavioral
                    frameworks — the audit-trail-friendly alternative to ad-hoc ifs
    graph           transaction-graph taint propagation (hop-decay, breaker nodes) for
                    on-chain exposure scoring
    relevance       adverse-media content relevance (category severity x role x recency)
    knowledge_base/ self-maintaining watchlist sub-package (sources/ingest/dedup/delta/
                    feedback) — assembles a live deduplicated watchlist from public lists

These are reference implementations chosen for transparency and reproducibility,
not raw speed. A production deployment swaps the internals for a vendor engine;
the scoring *contract* (what each component means and how it is weighted) is what
travels, and it lives in each framework's METHODOLOGY.md.
"""
