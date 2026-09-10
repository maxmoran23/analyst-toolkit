"""Analytic and adversarial regressions for quant input and numerical contracts."""
import math
import unittest
from statistics import NormalDist

try:
    from . import kelly, dcf, var, markowitz
except ImportError:
    import kelly, dcf, var, markowitz


class QuantRegressions(unittest.TestCase):
    def test_kelly_closed_form(self):
        self.assertAlmostEqual(kelly.kelly_single(.55, 2), .1)
        self.assertEqual(kelly.kelly_single(.4, 2), 0)

    def test_kelly_invalid_inputs(self):
        for probability, odds in [(1.1, 2), (-.1, 2), (.5, 1), (.5, float('inf')), (float('nan'), 2), (True, 2)]:
            with self.subTest(p=probability, odds=odds), self.assertRaises(ValueError):
                kelly.kelly_single(probability, odds)

    def test_correlation_haircut_uses_actual_off_diagonal_count(self):
        bets = [{'label': x, 'p': .6, 'odds': 2} for x in 'abc']
        result = kelly.kelly_portfolio(bets, corr_matrix={'a': {'b': .4, 'c': .4}})
        self.assertEqual(result['bets'][0]['correlation_shrink'], .8)

    def test_negative_correlations_never_increase_capped_exposure(self):
        bets = [{'label': x, 'p': 1, 'odds': 2} for x in 'abc']
        result = kelly.kelly_portfolio(bets, fraction=1, corr_matrix={'a': {'b': -1}, 'b': {'a': -1}})
        self.assertLessEqual(result['total_exposure_pct'], 50)
        self.assertLessEqual(sum(x['fractional_kelly_pct'] for x in result['bets']), 50)

    def test_bad_correlation_matrix_rejected(self):
        bets = [{'label': x, 'p': .6, 'odds': 2} for x in 'ab']
        for matrix in [{'a': {'a': 0}}, {'a': {'b': 2}}, {'a': {'b': .1}, 'b': {'a': .2}}]:
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                kelly.kelly_portfolio(bets, corr_matrix=matrix)

    def test_dcf_constant_perpetuity_identity(self):
        self.assertEqual(dcf.dcf([100], .1, 0, 100)['enterprise_value'], 1000)

    def test_dcf_invalid_perpetuity_is_not_zero(self):
        for fees, discount, growth, supply in [([], .1, 0, 100), ([100], .1, .1, 100),
                ([100], .1, .2, 100), ([100], .1, 0, 0), ([float('nan')], .1, 0, 100)]:
            with self.subTest(fees=fees, discount=discount), self.assertRaises(ValueError):
                dcf.dcf(fees, discount, growth, supply)

    def test_gaussian_quantile_handles_arbitrary_confidence(self):
        returns = [-1, 0, 1]
        for confidence in [.8, .95, .987, .9999]:
            value, es = var.parametric_var(returns, confidence)
            z = NormalDist().inv_cdf(confidence)
            self.assertAlmostEqual(value, z, places=12)
            self.assertAlmostEqual(es, math.exp(-z*z/2)/math.sqrt(2*math.pi)/(1-confidence), places=12)
            self.assertGreaterEqual(es, value)

    def test_var_invalid_inputs(self):
        for fn in [var.historical_var, var.parametric_var]:
            for returns, confidence in [([], .95), ([0, 1], 1), ([0, 1], 0), ([0, float('nan')], .95)]:
                with self.subTest(fn=fn.__name__), self.assertRaises(ValueError):
                    fn(returns, confidence)

    def test_linear_solver_solves_original_system(self):
        result = markowitz.solve_linear([[2, 1], [1, 3]], [1, 2])
        self.assertAlmostEqual(2*result[0] + result[1], 1)
        self.assertAlmostEqual(result[0] + 3*result[1], 2)

    def test_invalid_covariance_not_silently_regularized(self):
        for matrix in [[[1, 1], [1, 1]], [[1, 2], [2, 1]], [[1, 0], [1, 1]], [[float('nan')]]]:
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                markowitz.cholesky(matrix)

    def test_min_variance_diagonal_analytic_weights(self):
        self.assertEqual(markowitz.min_variance_portfolio([[1, 0], [0, 4]]), [.8, .2])

    def test_negative_tangency_normalization_is_not_max_sharpe(self):
        self.assertIsNone(markowitz.max_sharpe_portfolio([[1, 0], [0, 1]], [-.1, -.2]))


if __name__ == '__main__':
    unittest.main()
