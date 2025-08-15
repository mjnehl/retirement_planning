"""Social Security benefits calculator with optimization strategies"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class ClaimingStrategy(Enum):
    """Social Security claiming strategies"""
    EARLY = "early"  # Age 62
    FULL = "full"    # Full retirement age (66-67)
    DELAYED = "delayed"  # Age 70


@dataclass
class EarningsRecord:
    """Annual earnings record for Social Security calculation"""
    year: int
    earnings: Decimal
    
    def get_indexed_earnings(self, index_factor: Decimal) -> Decimal:
        """Get indexed earnings for AIME calculation"""
        return self.earnings * index_factor


@dataclass
class SocialSecurityBenefit:
    """Social Security benefit calculation results"""
    monthly_benefit: Decimal
    annual_benefit: Decimal
    lifetime_benefit: Decimal
    claiming_age: int
    full_retirement_age: int
    primary_insurance_amount: Decimal
    average_indexed_monthly_earnings: Decimal
    break_even_age: Optional[int] = None
    reduction_percentage: Optional[Decimal] = None
    increase_percentage: Optional[Decimal] = None


class SocialSecurityCalculator:
    """Calculator for Social Security benefits and optimization"""
    
    # 2024 bend points for PIA calculation
    BEND_POINTS = [
        (Decimal('1174'), Decimal('0.90')),  # 90% of first $1,174
        (Decimal('7078'), Decimal('0.32')),  # 32% of amount over $1,174 through $7,078
        (Decimal('999999'), Decimal('0.15'))  # 15% of amount over $7,078
    ]
    
    # Wage index factors (simplified - normally would use SSA tables)
    WAGE_INDEX_FACTORS = {
        2024: Decimal('1.00'),
        2023: Decimal('1.03'),
        2022: Decimal('1.08'),
        2021: Decimal('1.12'),
        2020: Decimal('1.15'),
        2019: Decimal('1.18'),
        2018: Decimal('1.21'),
        2015: Decimal('1.30'),
        2010: Decimal('1.45'),
        2005: Decimal('1.65'),
        2000: Decimal('1.90'),
        1995: Decimal('2.20'),
        1990: Decimal('2.60')
    }
    
    # Maximum taxable earnings by year (simplified)
    MAX_TAXABLE_EARNINGS = {
        2024: Decimal('168600'),
        2023: Decimal('160200'),
        2022: Decimal('147000'),
        2021: Decimal('142800'),
        2020: Decimal('137700'),
        2019: Decimal('132900'),
        2018: Decimal('128400')
    }
    
    def __init__(self, birth_year: int, earnings_history: Optional[List[EarningsRecord]] = None):
        """
        Initialize Social Security calculator
        
        Args:
            birth_year: Year of birth
            earnings_history: Optional list of earnings records
        """
        self.birth_year = birth_year
        self.earnings_history = earnings_history or []
        self.full_retirement_age = self._calculate_fra()
    
    def _calculate_fra(self) -> int:
        """Calculate Full Retirement Age based on birth year"""
        if self.birth_year <= 1937:
            return 65
        elif self.birth_year <= 1942:
            # Gradually increases from 65 to 66
            return 65 + (self.birth_year - 1937) * 2 // 12
        elif self.birth_year <= 1954:
            return 66
        elif self.birth_year <= 1959:
            # Gradually increases from 66 to 67
            return 66 + (self.birth_year - 1954) * 2 // 12
        else:
            return 67
    
    def calculate_aime(self, earnings_history: Optional[List[EarningsRecord]] = None) -> Decimal:
        """
        Calculate Average Indexed Monthly Earnings (AIME)
        
        Args:
            earnings_history: Optional earnings history (uses instance history if not provided)
        
        Returns:
            AIME value
        """
        history = earnings_history or self.earnings_history
        
        if not history:
            # Use default estimate if no history provided
            return Decimal('5000')  # Roughly average AIME
        
        # Index earnings to current year
        indexed_earnings = []
        for record in history:
            index_factor = self.WAGE_INDEX_FACTORS.get(record.year, Decimal('1.0'))
            # Cap at maximum taxable earnings
            max_earnings = self.MAX_TAXABLE_EARNINGS.get(record.year, Decimal('168600'))
            capped_earnings = min(record.earnings, max_earnings)
            indexed = capped_earnings * index_factor
            indexed_earnings.append(indexed)
        
        # Sort and take highest 35 years
        indexed_earnings.sort(reverse=True)
        top_35_years = indexed_earnings[:35]
        
        # Pad with zeros if less than 35 years
        while len(top_35_years) < 35:
            top_35_years.append(Decimal('0'))
        
        # Calculate average monthly earnings
        total_earnings = sum(top_35_years)
        aime = total_earnings / Decimal('420')  # 35 years * 12 months
        
        return aime.quantize(Decimal('1'))  # Round to nearest dollar
    
    def calculate_pia(self, aime: Optional[Decimal] = None) -> Decimal:
        """
        Calculate Primary Insurance Amount (PIA)
        
        Args:
            aime: Average Indexed Monthly Earnings
        
        Returns:
            Primary Insurance Amount
        """
        if aime is None:
            aime = self.calculate_aime()
        
        pia = Decimal('0')
        remaining_aime = aime
        
        for i, (bend_point, rate) in enumerate(self.BEND_POINTS):
            if i == 0:
                # First bend point
                amount = min(remaining_aime, bend_point)
                pia += amount * rate
                remaining_aime -= amount
            elif i == 1:
                # Second bend point
                prev_bend = self.BEND_POINTS[0][0]
                amount = min(remaining_aime, bend_point - prev_bend)
                pia += amount * rate
                remaining_aime -= amount
            else:
                # Above second bend point
                pia += remaining_aime * rate
                break
        
        return pia.quantize(Decimal('0.01'))  # Round to cents
    
    def calculate_benefit(self, 
                         claiming_age: int,
                         pia: Optional[Decimal] = None,
                         life_expectancy: int = 85) -> SocialSecurityBenefit:
        """
        Calculate Social Security benefit at a specific claiming age
        
        Args:
            claiming_age: Age at which to claim benefits (62-70)
            pia: Primary Insurance Amount (calculated if not provided)
            life_expectancy: Expected lifespan for lifetime benefit calculation
        
        Returns:
            SocialSecurityBenefit with detailed calculations
        """
        if claiming_age < 62 or claiming_age > 70:
            raise ValueError("Claiming age must be between 62 and 70")
        
        if pia is None:
            aime = self.calculate_aime()
            pia = self.calculate_pia(aime)
        else:
            aime = None
        
        # Calculate adjustment based on claiming age
        if claiming_age < self.full_retirement_age:
            # Early retirement reduction
            months_early = (self.full_retirement_age - claiming_age) * 12
            
            # First 36 months: 5/9 of 1% per month
            # After 36 months: 5/12 of 1% per month
            if months_early <= 36:
                reduction = months_early * Decimal('5') / Decimal('900')
            else:
                reduction = (Decimal('36') * Decimal('5') / Decimal('900') +
                           (months_early - 36) * Decimal('5') / Decimal('1200'))
            
            monthly_benefit = pia * (Decimal('1') - reduction)
            adjustment_pct = -reduction
            
        elif claiming_age > self.full_retirement_age:
            # Delayed retirement credits
            months_delayed = (claiming_age - self.full_retirement_age) * 12
            
            # 8% per year (2/3 of 1% per month) for those born 1943 or later
            if self.birth_year >= 1943:
                increase = months_delayed * Decimal('2') / Decimal('300')
            else:
                increase = months_delayed * Decimal('0.055') / Decimal('12')  # Older rate
            
            monthly_benefit = pia * (Decimal('1') + increase)
            adjustment_pct = increase
            
        else:
            # Claiming at FRA
            monthly_benefit = pia
            adjustment_pct = Decimal('0')
        
        # Calculate annual and lifetime benefits
        annual_benefit = monthly_benefit * Decimal('12')
        years_receiving = life_expectancy - claiming_age
        lifetime_benefit = annual_benefit * Decimal(str(years_receiving))
        
        # Calculate break-even age vs FRA
        if claiming_age != self.full_retirement_age:
            fra_monthly = pia
            fra_annual = fra_monthly * Decimal('12')
            
            if claiming_age < self.full_retirement_age:
                # Early claiming - when does total benefit exceed FRA start?
                years_early = self.full_retirement_age - claiming_age
                early_total_at_fra = annual_benefit * Decimal(str(years_early))
                
                if annual_benefit < fra_annual:
                    years_to_break_even = early_total_at_fra / (fra_annual - annual_benefit)
                    break_even_age = self.full_retirement_age + int(years_to_break_even)
                else:
                    break_even_age = None
            else:
                # Delayed claiming - when does higher benefit make up for lost years?
                years_delayed = claiming_age - self.full_retirement_age
                lost_benefits = fra_annual * Decimal(str(years_delayed))
                annual_difference = annual_benefit - fra_annual
                
                if annual_difference > 0:
                    years_to_break_even = lost_benefits / annual_difference
                    break_even_age = claiming_age + int(years_to_break_even)
                else:
                    break_even_age = None
        else:
            break_even_age = None
        
        return SocialSecurityBenefit(
            monthly_benefit=monthly_benefit.quantize(Decimal('1')),
            annual_benefit=annual_benefit.quantize(Decimal('1')),
            lifetime_benefit=lifetime_benefit.quantize(Decimal('1')),
            claiming_age=claiming_age,
            full_retirement_age=self.full_retirement_age,
            primary_insurance_amount=pia,
            average_indexed_monthly_earnings=aime or self.calculate_aime(),
            break_even_age=break_even_age,
            reduction_percentage=adjustment_pct if adjustment_pct < 0 else None,
            increase_percentage=adjustment_pct if adjustment_pct > 0 else None
        )
    
    def optimize_claiming_strategy(self,
                                  life_expectancy: int = 85,
                                  discount_rate: Decimal = Decimal('0.03'),
                                  include_spousal: bool = False,
                                  spouse_age_difference: int = 0) -> Dict[str, SocialSecurityBenefit]:
        """
        Optimize Social Security claiming strategy
        
        Args:
            life_expectancy: Expected lifespan
            discount_rate: Discount rate for present value calculations
            include_spousal: Whether to include spousal benefits
            spouse_age_difference: Age difference (positive if spouse is younger)
        
        Returns:
            Dictionary of benefits by strategy
        """
        strategies = {}
        
        # Calculate benefits for different claiming ages
        for age in [62, self.full_retirement_age, 70]:
            benefit = self.calculate_benefit(age, life_expectancy=life_expectancy)
            
            # Calculate present value of lifetime benefits
            pv = self._calculate_present_value(
                benefit.annual_benefit,
                claiming_age=age,
                life_expectancy=life_expectancy,
                discount_rate=discount_rate
            )
            
            if age == 62:
                strategy_name = "early"
            elif age == self.full_retirement_age:
                strategy_name = "full"
            else:
                strategy_name = "delayed"
            
            strategies[strategy_name] = benefit
            strategies[f"{strategy_name}_pv"] = pv
        
        # Find optimal strategy based on present value
        optimal_strategy = max(
            ["early", "full", "delayed"],
            key=lambda s: strategies[f"{s}_pv"]
        )
        strategies["optimal"] = strategies[optimal_strategy]
        
        return strategies
    
    def _calculate_present_value(self,
                                annual_benefit: Decimal,
                                claiming_age: int,
                                life_expectancy: int,
                                discount_rate: Decimal) -> Decimal:
        """Calculate present value of benefit stream"""
        pv = Decimal('0')
        current_age = datetime.now().year - self.birth_year
        
        for year in range(claiming_age, life_expectancy + 1):
            years_from_now = year - current_age
            if years_from_now > 0:
                discount_factor = (Decimal('1') + discount_rate) ** years_from_now
                pv += annual_benefit / discount_factor
        
        return pv.quantize(Decimal('1'))
    
    def calculate_spousal_benefit(self,
                                 primary_pia: Decimal,
                                 spouse_pia: Decimal,
                                 spouse_claiming_age: int,
                                 spouse_fra: int) -> Decimal:
        """
        Calculate spousal benefit
        
        Args:
            primary_pia: Primary earner's PIA
            spouse_pia: Spouse's own PIA
            spouse_claiming_age: Age spouse claims benefit
            spouse_fra: Spouse's full retirement age
        
        Returns:
            Monthly spousal benefit amount
        """
        # Spousal benefit is 50% of primary PIA at FRA
        max_spousal = primary_pia * Decimal('0.5')
        
        # Compare with spouse's own benefit
        if spouse_pia >= max_spousal:
            # Spouse's own benefit is higher
            return spouse_pia
        
        # Calculate spousal benefit with early claiming reduction if applicable
        if spouse_claiming_age < spouse_fra:
            months_early = (spouse_fra - spouse_claiming_age) * 12
            # Reduction is 25/36 of 1% for first 36 months, 5/12 of 1% thereafter
            if months_early <= 36:
                reduction = months_early * Decimal('25') / Decimal('3600')
            else:
                reduction = (Decimal('36') * Decimal('25') / Decimal('3600') +
                           (months_early - 36) * Decimal('5') / Decimal('1200'))
            
            spousal_benefit = max_spousal * (Decimal('1') - reduction)
        else:
            spousal_benefit = max_spousal
        
        return max(spousal_benefit, spouse_pia)
    
    def calculate_survivor_benefit(self,
                                  deceased_benefit: Decimal,
                                  survivor_age: int,
                                  survivor_fra: int) -> Decimal:
        """
        Calculate survivor benefit
        
        Args:
            deceased_benefit: Deceased spouse's monthly benefit
            survivor_age: Age of survivor when claiming
            survivor_fra: Survivor's full retirement age
        
        Returns:
            Monthly survivor benefit
        """
        if survivor_age >= survivor_fra:
            # Full survivor benefit
            return deceased_benefit
        elif survivor_age >= 60:
            # Reduced survivor benefit (71.5% to 99%)
            months_early = (survivor_fra - survivor_age) * 12
            max_reduction = Decimal('0.285')  # 28.5% maximum reduction
            reduction = min(max_reduction, months_early * Decimal('0.00396'))
            return deceased_benefit * (Decimal('1') - reduction)
        else:
            # Too young for survivor benefits
            return Decimal('0')