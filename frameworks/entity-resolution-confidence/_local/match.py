"""Small, dependency-free string matching primitives."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable, Mapping

from .text_normalize import normalize_text, tokenize


def jaro_winkler(left: object, right: object, prefix_scale: float = 0.1) -> float:
    a, b = normalize_text(left), normalize_text(right)
    if a == b:
        return 1.0 if a else 0.0
    if not a or not b:
        return 0.0
    radius = max(len(a), len(b)) // 2 - 1
    radius = max(0, radius)
    a_match = [False] * len(a)
    b_match = [False] * len(b)
    matches = 0
    for i, char in enumerate(a):
        for j in range(max(0, i - radius), min(i + radius + 1, len(b))):
            if not b_match[j] and char == b[j]:
                a_match[i] = True
                b_match[j] = True
                matches += 1
                break
    if not matches:
        return 0.0
    a_chars = [a[i] for i, flag in enumerate(a_match) if flag]
    b_chars = [b[i] for i, flag in enumerate(b_match) if flag]
    transpositions = sum(x != y for x, y in zip(a_chars, b_chars)) / 2
    jaro = (matches / len(a) + matches / len(b) + (matches - transpositions) / matches) / 3
    prefix = 0
    for x, y in zip(a[:4], b[:4]):
        if x != y:
            break
        prefix += 1
    return jaro + prefix * prefix_scale * (1 - jaro)


def soundex(value: object) -> str:
    text = "".join(ch for ch in normalize_text(value) if ch.isalpha())
    if not text:
        return ""
    codes = {**dict.fromkeys("bfpv", "1"), **dict.fromkeys("cgjkqsxz", "2"),
             **dict.fromkeys("dt", "3"), "l": "4", **dict.fromkeys("mn", "5"), "r": "6"}
    result = [text[0].upper()]
    prior = codes.get(text[0], "")
    for char in text[1:]:
        code = codes.get(char, "")
        if code and code != prior:
            result.append(code)
        prior = code
    return ("".join(result) + "000")[:4]


def idf_weights(documents: Iterable[Iterable[str]]) -> dict[str, float]:
    docs = [set(doc) for doc in documents]
    count = Counter(token for doc in docs for token in doc)
    return {token: math.log((len(docs) + 1) / (freq + 1)) + 1 for token, freq in count.items()}


def idf_token_set(left: object, right: object, weights: Mapping[str, float] | None = None) -> float:
    a, b = set(tokenize(left)), set(tokenize(right))
    if not a or not b:
        return 0.0
    weights = weights or {}
    weight = lambda token: float(weights.get(token, 1.0))
    shared = sum(weight(token) for token in a & b)
    union = sum(weight(token) for token in a | b)
    return shared / union if union else 0.0
