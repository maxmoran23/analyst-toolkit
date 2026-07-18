from __future__ import annotations

import unittest

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from _lib.ownership import OwnershipConfig, effective_ownership, resolve_candidate


def graph(nodes, edges, controls=None, candidate="p"):
    return {"target_entity": "t", "nodes": nodes, "ownership_edges": edges,
            "control_relationships": controls or [], "candidates": [candidate]}


class OwnershipTests(unittest.TestCase):
    def test_direct_ownership(self) -> None:
        g = graph([{"id": "p", "type": "person"}, {"id": "t", "type": "entity", "ownership_complete": True}],
                  [{"owner": "p", "owned": "t", "fraction": 0.30}])
        self.assertAlmostEqual(effective_ownership(g, "p")["effective_ownership"], 0.30)

    def test_multipath_aggregation(self) -> None:
        nodes = [{"id": "p", "type": "person"}, {"id": "a", "type": "entity", "ownership_complete": True},
                 {"id": "b", "type": "entity", "ownership_complete": True}, {"id": "t", "type": "entity", "ownership_complete": True}]
        edges = [{"owner": "p", "owned": "a", "fraction": 1.0}, {"owner": "a", "owned": "t", "fraction": .14},
                 {"owner": "p", "owned": "b", "fraction": 1.0}, {"owner": "b", "owned": "t", "fraction": .14}]
        self.assertAlmostEqual(effective_ownership(graph(nodes, edges), "p")["effective_ownership"], .28)

    def test_circular_ownership_converges(self) -> None:
        nodes = [{"id": "p", "type": "person"}, {"id": "a", "type": "entity", "ownership_complete": True},
                 {"id": "b", "type": "entity", "ownership_complete": True}, {"id": "t", "type": "entity", "ownership_complete": True}]
        edges = [{"owner": "p", "owned": "a", "fraction": .20}, {"owner": "a", "owned": "t", "fraction": 1.0},
                 {"owner": "a", "owned": "b", "fraction": .50}, {"owner": "b", "owned": "a", "fraction": .50}]
        result = effective_ownership(graph(nodes, edges), "p")
        self.assertTrue(result["converged"])
        self.assertAlmostEqual(result["effective_ownership"], 0.266666666666, places=9)

    def test_concealed_majority_is_confirmed(self) -> None:
        nodes = [{"id": "p", "type": "person"}, {"id": "a", "type": "entity", "ownership_complete": True},
                 {"id": "b", "type": "entity", "ownership_complete": True}, {"id": "t", "type": "entity", "ownership_complete": True}]
        edges = [{"owner": "p", "owned": "a", "fraction": .14}, {"owner": "a", "owned": "t", "fraction": 1.0},
                 {"owner": "p", "owned": "b", "fraction": .14}, {"owner": "b", "owned": "t", "fraction": 1.0}]
        self.assertEqual(resolve_candidate(graph(nodes, edges), "p")["disposition"], "CONFIRMED_BENEFICIAL_OWNER")

    def test_control_without_equity_is_confirmed(self) -> None:
        nodes = [{"id": "p", "type": "person"}, {"id": "t", "type": "entity", "ownership_complete": True}]
        controls = [{"person": "p", "entity": "t", "prong": "sole_director"}]
        result = resolve_candidate(graph(nodes, [], controls), "p")
        self.assertEqual(result["disposition"], "CONFIRMED_BENEFICIAL_OWNER")
        self.assertTrue(result["control_prong"])

    def test_unresolved_chain_is_review(self) -> None:
        nodes = [{"id": "p", "type": "person"}, {"id": "a", "type": "entity", "opaque": True, "ownership_complete": False},
                 {"id": "t", "type": "entity", "ownership_complete": True}]
        edges = [{"owner": "p", "owned": "a", "fraction": .10}, {"owner": "a", "owned": "t", "fraction": 1.0}]
        result = resolve_candidate(graph(nodes, edges), "p")
        self.assertEqual(result["disposition"], "REVIEW")
        self.assertFalse(result["auto_clear_eligible"])

    def test_fully_resolved_below_threshold_clears(self) -> None:
        nodes = [{"id": "p", "type": "person"}, {"id": "t", "type": "entity", "ownership_complete": True}]
        result = resolve_candidate(graph(nodes, [{"owner": "p", "owned": "t", "fraction": .10}]), "p")
        self.assertEqual(result["disposition"], "RESOLVED_BELOW_THRESHOLD")
        self.assertTrue(result["auto_clear_eligible"])

    def test_near_threshold_is_review(self) -> None:
        nodes = [{"id": "p", "type": "person"}, {"id": "t", "type": "entity", "ownership_complete": True}]
        result = resolve_candidate(graph(nodes, [{"owner": "p", "owned": "t", "fraction": .24}]), "p")
        self.assertEqual(result["disposition"], "REVIEW")

    def test_opaque_above_threshold_is_still_confirmed(self) -> None:
        nodes = [{"id": "p", "type": "person"}, {"id": "a", "type": "entity", "opaque": True, "ownership_complete": False},
                 {"id": "t", "type": "entity", "ownership_complete": True}]
        edges = [{"owner": "p", "owned": "a", "fraction": .30}, {"owner": "a", "owned": "t", "fraction": 1.0}]
        self.assertEqual(resolve_candidate(graph(nodes, edges), "p")["disposition"], "CONFIRMED_BENEFICIAL_OWNER")

    def test_nonsole_director_does_not_create_control_prong(self) -> None:
        nodes = [{"id": "p", "type": "person"}, {"id": "t", "type": "entity", "ownership_complete": True}]
        controls = [{"person": "p", "entity": "t", "prong": "director"}]
        result = resolve_candidate(graph(nodes, [], controls), "p")
        self.assertEqual(result["disposition"], "RESOLVED_BELOW_THRESHOLD")

    def test_invalid_fraction_is_rejected(self) -> None:
        nodes = [{"id": "p", "type": "person"}, {"id": "t", "type": "entity", "ownership_complete": True}]
        with self.assertRaises(ValueError):
            effective_ownership(graph(nodes, [{"owner": "p", "owned": "t", "fraction": 1.2}]), "p")


if __name__ == "__main__":
    unittest.main()
