"""Example demonstrating multiple income sources in retirement planning"""

import sys
sys.path.append('../src')

from decimal import Decimal
from retirement_planner import RetirementPlanner
from core.portfolio_builder import PortfolioBuilder
from core.multi_account_portfolio import WithdrawalOrder
from core.multi_account_withdrawal import MultiAccountFixedWithdrawal
from core.money import Money


def example_income_sources():
    """Example with multiple income sources during retirement"""
    
    print("\n" + "="*60)
    print("MULTIPLE INCOME SOURCES EXAMPLE")
    print("="*60)
    
    # Create planner
    planner = RetirementPlanner()
    
    # Build portfolio with multiple income sources
    print("\nBuilding portfolio with income sources...")
    portfolio = (PortfolioBuilder("income_demo", "john_smith")
                 .with_age(62)  # Starting at age 62
                 .with_inflation(Decimal('0.025'), Decimal('0.008'))  # 2.5% inflation, 0.8% volatility
                 .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                 # Add regular accounts
                 .add_cash_account(
                     balance=Decimal('100000'),
                     annual_return=Decimal('0.03'),
                     name="Emergency Fund"
                 )
                 .add_taxable_account(
                     balance=Decimal('400000'),
                     stock_allocation=Decimal('0.70'),
                     name="Investment Account"
                 )
                 .add_ira_account(
                     balance=Decimal('600000'),
                     stock_allocation=Decimal('0.60'),
                     name="401k Rollover"
                 )
                 # Add income sources
                 .add_income_account(
                     annual_income=Decimal('85000'),
                     start_year=0,  # Starts immediately (working part-time)
                     duration_years=3,  # Work for 3 more years
                     annual_adjustment=Decimal('0.03'),  # 3% annual raises
                     tax_rate=Decimal('0.25'),
                     name="Part-time Salary"
                 )
                 .add_income_account(
                     annual_income=Decimal('36000'),
                     start_year=8,  # Social Security at age 70 (62 + 8)
                     duration_years=30,  # Lifetime benefit
                     annual_adjustment=Decimal('0.025'),  # COLA adjustments
                     tax_rate=Decimal('0.10'),  # Lower tax on SS
                     name="Social Security"
                 )
                 .add_income_account(
                     annual_income=Decimal('24000'),
                     start_year=3,  # Pension starts at 65
                     duration_years=30,  # Lifetime benefit
                     annual_adjustment=Decimal('0.02'),  # 2% annual increase
                     tax_rate=Decimal('0.22'),
                     name="Company Pension"
                 )
                 .add_income_account(
                     annual_income=Decimal('12000'),
                     start_year=5,  # Rental income starts in 5 years
                     duration_years=15,  # Plan to sell property after 15 years
                     annual_adjustment=Decimal('0.03'),  # Rent increases
                     tax_rate=Decimal('0.15'),  # After deductions
                     name="Rental Income"
                 )
                 .add_mortgage(
                     balance=Decimal('180000'),
                     interest_rate=Decimal('0.04'),
                     remaining_years=10,
                     name="Primary Residence"
                 )
                 .build())
    
    # Print portfolio summary
    print("\nPortfolio Summary:")
    print("-" * 40)
    summary = portfolio.get_account_summary()
    for name, balance in summary.items():
        if not name.startswith('total') and not name.startswith('net'):
            print(f"  {name}: {balance}")
    print(f"\nStarting Net Worth: {portfolio.get_net_worth()}")
    
    # Show income schedule
    print("\nIncome Schedule:")
    print("-" * 40)
    for year in [0, 3, 5, 8, 10, 15, 20]:
        gross, after_tax = portfolio.get_annual_income(year)
        age = portfolio.current_age + year
        print(f"  Year {year:2d} (Age {age}): {after_tax} after-tax")
    
    # Create withdrawal strategy - lower initial withdrawal due to income
    withdrawal_strategy = MultiAccountFixedWithdrawal(
        initial_withdrawal=Money(Decimal('40000')),  # Lower withdrawal while working
        # inflation_rate will use portfolio's rate (2.5%)
    )
    
    # Run simulation
    print("\nRunning simulation with income sources...")
    results = planner.run_simulation(
        portfolio=portfolio,
        withdrawal_strategy=withdrawal_strategy,
        years=35,
        num_simulations=1000
    )
    
    # Print results
    print("\n" + "="*60)
    print("SIMULATION RESULTS")
    print("="*60)
    print(f"Success Rate: {results.success_rate:.1f}%")
    print(f"Median Final Net Worth: {results.median_final_net_worth}")
    
    # Analyze by phase
    successful_runs = results.get_successful_runs()
    if successful_runs:
        print("\nPhase Analysis:")
        print("-" * 40)
        print("Phase 1 (62-65): Working part-time + portfolio")
        print("Phase 2 (65-70): Pension + portfolio")  
        print("Phase 3 (70+): Social Security + pension + portfolio")
    
    return portfolio, results


def example_early_retirement_with_bridge():
    """Example of early retirement with bridge income until Social Security"""
    
    print("\n" + "="*60)
    print("EARLY RETIREMENT WITH BRIDGE INCOME")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Early retirement at 55 with bridge income
    portfolio = (PortfolioBuilder()
                 .with_age(62)
                 .with_inflation(Decimal('0.03'))
                 .add_cash_account(
                     balance=Decimal('150000'),
                     name="Cash Reserve"
                 )
                 .add_taxable_account(
                     balance=Decimal('800000'),
                     stock_allocation=Decimal('0.75'),
                     name="Brokerage"
                 )
                 .add_ira_account(
                     balance=Decimal('1200000'),
                     stock_allocation=Decimal('0.65'),
                     name="401k/IRA"
                 )
                 # Bridge income from consulting
                 .add_income_account(
                     annual_income=Decimal('60000'),
                     start_year=0,
                     duration_years=7,  # Until age 62
                     annual_adjustment=Decimal('0.025'),
                     tax_rate=Decimal('0.30'),  # Self-employment taxes
                     name="Consulting Income"
                 )
                 # Early Social Security at 62
                 .add_income_account(
                     annual_income=Decimal('24000'),
                     start_year=7,  # Age 62
                     duration_years=35,
                     annual_adjustment=Decimal('0.025'),
                     tax_rate=Decimal('0.10'),
                     name="Social Security (Early)"
                 )
                 # Spouse's Social Security at 67
                 .add_income_account(
                     annual_income=Decimal('20000'),
                     start_year=12,  # Age 67
                     duration_years=30,
                     annual_adjustment=Decimal('0.025'),
                     tax_rate=Decimal('0.10'),
                     name="Spouse Social Security"
                 )
                 .build())
    
    print("\nEarly Retirement Portfolio:")
    print(f"  Starting Age: 55")
    print(f"  Net Worth: {portfolio.get_net_worth()}")
    print(f"  Bridge Income: 7 years of consulting")
    print(f"  Social Security: Starting at 62")
    
    # Higher withdrawal needs in early retirement
    results = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio,
        annual_withdrawal=Decimal('80000'),
        years=40,  # Longer retirement
        num_simulations=1000
    )
    
    print(f"\nResults:")
    print(f"  Success Rate: {results.success_rate:.1f}%")
    print(f"  Median Final: {results.median_final_net_worth}")
    
    return portfolio, results


def example_compare_with_without_income():
    """Compare retirement with and without additional income sources"""
    
    print("\n" + "="*60)
    print("COMPARISON: WITH vs WITHOUT INCOME")
    print("="*60)
    
    planner = RetirementPlanner()
    
    # Base portfolio without income
    portfolio_no_income = (PortfolioBuilder("no_income")
                           .with_age(62)
                           .with_inflation(Decimal('0.03'),Decimal(0.008))
                           .add_cash_account(Decimal('50000'))
                           .add_taxable_account(Decimal('500000'))
                           .add_ira_account(Decimal('800000'))
                           .build())
    
    # Same portfolio with Social Security and pension
    portfolio_with_income = (PortfolioBuilder("with_income")
                             .with_age(65)
                             .with_inflation(Decimal('0.03'),Decimal('0.008'))
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
                            .add_income_account(
                                 annual_income=Decimal('32400'),
                                 start_year=0,
                                 duration_years=30,
                                 annual_adjustment=Decimal('0.025'),
                                 tax_rate=Decimal('0.12'),
                                 name="Social Security"
                             )                             
                             .build())
    
    # Same withdrawal needs
    annual_expenses = Decimal('70000')
    
    print("\nScenario 1: No Additional Income")
    print("-" * 40)
    results_no_income = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio_no_income,
        annual_withdrawal=annual_expenses,
        years=30,
        num_simulations=1000
    )
    print(f"  Success Rate: {results_no_income.success_rate:.1f}%")
    print(f"  Median Final: {results_no_income.median_final_net_worth}")
    
    print("\nScenario 2: With SS + Pension ($50k/year)")
    print("-" * 40)
    results_with_income = planner.run_simulation_with_fixed_withdrawal(
        portfolio=portfolio_with_income,
        annual_withdrawal=annual_expenses,
        years=30,
        num_simulations=1000
    )
    print(f"  Success Rate: {results_with_income.success_rate:.1f}%")
    print(f"  Median Final: {results_with_income.median_final_net_worth}")
    
    print("\nImpact of Guaranteed Income:")
    print("-" * 40)
    success_improvement = results_with_income.success_rate - results_no_income.success_rate
    print(f"  Success Rate Improvement: {success_improvement:.1f}%")
    
    # Calculate effective withdrawal reduction
    gross_income, after_tax = portfolio_with_income.get_annual_income(0)
    print(f"  After-tax Income: {after_tax}")
    print(f"  Effective Portfolio Withdrawal: {Money(annual_expenses).subtract(after_tax)}")
    
    return results_no_income, results_with_income


if __name__ == "__main__":
    print("\n" + "="*60)
    print("INCOME ACCOUNT EXAMPLES")
    print("="*60)
    
    # # Example 1: Multiple income sources
    # portfolio1, results1 = example_income_sources()
    
    # # Example 2: Early retirement with bridge income
    # portfolio2, results2 = example_early_retirement_with_bridge()
    
    # Example 3: Compare with and without income
    results_no, results_with = example_compare_with_without_income()
    
    print("\n" + "="*60)
    print("All income examples completed!")
    print("="*60)