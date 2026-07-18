#!/usr/bin/env python3
"""CLI for conservative beneficial-ownership and control resolution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from _lib.ownership import OwnershipConfig, resolve_graph


def score_payload(payload: dict) -> dict:
    graphs = payload.get("graphs")
    if not isinstance(graphs, list):
        raise ValueError("top-level 'graphs' must be an array")
    output = {"schema_version": "1.0", "results": []}
    for index, graph in enumerate(graphs):
        if not isinstance(graph, dict):
            raise ValueError(f"graphs[{index}] must be an object")
        config = OwnershipConfig(
            threshold=float(graph.get("threshold", payload.get("threshold", 0.25))),
            near_threshold_margin=float(graph.get("near_threshold_margin", payload.get("near_threshold_margin", 0.02))),
            convergence_tolerance=float(graph.get("convergence_tolerance", payload.get("convergence_tolerance", 1e-12))),
            max_iterations=int(graph.get("max_iterations", payload.get("max_iterations", 500))),
        )
        results = resolve_graph(graph, config)
        output["results"].append({"graph_id": graph.get("graph_id", f"graph-{index}"),
                                  "target_entity": graph.get("target_entity"), "candidates": results})
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
    rendered = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
