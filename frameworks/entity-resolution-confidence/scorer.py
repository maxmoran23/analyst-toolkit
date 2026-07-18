#!/usr/bin/env python3
"""CLI for conservative query-to-candidate entity resolution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _local.identity import resolve_pair


def validate_record(record: object, where: str) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError(f"{where} must be an object")
    if not record.get("name") and not record.get("names") and not record.get("aliases"):
        raise ValueError(f"{where} must contain name, names, or aliases")
    return record


def score_payload(payload: dict[str, Any]) -> dict[str, Any]:
    queries = payload.get("queries")
    if not isinstance(queries, list):
        raise ValueError("top-level 'queries' must be an array")
    output = {"schema_version": "1.0", "results": []}
    for q_index, item in enumerate(queries):
        if not isinstance(item, dict):
            raise ValueError(f"queries[{q_index}] must be an object")
        query = validate_record(item.get("query"), f"queries[{q_index}].query")
        candidates = item.get("candidates")
        if not isinstance(candidates, list):
            raise ValueError(f"queries[{q_index}].candidates must be an array")
        result = {"query_id": item.get("query_id", f"query-{q_index}"), "candidates": []}
        for c_index, candidate in enumerate(candidates):
            candidate = validate_record(candidate, f"queries[{q_index}].candidates[{c_index}]")
            decision = resolve_pair(query, candidate)
            result["candidates"].append({"candidate_id": candidate.get("candidate_id", f"candidate-{c_index}"), **decision})
        output["results"].append(result)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="default: stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        output = score_payload(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
