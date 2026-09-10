"""Adversarial input-contract regressions outside the synthetic accuracy populations."""
import importlib.util
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _lib.aggregations import clamp, saturating
from _lib.ownership import resolve_candidate
from _lib.rules import Rule
from _lib.graph import address_exposure, propagate_taint
from _lib.provenance import EvidenceFact, canonical_json
from _lib.scoring import weighted_composite, band
from _lib.metrics import confusion, sweep


def load_engine(name, filename='scorer.py'):
    key = name.replace('-', '_') + '_boundaries'
    spec = importlib.util.spec_from_file_location(key, ROOT / name / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


dq = load_engine('data-quality-rules')
tm = load_engine('transaction-monitoring')
crr = load_engine('customer-risk-rating')
kyt = load_engine('onchain-kyt-address-risk')
tuning = load_engine('tm-threshold-tuning', 'engine.py')
qa = load_engine('qa-sampling', 'engine.py')


class BoundaryTests(unittest.TestCase):
    def test_zero_baseline_saturates_without_nan(self):
        self.assertEqual(saturating(float('inf'), 3), 1)
        result = tm.score_alert(tm.Alert('a', 'c', total_in=100, txn_count=2), tm.CustomerProfile('c'))
        self.assertEqual(result.decision, 'ANALYST_REVIEW')
        self.assertEqual(result.priority, 'HIGH')
        self.assertTrue(math.isfinite(result.suspicion_score))

    def test_large_finite_weights_preserve_bounded_average(self):
        self.assertEqual(weighted_composite({'x': 100}, {'x': 1e308}), 100)
        self.assertEqual(weighted_composite({'x': 100, 'y': 0}, {'x': 1e308, 'y': 1e308}), 50)
        self.assertEqual(weighted_composite({'x': 100, 'y': 20}, {'x': 1e308, 'y': 5e307}), 220 / 3)

    def test_large_finite_saturation_preserves_ratio(self):
        self.assertEqual(saturating(1e308, 1e308), .5)
        self.assertAlmostEqual(saturating(1.5e308, 1e308), .6)
        self.assertAlmostEqual(saturating(1e308, 1.5e308), .4)

    def test_shared_numeric_contracts(self):
        for call in [lambda: clamp(float('nan')), lambda: saturating(float('nan'), 3),
                     lambda: saturating(1, 0), lambda: weighted_composite({'x': 10}, {'x': -1}),
                     lambda: weighted_composite({'x': float('nan')}, {'x': 1}),
                     lambda: weighted_composite({'x': 10}, {'x': 0}),
                     lambda: band(10, [20, 10], ['LOW', 'MEDIUM', 'HIGH']),
                     lambda: band(float('nan'), [10], ['LOW', 'HIGH'])]:
            with self.subTest(call=call), self.assertRaises(ValueError):
                call()

    def test_rule_contract_rejects_truthy_strings_and_nonfinite_severity(self):
        for output in [('false', .5, ''), (True, float('nan'), ''), (True, 2, '')]:
            with self.subTest(output=output), self.assertRaises(ValueError):
                Rule('bad', lambda _: output).evaluate({})

    def test_empty_feed_cannot_pass(self):
        with self.assertRaises(ValueError):
            dq.assess_feed([])

    def test_duplicate_record_ids_cannot_hide_defects(self):
        with self.assertRaises(ValueError):
            dq.assess_feed([dq.Record('same'), dq.Record('same')])

    def test_invalid_asof_cannot_fall_back_to_default(self):
        with self.assertRaises(ValueError):
            dq.assess_feed([dq.Record('one')], asof_str='2026-02-30')

    def test_profile_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            tm.score_alert(tm.Alert('a', 'one'), tm.CustomerProfile('two'))

    def test_nonfinite_score_inputs_rejected_before_clear(self):
        for value in [float('nan'), float('inf'), '0', True]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                crr.rate(crr.Customer('c', ownership_opacity=value))
            with self.subTest(value=value), self.assertRaises(ValueError):
                kyt.score_address(kyt.AddressAlert('synthetic', 'none', value))

    def test_boolean_string_cannot_prove_broken_attribution(self):
        with self.assertRaises(ValueError):
            kyt.score_address(kyt.AddressAlert('synthetic', 'mixer', .8, hops=1,
                                               amount_fraction=.8, via_breaker='false'))

    def test_missing_completeness_is_not_confirmed_ownership(self):
        graph = {'target_entity': 't', 'nodes': [{'id': 'p', 'type': 'person'}, {'id': 't', 'type': 'entity'}],
                 'ownership_edges': [{'owner': 'p', 'owned': 't', 'fraction': .1}]}
        for value in [None, 'false', False]:
            graph['nodes'][1]['ownership_complete'] = value
            result = resolve_candidate(graph, 'p')
            self.assertEqual(result['disposition'], 'REVIEW')
            self.assertFalse(result['auto_clear_eligible'])


class GraphAndProvenanceTests(unittest.TestCase):
    def test_direct_seed_is_direct_exposure(self):
        self.assertEqual(address_exposure([], {'seed': 1}, 'seed'),
                         {'exposure': 1.0, 'hops': 0, 'seed': 'seed', 'via_breaker': False})

    def test_stronger_attributable_path_overrides_weaker_seed_label(self):
        edges = [('severe', 'target', 1.0)]
        self.assertEqual(address_exposure(edges, {'severe': 1.0, 'target': .1}, 'target', hop_decay=.6),
                         {'exposure': .6, 'hops': 1, 'seed': 'severe', 'via_breaker': False})
        self.assertEqual(address_exposure(edges, {'severe': 1.0, 'target': .8}, 'target', hop_decay=.6),
                         {'exposure': .8, 'hops': 0, 'seed': 'target', 'via_breaker': False})
        self.assertEqual(address_exposure(edges, {'severe': 1.0, 'target': .6}, 'target', hop_decay=.6),
                         {'exposure': .6, 'hops': 0, 'seed': 'target', 'via_breaker': False})

    def test_generator_edges_preserve_breaker_pass(self):
        edges = [('seed', 'exchange', 1), ('exchange', 'target', 1)]
        expected = address_exposure(edges, {'seed': 1}, 'target', {'exchange'})
        self.assertTrue(expected['via_breaker'])
        self.assertEqual(address_exposure(iter(edges), {'seed': 1}, 'target', {'exchange'}), expected)

    def test_shorter_lower_weight_path_keeps_hop_budget(self):
        edges = [('seed', 'a', 1), ('a', 'mid', 1), ('seed', 'mid', .5), ('mid', 'target', 1)]
        result = address_exposure(edges, {'seed': 1}, 'target', max_hops=2, hop_decay=1)
        self.assertEqual(result['exposure'], .5)
        self.assertEqual(result['hops'], 2)

    def test_cycle_propagation_retains_bounded_strongest_path(self):
        edges = [(a, b, 1) for a in ['seed', 'a', 'b', 'target'] for b in ['a', 'b', 'target']]
        self.assertEqual(address_exposure(edges, {'seed': 1}, 'target', max_hops=25)['hops'], 1)

    def test_bad_graph_fraction_rejected(self):
        for fraction in [-.1, 1.1, float('nan')]:
            with self.subTest(fraction=fraction), self.assertRaises(ValueError):
                propagate_taint([('seed', 'target', fraction)], {'seed': 1})

    def test_timestamp_requires_real_utc_instant(self):
        for stamp in ['not-a-time', '2026-02-30T10:00:00Z', '2026-01-01',
                      '2026-01-01T10:00:00', '2026-01-01T10:00:00-04:00']:
            fact = EvidenceFact('test', {}, 'https://example.invalid', stamp, 'a' * 64, 'synthetic')
            self.assertIn('retrieved_at_utc', fact.missing_fields())
        fact = EvidenceFact('test', {}, 'https://example.invalid', '2026-01-01T10:00:00Z', 'a' * 64, 'synthetic')
        self.assertTrue(fact.is_complete())

    def test_canonical_evidence_rejects_non_json_numbers(self):
        with self.assertRaises(ValueError):
            canonical_json({'amount': float('nan')})


class CalibrationAndSelectionTests(unittest.TestCase):
    def test_mismatched_labels_cannot_hide_false_negatives(self):
        for truth, predictions in [([1, 1], [1]), ([1], [1, 0]), ([1], ['false'])]:
            with self.subTest(truth=truth), self.assertRaises(ValueError):
                confusion(iter(truth), iter(predictions))

    def test_sweep_reuses_generator_population(self):
        rows = sweep(iter([1, 0]), iter([.8, .2]), [.1, .5])
        self.assertEqual(rows[0]['tp'] + rows[0]['tn'] + rows[0]['fp'] + rows[0]['fn'], 2)
        self.assertEqual(rows[1]['tp'], 1)
        self.assertEqual(rows[1]['tn'], 1)

    def test_recall_rounding_cannot_accept_below_floor(self):
        values = [0] * 1251 + [1] * 23749
        labels = [1] * 25000
        result = tuning.tune_rule(tuning.Rule('synthetic', 'metric', 1), values, labels,
                                  tuning.Config(recall_floor=.95, n_candidates=2))
        self.assertEqual(result.current['detection_rate'], .95)
        self.assertEqual(result.action, 'LOWER')
        self.assertEqual(result.recommended['btl_missed'], 0)

    def test_no_positive_labels_cannot_establish_safe_recall(self):
        with self.assertRaises(ValueError):
            tuning.tune_rule(tuning.Rule('synthetic', 'metric', 1), [0, 1], [0, 0])

    def test_selection_rejects_duplicated_or_misaligned_population(self):
        plan = qa.plan(qa.ControlTest('synthetic', 'test', expected_rate=0))
        for options in [dict(item_ids=['a', 'a']), dict(item_ids=['a', 'b'], strata=['one']),
                        dict(strata={'one': ['a'], 'two': ['a']})]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                qa.select(plan, **options)

    def test_nan_data_quality_ceiling_cannot_pass(self):
        with self.assertRaises(ValueError):
            dq.assess_feed([dq.Record('a')], config=dq.Config(crit_ceiling=float('nan')))


if __name__ == '__main__':
    unittest.main()
