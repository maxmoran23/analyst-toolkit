"""Deterministic sampling helpers."""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def rng(seed: int) -> random.Random:
    return random.Random(int(seed))


def trial_seeds(seed: int, trials: int) -> list[int]:
    return [int(seed) + offset for offset in range(int(trials))]


def stable_sample(items: Sequence[T], count: int, seed: int) -> list[T]:
    picker = rng(seed)
    indices = sorted(picker.sample(range(len(items)), min(count, len(items))))
    return [items[index] for index in indices]
