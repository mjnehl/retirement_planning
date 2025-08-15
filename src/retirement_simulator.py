"""
Simple Monte Carlo Retirement Planning Simulator
Phase 1: Basic portfolio simulation with withdrawals
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt


@dataclass
class RetirementParams:
    """Basic retirement parameters for Phase 1"""
    # Portfolio
    initial_portfolio: float = 1_000_000  # Starting portfolio value
    
    # Withdrawal strategy
    annual_withdrawal: float = 40_000  # Fixed withdrawal amount (4% rule)
    withdrawal_increase_rate: float = 0.03  # Annual inflation adjustment
    
    # Time horizon
    years_in_retirement: int = 30  # Planning horizon
    
    # Market assumptions
    mean_return: float = 0.07  # Historical average stock return
    std_return: float = 0.18  # Historical volatility
    
    # Simulation
    num_simulations: int = 10_000  # Number of Monte Carlo runs


class RetirementSimulator:
    """Monte Carlo retirement planning simulator"""
    
    def __init__(self, params: RetirementParams):
        self.params = params
        self.results = None
        
    def run_single_simulation(self, seed: int = None) -> Dict:
        """Run a single Monte Carlo simulation"""
        if seed is not None:
            np.random.seed(seed)
            
        portfolio_values = []
        withdrawals = []
        
        # Initialize
        current_portfolio = self.params.initial_portfolio
        current_withdrawal = self.params.annual_withdrawal
        
        for year in range(self.params.years_in_retirement):
            # Record starting values
            portfolio_values.append(current_portfolio)
            withdrawals.append(current_withdrawal)
            
            # Check if portfolio is depleted
            if current_portfolio <= 0:
                # Fill remaining years with zeros
                portfolio_values.extend([0] * (self.params.years_in_retirement - year - 1))
                withdrawals.extend([0] * (self.params.years_in_retirement - year - 1))
                break
                
            # Apply withdrawal
            current_portfolio -= current_withdrawal
            
            # Apply market return (only on remaining balance)
            if current_portfolio > 0:
                annual_return = np.random.normal(
                    self.params.mean_return, 
                    self.params.std_return
                )
                current_portfolio *= (1 + annual_return)
            
            # Increase withdrawal for inflation
            current_withdrawal *= (1 + self.params.withdrawal_increase_rate)
        
        return {
            'portfolio_values': portfolio_values,
            'withdrawals': withdrawals,
            'final_value': portfolio_values[-1] if portfolio_values else 0,
            'depleted': portfolio_values[-1] <= 0 if portfolio_values else True,
            'depletion_year': next((i for i, v in enumerate(portfolio_values) if v <= 0), None)
        }
    
    def run_simulation(self) -> pd.DataFrame:
        """Run full Monte Carlo simulation"""
        results = []
        
        for i in range(self.params.num_simulations):
            sim_result = self.run_single_simulation(seed=None)
            sim_result['simulation_id'] = i
            results.append(sim_result)
        
        self.results = pd.DataFrame(results)
        return self.results
    
    def calculate_success_rate(self) -> float:
        """Calculate the probability of not running out of money"""
        if self.results is None:
            raise ValueError("Run simulation first")
        
        success_count = (~self.results['depleted']).sum()
        return (success_count / len(self.results)) * 100
    
    def get_percentile_paths(self, percentiles: List[int] = [10, 25, 50, 75, 90]) -> Dict:
        """Get portfolio paths at different percentiles"""
        if self.results is None:
            raise ValueError("Run simulation first")
        
        # Extract all portfolio paths
        all_paths = np.array([path for path in self.results['portfolio_values']])
        
        # Calculate percentiles for each year
        percentile_paths = {}
        for p in percentiles:
            percentile_paths[f'p{p}'] = np.percentile(all_paths, p, axis=0)
        
        return percentile_paths
    
    def plot_simulation_results(self, num_paths: int = 100):
        """Visualize simulation results"""
        if self.results is None:
            raise ValueError("Run simulation first")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Sample paths
        ax = axes[0, 0]
        sample_indices = np.random.choice(len(self.results), min(num_paths, len(self.results)), replace=False)
        for idx in sample_indices:
            path = self.results.iloc[idx]['portfolio_values']
            ax.plot(range(len(path)), path, alpha=0.1, color='blue')
        
        # Add percentile paths
        percentile_paths = self.get_percentile_paths()
        ax.plot(percentile_paths['p50'], color='red', linewidth=2, label='Median')
        ax.plot(percentile_paths['p25'], color='orange', linewidth=1, label='25th percentile')
        ax.plot(percentile_paths['p75'], color='orange', linewidth=1, label='75th percentile')
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax.set_xlabel('Years in Retirement')
        ax.set_ylabel('Portfolio Value ($)')
        ax.set_title('Monte Carlo Simulation Paths')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Final value distribution
        ax = axes[0, 1]
        final_values = self.results['final_value']
        ax.hist(final_values[final_values > 0], bins=50, alpha=0.7, color='green', edgecolor='black')
        ax.axvline(x=0, color='red', linestyle='--', label='Depleted')
        ax.set_xlabel('Final Portfolio Value ($)')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Final Portfolio Values')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Depletion timeline
        ax = axes[1, 0]
        depletion_years = self.results['depletion_year'].dropna()
        if len(depletion_years) > 0:
            ax.hist(depletion_years, bins=range(0, self.params.years_in_retirement + 1), 
                   alpha=0.7, color='red', edgecolor='black')
            ax.set_xlabel('Year of Depletion')
            ax.set_ylabel('Frequency')
            ax.set_title('When Portfolios Run Out')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No Depletions!', ha='center', va='center', fontsize=16)
            ax.set_title('When Portfolios Run Out')
        
        # Plot 4: Success metrics
        ax = axes[1, 1]
        ax.axis('off')
        success_rate = self.calculate_success_rate()
        median_final = np.median(self.results['final_value'])
        mean_final = np.mean(self.results['final_value'])
        
        metrics_text = f"""
        Simulation Results:
        ───────────────────
        Success Rate: {success_rate:.1f}%
        (Portfolio survives {self.params.years_in_retirement} years)
        
        Median Final Value: ${median_final:,.0f}
        Mean Final Value: ${mean_final:,.0f}
        
        Parameters:
        • Initial Portfolio: ${self.params.initial_portfolio:,.0f}
        • Annual Withdrawal: ${self.params.annual_withdrawal:,.0f}
        • Withdrawal Rate: {(self.params.annual_withdrawal/self.params.initial_portfolio)*100:.1f}%
        • Simulations: {self.params.num_simulations:,}
        """
        ax.text(0.1, 0.5, metrics_text, fontsize=11, family='monospace', va='center')
        
        plt.tight_layout()
        return fig
    
    def sensitivity_analysis(self, param_name: str, values: List[float]) -> pd.DataFrame:
        """Analyze sensitivity to parameter changes"""
        results = []
        original_value = getattr(self.params, param_name)
        
        for value in values:
            setattr(self.params, param_name, value)
            self.run_simulation()
            success_rate = self.calculate_success_rate()
            results.append({
                param_name: value,
                'success_rate': success_rate,
                'median_final': np.median(self.results['final_value'])
            })
        
        # Restore original value
        setattr(self.params, param_name, original_value)
        
        return pd.DataFrame(results)


def run_basic_example():
    """Run a basic example simulation"""
    # Create parameters
    params = RetirementParams(
        initial_portfolio=1_000_000,
        annual_withdrawal=40_000,  # 4% rule
        years_in_retirement=30,
        mean_return=0.07,
        std_return=0.18,
        num_simulations=10_000
    )
    
    # Run simulation
    simulator = RetirementSimulator(params)
    results = simulator.run_simulation()
    
    # Calculate success rate
    success_rate = simulator.calculate_success_rate()
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Show percentile paths
    percentiles = simulator.get_percentile_paths()
    print("\nPortfolio Value Percentiles (Year 30):")
    for key, values in percentiles.items():
        print(f"  {key}: ${values[-1]:,.0f}")
    
    return simulator


if __name__ == "__main__":
    simulator = run_basic_example()
    fig = simulator.plot_simulation_results()
    plt.savefig('docs/basic_simulation_results.png', dpi=150, bbox_inches='tight')
    plt.show()