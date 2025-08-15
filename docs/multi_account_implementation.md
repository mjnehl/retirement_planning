# Multi-Account Retirement Planning Implementation

## Overview
The retirement planning system has been enhanced to support multiple account types with realistic tax implications, withdrawal strategies, and account-specific characteristics.

## Account Types Implemented

### 1. **Cash Account** (`CashAccount`)
- Emergency fund or liquid savings
- Fixed return rate (typically 2-3%)
- No volatility
- No taxes on withdrawal
- First source for withdrawals

### 2. **Taxable Investment Account** (`TaxableAccount`)
- Brokerage account with stocks and cash
- Configurable stock/cash allocation (default 80/20)
- Subject to capital gains tax (15% long-term)
- Dividend income
- Tracks cost basis for tax calculations

### 3. **Traditional IRA** (`IRAAccount`)
- Tax-deferred retirement account
- More conservative allocation (70/30 stocks/cash)
- Taxed as ordinary income on withdrawal (22% default)
- 10% early withdrawal penalty before age 59.5
- Required Minimum Distributions (RMDs) after age 72

### 4. **Mortgage** (`Mortgage`)
- Liability account
- Fixed interest rate and payment schedule
- Can be paid off early
- Reduces net worth until paid off

## Key Features

### Multi-Account Portfolio Management
- **`MultiAccountPortfolio`** class manages all accounts
- Tracks total assets, liabilities, and net worth
- Supports different withdrawal orders
- Handles mortgage payments automatically

### Withdrawal Strategies
1. **Traditional Order**: Cash → Taxable → IRA
2. **Tax-Efficient Order**: RMDs → Cash → Taxable → IRA
3. **Proportional**: Withdraw from all accounts proportionally

### Tax Modeling
- **Capital gains tax** on taxable account withdrawals
- **Ordinary income tax** on IRA withdrawals
- **Early withdrawal penalties** for IRA before 59.5
- **RMD calculations** for traditional IRAs after 72

## Usage Example

```python
from retirement_planner import RetirementPlanner

planner = RetirementPlanner()

# Run multi-account simulation
results = planner.create_multi_account_scenario(
    cash_balance=50000,      # Emergency fund
    taxable_balance=500000,  # Brokerage account
    ira_balance=800000,      # Traditional IRA
    mortgage_balance=200000, # Remaining mortgage
    mortgage_rate=0.04,      # 4% rate
    mortgage_years=15,       # 15 years remaining
    annual_expenses=60000,   # Living expenses
    current_age=65,
    years=30,
    num_simulations=1000
)

print(f"Success Rate: {results.success_rate:.1f}%")
print(f"Median Final Net Worth: {results.median_final_net_worth}")
```

## Simulation Results Analysis

The multi-account simulation provides:
- **Success rate** - Probability of not running out of money
- **Account depletion statistics** - When each account type typically depletes
- **Tax burden analysis** - Total taxes paid over retirement
- **Mortgage payoff timeline** - When mortgage is typically paid off
- **Net worth trajectory** - How net worth changes over time

## Key Findings from Examples

### Base Scenario (from example)
- **Success Rate**: 74.4%
- **Median Final Net Worth**: $1.5M
- **Average Annual Taxes**: $20K
- **Median Mortgage Payoff**: Year 6

### Strategy Comparison
- **Conservative** ($50K/year): 98.4% success, $5.1M median final
- **Standard** ($65K/year): 85.0% success, $3.2M median final
- **Aggressive** ($80K/year): Lower success rate

### Tax Efficiency
Tax-efficient withdrawal ordering can save significant money over traditional ordering by:
1. Taking RMDs when required
2. Using tax-free cash first
3. Managing capital gains tax through taxable account
4. Delaying IRA withdrawals when possible

## Benefits of Multi-Account Approach

1. **Realistic Modeling** - Accounts for actual tax implications
2. **Withdrawal Flexibility** - Different strategies for different situations
3. **Tax Optimization** - Can minimize lifetime tax burden
4. **Mortgage Integration** - Models liability alongside assets
5. **Account-Specific Returns** - Different risk/return profiles per account

## Future Enhancements

Potential improvements:
- Roth IRA conversions
- Social Security integration
- Healthcare expense modeling
- Estate planning considerations
- More sophisticated tax brackets
- State tax variations
- Investment expense ratios