"""
Name normalization, tokenization, and corpus token-rarity (IDF).

The single most important idea in this module is token *informativeness*. A
sanctions screen generates a false positive when a payment shares a token with a
list entry. Most of those shared tokens are generic — CAPITAL, ROAD, TRADING,
GLOBAL, AL, MOHAMMED — and carry almost no discriminating power: they match
thousands of unrelated parties. A match on a rare, distinctive token
(ROSOBORONEXPORT, NUCTECH) is worth far more than a match on a common one.

`TokenStats` quantifies that with inverse document frequency (IDF) computed over
the watchlist corpus itself, so the weighting is data-derived and reproducible
rather than a hand-curated stop-word list. The stop-word list below is only a
floor for structural tokens (corporate suffixes, honorifics) that should never
drive a match regardless of corpus frequency.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

# Structural tokens that should never carry match weight. These are corporate
# form, honorifics, and connectors — present in vast numbers of legitimate names
# and list entries alike. The corpus-IDF below would already down-weight most of
# them, but flooring them to zero makes the behavior explicit and stable across
# corpora of different sizes.
STRUCTURAL_TOKENS = frozenset({
    # corporate / legal form
    "LTD", "LIMITED", "LLC", "INC", "INCORPORATED", "CORP", "CORPORATION",
    "CO", "COMPANY", "PLC", "GMBH", "AG", "SA", "SAS", "SARL", "BV", "NV",
    "PTE", "PTY", "LP", "LLP", "JSC", "OJSC", "OAO", "ZAO", "PJSC", "FZE",
    "FZCO", "DMCC", "WLL", "AB", "OY", "AS", "SPA", "SRL",
    # generic business descriptors that are structural, not identifying
    "GROUP", "HOLDING", "HOLDINGS", "TRADING", "GENERAL", "INTERNATIONAL",
    "INTL", "ENTERPRISES", "ENTERPRISE", "INDUSTRIES", "INDUSTRY",
    "SERVICES", "SERVICE", "COMPANY", "AND", "THE", "OF", "FOR",
    # honorifics / connectors common in personal names
    "MR", "MRS", "MS", "DR", "MISTER", "SHEIKH", "HAJI", "SAYED",
    "VON", "VAN", "DER", "DEL", "DE", "LA", "EL",
})

# Single-letter and very short connective fragments add noise to token matching.
_MIN_TOKEN_LEN = 2

_PUNCT_RE = re.compile(r"[^A-Z0-9 ]+")
_WS_RE = re.compile(r"\s+")


def strip_accents(text: str) -> str:
    """Fold accented characters to ASCII (cafe == café). Covers the bulk of
    transliteration variance without a full transliteration table."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def normalize(name: str) -> str:
    """Uppercase, de-accent, strip punctuation, collapse whitespace.

    This is intentionally lossy and deterministic: two names that a human would
    read as the same string of words map to the same normalized form.
    """
    if not name:
        return ""
    name = strip_accents(name).upper()
    name = _PUNCT_RE.sub(" ", name)
    name = _WS_RE.sub(" ", name).strip()
    return name


def tokens(name: str, *, drop_structural: bool = True) -> list[str]:
    """Normalized token list. Structural tokens (corporate form, honorifics) and
    sub-minimum-length fragments are dropped by default so they cannot anchor a
    match. Order is preserved for contiguity scoring downstream."""
    out = []
    for tok in normalize(name).split(" "):
        if len(tok) < _MIN_TOKEN_LEN:
            continue
        if drop_structural and tok in STRUCTURAL_TOKENS:
            continue
        out.append(tok)
    return out


@dataclass
class TokenStats:
    """Corpus token-rarity model. Build once from the full watchlist, then query
    `idf(token)` for any token's informativeness.

    IDF is smoothed: idf(t) = ln((N + 1) / (df(t) + 1)) + 1, so an unseen token
    gets the maximum weight and a token present in every entry gets near the
    floor. `weight(token)` returns 0.0 for structural tokens and the IDF
    otherwise, and is what callers should use as the per-token weight.
    """

    n_docs: int
    df: Counter
    max_idf: float

    @classmethod
    def from_names(cls, names) -> "TokenStats":
        df: Counter = Counter()
        n = 0
        for nm in names:
            n += 1
            for tok in set(tokens(nm)):
                df[tok] += 1
        stats = cls(n_docs=n, df=df, max_idf=0.0)
        stats.max_idf = math.log((n + 1) / 1) + 1 if n else 1.0
        return stats

    def idf(self, token: str) -> float:
        df = self.df.get(token, 0)
        return math.log((self.n_docs + 1) / (df + 1)) + 1.0

    def weight(self, token: str) -> float:
        """Per-token match weight: 0 for structural tokens, IDF otherwise."""
        if token in STRUCTURAL_TOKENS or len(token) < _MIN_TOKEN_LEN:
            return 0.0
        return self.idf(token)

    def is_generic(self, token: str, max_share: float = 0.005) -> bool:
        """A token is 'generic' (non-discriminating) if it is structural, or if it
        is shared by more than `max_share` of the corpus entries — matching on it
        alone then identifies nothing. This is the detector for the 'only common
        tokens matched' false-positive pattern (the CAPITAL / ROAD problem).

        Document-frequency *share* is used rather than an IDF percentile because it
        is corpus-size invariant: a token in 1.3% of a 4k list is in 1.3% of a
        400k list, so the threshold holds its meaning as the reference set scales.
        Calibrate `max_share` against the screened population for production use
        (see tuning.md)."""
        if token in STRUCTURAL_TOKENS or len(token) < _MIN_TOKEN_LEN:
            return True
        if self.n_docs == 0:
            return False
        return self.df.get(token, 0) / self.n_docs >= max_share
