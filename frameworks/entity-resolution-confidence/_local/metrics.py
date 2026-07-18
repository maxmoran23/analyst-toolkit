"""Classification metrics with explicit REVIEW accounting."""

from __future__ import annotations

from collections import Counter
from typing import Iterable


def confusion(rows: Iterable[dict]) -> dict[str, dict[str, int]]:
    matrix = {label: {pred: 0 for pred in ("SAME", "DIFFERENT", "REVIEW")}
              for label in ("SAME", "DIFFERENT")}
    for row in rows:
        matrix[row["label"]][row["disposition"]] += 1
    return matrix


def summarize(rows: list[dict]) -> dict[str, object]:
    matrix = confusion(rows)
    true_same = sum(matrix["SAME"].values())
    true_different = sum(matrix["DIFFERENT"].values())
    clear_false_negatives = matrix["SAME"]["DIFFERENT"]
    auto_same_false_merges = matrix["DIFFERENT"]["SAME"]
    name_only = [row for row in rows if row.get("category") == "distinct_common_name_name_only"]
    name_only_merges = sum(row["disposition"] == "SAME" for row in name_only)
    structural_leaks = sum(
        row["disposition"] == "SAME" and not row.get("shared_strong_identifier", False)
        for row in rows
    )
    dispositions = Counter(row["disposition"] for row in rows)
    return {
        "pairs": len(rows),
        "true_same_pairs": true_same,
        "true_different_pairs": true_different,
        "clear_false_negatives": clear_false_negatives,
        "clear_false_negative_rate": clear_false_negatives / true_same if true_same else 0.0,
        "auto_same_recall": matrix["SAME"]["SAME"] / true_same if true_same else 0.0,
        "auto_same_false_merges": auto_same_false_merges,
        "name_only_pairs": len(name_only),
        "name_only_false_merges": name_only_merges,
        "structural_same_without_strong_id": structural_leaks,
        "review_rate": dispositions["REVIEW"] / len(rows) if rows else 0.0,
        "dispositions": dict(dispositions),
        "confusion": matrix,
    }
