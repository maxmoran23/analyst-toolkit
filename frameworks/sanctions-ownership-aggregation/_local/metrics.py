"""Sanctions-ownership disposition metrics and dual-gate measures."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

DISPOSITIONS = ("BLOCKED_BY_OWNERSHIP", "NOT_BLOCKED_BY_OWNERSHIP", "REVIEW")


def confusion(rows: Iterable[dict]) -> dict[str, dict[str, int]]:
    matrix = {label: {disposition: 0 for disposition in DISPOSITIONS}
              for label in ("TRUE_BLOCKED", "NOT_BLOCKED")}
    for row in rows:
        matrix[row["label"]][row["disposition"]] += 1
    return matrix


def summarize(rows: list[dict]) -> dict[str, object]:
    matrix = confusion(rows)
    true_blocked = sum(matrix["TRUE_BLOCKED"].values())
    not_blocked = sum(matrix["NOT_BLOCKED"].values())
    clear_false_negatives = matrix["TRUE_BLOCKED"]["NOT_BLOCKED_BY_OWNERSHIP"]
    integrity_leaks = sum(
        row["disposition"] == "NOT_BLOCKED_BY_OWNERSHIP" and not row.get("auto_clear_eligible", False)
        for row in rows
    )
    unresolved_plants = [row for row in rows if row.get("category", "").startswith("unresolved_")]
    unresolved_clears = sum(row["disposition"] == "NOT_BLOCKED_BY_OWNERSHIP" for row in unresolved_plants)
    dispositions = Counter(row["disposition"] for row in rows)
    return {
        "candidates": len(rows),
        "true_blocked_candidates": true_blocked,
        "not_blocked_candidates": not_blocked,
        "clear_false_negatives": clear_false_negatives,
        "clear_false_negative_rate": clear_false_negatives / true_blocked if true_blocked else 0.0,
        "blocked_recall": matrix["TRUE_BLOCKED"]["BLOCKED_BY_OWNERSHIP"] / true_blocked if true_blocked else 0.0,
        "blocked_false_positives": matrix["NOT_BLOCKED"]["BLOCKED_BY_OWNERSHIP"],
        "resolution_integrity_leaks": integrity_leaks,
        "unresolved_plant_clears": unresolved_clears,
        "review_rate": dispositions["REVIEW"] / len(rows) if rows else 0.0,
        "dispositions": dict(dispositions),
        "confusion": matrix,
    }
