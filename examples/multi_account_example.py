"""Example demonstrating flexible portfolio building and simulation"""

import sys
sys.path.append('../src')

from decimal import Decimal
from retirement_planner import RetirementPlanner
from core.portfolio_builder import PortfolioBuilder, create_conservative_portfolio, create_aggressive_portfolio
from core.multi_account_portfolio import WithdrawalOrder
from core.multi_account_withdrawal import (
    MultiAccountFixedWithdrawal,
    MultiAccountPercentageWithdrawal,
    MultiAccountDynamicWithdrawal
)
from core.money import Money
from core.accounts import CashAccount, TaxableAccount, IRAAccount, Mortgage


def example_manual_portfolio_building():
    """Build a portfolio manually with custom accounts"""
    
    print("\n" + "="*60)
    print("MANUAL PORTFOLIO BUILDING EXAMPLE")
    print("="*60)
    
    # Create planner
    planner = RetirementPlanner()
    
    # Build portfolio step by step
    print("\nBuilding custom portfolio...")
    portfolio = (PortfolioBuilder("my_portfolio", "user_001")
                 .with_age(62)
                 .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                 .add_cash_account(
                     balance=Decimal('50000'),
                     annual_return=Decimal('0.03'),
                     name="Cash Buffer"
                 )
                 .add_taxable_account(
                     balance=Decimal('300000'),
                     stock_allocation=Decimal('0.75'),
                     stock_return=Decimal('0.10'),  # Custom return
                     stock_volatility=Decimal('0.16'),  # Custom volatility
                     dividend_yield=Decimal('0.02'),
                     capital_gains_tax_rate=Decimal('0.15'),
                     name="Etrade Taxable"
                 )
                 .add_ira_account(
                     balance=Decimal('200000'),
                     stock_allocation=Decimal('0.70'),
                     stock_return=Decimal('0.10'),  # Custom return
                     stock_volatility=Decimal('0.16'),  # Custom volatility
                     ordinary_income_tax_rate=Decimal('0.24'),  # 24% tax bracket
                     name="Etrade Trad IRA"
                 )
                 .add_mortgage(
                     balance=Decimal('570000'),
                     interest_rate=Decimal('0.06'),
                     remaining_years=23,
                     name="Home Mortgage"
                 )
                 .build())
    
    # Print portfolio summary
    print("\nPortfolio Created:")
    summary = portfolio.get_account_summary()
    for name, balance in summary.items():
        if not name.startswith('total') and not name.startswith('net'):
            print(f"  {name}: {balance}")
    print(f"\nNet Worth: {portfolio.get_net_worth()}")
    print(f"Total Assets: {portfolio.get_total_assets()}")
    print(f"Total Liabilities: {portfolio.get_total_liabilities()}")
    
    # Create withdrawal strategy
    withdrawal_strategy = MultiAccountFixedWithdrawal(
        initial_withdrawal=Money(Decimal('50000')),
        inflation_rate=Decimal('0.025'),
        withdrawal_order=WithdrawalOrder.TAX_EFFICIENT
    )
    
    # Run simulation
    print("\nRunning simulation...")
    results = planner.run_simulation(
        portfolio=portfolio,
        withdrawal_strategy=withdrawal_strategy,
        years=30,
        num_simulations=1000
    )
    
    # Print results
    planner.print_results_summary(results, detailed=True)
    
    return portfolio, results


def example_custom_account_creation():
    """Create a portfolio with completely custom account types"""
    
    print("\n" + "="*60)
    print("CUSTOM ACCOUNT CREATION EXAMPLE")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Create custom accounts with specific parameters
    print("\nCreating custom accounts...")
    
    # Create a high-yield savings account
    savings = CashAccount(
        account_id="savings_001",
        balance=Money(Decimal('100000')),
        annual_return=Decimal('0.045'),  # 4.5% high-yield
        name="Marcus Savings"
    )
    
    # Create a conservative taxable account
    conservative_taxable = TaxableAccount(
        account_id="conservative_001",
        balance=Money(Decimal('250000')),
        stock_allocation=Decimal('0.40'),  # 40% stocks, 60% bonds
        name="Conservative Portfolio"
    )
    conservative_taxable.stock_return = Decimal('0.06')
    conservative_taxable.stock_volatility = Decimal('0.10')
    conservative_taxable.dividend_yield = Decimal('0.03')
    
    # Create an aggressive taxable account
    aggressive_taxable = TaxableAccount(
        account_id="aggressive_001",
        balance=Money(Decimal('150000')),
        stock_allocation=Decimal('0.95'),  # 95% stocks
        name="Growth Portfolio"
    )
    aggressive_taxable.stock_return = Decimal('0.12')
    aggressive_taxable.stock_volatility = Decimal('0.25')
    
    # Create IRA with custom tax rate
    ira = IRAAccount(
        account_id="ira_001",
        balance=Money(Decimal('400000')),
        stock_allocation=Decimal('0.70'),
        name="Traditional IRA"
    )
    ira.ordinary_income_tax_rate = Decimal('0.22')  # 22% bracket
    
    # Build portfolio with custom accounts
    portfolio = (PortfolioBuilder()
                 .with_age(65)
                 .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                 .add_custom_account(savings)
                 .add_custom_account(conservative_taxable)
                 .add_custom_account(aggressive_taxable)
                 .add_custom_account(ira)
                 .build())
    
    print("\nCustom Portfolio Created:")
    for account_id, account in portfolio.accounts.items():
        print(f"  {account.name}: {account.get_balance()}")
    print(f"\nTotal Portfolio Value: {portfolio.get_total_assets()}")
    
    # Run simulation with percentage withdrawal
    results = planner.run_simulation_with_percentage_withdrawal(
        portfolio=portfolio,
        withdrawal_rate=Decimal('4'),  # 4% withdrawal rate
        years=30,
        num_simulations=1000
    )
    
    print(f"\nSimulation Results:")
    print(f"  Success Rate: {results.success_rate:.1f}%")
    print(f"  Median Final Net Worth: {results.median_final_net_worth}")
    
    return portfolio, results


def example_strategy_comparison():
    """Compare multiple withdrawal strategies on the same portfolio"""
    
    print("\n" + "="*60)
    print("WITHDRAWAL STRATEGY COMPARISON")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Build a realistic retirement portfolio
    portfolio = (PortfolioBuilder()
                 .with_age(65)
                 .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                 .add_cash_account(Decimal('60000'), name="Cash Reserve")
                 .add_taxable_account(Decimal('500000'), stock_allocation=Decimal('0.70'), name="Brokerage")
                 .add_ira_account(Decimal('700000'), stock_allocation=Decimal('0.60'), name="IRA")
                 .build())
    
    print("\nPortfolio Value: ", portfolio.get_total_assets())
    
    # Define multiple strategies to compare
    strategies = {
        "Fixed 3%": MultiAccountFixedWithdrawal(
            initial_withdrawal=Money(Decimal('38400')),  # 3% of 1.28M
            inflation_rate=Decimal('0.03')
        ),
        "Fixed 4%": MultiAccountFixedWithdrawal(
            initial_withdrawal=Money(Decimal('51200')),  # 4% of 1.28M
            inflation_rate=Decimal('0.03')
        ),
        "Percentage 4%": MultiAccountPercentageWithdrawal(
            withdrawal_rate=Decimal('4'),
            min_withdrawal=Money(Decimal('30000')),
            max_withdrawal=Money(Decimal('80000'))
        ),
        "Dynamic 3-5%": MultiAccountDynamicWithdrawal(
            base_withdrawal=Money(Decimal('50000')),
            min_rate=Decimal('3'),
            max_rate=Decimal('5')
        )
    }
    
    # Compare strategies
    print("\nComparing withdrawal strategies...")
    comparison_results = planner.compare_strategies_for_portfolio(
        portfolio=portfolio,
        strategies=strategies,
        years=30,
        num_simulations=1000
    )
    
    # Print comparison table
    print("\n" + "="*60)
    print("STRATEGY COMPARISON RESULTS")
    print("="*60)
    print(f"{'Strategy':<20} {'Success Rate':>15} {'Median Final':>20}")
    print("-" * 55)
    
    for name, results in comparison_results.items():
        print(f"{name:<20} {results.success_rate:>14.1f}% {str(results.median_final_net_worth):>20}")
    
    # Find best strategy
    best_strategy = max(comparison_results.items(), key=lambda x: x[1].success_rate)
    print(f"\nBest Strategy: {best_strategy[0]} with {best_strategy[1].success_rate:.1f}% success rate")
    
    return comparison_results


def example_conservative_vs_aggressive():
    """Compare conservative vs aggressive portfolio allocations"""
    
    print("\n" + "="*60)
    print("CONSERVATIVE VS AGGRESSIVE PORTFOLIOS")
    print("="*60)
    
    planner = RetirementPlanner()
    total_value = Decimal('1000000')
    
    # Create conservative portfolio
    conservative = create_conservative_portfolio(total_value, age=65)
    
    # Create aggressive portfolio  
    aggressive = create_aggressive_portfolio(total_value, age=65)
    
    # Same withdrawal strategy for both
    withdrawal_strategy = MultiAccountFixedWithdrawal(
        initial_withdrawal=Money(Decimal('40000')),  # 4% withdrawal
        inflation_rate=Decimal('0.03')
    )
    
    print("\nRunning Conservative Portfolio Simulation...")
    conservative_results = planner.run_simulation(
        portfolio=conservative,
        withdrawal_strategy=withdrawal_strategy,
        years=30,
        num_simulations=1000
    )
    
    print("Running Aggressive Portfolio Simulation...")
    aggressive_results = planner.run_simulation(
        portfolio=aggressive,
        withdrawal_strategy=withdrawal_strategy,
        years=30,
        num_simulations=1000
    )
    
    print("\n" + "="*60)
    print("PORTFOLIO COMPARISON RESULTS")
    print("="*60)
    
    print("\nConservative Portfolio:")
    print(f"  Success Rate: {conservative_results.success_rate:.1f}%")
    print(f"  Median Final: {conservative_results.median_final_net_worth}")
    
    print("\nAggressive Portfolio:")
    print(f"  Success Rate: {aggressive_results.success_rate:.1f}%")
    print(f"  Median Final: {aggressive_results.median_final_net_worth}")
    
    # Determine winner
    if conservative_results.success_rate > aggressive_results.success_rate:
        print("\n✓ Conservative portfolio has higher success rate")
    else:
        print("\n✓ Aggressive portfolio has higher success rate")
    
    return conservative_results, aggressive_results


if __name__ == "__main__":
    print("\n" + "="*60)
    print("FLEXIBLE PORTFOLIO BUILDING EXAMPLES")
    print("="*60)
    
    # Example 1: Manual portfolio building
    portfolio1, results1 = example_manual_portfolio_building()
    
    # # Example 2: Custom account creation
    # portfolio2, results2 = example_custom_account_creation()
    
    # # Example 3: Strategy comparison
    # comparison_results = example_strategy_comparison()
    
    # # Example 4: Conservative vs Aggressive
    # conservative_results, aggressive_results = example_conservative_vs_aggressive()
    
    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60)