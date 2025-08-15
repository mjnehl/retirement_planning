# Retirement Planning System - API Documentation

## Overview

The Retirement Planning System provides comprehensive tools for retirement financial planning, including portfolio optimization, tax strategies, Social Security optimization, and Monte Carlo simulations for risk analysis.

## Core Modules

### 1. Input Validation (`core.validators`)

Ensures all inputs are valid and within acceptable ranges.

#### `RetirementValidator`

**Methods:**

- `validate_decimal(value, field_name, min_value=None, max_value=None)` - Validates numeric inputs
- `validate_percentage(value, field_name)` - Validates percentages (0-1 range)
- `validate_age(value, field_name)` - Validates age (18-120)
- `validate_years(value, field_name)` - Validates year duration (1-100)
- `validate_portfolio_inputs(balance, stock_allocation, stock_return, stock_volatility)` - Validates portfolio parameters

**Example:**
```python
from core.validators import RetirementValidator

# Validate age
age = RetirementValidator.validate_age(65)

# Validate portfolio inputs
inputs = RetirementValidator.validate_portfolio_inputs(
    balance='100000',
    stock_allocation='0.7',
    stock_return='0.08',
    stock_volatility='0.15'
)
```

### 2. Monte Carlo Simulations (`core.monte_carlo_advanced`)

Advanced Monte Carlo simulations with comprehensive risk analytics.

#### `AdvancedMonteCarloSimulator`

**Initialization:**
```python
simulator = AdvancedMonteCarloSimulator(
    num_simulations=10000,
    random_seed=42  # Optional for reproducibility
)
```

**Methods:**

- `simulate_portfolio_returns()` - Simulate portfolio growth with contributions/withdrawals
- `simulate_retirement_scenarios()` - Simulate retirement withdrawal scenarios
- `sensitivity_analysis()` - Analyze sensitivity to parameter changes

**Returns:** `MonteCarloResults` object containing:
- Success rate
- Mean/median outcomes
- Confidence intervals (90%, 95%, 99%)
- Risk metrics (VaR, CVaR, Sharpe ratio, Sortino ratio)
- Maximum drawdown

**Example:**
```python
results = simulator.simulate_retirement_scenarios(
    portfolio_value=1000000,
    withdrawal_rate=0.04,
    expected_return=0.06,
    volatility=0.12,
    years=30,
    inflation_rate=0.025,
    tax_rate=0.20
)

print(results.get_summary())
```

### 3. Tax Optimization (`core.tax_optimizer`)

Optimizes withdrawal strategies to minimize lifetime taxes.

#### `TaxOptimizer`

**Initialization:**
```python
optimizer = TaxOptimizer(
    filing_status='single',  # or 'married'
    state_tax_rate=Decimal('0.05')
)
```

**Methods:**

- `optimize_withdrawal_strategy()` - Optimizes account withdrawal order
- `calculate_lifetime_tax_efficiency()` - Analyzes lifetime tax impact

**Account Types:**
- `TAXABLE` - Regular investment accounts
- `TRADITIONAL_IRA` - Traditional IRA/401(k)
- `ROTH_IRA` - Roth IRA/401(k)
- `HSA` - Health Savings Account

**Example:**
```python
strategy = optimizer.optimize_withdrawal_strategy(
    account_balances={
        AccountType.TAXABLE: Decimal('200000'),
        AccountType.TRADITIONAL_IRA: Decimal('300000'),
        AccountType.ROTH_IRA: Decimal('100000')
    },
    withdrawal_amount=Decimal('50000'),
    current_age=65,
    other_income=Decimal('20000')
)

print(f"Tax Savings: ${strategy.tax_savings}")
print(f"Effective Tax Rate: {strategy.effective_tax_rate:.2%}")
```

### 4. Social Security Calculator (`core.social_security`)

Optimizes Social Security claiming strategies.

#### `SocialSecurityCalculator`

**Initialization:**
```python
calculator = SocialSecurityCalculator(
    birth_year=1958,
    earnings_history=earnings_records  # Optional
)
```

**Methods:**

- `calculate_benefit()` - Calculate benefit at specific claiming age
- `optimize_claiming_strategy()` - Find optimal claiming age
- `calculate_spousal_benefit()` - Calculate spousal benefits
- `calculate_survivor_benefit()` - Calculate survivor benefits

**Example:**
```python
# Calculate benefit at different ages
early_benefit = calculator.calculate_benefit(claiming_age=62)
full_benefit = calculator.calculate_benefit(claiming_age=67)
delayed_benefit = calculator.calculate_benefit(claiming_age=70)

# Optimize strategy
strategies = calculator.optimize_claiming_strategy(
    life_expectancy=85,
    discount_rate=Decimal('0.03')
)

optimal = strategies['optimal']
print(f"Optimal claiming age: {optimal.claiming_age}")
print(f"Monthly benefit: ${optimal.monthly_benefit}")
```

### 5. Portfolio Optimizer (`core.portfolio_optimizer`)

Implements Modern Portfolio Theory for asset allocation.

#### `PortfolioOptimizer`

**Initialization:**
```python
optimizer = PortfolioOptimizer(risk_free_rate=0.03)
```

**Methods:**

- `optimize_portfolio()` - Find optimal asset allocation
- `rebalance_portfolio()` - Calculate rebalancing trades
- `calculate_risk_metrics()` - Comprehensive risk analysis

**Asset Classes:**
- `equity` - Stocks
- `bond` - Bonds
- `commodity` - Commodities
- `real_estate` - Real estate

**Example:**
```python
assets = [
    Asset('SPY', expected_return=0.10, volatility=0.16, asset_class='equity'),
    Asset('AGG', expected_return=0.04, volatility=0.05, asset_class='bond'),
    Asset('GLD', expected_return=0.06, volatility=0.18, asset_class='commodity')
]

portfolio = optimizer.optimize_portfolio(
    assets=assets,
    maximize_sharpe=True
)

print(portfolio.get_summary())
```

### 6. Inflation Models (`core.inflation_models`)

Multiple inflation models for realistic projections.

#### Available Models

- `ConstantInflationModel` - Fixed inflation rate
- `VariableInflationModel` - Different rates for different periods
- `HistoricalInflationModel` - Based on historical CPI data
- `StochasticInflationModel` - Random with mean reversion
- `AdaptiveInflationModel` - Adjusts based on economic indicators

**Example:**
```python
from core.inflation_models import create_inflation_model, InflationType

# Create stochastic model
model = create_inflation_model(
    InflationType.STOCHASTIC,
    mean_rate=Decimal('0.03'),
    volatility=Decimal('0.01')
)

# Project future values
projections = model.project_value(
    initial_value=Decimal('100000'),
    years=30,
    category='healthcare'  # Use healthcare-specific inflation
)

# Calculate real returns
real_return = model.calculate_real_return(
    nominal_return=Decimal('0.07'),
    inflation_rate=Decimal('0.03')
)
```

## Integration Example

Complete retirement planning workflow:

```python
from decimal import Decimal
from retirement_planner import RetirementPlanner
from core.portfolio_builder import PortfolioBuilder
from core.validators import RetirementValidator
from core.monte_carlo_advanced import AdvancedMonteCarloSimulator
from core.tax_optimizer import TaxOptimizer, AccountType
from core.social_security import SocialSecurityCalculator

# 1. Validate inputs
age = RetirementValidator.validate_age(65)
years = RetirementValidator.validate_years(30)

# 2. Build portfolio
portfolio = (PortfolioBuilder("retirement_portfolio")
    .with_age(age)
    .with_inflation(Decimal('0.03'), Decimal('0.008'))
    .add_taxable_account(
        balance=Decimal('300000'),
        stock_allocation=Decimal('0.70')
    )
    .add_ira_account(
        balance=Decimal('500000'),
        stock_allocation=Decimal('0.60')
    )
    .build())

# 3. Optimize taxes
tax_optimizer = TaxOptimizer(filing_status='married')
tax_strategy = tax_optimizer.optimize_withdrawal_strategy(
    account_balances={
        AccountType.TAXABLE: Decimal('300000'),
        AccountType.TRADITIONAL_IRA: Decimal('500000')
    },
    withdrawal_amount=Decimal('80000'),
    current_age=age
)

# 4. Calculate Social Security
ss_calculator = SocialSecurityCalculator(birth_year=1959)
ss_benefit = ss_calculator.calculate_benefit(claiming_age=67)

# 5. Run Monte Carlo simulation
simulator = AdvancedMonteCarloSimulator(num_simulations=10000)
results = simulator.simulate_retirement_scenarios(
    portfolio_value=800000,
    withdrawal_rate=0.04,
    expected_return=0.06,
    volatility=0.15,
    years=years
)

# 6. Analyze results
print(f"Success Rate: {results.success_rate:.1%}")
print(f"Median Final Value: ${results.median_outcome:,.0f}")
print(f"Tax Savings: ${tax_strategy.tax_savings:,.0f}")
print(f"Social Security: ${ss_benefit.annual_benefit:,.0f}/year")
```

## Error Handling

All modules use custom `ValidationError` exceptions for input validation:

```python
from core.validators import ValidationError

try:
    age = RetirementValidator.validate_age(150)
except ValidationError as e:
    print(f"Error: {e}")
    # Output: Validation error for age: Must be between 18 and 120 (value: 150)
```

## Performance Considerations

- Monte Carlo simulations: Use fewer simulations (1000-5000) for quick estimates, 10000+ for final analysis
- Portfolio optimization: Computation scales with O(n²) for n assets
- Tax optimization: Linear in number of accounts
- Use `random_seed` parameter for reproducible results in testing

## Testing

Run comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_validators.py -v
python -m pytest tests/test_monte_carlo_advanced.py -v
python -m pytest tests/test_tax_optimizer.py -v
```

## Dependencies

- `numpy` - Numerical computations
- `scipy` - Statistical functions and optimization
- `pandas` - Data analysis
- `decimal` - Precise decimal arithmetic

## Support

For issues or questions, please refer to the project repository or contact the development team.