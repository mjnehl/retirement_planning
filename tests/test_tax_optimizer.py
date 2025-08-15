"""Unit tests for tax optimization strategies"""

import unittest
from decimal import Decimal
import sys
sys.path.append('../src')
from core.tax_optimizer import TaxOptimizer, AccountType, TaxBracket, TaxOptimizationStrategy


class TestTaxOptimizer(unittest.TestCase):
    """Test tax optimization functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer_single = TaxOptimizer(filing_status='single', state_tax_rate=Decimal('0.05'))
        self.optimizer_married = TaxOptimizer(filing_status='married', state_tax_rate=Decimal('0.05'))
    
    def test_tax_calculation_single(self):
        """Test federal tax calculation for single filer"""
        # Test standard deduction (no tax)
        tax = self.optimizer_single._calculate_tax(Decimal('11000'))
        self.assertEqual(tax, Decimal('550'))  # Only state tax (5% of 11000)
        
        # Test 10% bracket
        tax = self.optimizer_single._calculate_tax(Decimal('30000'))
        # Federal: (30000 - 11600) * 0.10 = 1840
        # State: 30000 * 0.05 = 1500
        # Total: 3340
        self.assertAlmostEqual(float(tax), 3340, places=0)
        
        # Test 12% bracket
        tax = self.optimizer_single._calculate_tax(Decimal('75000'))
        # More complex calculation across brackets
        self.assertGreater(tax, Decimal('10000'))
        self.assertLess(tax, Decimal('15000'))
    
    def test_tax_calculation_married(self):
        """Test federal tax calculation for married filing jointly"""
        # Test standard deduction (no tax)
        tax = self.optimizer_married._calculate_tax(Decimal('23000'))
        self.assertEqual(tax, Decimal('1150'))  # Only state tax
        
        # Test 10% bracket
        tax = self.optimizer_married._calculate_tax(Decimal('50000'))
        # Federal: (50000 - 23200) * 0.10 = 2680
        # State: 50000 * 0.05 = 2500
        # Total: 5180
        self.assertAlmostEqual(float(tax), 5180, places=0)
    
    def test_withdrawal_optimization_basic(self):
        """Test basic withdrawal optimization"""
        account_balances = {
            AccountType.TAXABLE: Decimal('200000'),
            AccountType.TRADITIONAL_IRA: Decimal('300000'),
            AccountType.ROTH_IRA: Decimal('100000')
        }
        
        strategy = self.optimizer_single.optimize_withdrawal_strategy(
            account_balances=account_balances,
            withdrawal_amount=Decimal('50000'),
            current_age=65,
            other_income=Decimal('20000')
        )
        
        # Check strategy structure
        self.assertIsInstance(strategy, TaxOptimizationStrategy)
        self.assertIsNotNone(strategy.recommended_withdrawals)
        self.assertIsNotNone(strategy.estimated_tax)
        self.assertIsNotNone(strategy.effective_tax_rate)
        
        # Should prioritize taxable account first
        self.assertIn(AccountType.TAXABLE, strategy.recommended_withdrawals)
        
        # Total withdrawals should equal requested amount
        total_withdrawal = sum(strategy.recommended_withdrawals.values())
        self.assertAlmostEqual(float(total_withdrawal), 50000, places=0)
    
    def test_rmd_calculation(self):
        """Test Required Minimum Distribution calculation"""
        account_balances = {
            AccountType.TRADITIONAL_IRA: Decimal('500000'),
            AccountType.TRADITIONAL_401K: Decimal('300000')
        }
        
        # Age 71 - no RMD
        rmd = self.optimizer_single._calculate_rmd(account_balances, 71)
        self.assertEqual(rmd, Decimal('0'))
        
        # Age 72 - RMD required
        rmd = self.optimizer_single._calculate_rmd(account_balances, 72)
        # Total: 800000 / 27.4 ≈ 29197
        self.assertAlmostEqual(float(rmd), 29197, places=0)
        
        # Age 80 - higher RMD
        rmd = self.optimizer_single._calculate_rmd(account_balances, 80)
        # Total: 800000 / 20.2 ≈ 39604
        self.assertAlmostEqual(float(rmd), 39604, places=0)
    
    def test_withdrawal_with_rmd(self):
        """Test withdrawal optimization with RMD requirements"""
        account_balances = {
            AccountType.TRADITIONAL_IRA: Decimal('400000'),
            AccountType.ROTH_IRA: Decimal('200000')
        }
        
        strategy = self.optimizer_single.optimize_withdrawal_strategy(
            account_balances=account_balances,
            withdrawal_amount=Decimal('30000'),
            current_age=72,  # RMD age
            other_income=Decimal('15000')
        )
        
        # Should include RMD from traditional IRA
        self.assertIn(AccountType.TRADITIONAL_IRA, strategy.recommended_withdrawals)
        
        # RMD should be taken first
        rmd_amount = self.optimizer_single._calculate_rmd(account_balances, 72)
        trad_withdrawal = strategy.recommended_withdrawals.get(AccountType.TRADITIONAL_IRA, Decimal('0'))
        self.assertGreaterEqual(trad_withdrawal, min(rmd_amount, Decimal('30000')))
    
    def test_tax_bracket_room_calculation(self):
        """Test calculation of room in tax brackets"""
        # Single filer with $50,000 income
        room = self.optimizer_single._calculate_bracket_room(Decimal('50000'), Decimal('0.12'))
        # 12% bracket goes up to $100,525
        expected_room = Decimal('100525') - Decimal('50000')
        self.assertEqual(room, expected_room)
        
        # At top of bracket
        room = self.optimizer_single._calculate_bracket_room(Decimal('100525'), Decimal('0.12'))
        self.assertEqual(room, Decimal('0'))
        
        # Above bracket
        room = self.optimizer_single._calculate_bracket_room(Decimal('150000'), Decimal('0.12'))
        self.assertEqual(room, Decimal('0'))
    
    def test_roth_conversion_recommendation(self):
        """Test Roth conversion recommendations"""
        account_balances = {
            AccountType.TRADITIONAL_IRA: Decimal('200000'),
            AccountType.ROTH_IRA: Decimal('50000')
        }
        
        # Young person in low bracket - should recommend conversion
        strategy = self.optimizer_single.optimize_withdrawal_strategy(
            account_balances=account_balances,
            withdrawal_amount=Decimal('30000'),
            current_age=55,
            other_income=Decimal('40000')
        )
        
        self.assertIsNotNone(strategy.roth_conversion_amount)
        if strategy.roth_conversion_amount:
            self.assertGreater(strategy.roth_conversion_amount, Decimal('0'))
        
        # Older person or high income - might not recommend
        strategy_old = self.optimizer_single.optimize_withdrawal_strategy(
            account_balances=account_balances,
            withdrawal_amount=Decimal('30000'),
            current_age=70,
            other_income=Decimal('150000')
        )
        
        # Should not recommend conversion for older/high income
        self.assertIsNone(strategy_old.roth_conversion_amount)
    
    def test_tax_loss_harvesting_recommendation(self):
        """Test tax loss harvesting recommendations"""
        account_balances = {
            AccountType.TAXABLE: Decimal('300000'),
            AccountType.TRADITIONAL_IRA: Decimal('200000')
        }
        
        strategy = self.optimizer_single.optimize_withdrawal_strategy(
            account_balances=account_balances,
            withdrawal_amount=Decimal('40000'),
            current_age=65,
            other_income=Decimal('25000')
        )
        
        # Should have harvesting recommendations for taxable account
        self.assertIsNotNone(strategy.harvesting_recommendations)
        self.assertGreater(len(strategy.harvesting_recommendations), 0)
        
        # Check recommendation structure
        if strategy.harvesting_recommendations:
            rec = strategy.harvesting_recommendations[0]
            self.assertIn('strategy', rec)
            self.assertIn('description', rec)
            self.assertIn('potential_savings', rec)
    
    def test_tax_efficiency_comparison(self):
        """Test tax efficiency between different strategies"""
        account_balances = {
            AccountType.TAXABLE: Decimal('100000'),
            AccountType.TRADITIONAL_IRA: Decimal('300000'),
            AccountType.ROTH_IRA: Decimal('200000')
        }
        
        # Optimized strategy
        optimized = self.optimizer_single.optimize_withdrawal_strategy(
            account_balances=account_balances,
            withdrawal_amount=Decimal('60000'),
            current_age=65,
            other_income=Decimal('20000')
        )
        
        # Calculate naive tax (all from traditional)
        naive_tax = self.optimizer_single._calculate_tax(Decimal('20000') + Decimal('60000'))
        
        # Optimized should be better
        self.assertLess(optimized.estimated_tax, naive_tax)
        self.assertGreater(optimized.tax_savings, Decimal('0'))
    
    def test_lifetime_tax_efficiency(self):
        """Test lifetime tax efficiency calculation"""
        results = self.optimizer_single.calculate_lifetime_tax_efficiency(
            portfolio_value=Decimal('500000'),
            years_to_retirement=10,
            retirement_years=25,
            contribution_rate=Decimal('0.10')
        )
        
        # Check result structure
        self.assertIn('pre_retirement_tax_benefit', results)
        self.assertIn('retirement_tax_liability', results)
        self.assertIn('net_lifetime_tax', results)
        self.assertIn('effective_tax_rate', results)
        
        # Pre-retirement should be negative (tax benefit)
        self.assertLess(results['pre_retirement_tax_benefit'], Decimal('0'))
        
        # Retirement tax should be positive
        self.assertGreater(results['retirement_tax_liability'], Decimal('0'))
    
    def test_account_type_enum(self):
        """Test AccountType enum values"""
        self.assertEqual(AccountType.TAXABLE.value, 'taxable')
        self.assertEqual(AccountType.TRADITIONAL_IRA.value, 'traditional_ira')
        self.assertEqual(AccountType.ROTH_IRA.value, 'roth_ira')
        self.assertEqual(AccountType.HSA.value, 'hsa')
    
    def test_tax_bracket_application(self):
        """Test tax bracket application logic"""
        bracket = TaxBracket(
            min_income=Decimal('50000'),
            max_income=Decimal('100000'),
            rate=Decimal('0.22')
        )
        
        # Income in bracket
        self.assertTrue(bracket.applies_to(Decimal('75000')))
        
        # Income at boundaries
        self.assertTrue(bracket.applies_to(Decimal('50000')))
        self.assertTrue(bracket.applies_to(Decimal('100000')))
        
        # Income outside bracket
        self.assertFalse(bracket.applies_to(Decimal('49999')))
        self.assertFalse(bracket.applies_to(Decimal('100001')))


if __name__ == '__main__':
    unittest.main()