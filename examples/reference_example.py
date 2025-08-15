"""simple example that will evolve as needed"""

import sys
sys.path.append('../src')

from decimal import Decimal
from retirement_planner import RetirementPlanner
from core.portfolio_builder import PortfolioBuilder
from core.multi_account_portfolio import WithdrawalOrder
from core.multi_account_withdrawal import MultiAccountFixedWithdrawal
from core.money import Money


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RETIREMENT EXAMPLES")
    print("="*60)
    
    
    # Same portfolio with Social Security and pension
    portfolio= (PortfolioBuilder("with_income")
                .with_age(62)
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
    annual_withdrawal = 80000
    years=30
    num_simulations=1000

    withdrawal_strategy = MultiAccountFixedWithdrawal(
        initial_withdrawal=Money(annual_withdrawal),
        inflation_rate=portfolio.inflation_rate,
        pay_mortgage_first = False,
        withdrawal_order=portfolio.withdrawal_order
    )
        
    planner = RetirementPlanner()
    
    print("\n" + "="*60)
    print("simulation years",years)
    print("num simulations",num_simulations)
    print("annual non-mortgage expense",annual_withdrawal)
    print("inflation",portfolio.inflation_rate)
    print("withdrawal order",portfolio.withdrawal_order)

    print("\n" + "="*60)
    print("accounts")
    print("="*60)
    
  
  
    results = planner.run_simulation(
        portfolio=portfolio,
        withdrawal_strategy=withdrawal_strategy,
        years=years,
        num_simulations=num_simulations
    )
  

  



    print("# final nw: ",results.median_final_net_worth)
    print("# success rate: ",results.success_rate)
    print("# runs",len(results.runs))
    # print("# runs",results.runs[0].yearly_snapshots[0])
    # print("# runs",results.runs[0].yearly_snapshots[1])
    # print("# runs",results.runs[0].yearly_snapshots[2])
    print("="*60)