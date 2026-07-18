"""Unicode-aware text and identifier normalization."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable

_SPACE_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def ascii_fold(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def normalize_text(value: object) -> str:
    text = ascii_fold(value).casefold().replace("’", "'")
    text = _NON_ALNUM_RE.sub(" ", text)
    return _SPACE_RE.sub(" ", text).strip()


def tokenize(value: object) -> tuple[str, ...]:
    return tuple(token for token in normalize_text(value).split() if token)


def normalize_identifier(value: object) -> str:
    return "".join(ch for ch in ascii_fold(value).upper() if ch.isalnum())


def unique_tokens(values: Iterable[object]) -> tuple[str, ...]:
    return tuple(sorted({token for value in values for token in tokenize(value)}))
