"""Example demonstrating private stock accounts (RSUs, private equity, etc.)"""

import sys
sys.path.append('../src')

from decimal import Decimal
from retirement_planner import RetirementPlanner
from core.portfolio_builder import PortfolioBuilder
from core.multi_account_portfolio import WithdrawalOrder
from core.multi_account_withdrawal import MultiAccountFixedWithdrawal
from core.money import Money


def example_rsu_vesting():
    """Example with RSUs that vest over time"""
    
    print("\n" + "="*60)
    print("RSU VESTING EXAMPLE")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Build portfolio with RSUs vesting at different times
    print("\nBuilding portfolio with RSU vesting schedule...")
    portfolio = (PortfolioBuilder("rsu_demo")
                 .with_age(45)  # Tech worker age 45
                 .with_inflation(Decimal('0.025'))
                 .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                 # Regular accounts
                 .add_cash_account(
                     balance=Decimal('150000'),
                     annual_return=Decimal('0.03'),
                     name="Emergency Fund"
                 )
                 .add_taxable_account(
                     balance=Decimal('500000'),
                     stock_allocation=Decimal('0.80'),
                     name="Brokerage Account"
                 )
                 .add_ira_account(
                     balance=Decimal('800000'),
                     stock_allocation=Decimal('0.70'),
                     name="401k"
                 )
                 # RSUs vesting over time
                 .add_private_stock_account(
                     balance=Decimal('200000'),
                     conversion_year=2,  # Vests in 2 years
                     stock_return=Decimal('0.15'),  # High growth potential
                     stock_volatility=Decimal('0.30'),  # High volatility
                     capital_gains_tax_rate=Decimal('0.15'),
                     name="RSU Grant 2024"
                 )
                 .add_private_stock_account(
                     balance=Decimal('250000'),
                     conversion_year=4,  # Vests in 4 years
                     stock_return=Decimal('0.15'),
                     stock_volatility=Decimal('0.30'),
                     capital_gains_tax_rate=Decimal('0.15'),
                     name="RSU Grant 2025"
                 )
                 .add_private_stock_account(
                     balance=Decimal('300000'),
                     conversion_year=6,  # Vests in 6 years
                     stock_return=Decimal('0.15'),
                     stock_volatility=Decimal('0.30'),
                     capital_gains_tax_rate=Decimal('0.15'),
                     name="RSU Grant 2026"
                 )
                 .build())
    
    # Print portfolio summary
    print("\nInitial Portfolio:")
    print("-" * 40)
    summary = portfolio.get_account_summary()
    for name, balance in summary.items():
        if not name.startswith('total') and not name.startswith('net'):
            print(f"  {name}: {balance}")
    print(f"\nTotal Liquid Assets: {portfolio.get_total_assets()}")
    print(f"Total with RSUs: {portfolio.get_net_worth()}")
    
    # Show vesting schedule
    print("\nRSU Vesting Schedule:")
    print("-" * 40)
    print("  Year 0-1: No RSUs available")
    print("  Year 2: $200k RSUs become liquid")
    print("  Year 4: Additional $250k RSUs become liquid")
    print("  Year 6: Final $300k RSUs become liquid")
    
    # Run simulation
    withdrawal_strategy = MultiAccountFixedWithdrawal(
        initial_withdrawal=Money(Decimal('100000'))  # Living expenses
    )
    
    print("\nRunning simulation with RSU vesting...")
    results = planner.run_simulation(
        portfolio=portfolio,
        withdrawal_strategy=withdrawal_strategy,
        years=20,
        num_simulations=500
    )
    
    print(f"\nResults:")
    print(f"  Success Rate: {results.success_rate:.1f}%")
    print(f"  Median Final Net Worth: {results.median_final_net_worth}")
    
    return portfolio, results


def example_private_equity_liquidity_event():
    """Example with private equity that has a liquidity event"""
    
    print("\n" + "="*60)
    print("PRIVATE EQUITY LIQUIDITY EVENT")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Startup founder with significant private equity
    portfolio = (PortfolioBuilder()
                 .with_age(55)
                 .with_inflation(Decimal('0.03'))
                 .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                 .add_cash_account(
                     balance=Decimal('200000'),
                     name="Cash"
                 )
                 .add_taxable_account(
                     balance=Decimal('300000'),
                     stock_allocation=Decimal('0.70'),
                     name="Public Stocks"
                 )
                 .add_ira_account(
                     balance=Decimal('400000'),
                     name="Retirement Account"
                 )
                 # Large private equity position
                 .add_private_stock_account(
                     balance=Decimal('3000000'),  # $3M private equity
                     conversion_year=5,  # IPO/acquisition in 5 years
                     stock_return=Decimal('0.20'),  # High growth
                     stock_volatility=Decimal('0.40'),  # Very volatile
                     capital_gains_tax_rate=Decimal('0.20'),  # Higher rate
                     name="Startup Equity"
                 )
                 .build())
    
    print("\nFounder Portfolio:")
    print(f"  Liquid Assets: {portfolio.get_total_assets()}")
    print(f"  Private Equity: $3,000,000 (illiquid)")
    print(f"  Liquidity Event: Year 5")
    
    # Conservative withdrawal until liquidity event
    results = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio,
        annual_withdrawal=Decimal('150000'),
        years=15,
        num_simulations=500
    )
    
    print(f"\nResults:")
    print(f"  Success Rate: {results.success_rate:.1f}%")
    print(f"  Median Final: {results.median_final_net_worth}")
    print("\nNote: Must survive on liquid assets until year 5 liquidity event")
    
    return portfolio, results


def example_compare_with_without_private():
    """Compare portfolios with and without private stock"""
    
    print("\n" + "="*60)
    print("COMPARISON: LIQUID vs PRIVATE STOCK")
    print("="*60)
    
    planner = RetirementPlanner()
    initial_wealth = Decimal('2000000')
    
    # Portfolio 1: All liquid
    portfolio_liquid = (PortfolioBuilder("all_liquid")
                        .with_age(50)
                        .with_inflation(Decimal('0.03'))
                        .add_cash_account(Decimal('100000'))
                        .add_taxable_account(
                            balance=Decimal('1900000'),
                            stock_allocation=Decimal('0.80')
                        )
                        .build())
    
    # Portfolio 2: Half in private stock
    portfolio_mixed = (PortfolioBuilder("mixed")
                       .with_age(50)
                       .with_inflation(Decimal('0.03'))
                       .add_cash_account(Decimal('100000'))
                       .add_taxable_account(
                           balance=Decimal('900000'),
                           stock_allocation=Decimal('0.80')
                       )
                       .add_private_stock_account(
                           balance=Decimal('1000000'),
                           conversion_year=7,  # Liquid in 7 years
                           stock_return=Decimal('0.18'),  # Higher return
                           stock_volatility=Decimal('0.35'),  # Higher volatility
                           name="Private Holdings"
                       )
                       .build())
    
    annual_withdrawal = Decimal('80000')
    
    print("\nScenario 1: All Liquid Assets")
    print("-" * 40)
    results_liquid = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio_liquid,
        annual_withdrawal=annual_withdrawal,
        years=25,
        num_simulations=500
    )
    print(f"  Success Rate: {results_liquid.success_rate:.1f}%")
    print(f"  Median Final: {results_liquid.median_final_net_worth}")
    
    print("\nScenario 2: 50% Private Stock (liquid in year 7)")
    print("-" * 40)
    results_mixed = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio_mixed,
        annual_withdrawal=annual_withdrawal,
        years=25,
        num_simulations=500
    )
    print(f"  Success Rate: {results_mixed.success_rate:.1f}%")
    print(f"  Median Final: {results_mixed.median_final_net_worth}")
    
    print("\nAnalysis:")
    print("-" * 40)
    if results_mixed.success_rate > results_liquid.success_rate:
        print("✓ Private stock's higher returns outweigh liquidity constraints")
    else:
        print("✗ Liquidity constraints hurt more than higher returns help")
    
    return results_liquid, results_mixed


def example_tech_employee_compensation():
    """Realistic tech employee with salary, RSUs, and ESPP"""
    
    print("\n" + "="*60)
    print("TECH EMPLOYEE TOTAL COMPENSATION")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Senior tech employee with complex compensation
    portfolio = (PortfolioBuilder()
                 .with_age(35)
                 .with_inflation(Decimal('0.03'))
                 .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                 # Standard accounts
                 .add_cash_account(
                     balance=Decimal('75000'),
                     name="Savings"
                 )
                 .add_taxable_account(
                     balance=Decimal('200000'),
                     stock_allocation=Decimal('0.90'),  # Tech worker = aggressive
                     name="Brokerage"
                 )
                 .add_ira_account(
                     balance=Decimal('300000'),
                     name="401k"
                 )
                 # Income streams
                 .add_income_account(
                     annual_income=Decimal('250000'),  # Base salary
                     start_year=0,
                     duration_years=10,  # Working for 10 more years
                     annual_adjustment=Decimal('0.04'),  # Raises
                     tax_rate=Decimal('0.35'),  # High tax bracket
                     name="Salary"
                 )
                 # RSU vesting schedule (4-year vest)
                 .add_private_stock_account(
                     balance=Decimal('100000'),
                     conversion_year=1,
                     stock_return=Decimal('0.15'),
                     stock_volatility=Decimal('0.30'),
                     name="RSU Year 1"
                 )
                 .add_private_stock_account(
                     balance=Decimal('100000'),
                     conversion_year=2,
                     stock_return=Decimal('0.15'),
                     stock_volatility=Decimal('0.30'),
                     name="RSU Year 2"
                 )
                 .add_private_stock_account(
                     balance=Decimal('100000'),
                     conversion_year=3,
                     stock_return=Decimal('0.15'),
                     stock_volatility=Decimal('0.30'),
                     name="RSU Year 3"
                 )
                 .add_private_stock_account(
                     balance=Decimal('100000'),
                     conversion_year=4,
                     stock_return=Decimal('0.15'),
                     stock_volatility=Decimal('0.30'),
                     name="RSU Year 4"
                 )
                 .build())
    
    print("\nTech Employee Portfolio:")
    print("-" * 40)
    print(f"  Current Savings: {portfolio.get_total_assets()}")
    print(f"  Annual Salary: $250,000 (pre-tax)")
    print(f"  RSU Grants: $400,000 vesting over 4 years")
    print(f"  Total Comp Value: ~$650,000/year for next 4 years")
    
    # Low withdrawal while working, then retirement
    results = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio,
        annual_withdrawal=Decimal('50000'),  # Low expenses while earning
        years=30,
        num_simulations=500
    )
    
    print(f"\nSimulation Results (30 years):")
    print(f"  Success Rate: {results.success_rate:.1f}%")
    print(f"  Median Final: {results.median_final_net_worth}")
    
    return portfolio, results


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRIVATE STOCK ACCOUNT EXAMPLES")
    print("="*60)
    
    # Example 1: RSU vesting
    portfolio1, results1 = example_rsu_vesting()
    
    # Example 2: Private equity liquidity event
    portfolio2, results2 = example_private_equity_liquidity_event()
    
    # Example 3: Compare liquid vs private
    results_liquid, results_mixed = example_compare_with_without_private()
    
    # Example 4: Tech employee compensation
    portfolio4, results4 = example_tech_employee_compensation()
    
    print("\n" + "="*60)
    print("All private stock examples completed!")
    print("="*60)