"""Example usage of the unified retirement planning system"""

import sys
sys.path.append('../src')

from decimal import Decimal
from retirement_planner import RetirementPlanner


def example_basic_simulation():
    """Basic simulation example using simple scenario"""
    print("\n" + "="*60)
    print("BASIC SIMULATION EXAMPLE")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Run a simple simulation (single account, no taxes)
    results = planner.create_simple_scenario(
        initial_portfolio=Decimal('500000'),
        annual_withdrawal=Decimal('20000'),  # 4% withdrawal rate
        years=30,
        mean_return=Decimal('0.10'),  # 10% expected return
        volatility=Decimal('0.18'),
        num_simulations=5000
    )
    
    print(f"\nResults:")
    print(f"  Success Rate: {results.success_rate:.1f}%")
    print(f"  Successful Runs: {len(results.get_successful_runs())}")
    print(f"  Failed Runs: {len([r for r in results.runs if r.depleted])}")
    print(f"  Median Final Net Worth: {results.median_final_net_worth}")
    
    return results


def example_multi_account():
    """Example with multiple account types"""
    print("\n" + "="*60)
    print("MULTI-ACCOUNT EXAMPLE")
    print("="*60)
    
    planner = RetirementPlanner()
    
    results = planner.create_multi_account_scenario(
        cash_balance=Decimal('50000'),      # Emergency fund
        taxable_balance=Decimal('400000'),  # Brokerage
        ira_balance=Decimal('600000'),      # Traditional IRA
        mortgage_balance=Decimal('150000'), # Mortgage
        mortgage_rate=Decimal('0.035'),
        mortgage_years=10,
        annual_expenses=Decimal('55000'),
        current_age=65,
        years=30,
        num_simulations=2000
    )
    
    print(f"\nResults:")
    print(f"  Success Rate: {results.success_rate:.1f}%")
    print(f"  Median Final Net Worth: {results.median_final_net_worth}")
    
    # Show account depletion patterns
    depletion_stats = results.get_account_depletion_stats()
    if depletion_stats:
        print("\nAccount Depletion Patterns:")
        for account_type, stats in depletion_stats.items():
            if 'median_depletion' in stats:
                print(f"  {account_type}: Median depletion year {stats['median_depletion']}")
    
    return results


def example_compare_strategies():
    """Compare different withdrawal strategies"""
    print("\n" + "="*60)
    print("STRATEGY COMPARISON")
    print("="*60)
    
    planner = RetirementPlanner()
    
    scenarios = planner.compare_strategies(
        initial_portfolio=Decimal('1000000'),
        years=30,
        num_simulations=2000,
        current_age=65
    )
    
    print("\nStrategy Success Rates:")
    print("-" * 40)
    for name, results in scenarios.items():
        print(f"{name:20} {results.success_rate:5.1f}%")
    
    print("\nMedian Final Net Worth:")
    print("-" * 40)
    for name, results in scenarios.items():
        print(f"{name:20} {results.median_final_net_worth}")
    
    return scenarios


def example_sensitivity_analysis():
    """Perform sensitivity analysis on key parameters"""
    print("\n" + "="*60)
    print("SENSITIVITY ANALYSIS")
    print("="*60)
    
    planner = RetirementPlanner()
    base_portfolio = Decimal('1000000')
    
    # Test different withdrawal rates
    print("\nWithdrawal Rate Sensitivity:")
    print("-" * 40)
    withdrawal_rates = [Decimal('30000'), Decimal('35000'), Decimal('40000'), 
                       Decimal('45000'), Decimal('50000'), Decimal('55000')]
    
    for withdrawal in withdrawal_rates:
        results = planner.create_simple_scenario(
            initial_portfolio=base_portfolio,
            annual_withdrawal=withdrawal,
            years=30,
            num_simulations=1000
        )
        rate = (withdrawal / base_portfolio) * Decimal('100')
        print(f"  {rate:4.1f}% withdrawal → {results.success_rate:5.1f}% success")
    
    # Test different time horizons
    print("\nTime Horizon Sensitivity:")
    print("-" * 40)
    time_horizons = [20, 25, 30, 35, 40]
    
    for years in time_horizons:
        results = planner.create_simple_scenario(
            initial_portfolio=base_portfolio,
            annual_withdrawal=Decimal('40000'),
            years=years,
            num_simulations=1000
        )
        print(f"  {years:2d} years → {results.success_rate:5.1f}% success")
    
    # Test different return assumptions
    print("\nReturn Assumption Sensitivity:")
    print("-" * 40)
    return_assumptions = [Decimal('0.05'), Decimal('0.06'), Decimal('0.07'), 
                         Decimal('0.08'), Decimal('0.09')]
    
    for mean_return in return_assumptions:
        results = planner.create_simple_scenario(
            initial_portfolio=base_portfolio,
            annual_withdrawal=Decimal('40000'),
            years=30,
            mean_return=mean_return,
            num_simulations=1000
        )
        print(f"  {mean_return*100:3.0f}% returns → {results.success_rate:5.1f}% success")


def example_dynamic_withdrawal():
    """Test dynamic withdrawal strategy"""
    print("\n" + "="*60)
    print("DYNAMIC WITHDRAWAL STRATEGY")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Compare fixed vs dynamic
    fixed_results = planner.create_simple_scenario(
        initial_portfolio=Decimal('1000000'),
        annual_withdrawal=Decimal('40000'),
        years=30,
        num_simulations=2000
    )
    
    dynamic_results = planner.create_dynamic_scenario(
        initial_portfolio=Decimal('1000000'),
        base_withdrawal_rate=Decimal('4'),
        min_rate=Decimal('3'),
        max_rate=Decimal('5'),
        years=30,
        num_simulations=2000
    )
    
    print("\nStrategy Comparison:")
    print("-" * 40)
    print(f"Fixed 4% Strategy:")
    print(f"  Success Rate: {fixed_results.success_rate:.1f}%")
    print(f"  Median Final: {fixed_results.median_final_net_worth}")
    
    print(f"\nDynamic 3-5% Strategy:")
    print(f"  Success Rate: {dynamic_results.success_rate:.1f}%")
    print(f"  Median Final: {dynamic_results.median_final_net_worth}")
    
    return fixed_results, dynamic_results


if __name__ == "__main__":
    # Run all examples
    print("\n" + "="*60)
    print("UNIFIED RETIREMENT PLANNING EXAMPLES")
    print("="*60)
    
    # Basic simulation
    basic_results = example_basic_simulation()
    
    # Multi-account simulation
    multi_results = example_multi_account()
    
    # Strategy comparison
    strategy_results = example_compare_strategies()
    
    # Sensitivity analysis
    example_sensitivity_analysis()
    
    # Dynamic withdrawal
    fixed, dynamic = example_dynamic_withdrawal()
    
    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60)