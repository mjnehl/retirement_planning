"""
Scenario runner for retirement planning questions
Allows you to test different scenarios and what-if questions
"""

from retirement_simulator import RetirementParams, RetirementSimulator
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class ScenarioRunner:
    """Run and compare different retirement scenarios"""
    
    def __init__(self):
        self.scenarios = {}
        self.results = {}
    
    def add_scenario(self, name: str, params: RetirementParams):
        """Add a scenario to test"""
        self.scenarios[name] = params
    
    def run_all_scenarios(self):
        """Run all defined scenarios"""
        for name, params in self.scenarios.items():
            print(f"Running scenario: {name}")
            simulator = RetirementSimulator(params)
            simulator.run_simulation()
            self.results[name] = {
                'simulator': simulator,
                'success_rate': simulator.calculate_success_rate(),
                'percentiles': simulator.get_percentile_paths()
            }
    
    def compare_scenarios(self) -> pd.DataFrame:
        """Create comparison table of all scenarios"""
        comparison = []
        for name, result in self.results.items():
            sim = result['simulator']
            comparison.append({
                'Scenario': name,
                'Initial Portfolio': f"${sim.params.initial_portfolio:,.0f}",
                'Annual Withdrawal': f"${sim.params.annual_withdrawal:,.0f}",
                'Withdrawal Rate': f"{(sim.params.annual_withdrawal/sim.params.initial_portfolio)*100:.1f}%",
                'Success Rate': f"{result['success_rate']:.1f}%",
                'Median Final': f"${np.median(sim.results['final_value']):,.0f}"
            })
        return pd.DataFrame(comparison)
    
    def plot_scenario_comparison(self):
        """Plot all scenarios together"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Median paths comparison
        ax = axes[0]
        for name, result in self.results.items():
            percentiles = result['percentiles']
            years = range(len(percentiles['p50']))
            ax.plot(years, percentiles['p50'], linewidth=2, label=name)
        
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax.set_xlabel('Years in Retirement')
        ax.set_ylabel('Portfolio Value ($)')
        ax.set_title('Median Portfolio Paths Comparison')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Success rate comparison
        ax = axes[1]
        scenarios = list(self.results.keys())
        success_rates = [self.results[s]['success_rate'] for s in scenarios]
        colors = ['green' if sr >= 80 else 'orange' if sr >= 60 else 'red' for sr in success_rates]
        
        bars = ax.bar(range(len(scenarios)), success_rates, color=colors, edgecolor='black')
        ax.set_xticks(range(len(scenarios)))
        ax.set_xticklabels(scenarios, rotation=45, ha='right')
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Success Rate Comparison')
        ax.axhline(y=80, color='green', linestyle='--', alpha=0.5, label='80% threshold')
        ax.axhline(y=60, color='orange', linestyle='--', alpha=0.5, label='60% threshold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, rate in zip(bars, success_rates):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{rate:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig


# Example scenarios to answer common questions
def create_example_scenarios():
    """Create example scenarios for common retirement questions"""
    runner = ScenarioRunner()
    
    # Scenario 1: Conservative baseline (4% rule)
    runner.add_scenario("Conservative (4% rule)", RetirementParams(
        initial_portfolio=1_000_000,
        annual_withdrawal=40_000,
        years_in_retirement=30,
        mean_return=0.07,
        std_return=0.18
    ))
    
    # Scenario 2: Aggressive withdrawal (5% rule)
    runner.add_scenario("Aggressive (5% rule)", RetirementParams(
        initial_portfolio=1_000_000,
        annual_withdrawal=50_000,
        years_in_retirement=30,
        mean_return=0.07,
        std_return=0.18
    ))
    
    # Scenario 3: Very conservative (3% rule)
    runner.add_scenario("Very Conservative (3% rule)", RetirementParams(
        initial_portfolio=1_000_000,
        annual_withdrawal=30_000,
        years_in_retirement=30,
        mean_return=0.07,
        std_return=0.18
    ))
    
    # Scenario 4: Lower returns environment
    runner.add_scenario("Lower Returns (6%)", RetirementParams(
        initial_portfolio=1_000_000,
        annual_withdrawal=40_000,
        years_in_retirement=30,
        mean_return=0.06,  # Lower expected returns
        std_return=0.18
    ))
    
    # Scenario 5: Higher volatility
    runner.add_scenario("High Volatility", RetirementParams(
        initial_portfolio=1_000_000,
        annual_withdrawal=40_000,
        years_in_retirement=30,
        mean_return=0.07,
        std_return=0.25  # Higher volatility
    ))
    
    # Scenario 6: Longer retirement (40 years)
    runner.add_scenario("40-Year Retirement", RetirementParams(
        initial_portfolio=1_000_000,
        annual_withdrawal=40_000,
        years_in_retirement=40,  # Longer horizon
        mean_return=0.07,
        std_return=0.18
    ))
    
    return runner


def answer_specific_questions():
    """Answer specific retirement planning questions"""
    
    print("=" * 60)
    print("RETIREMENT PLANNING MONTE CARLO ANALYSIS")
    print("=" * 60)
    
    # Question 1: What withdrawal rate gives 90% success?
    print("\n📊 Question 1: What withdrawal rate gives ~90% success rate?")
    print("-" * 50)
    
    test_rates = [0.025, 0.03, 0.035, 0.04, 0.045, 0.05]
    results = []
    
    for rate in test_rates:
        params = RetirementParams(
            initial_portfolio=1_000_000,
            annual_withdrawal=1_000_000 * rate,
            years_in_retirement=30,
            num_simulations=5000  # Fewer for speed
        )
        sim = RetirementSimulator(params)
        sim.run_simulation()
        success = sim.calculate_success_rate()
        results.append((rate * 100, success))
        print(f"  {rate*100:.1f}% withdrawal rate → {success:.1f}% success")
    
    # Question 2: How much do I need to retire?
    print("\n📊 Question 2: Portfolio needed for $60k/year spending?")
    print("-" * 50)
    
    annual_spending = 60_000
    test_portfolios = [1_000_000, 1_250_000, 1_500_000, 1_750_000, 2_000_000]
    
    for portfolio in test_portfolios:
        params = RetirementParams(
            initial_portfolio=portfolio,
            annual_withdrawal=annual_spending,
            years_in_retirement=30,
            num_simulations=5000
        )
        sim = RetirementSimulator(params)
        sim.run_simulation()
        success = sim.calculate_success_rate()
        withdrawal_rate = (annual_spending / portfolio) * 100
        print(f"  ${portfolio:,.0f} portfolio → {success:.1f}% success ({withdrawal_rate:.1f}% rate)")
    
    # Question 3: Impact of time horizon
    print("\n📊 Question 3: How does retirement length affect success?")
    print("-" * 50)
    
    test_years = [20, 25, 30, 35, 40, 45]
    
    for years in test_years:
        params = RetirementParams(
            initial_portfolio=1_000_000,
            annual_withdrawal=40_000,
            years_in_retirement=years,
            num_simulations=5000
        )
        sim = RetirementSimulator(params)
        sim.run_simulation()
        success = sim.calculate_success_rate()
        print(f"  {years} years → {success:.1f}% success")
    
    return results


if __name__ == "__main__":
    # Run example scenarios
    runner = create_example_scenarios()
    runner.run_all_scenarios()
    
    # Show comparison
    print("\nScenario Comparison:")
    print(runner.compare_scenarios().to_string(index=False))
    
    # Create visualization
    fig = runner.plot_scenario_comparison()
    plt.savefig('docs/scenario_comparison.png', dpi=150, bbox_inches='tight')
    
    # Answer specific questions
    answer_specific_questions()
    
    plt.show()