"""Unified retirement planning system with flexible portfolio support"""

from decimal import Decimal
from typing import Optional, Dict
import matplotlib.pyplot as plt

from core.money import Money
from core.multi_account_portfolio import (
    MultiAccountPortfolio, WithdrawalOrder
)
from core.multi_account_withdrawal import (
    MultiAccountWithdrawalStrategy,
    MultiAccountFixedWithdrawal,
    MultiAccountPercentageWithdrawal,
    MultiAccountDynamicWithdrawal
)
from core.multi_account_simulator import (
    MultiAccountMonteCarloSimulator,
    MultiAccountSimulationParameters,
    MultiAccountSimulationResults
)
from core.portfolio_builder import (
    PortfolioBuilder,
    create_simple_portfolio,
    create_traditional_retirement_portfolio
)


class RetirementPlanner:
    """Flexible retirement planning orchestrator"""
    
    def __init__(self):
        self.simulations = {}
        self.scenarios = {}
    
    def run_simulation(
        self,
        portfolio: MultiAccountPortfolio,
        withdrawal_strategy: MultiAccountWithdrawalStrategy,
        years: int = 30,
        num_simulations: int = 1000,
        pay_mortgage: bool = None
    ) -> MultiAccountSimulationResults:
        """
        Run simulation with a pre-built portfolio and withdrawal strategy.
        This is the most flexible method that accepts any portfolio configuration.
        """
        # Auto-detect if mortgage payment is needed
        if pay_mortgage is None:
            from core.accounts import AccountType
            pay_mortgage = any(
                acc.account_type == AccountType.MORTGAGE 
                for acc in portfolio.accounts.values()
            )
        
        # Create simulation parameters
        params = MultiAccountSimulationParameters(
            portfolio=portfolio,
            years=years,
            num_simulations=num_simulations,
            withdrawal_strategy=withdrawal_strategy,
            pay_mortgage=pay_mortgage
        )
        
        # Run simulation
        simulator = MultiAccountMonteCarloSimulator(params)
        return simulator.run()
    
    def run_simulation_with_fixed_withdrawal(
        self,
        portfolio: MultiAccountPortfolio,
        annual_withdrawal: Decimal,
        years: int = 30,
        num_simulations: int = 1000,
        inflation_rate: Decimal = Decimal('0.03')
    ) -> MultiAccountSimulationResults:
        """Run simulation with fixed withdrawal amount"""
        withdrawal_strategy = MultiAccountFixedWithdrawal(
            initial_withdrawal=Money(annual_withdrawal),
            inflation_rate=inflation_rate,
            withdrawal_order=portfolio.withdrawal_order
        )
        
        return self.run_simulation(
            portfolio=portfolio,
            withdrawal_strategy=withdrawal_strategy,
            years=years,
            num_simulations=num_simulations
        )
    
    def run_simulation_with_percentage_withdrawal(
        self,
        portfolio: MultiAccountPortfolio,
        withdrawal_rate: Decimal,  # As percentage (e.g., 4.0 for 4%)
        years: int = 30,
        num_simulations: int = 1000,
        min_withdrawal: Optional[Money] = None,
        max_withdrawal: Optional[Money] = None
    ) -> MultiAccountSimulationResults:
        """Run simulation with percentage-based withdrawal"""
        withdrawal_strategy = MultiAccountPercentageWithdrawal(
            withdrawal_rate=withdrawal_rate,
            min_withdrawal=min_withdrawal,
            max_withdrawal=max_withdrawal,
            withdrawal_order=portfolio.withdrawal_order
        )
        
        return self.run_simulation(
            portfolio=portfolio,
            withdrawal_strategy=withdrawal_strategy,
            years=years,
            num_simulations=num_simulations
        )
    
    def run_simulation_with_dynamic_withdrawal(
        self,
        portfolio: MultiAccountPortfolio,
        base_withdrawal: Money,
        min_rate: Decimal = Decimal('3'),
        max_rate: Decimal = Decimal('6'),
        years: int = 30,
        num_simulations: int = 1000
    ) -> MultiAccountSimulationResults:
        """Run simulation with dynamic withdrawal strategy"""
        withdrawal_strategy = MultiAccountDynamicWithdrawal(
            base_withdrawal=base_withdrawal,
            min_rate=min_rate,
            max_rate=max_rate,
            withdrawal_order=portfolio.withdrawal_order
        )
        
        return self.run_simulation(
            portfolio=portfolio,
            withdrawal_strategy=withdrawal_strategy,
            years=years,
            num_simulations=num_simulations
        )
    
    def compare_strategies_for_portfolio(
        self,
        portfolio: MultiAccountPortfolio,
        strategies: Dict[str, MultiAccountWithdrawalStrategy],
        years: int = 30,
        num_simulations: int = 1000
    ) -> Dict[str, MultiAccountSimulationResults]:
        """Compare multiple strategies for the same portfolio"""
        results = {}
        
        for name, strategy in strategies.items():
            print(f"Running {name} strategy...")
            results[name] = self.run_simulation(
                portfolio=portfolio,
                withdrawal_strategy=strategy,
                years=years,
                num_simulations=num_simulations
            )
        
        return results
    
    def compare_strategies(
        self,
        initial_portfolio: Decimal,
        years: int = 30,
        num_simulations: int = 1000,
        current_age: int = 65
    ) -> Dict[str, MultiAccountSimulationResults]:
        """Compare standard withdrawal strategies (backward compatibility)"""
        portfolio = create_simple_portfolio(
            balance=initial_portfolio,
            age=current_age
        )
        
        strategies = {
            "Conservative 3%": MultiAccountFixedWithdrawal(
                initial_withdrawal=Money(initial_portfolio * Decimal('0.03')),
                inflation_rate=Decimal('0.03')
            ),
            "Standard 4%": MultiAccountFixedWithdrawal(
                initial_withdrawal=Money(initial_portfolio * Decimal('0.04')),
                inflation_rate=Decimal('0.03')
            ),
            "Aggressive 5%": MultiAccountFixedWithdrawal(
                initial_withdrawal=Money(initial_portfolio * Decimal('0.05')),
                inflation_rate=Decimal('0.03')
            )
        }
        
        return self.compare_strategies_for_portfolio(
            portfolio=portfolio,
            strategies=strategies,
            years=years,
            num_simulations=num_simulations
        )
    
    def create_dynamic_scenario(
        self,
        initial_portfolio: Decimal,
        base_withdrawal_rate: Decimal,
        min_rate: Decimal = Decimal('3'),
        max_rate: Decimal = Decimal('6'),
        years: int = 30,
        num_simulations: int = 1000,
        current_age: int = 65
    ) -> MultiAccountSimulationResults:
        """Create a dynamic withdrawal scenario (backward compatibility)"""
        portfolio = create_simple_portfolio(
            balance=initial_portfolio,
            age=current_age
        )
        
        base_withdrawal = Money(initial_portfolio * (base_withdrawal_rate / Decimal('100')))
        
        return self.run_simulation_with_dynamic_withdrawal(
            portfolio=portfolio,
            base_withdrawal=base_withdrawal,
            min_rate=min_rate,
            max_rate=max_rate,
            years=years,
            num_simulations=num_simulations
        )
    
    # Legacy convenience methods for backward compatibility
    def create_simple_scenario(
        self,
        initial_portfolio: Decimal,
        annual_withdrawal: Decimal,
        years: int = 30,
        mean_return: Decimal = Decimal('0.07'),
        volatility: Decimal = Decimal('0.18'),
        num_simulations: int = 10000,
        current_age: int = 65
    ) -> MultiAccountSimulationResults:
        """Create a simple scenario using a single account (backward compatibility)"""
        portfolio = create_simple_portfolio(
            balance=initial_portfolio,
            mean_return=mean_return,
            volatility=volatility,
            age=current_age
        )
        
        return self.run_simulation_with_fixed_withdrawal(
            portfolio=portfolio,
            annual_withdrawal=annual_withdrawal,
            years=years,
            num_simulations=num_simulations
        )
    
    def create_multi_account_scenario(
        self,
        cash_balance: Decimal = Decimal('50000'),
        taxable_balance: Decimal = Decimal('500000'),
        ira_balance: Decimal = Decimal('800000'),
        mortgage_balance: Decimal = Decimal('200000'),
        mortgage_rate: Decimal = Decimal('0.04'),
        mortgage_years: int = 15,
        annual_expenses: Decimal = Decimal('60000'),
        current_age: int = 65,
        years: int = 30,
        num_simulations: int = 1000,
        withdrawal_order: WithdrawalOrder = WithdrawalOrder.TAX_EFFICIENT
    ) -> MultiAccountSimulationResults:
        """Create a multi-account scenario (backward compatibility)"""
        portfolio = create_traditional_retirement_portfolio(
            cash=cash_balance,
            taxable=taxable_balance,
            ira=ira_balance,
            mortgage=mortgage_balance,
            mortgage_rate=mortgage_rate,
            mortgage_years=mortgage_years,
            age=current_age
        )
        portfolio.withdrawal_order = withdrawal_order
        
        return self.run_simulation_with_fixed_withdrawal(
            portfolio=portfolio,
            annual_withdrawal=annual_expenses,
            years=years,
            num_simulations=num_simulations
        )
    
    def visualize_results(
        self, 
        results: MultiAccountSimulationResults, 
        title: str = "Simulation Results",
        show_tax_info: bool = True
    ) -> plt.Figure:
        """Create visualization of simulation results"""
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Net worth trajectories (sample of runs)
        ax = axes[0, 0]
        sample_size = min(100, len(results.runs))
        for i in range(sample_size):
            run = results.runs[i]
            trajectory = [float(nw.amount) for nw in run.net_worth_trajectory]
            alpha = 0.1 if run.depleted else 0.2
            color = 'red' if run.depleted else 'blue'
            ax.plot(trajectory, alpha=alpha, color=color, linewidth=0.5)
        
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax.set_xlabel('Years in Retirement')
        ax.set_ylabel('Net Worth ($)')
        ax.set_title('Sample Portfolio Trajectories')
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Final net worth distribution
        ax = axes[0, 1]
        final_values = [float(run.final_net_worth.amount) for run in results.runs]
        positive_finals = [v for v in final_values if v > 0]
        
        if positive_finals:
            ax.hist(positive_finals, bins=50, alpha=0.7, edgecolor='black')
        ax.axvline(x=0, color='red', linestyle='--', label='Depleted')
        ax.set_xlabel('Final Net Worth ($)')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Final Net Worth')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Account depletion analysis
        ax = axes[1, 0]
        depletion_years = [run.depletion_year for run in results.runs if run.depletion_year is not None]
        
        if depletion_years:
            ax.hist(depletion_years, bins=range(0, results.parameters.years + 1),
                   alpha=0.7, color='red', edgecolor='black')
            ax.set_xlabel('Year of Depletion')
            ax.set_ylabel('Frequency')
            ax.set_title('Portfolio Depletion Timeline')
        else:
            ax.text(0.5, 0.5, 'No Depletions!', ha='center', va='center', fontsize=16)
            ax.set_title('Portfolio Depletion Timeline')
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Summary statistics
        ax = axes[1, 1]
        ax.axis('off')
        
        successful_runs = results.get_successful_runs()
        failed_runs = [r for r in results.runs if r.depleted]
        
        # Build summary text
        summary_text = f"""
        {title}
        ────────────────────
        Success Rate: {results.success_rate:.1f}%
        
        Successful Runs: {len(successful_runs):,}
        Failed Runs: {len(failed_runs):,}
        
        Median Final Net Worth: {results.median_final_net_worth}
        """
        
        # Add tax information if available and requested
        if show_tax_info and results.runs and results.runs[0].taxes_paid:
            total_taxes = Money(Decimal('0'))
            for run in results.runs:
                for tax in run.taxes_paid:
                    total_taxes = total_taxes.add(tax)
            avg_annual_tax = total_taxes.divide(
                Decimal(len(results.runs) * results.parameters.years)
            )
            summary_text += f"Average Annual Taxes: {avg_annual_tax}\n        "
        
        summary_text += f"""
        Parameters:
        • Years: {results.parameters.years}
        • Simulations: {results.parameters.num_simulations:,}
        • Starting Age: {results.parameters.portfolio.current_age}
        """
        
        ax.text(0.1, 0.5, summary_text, fontsize=11, family='monospace', va='center')
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def print_results_summary(
        self,
        results: MultiAccountSimulationResults,
        detailed: bool = False
    ) -> None:
        """Print a summary of simulation results"""
        print(f"\n{'='*60}")
        print("SIMULATION RESULTS SUMMARY")
        print('='*60)
        print(f"Success Rate: {results.success_rate:.1f}%")
        print(f"Median Final Net Worth: {results.median_final_net_worth}")
        
        if detailed:
            # Account depletion analysis
            depletion_stats = results.get_account_depletion_stats()
            if depletion_stats:
                print("\nAccount Depletion Statistics:")
                print("-"*40)
                for account_type, stats in depletion_stats.items():
                    if 'median_depletion' in stats:
                        print(f"{account_type.upper()}:")
                        print(f"  Median depletion: Year {stats['median_depletion']}")
                        print(f"  Depletion rate: {stats['depletion_rate']*100:.1f}%")
            
            # Mortgage payoff analysis
            mortgage_payoffs = [
                r.mortgage_paid_off_year 
                for r in results.runs 
                if r.mortgage_paid_off_year is not None
            ]
            if mortgage_payoffs:
                import numpy as np
                median_payoff = np.median(mortgage_payoffs)
                print(f"\nMedian Mortgage Payoff: Year {median_payoff:.0f}")
            
            # Tax analysis
            if results.total_taxes_paid.amount > 0:
                avg_annual = results.total_taxes_paid.divide(Decimal('30'))
                print(f"\nAverage Annual Taxes: {avg_annual}")


def main():
    """Example usage of flexible retirement planning system"""
    
    planner = RetirementPlanner()
    
    # Example 1: Build a custom portfolio manually
    print("\n" + "="*60)
    print("EXAMPLE 1: Custom Portfolio Building")
    print("="*60)
    
    # Build portfolio using the builder
    portfolio = (PortfolioBuilder("custom_001", "john_doe")
                 .with_age(62)
                 .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                 .add_cash_account(
                     balance=Decimal('75000'),
                     annual_return=Decimal('0.03'),
                     name="High-Yield Savings"
                 )
                 .add_taxable_account(
                     balance=Decimal('450000'),
                     stock_allocation=Decimal('0.75'),
                     name="Vanguard Brokerage"
                 )
                 .add_ira_account(
                     balance=Decimal('650000'),
                     stock_allocation=Decimal('0.60'),
                     name="Fidelity IRA"
                 )
                 .add_mortgage(
                     balance=Decimal('125000'),
                     interest_rate=Decimal('0.0375'),
                     remaining_years=12,
                     name="Home Loan"
                 )
                 .build())
    
    # Print portfolio summary
    print("\nPortfolio Summary:")
    summary = portfolio.get_account_summary()
    for name, balance in summary.items():
        print(f"  {name}: {balance}")
    
    # Run simulation with custom withdrawal strategy
    withdrawal_strategy = MultiAccountFixedWithdrawal(
        initial_withdrawal=Money(Decimal('55000')),
        inflation_rate=Decimal('0.025'),
        withdrawal_order=WithdrawalOrder.TAX_EFFICIENT
    )
    
    results = planner.run_simulation(
        portfolio=portfolio,
        withdrawal_strategy=withdrawal_strategy,
        years=35,
        num_simulations=1000
    )
    
    planner.print_results_summary(results, detailed=True)
    
    # Example 2: Compare strategies on the same portfolio
    print("\n" + "="*60)
    print("EXAMPLE 2: Strategy Comparison")
    print("="*60)
    
    strategies = {
        "Conservative 3%": MultiAccountPercentageWithdrawal(
            withdrawal_rate=Decimal('3'),
            withdrawal_order=portfolio.withdrawal_order
        ),
        "Standard 4%": MultiAccountPercentageWithdrawal(
            withdrawal_rate=Decimal('4'),
            withdrawal_order=portfolio.withdrawal_order
        ),
        "Dynamic 3-5%": MultiAccountDynamicWithdrawal(
            base_withdrawal=Money(Decimal('55000')),
            min_rate=Decimal('3'),
            max_rate=Decimal('5'),
            withdrawal_order=portfolio.withdrawal_order
        )
    }
    
    comparison_results = planner.compare_strategies_for_portfolio(
        portfolio=portfolio,
        strategies=strategies,
        years=30,
        num_simulations=500
    )
    
    print("\nStrategy Comparison Results:")
    print("-"*40)
    for name, results in comparison_results.items():
        print(f"{name:20} Success Rate: {results.success_rate:.1f}%")
    
    print("\n" + "="*60)
    print("Examples completed!")


if __name__ == "__main__":
    main()