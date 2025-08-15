"""Advanced Monte Carlo simulation with confidence intervals and analytics"""

import numpy as np
from decimal import Decimal
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from scipy import stats
import pandas as pd


@dataclass
class MonteCarloResults:
    """Results from Monte Carlo simulation with detailed analytics"""
    simulations: np.ndarray
    success_rate: float
    mean_outcome: float
    median_outcome: float
    std_deviation: float
    confidence_intervals: Dict[int, Tuple[float, float]]
    percentiles: Dict[int, float]
    value_at_risk: float  # VaR at 95% confidence
    conditional_value_at_risk: float  # CVaR
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    
    def get_summary(self) -> str:
        """Get formatted summary of results"""
        summary = [
            f"Monte Carlo Simulation Results",
            f"=" * 40,
            f"Success Rate: {self.success_rate:.1%}",
            f"Mean Outcome: ${self.mean_outcome:,.0f}",
            f"Median Outcome: ${self.median_outcome:,.0f}",
            f"Std Deviation: ${self.std_deviation:,.0f}",
            f"",
            f"Confidence Intervals:",
        ]
        
        for ci_level, (lower, upper) in self.confidence_intervals.items():
            summary.append(f"  {ci_level}%: ${lower:,.0f} - ${upper:,.0f}")
        
        summary.extend([
            f"",
            f"Risk Metrics:",
            f"  Value at Risk (95%): ${self.value_at_risk:,.0f}",
            f"  Conditional VaR: ${self.conditional_value_at_risk:,.0f}",
        ])
        
        if self.sharpe_ratio is not None:
            summary.append(f"  Sharpe Ratio: {self.sharpe_ratio:.3f}")
        if self.sortino_ratio is not None:
            summary.append(f"  Sortino Ratio: {self.sortino_ratio:.3f}")
        if self.max_drawdown is not None:
            summary.append(f"  Max Drawdown: {self.max_drawdown:.1%}")
        
        return "\n".join(summary)


class AdvancedMonteCarloSimulator:
    """Advanced Monte Carlo simulator with comprehensive analytics"""
    
    def __init__(self, num_simulations: int = 10000, random_seed: Optional[int] = None):
        self.num_simulations = num_simulations
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def simulate_portfolio_returns(self, 
                                  initial_value: float,
                                  expected_return: float,
                                  volatility: float,
                                  years: int,
                                  annual_contribution: float = 0,
                                  annual_withdrawal: float = 0,
                                  inflation_rate: float = 0.03) -> MonteCarloResults:
        """
        Simulate portfolio returns with contributions and withdrawals
        
        Args:
            initial_value: Starting portfolio value
            expected_return: Annual expected return
            volatility: Annual volatility (standard deviation)
            years: Number of years to simulate
            annual_contribution: Annual contribution amount
            annual_withdrawal: Annual withdrawal amount
            inflation_rate: Annual inflation rate
        
        Returns:
            MonteCarloResults with detailed analytics
        """
        results = np.zeros((self.num_simulations, years + 1))
        results[:, 0] = initial_value
        
        for sim in range(self.num_simulations):
            for year in range(1, years + 1):
                # Generate random return
                annual_return = np.random.normal(expected_return, volatility)
                
                # Apply inflation adjustment
                inflation_adjusted_contribution = annual_contribution * ((1 + inflation_rate) ** year)
                inflation_adjusted_withdrawal = annual_withdrawal * ((1 + inflation_rate) ** year)
                
                # Calculate new value
                prev_value = results[sim, year - 1]
                new_value = prev_value * (1 + annual_return)
                new_value += inflation_adjusted_contribution
                new_value -= inflation_adjusted_withdrawal
                
                # Don't allow negative values
                results[sim, year] = max(0, new_value)
        
        # Extract final values
        final_values = results[:, -1]
        
        return self._analyze_results(final_values, results, annual_withdrawal > 0)
    
    def simulate_retirement_scenarios(self,
                                    portfolio_value: float,
                                    withdrawal_rate: float,
                                    expected_return: float,
                                    volatility: float,
                                    years: int,
                                    inflation_rate: float = 0.03,
                                    tax_rate: float = 0.20) -> MonteCarloResults:
        """
        Simulate retirement withdrawal scenarios
        
        Args:
            portfolio_value: Starting portfolio value
            withdrawal_rate: Annual withdrawal rate (e.g., 0.04 for 4%)
            expected_return: Expected annual return
            volatility: Annual volatility
            years: Number of retirement years
            inflation_rate: Annual inflation rate
            tax_rate: Effective tax rate on withdrawals
        
        Returns:
            MonteCarloResults with retirement-specific metrics
        """
        results = np.zeros((self.num_simulations, years + 1))
        results[:, 0] = portfolio_value
        success_count = 0
        
        for sim in range(self.num_simulations):
            initial_withdrawal = portfolio_value * withdrawal_rate
            
            for year in range(1, years + 1):
                # Generate random return
                annual_return = np.random.normal(expected_return, volatility)
                
                # Calculate inflation-adjusted withdrawal
                withdrawal = initial_withdrawal * ((1 + inflation_rate) ** year)
                
                # Apply tax
                gross_withdrawal = withdrawal / (1 - tax_rate)
                
                # Update portfolio value
                prev_value = results[sim, year - 1]
                if prev_value > gross_withdrawal:
                    new_value = (prev_value - gross_withdrawal) * (1 + annual_return)
                    results[sim, year] = max(0, new_value)
                else:
                    results[sim, year] = 0
            
            # Check if portfolio survived
            if results[sim, -1] > 0:
                success_count += 1
        
        final_values = results[:, -1]
        success_rate = success_count / self.num_simulations
        
        return self._analyze_results(final_values, results, True, success_rate)
    
    def _analyze_results(self, 
                        final_values: np.ndarray,
                        full_results: np.ndarray,
                        is_retirement: bool = False,
                        success_rate: Optional[float] = None) -> MonteCarloResults:
        """Analyze simulation results and calculate metrics"""
        
        # Basic statistics
        mean_outcome = np.mean(final_values)
        median_outcome = np.median(final_values)
        std_deviation = np.std(final_values)
        
        # Success rate (portfolio > 0 at end)
        if success_rate is None:
            success_rate = np.sum(final_values > 0) / len(final_values)
        
        # Confidence intervals
        confidence_intervals = {
            90: self._calculate_confidence_interval(final_values, 0.90),
            95: self._calculate_confidence_interval(final_values, 0.95),
            99: self._calculate_confidence_interval(final_values, 0.99)
        }
        
        # Percentiles
        percentiles = {
            5: np.percentile(final_values, 5),
            10: np.percentile(final_values, 10),
            25: np.percentile(final_values, 25),
            50: np.percentile(final_values, 50),
            75: np.percentile(final_values, 75),
            90: np.percentile(final_values, 90),
            95: np.percentile(final_values, 95)
        }
        
        # Risk metrics
        value_at_risk = np.percentile(final_values, 5)  # 95% confidence VaR
        conditional_value_at_risk = np.mean(final_values[final_values <= value_at_risk])
        
        # Calculate returns for ratio metrics
        if full_results.shape[1] > 1:
            returns = np.diff(full_results, axis=1) / full_results[:, :-1]
            returns = returns[~np.isnan(returns).any(axis=1)]  # Remove NaN rows
            
            if len(returns) > 0:
                mean_return = np.mean(returns)
                return_std = np.std(returns)
                
                # Sharpe ratio (assuming risk-free rate of 3%)
                risk_free_rate = 0.03
                sharpe_ratio = (mean_return - risk_free_rate) / return_std if return_std > 0 else 0
                
                # Sortino ratio (downside deviation)
                downside_returns = returns[returns < 0]
                downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
                sortino_ratio = (mean_return - risk_free_rate) / downside_std if downside_std > 0 else 0
                
                # Maximum drawdown
                max_drawdown = self._calculate_max_drawdown(full_results)
            else:
                sharpe_ratio = sortino_ratio = max_drawdown = None
        else:
            sharpe_ratio = sortino_ratio = max_drawdown = None
        
        return MonteCarloResults(
            simulations=final_values,
            success_rate=success_rate,
            mean_outcome=mean_outcome,
            median_outcome=median_outcome,
            std_deviation=std_deviation,
            confidence_intervals=confidence_intervals,
            percentiles=percentiles,
            value_at_risk=value_at_risk,
            conditional_value_at_risk=conditional_value_at_risk,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown
        )
    
    def _calculate_confidence_interval(self, data: np.ndarray, confidence: float) -> Tuple[float, float]:
        """Calculate confidence interval for data"""
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        return (np.percentile(data, lower_percentile), np.percentile(data, upper_percentile))
    
    def _calculate_max_drawdown(self, portfolio_values: np.ndarray) -> float:
        """Calculate maximum drawdown across all simulations"""
        max_drawdowns = []
        
        for sim in range(portfolio_values.shape[0]):
            values = portfolio_values[sim]
            peak = np.maximum.accumulate(values)
            drawdown = (values - peak) / peak
            max_drawdowns.append(np.min(drawdown))
        
        return np.mean(max_drawdowns)
    
    def sensitivity_analysis(self,
                           base_params: Dict[str, float],
                           param_ranges: Dict[str, Tuple[float, float]],
                           portfolio_value: float,
                           years: int) -> pd.DataFrame:
        """
        Perform sensitivity analysis on key parameters
        
        Args:
            base_params: Base case parameters
            param_ranges: Min/max ranges for each parameter
            portfolio_value: Initial portfolio value
            years: Number of years
        
        Returns:
            DataFrame with sensitivity analysis results
        """
        results = []
        
        for param_name, (min_val, max_val) in param_ranges.items():
            # Test 5 values across the range
            test_values = np.linspace(min_val, max_val, 5)
            
            for test_value in test_values:
                # Create modified parameters
                test_params = base_params.copy()
                test_params[param_name] = test_value
                
                # Run simulation
                sim_results = self.simulate_portfolio_returns(
                    initial_value=portfolio_value,
                    expected_return=test_params.get('expected_return', 0.07),
                    volatility=test_params.get('volatility', 0.15),
                    years=years,
                    annual_withdrawal=test_params.get('withdrawal', 0),
                    inflation_rate=test_params.get('inflation', 0.03)
                )
                
                results.append({
                    'parameter': param_name,
                    'value': test_value,
                    'success_rate': sim_results.success_rate,
                    'median_outcome': sim_results.median_outcome,
                    'std_deviation': sim_results.std_deviation
                })
        
        return pd.DataFrame(results)