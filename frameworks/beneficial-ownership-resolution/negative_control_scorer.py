"""Intentionally unsafe ownership scorer used only to prove both gates fail closed."""

from __future__ import annotations

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from _lib.ownership import OwnershipConfig, resolve_candidate


def score_candidate(graph: dict, candidate_id: str, config: OwnershipConfig | None = None) -> dict:
    config = config or OwnershipConfig()
    production = resolve_candidate(graph, candidate_id, config)
    if production["control_prong"]:
        return production
    direct = sum(float(edge["fraction"]) for edge in graph.get("ownership_edges", [])
                 if edge.get("owner") == candidate_id and edge.get("owned") == graph.get("target_entity"))
    weakened = dict(production)
    if direct >= config.threshold:
        weakened.update({"disposition": "CONFIRMED_BENEFICIAL_OWNER",
                         "reason": "UNSAFE: direct-only ownership check happened to meet threshold"})
    else:
        weakened.update({"disposition": "RESOLVED_BELOW_THRESHOLD",
                         "reason": "UNSAFE: direct-only ownership check ignored path aggregation and graph resolution"})
    return weakened
