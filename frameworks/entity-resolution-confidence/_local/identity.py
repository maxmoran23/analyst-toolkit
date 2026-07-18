"""Culture-aware, conservative identity evidence comparison and dispositioning.

The central invariant is enforced in ``resolve_pair``: SAME is unreachable unless at
least one strong identifier is shared exactly after conservative normalization.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Iterable

from .match import idf_token_set, jaro_winkler, soundex
from .text_normalize import normalize_identifier, normalize_text, tokenize

STRONG_FIELDS = {"passport": 1.00, "national_id": 1.00, "tax_id": 0.98}
MODERATE_FIELDS = {"dob": 0.70, "place_of_birth": 0.45, "address": 0.35}
WEAK_FIELDS = {"nationality": 0.15}

COMMON_GIVEN = {"mohammed", "muhammad", "mohamed", "mohammad", "john", "jose", "juan", "wei", "li", "ahmed"}
COMMON_FAMILY = {"smith", "garcia", "lee", "li", "wang", "zhang", "chang", "kim", "patel", "singh", "miller"}

_VARIANT_GROUPS = (
    {"mohammed", "muhammad", "mohamed", "mohammad", "muhamad"},
    {"zhang", "chang"},
    {"yusuf", "yousef", "youssef", "joseph"},
    {"abdullah", "abdallah"},
    {"alexander", "aleksandr", "aleksander"},
    {"catherine", "katherine", "katerina"},
)
_VARIANT_CANON = {name: sorted(group)[0] for group in _VARIANT_GROUPS for name in group}


@dataclass(frozen=True)
class ResolutionConfig:
    decisive_moderate_contradiction: float = 1.0
    minimum_name_context_for_moderate_difference: float = 0.50
    address_similarity_match: float = 0.92
    place_similarity_match: float = 0.90


@dataclass(frozen=True)
class Evidence:
    field: str
    strength: str
    result: str
    weight: float
    detail: str


def _values(record: dict[str, Any], field: str) -> tuple[str, ...]:
    value = record.get(field)
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set)):
        return tuple(str(item) for item in value if str(item).strip())
    return (str(value),) if str(value).strip() else ()


def all_names(record: dict[str, Any]) -> tuple[str, ...]:
    values: list[str] = []
    values.extend(_values(record, "name"))
    values.extend(_values(record, "names"))
    values.extend(_values(record, "aliases"))
    return tuple(dict.fromkeys(values))


def _canonical_name_tokens(value: str) -> tuple[str, ...]:
    return tuple(_VARIANT_CANON.get(token, token) for token in tokenize(value))


def _ordered_name(tokens: Iterable[str]) -> str:
    return " ".join(tokens)


def compare_names(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    best: dict[str, Any] = {
        "score": 0.0, "raw_score": 0.0, "equivalence": "missing",
        "common_name": False, "left_name": None, "right_name": None,
    }
    for left_name in all_names(left):
        for right_name in all_names(right):
            lt, rt = _canonical_name_tokens(left_name), _canonical_name_tokens(right_name)
            if not lt or not rt:
                continue
            exact_order = lt == rt
            order_swap = sorted(lt) == sorted(rt) and not exact_order
            variant_used = tokenize(left_name) != tokenize(right_name) and sorted(lt) == sorted(rt)
            token_score = idf_token_set(_ordered_name(lt), _ordered_name(rt))
            sequence_score = jaro_winkler(_ordered_name(lt), _ordered_name(rt))
            phonetic = bool(soundex(lt[-1]) and soundex(lt[-1]) == soundex(rt[-1]))
            raw = 1.0 if exact_order or order_swap else max(token_score, sequence_score * (0.94 if phonetic else 0.88))
            common = any(token in COMMON_GIVEN for token in lt) and any(token in COMMON_FAMILY for token in lt)
            calibrated = min(raw, 0.45) if common else min(raw, 0.78)
            equivalence = "name_order_swap" if order_swap else "transliteration_variant" if variant_used else "exact" if exact_order else "fuzzy"
            if calibrated > best["score"] or (calibrated == best["score"] and raw > best["raw_score"]):
                best = {"score": calibrated, "raw_score": raw, "equivalence": equivalence,
                        "common_name": common, "left_name": left_name, "right_name": right_name}
    return best


def _is_single_transposition(left: str, right: str) -> bool:
    if len(left) != len(right):
        return False
    differences = [index for index, (a, b) in enumerate(zip(left, right)) if a != b]
    return len(differences) == 2 and differences[1] == differences[0] + 1 and \
        left[differences[0]] == right[differences[1]] and left[differences[1]] == right[differences[0]]


def _compare_strong(field: str, left: tuple[str, ...], right: tuple[str, ...]) -> Evidence | None:
    if not left or not right:
        return None
    a = {normalize_identifier(value) for value in left if normalize_identifier(value)}
    b = {normalize_identifier(value) for value in right if normalize_identifier(value)}
    shared = a & b
    full_shared = {value for value in shared if len(value) >= 6}
    if full_shared:
        return Evidence(field, "strong", "match", STRONG_FIELDS[field], f"exact normalized value {sorted(full_shared)[0]}")
    if shared:
        return Evidence(field, "strong", "quality_flag", 0.0, "matching but short/partial values; not treated as a strong match")
    if any(_is_single_transposition(x, y) for x in a for y in b):
        return Evidence(field, "strong", "quality_flag", 0.0, "adjacent-character transposition; not treated as contradiction")
    if min((len(value) for value in a | b), default=0) >= 6:
        return Evidence(field, "strong", "contradiction", STRONG_FIELDS[field], "clean non-matching full values")
    return Evidence(field, "strong", "quality_flag", 0.0, "short/partial values; not treated as contradiction")


def _dob_parts(value: str) -> tuple[int | None, int | None, int | None] | None:
    text = str(value).strip().replace("/", "-")
    parts = text.split("-")
    if not 1 <= len(parts) <= 3:
        return None
    result: list[int | None] = []
    for part in parts:
        if part in {"", "00", "XX", "xx", "????"}:
            result.append(None)
        elif part.isdigit():
            result.append(int(part))
        else:
            return None
    result.extend([None] * (3 - len(result)))
    year, month, day = result
    try:
        if year and month and day:
            date(year, month, day)
    except ValueError:
        return None
    return year, month, day


def _compare_dob(left: str, right: str) -> Evidence:
    a, b = _dob_parts(left), _dob_parts(right)
    if not a or not b:
        return Evidence("dob", "moderate", "quality_flag", 0.0, "unparseable DOB")
    known = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if known and all(x == y for x, y in known):
        full = all(value is not None for value in (*a, *b))
        return Evidence("dob", "moderate", "match" if full else "partial_match", 0.70 if full else 0.30,
                        "full DOB match" if full else "known DOB components agree")
    compact_a = "".join(f"{part:02d}" if part is not None else "" for part in a)
    compact_b = "".join(f"{part:02d}" if part is not None else "" for part in b)
    if compact_a and compact_b and _is_single_transposition(compact_a, compact_b):
        return Evidence("dob", "moderate", "quality_flag", 0.0, "one adjacent-digit transposition; not decisive")
    if a[0] is not None and b[0] is not None and abs(a[0] - b[0]) == 1 and a[1:] == b[1:]:
        return Evidence("dob", "moderate", "quality_flag", 0.0, "one-digit/year data-quality variant; not decisive")
    return Evidence("dob", "moderate", "contradiction", 0.70, "incompatible known DOB components")


def _compare_text_field(field: str, left: str, right: str, weight: float, threshold: float, strength: str) -> Evidence:
    score = jaro_winkler(left, right)
    if normalize_text(left) == normalize_text(right) or score >= threshold:
        return Evidence(field, strength, "match", weight, f"normalized similarity {score:.3f}")
    return Evidence(field, strength, "contradiction", weight, f"normalized similarity {score:.3f}")


def compare_identifiers(left: dict[str, Any], right: dict[str, Any], config: ResolutionConfig) -> list[Evidence]:
    evidence: list[Evidence] = []
    for field in STRONG_FIELDS:
        item = _compare_strong(field, _values(left, field), _values(right, field))
        if item:
            evidence.append(item)
    if _values(left, "dob") and _values(right, "dob"):
        evidence.append(_compare_dob(_values(left, "dob")[0], _values(right, "dob")[0]))
    for field, threshold in (("place_of_birth", config.place_similarity_match), ("address", config.address_similarity_match)):
        if _values(left, field) and _values(right, field):
            evidence.append(_compare_text_field(field, _values(left, field)[0], _values(right, field)[0],
                                                MODERATE_FIELDS[field], threshold, "moderate"))
    if _values(left, "nationality") and _values(right, "nationality"):
        evidence.append(_compare_text_field("nationality", _values(left, "nationality")[0],
                                            _values(right, "nationality")[0], WEAK_FIELDS["nationality"], 0.92, "weak"))
    return evidence


def resolve_pair(left: dict[str, Any], right: dict[str, Any], config: ResolutionConfig | None = None) -> dict[str, Any]:
    config = config or ResolutionConfig()
    name = compare_names(left, right)
    evidence = compare_identifiers(left, right, config)
    strong_matches = [item for item in evidence if item.strength == "strong" and item.result == "match"]
    strong_conflicts = [item for item in evidence if item.strength == "strong" and item.result == "contradiction"]
    moderate_positive = sum(item.weight for item in evidence if item.strength == "moderate" and item.result in {"match", "partial_match"})
    moderate_negative = sum(item.weight for item in evidence if item.strength == "moderate" and item.result == "contradiction")
    flags = [item.detail for item in evidence if item.result == "quality_flag"]

    # Structural safety invariant: the sole production path to SAME requires a shared strong ID.
    if strong_matches and not strong_conflicts:
        disposition, reason = "SAME", f"shared strong identifier: {strong_matches[0].field}"
    elif strong_matches and strong_conflicts:
        disposition, reason = "REVIEW", "conflicting strong evidence; human reconciliation required"
    elif strong_conflicts:
        disposition, reason = "DIFFERENT", f"clean strong-identifier contradiction: {strong_conflicts[0].field}"
    elif (moderate_negative >= config.decisive_moderate_contradiction
          and moderate_positive == 0
          and name["raw_score"] >= config.minimum_name_context_for_moderate_difference):
        disposition, reason = "DIFFERENT", "decisive unopposed moderate-identifier contradiction"
    else:
        disposition = "REVIEW"
        if not evidence:
            reason = "name-only evidence cannot establish identity"
        elif name["common_name"] and not moderate_positive:
            reason = "common-name base rate and no corroborating identifier"
        elif flags:
            reason = "data-quality or partial-identifier evidence is non-decisive"
        else:
            reason = "evidence is insufficient or mixed"

    result = {
        "disposition": disposition,
        "reason": reason,
        "shared_strong_identifier": bool(strong_matches),
        "name": name,
        "evidence": [asdict(item) for item in evidence],
        "scores": {"moderate_positive": round(moderate_positive, 6),
                   "moderate_negative": round(moderate_negative, 6)},
        "quality_flags": flags,
    }
    if result["disposition"] == "SAME" and not result["shared_strong_identifier"]:
        raise AssertionError("structural invariant violated: SAME requires a shared strong identifier")
    return result
