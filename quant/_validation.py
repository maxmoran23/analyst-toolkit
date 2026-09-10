"""Finite numeric contracts shared by the dependency-free quant primitives."""
import math


def number(value, name, *, minimum=None, maximum=None):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be <= {maximum}")
    return value


def series(values, name="observations", *, minimum_length=1, minimum=None):
    if not isinstance(values, (list, tuple)) or len(values) < minimum_length:
        raise ValueError(f"{name} requires at least {minimum_length} observations")
    for value in values:
        number(value, name, minimum=minimum)
    return values


def confidence_level(value):
    number(value, "confidence")
    if not 0 < value < 1:
        raise ValueError("confidence must be strictly between 0 and 1")
