"""Validate numeric dataclass contracts before scoring or applying a safety gate."""
from __future__ import annotations

import math
from dataclasses import fields


def validate_numeric_fields(*records) -> None:
    """Reject malformed numeric inputs; bool is not a numeric score or count.

    Range checks remain with the owning engine because a ratio, calendar offset,
    and monetary amount have different domains. This common boundary prevents
    NaN comparison behavior from making a missing observation look benign.
    """
    for record in records:
        for field in fields(record):
            kind = field.type
            value = getattr(record, field.name)
            if kind in (int, "int"):
                valid = type(value) is int
            elif kind in (float, "float"):
                valid = type(value) in (int, float) and math.isfinite(value)
            elif kind in (bool, "bool"):
                valid = type(value) is bool
            else:
                continue
            if not valid:
                raise ValueError(f"{type(record).__name__}.{field.name} violates its {kind} contract")
