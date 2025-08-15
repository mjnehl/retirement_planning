"""Unit tests for advanced Monte Carlo simulations"""

import unittest
import numpy as np
from decimal import Decimal
import sys
sys.path.append('../src')
from core.monte_carlo_advanced import AdvancedMonteCarloSimulator, MonteCarloResults


class TestAdvancedMonteCarloSimulator(unittest.TestCase):
    """Test advanced Monte Carlo simulation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.simulator = AdvancedMonteCarloSimulator(num_simulations=1000, random_seed=42)
    
    def test_portfolio_simulation_basic(self):
        """Test basic portfolio simulation"""
        results = self.simulator.simulate_portfolio_returns(
            initial_value=100000,
            expected_return=0.07,
            volatility=0.15,
            years=10
        )
        
        # Check result structure
        self.assertIsInstance(results, MonteCarloResults)
        self.assertIsNotNone(results.mean_outcome)
        self.assertIsNotNone(results.median_outcome)
        self.assertIsNotNone(results.std_deviation)
        self.assertIsNotNone(results.success_rate)
        
        # Check confidence intervals
        self.assertIn(95, results.confidence_intervals)
        ci_95 = results.confidence_intervals[95]
        self.assertLess(ci_95[0], ci_95[1])
        
        # Check percentiles
        self.assertIn(50, results.percentiles)
        self.assertAlmostEqual(results.percentiles[50], results.median_outcome, places=0)
    
    def test_portfolio_with_contributions(self):
        """Test portfolio simulation with contributions"""
        results = self.simulator.simulate_portfolio_returns(
            initial_value=50000,
            expected_return=0.08,
            volatility=0.16,
            years=20,
            annual_contribution=5000,
            inflation_rate=0.03
        )
        
        # Should generally have higher final value with contributions
        self.assertGreater(results.mean_outcome, 50000)
        self.assertEqual(results.success_rate, 1.0)  # No withdrawals, should always succeed
    
    def test_retirement_withdrawal_simulation(self):
        """Test retirement withdrawal simulation"""
        results = self.simulator.simulate_retirement_scenarios(
            portfolio_value=1000000,
            withdrawal_rate=0.04,
            expected_return=0.06,
            volatility=0.12,
            years=30,
            inflation_rate=0.025,
            tax_rate=0.20
        )
        
        # Check success rate is reasonable
        self.assertGreaterEqual(results.success_rate, 0)
        self.assertLessEqual(results.success_rate, 1)
        
        # Check risk metrics
        self.assertIsNotNone(results.value_at_risk)
        self.assertIsNotNone(results.conditional_value_at_risk)
        self.assertLessEqual(results.value_at_risk, results.median_outcome)
    
    def test_risk_metrics_calculation(self):
        """Test calculation of risk metrics"""
        results = self.simulator.simulate_portfolio_returns(
            initial_value=100000,
            expected_return=0.07,
            volatility=0.15,
            years=10,
            annual_withdrawal=4000
        )
        
        # Check Sharpe ratio calculation
        self.assertIsNotNone(results.sharpe_ratio)
        
        # Check Sortino ratio
        self.assertIsNotNone(results.sortino_ratio)
        
        # Check max drawdown
        self.assertIsNotNone(results.max_drawdown)
        self.assertLess(results.max_drawdown, 0)  # Drawdown should be negative
    
    def test_confidence_intervals(self):
        """Test confidence interval calculations"""
        results = self.simulator.simulate_portfolio_returns(
            initial_value=100000,
            expected_return=0.07,
            volatility=0.15,
            years=10
        )
        
        # Check multiple confidence levels
        for level in [90, 95, 99]:
            self.assertIn(level, results.confidence_intervals)
            ci = results.confidence_intervals[level]
            
            # Higher confidence level should have wider interval
            if level > 90:
                ci_90 = results.confidence_intervals[90]
                self.assertLessEqual(ci[0], ci_90[0])
                self.assertGreaterEqual(ci[1], ci_90[1])
    
    def test_percentile_calculations(self):
        """Test percentile calculations"""
        results = self.simulator.simulate_portfolio_returns(
            initial_value=100000,
            expected_return=0.07,
            volatility=0.15,
            years=10
        )
        
        # Check percentiles are in order
        percentile_values = [results.percentiles[p] for p in sorted(results.percentiles.keys())]
        for i in range(len(percentile_values) - 1):
            self.assertLessEqual(percentile_values[i], percentile_values[i + 1])
    
    def test_summary_generation(self):
        """Test summary report generation"""
        results = self.simulator.simulate_portfolio_returns(
            initial_value=100000,
            expected_return=0.07,
            volatility=0.15,
            years=10,
            annual_withdrawal=4000
        )
        
        summary = results.get_summary()
        
        # Check summary contains key information
        self.assertIn('Success Rate', summary)
        self.assertIn('Mean Outcome', summary)
        self.assertIn('Median Outcome', summary)
        self.assertIn('Confidence Intervals', summary)
        self.assertIn('Risk Metrics', summary)
        self.assertIn('Value at Risk', summary)
    
    def test_sensitivity_analysis(self):
        """Test sensitivity analysis functionality"""
        base_params = {
            'expected_return': 0.07,
            'volatility': 0.15,
            'withdrawal': 40000,
            'inflation': 0.03
        }
        
        param_ranges = {
            'expected_return': (0.04, 0.10),
            'volatility': (0.10, 0.25),
            'withdrawal': (30000, 50000)
        }
        
        results_df = self.simulator.sensitivity_analysis(
            base_params=base_params,
            param_ranges=param_ranges,
            portfolio_value=1000000,
            years=30
        )
        
        # Check DataFrame structure
        self.assertGreater(len(results_df), 0)
        self.assertIn('parameter', results_df.columns)
        self.assertIn('value', results_df.columns)
        self.assertIn('success_rate', results_df.columns)
        self.assertIn('median_outcome', results_df.columns)
        
        # Check all parameters were tested
        for param in param_ranges.keys():
            param_results = results_df[results_df['parameter'] == param]
            self.assertEqual(len(param_results), 5)  # 5 test values per parameter
    
    def test_zero_volatility(self):
        """Test simulation with zero volatility (deterministic)"""
        results = self.simulator.simulate_portfolio_returns(
            initial_value=100000,
            expected_return=0.05,
            volatility=0,  # No randomness
            years=10
        )
        
        # With zero volatility, all simulations should be identical
        self.assertAlmostEqual(results.std_deviation, 0, places=2)
        self.assertAlmostEqual(results.mean_outcome, results.median_outcome, places=2)
    
    def test_extreme_scenarios(self):
        """Test extreme market scenarios"""
        # High volatility scenario
        high_vol_results = self.simulator.simulate_portfolio_returns(
            initial_value=100000,
            expected_return=0.07,
            volatility=0.40,  # Very high volatility
            years=10
        )
        
        # Low volatility scenario
        low_vol_results = self.simulator.simulate_portfolio_returns(
            initial_value=100000,
            expected_return=0.07,
            volatility=0.05,  # Very low volatility
            years=10
        )
        
        # High volatility should have wider distribution
        self.assertGreater(high_vol_results.std_deviation, low_vol_results.std_deviation)
        
        # Confidence intervals should be wider for high volatility
        high_vol_ci = high_vol_results.confidence_intervals[95]
        low_vol_ci = low_vol_results.confidence_intervals[95]
        high_vol_range = high_vol_ci[1] - high_vol_ci[0]
        low_vol_range = low_vol_ci[1] - low_vol_ci[0]
        self.assertGreater(high_vol_range, low_vol_range)


if __name__ == '__main__':
    unittest.main()