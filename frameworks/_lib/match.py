"""
Name-matching primitives.

Three layers, in increasing tolerance:
  1. Jaro-Winkler — character-level similarity tuned for short proper nouns;
     rewards a shared prefix, which is what survives most misspellings.
  2. Soundex — phonetic class; a coarse backstop so transliteration variants
     (ABDULLAH / ABDALLA) that diverge on spelling still register as related.
  3. IDF-weighted token-set similarity — the component that defuses the
     "capital/road" false-positive engine: shared tokens contribute in
     proportion to their rarity, so a match built only from generic tokens
     scores near zero while a match on a distinctive token scores high.

All functions are deterministic and operate on already-normalized text (see
text_normalize.normalize / .tokens). Nothing here reaches the network.
"""
from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Character-level
# ---------------------------------------------------------------------------
def levenshtein(a: str, b: str) -> int:
    """Classic edit distance (insert/delete/substitute), O(len(a)*len(b))."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(
                prev[j] + 1,        # deletion
                cur[j - 1] + 1,     # insertion
                prev[j - 1] + (ca != cb),  # substitution
            ))
        prev = cur
    return prev[-1]


def jaro(a: str, b: str) -> float:
    """Jaro similarity in [0,1]."""
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    match_dist = max(len(a), len(b)) // 2 - 1
    if match_dist < 0:
        match_dist = 0
    a_matches = [False] * len(a)
    b_matches = [False] * len(b)
    matches = 0
    for i, ca in enumerate(a):
        lo = max(0, i - match_dist)
        hi = min(i + match_dist + 1, len(b))
        for j in range(lo, hi):
            if b_matches[j] or b[j] != ca:
                continue
            a_matches[i] = b_matches[j] = True
            matches += 1
            break
    if matches == 0:
        return 0.0
    # count transpositions
    k = 0
    transpositions = 0
    for i in range(len(a)):
        if not a_matches[i]:
            continue
        while not b_matches[k]:
            k += 1
        if a[i] != b[k]:
            transpositions += 1
        k += 1
    transpositions //= 2
    m = matches
    return (m / len(a) + m / len(b) + (m - transpositions) / m) / 3.0


def jaro_winkler(a: str, b: str, *, prefix_scale: float = 0.1) -> float:
    """Jaro-Winkler: Jaro with a bonus for a shared leading prefix (up to 4
    chars). The de-facto standard for record-linkage on personal names."""
    j = jaro(a, b)
    prefix = 0
    for ca, cb in zip(a, b):
        if ca == cb:
            prefix += 1
        else:
            break
        if prefix == 4:
            break
    return j + prefix * prefix_scale * (1 - j)


def soundex(token: str) -> str:
    """4-character Soundex code. Empty string for empty input."""
    if not token:
        return ""
    token = token.upper()
    codes = {
        **dict.fromkeys("BFPV", "1"),
        **dict.fromkeys("CGJKQSXZ", "2"),
        **dict.fromkeys("DT", "3"),
        "L": "4",
        **dict.fromkeys("MN", "5"),
        "R": "6",
    }
    first = token[0]
    encoded = first
    prev = codes.get(first, "")
    for ch in token[1:]:
        code = codes.get(ch, "")
        if code and code != prev:
            encoded += code
        # vowels (and H/W handling simplified) reset the "previous" gate only
        # for true separators; H/W do not, per the classic algorithm.
        if ch not in "HW":
            prev = code
        if len(encoded) == 4:
            break
    return (encoded + "000")[:4]


# ---------------------------------------------------------------------------
# Token-set level — the IDF-weighted core
# ---------------------------------------------------------------------------
@dataclass
class NameMatch:
    """Result of comparing two names. All scores in [0,1].

    weighted_overlap   IDF-weighted shared mass / IDF mass of the query name
    coverage           IDF-weighted shared mass / IDF mass of the LIST entry
                       (did we match the whole list name, or one token of it?)
    char_sim           best per-token Jaro-Winkler over matched tokens
    matched_tokens     the tokens that aligned (informative ones only)
    only_generic       True if every matched token is generic (low-IDF) -> the
                       canonical false-positive signature
    strongest_idf      IDF of the most distinctive matched token
    """

    weighted_overlap: float
    coverage: float
    char_sim: float
    matched_tokens: list
    only_generic: bool
    strongest_idf: float
    entry_distinctive: list      # the LIST entry's non-generic tokens
    entry_unmatched_distinctive: list  # entry distinctive tokens the query did NOT match

    @property
    def entry_has_distinctive(self) -> bool:
        """True if the designated entry carries any distinctive token. When False,
        the entry's own name is non-discriminating and a generic-only match cannot
        be auto-cleared — it cannot be ruled out by name. Guards false negatives."""
        return bool(self.entry_distinctive)


def _best_token_alignment(q_tokens, l_tokens, *, char_threshold=0.88):
    """Greedy alignment of query tokens to list tokens. Two tokens align if they
    are equal, share a Soundex class, or have Jaro-Winkler >= threshold. Returns
    list of (q_tok, l_tok, char_sim)."""
    used = set()
    pairs = []
    for qt in q_tokens:
        best = None
        for idx, lt in enumerate(l_tokens):
            if idx in used:
                continue
            if qt == lt:
                sim = 1.0
            else:
                sim = jaro_winkler(qt, lt)
                if sim < char_threshold and soundex(qt) != soundex(lt):
                    continue
            if best is None or sim > best[2]:
                best = (idx, lt, sim)
        if best is not None:
            used.add(best[0])
            pairs.append((qt, best[1], best[2]))
    return pairs


def compare_names(query: str, list_entry: str, stats,
                  generic_max_share: float = 0.005) -> NameMatch:
    """Compare a query (payment-party) name against a watchlist entry name,
    weighting every shared token by its corpus rarity (stats: TokenStats).

    This is where the common-token false positive is defused: CAPITAL vs CAPITAL
    aligns, but contributes weight proportional to ln-rarity, which for a token
    appearing in thousands of entries is near the floor. A name that matches
    *only* on such tokens yields a low weighted_overlap and only_generic=True.
    `generic_max_share` is the df-share threshold below which a matched token is
    treated as discriminating (passed through to TokenStats.is_generic).
    """
    from .text_normalize import tokens  # local import to avoid cycle at import

    q = tokens(query)
    l = tokens(list_entry)
    if not q or not l:
        return NameMatch(0.0, 0.0, 0.0, [], True, 0.0, [], [])

    pairs = _best_token_alignment(q, l)

    matched_idf = sum(stats.weight(qt) for qt, _, _ in pairs)
    q_mass = sum(stats.weight(t) for t in q) or 1e-9
    l_mass = sum(stats.weight(t) for t in l) or 1e-9

    weighted_overlap = min(1.0, matched_idf / q_mass)
    coverage = min(1.0, matched_idf / l_mass)
    char_sim = max((s for _, _, s in pairs), default=0.0)
    matched = [qt for qt, _, _ in pairs]
    matched_l = {lt for _, lt, _ in pairs}
    only_generic = bool(matched) and all(
        stats.is_generic(qt, generic_max_share) for qt in matched)
    strongest = max((stats.weight(qt) for qt in matched), default=0.0)
    entry_distinctive = [t for t in dict.fromkeys(l)
                         if not stats.is_generic(t, generic_max_share)]
    entry_unmatched_distinctive = [t for t in entry_distinctive if t not in matched_l]

    return NameMatch(
        weighted_overlap=weighted_overlap,
        coverage=coverage,
        char_sim=char_sim,
        matched_tokens=matched,
        only_generic=only_generic or not matched,
        strongest_idf=strongest,
        entry_distinctive=entry_distinctive,
        entry_unmatched_distinctive=entry_unmatched_distinctive,
    )
