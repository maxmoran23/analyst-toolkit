"""Analytic and rejected-input regressions for the remaining quant primitives."""
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import correlation
import drawdown
import monte_carlo
import sharpe
import vol


class SeriesContracts(unittest.TestCase):
    def test_sample_volatility_and_downside_hand_math(self):
        self.assertAlmostEqual(vol.realized_vol([.1, -.1], 1), math.sqrt(.02))
        self.assertEqual(sharpe.stdev([.01] * 30), 0)
        self.assertAlmostEqual(sharpe.downside_stdev([-.1, .1]), math.sqrt(.005))
        self.assertAlmostEqual(vol.ewma_vol([.1, -.2], 0, 1), .2)
        self.assertAlmostEqual(vol.ewma_vol([.1, -.2], 1, 1), .1)

    def test_sample_sizes_frequency_and_types(self):
        for fn, args in [(vol.realized_vol, ([],)), (vol.realized_vol, ([.1],)),
                         (vol.ewma_vol, ([],)), (sharpe.stdev, ([.1],)),
                         (sharpe.stdev, ([1, 2], 2)), (sharpe.stdev, ([1, 2], True)),
                         (sharpe.downside_stdev, ([True],))]:
            with self.subTest(fn=fn.__name__, args=args), self.assertRaises(ValueError):
                fn(*args)
        for annualize in [0, -1, 2.5, True]:
            with self.subTest(annualize=annualize), self.assertRaises(ValueError):
                vol.realized_vol([.1, -.1], annualize)

    def test_volatility_finite_and_parameter_domains(self):
        for value in [float('nan'), float('inf'), True, '0.1']:
            for fn in [vol.realized_vol, vol.ewma_vol]:
                with self.subTest(fn=fn.__name__, value=value), self.assertRaises(ValueError):
                    fn([value, .1])
        for lam in [-.1, 1.01, float('nan')]:
            with self.assertRaises(ValueError):
                vol.ewma_vol([.1], lam)

    def test_ohlc_invalid_bars_are_rejected_instead_of_diluting_estimate(self):
        self.assertAlmostEqual(vol.parkinson_vol([(math.e, 1)], 1), math.sqrt(1 / (4 * math.log(2))))
        self.assertAlmostEqual(vol.garman_klass_vol([(1, math.e, 1, 1)], 1), math.sqrt(.5))
        for pairs in [[], [(2, 0)], [(1, 2)], [(float('inf'), 1)]]:
            with self.subTest(pairs=pairs), self.assertRaises(ValueError):
                vol.parkinson_vol(pairs)
        for bars in [[], [(0, 2, 1, 1)], [(3, 2, 1, 1)], [(1, 2, 1, .9)]]:
            with self.subTest(bars=bars), self.assertRaises(ValueError):
                vol.garman_klass_vol(bars)

    def test_garch_stationarity_and_fixed_point(self):
        expected = round(.01 * math.sqrt(252) * 100, 3)
        self.assertEqual(vol.simple_garch([.01] * 20)['garch_annualized_vol_pct'], expected)
        for kwargs in [dict(alpha=-.1), dict(beta=-.1), dict(alpha=.2, beta=.8), dict(omega=-.1), dict(annualize=0)]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                vol.simple_garch([.01] * 20, **kwargs)
        with self.assertRaises(ValueError):
            vol.simple_garch([.1] * 19)

    def test_drawdown_complete_loss_and_invalid_equity(self):
        self.assertEqual(drawdown.equity_from_returns([-.5, -1, .2]), [1, .5, 0, 0])
        self.assertEqual(drawdown.drawdown_series([100, 0, 0]), [0, 1, 1])
        self.assertEqual(drawdown.recovery_episodes([100, 0])[-1]['dd_pct'], 100)
        for equity in [[], [0], [-1, -2], [100, -1], [100, float('nan')]]:
            for fn in [drawdown.drawdown_series, drawdown.recovery_episodes]:
                with self.subTest(equity=equity, fn=fn.__name__), self.assertRaises(ValueError):
                    fn(equity)
        for returns in [[], [-1.01], [True]]:
            with self.assertRaises(ValueError):
                drawdown.equity_from_returns(returns)
        with self.assertRaises(ValueError):
            drawdown.equity_from_returns([.1], start=0)

    def test_recovery_is_in_observation_periods(self):
        episode = drawdown.recovery_episodes([100, 120, 90, 130])[0]
        self.assertEqual((episode['dd_pct'], episode['duration_to_recovery']), (25, 2))

    def test_correlation_alignment_and_zero_variance_convention(self):
        self.assertAlmostEqual(correlation.corr([1, 2, 3], [6, 4, 2]), -1)
        self.assertEqual(correlation.corr([1, 2, 3], [5, 5, 5]), 0)
        for x, y in [([1, 2], [1]), ([1], [1, 2]), ([1, float('nan')], [1, 2]), ([True, 2], [1, 2])]:
            with self.subTest(x=x, y=y), self.assertRaises(ValueError):
                correlation.corr(x, y)

    def test_csv_bad_rows_are_never_silently_dropped(self):
        self.assertEqual(correlation.parse_returns_csv(io.StringIO('a,b\n\n"1","2"\n3,4\n')), [[1, 2], [3, 4]])
        for text in ['a,b\n', '1,2\n', '1,2\n3\n', 'a,b\n1,2\nbad,row\n3,4', '1,2\nNaN,4', '1,2\n3,inf', 'a,2\n1,2\n3,4']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                correlation.parse_returns_csv(io.StringIO(text))

    def test_simulation_zero_horizon_and_deterministic_path(self):
        self.assertEqual(monte_carlo.gbm_path(100, .05, .2, 0), [100])
        self.assertEqual(monte_carlo.gbm_path(100, 0, 0, 3), [100] * 4)
        self.assertAlmostEqual(monte_carlo.gbm_path(100, .1, 0, 2, dt=.5)[-1], 100 * math.exp(.1))

    def test_simulation_rejects_invalid_domains_before_rng(self):
        for kwargs in [dict(spot=0), dict(spot=-1), dict(vol=-.1), dict(drift=float('nan')), dict(days=-1), dict(days=1.2), dict(dt=0), dict(days=True)]:
            args = dict(spot=100, drift=0, vol=.1, days=1)
            args.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                monte_carlo.gbm_path(**args)
        for kwargs in [dict(jump_intensity=-1), dict(jump_intensity=366), dict(jump_vol=-.1), dict(jump_mean=float('inf'))]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                monte_carlo.jump_gbm_path(100, 0, .1, 1, **kwargs)

    def test_percentile_floor_index_and_input_domain(self):
        self.assertEqual(monte_carlo.percentile([1, 2, 3, 4], .5), 3)
        self.assertEqual(monte_carlo.percentile([1, 2, 3, 4], 1), 4)
        for values, p in [([], .5), ([1], -.1), ([1], 1.1), ([2, 1], .5), ([float('nan')], .5)]:
            with self.subTest(values=values, p=p), self.assertRaises(ValueError):
                monte_carlo.percentile(values, p)

    def test_extreme_ohlc_does_not_silently_report_zero(self):
        value = vol.garman_klass_vol([(1e-308, 1e308, 1e-308, 1e308)], 1)
        self.assertTrue(math.isfinite(value))
        self.assertGreater(value, 0)
        with self.assertRaises(ValueError):
            sharpe.downside_stdev([-1e308], 1e308)

    def test_constant_crisis_subset_has_no_compression(self):
        self.assertIsNone(correlation.correlation_value([-.125] * 6, [-.25] * 6))
        root = Path(__file__).parent
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'crisis.csv'
            path.write_text('-.125,-.25\n' * 6 + '.125,.25\n.25,.5\n')
            result = subprocess.run([sys.executable, str(root / 'correlation.py'), '--returns-csv', str(path)], capture_output=True, text=True, check=True)
            output = json.loads(result.stdout)
            self.assertIsNone(output['crisis_correlation']['a0__a1'])
            self.assertEqual(output['correlation_compression'], {})

    def test_nonconstant_underflow_is_not_a_zero_correlation(self):
        with self.assertRaises(ValueError):
            correlation.corr([1e-200, 2e-200], [1e-200, 2e-200])

    def test_markowitz_accepts_single_asset_but_rejects_malformed_rows(self):
        root = Path(__file__).parent
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'single.csv'
            path.write_text('asset\n0.01\n0.02\n-0.01\n')
            command = [sys.executable, str(root / 'markowitz.py'), '--returns-csv', str(path)]
            good = subprocess.run(command, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(good.stdout)['n_assets'], 1)
            path.write_text('asset\n0.01\nbad\n0.02\n-0.01\n')
            self.assertNotEqual(subprocess.run(command, capture_output=True, text=True).returncode, 0)

    def test_cli_rejects_false_success_and_invalid_labels(self):
        root = Path(__file__).parent
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / 'returns.json'
            data.write_text(json.dumps([.01] * 5))
            csv_file = Path(directory) / 'returns.csv'
            csv_file.write_text('1,2\n3,4\n')
            commands = [
                ['vol.py', '--returns-json', str(data), '--method', 'garch'],
                ['monte_carlo.py', '--spot', '100', '--vol', '.1', '--paths', '0'],
                ['correlation.py', '--returns-csv', str(csv_file), '--window', '0'],
                ['correlation.py', '--returns-csv', str(csv_file), '--asset-names', 'a,a'],
                ['correlation.py', '--returns-csv', str(csv_file), '--asset-names', 'a,b,c'],
                ['drawdown.py', '--returns-json', str(data), '--top-n', '-1'],
            ]
            data.write_text(json.dumps([.01] * 30))
            commands.extend([
                ['sharpe.py', '--returns-json', str(data), '--annualize', '0'],
                ['sharpe.py', '--returns-json', str(data), '--rf', '-1'],
            ])
            for command in commands:
                if command[0] == 'vol.py':
                    data.write_text('[0.01]')
                else:
                    data.write_text(json.dumps([.01] * 30))
                result = subprocess.run([sys.executable, str(root / command[0]), *command[1:]], capture_output=True, text=True)
                with self.subTest(command=command):
                    self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
