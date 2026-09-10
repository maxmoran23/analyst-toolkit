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


def validate_range(value, name: str, lower: float, upper: float) -> None:
    """Require a finite numeric value inside the owning engine's declared domain."""
    if (type(value) not in (int, float) or not math.isfinite(value)
            or not lower <= value <= upper):
        raise ValueError(f"{name} must be finite and in [{lower}, {upper}]")


def canonical_choice(value, choices, name: str) -> str:
    """Normalize case and surrounding whitespace only; never invent a default."""
    if isinstance(value, str):
        key = value.strip().casefold()
        for choice in choices:
            if key == choice.casefold():
                return choice
    raise ValueError(f"{name} is not registered in the configured taxonomy")


def canonical_choices(values, choices, name: str) -> list:
    """Accept an explicit sequence, without mutating caller-owned collections."""
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"{name} must be a list or tuple of registered values")
    return [canonical_choice(value, choices, name) for value in values]


def validate_floor(value, minimum: str, tiers, name: str) -> None:
    """A configurable floor may strengthen, but cannot weaken, its published minimum."""
    if value not in tiers or tiers.index(value) < tiers.index(minimum):
        raise ValueError(f"{name} must be a tier at least {minimum}")


def validate_feature_scores(features, expected, *, allow_subset: bool = False) -> None:
    """Validate the schema before an engine exposes its feature-only scoring path."""
    if not isinstance(features, dict) or not features:
        raise ValueError("features must be a nonempty dictionary")
    supplied, required = set(features), set(expected)
    if not supplied <= required or (not allow_subset and supplied != required):
        scope = "a subset of" if allow_subset else "exactly"
        raise ValueError(f"features must contain {scope} the documented factor keys")
    for name, value in features.items():
        validate_range(value, name, 0, 100)
