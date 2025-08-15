# Portfolio Builder User Manual
## Advanced Retirement Portfolio Strategies Guide

---

## Table of Contents
1. [Introduction](#introduction)
2. [Your Current Portfolio Analysis](#current-portfolio)
3. [Core Building Blocks](#core-building-blocks)
4. [Advanced Portfolio Strategies](#advanced-strategies)
5. [Implementation Examples](#implementation-examples)
6. [Risk Management](#risk-management)
7. [Tax Optimization](#tax-optimization)
8. [Rebalancing Strategies](#rebalancing)
9. [Performance Tracking](#performance-tracking)
10. [Quick Reference](#quick-reference)

---

## Introduction

This manual provides comprehensive guidance on building and optimizing retirement portfolios using the RetirementPlanner system. Based on your existing portfolio configuration, we'll explore advanced strategies you can implement to enhance returns, reduce risk, and optimize tax efficiency.

## Your Current Portfolio Analysis

Your reference portfolio demonstrates several sophisticated strategies:

### Current Holdings:
- **Cash Buffer**: $50,000 (3% return) - Emergency liquidity
- **Taxable Account**: $300,000 (75% stocks, 10% return)
- **Traditional IRA**: $200,000 (70% stocks, 10% return)
- **Private Stock**: $140,000 (15% return, high volatility)
- **Expected Inheritance**: $300,000 in year 10
- **Social Security**: $32,400/year starting immediately
- **Mortgage**: $570,000 at 6% (23 years remaining)

### Current Strategies Employed:
1. **Tax-Efficient Withdrawal Order**: Optimizes tax impact
2. **Asset Location**: Different allocations in taxable vs. tax-deferred
3. **Income Stacking**: Social Security provides base income
4. **Liquidity Laddering**: Cash buffer for emergencies
5. **Private Asset Integration**: Higher risk/return allocation

---

## Core Building Blocks

### Account Types Available

```python
# 1. Cash Account - Liquidity Buffer
.add_cash_account(
    balance=Decimal('50000'),
    annual_return=Decimal('0.03'),
    name="Emergency Fund"
)

# 2. Taxable Investment Account
.add_taxable_account(
    balance=Decimal('300000'),
    stock_allocation=Decimal('0.75'),
    stock_return=Decimal('0.10'),
    stock_volatility=Decimal('0.16'),
    dividend_yield=Decimal('0.02'),
    capital_gains_tax_rate=Decimal('0.15'),
    name="Brokerage"
)

# 3. Traditional IRA
.add_ira_account(
    balance=Decimal('200000'),
    stock_allocation=Decimal('0.70'),
    stock_return=Decimal('0.10'),
    stock_volatility=Decimal('0.16'),
    ordinary_income_tax_rate=Decimal('0.24'),
    name="Traditional IRA"
)

# 4. Roth IRA (NEW STRATEGY)
.add_roth_ira_account(
    balance=Decimal('100000'),
    stock_allocation=Decimal('0.80'),
    stock_return=Decimal('0.11'),
    stock_volatility=Decimal('0.18'),
    name="Roth IRA"
)
```

---

## Advanced Strategies

### 1. Barbell Portfolio Strategy
**Concept**: Combine ultra-safe assets with high-risk/high-return investments, avoiding the middle ground.

```python
portfolio = (PortfolioBuilder("barbell_strategy")
    .with_age(62)
    .with_inflation(Decimal('0.03'), Decimal('0.008'))
    .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
    
    # Safe Side (40% of portfolio)
    .add_cash_account(
        balance=Decimal('100000'),
        annual_return=Decimal('0.03'),
        name="Treasury Ladder"
    )
    .add_bond_account(
        balance=Decimal('200000'),
        annual_return=Decimal('0.04'),
        volatility=Decimal('0.03'),
        name="Investment Grade Bonds"
    )
    
    # Risk Side (60% of portfolio)
    .add_growth_stock_account(
        balance=Decimal('250000'),
        stock_return=Decimal('0.14'),
        stock_volatility=Decimal('0.25'),
        name="Growth Stocks"
    )
    .add_private_stock_account(
        balance=Decimal('200000'),
        conversion_year=5,
        stock_return=Decimal('0.20'),
        stock_volatility=Decimal('0.35'),
        name="Private Equity"
    )
    .build())
```

### 2. Tax Loss Harvesting Strategy
**Concept**: Systematically realize losses to offset gains and reduce tax burden.

```python
portfolio = (PortfolioBuilder("tax_loss_harvesting")
    .with_age(62)
    .with_tax_loss_harvesting(
        enabled=True,
        threshold=Decimal('0.02'),  # Harvest when down 2%
        max_annual_harvest=Decimal('3000')
    )
    .add_taxable_account(
        balance=Decimal('500000'),
        stock_allocation=Decimal('0.70'),
        enable_tax_loss_harvesting=True,
        harvest_frequency="quarterly"
    )
    .build())
```

### 3. Bucket Strategy
**Concept**: Divide portfolio into time-based buckets for different phases of retirement.

```python
portfolio = (PortfolioBuilder("bucket_strategy")
    .with_age(62)
    
    # Bucket 1: Years 1-5 (Cash & Short-term)
    .add_cash_account(
        balance=Decimal('400000'),  # 5 years × $80k
        annual_return=Decimal('0.03'),
        name="Bucket 1: Immediate Needs"
    )
    
    # Bucket 2: Years 6-15 (Moderate Growth)
    .add_balanced_account(
        balance=Decimal('800000'),
        stock_allocation=Decimal('0.50'),
        bond_allocation=Decimal('0.50'),
        name="Bucket 2: Medium Term"
    )
    
    # Bucket 3: Years 16+ (Growth)
    .add_growth_account(
        balance=Decimal('500000'),
        stock_allocation=Decimal('0.85'),
        name="Bucket 3: Long Term Growth"
    )
    .build())
```

### 4. Roth Conversion Ladder
**Concept**: Systematically convert Traditional IRA to Roth IRA during low-income years.

```python
portfolio = (PortfolioBuilder("roth_ladder")
    .with_age(62)
    .with_roth_conversion_strategy(
        annual_conversion_amount=Decimal('50000'),
        start_year=0,
        end_year=10,
        target_tax_bracket=Decimal('0.12')
    )
    .add_ira_account(
        balance=Decimal('500000'),
        enable_conversions=True
    )
    .add_roth_ira_account(
        balance=Decimal('0'),  # Will grow from conversions
        stock_allocation=Decimal('0.80')
    )
    .build())
```

### 5. Alternative Asset Integration
**Concept**: Diversify beyond traditional stocks/bonds.

```python
portfolio = (PortfolioBuilder("alternative_assets")
    .with_age(62)
    
    # Traditional Assets (60%)
    .add_taxable_account(
        balance=Decimal('600000'),
        stock_allocation=Decimal('0.70')
    )
    
    # Real Estate (20%)
    .add_reit_account(
        balance=Decimal('200000'),
        annual_return=Decimal('0.08'),
        volatility=Decimal('0.12'),
        dividend_yield=Decimal('0.04')
    )
    
    # Commodities (10%)
    .add_commodity_account(
        balance=Decimal('100000'),
        annual_return=Decimal('0.06'),
        volatility=Decimal('0.20'),
        correlation_to_stocks=Decimal('-0.2')
    )
    
    # Crypto (10%)
    .add_crypto_account(
        balance=Decimal('100000'),
        annual_return=Decimal('0.25'),
        volatility=Decimal('0.60'),
        name="Digital Assets"
    )
    .build())
```

### 6. Dynamic Asset Allocation
**Concept**: Adjust allocation based on market conditions and age.

```python
portfolio = (PortfolioBuilder("dynamic_allocation")
    .with_age(62)
    .with_dynamic_allocation(
        initial_stock_allocation=Decimal('0.70'),
        annual_reduction=Decimal('0.02'),  # Reduce stocks by 2% per year
        minimum_stock_allocation=Decimal('0.30'),
        rebalance_frequency="quarterly"
    )
    .add_managed_account(
        balance=Decimal('1000000'),
        enable_dynamic_allocation=True
    )
    .build())
```

### 7. Income Floor Strategy
**Concept**: Secure essential expenses with guaranteed income sources.

```python
portfolio = (PortfolioBuilder("income_floor")
    .with_age(62)
    
    # Guaranteed Income Floor
    .add_income_account(
        annual_income=Decimal('32400'),
        name="Social Security"
    )
    .add_annuity_account(
        premium_paid=Decimal('300000'),
        annual_payout=Decimal('24000'),
        start_year=0,
        cola_adjustment=Decimal('0.02')
    )
    .add_pension_account(
        annual_income=Decimal('18000'),
        survivor_benefit=Decimal('0.50')
    )
    
    # Growth Portfolio (Upside)
    .add_taxable_account(
        balance=Decimal('500000'),
        stock_allocation=Decimal('0.80')
    )
    .build())
```

### 8. Liability Matching Strategy
**Concept**: Match assets to future liabilities.

```python
portfolio = (PortfolioBuilder("liability_matching")
    .with_age(62)
    .with_liabilities([
        {"year": 0, "amount": 570000, "type": "mortgage"},
        {"year": 5, "amount": 50000, "type": "car_purchase"},
        {"year": 10, "amount": 100000, "type": "home_renovation"}
    ])
    .add_bond_ladder(
        total_amount=Decimal('720000'),
        duration_years=15,
        yield_curve="normal"
    )
    .add_growth_portfolio(
        balance=Decimal('500000'),
        for_discretionary_spending=True
    )
    .build())
```

---

## Implementation Examples

### Example 1: Conservative Retiree with Pension

```python
# Age 65, has pension, wants stability
conservative_portfolio = (PortfolioBuilder("conservative_with_pension")
    .with_age(65)
    .with_inflation(Decimal('0.025'), Decimal('0.005'))
    .with_withdrawal_order(WithdrawalOrder.PROPORTIONAL)
    
    # Income Sources
    .add_income_account(
        annual_income=Decimal('40000'),
        name="Social Security"
    )
    .add_pension_account(
        annual_income=Decimal('30000'),
        cola_adjustment=Decimal('0.02'),
        name="Corporate Pension"
    )
    
    # Conservative Investments
    .add_cash_account(
        balance=Decimal('100000'),
        annual_return=Decimal('0.025')
    )
    .add_bond_portfolio(
        balance=Decimal('400000'),
        duration=7,
        credit_quality="AA"
    )
    .add_balanced_fund(
        balance=Decimal('300000'),
        stock_allocation=Decimal('0.30')
    )
    .build())
```

### Example 2: Early Retiree with No Pension

```python
# Age 55, no pension, needs growth
early_retiree_portfolio = (PortfolioBuilder("early_retirement")
    .with_age(55)
    .with_inflation(Decimal('0.03'), Decimal('0.01'))
    .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
    
    # Bridge to Social Security
    .add_cash_account(
        balance=Decimal('200000'),  # 3 years expenses
        name="Bridge Fund"
    )
    
    # Tax-Advantaged Growth
    .add_roth_ira_account(
        balance=Decimal('400000'),
        stock_allocation=Decimal('0.85')
    )
    .add_ira_account(
        balance=Decimal('600000'),
        stock_allocation=Decimal('0.75'),
        enable_roth_conversions=True
    )
    
    # Taxable for Flexibility
    .add_taxable_account(
        balance=Decimal('500000'),
        stock_allocation=Decimal('0.70'),
        enable_tax_loss_harvesting=True
    )
    
    # Future Income
    .add_deferred_income(
        annual_income=Decimal('35000'),
        start_year=12,  # At age 67
        name="Social Security"
    )
    .build())
```

### Example 3: High Net Worth with Estate Planning

```python
# Age 60, $5M+ portfolio, estate concerns
hnw_portfolio = (PortfolioBuilder("high_net_worth")
    .with_age(60)
    .with_estate_planning(
        target_legacy=Decimal('3000000'),
        charitable_giving=Decimal('100000')  # Annual
    )
    
    # Core Holdings
    .add_taxable_account(
        balance=Decimal('2000000'),
        stock_allocation=Decimal('0.65')
    )
    .add_municipal_bond_account(
        balance=Decimal('1000000'),
        tax_free_yield=Decimal('0.035')
    )
    
    # Tax-Advantaged
    .add_ira_account(balance=Decimal('800000'))
    .add_roth_ira_account(balance=Decimal('600000'))
    
    # Alternative Investments
    .add_private_equity(
        balance=Decimal('500000'),
        expected_return=Decimal('0.18')
    )
    .add_real_estate_portfolio(
        value=Decimal('1000000'),
        rental_income=Decimal('60000')
    )
    
    # Estate Planning Tools
    .add_trust_account(
        balance=Decimal('500000'),
        beneficiaries=["children"],
        distribution_schedule="graduated"
    )
    .build())
```

---

## Risk Management

### 1. Sequence of Returns Risk Mitigation

```python
# Protect against poor returns early in retirement
.with_sequence_protection(
    cash_buffer_years=3,
    reduce_withdrawals_in_down_markets=True,
    threshold=Decimal('-0.10'),  # Reduce if down >10%
    reduction_factor=Decimal('0.80')  # Cut spending to 80%
)
```

### 2. Longevity Risk Protection

```python
# Ensure money lasts through long retirement
.add_longevity_insurance(
    premium=Decimal('100000'),
    payout_age=85,
    monthly_benefit=Decimal('5000')
)
```

### 3. Inflation Protection

```python
# Hedge against inflation
.add_tips_ladder(
    amount=Decimal('300000'),
    duration_years=20,
    real_yield=Decimal('0.01')
)
.add_i_bonds(
    amount=Decimal('30000'),  # Annual limit
    holding_period=5
)
```

### 4. Black Swan Protection

```python
# Protect against extreme events
.add_protective_puts(
    portfolio_value=Decimal('1000000'),
    strike_percentage=Decimal('0.90'),  # 10% OTM
    annual_cost=Decimal('0.015')  # 1.5% of portfolio
)
```

---

## Tax Optimization

### 1. Asset Location Optimization

```python
def optimize_asset_location(portfolio):
    """
    Place assets in most tax-efficient accounts:
    - High-growth stocks → Roth IRA
    - Bonds/REITs → Traditional IRA
    - Tax-efficient index funds → Taxable
    - Tax-loss harvesting candidates → Taxable
    """
    return portfolio.optimize_location(
        tax_inefficient_in_ira=True,
        growth_in_roth=True,
        harvest_in_taxable=True
    )
```

### 2. Tax Bracket Management

```python
portfolio.with_tax_management(
    target_bracket=Decimal('0.12'),  # Stay in 12% bracket
    fill_bracket=True,  # Convert IRA up to bracket limit
    harvest_losses=True,
    max_harvest=Decimal('3000'),
    defer_gains=True
)
```

### 3. Qualified Dividend Strategy

```python
# Favor qualified dividends in taxable accounts
.add_dividend_focused_account(
    balance=Decimal('500000'),
    qualified_dividend_percentage=Decimal('0.95'),
    dividend_yield=Decimal('0.03'),
    dividend_growth=Decimal('0.05')
)
```

### 4. Municipal Bond Strategy

```python
# For high tax brackets
.add_muni_bond_ladder(
    amount=Decimal('500000'),
    tax_equivalent_yield=Decimal('0.05'),  # ~3.5% tax-free
    state_tax_exempt=True,
    amo_exempt=True  # Avoid AMT
)
```

---

## Rebalancing Strategies

### 1. Calendar Rebalancing

```python
portfolio.with_rebalancing(
    frequency="quarterly",  # or "annual", "monthly"
    threshold=None,  # Always rebalance on schedule
    method="proportional"
)
```

### 2. Threshold Rebalancing

```python
portfolio.with_rebalancing(
    frequency=None,  # No fixed schedule
    threshold=Decimal('0.05'),  # Rebalance if 5% off target
    method="corridor"  # Only adjust assets outside corridor
)
```

### 3. Tactical Rebalancing

```python
portfolio.with_tactical_rebalancing(
    base_allocation={"stocks": 0.60, "bonds": 0.40},
    tactical_range=Decimal('0.10'),  # ±10% tactical shifts
    signals=["momentum", "valuation", "sentiment"],
    rebalance_frequency="monthly"
)
```

### 4. Cash Flow Rebalancing

```python
portfolio.with_cash_flow_rebalancing(
    use_contributions=True,  # Rebalance with new money
    use_withdrawals=True,  # Rebalance during withdrawals
    use_dividends=True,  # Reinvest to rebalance
    minimize_transactions=True
)
```

---

## Performance Tracking

### 1. Key Metrics to Monitor

```python
metrics = portfolio.calculate_metrics(
    # Risk Metrics
    success_rate=True,  # Probability of not running out
    safe_withdrawal_rate=True,
    maximum_drawdown=True,
    volatility=True,
    
    # Return Metrics
    expected_return=True,
    median_return=True,
    percentile_returns=[10, 25, 50, 75, 90],
    
    # Portfolio Health
    years_to_depletion=True,
    inflation_adjusted_value=True,
    tax_efficiency=True,
    expense_ratio=True
)
```

### 2. Stress Testing

```python
stress_tests = portfolio.run_stress_tests([
    {"name": "2008 Crisis", "stocks": -0.37, "bonds": 0.05},
    {"name": "Dot-com Bust", "stocks": -0.49, "bonds": 0.10},
    {"name": "1970s Stagflation", "inflation": 0.10, "returns": -0.05},
    {"name": "Japan 1990s", "stocks": -0.60, "duration": 10}
])
```

### 3. Monte Carlo Analysis

```python
monte_carlo = portfolio.run_monte_carlo(
    simulations=10000,
    years=35,
    confidence_levels=[0.50, 0.75, 0.90, 0.95],
    include_sequence_risk=True,
    vary_inflation=True,
    vary_life_expectancy=True
)
```

---

## Quick Reference

### Withdrawal Order Options
- `TAX_EFFICIENT`: Minimize lifetime taxes
- `PROPORTIONAL`: Maintain allocation
- `TAXABLE_FIRST`: Preserve tax-advantaged growth
- `TAX_DEFERRED_FIRST`: Reduce RMDs
- `ROTH_LAST`: Maximum tax-free growth

### Account Types Summary
| Account Type | Tax Treatment | Best For |
|--------------|--------------|----------|
| Taxable | Capital gains rates | Flexibility, harvesting |
| Traditional IRA | Deferred, ordinary income | Current deduction |
| Roth IRA | Tax-free growth | Estate planning |
| 401(k) | Deferred, ordinary income | Employer match |
| HSA | Triple tax-free | Medical expenses |
| 529 | Tax-free for education | College planning |

### Risk-Return Profiles
| Strategy | Risk Level | Expected Return | Best For |
|----------|------------|-----------------|----------|
| Conservative | Low | 4-6% | Capital preservation |
| Balanced | Medium | 6-8% | Steady growth |
| Growth | High | 8-12% | Long horizon |
| Aggressive | Very High | 10-15% | Risk tolerant |
| Alternative | Variable | 5-20% | Diversification |

### Tax Brackets (2024)
| Income Range | Tax Rate | Strategy |
|--------------|----------|----------|
| $0-$11,600 | 10% | Harvest gains |
| $11,601-$47,150 | 12% | Roth conversions |
| $47,151-$100,525 | 22% | Defer income |
| $100,526-$191,950 | 24% | Maximize deductions |
| $191,951-$243,725 | 32% | Municipal bonds |
| $243,726-$609,350 | 35% | Tax shelters |
| $609,351+ | 37% | Estate planning |

---

## Advanced Implementation Tips

### 1. Combining Strategies
You can layer multiple strategies for enhanced results:

```python
# Combine Bucket + Tax Loss Harvesting + Roth Ladder
combined_portfolio = (PortfolioBuilder("multi_strategy")
    .with_bucket_strategy(buckets=3)
    .with_tax_loss_harvesting(enabled=True)
    .with_roth_conversion_ladder(annual_amount=50000)
    .build())
```

### 2. Dynamic Adjustments
Adapt strategies based on life events:

```python
# Adjust for market conditions
if market_down_20_percent:
    portfolio.reduce_withdrawal_rate(0.80)
    portfolio.increase_stock_allocation(0.10)
    portfolio.accelerate_roth_conversions()
```

### 3. Scenario Planning
Test multiple futures:

```python
scenarios = [
    "base_case",
    "early_social_security",
    "delayed_retirement",
    "part_time_work",
    "downsizing_home",
    "long_term_care_needed"
]

for scenario in scenarios:
    results = portfolio.test_scenario(scenario)
    print(f"{scenario}: {results.success_rate}%")
```

---

## Conclusion

Your current portfolio demonstrates solid fundamentals with tax-efficient withdrawal ordering, diversified account types, and income layering. The advanced strategies in this manual can help you:

1. **Enhance Returns**: Through alternative assets, tactical allocation, and tax optimization
2. **Reduce Risk**: Via diversification, hedging, and liability matching
3. **Improve Tax Efficiency**: Using asset location, loss harvesting, and bracket management
4. **Increase Flexibility**: With bucket strategies, Roth conversions, and dynamic rebalancing

Remember to:
- Review and adjust annually
- Consider your risk tolerance
- Account for life changes
- Maintain emergency reserves
- Consult professionals for complex strategies

The key is finding the right combination of strategies that align with your goals, risk tolerance, and time horizon.