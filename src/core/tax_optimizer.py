"""Tax optimization strategies for retirement planning"""

from decimal import Decimal
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class AccountType(Enum):
    """Types of investment accounts for tax purposes"""
    TAXABLE = "taxable"
    TRADITIONAL_IRA = "traditional_ira"
    ROTH_IRA = "roth_ira"
    TRADITIONAL_401K = "traditional_401k"
    ROTH_401K = "roth_401k"
    HSA = "hsa"


@dataclass
class TaxBracket:
    """Federal tax bracket information"""
    min_income: Decimal
    max_income: Decimal
    rate: Decimal
    
    def applies_to(self, income: Decimal) -> bool:
        """Check if income falls in this bracket"""
        return self.min_income <= income <= self.max_income


@dataclass
class TaxOptimizationStrategy:
    """Result of tax optimization analysis"""
    recommended_withdrawals: Dict[AccountType, Decimal]
    estimated_tax: Decimal
    effective_tax_rate: Decimal
    tax_savings: Decimal
    roth_conversion_amount: Optional[Decimal]
    harvesting_recommendations: List[Dict]


class TaxOptimizer:
    """Optimizes tax strategies for retirement withdrawals"""
    
    # 2024 Tax brackets (simplified for example)
    TAX_BRACKETS_SINGLE = [
        TaxBracket(Decimal('0'), Decimal('11600'), Decimal('0')),  # Standard deduction
        TaxBracket(Decimal('11601'), Decimal('47150'), Decimal('0.10')),
        TaxBracket(Decimal('47151'), Decimal('100525'), Decimal('0.12')),
        TaxBracket(Decimal('100526'), Decimal('191950'), Decimal('0.22')),
        TaxBracket(Decimal('191951'), Decimal('243725'), Decimal('0.24')),
        TaxBracket(Decimal('243726'), Decimal('609350'), Decimal('0.32')),
        TaxBracket(Decimal('609351'), Decimal('523600'), Decimal('0.35')),
        TaxBracket(Decimal('523601'), Decimal('999999999'), Decimal('0.37'))
    ]
    
    TAX_BRACKETS_MARRIED = [
        TaxBracket(Decimal('0'), Decimal('23200'), Decimal('0')),  # Standard deduction
        TaxBracket(Decimal('23201'), Decimal('94300'), Decimal('0.10')),
        TaxBracket(Decimal('94301'), Decimal('201050'), Decimal('0.12')),
        TaxBracket(Decimal('201051'), Decimal('383900'), Decimal('0.22')),
        TaxBracket(Decimal('383901'), Decimal('487450'), Decimal('0.24')),
        TaxBracket(Decimal('487451'), Decimal('731200'), Decimal('0.32')),
        TaxBracket(Decimal('731201'), Decimal('647850'), Decimal('0.35')),
        TaxBracket(Decimal('647851'), Decimal('999999999'), Decimal('0.37'))
    ]
    
    # Capital gains tax rates
    CAPITAL_GAINS_RATES = {
        'short_term': None,  # Taxed as ordinary income
        'long_term': {
            'single': [
                (Decimal('44625'), Decimal('0')),
                (Decimal('492300'), Decimal('0.15')),
                (Decimal('999999999'), Decimal('0.20'))
            ],
            'married': [
                (Decimal('89250'), Decimal('0')),
                (Decimal('553850'), Decimal('0.15')),
                (Decimal('999999999'), Decimal('0.20'))
            ]
        }
    }
    
    def __init__(self, filing_status: str = 'single', state_tax_rate: Decimal = Decimal('0')):
        """
        Initialize tax optimizer
        
        Args:
            filing_status: 'single' or 'married'
            state_tax_rate: State income tax rate
        """
        self.filing_status = filing_status
        self.state_tax_rate = state_tax_rate
        self.tax_brackets = (self.TAX_BRACKETS_SINGLE if filing_status == 'single' 
                            else self.TAX_BRACKETS_MARRIED)
    
    def optimize_withdrawal_strategy(self,
                                    account_balances: Dict[AccountType, Decimal],
                                    withdrawal_amount: Decimal,
                                    current_age: int,
                                    other_income: Decimal = Decimal('0')) -> TaxOptimizationStrategy:
        """
        Optimize withdrawal strategy to minimize taxes
        
        Args:
            account_balances: Current balances by account type
            withdrawal_amount: Total amount to withdraw
            current_age: Current age (for RMD calculations)
            other_income: Other taxable income (Social Security, pensions, etc.)
        
        Returns:
            Optimized withdrawal strategy
        """
        # Strategy 1: Fill up lower tax brackets first
        recommended_withdrawals = {}
        remaining_withdrawal = withdrawal_amount
        current_taxable_income = other_income
        
        # Priority order for tax-efficient withdrawals
        if current_age >= 72:
            # RMDs must be taken first
            rmd_amount = self._calculate_rmd(account_balances, current_age)
            if AccountType.TRADITIONAL_IRA in account_balances and rmd_amount > 0:
                recommended_withdrawals[AccountType.TRADITIONAL_IRA] = min(rmd_amount, remaining_withdrawal)
                remaining_withdrawal -= recommended_withdrawals[AccountType.TRADITIONAL_IRA]
                current_taxable_income += recommended_withdrawals[AccountType.TRADITIONAL_IRA]
        
        # Step 1: Use taxable accounts first (already taxed)
        if AccountType.TAXABLE in account_balances and remaining_withdrawal > 0:
            taxable_withdrawal = min(account_balances[AccountType.TAXABLE], remaining_withdrawal)
            recommended_withdrawals[AccountType.TAXABLE] = taxable_withdrawal
            remaining_withdrawal -= taxable_withdrawal
            # Only gains are taxable, estimate 30% of withdrawal as gains
            current_taxable_income += taxable_withdrawal * Decimal('0.3')
        
        # Step 2: Fill up to 12% tax bracket with traditional IRA/401k
        if remaining_withdrawal > 0:
            bracket_room = self._calculate_bracket_room(current_taxable_income, Decimal('0.12'))
            if bracket_room > 0:
                trad_withdrawal = min(remaining_withdrawal, bracket_room)
                if AccountType.TRADITIONAL_IRA in account_balances:
                    actual_withdrawal = min(trad_withdrawal, account_balances[AccountType.TRADITIONAL_IRA])
                    recommended_withdrawals[AccountType.TRADITIONAL_IRA] = actual_withdrawal
                    remaining_withdrawal -= actual_withdrawal
                    current_taxable_income += actual_withdrawal
        
        # Step 3: Use Roth accounts for remaining (tax-free)
        if remaining_withdrawal > 0 and AccountType.ROTH_IRA in account_balances:
            roth_withdrawal = min(remaining_withdrawal, account_balances[AccountType.ROTH_IRA])
            recommended_withdrawals[AccountType.ROTH_IRA] = roth_withdrawal
            remaining_withdrawal -= roth_withdrawal
        
        # Step 4: Fill remaining from traditional accounts (will be taxed)
        if remaining_withdrawal > 0 and AccountType.TRADITIONAL_IRA in account_balances:
            final_withdrawal = min(remaining_withdrawal, 
                                  account_balances[AccountType.TRADITIONAL_IRA] - 
                                  recommended_withdrawals.get(AccountType.TRADITIONAL_IRA, Decimal('0')))
            if AccountType.TRADITIONAL_IRA in recommended_withdrawals:
                recommended_withdrawals[AccountType.TRADITIONAL_IRA] += final_withdrawal
            else:
                recommended_withdrawals[AccountType.TRADITIONAL_IRA] = final_withdrawal
            current_taxable_income += final_withdrawal
        
        # Calculate taxes
        estimated_tax = self._calculate_tax(current_taxable_income)
        effective_rate = estimated_tax / withdrawal_amount if withdrawal_amount > 0 else Decimal('0')
        
        # Calculate tax savings vs naive strategy
        naive_tax = self._calculate_tax(other_income + withdrawal_amount)
        tax_savings = naive_tax - estimated_tax
        
        # Roth conversion recommendation
        roth_conversion = self._recommend_roth_conversion(account_balances, current_taxable_income, current_age)
        
        # Tax loss harvesting recommendations
        harvesting = self._recommend_tax_loss_harvesting(account_balances)
        
        return TaxOptimizationStrategy(
            recommended_withdrawals=recommended_withdrawals,
            estimated_tax=estimated_tax,
            effective_tax_rate=effective_rate,
            tax_savings=tax_savings,
            roth_conversion_amount=roth_conversion,
            harvesting_recommendations=harvesting
        )
    
    def _calculate_tax(self, taxable_income: Decimal) -> Decimal:
        """Calculate federal income tax"""
        tax = Decimal('0')
        
        for bracket in self.tax_brackets:
            if taxable_income > bracket.max_income:
                tax += (bracket.max_income - bracket.min_income) * bracket.rate
            elif taxable_income > bracket.min_income:
                tax += (taxable_income - bracket.min_income) * bracket.rate
                break
        
        # Add state tax
        tax += taxable_income * self.state_tax_rate
        
        return tax
    
    def _calculate_bracket_room(self, current_income: Decimal, target_rate: Decimal) -> Decimal:
        """Calculate room left in a tax bracket"""
        for bracket in self.tax_brackets:
            if bracket.rate == target_rate and current_income < bracket.max_income:
                return bracket.max_income - current_income
        return Decimal('0')
    
    def _calculate_rmd(self, account_balances: Dict[AccountType, Decimal], age: int) -> Decimal:
        """Calculate Required Minimum Distribution"""
        if age < 72:
            return Decimal('0')
        
        # IRS Uniform Lifetime Table (simplified)
        life_expectancy = {
            72: Decimal('27.4'), 73: Decimal('26.5'), 74: Decimal('25.5'),
            75: Decimal('24.6'), 76: Decimal('23.7'), 77: Decimal('22.9'),
            78: Decimal('22.0'), 79: Decimal('21.1'), 80: Decimal('20.2'),
            85: Decimal('16.0'), 90: Decimal('12.2'), 95: Decimal('9.1')
        }
        
        divisor = life_expectancy.get(age, Decimal('20'))  # Default divisor
        
        # RMD applies to traditional accounts
        traditional_balance = (account_balances.get(AccountType.TRADITIONAL_IRA, Decimal('0')) +
                              account_balances.get(AccountType.TRADITIONAL_401K, Decimal('0')))
        
        return traditional_balance / divisor
    
    def _recommend_roth_conversion(self, 
                                  account_balances: Dict[AccountType, Decimal],
                                  current_income: Decimal,
                                  age: int) -> Optional[Decimal]:
        """Recommend Roth conversion amount"""
        if AccountType.TRADITIONAL_IRA not in account_balances:
            return None
        
        # If under 60 and in low tax bracket, consider conversion
        if age < 60 and current_income < Decimal('100000'):
            # Convert up to top of 12% bracket
            bracket_room = self._calculate_bracket_room(current_income, Decimal('0.12'))
            if bracket_room > 0:
                return min(bracket_room, account_balances[AccountType.TRADITIONAL_IRA] * Decimal('0.25'))
        
        return None
    
    def _recommend_tax_loss_harvesting(self, 
                                      account_balances: Dict[AccountType, Decimal]) -> List[Dict]:
        """Recommend tax loss harvesting strategies"""
        recommendations = []
        
        if AccountType.TAXABLE in account_balances:
            # Simplified recommendation
            recommendations.append({
                'strategy': 'tax_loss_harvesting',
                'description': 'Consider selling losing positions to offset gains',
                'potential_savings': account_balances[AccountType.TAXABLE] * Decimal('0.003')  # 0.3% estimate
            })
        
        return recommendations
    
    def calculate_lifetime_tax_efficiency(self,
                                         portfolio_value: Decimal,
                                         years_to_retirement: int,
                                         retirement_years: int,
                                         contribution_rate: Decimal) -> Dict:
        """
        Calculate lifetime tax efficiency metrics
        
        Returns:
            Dictionary with tax efficiency metrics
        """
        # Pre-retirement phase (accumulation)
        pre_retirement_tax = Decimal('0')
        annual_contribution = portfolio_value * contribution_rate
        
        for year in range(years_to_retirement):
            # Assume contributions to traditional accounts
            tax_deduction = annual_contribution * Decimal('0.22')  # Assumed tax bracket
            pre_retirement_tax -= tax_deduction
        
        # Retirement phase (distribution)
        retirement_tax = Decimal('0')
        annual_withdrawal = portfolio_value / Decimal(str(retirement_years))
        
        for year in range(retirement_years):
            year_tax = self._calculate_tax(annual_withdrawal)
            retirement_tax += year_tax
        
        total_lifetime_tax = pre_retirement_tax + retirement_tax
        
        return {
            'pre_retirement_tax_benefit': pre_retirement_tax,
            'retirement_tax_liability': retirement_tax,
            'net_lifetime_tax': total_lifetime_tax,
            'effective_tax_rate': total_lifetime_tax / (portfolio_value * Decimal('2'))  # Rough estimate
        }