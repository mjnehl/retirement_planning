"""Example demonstrating inheritance accounts in retirement planning"""

import sys
sys.path.append('../src')

from decimal import Decimal
from retirement_planner import RetirementPlanner
from core.portfolio_builder import PortfolioBuilder
from core.multi_account_portfolio import WithdrawalOrder
from core.multi_account_withdrawal import MultiAccountFixedWithdrawal
from core.money import Money


def example_single_inheritance():
    """Example with a single expected inheritance"""
    
    print("\n" + "="*60)
    print("SINGLE INHERITANCE EXAMPLE")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Couple retiring at 65, expecting inheritance from parent
    print("\nBuilding portfolio with expected inheritance...")
    portfolio = (PortfolioBuilder("inheritance_demo")
                 .with_age(65)
                 .with_inflation(Decimal('0.025'))
                 .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                 # Current assets
                 .add_cash_account(
                     balance=Decimal('100000'),
                     annual_return=Decimal('0.03'),
                     name="Emergency Fund"
                 )
                 .add_taxable_account(
                     balance=Decimal('400000'),
                     stock_allocation=Decimal('0.70'),
                     name="Brokerage Account"
                 )
                 .add_ira_account(
                     balance=Decimal('600000'),
                     stock_allocation=Decimal('0.60'),
                     name="401k/IRA"
                 )
                 # Expected inheritance
                 .add_inheritance_account(
                     expected_amount=Decimal('500000'),  # $500k inheritance
                     inheritance_year=10,  # Expected in 10 years (parent is 85)
                     asset_allocation=Decimal('0.50'),  # Conservative portfolio
                     growth_rate=Decimal('0.05'),  # 5% growth (conservative)
                     volatility=Decimal('0.10'),  # 10% volatility (low)
                     is_step_up_basis=True,  # Step-up basis (no capital gains)
                     name="Parent's Estate"
                 )
                 .build())
    
    # Print portfolio summary
    print("\nCurrent Portfolio:")
    print("-" * 40)
    print(f"  Cash: $100,000")
    print(f"  Taxable: $400,000")
    print(f"  IRA: $600,000")
    print(f"  Total Current Assets: {portfolio.get_total_assets()}")
    print(f"\nExpected Inheritance:")
    print(f"  Amount: $500,000")
    print(f"  Expected Year: 10 (age 75)")
    print(f"  Tax Treatment: Step-up basis (minimal taxes)")
    
    # Run simulation
    withdrawal_strategy = MultiAccountFixedWithdrawal(
        initial_withdrawal=Money(Decimal('60000'))  # Annual expenses
    )
    
    print("\nRunning simulation with expected inheritance...")
    results = planner.run_simulation(
        portfolio=portfolio,
        withdrawal_strategy=withdrawal_strategy,
        years=30,
        num_simulations=500
    )
    
    print(f"\nResults (30 years):")
    print(f"  Success Rate: {results.success_rate:.1f}%")
    print(f"  Median Final Net Worth: {results.median_final_net_worth}")
    
    return portfolio, results


def example_multiple_inheritances():
    """Example with multiple expected inheritances from different sources"""
    
    print("\n" + "="*60)
    print("MULTIPLE INHERITANCES EXAMPLE")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Build portfolio with multiple inheritances
    portfolio = (PortfolioBuilder()
                 .with_age(55)  # Early retirement
                 .with_inflation(Decimal('0.03'))
                 .add_cash_account(
                     balance=Decimal('75000'),
                     name="Cash"
                 )
                 .add_taxable_account(
                     balance=Decimal('300000'),
                     stock_allocation=Decimal('0.75'),
                     name="Investments"
                 )
                 .add_ira_account(
                     balance=Decimal('500000'),
                     name="Retirement Accounts"
                 )
                 # Multiple inheritances with different growth profiles
                 .add_inheritance_account(
                     expected_amount=Decimal('300000'),
                     inheritance_year=5,  # Parent 1 (age 80)
                     growth_rate=Decimal('0.06'),  # Balanced portfolio
                     volatility=Decimal('0.12'),
                     name="Mother's Estate"
                 )
                 .add_inheritance_account(
                     expected_amount=Decimal('250000'),
                     inheritance_year=8,  # Parent 2 (age 82)
                     growth_rate=Decimal('0.07'),  # Slightly more aggressive
                     volatility=Decimal('0.15'),
                     name="Father's Estate"
                 )
                 .add_inheritance_account(
                     expected_amount=Decimal('150000'),
                     inheritance_year=15,  # Aunt (age 85)
                     asset_allocation=Decimal('0.40'),  # More conservative
                     growth_rate=Decimal('0.04'),  # Conservative growth
                     volatility=Decimal('0.08'),  # Low volatility
                     name="Aunt's Estate"
                 )
                 .build())
    
    print("\nPortfolio with Multiple Inheritances:")
    print("-" * 40)
    print(f"  Current Assets: {portfolio.get_total_assets()}")
    print(f"\nExpected Inheritances:")
    print(f"  Year 5: $300,000 (Mother)")
    print(f"  Year 8: $250,000 (Father)")
    print(f"  Year 15: $150,000 (Aunt)")
    print(f"  Total Expected: $700,000")
    
    # Conservative withdrawal until inheritances arrive
    results = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio,
        annual_withdrawal=Decimal('50000'),
        years=35,
        num_simulations=500
    )
    
    print(f"\nResults (35 years):")
    print(f"  Success Rate: {results.success_rate:.1f}%")
    print(f"  Median Final: {results.median_final_net_worth}")
    
    return portfolio, results


def example_compare_with_without_inheritance():
    """Compare retirement plans with and without expected inheritance"""
    
    print("\n" + "="*60)
    print("COMPARISON: WITH vs WITHOUT INHERITANCE")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Base portfolio without inheritance
    portfolio_no_inheritance = (PortfolioBuilder("no_inheritance")
                                .with_age(65)
                                .with_inflation(Decimal('0.03'))
                                .add_cash_account(Decimal('50000'))
                                .add_taxable_account(Decimal('350000'))
                                .add_ira_account(Decimal('500000'))
                                .build())
    
    # Same portfolio with expected inheritance
    portfolio_with_inheritance = (PortfolioBuilder("with_inheritance")
                                  .with_age(65)
                                  .with_inflation(Decimal('0.03'))
                                  .add_cash_account(Decimal('50000'))
                                  .add_taxable_account(Decimal('350000'))
                                  .add_ira_account(Decimal('500000'))
                                  .add_inheritance_account(
                                      expected_amount=Decimal('400000'),
                                      inheritance_year=7,  # Expected at age 72
                                      name="Expected Inheritance"
                                  )
                                  .build())
    
    annual_expenses = Decimal('55000')
    
    print("\nScenario 1: No Inheritance Expected")
    print("-" * 40)
    print(f"  Starting Assets: $900,000")
    results_no_inheritance = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio_no_inheritance,
        annual_withdrawal=annual_expenses,
        years=30,
        num_simulations=500
    )
    print(f"  Success Rate: {results_no_inheritance.success_rate:.1f}%")
    print(f"  Median Final: {results_no_inheritance.median_final_net_worth}")
    
    print("\nScenario 2: With $400k Inheritance (Year 7)")
    print("-" * 40)
    print(f"  Starting Assets: $900,000")
    print(f"  Expected Inheritance: $400,000 at age 72")
    results_with_inheritance = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio_with_inheritance,
        annual_withdrawal=annual_expenses,
        years=30,
        num_simulations=500
    )
    print(f"  Success Rate: {results_with_inheritance.success_rate:.1f}%")
    print(f"  Median Final: {results_with_inheritance.median_final_net_worth}")
    
    print("\nImpact of Expected Inheritance:")
    print("-" * 40)
    success_improvement = results_with_inheritance.success_rate - results_no_inheritance.success_rate
    print(f"  Success Rate Improvement: {success_improvement:.1f}%")
    
    if success_improvement > 0:
        print("  ✓ Inheritance significantly improves retirement security")
    else:
        print("  ✗ Current assets alone may be sufficient")
    
    return results_no_inheritance, results_with_inheritance


def example_early_retirement_with_inheritance():
    """Example of planning early retirement counting on future inheritance"""
    
    print("\n" + "="*60)
    print("EARLY RETIREMENT WITH INHERITANCE PLANNING")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Person wanting to retire early, counting on inheritance
    portfolio = (PortfolioBuilder()
                 .with_age(50)  # Retire at 50
                 .with_inflation(Decimal('0.03'))
                 .add_cash_account(
                     balance=Decimal('100000'),
                     name="Cash Reserve"
                 )
                 .add_taxable_account(
                     balance=Decimal('600000'),
                     stock_allocation=Decimal('0.80'),  # Aggressive allocation
                     name="Investment Portfolio"
                 )
                 .add_ira_account(
                     balance=Decimal('400000'),
                     name="401k"
                 )
                 # Expected inheritances that enable early retirement
                 .add_inheritance_account(
                     expected_amount=Decimal('800000'),
                     inheritance_year=15,  # Parents are 75, expected at age 65
                     asset_allocation=Decimal('0.60'),
                     name="Parents' Estate"
                 )
                 .add_inheritance_account(
                     expected_amount=Decimal('200000'),
                     inheritance_year=20,  # Uncle's estate
                     name="Uncle's Estate"
                 )
                 .build())
    
    print("\nEarly Retirement Portfolio (Age 50):")
    print("-" * 40)
    print(f"  Current Assets: {portfolio.get_total_assets()}")
    print(f"  Expected Inheritances:")
    print(f"    - $800k at age 65 (parents)")
    print(f"    - $200k at age 70 (uncle)")
    print(f"  Total Future Value: ~$1M")
    
    # Higher withdrawal rate for early retirement
    print("\nStrategy: Use current assets until inheritances arrive")
    
    results = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio,
        annual_withdrawal=Decimal('70000'),  # Higher expenses
        years=40,  # Long retirement
        num_simulations=500
    )
    
    print(f"\nSimulation Results (40 years):")
    print(f"  Success Rate: {results.success_rate:.1f}%")
    print(f"  Median Final: {results.median_final_net_worth}")
    
    if results.success_rate > 90:
        print("\n✓ Early retirement is feasible with expected inheritances")
    elif results.success_rate > 75:
        print("\n⚠ Early retirement possible but risky")
    else:
        print("\n✗ Early retirement too risky even with inheritances")
    
    return portfolio, results


def example_inheritance_timing_sensitivity():
    """Test sensitivity to inheritance timing"""
    
    print("\n" + "="*60)
    print("INHERITANCE TIMING SENSITIVITY")
    print("="*60)
    
    planner = RetirementPlanner()
    base_assets = {
        'cash': Decimal('75000'),
        'taxable': Decimal('400000'),
        'ira': Decimal('500000')
    }
    inheritance_amount = Decimal('500000')
    annual_expenses = Decimal('60000')
    
    # Test different inheritance timings
    timings = [5, 10, 15, 20]
    results_by_timing = {}
    
    print("\nTesting different inheritance timings...")
    print("-" * 40)
    
    for years_until in timings:
        portfolio = (PortfolioBuilder(f"timing_{years_until}")
                     .with_age(65)
                     .with_inflation(Decimal('0.03'))
                     .add_cash_account(base_assets['cash'])
                     .add_taxable_account(base_assets['taxable'])
                     .add_ira_account(base_assets['ira'])
                     .add_inheritance_account(
                         expected_amount=inheritance_amount,
                         inheritance_year=years_until,
                         name=f"Inheritance Year {years_until}"
                     )
                     .build())
        
        results = planner.run_simulation_with_fixed_withdrawal(
            portfolio=portfolio,
            annual_withdrawal=annual_expenses,
            years=30,
            num_simulations=300
        )
        
        results_by_timing[years_until] = results.success_rate
        print(f"  Year {years_until:2d} (Age {65+years_until}): {results.success_rate:.1f}% success")
    
    print("\nAnalysis:")
    print("-" * 40)
    early_better = results_by_timing[5] - results_by_timing[20]
    if early_better > 10:
        print(f"✓ Earlier inheritance significantly better (+{early_better:.1f}%)")
    elif early_better > 0:
        print(f"→ Earlier inheritance moderately better (+{early_better:.1f}%)")
    else:
        print("✗ Timing makes little difference with these assets")
    
    return results_by_timing


if __name__ == "__main__":
    print("\n" + "="*60)
    print("INHERITANCE ACCOUNT EXAMPLES")
    print("="*60)
    
    # Example 1: Single inheritance
    portfolio1, results1 = example_single_inheritance()
    
    # Example 2: Multiple inheritances
    portfolio2, results2 = example_multiple_inheritances()
    
    # Example 3: Compare with/without inheritance
    results_no, results_with = example_compare_with_without_inheritance()
    
    # Example 4: Early retirement with inheritance
    portfolio4, results4 = example_early_retirement_with_inheritance()
    
    # Example 5: Timing sensitivity
    timing_results = example_inheritance_timing_sensitivity()
    
    print("\n" + "="*60)
    print("All inheritance examples completed!")
    print("="*60)