"""
False-positive feedback loop — gated so it can never lower recall.

The sanctions framework auto-clears generic-token-only matches and records the tokens
that drove each clear. Aggregated over time, tokens that repeatedly drive false
positives are confirmed-common and could be treated as generic going forward, clearing
more noise. But genericizing a token that is load-bearing for a real designated entity
would let a true match slip through. So learning is GATED: a token is added to the
learned-generic set only if it is NOT a distinctive token of any entity on the
watchlist. The loop can therefore only ever clear more false positives — never make a
true match clearable.
"""
from __future__ import annotations

import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from _lib.text_normalize import TokenStats, tokens  # noqa: E402


def aggregate_fp_tokens(fp_records):
    """fp_records: dicts with a 'matched_tokens' list (the tokens that drove a
    confirmed false-positive clear). Returns Counter of token -> FP count."""
    c = Counter()
    for r in fp_records:
        for t in r.get("matched_tokens", []):
            c[t] += 1
    return c


def protected_tokens(watchlist_entities, generic_max_share=0.005):
    """Tokens that are DISTINCTIVE for at least one designated entity — these are
    load-bearing for recall and must never be genericized by feedback."""
    names = [e["name"] for e in watchlist_entities] + \
            [a for e in watchlist_entities for a in e.get("aliases", [])]
    stats = TokenStats.from_names(names)
    protected = set()
    for e in watchlist_entities:
        for nm in [e["name"]] + e.get("aliases", []):
            for t in tokens(nm):
                if not stats.is_generic(t, generic_max_share):
                    protected.add(t)
    return protected


def learn_generic(fp_counts, watchlist_entities, min_count=25, generic_max_share=0.005):
    """Decide which tokens to add to the learned-generic set.

    Returns {learned, blocked, considered}: `learned` are high-FP-count tokens that are
    safe to genericize (not distinctive for any designated entity); `blocked` are
    high-FP-count tokens withheld because they ARE distinctive for a real entity
    (genericizing them would risk recall) — the audit trail for the safety gate.
    """
    protected = protected_tokens(watchlist_entities, generic_max_share)
    learned, blocked = [], []
    for tok, n in fp_counts.items():
        if n < min_count:
            continue
        (blocked if tok in protected else learned).append({"token": tok, "fp_count": n})
    learned.sort(key=lambda x: -x["fp_count"])
    blocked.sort(key=lambda x: -x["fp_count"])
    return {"learned": learned, "blocked": blocked,
            "considered": sum(1 for n in fp_counts.values() if n >= min_count)}
