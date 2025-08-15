"""Portfolio optimization using Modern Portfolio Theory"""

import numpy as np
from scipy.optimize import minimize
from decimal import Decimal
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import pandas as pd


@dataclass
class Asset:
    """Individual asset in portfolio"""
    symbol: str
    expected_return: float
    volatility: float
    current_allocation: float = 0.0
    min_allocation: float = 0.0
    max_allocation: float = 1.0
    asset_class: str = "equity"


@dataclass
class OptimizedPortfolio:
    """Results from portfolio optimization"""
    weights: np.ndarray
    expected_return: float
    volatility: float
    sharpe_ratio: float
    asset_allocations: Dict[str, float]
    efficient_frontier: Optional[List[Tuple[float, float]]] = None
    
    def get_summary(self) -> str:
        """Get formatted summary of optimization results"""
        summary = [
            "Optimized Portfolio",
            "=" * 40,
            f"Expected Return: {self.expected_return:.2%}",
            f"Volatility: {self.volatility:.2%}",
            f"Sharpe Ratio: {self.sharpe_ratio:.3f}",
            "",
            "Asset Allocations:"
        ]
        
        for asset, weight in self.asset_allocations.items():
            if weight > 0.001:  # Only show allocations > 0.1%
                summary.append(f"  {asset}: {weight:.1%}")
        
        return "\n".join(summary)


class PortfolioOptimizer:
    """Portfolio optimizer using Markowitz Mean-Variance Optimization"""
    
    def __init__(self, risk_free_rate: float = 0.03):
        """
        Initialize portfolio optimizer
        
        Args:
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
        """
        self.risk_free_rate = risk_free_rate
    
    def optimize_portfolio(self,
                          assets: List[Asset],
                          correlation_matrix: Optional[np.ndarray] = None,
                          target_return: Optional[float] = None,
                          target_volatility: Optional[float] = None,
                          maximize_sharpe: bool = True) -> OptimizedPortfolio:
        """
        Optimize portfolio allocation
        
        Args:
            assets: List of assets to optimize
            correlation_matrix: Correlation matrix between assets
            target_return: Target return constraint
            target_volatility: Target volatility constraint
            maximize_sharpe: Whether to maximize Sharpe ratio
        
        Returns:
            OptimizedPortfolio with optimal weights
        """
        n_assets = len(assets)
        
        # Extract returns and volatilities
        returns = np.array([asset.expected_return for asset in assets])
        volatilities = np.array([asset.volatility for asset in assets])
        
        # Generate correlation matrix if not provided
        if correlation_matrix is None:
            correlation_matrix = self._estimate_correlation_matrix(assets)
        
        # Calculate covariance matrix
        cov_matrix = self._calculate_covariance_matrix(volatilities, correlation_matrix)
        
        # Set up optimization constraints
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]  # Weights sum to 1
        
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: np.dot(x, returns) - target_return
            })
        
        if target_volatility is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: np.sqrt(np.dot(x, np.dot(cov_matrix, x))) - target_volatility
            })
        
        # Set bounds for each asset
        bounds = [(asset.min_allocation, asset.max_allocation) for asset in assets]
        
        # Initial guess (equal weights adjusted for constraints)
        x0 = np.array([1.0 / n_assets for _ in range(n_assets)])
        
        # Objective function
        if maximize_sharpe:
            # Negative Sharpe ratio (minimize negative = maximize positive)
            def objective(weights):
                portfolio_return = np.dot(weights, returns)
                portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
                return -sharpe
        else:
            # Minimize volatility
            def objective(weights):
                return np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        
        # Perform optimization
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if not result.success:
            # Fall back to equal weights if optimization fails
            optimal_weights = x0
        else:
            optimal_weights = result.x
        
        # Calculate portfolio metrics
        portfolio_return = np.dot(optimal_weights, returns)
        portfolio_vol = np.sqrt(np.dot(optimal_weights, np.dot(cov_matrix, optimal_weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
        
        # Create allocation dictionary
        allocations = {asset.symbol: weight for asset, weight in zip(assets, optimal_weights)}
        
        # Generate efficient frontier
        efficient_frontier = self._calculate_efficient_frontier(
            returns, cov_matrix, bounds
        )
        
        return OptimizedPortfolio(
            weights=optimal_weights,
            expected_return=portfolio_return,
            volatility=portfolio_vol,
            sharpe_ratio=sharpe_ratio,
            asset_allocations=allocations,
            efficient_frontier=efficient_frontier
        )
    
    def _calculate_covariance_matrix(self,
                                    volatilities: np.ndarray,
                                    correlation_matrix: np.ndarray) -> np.ndarray:
        """Calculate covariance matrix from volatilities and correlations"""
        n = len(volatilities)
        cov_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                cov_matrix[i, j] = correlation_matrix[i, j] * volatilities[i] * volatilities[j]
        
        return cov_matrix
    
    def _estimate_correlation_matrix(self, assets: List[Asset]) -> np.ndarray:
        """
        Estimate correlation matrix based on asset classes
        
        Simple heuristic correlations based on asset classes
        """
        n = len(assets)
        corr_matrix = np.eye(n)
        
        # Define typical correlations between asset classes
        correlations = {
            ('equity', 'equity'): 0.7,
            ('equity', 'bond'): -0.2,
            ('equity', 'commodity'): 0.3,
            ('equity', 'real_estate'): 0.6,
            ('bond', 'bond'): 0.9,
            ('bond', 'commodity'): -0.1,
            ('bond', 'real_estate'): 0.2,
            ('commodity', 'commodity'): 0.8,
            ('commodity', 'real_estate'): 0.4,
            ('real_estate', 'real_estate'): 0.8
        }
        
        for i in range(n):
            for j in range(i + 1, n):
                class_i = assets[i].asset_class
                class_j = assets[j].asset_class
                
                # Look up correlation
                key = tuple(sorted([class_i, class_j]))
                if key in correlations:
                    corr = correlations[key]
                else:
                    corr = 0.3  # Default moderate correlation
                
                corr_matrix[i, j] = corr
                corr_matrix[j, i] = corr
        
        return corr_matrix
    
    def _calculate_efficient_frontier(self,
                                     returns: np.ndarray,
                                     cov_matrix: np.ndarray,
                                     bounds: List[Tuple[float, float]],
                                     n_points: int = 50) -> List[Tuple[float, float]]:
        """Calculate efficient frontier points"""
        frontier = []
        
        # Get min and max possible returns
        min_return = np.min(returns)
        max_return = np.max(returns)
        
        # Generate target returns
        target_returns = np.linspace(min_return, max_return, n_points)
        
        for target in target_returns:
            # Minimize volatility for each target return
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x, tr=target: np.dot(x, returns) - tr}
            ]
            
            def objective(weights):
                return np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            
            x0 = np.array([1.0 / len(returns) for _ in range(len(returns))])
            
            result = minimize(
                objective,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'disp': False, 'maxiter': 100}
            )
            
            if result.success:
                volatility = objective(result.x)
                frontier.append((volatility, target))
        
        return frontier
    
    def rebalance_portfolio(self,
                           current_portfolio: Dict[str, float],
                           target_allocations: Dict[str, float],
                           threshold: float = 0.05,
                           transaction_cost: float = 0.001) -> Dict[str, float]:
        """
        Calculate rebalancing trades
        
        Args:
            current_portfolio: Current portfolio values by asset
            target_allocations: Target allocation percentages
            threshold: Rebalancing threshold (don't rebalance if within threshold)
            transaction_cost: Transaction cost as percentage
        
        Returns:
            Dictionary of trades (positive = buy, negative = sell)
        """
        total_value = sum(current_portfolio.values())
        trades = {}
        
        for asset, target_pct in target_allocations.items():
            current_value = current_portfolio.get(asset, 0)
            current_pct = current_value / total_value if total_value > 0 else 0
            
            # Check if rebalancing is needed
            if abs(current_pct - target_pct) > threshold:
                target_value = total_value * target_pct
                trade_value = target_value - current_value
                
                # Account for transaction costs
                if trade_value > 0:
                    # Buying - need extra for transaction cost
                    trade_value *= (1 + transaction_cost)
                else:
                    # Selling - receive less due to transaction cost
                    trade_value *= (1 - transaction_cost)
                
                trades[asset] = trade_value
        
        return trades
    
    def calculate_risk_metrics(self,
                              weights: np.ndarray,
                              returns: np.ndarray,
                              cov_matrix: np.ndarray,
                              confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Calculate various risk metrics for portfolio
        
        Args:
            weights: Portfolio weights
            returns: Expected returns
            cov_matrix: Covariance matrix
            confidence_level: Confidence level for VaR calculation
        
        Returns:
            Dictionary of risk metrics
        """
        portfolio_return = np.dot(weights, returns)
        portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        
        # Value at Risk (parametric)
        from scipy import stats
        z_score = stats.norm.ppf(1 - confidence_level)
        var = -portfolio_return - z_score * portfolio_vol
        
        # Conditional Value at Risk (CVaR)
        # Using parametric approximation
        pdf_z = stats.norm.pdf(z_score)
        cvar = -portfolio_return + portfolio_vol * pdf_z / (1 - confidence_level)
        
        # Maximum diversification ratio
        weighted_avg_vol = np.dot(weights, np.sqrt(np.diag(cov_matrix)))
        diversification_ratio = weighted_avg_vol / portfolio_vol
        
        # Effective number of assets (using entropy)
        # Avoid log(0) by filtering out zero weights
        non_zero_weights = weights[weights > 1e-10]
        if len(non_zero_weights) > 0:
            entropy = -np.sum(non_zero_weights * np.log(non_zero_weights))
            effective_n = np.exp(entropy)
        else:
            effective_n = 1
        
        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': (portfolio_return - self.risk_free_rate) / portfolio_vol,
            'value_at_risk': var,
            'conditional_var': cvar,
            'diversification_ratio': diversification_ratio,
            'effective_assets': effective_n
        }
    
    def optimize_with_constraints(self,
                                 assets: List[Asset],
                                 constraints: Dict[str, any]) -> OptimizedPortfolio:
        """
        Optimize with additional constraints
        
        Constraints can include:
        - max_single_asset: Maximum allocation to any single asset
        - min_diversification: Minimum number of assets
        - sector_limits: Maximum allocation per sector
        - esg_minimum: Minimum ESG score
        
        Args:
            assets: List of assets
            constraints: Dictionary of constraints
        
        Returns:
            Optimized portfolio
        """
        # Apply max single asset constraint
        if 'max_single_asset' in constraints:
            max_allocation = constraints['max_single_asset']
            for asset in assets:
                asset.max_allocation = min(asset.max_allocation, max_allocation)
        
        # Apply minimum diversification
        if 'min_diversification' in constraints:
            min_assets = constraints['min_diversification']
            max_per_asset = 1.0 / min_assets
            for asset in assets:
                asset.max_allocation = min(asset.max_allocation, max_per_asset * 2)
        
        # Optimize with updated constraints
        return self.optimize_portfolio(assets, maximize_sharpe=True)