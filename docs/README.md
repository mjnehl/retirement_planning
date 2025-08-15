# Retirement Planning Monte Carlo Simulator

## Overview
A Python-based Monte Carlo simulation tool for retirement planning that helps answer key questions about portfolio sustainability and withdrawal strategies.

## Current Features (Phase 1 - Simple)
- **Portfolio simulation** with random market returns
- **Fixed withdrawal strategy** with inflation adjustments  
- **Success rate calculation** (probability of not running out of money)
- **Visualization** of simulation paths and outcomes
- **Scenario comparison** tools

## Quick Start

```python
from retirement_simulator import RetirementParams, RetirementSimulator

# Define your retirement scenario
params = RetirementParams(
    initial_portfolio=1_000_000,  # $1M starting
    annual_withdrawal=40_000,      # $40k/year (4% rule)
    years_in_retirement=30,        # 30-year horizon
    mean_return=0.07,              # 7% average returns
    std_return=0.18,               # 18% volatility
    num_simulations=10_000         # 10k Monte Carlo runs
)

# Run simulation
simulator = RetirementSimulator(params)
results = simulator.run_simulation()
success_rate = simulator.calculate_success_rate()

print(f"Success Rate: {success_rate:.1f}%")
```

## Key Questions You Can Answer

### 1. "What's my probability of success?"
The simulator calculates what percentage of simulations don't run out of money.

### 2. "How much can I safely withdraw?"
Test different withdrawal rates to find your comfort level:
- 3% withdrawal → ~95% success
- 4% withdrawal → ~85% success  
- 5% withdrawal → ~65% success

### 3. "How much do I need to retire?"
Work backwards from your spending needs to required portfolio size.

### 4. "What if market returns are lower?"
Adjust the `mean_return` parameter to test conservative scenarios.

## Understanding the Results

The simulator provides:
- **Success Rate**: Percentage of simulations where money lasts
- **Portfolio Paths**: Visual representation of possible outcomes
- **Percentile Analysis**: Best case, worst case, and median scenarios
- **Depletion Timeline**: When failures typically occur

## Planned Enhancements

### Phase 2: Tax-Advantaged Accounts
- Traditional IRA/401(k) with RMDs
- Roth IRA conversions
- Tax optimization strategies

### Phase 3: Income Streams
- Social Security modeling
- Pension income
- Part-time work scenarios

### Phase 4: Advanced Assets
- Real estate/mortgage
- Private stock options
- Alternative investments

## Files Structure
```
src/
  retirement_simulator.py  - Core Monte Carlo engine
  scenario_runner.py       - Scenario comparison tools
examples/
  simple_example.py        - Getting started example
docs/
  README.md               - This file
```

## Key Assumptions
- Returns are normally distributed (can be enhanced with historical data)
- Withdrawals happen at start of year
- Inflation applies to withdrawals
- No taxes (yet - Phase 2)
- Single portfolio (no asset allocation yet)

## Next Steps
1. Run `examples/simple_example.py` to see it in action
2. Modify parameters to match your situation
3. Use `scenario_runner.py` to compare strategies
4. Let me know what specific questions you want to explore!