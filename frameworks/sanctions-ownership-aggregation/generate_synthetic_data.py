#!/usr/bin/env python3
"""Generate seeded labelled sanctions-ownership graphs and a sample-input pack."""

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
              edges: list[dict[str, Any]], sanctioned: list[str],
              controls: list[dict[str, Any]] | None = None, basis: str = "") -> dict[str, Any]:
    return {
        "case_id": case_id, "category": category, "label": label, "candidate_id": "target",
        "ground_truth_basis": basis,
        "graph": {"graph_id": case_id, "nodes": nodes, "ownership_edges": edges,
                  "sanctioned_parties": sanctioned, "control_relationships": controls or [],
                  "candidates": ["target"]},
    }


def base_nodes(sanctioned_count: int, *intermediaries: dict[str, Any]) -> list[dict[str, Any]]:
    sanctioned = [node(f"s{i + 1}", "person") for i in range(sanctioned_count)]
    return [*sanctioned, *intermediaries,
            node("target", "entity", ownership_complete=True, resolved=True)]


def true_blocked_case(index: int) -> dict[str, Any]:
    category = index % 6
    case_id = f"T-{index:06d}"
    if category == 0:
        edges = [edge("s1", "target", .30), edge("s2", "target", .25)]
        return make_case(case_id, "true_aggregation_30_plus_25", "TRUE_BLOCKED", base_nodes(2), edges,
                         ["s1", "s2"], basis="30% + 25% sanctioned ownership aggregates to 55%")
    if category == 1:
        edges = [edge("s1", "target", .18), edge("s2", "target", .17), edge("s3", "target", .16)]
        return make_case(case_id, "true_aggregation_three_subthreshold_owners", "TRUE_BLOCKED", base_nodes(3), edges,
                         ["s1", "s2", "s3"], basis="18% + 17% + 16% aggregates to 51%")
    if category == 2:
        shells = [node(f"shell_{n}", "entity", ownership_complete=True, resolved=True) for n in range(3)]
        edges = []
        for n in range(3):
            edges.extend([edge("s1", f"shell_{n}", 1.0), edge(f"shell_{n}", "target", .18)])
        return make_case(case_id, "true_concealed_majority_shell_slices", "TRUE_BLOCKED", base_nodes(1, *shells),
                         edges, ["s1"], basis="one sanctioned owner uses three 18% shell slices; aggregate 54%")
    if category == 3:
        a = node("cross_a", "entity", ownership_complete=True, resolved=True)
        b = node("cross_b", "entity", ownership_complete=True, resolved=True)
        edges = [edge("s1", "cross_a", .40), edge("cross_a", "target", 1.0),
                 edge("cross_a", "cross_b", .50), edge("cross_b", "cross_a", .50)]
        return make_case(case_id, "true_circular_cross_ownership", "TRUE_BLOCKED", base_nodes(1, a, b), edges,
                         ["s1"], basis="convergent circular series yields 53.3333%")
    if category == 4:
        clean = node("clean_intermediary", "entity", ownership_complete=True, resolved=True)
        edges = [edge("s1", "clean_intermediary", 1.0), edge("clean_intermediary", "target", .55)]
        return make_case(case_id, "true_sanctioned_party_behind_clean_intermediary", "TRUE_BLOCKED",
                         base_nodes(1, clean), edges, ["s1"], basis="sanctioned party indirectly owns 55%")
    a = node("holdco_a", "entity", ownership_complete=True, resolved=True)
    b = node("holdco_b", "entity", ownership_complete=True, resolved=True)
    edges = [edge("s1", "holdco_a", 1.0), edge("holdco_a", "target", .28),
             edge("s2", "holdco_b", 1.0), edge("holdco_b", "target", .24)]
    return make_case(case_id, "true_indirect_multiowner_aggregation", "TRUE_BLOCKED", base_nodes(2, a, b), edges,
                     ["s1", "s2"], basis="indirect 28% + 24% aggregates to 52%")


def not_blocked_case(index: int) -> dict[str, Any]:
    category = index % 6
    case_id = f"B-{index:06d}"
    if category == 0:
        return make_case(case_id, "below_direct_resolved", "NOT_BLOCKED", base_nodes(1),
                         [edge("s1", "target", .10)], ["s1"], basis="10% resolved sanctioned ownership")
    if category == 1:
        edges = [edge("s1", "target", .12), edge("s2", "target", .11)]
        return make_case(case_id, "below_aggregate_23_resolved", "NOT_BLOCKED", base_nodes(2), edges,
                         ["s1", "s2"], basis="aggregate 23% is below the review floor")
    if category == 2:
        return make_case(case_id, "below_zero_ownership", "NOT_BLOCKED", base_nodes(1), [], ["s1"],
                         basis="0% sanctioned ownership")
    if category == 3:
        return make_case(case_id, "below_review_band_30", "NOT_BLOCKED", base_nodes(1),
                         [edge("s1", "target", .30)], ["s1"], basis="30% does not meet 50% but requires review")
    if category == 4:
        return make_case(case_id, "below_near_threshold_49", "NOT_BLOCKED", base_nodes(1),
                         [edge("s1", "target", .49)], ["s1"], basis="49% is near the blocked threshold and requires review")
    controls = [{"person": "s1", "entity": "target", "prong": "sole_director"}]
    return make_case(case_id, "below_sanctioned_control_without_equity", "NOT_BLOCKED", base_nodes(1), [],
                     ["s1"], controls, basis="0% equity with sanctioned sole-director control routes to review")


def unresolved_case(index: int) -> dict[str, Any]:
    category = index % 4
    case_id = f"U-{index:06d}"
    if category == 0:
        intermediary = node("opaque_shell", "entity", ownership_complete=False, resolved=False, opaque=True)
        category_name = "unresolved_opaque_intermediary_below_looking"
    elif category == 1:
        intermediary = node("incomplete_holdco", "entity", ownership_complete=False, resolved=False)
        category_name = "unresolved_incomplete_intermediary_below_looking"
    elif category == 2:
        intermediary = node("nominee_holdco", "entity", ownership_complete=False, resolved=True, nominee=True)
        category_name = "unresolved_nominee_intermediary_below_looking"
    else:
        clean = node("clean_path", "entity", ownership_complete=True, resolved=True)
        opaque = node("opaque_path", "entity", ownership_complete=False, resolved=False, opaque=True)
        edges = [edge("s1", "clean_path", 1.0), edge("clean_path", "target", .05),
                 edge("s1", "opaque_path", 1.0), edge("opaque_path", "target", .05)]
        return make_case(case_id, "unresolved_parallel_opaque_path_below_looking", "NOT_BLOCKED",
                         base_nodes(1, clean, opaque), edges, ["s1"],
                         basis="aggregate appears 10%, but one sanctioned path is opaque")
    fraction = .10 + (index % 3) * .03
    edges = [edge("s1", intermediary["id"], 1.0), edge(intermediary["id"], "target", fraction)]
    return make_case(case_id, category_name, "NOT_BLOCKED", base_nodes(1, intermediary), edges, ["s1"],
                     basis="below-looking ownership path is unresolved")


def generate_cases(seed: int, true_blocked: int, below: int, unresolved: int) -> list[dict[str, Any]]:
    if true_blocked < 6 or below < 6 or unresolved < 4:
        raise ValueError("sizes must be at least --true-blocked 6 --below 6 --unresolved 4")
    cases = [true_blocked_case(seed * 10007 + index) for index in range(true_blocked)]
    cases.extend(not_blocked_case(seed * 10009 + index) for index in range(below))
    cases.extend(unresolved_case(seed * 10037 + index) for index in range(unresolved))
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
    parser.add_argument("--true-blocked", type=int, default=160)
    parser.add_argument("--below", type=int, default=240)
    parser.add_argument("--unresolved", type=int, default=80)
    parser.add_argument("--output", type=Path, default=Path("data/labelled-graphs.jsonl"))
    parser.add_argument("--out", type=Path, help="write sample-input.json into this directory")
    parser.add_argument("--sample-size", type=int, default=24)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases = generate_cases(args.seed, args.true_blocked, args.below, args.unresolved)
    write_jsonl(args.output, cases)
    if args.out:
        write_sample_pack(args.out / "sample-input.json", cases, args.seed, args.sample_size)
    print(f"generated={len(cases)} seed={args.seed} output={args.output}")
    if args.out:
        print(f"sample_input={args.out / 'sample-input.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
