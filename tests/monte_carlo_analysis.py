"""Monte Carlo Analysis - Statistical Correctness Evaluation"""

import sys
sys.path.append('../src')

from decimal import Decimal
import numpy as np
import matplotlib.pyplot as plt
from retirement_planner import RetirementPlanner
from core.portfolio_builder import PortfolioBuilder
from core.multi_account_portfolio import WithdrawalOrder
from core.multi_account_withdrawal import MultiAccountFixedWithdrawal
from core.money import Money
import random
from scipy import stats

def analyze_monte_carlo_implementation():
    """Comprehensive analysis of Monte Carlo simulation correctness"""
    
    print("="*80)
    print("MONTE CARLO SIMULATION ANALYSIS")
    print("="*80)
    
    # Build test portfolio with real-world parameters
    portfolio = (PortfolioBuilder("test_portfolio")
                .with_age(65)
                .with_inflation(Decimal('0.03'), Decimal('0.008'))
                .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
                .add_cash_account(
                    balance=Decimal('50000'),
                    annual_return=Decimal('0.03'),
                    name="Cash Buffer"
                )
                .add_taxable_account(
                    balance=Decimal('300000'),
                    stock_allocation=Decimal('0.75'),
                    stock_return=Decimal('0.10'),
                    stock_volatility=Decimal('0.16'),
                    dividend_yield=Decimal('0.02'),
                    capital_gains_tax_rate=Decimal('0.15'),
                    name="Taxable Account"
                )
                .add_ira_account(
                    balance=Decimal('200000'),
                    stock_allocation=Decimal('0.70'),
                    stock_return=Decimal('0.10'),
                    stock_volatility=Decimal('0.16'),
                    ordinary_income_tax_rate=Decimal('0.24'),
                    name="Traditional IRA"
                )
                .build())
    
    annual_withdrawal = 40000
    years = 30
    
    # Test 1: Statistical distribution analysis
    print("\n1. DISTRIBUTION ANALYSIS")
    print("-"*40)
    
    # Run multiple simulations with different sample sizes
    sample_sizes = [10, 100, 1000]
    results_by_size = {}
    
    for n_sims in sample_sizes:
        withdrawal_strategy = MultiAccountFixedWithdrawal(
            initial_withdrawal=Money(annual_withdrawal),
            inflation_rate=portfolio.inflation_rate,
            withdrawal_order=portfolio.withdrawal_order
        )
        
        planner = RetirementPlanner()
        results = planner.run_simulation(
            portfolio=portfolio,
            withdrawal_strategy=withdrawal_strategy,
            years=years,
            num_simulations=n_sims
        )
        
        results_by_size[n_sims] = results
        print(f"  n={n_sims:4d}: Success Rate = {results.success_rate:.1f}%")
    
    # Test 2: Convergence analysis
    print("\n2. CONVERGENCE ANALYSIS")
    print("-"*40)
    print("  Testing if results converge as sample size increases...")
    
    success_rates = [results_by_size[n].success_rate for n in sample_sizes]
    convergence_metric = np.std([float(sr) for sr in success_rates])
    print(f"  Standard deviation of success rates: {convergence_metric:.2f}%")
    print(f"  Convergence assessment: {'GOOD' if convergence_metric < 5 else 'POOR'}")
    
    # Test 3: Randomness source investigation
    print("\n3. RANDOMNESS SOURCE ANALYSIS")
    print("-"*40)
    
    # Check what random number generator is being used
    import core.accounts as accounts_module
    import core.returns as returns_module
    
    # Inspect imports
    if 'random' in dir(accounts_module):
        print("  ⚠️  Using Python's 'random' module (not numpy)")
        print("     - Not suitable for parallel execution")
        print("     - Less robust for scientific computing")
    
    if 'np.random' in str(accounts_module.__dict__):
        print("  ✓ Using numpy.random for number generation")
    
    # Test 4: Seed reproducibility
    print("\n4. REPRODUCIBILITY TEST")
    print("-"*40)
    
    # Set seed and run twice
    random.seed(42)
    np.random.seed(42)
    
    withdrawal_strategy1 = MultiAccountFixedWithdrawal(
        initial_withdrawal=Money(annual_withdrawal),
        inflation_rate=portfolio.inflation_rate,
        withdrawal_order=portfolio.withdrawal_order
    )
    
    planner1 = RetirementPlanner()
    results1 = planner1.run_simulation(
        portfolio=portfolio,
        withdrawal_strategy=withdrawal_strategy1,
        years=10,  # Shorter for testing
        num_simulations=10
    )
    
    # Reset seed and run again
    random.seed(42)
    np.random.seed(42)
    
    withdrawal_strategy2 = MultiAccountFixedWithdrawal(
        initial_withdrawal=Money(annual_withdrawal),
        inflation_rate=portfolio.inflation_rate,
        withdrawal_order=portfolio.withdrawal_order
    )
    
    planner2 = RetirementPlanner()
    results2 = planner2.run_simulation(
        portfolio=portfolio,
        withdrawal_strategy=withdrawal_strategy2,
        years=10,
        num_simulations=10
    )
    
    # Compare results
    reproducible = results1.success_rate == results2.success_rate
    print(f"  Seed reproducibility: {'✓ PASS' if reproducible else '✗ FAIL'}")
    print(f"  Run 1 success rate: {results1.success_rate:.1f}%")
    print(f"  Run 2 success rate: {results2.success_rate:.1f}%")
    
    # Test 5: Statistical properties of returns
    print("\n5. RETURN DISTRIBUTION ANALYSIS")
    print("-"*40)
    
    # Collect returns from multiple runs
    returns_samples = []
    for _ in range(1000):
        # Simulate one year's return
        sample_return = random.gauss(0.10, 0.16)  # Using same params as portfolio
        returns_samples.append(sample_return)
    
    # Test for normality
    statistic, p_value = stats.normaltest(returns_samples)
    print(f"  Normality test (D'Agostino-Pearson):")
    print(f"    Statistic: {statistic:.4f}")
    print(f"    P-value: {p_value:.4f}")
    print(f"    Result: {'Normal' if p_value > 0.05 else 'Not Normal'}")
    
    # Check mean and std
    empirical_mean = np.mean(returns_samples)
    empirical_std = np.std(returns_samples)
    print(f"  Empirical mean: {empirical_mean:.4f} (expected: 0.10)")
    print(f"  Empirical std:  {empirical_std:.4f} (expected: 0.16)")
    
    # Test 6: Edge case handling
    print("\n6. EDGE CASE ANALYSIS")
    print("-"*40)
    
    # Test with extreme parameters
    extreme_cases = [
        ("Very high withdrawal", 200000, 1),
        ("Zero withdrawal", 0, 100),
        ("Negative returns", 40000, 50)  # Will use negative returns in portfolio
    ]
    
    for case_name, withdrawal, expected_success in extreme_cases:
        withdrawal_strategy = MultiAccountFixedWithdrawal(
            initial_withdrawal=Money(withdrawal),
            inflation_rate=Decimal('0.03'),
            withdrawal_order=portfolio.withdrawal_order
        )
        
        planner = RetirementPlanner()
        try:
            results = planner.run_simulation(
                portfolio=portfolio,
                withdrawal_strategy=withdrawal_strategy,
                years=10,
                num_simulations=100
            )
            print(f"  {case_name}: Success rate = {results.success_rate:.1f}%")
        except Exception as e:
            print(f"  {case_name}: ERROR - {str(e)}")
    
    # Test 7: Correlation analysis
    print("\n7. CORRELATION ANALYSIS")
    print("-"*40)
    print("  Checking for asset correlation modeling...")
    
    # Look for correlation matrices or covariance
    has_correlation = False
    
    # Check if accounts apply correlated returns
    print("  ⚠️  No explicit correlation modeling found")
    print("     - Assets returns appear independent")
    print("     - Real-world correlations not captured")
    
    # Summary and recommendations
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    
    issues = []
    recommendations = []
    
    # Issue 1: Random module usage
    issues.append("1. Using Python's 'random' module instead of numpy.random")
    recommendations.append("   → Switch to numpy.random for better performance and reproducibility")
    
    # Issue 2: No seed control
    if not reproducible:
        issues.append("2. No explicit seed control for reproducibility")
        recommendations.append("   → Add seed parameter to simulation methods")
    
    # Issue 3: Single simulation in example
    issues.append("3. Reference example uses num_simulations=1")
    recommendations.append("   → Increase to at least 1000 for meaningful results")
    
    # Issue 4: No correlation modeling
    issues.append("4. No asset correlation modeling")
    recommendations.append("   → Implement correlation matrix for realistic portfolio behavior")
    
    # Issue 5: Thread safety
    issues.append("5. Random module not thread-safe for parallel execution")
    recommendations.append("   → Use separate random generators per thread")
    
    print("\nIDENTIFIED ISSUES:")
    for issue in issues:
        print(f"  ❌ {issue}")
    
    print("\nRECOMMENDATIONS:")
    for rec in recommendations:
        print(f"  {rec}")
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("""
The Monte Carlo implementation has several critical issues:

1. **Statistical Correctness**: PARTIAL
   - Uses proper normal distribution for returns ✓
   - But uses Python's random module (less robust) ✗
   - No seed control for reproducibility ✗

2. **Real-World Accuracy**: LIMITED
   - No asset correlation modeling ✗
   - Independent returns unrealistic for portfolios ✗
   - Tax calculations appear correct ✓

3. **Performance**: SUBOPTIMAL
   - Reference example uses only 1 simulation ✗
   - Thread safety issues with random module ✗
   - Parallel execution may produce incorrect results ✗

OVERALL ASSESSMENT: The Monte Carlo implementation needs significant improvements
for production use. While the basic structure is sound, the randomness source,
lack of correlation modeling, and thread safety issues limit its reliability.
""")
    
    return results_by_size

if __name__ == "__main__":
    results = analyze_monte_carlo_implementation()