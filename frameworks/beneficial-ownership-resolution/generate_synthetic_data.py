#!/usr/bin/env python3
"""Generate deterministic, labelled ownership graphs with adversarial safety plants."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from _lib.seeding import rng, stable_sample


def node(node_id: str, kind: str, **flags: Any) -> dict[str, Any]:
    return {"id": node_id, "type": kind, "name": node_id.replace("_", " ").title(), **flags}


def edge(owner: str, owned: str, fraction: float) -> dict[str, Any]:
    return {"owner": owner, "owned": owned, "fraction": fraction}


def make_case(case_id: str, category: str, label: str, nodes: list[dict[str, Any]],
              edges: list[dict[str, Any]], controls: list[dict[str, Any]] | None = None,
              basis: str = "") -> dict[str, Any]:
    return {
        "case_id": case_id, "category": category, "label": label, "candidate_id": "person",
        "ground_truth_basis": basis,
        "graph": {"graph_id": case_id, "target_entity": "target", "nodes": nodes,
                  "ownership_edges": edges, "control_relationships": controls or [], "candidates": ["person"]},
    }


def base_nodes(*intermediaries: dict[str, Any]) -> list[dict[str, Any]]:
    return [node("person", "person"), *intermediaries,
            node("target", "entity", ownership_complete=True, resolved=True)]


def true_owner_case(index: int) -> dict[str, Any]:
    category = index % 6
    case_id = f"T-{index:05d}"
    if category == 0:
        shells = [node(f"shell_{n}", "entity", ownership_complete=True, resolved=True) for n in range(3)]
        edges = []
        for n in range(3):
            edges.extend([edge("person", f"shell_{n}", 1.0), edge(f"shell_{n}", "target", .09)])
        return make_case(case_id, "true_concealed_majority_many_subthreshold_shells", "TRUE_BO",
                         base_nodes(*shells), edges, basis="three 9% shell paths aggregate to 27%")
    if category == 1:
        a = node("cross_a", "entity", ownership_complete=True, resolved=True)
        b = node("cross_b", "entity", ownership_complete=True, resolved=True)
        edges = [edge("person", "cross_a", .20), edge("cross_a", "target", 1.0),
                 edge("cross_a", "cross_b", .50), edge("cross_b", "cross_a", .50)]
        return make_case(case_id, "true_circular_cross_ownership", "TRUE_BO", base_nodes(a, b), edges,
                         basis="convergent circular path series equals 26.6667%")
    if category == 2:
        opaque = node("opaque_holdco", "entity", ownership_complete=False, resolved=False, opaque=True)
        edges = [edge("person", "opaque_holdco", .30), edge("opaque_holdco", "target", 1.0)]
        return make_case(case_id, "true_opaque_layer_above_threshold", "TRUE_BO", base_nodes(opaque), edges,
                         basis="known path product is 30% despite opacity; owner must be surfaced")
    if category == 3:
        controls = [{"person": "person", "entity": "target", "prong": "sole_director"}]
        return make_case(case_id, "true_control_without_equity_sole_director", "TRUE_BO", base_nodes(), [], controls,
                         basis="0% equity plus qualifying sole-director control prong")
    if category == 4:
        fraction = .30 + (index % 3) * .01
        return make_case(case_id, "true_direct_ownership", "TRUE_BO", base_nodes(),
                         [edge("person", "target", fraction)], basis=f"direct ownership {fraction:.2%}")
    a = node("path_a", "entity", ownership_complete=True, resolved=True)
    b = node("path_b", "entity", ownership_complete=True, resolved=True)
    edges = [edge("person", "path_a", .50), edge("path_a", "target", .30),
             edge("person", "path_b", .50), edge("path_b", "target", .25)]
    return make_case(case_id, "true_multipath_products", "TRUE_BO", base_nodes(a, b), edges,
                     basis="15% plus 12.5% path products aggregate to 27.5%")


def below_case(index: int) -> dict[str, Any]:
    category = index % 5
    case_id = f"B-{index:05d}"
    if category == 0:
        return make_case(case_id, "below_direct_fully_resolved", "NOT_BO", base_nodes(),
                         [edge("person", "target", .10)], basis="10% direct ownership; complete graph")
    if category == 1:
        a = node("small_a", "entity", ownership_complete=True, resolved=True)
        b = node("small_b", "entity", ownership_complete=True, resolved=True)
        edges = [edge("person", "small_a", .20), edge("small_a", "target", .40),
                 edge("person", "small_b", .20), edge("small_b", "target", .35)]
        return make_case(case_id, "below_multipath_fully_resolved", "NOT_BO", base_nodes(a, b), edges,
                         basis="8% plus 7% path products aggregate to 15%")
    if category == 2:
        return make_case(case_id, "below_zero_equity_no_control", "NOT_BO", base_nodes(), [],
                         basis="0% equity, no qualifying control, complete graph")
    if category == 3:
        controls = [{"person": "person", "entity": "target", "prong": "director", "sole_director": False}]
        return make_case(case_id, "below_nonsole_director", "NOT_BO", base_nodes(),
                         [edge("person", "target", .05)], controls,
                         basis="5% equity and non-sole directorship is not a qualifying control prong")
    return make_case(case_id, "below_near_threshold_review", "NOT_BO", base_nodes(),
                     [edge("person", "target", .24)], basis="24% is below threshold but inside review margin")


def unresolved_case(index: int) -> dict[str, Any]:
    category = index % 4
    case_id = f"U-{index:05d}"
    if category == 0:
        intermediary = node("opaque_shell", "entity", ownership_complete=False, resolved=False, opaque=True)
        category_name = "unresolved_opaque_intermediary_below_looking"
    elif category == 1:
        intermediary = node("incomplete_holdco", "entity", ownership_complete=False, resolved=False)
        category_name = "unresolved_incomplete_intermediary_below_looking"
    elif category == 2:
        intermediary = node("nominee_holdco", "entity", ownership_complete=False, resolved=True, nominee=True)
        category_name = "unresolved_nominee_layer_below_looking"
    else:
        opaque_branch = node("unrelated_opaque_owner", "entity", ownership_complete=False, resolved=False, opaque=True)
        nodes = base_nodes(opaque_branch)
        edges = [edge("person", "target", .10), edge("unrelated_opaque_owner", "target", .60)]
        return make_case(case_id, "unresolved_global_target_graph_below_looking", "NOT_BO", nodes, edges,
                         basis="candidate appears at 10%, but another target-ownership branch is opaque")
    edges = [edge("person", intermediary["id"], .10 + (index % 3) * .02), edge(intermediary["id"], "target", 1.0)]
    return make_case(case_id, category_name, "NOT_BO", base_nodes(intermediary), edges,
                     basis="computed slice is below threshold but the chain cannot be resolved")


def generate_cases(seed: int, true_owners: int, below: int, unresolved: int) -> list[dict[str, Any]]:
    if true_owners < 6 or below < 5 or unresolved < 4:
        raise ValueError("sizes must be at least --true-owners 6 --below 5 --unresolved 4")
    # Prime seed strides vary category boundaries and numeric variants, not merely row order.
    cases = [true_owner_case(seed * 10003 + index) for index in range(true_owners)]
    cases.extend(below_case(seed * 10007 + index) for index in range(below))
    cases.extend(unresolved_case(seed * 10009 + index) for index in range(unresolved))
    picker = rng(seed)
    picker.shuffle(cases)
    return cases


def write_jsonl(path: Path, cases: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(case, sort_keys=True) + "\n")


def write_sample_pack(path: Path, cases: list[dict[str, Any]], seed: int, count: int) -> None:
    selected = stable_sample(cases, count, seed)
    payload = {"schema_version": "1.0", "seed": seed, "graphs": [case["graph"] for case in selected]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--true-owners", type=int, default=160)
    parser.add_argument("--below", type=int, default=240)
    parser.add_argument("--unresolved", type=int, default=80)
    parser.add_argument("--output", type=Path, default=Path("data/labelled-graphs.jsonl"))
    parser.add_argument("--sample-pack", type=Path)
    parser.add_argument("--sample-size", type=int, default=24)
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
    cases = generate_cases(args.seed, args.true_owners, args.below, args.unresolved)
    write_jsonl(args.output, cases)
    if args.sample_pack:
        write_sample_pack(args.sample_pack, cases, args.seed, args.sample_size)
    print(f"generated={len(cases)} seed={args.seed} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
