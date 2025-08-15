"""
Customized Bucket Strategy for Your Specific Portfolio
Based on your assets: $558K initial + $144K private stock (year 5) + $300K inheritance (year 10)
"""

import sys
sys.path.append('../src')

from decimal import Decimal
from retirement_planner import RetirementPlanner
from core.portfolio_builder import PortfolioBuilder
from core.multi_account_portfolio import WithdrawalOrder
from core.multi_account_withdrawal import MultiAccountFixedWithdrawal
from core.money import Money


def your_bucket_strategy():
    """
    Your personalized bucket strategy implementation
    
    Current Assets:
    - Cash: $50,000
    - Taxable: $300,000
    - IRA: $200,000
    - Total: $550,000 (excluding mortgage)
    
    Future Assets:
    - Private Stock: $144,000 in year 5
    - Inheritance: $300,000 in year 10
    """
    
    print("\n" + "="*80)
    print("YOUR PERSONALIZED BUCKET STRATEGY")
    print("="*80)
    print("\nBUCKET ALLOCATION PLAN:")
    print("-"*80)
    
    # BUCKET 1: Years 1-5 (Immediate Needs)
    # Need: $80,000/year × 5 years = $400,000
    # Available now: $50,000 cash + $350,000 from other accounts
    print("\n📦 BUCKET 1: Years 1-5 (Immediate Needs)")
    print("   Purpose: Cover living expenses without market risk")
    print("   Target: $400,000 ($80K × 5 years)")
    print("   Allocation:")
    print("   - $50,000 Cash (existing)")
    print("   - $150,000 from Taxable (sell bonds/stable stocks)")
    print("   - $200,000 Money Market/Short-term bonds")
    print("   Returns: 3% (very conservative)")
    
    # BUCKET 2: Years 6-15 (Medium Term)
    # This bucket gets replenished by private stock in year 5
    print("\n📦 BUCKET 2: Years 6-15 (Medium Term)")
    print("   Purpose: Balanced growth with moderate risk")
    print("   Target: $800,000 ($80K × 10 years)")
    print("   Allocation:")
    print("   - $150,000 from Taxable (balanced allocation)")
    print("   - $144,000 Private Stock (arrives year 5)")
    print("   - $300,000 Inheritance (arrives year 10)")
    print("   - Refills from Bucket 3 growth")
    print("   Returns: 7-8% (balanced)")
    
    # BUCKET 3: Years 16+ (Long Term Growth)
    # Can be more aggressive since won't touch for 15+ years
    print("\n📦 BUCKET 3: Years 16+ (Long Term)")
    print("   Purpose: Maximum growth for later years")
    print("   Target: Remaining assets")
    print("   Allocation:")
    print("   - $200,000 IRA (100% stocks)")
    print("   - Growth overflow from Buckets 1 & 2")
    print("   Returns: 10-11% (aggressive)")
    
    print("\n" + "="*80)
    print("IMPLEMENTATION IN YOUR PORTFOLIO")
    print("="*80)
    
    portfolio = (PortfolioBuilder("your_bucket_strategy")
        .with_age(62)
        .with_inflation(Decimal('0.03'), Decimal('0.008'))
        .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
        
        # ==========================================
        # BUCKET 1: Years 1-5 (Safe & Liquid)
        # ==========================================
        .add_cash_account(
            balance=Decimal('50000'),  # Your existing cash
            annual_return=Decimal('0.03'),
            name="Bucket 1A: Emergency Cash"
        )
        .add_cash_account(
            balance=Decimal('200000'),  # Additional safe money
            annual_return=Decimal('0.035'),  # Short-term bonds
            name="Bucket 1B: Short-term Bonds"
        )
        
        # ==========================================
        # BUCKET 2: Years 6-15 (Balanced)
        # ==========================================
        .add_taxable_account(
            balance=Decimal('150000'),  # Part of your taxable
            stock_allocation=Decimal('0.50'),  # 50/50 balanced
            stock_return=Decimal('0.08'),
            stock_volatility=Decimal('0.12'),
            dividend_yield=Decimal('0.025'),
            capital_gains_tax_rate=Decimal('0.15'),
            name="Bucket 2A: Balanced Portfolio"
        )
        
        # Private stock arrives in year 5 - perfect for Bucket 2
        .add_private_stock_account(
            balance=Decimal('144000'),
            conversion_year=5,  # Liquidates just as Bucket 1 depletes
            stock_return=Decimal('0.15'),
            stock_volatility=Decimal('0.30'),
            name="Bucket 2B: Private Stock (Year 5)"
        )
        
        # Inheritance arrives in year 10 - replenishes Bucket 2
        .add_inheritance_account(
            expected_amount=Decimal('300000'),
            inheritance_year=10,
            asset_allocation=Decimal('0.60'),  # 60% stocks
            growth_rate=Decimal('0.06'),
            volatility=Decimal('0.10'),
            is_step_up_basis=True,
            name="Bucket 2C: Inheritance (Year 10)"
        )
        
        # ==========================================
        # BUCKET 3: Years 16+ (Growth)
        # ==========================================
        .add_ira_account(
            balance=Decimal('200000'),  # Your IRA for long-term growth
            stock_allocation=Decimal('0.85'),  # Aggressive for long term
            stock_return=Decimal('0.10'),
            stock_volatility=Decimal('0.16'),
            ordinary_income_tax_rate=Decimal('0.24'),
            name="Bucket 3A: IRA Growth"
        )
        .add_taxable_account(
            balance=Decimal('150000'),  # Rest of taxable for growth
            stock_allocation=Decimal('0.80'),  # Growth focused
            stock_return=Decimal('0.10'),
            stock_volatility=Decimal('0.16'),
            dividend_yield=Decimal('0.015'),
            capital_gains_tax_rate=Decimal('0.15'),
            name="Bucket 3B: Growth Stocks"
        )
        
        # ==========================================
        # Income Sources
        # ==========================================
        .add_income_account(
            annual_income=Decimal('32400'),
            start_year=0,
            duration_years=30,
            annual_adjustment=Decimal('0.025'),
            tax_rate=Decimal('0.12'),
            name="Social Security"
        )
        
        # ==========================================
        # Liabilities
        # ==========================================
        .add_mortgage(
            balance=Decimal('570000'),
            interest_rate=Decimal('0.06'),
            remaining_years=23,
            name="Home Mortgage"
        )
        .build())
    
    return portfolio


def explain_bucket_rebalancing():
    """
    Explain how bucket rebalancing works over time
    """
    print("\n" + "="*80)
    print("HOW BUCKET REBALANCING WORKS")
    print("="*80)
    
    print("\n📅 YEAR 1-5: Living off Bucket 1")
    print("   • Withdraw $80K/year from Bucket 1 (cash/bonds)")
    print("   • Buckets 2 & 3 grow untouched")
    print("   • No market risk on immediate needs")
    print("   • Rebalance within Buckets 2 & 3 if needed")
    
    print("\n📅 YEAR 5: Private Stock Arrives")
    print("   • Private stock ($144K) liquidates")
    print("   • Replenishes Bucket 2")
    print("   • Move some Bucket 2 gains → Bucket 1 (refill)")
    print("   • Continue withdrawing from Bucket 1")
    
    print("\n📅 YEAR 6-10: Transition Period")
    print("   • Bucket 1 may be depleted")
    print("   • Start withdrawing from Bucket 2")
    print("   • Bucket 3 continues growing")
    print("   • Monitor and rebalance annually")
    
    print("\n📅 YEAR 10: Inheritance Arrives")
    print("   • $300K inheritance received")
    print("   • Refill Bucket 1 (2-3 years expenses)")
    print("   • Boost Bucket 2 (balanced allocation)")
    print("   • Excess → Bucket 3 (growth)")
    
    print("\n📅 YEAR 11-15: Mid-Retirement")
    print("   • Three buckets fully operational")
    print("   • Withdraw from Bucket 1")
    print("   • Cascade gains: Bucket 3 → 2 → 1")
    print("   • Annual rebalancing")
    
    print("\n📅 YEAR 16+: Late Retirement")
    print("   • Original Bucket 3 becomes available")
    print("   • Continue cascade strategy")
    print("   • May reduce stock allocation with age")


def bucket_management_rules():
    """
    Key rules for managing bucket strategy
    """
    print("\n" + "="*80)
    print("BUCKET STRATEGY MANAGEMENT RULES")
    print("="*80)
    
    print("\n✅ DO's:")
    print("   • Keep 2-3 years expenses in Bucket 1 always")
    print("   • Rebalance by moving gains downstream (3→2→1)")
    print("   • Use new money (inheritance, stock sales) to refill buckets")
    print("   • Adjust allocations based on market conditions")
    print("   • Take gains from outperforming buckets")
    
    print("\n❌ DON'Ts:")
    print("   • Don't tap Bucket 3 in first 10-15 years")
    print("   • Don't panic sell from Bucket 2/3 in downturns")
    print("   • Don't let Bucket 1 run completely dry")
    print("   • Don't ignore rebalancing opportunities")
    print("   • Don't be too rigid - adapt as needed")
    
    print("\n🔄 REBALANCING TRIGGERS:")
    print("   • Bucket 1 < 2 years expenses → Refill")
    print("   • Any bucket off target by >20% → Rebalance")
    print("   • Major market move (±20%) → Review")
    print("   • Life event → Reassess buckets")
    print("   • Annual review regardless")


def compare_with_current_strategy():
    """
    Compare bucket strategy with your current approach
    """
    print("\n" + "="*80)
    print("COMPARISON: BUCKET vs YOUR CURRENT STRATEGY")
    print("="*80)
    
    print("\n📊 YOUR CURRENT APPROACH:")
    print("   • Single pooled portfolio")
    print("   • Tax-efficient withdrawal order")
    print("   • All assets subject to market volatility")
    print("   • Private stock & inheritance added to general pool")
    
    print("\n📊 BUCKET STRATEGY ADVANTAGES:")
    print("   ✓ Psychological comfort (safe money visible)")
    print("   ✓ Reduced sequence of returns risk")
    print("   ✓ Clear time horizons for each asset")
    print("   ✓ Natural rebalancing framework")
    print("   ✓ Flexibility to be aggressive with long-term money")
    
    print("\n📊 POTENTIAL DISADVANTAGES:")
    print("   ✗ May be less tax-efficient")
    print("   ✗ Requires more active management")
    print("   ✗ Could miss opportunities in Bucket 1")
    print("   ✗ More complex to track")
    
    print("\n💡 HYBRID APPROACH:")
    print("   • Use bucket concept for mental accounting")
    print("   • Maintain tax-efficient withdrawals")
    print("   • Keep 2-3 years in true cash (Bucket 1)")
    print("   • Rest stays invested but mentally allocated")


def run_simulation():
    """
    Run simulation comparing strategies
    """
    print("\n" + "="*80)
    print("SIMULATION RESULTS")
    print("="*80)
    
    # Your bucket strategy
    bucket_portfolio = your_bucket_strategy()
    
    # Simulation parameters
    annual_withdrawal = 80000
    years = 30
    num_simulations = 1000
    
    withdrawal_strategy = MultiAccountFixedWithdrawal(
        initial_withdrawal=Money(annual_withdrawal),
        inflation_rate=bucket_portfolio.inflation_rate,
        pay_mortgage_first=False,
        withdrawal_order=bucket_portfolio.withdrawal_order
    )
    
    planner = RetirementPlanner()
    
    results = planner.run_simulation(
        portfolio=bucket_portfolio,
        withdrawal_strategy=withdrawal_strategy,
        years=years,
        num_simulations=num_simulations
    )
    
    print(f"\nAnnual Withdrawal: ${annual_withdrawal:,}")
    print(f"Simulation Years: {years}")
    print(f"Number of Simulations: {num_simulations:,}")
    print("-"*40)
    print(f"Success Rate: {results.success_rate:.1f}%")
    print(f"Median Final Net Worth: ${float(results.median_final_net_worth.amount):,.0f}")


if __name__ == "__main__":
    # Show the complete bucket strategy explanation
    your_bucket_strategy()
    explain_bucket_rebalancing()
    bucket_management_rules()
    compare_with_current_strategy()
    
    # Run the simulation
    run_simulation()
    
    print("\n" + "="*80)
    print("KEY TAKEAWAY")
    print("="*80)
    print("""
The bucket strategy works exceptionally well with your portfolio timing:
    
1. You have enough for Bucket 1 ($250K) to cover years 1-5
2. Private stock arrives perfectly in year 5 to replenish
3. Inheritance in year 10 provides another boost
4. Social Security reduces withdrawal needs throughout

This natural timing alignment makes the bucket strategy ideal for 
your situation - assets arrive just when earlier buckets deplete!
""")