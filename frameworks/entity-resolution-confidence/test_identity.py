from __future__ import annotations

import unittest

from _local.attest import clopper_pearson_upper
from _local.identity import compare_names, resolve_pair


class IdentityTests(unittest.TestCase):
    def test_shared_strong_identifier_is_same(self) -> None:
        result = resolve_pair({"name": "Amina Rahman", "passport": "P-1234567"},
                              {"name": "Amina Rahman", "passport": "P1234567"})
        self.assertEqual(result["disposition"], "SAME")
        self.assertTrue(result["shared_strong_identifier"])

    def test_short_shared_identifier_is_review(self) -> None:
        result = resolve_pair({"name": "Amina Rahman", "passport": "P-12"},
                              {"name": "Amina Rahman", "passport": "P12"})
        self.assertEqual(result["disposition"], "REVIEW")
        self.assertFalse(result["shared_strong_identifier"])

    def test_name_only_never_same(self) -> None:
        result = resolve_pair({"name": "John Smith"}, {"name": "John Smith"})
        self.assertEqual(result["disposition"], "REVIEW")
        self.assertFalse(result["shared_strong_identifier"])

    def test_transliteration_is_non_difference(self) -> None:
        comparison = compare_names({"name": "Mohammed Rahman"}, {"name": "Muhammad Rahman"})
        self.assertEqual(comparison["raw_score"], 1.0)
        self.assertEqual(comparison["equivalence"], "transliteration_variant")

    def test_name_order_is_non_difference(self) -> None:
        comparison = compare_names({"name": "Wei Zhang"}, {"name": "Zhang, Wei"})
        self.assertEqual(comparison["raw_score"], 1.0)
        self.assertEqual(comparison["equivalence"], "name_order_swap")

    def test_partial_dob_is_review(self) -> None:
        result = resolve_pair({"name": "Maria Garcia", "dob": "1984-05-17"},
                              {"name": "Maria Garcia", "dob": "1984-05"})
        self.assertEqual(result["disposition"], "REVIEW")

    def test_dob_transposition_is_quality_flag(self) -> None:
        result = resolve_pair({"name": "Sofia Miller", "dob": "1984-05-17"},
                              {"name": "Sofia Miller", "dob": "1984-50-17"})
        self.assertEqual(result["disposition"], "REVIEW")
        self.assertTrue(result["quality_flags"])

    def test_clean_strong_conflict_is_different(self) -> None:
        result = resolve_pair({"name": "John Smith", "national_id": "NID123456"},
                              {"name": "John Smith", "national_id": "NID987654"})
        self.assertEqual(result["disposition"], "DIFFERENT")

    def test_conflicting_strong_evidence_is_review(self) -> None:
        result = resolve_pair({"name": "Amina Rahman", "passport": "P123456", "tax_id": "T111111"},
                              {"name": "Amina Rahman", "passport": "P123456", "tax_id": "T999999"})
        self.assertEqual(result["disposition"], "REVIEW")

    def test_common_name_score_is_capped(self) -> None:
        comparison = compare_names({"name": "John Smith"}, {"name": "John Smith"})
        self.assertLessEqual(comparison["score"], 0.45)

    def test_exact_bound_for_zero_events(self) -> None:
        upper = clopper_pearson_upper(0, 100, 0.95)
        self.assertAlmostEqual(upper, 1 - 0.05 ** (1 / 100), places=12)


if __name__ == "__main__":
    unittest.main()
