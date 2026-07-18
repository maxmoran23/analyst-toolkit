#!/usr/bin/env python3
"""Generate deterministic labelled identity pairs and an unlabelled sample-input pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from _lib.seeding import rng, stable_sample

GIVEN = ["Amina", "John", "Maria", "Wei", "Fatima", "Aleksandr", "Katherine", "Omar", "Sofia", "Daniel"]
FAMILY = ["Rahman", "Smith", "Garcia", "Li", "Patel", "Kuznetsov", "Kim", "Haddad", "Miller", "Singh"]
CITIES = ["Cairo", "Karachi", "Toronto", "London", "Lagos", "Dubai", "Singapore", "Madrid", "Berlin", "Sao Paulo"]
COUNTRIES = ["Egypt", "Pakistan", "Canada", "United Kingdom", "Nigeria", "UAE", "Singapore", "Spain", "Germany", "Brazil"]
COMMON_NAMES = ["John Smith", "Mohammed Ali", "Wei Li", "Maria Garcia", "Ahmed Khan", "Daniel Kim"]
TRANSLITERATIONS = [("Mohammed Rahman", "Muhammad Rahman"), ("Zhang Wei", "Chang Wei"),
                    ("Yousef Haddad", "Youssef Haddad"), ("Aleksandr Kuznetsov", "Alexander Kuznetsov")]


def _id(prefix: str, number: int, width: int = 8) -> str:
    return f"{prefix}{number:0{width}d}"


def _dob(index: int) -> str:
    year = 1965 + (index * 7) % 40
    month = 1 + (index * 5) % 12
    day = 1 + (index * 11) % 27
    return f"{year:04d}-{month:02d}-{day:02d}"


def _base(index: int) -> dict[str, Any]:
    given, family = GIVEN[index % len(GIVEN)], FAMILY[(index * 3) % len(FAMILY)]
    city_index = (index * 7) % len(CITIES)
    return {
        "name": f"{given} {family}",
        "dob": _dob(index),
        "place_of_birth": CITIES[city_index],
        "nationality": COUNTRIES[city_index],
        "address": f"{100 + index % 800} Market Street, {CITIES[(index * 2) % len(CITIES)]}",
    }


def _pair(pair_id: str, label: str, category: str, query: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    return {"pair_id": pair_id, "label": label, "category": category, "query": query, "candidate": candidate}


def _same_pair(index: int) -> dict[str, Any]:
    category = index % 6
    base = _base(index)
    if category == 0:
        left_name, right_name = TRANSLITERATIONS[index % len(TRANSLITERATIONS)]
        passport = _id("P", 100000 + index)
        query = {**base, "name": left_name, "passport": passport}
        candidate = {**base, "name": right_name, "passport": passport, "address": base["address"].replace("Street", "St")}
        name = "shared_passport_transliteration"
    elif category == 1:
        tax_id = _id("TAX", 200000 + index)
        parts = base["name"].split()
        query = {**base, "tax_id": tax_id}
        candidate = {**base, "name": f"{parts[-1]}, {parts[0]}", "tax_id": tax_id}
        name = "name_order_swap_shared_tax_id"
    elif category == 2:
        left_name, right_name = TRANSLITERATIONS[(index + 1) % len(TRANSLITERATIONS)]
        passport = _id("R", 300000 + index)
        query = {"name": left_name, "passport": passport, "nationality": base["nationality"]}
        candidate = {"name": right_name, "passport": passport, "nationality": base["nationality"]}
        name = "different_romanization_shared_passport"
    elif category == 3:
        year_month = "-".join(base["dob"].split("-")[:2])
        query = {"name": base["name"], "dob": base["dob"], "nationality": base["nationality"]}
        candidate = {"name": base["name"], "dob": year_month, "nationality": base["nationality"]}
        name = "partial_dob_only_true_match"
    elif category == 4:
        dob = base["dob"]
        year, month, day = dob.split("-")
        transposed = f"{year}-{month[::-1]}-{day}" if month[0] != month[1] else f"{year}-{month}-{day[::-1]}"
        query = {"name": base["name"], "dob": dob, "place_of_birth": base["place_of_birth"]}
        candidate = {"name": base["name"], "dob": transposed, "place_of_birth": base["place_of_birth"]}
        name = "dob_digit_transposition_true_match"
    else:
        national_id = _id("NID", 400000 + index)
        query = {**base, "national_id": national_id}
        candidate = {**base, "national_id": national_id, "address": f"PO Box {500 + index}, {CITIES[index % len(CITIES)]}"}
        name = "shared_national_id_address_drift"
    return _pair(f"S-{index:05d}", "SAME", name, query, candidate)


def _different_pair(index: int, name_only: bool = False) -> dict[str, Any]:
    if name_only:
        common = COMMON_NAMES[index % len(COMMON_NAMES)]
        return _pair(f"N-{index:05d}", "DIFFERENT", "distinct_common_name_name_only",
                     {"name": common}, {"name": common})
    category = index % 4
    base = _base(10000 + index)
    if category == 0:
        query = {**base, "national_id": _id("NID", 600000 + index)}
        candidate = {**base, "national_id": _id("NID", 900000 + index)}
        name = "distinct_clean_strong_id_conflict"
    elif category == 1:
        common = COMMON_NAMES[index % len(COMMON_NAMES)]
        query = {"name": common, "dob": "1978-02-11", "place_of_birth": "Cairo"}
        candidate = {"name": common, "dob": "1991-10-24", "place_of_birth": "Toronto"}
        name = "distinct_exact_name_moderate_contradictions"
    elif category == 2:
        query = {"name": base["name"], "passport": _id("P", 700000 + index)}
        candidate = {"name": base["name"], "passport": _id("P", 800000 + index)}
        name = "distinct_passport_conflict_sparse"
    else:
        other = _base(20000 + index)
        query = {"name": base["name"], "nationality": base["nationality"]}
        candidate = {"name": other["name"], "nationality": other["nationality"]}
        name = "distinct_sparse_unrelated_review"
    return _pair(f"D-{index:05d}", "DIFFERENT", name, query, candidate)


def generate_pairs(seed: int, same: int, different: int, name_only: int) -> list[dict[str, Any]]:
    if same < 6 or different < 4 or name_only < 1:
        raise ValueError("sizes must be at least --same 6 --different 4 --name-only 1")
    rows = [_same_pair(index) for index in range(same)]
    rows.extend(_different_pair(index) for index in range(different))
    rows.extend(_different_pair(index, name_only=True) for index in range(name_only))
    picker = rng(seed)
    picker.shuffle(rows)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_sample_pack(path: Path, rows: list[dict[str, Any]], seed: int, count: int) -> None:
    selected = stable_sample(rows, count, seed)
    queries = []
    for row in selected:
        candidate = {"candidate_id": f"C-{row['pair_id']}", **row["candidate"]}
        queries.append({"query_id": f"Q-{row['pair_id']}", "query": row["query"], "candidates": [candidate]})
    payload = {"schema_version": "1.0", "seed": seed, "queries": queries}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--same", type=int, default=160)
    parser.add_argument("--different", type=int, default=240)
    parser.add_argument("--name-only", type=int, default=80)
    parser.add_argument("--output", type=Path, default=Path("data/labelled-pairs.jsonl"))
    parser.add_argument("--sample-pack", type=Path)
    parser.add_argument("--sample-size", type=int, default=40)
    parser.add_argument("--out", type=Path,
                        help="write all outputs (population + sample-input.json) into this directory; "
                             "used by _tooling/build_reference_data.py")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        args.output = args.out / args.output.name
        args.sample_pack = args.out / "sample-input.json"
    rows = generate_pairs(args.seed, args.same, args.different, args.name_only)
    write_jsonl(args.output, rows)
    if args.sample_pack:
        write_sample_pack(args.sample_pack, rows, args.seed, args.sample_size)
    print(f"generated={len(rows)} seed={args.seed} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
