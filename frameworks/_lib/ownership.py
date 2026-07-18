"""Ownership-graph mathematics, resolution integrity, and control-prong logic.

Effective ownership is the sum of path products. Repeated paths created by cycles are
evaluated as a convergent series. A production auto-clear is structurally unreachable
unless the relevant graph is complete, transparent, converged, below threshold, and
free of a qualifying control prong.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class OwnershipConfig:
    threshold: float = 0.25
    near_threshold_margin: float = 0.02
    convergence_tolerance: float = 1e-12
    max_iterations: int = 500
    ownership_cap: float = 1.0


@dataclass(frozen=True)
class ControlEvidence:
    prong: str
    controlled_entity: str
    direct_to_target: bool
    entity_effective_ownership: float
    detail: str


def _validate_graph(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    nodes = graph.get("nodes")
    edges = graph.get("ownership_edges", [])
    controls = graph.get("control_relationships", [])
    target = graph.get("target_entity")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("nodes must be a non-empty array")
    if not isinstance(edges, list) or not isinstance(controls, list):
        raise ValueError("ownership_edges and control_relationships must be arrays")
    index: dict[str, dict[str, Any]] = {}
    for position, node in enumerate(nodes):
        if not isinstance(node, dict) or not str(node.get("id", "")).strip():
            raise ValueError(f"nodes[{position}] requires a non-empty id")
        node_id = str(node["id"])
        if node_id in index:
            raise ValueError(f"duplicate node id: {node_id}")
        if node.get("type") not in {"person", "entity"}:
            raise ValueError(f"node {node_id} type must be person or entity")
        index[node_id] = node
    if target not in index or index[target]["type"] != "entity":
        raise ValueError("target_entity must identify an entity node")
    for position, edge in enumerate(edges):
        if not isinstance(edge, dict) or edge.get("owner") not in index or edge.get("owned") not in index:
            raise ValueError(f"ownership_edges[{position}] references an unknown node")
        if index[edge["owned"]]["type"] != "entity":
            raise ValueError(f"ownership_edges[{position}].owned must be an entity")
        try:
            fraction = float(edge["fraction"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"ownership_edges[{position}].fraction must be numeric") from exc
        if not 0.0 <= fraction <= 1.0:
            raise ValueError(f"ownership_edges[{position}].fraction must be between 0 and 1")
    for position, relationship in enumerate(controls):
        if not isinstance(relationship, dict):
            raise ValueError(f"control_relationships[{position}] must be an object")
        if relationship.get("person") not in index or index[relationship["person"]]["type"] != "person":
            raise ValueError(f"control_relationships[{position}].person must identify a person")
        if relationship.get("entity") not in index or index[relationship["entity"]]["type"] != "entity":
            raise ValueError(f"control_relationships[{position}].entity must identify an entity")
    return index


def _outgoing(graph: dict[str, Any]) -> dict[str, list[tuple[str, float]]]:
    output: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for edge in graph.get("ownership_edges", []):
        fraction = float(edge["fraction"])
        if fraction > 0:
            output[str(edge["owner"])].append((str(edge["owned"]), fraction))
    return output


def nodes_reaching_target(graph: dict[str, Any]) -> set[str]:
    index = _validate_graph(graph)
    reverse: dict[str, set[str]] = defaultdict(set)
    for edge in graph.get("ownership_edges", []):
        if float(edge["fraction"]) > 0:
            reverse[str(edge["owned"])].add(str(edge["owner"]))
    target = str(graph["target_entity"])
    reached = {target}
    stack = [target]
    while stack:
        node = stack.pop()
        for owner in reverse.get(node, set()):
            if owner not in reached:
                reached.add(owner)
                stack.append(owner)
    return reached & set(index)


def graph_resolution(graph: dict[str, Any], candidate_id: str | None = None) -> dict[str, Any]:
    index = _validate_graph(graph)
    relevant = nodes_reaching_target(graph)
    unresolved = []
    for node_id in sorted(relevant):
        node = index[node_id]
        if node.get("resolved") is False:
            unresolved.append({"node_id": node_id, "reason": "resolved=false"})
        if node.get("opaque") is True:
            unresolved.append({"node_id": node_id, "reason": "opaque intermediary"})
        if node.get("nominee") is True:
            unresolved.append({"node_id": node_id, "reason": "nominee relationship"})
        if node["type"] == "entity" and node.get("ownership_complete") is False:
            unresolved.append({"node_id": node_id, "reason": "ownership_complete=false"})
    if candidate_id is not None:
        if candidate_id not in index or index[candidate_id]["type"] != "person":
            raise ValueError("candidate_id must identify a person node")
        candidate = index[candidate_id]
        if candidate.get("resolved") is False or candidate.get("opaque") is True or candidate.get("nominee") is True:
            unresolved.append({"node_id": candidate_id, "reason": "candidate identity/nominee status unresolved"})
    return {"fully_resolved": not unresolved, "unresolved_items": unresolved,
            "relevant_nodes": sorted(relevant)}


def effective_ownership(graph: dict[str, Any], source_id: str,
                        config: OwnershipConfig | None = None) -> dict[str, Any]:
    config = config or OwnershipConfig()
    index = _validate_graph(graph)
    if source_id not in index:
        raise ValueError(f"unknown source_id: {source_id}")
    target = str(graph["target_entity"])
    if source_id == target:
        return {"effective_ownership": 1.0, "raw_effective_ownership": 1.0, "converged": True,
                "iterations": 0, "residual_mass": 0.0, "capped": False}
    relevant = nodes_reaching_target(graph)
    outgoing = _outgoing(graph)
    frontier = {source_id: 1.0}
    total = 0.0
    residual = 1.0
    converged = False
    iterations = 0
    for iterations in range(1, config.max_iterations + 1):
        next_frontier: dict[str, float] = defaultdict(float)
        for owner, mass in frontier.items():
            for owned, fraction in outgoing.get(owner, []):
                if owned not in relevant:
                    continue
                contribution = mass * fraction
                if owned == target:
                    total += contribution
                else:
                    next_frontier[owned] += contribution
        frontier = dict(next_frontier)
        residual = sum(abs(value) for value in frontier.values())
        if residual <= config.convergence_tolerance:
            converged = True
            break
    capped = total > config.ownership_cap
    return {
        "effective_ownership": min(total, config.ownership_cap),
        "raw_effective_ownership": total,
        "converged": converged,
        "iterations": iterations,
        "residual_mass": residual,
        "capped": capped,
    }


def _qualifies_control(relationship: dict[str, Any], threshold: float) -> tuple[bool, str]:
    prong = str(relationship.get("prong", "")).strip().casefold().replace(" ", "_")
    decisive = relationship.get("decisive") is True
    if prong == "sole_director":
        return True, "sole director"
    if prong == "senior_managing_official":
        return True, "senior managing official"
    if prong in {"signatory", "authorized_signatory"}:
        qualifies = decisive or relationship.get("sole_authority") is True
        return qualifies, "sole/decisive signing authority" if qualifies else "non-sole signatory is not decisive"
    if prong == "voting_agreement":
        voting_fraction = float(relationship.get("voting_fraction", 0.0))
        qualifies = decisive or voting_fraction >= threshold
        return qualifies, f"voting agreement fraction {voting_fraction:.6f}"
    if prong == "director":
        qualifies = decisive or relationship.get("sole_director") is True
        return qualifies, "decisive directorship" if qualifies else "non-sole director is not decisive"
    if prong == "power_of_attorney":
        return decisive, "decisive power of attorney" if decisive else "limited power of attorney"
    return decisive, "explicitly decisive control relationship" if decisive else "unrecognized/non-decisive control relationship"


def control_prongs(graph: dict[str, Any], person_id: str,
                   config: OwnershipConfig | None = None) -> list[dict[str, Any]]:
    config = config or OwnershipConfig()
    index = _validate_graph(graph)
    if person_id not in index or index[person_id]["type"] != "person":
        raise ValueError("person_id must identify a person node")
    target = str(graph["target_entity"])
    evidence: list[ControlEvidence] = []
    for relationship in graph.get("control_relationships", []):
        if relationship.get("person") != person_id:
            continue
        qualifies, detail = _qualifies_control(relationship, config.threshold)
        if not qualifies:
            continue
        entity_id = str(relationship["entity"])
        direct = entity_id == target
        entity_share = 1.0 if direct else effective_ownership(graph, entity_id, config)["effective_ownership"]
        if direct or entity_share >= config.threshold:
            evidence.append(ControlEvidence(
                prong=str(relationship.get("prong", "unknown")), controlled_entity=entity_id,
                direct_to_target=direct, entity_effective_ownership=entity_share, detail=detail,
            ))
    return [asdict(item) for item in evidence]


def resolve_candidate(graph: dict[str, Any], candidate_id: str,
                      config: OwnershipConfig | None = None) -> dict[str, Any]:
    config = config or OwnershipConfig()
    ownership = effective_ownership(graph, candidate_id, config)
    resolution = graph_resolution(graph, candidate_id)
    controls = control_prongs(graph, candidate_id, config)
    effective = float(ownership["effective_ownership"])
    ownership_prong = effective >= config.threshold
    control_prong = bool(controls)
    auto_clear_eligible = (
        effective < config.threshold
        and not control_prong
        and resolution["fully_resolved"]
        and ownership["converged"]
        and not ownership["capped"]
        and effective < config.threshold - config.near_threshold_margin
    )
    if ownership_prong or control_prong:
        disposition = "CONFIRMED_BENEFICIAL_OWNER"
        reason = "effective ownership meets threshold" if ownership_prong else f"qualifying control prong: {controls[0]['prong']}"
    elif not resolution["fully_resolved"]:
        disposition, reason = "REVIEW", "ownership graph contains an unresolved, opaque, incomplete, or nominee element"
    elif not ownership["converged"] or ownership["capped"]:
        disposition, reason = "REVIEW", "circular ownership did not converge cleanly or required capping"
    elif effective >= config.threshold - config.near_threshold_margin:
        disposition, reason = "REVIEW", "effective ownership is within the near-threshold review margin"
    else:
        disposition, reason = "RESOLVED_BELOW_THRESHOLD", "fully resolved graph; aggregate ownership below threshold; no control prong"
    result = {
        "candidate_id": candidate_id,
        "disposition": disposition,
        "reason": reason,
        "effective_ownership": effective,
        "threshold": config.threshold,
        "ownership_prong": ownership_prong,
        "control_prong": control_prong,
        "control_evidence": controls,
        "graph_fully_resolved": resolution["fully_resolved"],
        "unresolved_items": resolution["unresolved_items"],
        "convergence": ownership,
        "auto_clear_eligible": auto_clear_eligible,
    }
    if disposition == "RESOLVED_BELOW_THRESHOLD" and not auto_clear_eligible:
        raise AssertionError("structural invariant violated: unsafe ownership auto-clear")
    return result


def resolve_graph(graph: dict[str, Any], config: OwnershipConfig | None = None) -> list[dict[str, Any]]:
    index = _validate_graph(graph)
    candidates = graph.get("candidates")
    if candidates is None:
        candidates = [node_id for node_id, node in index.items() if node["type"] == "person"]
    if not isinstance(candidates, list):
        raise ValueError("candidates must be an array")
    return [resolve_candidate(graph, str(candidate), config) for candidate in candidates]
