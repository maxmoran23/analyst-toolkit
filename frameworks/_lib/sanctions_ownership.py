"""OFAC-style aggregate sanctioned-ownership resolution built on ownership.py math."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from .ownership import OwnershipConfig, effective_ownership, graph_resolution, nodes_reaching_target


@dataclass(frozen=True)
class SanctionsConfig:
    blocked_threshold: float = 0.50
    review_floor: float = 0.25
    near_threshold_margin: float = 0.02
    convergence_tolerance: float = 1e-12
    max_iterations: int = 500
    aggregate_cap: float = 1.0
    max_evidence_paths: int = 2000
    max_path_states: int = 20000


def _target_graph(graph: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    return {**graph, "target_entity": candidate_id}


def _node_index(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    nodes = graph.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("nodes must be an array")
    index = {str(node.get("id")): node for node in nodes if isinstance(node, dict) and node.get("id") is not None}
    if len(index) != len(nodes):
        raise ValueError("every node requires a unique id")
    return index


def validate_input(graph: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    index = _node_index(graph)
    sanctioned = graph.get("sanctioned_parties", [])
    candidates = graph.get("candidates", [])
    if not isinstance(sanctioned, list) or not isinstance(candidates, list):
        raise ValueError("sanctioned_parties and candidates must be arrays")
    sanctioned_ids = [str(item) for item in sanctioned]
    candidate_ids = [str(item) for item in candidates]
    if len(set(sanctioned_ids)) != len(sanctioned_ids):
        raise ValueError("sanctioned_parties must not contain duplicates")
    for party in sanctioned_ids:
        if party not in index:
            raise ValueError(f"unknown sanctioned party: {party}")
    for candidate in candidate_ids:
        if candidate not in index or index[candidate].get("type") != "entity":
            raise ValueError(f"candidate must identify an entity node: {candidate}")
        # Reuse ownership.py validation and target-reachability semantics.
        graph_resolution(_target_graph(graph, candidate))
    return index, sanctioned_ids, candidate_ids


def trace_paths(graph: dict[str, Any], source_id: str, candidate_id: str,
                config: SanctionsConfig | None = None) -> dict[str, Any]:
    """Emit every numerically material path contribution under the convergence policy."""
    config = config or SanctionsConfig()
    target_graph = _target_graph(graph, candidate_id)
    relevant = nodes_reaching_target(target_graph)
    outgoing: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for ownership_edge in graph.get("ownership_edges", []):
        fraction = float(ownership_edge["fraction"])
        if fraction > 0:
            outgoing[str(ownership_edge["owner"])].append((str(ownership_edge["owned"]), fraction))
    for owner in outgoing:
        outgoing[owner].sort()
    frontier: list[tuple[str, tuple[str, ...], tuple[float, ...], float]] = [
        (source_id, (source_id,), (), 1.0)
    ]
    paths: list[dict[str, Any]] = []
    total = 0.0
    residual = 1.0
    truncated = False
    converged = False
    iterations = 0
    for iterations in range(1, config.max_iterations + 1):
        next_frontier = []
        for owner, node_path, fractions, mass in frontier:
            for owned, fraction in outgoing.get(owner, []):
                if owned not in relevant:
                    continue
                contribution = mass * fraction
                next_nodes = (*node_path, owned)
                next_fractions = (*fractions, fraction)
                if owned == candidate_id:
                    total += contribution
                    if len(paths) < config.max_evidence_paths:
                        paths.append({"nodes": list(next_nodes), "fractions": list(next_fractions),
                                      "contribution": contribution})
                    else:
                        truncated = True
                else:
                    next_frontier.append((owned, next_nodes, next_fractions, contribution))
                    if len(next_frontier) > config.max_path_states:
                        truncated = True
                        break
            if truncated and len(next_frontier) > config.max_path_states:
                break
        if len(next_frontier) > config.max_path_states:
            next_frontier = sorted(next_frontier, key=lambda item: (-item[3], item[1]))[:config.max_path_states]
        frontier = next_frontier
        residual = sum(abs(item[3]) for item in frontier)
        if residual <= config.convergence_tolerance:
            converged = True
            break
    paths.sort(key=lambda item: (-item["contribution"], item["nodes"]))
    return {
        "paths": paths,
        "path_contribution_total": total,
        "iterations": iterations,
        "residual_mass": residual,
        "converged": converged,
        "evidence_complete": converged and not truncated,
        "truncated": truncated,
    }


def _qualifying_control(relationship: dict[str, Any], threshold: float) -> tuple[bool, str]:
    prong = str(relationship.get("prong", "")).strip().casefold().replace(" ", "_")
    decisive = relationship.get("decisive") is True
    if prong in {"sole_director", "senior_managing_official"}:
        return True, prong.replace("_", " ")
    if prong in {"signatory", "authorized_signatory"}:
        qualifies = decisive or relationship.get("sole_authority") is True
        return qualifies, "sole/decisive signing authority" if qualifies else "non-sole signatory"
    if prong == "voting_agreement":
        voting_fraction = float(relationship.get("voting_fraction", 0.0))
        qualifies = decisive or voting_fraction >= threshold
        return qualifies, f"voting agreement fraction {voting_fraction:.6f}"
    if prong == "director":
        qualifies = decisive or relationship.get("sole_director") is True
        return qualifies, "decisive directorship" if qualifies else "non-sole director"
    if prong == "power_of_attorney":
        return decisive, "decisive power of attorney" if decisive else "limited power of attorney"
    return decisive, "explicitly decisive control" if decisive else "non-qualifying control"


def sanctioned_control_evidence(graph: dict[str, Any], sanctioned_ids: list[str], candidate_id: str,
                                config: SanctionsConfig) -> list[dict[str, Any]]:
    target_graph = _target_graph(graph, candidate_id)
    relevant = nodes_reaching_target(target_graph)
    evidence = []
    for relationship in graph.get("control_relationships", []):
        controller = str(relationship.get("person", ""))
        controlled_entity = str(relationship.get("entity", ""))
        if controller not in sanctioned_ids or controlled_entity not in relevant:
            continue
        qualifies, detail = _qualifying_control(relationship, config.blocked_threshold)
        if qualifies:
            evidence.append({"sanctioned_party": controller, "controlled_entity": controlled_entity,
                             "prong": relationship.get("prong"), "detail": detail,
                             "direct_to_candidate": controlled_entity == candidate_id})
    return evidence


def resolve_candidate(graph: dict[str, Any], candidate_id: str,
                      config: SanctionsConfig | None = None) -> dict[str, Any]:
    config = config or SanctionsConfig()
    _, sanctioned_ids, candidate_ids = validate_input(graph)
    if candidate_id not in candidate_ids:
        raise ValueError("candidate_id must appear in candidates")
    target_graph = _target_graph(graph, candidate_id)
    ownership_config = OwnershipConfig(
        threshold=config.blocked_threshold,
        convergence_tolerance=config.convergence_tolerance,
        max_iterations=config.max_iterations,
    )
    owner_evidence = []
    aggregate_raw = 0.0
    all_converged = True
    all_evidence_complete = True
    any_capped = False
    for party in sanctioned_ids:
        ownership = effective_ownership(target_graph, party, ownership_config)
        trace = trace_paths(graph, party, candidate_id, config)
        trace["matches_effective_ownership"] = abs(
            float(trace["path_contribution_total"]) - float(ownership["raw_effective_ownership"])
        ) <= max(config.convergence_tolerance, abs(float(ownership["raw_effective_ownership"])) * 1e-10)
        trace["evidence_complete"] = trace["evidence_complete"] and trace["matches_effective_ownership"]
        aggregate_raw += float(ownership["effective_ownership"])
        all_converged = all_converged and bool(ownership["converged"])
        all_evidence_complete = all_evidence_complete and bool(trace["evidence_complete"])
        any_capped = any_capped or bool(ownership["capped"])
        owner_evidence.append({"sanctioned_party": party,
                               "effective_ownership": ownership["effective_ownership"],
                               "raw_effective_ownership": ownership["raw_effective_ownership"],
                               "convergence": ownership, "path_evidence": trace})
    aggregate = min(aggregate_raw, config.aggregate_cap)
    resolution = graph_resolution(target_graph)
    controls = sanctioned_control_evidence(graph, sanctioned_ids, candidate_id, config)
    individual_blocker = any(item["effective_ownership"] >= config.blocked_threshold for item in owner_evidence)
    aggregate_blocker = aggregate >= config.blocked_threshold
    near_threshold = config.blocked_threshold - config.near_threshold_margin <= aggregate < config.blocked_threshold
    auto_clear_eligible = (
        aggregate < config.review_floor
        and resolution["fully_resolved"]
        and all_converged
        and all_evidence_complete
        and not any_capped
        and not controls
    )
    if aggregate_blocker:
        disposition = "BLOCKED_BY_OWNERSHIP"
        reason = ("one sanctioned owner meets the 50% threshold" if individual_blocker
                  else "aggregate sanctioned ownership meets the 50% threshold")
    elif not resolution["fully_resolved"]:
        disposition, reason = "REVIEW", "a relevant ownership path is unresolved, opaque, incomplete, or nominee-linked"
    elif not all_converged or not all_evidence_complete or any_capped:
        disposition, reason = "REVIEW", "ownership convergence or path evidence is incomplete"
    elif controls:
        disposition, reason = "REVIEW", "sanctioned control exists without qualifying 50% ownership"
    elif aggregate >= config.review_floor:
        disposition, reason = "REVIEW", "aggregate sanctioned ownership is in the 25%-to-50% review band"
    else:
        disposition, reason = "NOT_BLOCKED_BY_OWNERSHIP", "fully resolved aggregate below 25%; no sanctioned-control prong"
    result = {
        "candidate_id": candidate_id,
        "disposition": disposition,
        "reason": reason,
        "aggregate_sanctioned_ownership": aggregate,
        "raw_aggregate_sanctioned_ownership": aggregate_raw,
        "blocked_threshold": config.blocked_threshold,
        "review_floor": config.review_floor,
        "near_threshold": near_threshold,
        "individual_blocker": individual_blocker,
        "aggregate_blocker": aggregate_blocker,
        "sanctioned_owner_evidence": owner_evidence,
        "sanctioned_control_prong": bool(controls),
        "sanctioned_control_evidence": controls,
        "graph_fully_resolved": resolution["fully_resolved"],
        "unresolved_items": resolution["unresolved_items"],
        "all_converged": all_converged,
        "all_path_evidence_complete": all_evidence_complete,
        "auto_clear_eligible": auto_clear_eligible,
    }
    if disposition == "NOT_BLOCKED_BY_OWNERSHIP" and not auto_clear_eligible:
        raise AssertionError("structural invariant violated: unsafe sanctions ownership auto-clear")
    return result


def resolve_graph(graph: dict[str, Any], config: SanctionsConfig | None = None) -> list[dict[str, Any]]:
    _, _, candidates = validate_input(graph)
    return [resolve_candidate(graph, candidate, config) for candidate in candidates]
