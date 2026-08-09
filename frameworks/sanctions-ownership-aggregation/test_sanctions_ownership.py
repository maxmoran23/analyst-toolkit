from __future__ import annotations

import unittest

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from _lib.sanctions_ownership import resolve_candidate


def node(node_id, kind, **flags):
    return {"id": node_id, "type": kind, **flags}


def graph(nodes, edges, sanctioned, controls=None):
    return {"nodes": nodes, "ownership_edges": edges, "sanctioned_parties": sanctioned,
            "control_relationships": controls or [], "candidates": ["target"]}


class SanctionsOwnershipTests(unittest.TestCase):
    def test_two_owner_aggregation_blocks(self) -> None:
        nodes = [node("s1", "person"), node("s2", "person"), node("target", "entity", ownership_complete=True)]
        edges = [{"owner": "s1", "owned": "target", "fraction": .30},
                 {"owner": "s2", "owned": "target", "fraction": .25}]
        result = resolve_candidate(graph(nodes, edges, ["s1", "s2"]), "target")
        self.assertEqual(result["disposition"], "BLOCKED_BY_OWNERSHIP")
        self.assertFalse(result["individual_blocker"])
        self.assertAlmostEqual(result["aggregate_sanctioned_ownership"], .55)

    def test_three_shell_slices_block(self) -> None:
        nodes = [node("s1", "person"), *(node(f"h{i}", "entity", ownership_complete=True) for i in range(3)),
                 node("target", "entity", ownership_complete=True)]
        edges = []
        for i in range(3):
            edges.extend([{"owner": "s1", "owned": f"h{i}", "fraction": 1.0},
                          {"owner": f"h{i}", "owned": "target", "fraction": .18}])
        result = resolve_candidate(graph(nodes, edges, ["s1"]), "target")
        self.assertEqual(result["disposition"], "BLOCKED_BY_OWNERSHIP")
        self.assertAlmostEqual(result["aggregate_sanctioned_ownership"], .54)

    def test_circular_ownership_blocks(self) -> None:
        nodes = [node("s1", "person"), node("a", "entity", ownership_complete=True),
                 node("b", "entity", ownership_complete=True), node("target", "entity", ownership_complete=True)]
        edges = [{"owner": "s1", "owned": "a", "fraction": .40},
                 {"owner": "a", "owned": "target", "fraction": 1.0},
                 {"owner": "a", "owned": "b", "fraction": .50},
                 {"owner": "b", "owned": "a", "fraction": .50}]
        result = resolve_candidate(graph(nodes, edges, ["s1"]), "target")
        self.assertEqual(result["disposition"], "BLOCKED_BY_OWNERSHIP")
        self.assertAlmostEqual(result["aggregate_sanctioned_ownership"], .533333333333, places=9)

    def test_path_evidence_contains_full_chain(self) -> None:
        nodes = [node("s1", "person"), node("h", "entity", ownership_complete=True),
                 node("target", "entity", ownership_complete=True)]
        edges = [{"owner": "s1", "owned": "h", "fraction": 1.0},
                 {"owner": "h", "owned": "target", "fraction": .55}]
        result = resolve_candidate(graph(nodes, edges, ["s1"]), "target")
        paths = result["sanctioned_owner_evidence"][0]["path_evidence"]["paths"]
        self.assertEqual(paths[0]["nodes"], ["s1", "h", "target"])
        self.assertAlmostEqual(paths[0]["contribution"], .55)

    def test_resolved_under_25_clears(self) -> None:
        nodes = [node("s1", "person"), node("target", "entity", ownership_complete=True)]
        result = resolve_candidate(graph(nodes, [{"owner": "s1", "owned": "target", "fraction": .20}], ["s1"]), "target")
        self.assertEqual(result["disposition"], "NOT_BLOCKED_BY_OWNERSHIP")
        self.assertTrue(result["auto_clear_eligible"])

    def test_25_to_50_is_review(self) -> None:
        nodes = [node("s1", "person"), node("target", "entity", ownership_complete=True)]
        result = resolve_candidate(graph(nodes, [{"owner": "s1", "owned": "target", "fraction": .30}], ["s1"]), "target")
        self.assertEqual(result["disposition"], "REVIEW")

    def test_near_50_flag(self) -> None:
        nodes = [node("s1", "person"), node("target", "entity", ownership_complete=True)]
        result = resolve_candidate(graph(nodes, [{"owner": "s1", "owned": "target", "fraction": .49}], ["s1"]), "target")
        self.assertEqual(result["disposition"], "REVIEW")
        self.assertTrue(result["near_threshold"])

    def test_unresolved_chain_is_review(self) -> None:
        nodes = [node("s1", "person"), node("h", "entity", ownership_complete=False, opaque=True),
                 node("target", "entity", ownership_complete=True)]
        edges = [{"owner": "s1", "owned": "h", "fraction": 1.0},
                 {"owner": "h", "owned": "target", "fraction": .10}]
        result = resolve_candidate(graph(nodes, edges, ["s1"]), "target")
        self.assertEqual(result["disposition"], "REVIEW")
        self.assertFalse(result["auto_clear_eligible"])

    def test_sanctioned_control_without_equity_is_review(self) -> None:
        nodes = [node("s1", "person"), node("target", "entity", ownership_complete=True)]
        controls = [{"person": "s1", "entity": "target", "prong": "sole_director"}]
        result = resolve_candidate(graph(nodes, [], ["s1"], controls), "target")
        self.assertEqual(result["disposition"], "REVIEW")
        self.assertTrue(result["sanctioned_control_prong"])

    def test_nonsanctioned_ownership_is_ignored(self) -> None:
        nodes = [node("s1", "person"), node("other", "person"), node("target", "entity", ownership_complete=True)]
        edges = [{"owner": "s1", "owned": "target", "fraction": .10},
                 {"owner": "other", "owned": "target", "fraction": .80}]
        result = resolve_candidate(graph(nodes, edges, ["s1"]), "target")
        self.assertEqual(result["disposition"], "NOT_BLOCKED_BY_OWNERSHIP")

    def test_unknown_candidate_is_rejected(self) -> None:
        nodes = [node("s1", "person"), node("target", "entity", ownership_complete=True)]
        with self.assertRaises(ValueError):
            resolve_candidate(graph(nodes, [], ["s1"]), "missing")


if __name__ == "__main__":
    unittest.main()
