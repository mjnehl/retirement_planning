"""
Simple example to get started with retirement planning simulation
"""

import sys
sys.path.append('../src')

from retirement_simulator import RetirementParams, RetirementSimulator
import matplotlib.pyplot as plt


def main():
    """Run a simple retirement planning simulation"""
    
    print("🎯 Simple Retirement Planning Monte Carlo Simulation")
    print("=" * 50)
    
    # Define your retirement parameters
    params = RetirementParams(
        initial_portfolio=500_000,    # $1M starting portfolio
        annual_withdrawal=40_000,        # $40k per year (4% rule)
        withdrawal_increase_rate=0.03,   # 3% inflation adjustment
        years_in_retirement=40,          # 30-year retirement
        mean_return=0.12,                # 7% average market return
        std_return=0.18,                 # 18% volatility
        num_simulations=10_000           # Run 10,000 simulations
    )
    
    print(f"""
Your Retirement Scenario:
• Starting Portfolio: ${params.initial_portfolio:,.0f}
• Annual Withdrawal: ${params.annual_withdrawal:,.0f}
• Withdrawal Rate: {(params.annual_withdrawal/params.initial_portfolio)*100:.1f}%
• Years in Retirement: {params.years_in_retirement}
• Expected Return: {params.mean_return*100:.1f}%
• Volatility: {params.std_return*100:.1f}%
• Number of Simulations: {params.num_simulations:,}
    """)
    
    # Run the simulation
    print("Running simulation...")
    simulator = RetirementSimulator(params)
    results = simulator.run_simulation()
    
    # Get the results
    success_rate = simulator.calculate_success_rate()
    percentiles = simulator.get_percentile_paths()
    
    print(f"\n📊 RESULTS:")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"(Probability of not running out of money)")
    
    print(f"\nPortfolio Values at Year {params.years_in_retirement}:")
    print(f"  90th percentile: ${percentiles['p90'][-1]:,.0f} (best case)")
    print(f"  75th percentile: ${percentiles['p75'][-1]:,.0f}")
    print(f"  50th percentile: ${percentiles['p50'][-1]:,.0f} (median)")
    print(f"  25th percentile: ${percentiles['p25'][-1]:,.0f}")
    print(f"  10th percentile: ${percentiles['p10'][-1]:,.0f} (worst case)")
    
    # Visualize the results
    fig = simulator.plot_simulation_results(num_paths=100)
    plt.show()
    
    return simulator


def test_different_withdrawal_rates():
    """Test how different withdrawal rates affect success"""
    
    print("\n" + "=" * 50)
    print("Testing Different Withdrawal Rates")
    print("=" * 50)
    
    portfolio = 1_000_000
    rates = [0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06]
    
    for rate in rates:
        params = RetirementParams(
            initial_portfolio=portfolio,
            annual_withdrawal=portfolio * rate,
            years_in_retirement=30,
            num_simulations=5000  # Fewer simulations for speed
        )
        
        simulator = RetirementSimulator(params)
        simulator.run_simulation()
        success_rate = simulator.calculate_success_rate()
        
        print(f"{rate*100:.1f}% withdrawal rate → {success_rate:.1f}% success rate")


if __name__ == "__main__":
    # Run the main example
    simulator = main()
    
    # Test different scenarios
    test_different_withdrawal_rates()
    
    # Try your own scenario
    print("\n" + "=" * 50)
    print("Try modifying the parameters above to test your own scenario!")
    print("Questions you can answer:")
    print("• How much can I safely withdraw?")
    print("• What if returns are lower than expected?")
    print("• How does volatility affect my retirement?")
    print("• Do I have enough to retire?")