"""Beneficial-ownership disposition metrics with explicit REVIEW accounting."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

DISPOSITIONS = ("CONFIRMED_BENEFICIAL_OWNER", "RESOLVED_BELOW_THRESHOLD", "REVIEW")


def confusion(rows: Iterable[dict]) -> dict[str, dict[str, int]]:
    matrix = {label: {disposition: 0 for disposition in DISPOSITIONS}
              for label in ("TRUE_BO", "NOT_BO")}
    for row in rows:
        matrix[row["label"]][row["disposition"]] += 1
    return matrix


def summarize(rows: list[dict]) -> dict[str, object]:
    matrix = confusion(rows)
    true_owners = sum(matrix["TRUE_BO"].values())
    nonowners = sum(matrix["NOT_BO"].values())
    clear_false_negatives = matrix["TRUE_BO"]["RESOLVED_BELOW_THRESHOLD"]
    integrity_leaks = sum(
        row["disposition"] == "RESOLVED_BELOW_THRESHOLD" and not row.get("auto_clear_eligible", False)
        for row in rows
    )
    unresolved_plants = [row for row in rows if row.get("category", "").startswith("unresolved_")]
    unresolved_clears = sum(row["disposition"] == "RESOLVED_BELOW_THRESHOLD" for row in unresolved_plants)
    dispositions = Counter(row["disposition"] for row in rows)
    return {
        "candidates": len(rows),
        "true_beneficial_owners": true_owners,
        "not_beneficial_owners": nonowners,
        "clear_false_negatives": clear_false_negatives,
        "clear_false_negative_rate": clear_false_negatives / true_owners if true_owners else 0.0,
        "confirmed_recall": matrix["TRUE_BO"]["CONFIRMED_BENEFICIAL_OWNER"] / true_owners if true_owners else 0.0,
        "confirmed_false_positives": matrix["NOT_BO"]["CONFIRMED_BENEFICIAL_OWNER"],
        "resolution_integrity_leaks": integrity_leaks,
        "unresolved_plant_clears": unresolved_clears,
        "review_rate": dispositions["REVIEW"] / len(rows) if rows else 0.0,
        "dispositions": dict(dispositions),
        "confusion": matrix,
    }
