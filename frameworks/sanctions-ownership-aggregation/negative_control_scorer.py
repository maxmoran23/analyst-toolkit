"""Intentionally unsafe single-owner-only scorer for live gate testing."""

from __future__ import annotations

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from _lib.sanctions_ownership import SanctionsConfig, resolve_candidate


def score_candidate(graph: dict, candidate_id: str, config: SanctionsConfig | None = None) -> dict:
    config = config or SanctionsConfig()
    production = resolve_candidate(graph, candidate_id, config)
    maximum_individual = max(
        (float(item["effective_ownership"]) for item in production["sanctioned_owner_evidence"]),
        default=0.0,
    )
    weakened = dict(production)
    if maximum_individual >= config.blocked_threshold:
        weakened.update({"disposition": "BLOCKED_BY_OWNERSHIP",
                         "reason": "UNSAFE: single-owner-only check happened to reach 50%"})
    else:
        weakened.update({"disposition": "NOT_BLOCKED_BY_OWNERSHIP",
                         "reason": "UNSAFE: single-owner-only check ignored aggregation and graph resolution"})
    return weakened
