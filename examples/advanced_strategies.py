"""
Advanced Portfolio Strategy Examples
Based on the strategies outlined in the Portfolio Builder User Manual
"""

import sys
sys.path.append('../src')

from decimal import Decimal
from retirement_planner import RetirementPlanner
from core.portfolio_builder import PortfolioBuilder
from core.multi_account_portfolio import WithdrawalOrder
from core.multi_account_withdrawal import MultiAccountFixedWithdrawal
from core.money import Money


def baseline():
    portfolio = (PortfolioBuilder("baseline_strategy")
                .with_age(62)
                .with_inflation(Decimal('0.03'), Decimal('0.008'))
                .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                .add_cash_account(
                    balance=Decimal('70000'),
                    annual_return=Decimal('0.03'),
                    name="Cash Buffer"
            )
            .add_taxable_account(
                balance=Decimal('288000'),
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
            .add_private_stock_account(
                balance=Decimal('140000'),
                conversion_year=4,
                stock_return=Decimal('0.20'),
                stock_volatility=Decimal('0.35'),
                name="JSQ Private stock"
            )
            .add_inheritance_account(
                expected_amount=Decimal('300000'),  # $500k inheritance
                inheritance_year=10,  # Expected in 10 years (parent is 85)
                asset_allocation=Decimal('0.80'),  # Conservative portfolio
                growth_rate=Decimal('0.05'),  # 5% growth (conservative)
                volatility=Decimal('0.10'),  # 10% volatility (low)
                is_step_up_basis=True,  # Step-up basis (no capital gains)
                name="Parent's Estate"
            )
            .build())
    
    return portfolio    


def barbell_strategy_example():
    """
    Barbell Strategy: Combine ultra-safe assets with high-risk investments
    """
    print("\n" + "="*60)
    print("BARBELL STRATEGY PORTFOLIO")
    print("="*60)
    
    portfolio = (PortfolioBuilder("barbell_strategy")
                .with_age(62)
                .with_inflation(Decimal('0.03'), Decimal('0.008'))
                .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                .add_cash_account(
                    balance=Decimal('100000'),
                    annual_return=Decimal('0.03'),
                    name="Cash Buffer"
            )
            .add_taxable_account(
                balance=Decimal('258000'),
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
            .add_private_stock_account(
                balance=Decimal('140000'),
                conversion_year=4,
                stock_return=Decimal('0.15'),
                stock_volatility=Decimal('0.30'),
                name="JSQ Private stock"
            )
            .add_inheritance_account(
                expected_amount=Decimal('300000'),  # $500k inheritance
                inheritance_year=10,  # Expected in 10 years (parent is 85)
                asset_allocation=Decimal('0.80'),  # Conservative portfolio
                growth_rate=Decimal('0.05'),  # 5% growth (conservative)
                volatility=Decimal('0.10'),  # 10% volatility (low)
                is_step_up_basis=True,  # Step-up basis (no capital gains)
                name="Parent's Estate"
            )
            .build())
    
    return portfolio    




def bucket_strategy_example():
    """
    Bucket Strategy: Time-segmented portfolios for different retirement phases
    """
    print("\n" + "="*60)
    print("BUCKET STRATEGY PORTFOLIO")
    print("="*60)
    
    portfolio = (PortfolioBuilder("bucket_strategy")
        .with_age(62)
        .with_inflation(Decimal('0.03'), Decimal('0.008'))
        .with_withdrawal_order(WithdrawalOrder.PROPORTIONAL)
        
        # Bucket 1: Years 1-5 (Cash & Short-term) - $400k
        .add_cash_account(
            balance=Decimal('200000'),
            annual_return=Decimal('0.03'),
            name="Bucket 1: Years 1-5 (Cash)"
        )
        
        # Bucket 2: Years 6-15 (Balanced) - $800k
        .add_taxable_account(
            balance=Decimal('800000'),
            stock_allocation=Decimal('0.50'),  # 50/50 balanced
            stock_return=Decimal('0.08'),
            stock_volatility=Decimal('0.12'),
            dividend_yield=Decimal('0.025'),
            name="Bucket 2: Years 6-15 (Balanced)"
        )
        
        # Bucket 3: Years 16+ (Growth) - $500k
        .add_ira_account(
            balance=Decimal('500000'),
            stock_allocation=Decimal('0.85'),  # 85% stocks for growth
            stock_return=Decimal('0.11'),
            stock_volatility=Decimal('0.18'),
            name="Bucket 3: Years 16+ (Growth)"
        )
        .build())
    
    return portfolio


def tax_optimized_strategy_example():
    """
    Tax-Optimized Strategy: Asset location and tax-loss harvesting
    """
    print("\n" + "="*60)
    print("TAX-OPTIMIZED STRATEGY PORTFOLIO")
    print("="*60)
    
    portfolio = (PortfolioBuilder("tax_optimized")
        .with_age(62)
        .with_inflation(Decimal('0.03'), Decimal('0.008'))
        .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
        
        # Safe Side (40% of portfolio - $300k)
        .add_cash_account(
            balance=Decimal('100000'),
            annual_return=Decimal('0.03'),
            name="Treasury Money Market"
        )
        .add_cash_account(  # Using cash account to simulate bonds
            balance=Decimal('188000'),
            annual_return=Decimal('0.04'),
            name="Investment Grade Bonds"
        )
        
        # Risk Side (60% of portfolio - $450k)
        .add_taxable_account(
            balance=Decimal('270000'),
            stock_allocation=Decimal('1.0'),  # 100% growth stocks
            stock_return=Decimal('0.14'),
            stock_volatility=Decimal('0.25'),
            dividend_yield=Decimal('0.005'),  # Low dividend for growth
            name="Growth Stocks Portfolio"
        )
        .add_private_stock_account(
            balance=Decimal('141000'),
            conversion_year=5,
            stock_return=Decimal('0.20'),
            stock_volatility=Decimal('0.35'),
            name="Private Equity/Venture"
        )
        .build())
    
    return portfolio
    


def income_floor_strategy_example():
    """
    Income Floor Strategy: Secure essential expenses with guaranteed income
    """
    print("\n" + "="*60)
    print("INCOME FLOOR STRATEGY PORTFOLIO")
    print("="*60)
    
    portfolio = (PortfolioBuilder("income_floor")
        .with_age(65)
        .with_inflation(Decimal('0.025'), Decimal('0.005'))
        .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
        
        # Guaranteed Income Floor (covers $75k essential expenses)
        .add_income_account(
            annual_income=Decimal('35000'),
            start_year=0,
            duration_years=30,
            annual_adjustment=Decimal('0.025'),
            tax_rate=Decimal('0.12'),
            name="Social Security"
        )
        .add_income_account(
            annual_income=Decimal('24000'),
            start_year=0,
            duration_years=30,
            annual_adjustment=Decimal('0.02'),
            tax_rate=Decimal('0.22'),
            name="Pension"
        )
        .add_income_account(
            annual_income=Decimal('16000'),
            start_year=0,
            duration_years=30,
            annual_adjustment=Decimal('0.00'),  # Fixed annuity
            tax_rate=Decimal('0.15'),
            name="Immediate Annuity"
        )
        
        # Growth Portfolio for discretionary spending
        .add_taxable_account(
            balance=Decimal('500000'),
            stock_allocation=Decimal('0.70'),
            stock_return=Decimal('0.10'),
            stock_volatility=Decimal('0.16'),
            name="Growth Portfolio"
        )
        
        # Emergency reserve
        .add_cash_account(
            balance=Decimal('100000'),
            annual_return=Decimal('0.03'),
            name="Emergency Fund"
        )
        .build())
    
    return portfolio


def alternative_assets_strategy_example():
    """
    Alternative Assets Strategy: Diversify beyond traditional stocks/bonds
    """
    print("\n" + "="*60)
    print("ALTERNATIVE ASSETS STRATEGY PORTFOLIO")
    print("="*60)
    
    portfolio = (PortfolioBuilder("alternative_assets")
        .with_age(60)
        .with_inflation(Decimal('0.03'), Decimal('0.01'))
        .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
        
        # Traditional Assets (50% - $500k)
        .add_taxable_account(
            balance=Decimal('500000'),
            stock_allocation=Decimal('0.70'),
            stock_return=Decimal('0.09'),
            stock_volatility=Decimal('0.15'),
            name="Traditional Stocks/Bonds"
        )
        
        # Real Estate (20% - $200k) - simulated as income-producing asset
        .add_income_account(
            annual_income=Decimal('16000'),  # 8% yield on $200k
            start_year=0,
            duration_years=30,
            annual_adjustment=Decimal('0.03'),
            tax_rate=Decimal('0.25'),
            name="Real Estate (REIT)"
        )
        
        # Private Equity (20% - $200k)
        .add_private_stock_account(
            balance=Decimal('200000'),
            conversion_year=7,
            stock_return=Decimal('0.18'),
            stock_volatility=Decimal('0.30'),
            name="Private Equity Fund"
        )
        
        # Commodities/Gold (10% - $100k) - simulated as low-correlation asset
        .add_cash_account(
            balance=Decimal('100000'),
            annual_return=Decimal('0.06'),  # Historical gold return
            name="Commodities/Gold"
        )
        .build())
    
    return portfolio


def early_retirement_strategy_example():
    """
    Early Retirement Strategy: Bridge to Social Security with tax optimization
    """
    print("\n" + "="*60)
    print("EARLY RETIREMENT STRATEGY PORTFOLIO (Age 55)")
    print("="*60)
    
    portfolio = (PortfolioBuilder("early_retirement")
        .with_age(55)
        .with_inflation(Decimal('0.03'), Decimal('0.01'))
        .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
        
        # Bridge Fund - Cover 12 years until Social Security at 67
        .add_cash_account(
            balance=Decimal('200000'),
            annual_return=Decimal('0.03'),
            name="Bridge to SS Fund"
        )
        
        # Taxable for early retirement flexibility
        .add_taxable_account(
            balance=Decimal('500000'),
            stock_allocation=Decimal('0.70'),
            stock_return=Decimal('0.10'),
            stock_volatility=Decimal('0.16'),
            dividend_yield=Decimal('0.02'),
            capital_gains_tax_rate=Decimal('0.15'),
            name="Taxable Brokerage"
        )
        
        # Traditional IRA for Roth conversions
        .add_ira_account(
            balance=Decimal('600000'),
            stock_allocation=Decimal('0.75'),
            stock_return=Decimal('0.10'),
            stock_volatility=Decimal('0.16'),
            ordinary_income_tax_rate=Decimal('0.22'),
            name="Traditional IRA"
        )
        
        # Roth IRA for tax-free growth (simulated)
        .add_private_stock_account(
            balance=Decimal('400000'),
            conversion_year=35,  # Never sell - tax-free
            stock_return=Decimal('0.11'),
            stock_volatility=Decimal('0.18'),
            name="Roth IRA"
        )
        
        # Deferred Social Security (starts at age 67)
        .add_income_account(
            annual_income=Decimal('35000'),
            start_year=12,  # Starts at age 67
            duration_years=30,
            annual_adjustment=Decimal('0.025'),
            tax_rate=Decimal('0.12'),
            name="Social Security (Age 67)"
        )
        .build())
    
    return portfolio


def conservative_income_strategy_example():
    """
    Conservative Income Strategy: Focus on dividend and interest income
    """
    print("\n" + "="*60)
    print("CONSERVATIVE INCOME STRATEGY PORTFOLIO")
    print("="*60)
    
    portfolio = (PortfolioBuilder("conservative_income")
        .with_age(68)
        .with_inflation(Decimal('0.025'), Decimal('0.005'))
        .with_withdrawal_order(WithdrawalOrder.PROPORTIONAL)
        
        # High-dividend stocks
        .add_taxable_account(
            balance=Decimal('400000'),
            stock_allocation=Decimal('0.60'),  # Dividend stocks
            stock_return=Decimal('0.07'),
            stock_volatility=Decimal('0.12'),
            dividend_yield=Decimal('0.04'),  # High dividend yield
            capital_gains_tax_rate=Decimal('0.15'),
            name="Dividend Portfolio"
        )
        
        # Bond ladder (simulated as stable income)
        .add_cash_account(
            balance=Decimal('300000'),
            annual_return=Decimal('0.045'),  # Corporate bonds
            name="Bond Ladder"
        )
        
        # Preferred stocks (simulated)
        .add_taxable_account(
            balance=Decimal('200000'),
            stock_allocation=Decimal('0.00'),  # Like bonds
            stock_return=Decimal('0.055'),
            stock_volatility=Decimal('0.08'),
            dividend_yield=Decimal('0.055'),
            name="Preferred Stocks"
        )
        
        # Cash reserves
        .add_cash_account(
            balance=Decimal('100000'),
            annual_return=Decimal('0.025'),
            name="Money Market"
        )
        
        # Social Security
        .add_income_account(
            annual_income=Decimal('38000'),
            start_year=0,
            duration_years=30,
            annual_adjustment=Decimal('0.025'),
            tax_rate=Decimal('0.12'),
            name="Social Security"
        )
        .build())
    
    return portfolio


def display_portfolio_details(portfolio, name):
    """
    Display detailed portfolio initial conditions
    """
    print(f"\n{'='*80}")
    print(f"STRATEGY: {name}")
    print(f"{'='*80}")
    
    print(f"\nINITIAL CONDITIONS:")
    print(f"  Starting Age: {portfolio.current_age}")
    print(f"  Inflation Rate: {float(portfolio.inflation_rate)*100:.1f}%")
    print(f"  Inflation Volatility: {float(portfolio.inflation_volatility)*100:.1f}%")
    print(f"  Withdrawal Order: {portfolio.withdrawal_order.value}")
    
    print(f"\n  INITIAL ACCOUNT BALANCES:")
    
    total_assets = Decimal('0')
    total_liabilities = Decimal('0')
    
    # Display each account with ALL initial details
    for account_name, account in portfolio.accounts.items():
        from core.accounts import AccountType
        
        if account.account_type == AccountType.CASH:
            print(f"    {account_name:<35} ${float(account.balance.amount):>12,.0f}")
            print(f"      Return: {float(account.annual_return)*100:.1f}%")
            total_assets += account.balance.amount
            
        elif account.account_type == AccountType.TAXABLE:
            print(f"    {account_name:<35} ${float(account.balance.amount):>12,.0f}")
            print(f"      Stock Allocation: {float(account.stock_allocation)*100:.0f}%, Cash Allocation: {float(account.cash_allocation)*100:.0f}%")
            print(f"      Stock Return: {float(account.stock_return)*100:.1f}%, Volatility: {float(account.stock_volatility)*100:.1f}%")
            print(f"      Cash Return: {float(account.cash_return)*100:.1f}%")
            print(f"      Dividend Yield: {float(account.dividend_yield)*100:.2f}%")
            print(f"      Capital Gains Tax: {float(account.capital_gains_tax_rate)*100:.1f}%")
            total_assets += account.balance.amount
            
        elif account.account_type == AccountType.IRA:
            print(f"    {account_name:<35} ${float(account.balance.amount):>12,.0f}")
            print(f"      Stock Allocation: {float(account.stock_allocation)*100:.0f}%, Cash Allocation: {float(account.cash_allocation)*100:.0f}%")
            print(f"      Stock Return: {float(account.stock_return)*100:.1f}%, Volatility: {float(account.stock_volatility)*100:.1f}%")
            print(f"      Cash Return: {float(account.cash_return)*100:.1f}%")
            print(f"      Ordinary Income Tax: {float(account.ordinary_income_tax_rate)*100:.1f}%")
            total_assets += account.balance.amount
            
        elif account.account_type == AccountType.ROTH_IRA:
            print(f"    {account_name:<35} ${float(account.balance.amount):>12,.0f}")
            if hasattr(account, 'stock_allocation'):
                print(f"      Stock Allocation: {float(account.stock_allocation)*100:.0f}%, Cash Allocation: {float(account.cash_allocation)*100:.0f}%")
                print(f"      Stock Return: {float(account.stock_return)*100:.1f}%, Volatility: {float(account.stock_volatility)*100:.1f}%")
                print(f"      Cash Return: {float(account.cash_return)*100:.1f}%")
            print(f"      Tax-Free Growth")
            total_assets += account.balance.amount
            
        elif account.account_type == AccountType.PRIVATE_STOCK:
            print(f"    {account_name:<35} ${float(account.balance.amount):>12,.0f}")
            print(f"      Stock Return: {float(account.stock_return)*100:.1f}%, Volatility: {float(account.stock_volatility)*100:.1f}%")
            print(f"      Conversion Year: {account.conversion_year}")
            if hasattr(account, 'tax_rate'):
                print(f"      Tax Rate: {float(account.tax_rate)*100:.1f}%")
            total_assets += account.balance.amount
            
        elif account.account_type == AccountType.INHERITANCE:
            print(f"    {account_name:<35} ${float(account.balance.amount):>12,.0f}")
            print(f"      Inheritance Year: {account.inheritance_year}")
            print(f"      Asset Allocation: {float(account.asset_allocation)*100:.0f}%")
            print(f"      Growth Rate: {float(account.growth_rate)*100:.1f}%, Volatility: {float(account.volatility)*100:.1f}%")
            print(f"      Step-up Basis: {account.is_step_up_basis}")
            # Don't add to initial assets since it's future inheritance
            
        elif account.account_type == AccountType.INCOME:
            print(f"    {account_name:<35} ${float(account.annual_income.amount):>12,.0f}/year")
            print(f"      Duration: {account.duration_years} years, Starting Year: {account.start_year}")
            print(f"      Annual Adjustment: {float(account.annual_adjustment)*100:.1f}%")
            print(f"      Tax Rate: {float(account.tax_rate)*100:.1f}%")
            # Don't add to assets since it's income stream
            
        elif account.account_type == AccountType.MORTGAGE:
            print(f"    {account_name:<35} ${float(account.balance.amount):>12,.0f}")
            print(f"      Interest Rate: {float(account.interest_rate)*100:.1f}%")
            print(f"      Remaining Years: {account.remaining_years}")
            print(f"      Monthly Payment: ${float(account.monthly_payment.amount):,.0f}")
            total_liabilities += account.balance.amount
    
    print(f"\n  STARTING NET WORTH:")
    print(f"    Total Assets:                      ${float(total_assets):>12,.0f}")
    print(f"    Total Liabilities:                 ${float(total_liabilities):>12,.0f}")
    print(f"    Net Worth:                         ${float(total_assets - total_liabilities):>12,.0f}")


def run_strategy_comparison():
    """
    Compare all strategies side by side with detailed reporting
    """
    strategies = [
        ("baseline",baseline()),
        ("Barbell", barbell_strategy_example()),
        ("Tax Optimized", tax_optimized_strategy_example()),
        ("Bucket", bucket_strategy_example()),
        ("Income Floor", income_floor_strategy_example()),
        ("Alternative Assets", alternative_assets_strategy_example()),
        ("Early Retirement", early_retirement_strategy_example()),
        ("Conservative Income", conservative_income_strategy_example())
    ]
    
    # Common simulation parameters
    annual_withdrawal = 80000
    years = 30
    num_simulations = 1000
    
    planner = RetirementPlanner()
    
    print("\n" + "="*80)
    print("DETAILED STRATEGY ANALYSIS")
    print("="*80)
    print(f"Common Parameters:")
    print(f"  Annual Withdrawal: ${annual_withdrawal:,}")
    print(f"  Simulation Years: {years}")
    print(f"  Number of Simulations: {num_simulations}")
    
    # Detailed report for each strategy
    for name, portfolio in strategies:
        # Display initial portfolio details
        display_portfolio_details(portfolio, name)
        
        # Run simulation
        withdrawal_strategy = MultiAccountFixedWithdrawal(
            initial_withdrawal=Money(annual_withdrawal),
            inflation_rate=portfolio.inflation_rate,
            pay_mortgage_first=False,
            withdrawal_order=portfolio.withdrawal_order
        )
        
        results = planner.run_simulation(
            portfolio=portfolio,
            withdrawal_strategy=withdrawal_strategy,
            years=years,
            num_simulations=num_simulations
        )
        
        # Display simulation results
        print(f"\nSIMULATION RESULTS (Annual Withdrawal: ${annual_withdrawal:,}):")
        print(f"  Success Rate: {results.success_rate:.1f}%")
        print(f"  Median Final Net Worth: ${float(results.median_final_net_worth.amount):,.0f}")
        
        # Get all runs for percentile analysis
        all_runs = results.runs
        successful_runs = results.get_successful_runs()
        
        if all_runs:
            # Calculate percentiles for final net worth
            final_net_worths = [float(run.final_net_worth.amount) for run in all_runs]
            import numpy as np
            percentiles = np.percentile(final_net_worths, [10, 25, 50, 75, 90])
            
            print(f"\n  NET WORTH PERCENTILES:")
            print(f"    10th percentile:                   ${percentiles[0]:>12,.0f}")
            print(f"    25th percentile:                   ${percentiles[1]:>12,.0f}")
            print(f"    50th percentile (median):          ${percentiles[2]:>12,.0f}")
            print(f"    75th percentile:                   ${percentiles[3]:>12,.0f}")
            print(f"    90th percentile:                   ${percentiles[4]:>12,.0f}")
        
        if successful_runs:
            # Get final snapshots from successful runs for account-level analysis
            final_balances = {}
            initial_balances = {}
            
            # Store initial balances for comparison
            for account_name, account in portfolio.accounts.items():
                from core.accounts import AccountType
                if account.account_type not in [AccountType.INCOME, AccountType.INHERITANCE, AccountType.MORTGAGE]:
                    initial_balances[account_name] = float(account.balance.amount)
            
            for run in successful_runs:
                if run.yearly_snapshots:
                    final_snapshot = run.yearly_snapshots[-1]  # Last year snapshot
                    for account_name, balance in final_snapshot.items():
                        if account_name not in ['net_worth', 'total_assets', 'total_liabilities']:
                            if account_name not in final_balances:
                                final_balances[account_name] = []
                            final_balances[account_name].append(float(balance.amount))
            
            # Calculate and display detailed account statistics
            if final_balances:
                print(f"\n  ACCOUNT-LEVEL ANALYSIS (Successful Runs Only):")
                print(f"    {'Account':<35} {'Initial':>12} {'Median Final':>12} {'Growth':>10} {'Depletion %':>12}")
                print(f"    {'-'*35} {'-'*12} {'-'*12} {'-'*10} {'-'*12}")
                
                for account_name in sorted(final_balances.keys()):
                    balances = final_balances[account_name]
                    median_balance = np.median(balances)
                    initial = initial_balances.get(account_name, 0)
                    
                    # Calculate depletion percentage
                    depleted_count = sum(1 for b in balances if b <= 0)
                    depletion_pct = (depleted_count / len(balances)) * 100
                    
                    # Calculate growth
                    if initial > 0:
                        growth = ((median_balance - initial) / initial) * 100
                        growth_str = f"{growth:+.1f}%"
                    else:
                        growth_str = "N/A"
                    
                    if median_balance > 0 or initial > 0:  # Show if has initial or final balance
                        print(f"    {account_name:<35} ${initial:>11,.0f} ${median_balance:>11,.0f} {growth_str:>10} {depletion_pct:>11.1f}%")
        
        # Show failure analysis if applicable
        failed_runs = [r for r in all_runs if r.depleted]
        if failed_runs:
            depletion_years = [r.depletion_year for r in failed_runs if r.depletion_year is not None]
            if depletion_years:
                print(f"\n  FAILURE ANALYSIS:")
                print(f"    Failed runs: {len(failed_runs)} out of {len(all_runs)}")
                print(f"    Median depletion year: {np.median(depletion_years):.0f}")
                print(f"    Earliest depletion: Year {min(depletion_years)}")
                print(f"    Latest depletion: Year {max(depletion_years)}")
    
    # Summary table at the end
    print("\n" + "="*80)
    print("SUMMARY COMPARISON")
    print("="*80)
    print(f"{'Strategy':<20} {'Success Rate':>12} {'Median NW':>15} {'10th %ile':>15} {'90th %ile':>15}")
    print("-"*80)
    
    for name, portfolio in strategies:
        withdrawal_strategy = MultiAccountFixedWithdrawal(
            initial_withdrawal=Money(annual_withdrawal),
            inflation_rate=portfolio.inflation_rate,
            pay_mortgage_first=False,
            withdrawal_order=portfolio.withdrawal_order
        )
        
        results = planner.run_simulation(
            portfolio=portfolio,
            withdrawal_strategy=withdrawal_strategy,
            years=years,
            num_simulations=num_simulations
        )
        
        all_runs = results.runs
        final_net_worths = [float(run.final_net_worth.amount) for run in all_runs]
        import numpy as np
        percentiles = np.percentile(final_net_worths, [10, 50, 90])
        
        print(f"{name:<20} {results.success_rate:>11.1f}% ${percentiles[1]:>14,.0f} ${percentiles[0]:>14,.0f} ${percentiles[2]:>14,.0f}")
    
    print("="*80)


if __name__ == "__main__":
    # Run individual strategy examples
    print("\n" + "="*80)
    print("ADVANCED PORTFOLIO STRATEGIES DEMONSTRATION")
    print("="*80)
    
    # You can test individual strategies by uncommenting:
    # barbell_strategy_example()
    # bucket_strategy_example()
    # tax_optimized_strategy_example()
    # income_floor_strategy_example()
    # alternative_assets_strategy_example()
    # early_retirement_strategy_example()
    # conservative_income_strategy_example()
    
    # Or run the comparison
    run_strategy_comparison()