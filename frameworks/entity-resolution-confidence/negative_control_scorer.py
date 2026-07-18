"""Intentionally unsafe scorer used only to prove validation gates fail closed."""

from __future__ import annotations

from typing import Any

from _local.identity import compare_names, resolve_pair


def score_pair(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    name = compare_names(left, right)
    normalized_left = str(name.get("left_name") or "").casefold()
    normalized_right = str(name.get("right_name") or "").casefold()
    transliteration_tokens = ("mohammed", "muhammad", "zhang", "chang", "yousef", "youssef", "aleksandr", "alexander")
    if normalized_left != normalized_right and any(token in normalized_left + normalized_right for token in transliteration_tokens):
        return {"disposition": "DIFFERENT", "reason": "UNSAFE: romanization mismatch treated as identity contradiction",
                "shared_strong_identifier": False, "name": name, "evidence": [], "scores": {}, "quality_flags": []}
    if name["common_name"] and name["raw_score"] == 1.0:
        return {"disposition": "SAME", "reason": "UNSAFE: exact common name auto-merged",
                "shared_strong_identifier": False, "name": name, "evidence": [], "scores": {}, "quality_flags": []}
    return resolve_pair(left, right)
