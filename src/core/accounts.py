"""Account types for retirement planning"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, Tuple
from enum import Enum

from .money import Money


class AccountType(Enum):
    """Types of accounts"""
    CASH = "cash"
    TAXABLE = "taxable"
    PRIVATE_STOCK = "private_stock"
    INHERITANCE = "inheritance"
    IRA = "ira"
    ROTH_IRA = "roth_ira"
    MORTGAGE = "mortgage"
    INCOME = "income"


class Account(ABC):
    """Base account class"""
    
    def __init__(
        self,
        account_id: str,
        account_type: AccountType,
        balance: Money,
        name: Optional[str] = None
    ):
        self.account_id = account_id
        self.account_type = account_type
        self.balance = balance
        self.name = name or f"{account_type.value}_account"
    
    @abstractmethod
    def withdraw(self, amount: Money, age: int = 65) -> Tuple[Money, Money]:
        """
        Withdraw from account
        Returns: (actual_withdrawal, tax_owed)
        """
        pass
    
    @abstractmethod
    def deposit(self, amount: Money) -> None:
        """Deposit to account"""
        pass
    
    @abstractmethod
    def apply_returns(self, year: int) -> Money:
        """Apply investment returns for the year"""
        pass
    
    def get_balance(self) -> Money:
        """Get current balance"""
        return self.balance
    
    def is_depleted(self) -> bool:
        """Check if account is depleted"""
        return not self.balance.is_positive()


@dataclass
class CashAccount(Account):
    """Cash/savings account with fixed return"""
    
    annual_return: Decimal = Decimal('0.02')  # 2% savings rate
    
    def __init__(
        self,
        account_id: str,
        balance: Money,
        annual_return: Decimal = Decimal('0.02'),
        name: Optional[str] = None
    ):
        super().__init__(account_id, AccountType.CASH, balance, name)
        self.annual_return = annual_return
    
    def withdraw(self, amount: Money, age: int = 65) -> Tuple[Money, Money]:
        """Withdraw from cash account (no taxes or penalties)"""
        if amount.amount > self.balance.amount:
            actual_withdrawal = self.balance
            self.balance = Money(Decimal('0'))
        else:
            actual_withdrawal = amount
            self.balance = self.balance.subtract(amount)
        
        return actual_withdrawal, Money(Decimal('0'))  # No tax on cash withdrawals
    
    def deposit(self, amount: Money) -> None:
        """Deposit to cash account"""
        self.balance = self.balance.add(amount)
    
    def apply_returns(self, year: int) -> Money:
        """Apply fixed interest rate"""
        interest = self.balance.multiply(self.annual_return)
        self.balance = self.balance.add(interest)
        return interest


@dataclass
class TaxableAccount(Account):
    """Taxable investment account"""
    
    stock_allocation: Decimal = Decimal('0.80')  # 80% stocks
    cash_allocation: Decimal = Decimal('0.20')   # 20% cash
    stock_return: Decimal = Decimal('0.10')
    stock_volatility: Decimal = Decimal('0.18')
    cash_return: Decimal = Decimal('0.02')
    dividend_yield: Decimal = Decimal('0.02')
    capital_gains_tax_rate: Decimal = Decimal('0.15')  # Long-term cap gains
    
    def __init__(
        self,
        account_id: str,
        balance: Money,
        stock_allocation: Decimal = Decimal('0.80'),
        name: Optional[str] = None
    ):
        super().__init__(account_id, AccountType.TAXABLE, balance, name)
        self.stock_allocation = stock_allocation
        self.cash_allocation = Decimal('1') - stock_allocation
        self.cost_basis = balance  # Track for capital gains
    
    def withdraw(self, amount: Money, age: int = 65) -> Tuple[Money, Money]:
        """Withdraw from taxable account with capital gains tax"""
        # Store original balance for tax calculation
        original_balance = self.balance
        
        if amount.amount > self.balance.amount:
            actual_withdrawal = self.balance
            self.balance = Money(Decimal('0'))
        else:
            actual_withdrawal = amount
            self.balance = self.balance.subtract(amount)
        
        # Calculate capital gains tax (simplified)
        if self.cost_basis.amount > 0 and original_balance.amount > 0:
            gain_ratio = max(
                (original_balance.amount - self.cost_basis.amount) / original_balance.amount,
                Decimal('0')
            )
            taxable_gain = actual_withdrawal.multiply(gain_ratio)
            tax_owed = taxable_gain.multiply(self.capital_gains_tax_rate)
        else:
            tax_owed = Money(Decimal('0'))
        
        # Adjust cost basis proportionally
        if original_balance.amount > 0:
            reduction_ratio = actual_withdrawal.amount / original_balance.amount
            self.cost_basis = self.cost_basis.multiply(Decimal('1') - reduction_ratio)
            
            # Ensure cost basis doesn't go negative
            if self.cost_basis.amount < 0:
                self.cost_basis = Money(Decimal('0'))
        
        if self.balance.amount <= 0:
            self.cost_basis = Money(Decimal('0'))
        
        return actual_withdrawal, tax_owed
    
    def deposit(self, amount: Money) -> None:
        """Deposit to taxable account"""
        self.balance = self.balance.add(amount)
        self.cost_basis = self.cost_basis.add(amount)
    
    def apply_returns(self, year: int) -> Money:
        """Apply investment returns (simplified - using average return)"""
        import random
        
        # Calculate returns for stock portion
        stock_value = self.balance.multiply(self.stock_allocation)
        stock_return = Decimal(str(random.gauss(
            float(self.stock_return),
            float(self.stock_volatility)
        )))
        stock_growth = stock_value.multiply(stock_return)
        
        # Calculate returns for cash portion
        cash_value = self.balance.multiply(self.cash_allocation)
        cash_growth = cash_value.multiply(self.cash_return)
        
        # Calculate dividends (taxable in current year)
        dividends = stock_value.multiply(self.dividend_yield)
        
        # Total return
        total_return = stock_growth.add(cash_growth).add(dividends)
        self.balance = self.balance.add(total_return)
        
        return total_return


@dataclass
class IRAAccount(Account):
    """Traditional IRA account"""
    
    stock_allocation: Decimal = Decimal('0.70')  # 70% stocks (more conservative)
    cash_allocation: Decimal = Decimal('0.30')   # 30% cash
    stock_return: Decimal = Decimal('0.10')
    stock_volatility: Decimal = Decimal('0.18')
    cash_return: Decimal = Decimal('0.02')
    early_withdrawal_penalty: Decimal = Decimal('0.10')  # 10% penalty before 59.5
    ordinary_income_tax_rate: Decimal = Decimal('0.22')  # 22% tax bracket
    
    def __init__(
        self,
        account_id: str,
        balance: Money,
        stock_allocation: Decimal = Decimal('0.70'),
        name: Optional[str] = None
    ):
        super().__init__(account_id, AccountType.IRA, balance, name)
        self.stock_allocation = stock_allocation
        self.cash_allocation = Decimal('1') - stock_allocation
    
    def withdraw(self, amount: Money, age: int = 65) -> Tuple[Money, Money]:
        """Withdraw from IRA with taxes and potential penalties"""
        if amount.amount > self.balance.amount:
            actual_withdrawal = self.balance
            self.balance = Money(Decimal('0'))
        else:
            actual_withdrawal = amount
            self.balance = self.balance.subtract(amount)
        
        # Calculate taxes (ordinary income)
        tax_owed = actual_withdrawal.multiply(self.ordinary_income_tax_rate)
        
        # Add early withdrawal penalty if under 59.5
        if age < 59.5:
            penalty = actual_withdrawal.multiply(self.early_withdrawal_penalty)
            tax_owed = tax_owed.add(penalty)
        
        return actual_withdrawal, tax_owed
    
    def calculate_rmd(self, age: int, balance: Money) -> Money:
        """Calculate Required Minimum Distribution"""
        if age < 72:
            return Money(Decimal('0'))
        
        # Simplified RMD calculation
        rmd_divisors = {
            72: Decimal('27.4'),
            73: Decimal('26.5'),
            74: Decimal('25.5'),
            75: Decimal('24.6'),
            80: Decimal('20.2'),
            85: Decimal('16.0'),
            90: Decimal('12.2'),
            95: Decimal('9.5')
        }
        
        divisor = Decimal('25.0')  # default
        for rmd_age, div in rmd_divisors.items():
            if age <= rmd_age:
                divisor = div
                break
        
        return balance.divide(divisor)
    
    def deposit(self, amount: Money) -> None:
        """Deposit to IRA"""
        self.balance = self.balance.add(amount)
    
    def apply_returns(self, year: int) -> Money:
        """Apply investment returns (tax-deferred growth)"""
        import random
        
        # Calculate returns for stock portion
        stock_value = self.balance.multiply(self.stock_allocation)
        stock_return = Decimal(str(random.gauss(
            float(self.stock_return),
            float(self.stock_volatility)
        )))
        stock_growth = stock_value.multiply(stock_return)
        
        # Calculate returns for cash portion
        cash_value = self.balance.multiply(self.cash_allocation)
        cash_growth = cash_value.multiply(self.cash_return)
        
        # Total return (tax-deferred)
        total_return = stock_growth.add(cash_growth)
        self.balance = self.balance.add(total_return)
        
        return total_return


@dataclass
class PrivateStockAccount(Account):
    """
    Private stock account (RSUs, private equity, vesting stock options)
    Cannot be withdrawn until conversion date, then becomes liquid like taxable account
    """
    
    stock_allocation: Decimal = Decimal('1.0')  # Usually 100% stock
    stock_return: Decimal = Decimal('0.10')
    stock_volatility: Decimal = Decimal('0.20')
    dividend_yield: Decimal = Decimal('0.0')  # Private stock usually no dividends
    capital_gains_tax_rate: Decimal = Decimal('0.15')
    conversion_year: int = 5  # Years from portfolio start when stock becomes liquid
    
    def __init__(
        self,
        account_id: str,
        balance: Money,
        conversion_year: int,
        stock_allocation: Decimal = Decimal('1.0'),
        name: Optional[str] = None
    ):
        super().__init__(account_id, AccountType.PRIVATE_STOCK, balance, name)
        self.stock_allocation = stock_allocation
        self.cash_allocation = Decimal('1') - stock_allocation
        self.cash_return = Decimal('0.02')
        self.conversion_year = conversion_year
        self.is_converted = False
        self.original_balance = balance  # Track for tax basis
    
    def is_liquid(self, year: int) -> bool:
        """Check if stock has converted to liquid form"""
        return year >= self.conversion_year
    
    def convert_to_liquid(self) -> None:
        """Mark the stock as converted to liquid"""
        self.is_converted = True
    
    def withdraw(self, amount: Money, age: int = 65, year: int = 0) -> Tuple[Money, Money]:
        """
        Withdraw from private stock account
        Can only withdraw after conversion date
        """
        # Cannot withdraw before conversion
        if not self.is_liquid(year):
            return Money(Decimal('0')), Money(Decimal('0'))
        
        # Store balance before withdrawal for tax calculation
        balance_before = self.balance
        
        # After conversion, behaves like taxable account
        if amount.amount > self.balance.amount:
            actual_withdrawal = self.balance
            self.balance = Money(Decimal('0'))
        else:
            actual_withdrawal = amount
            self.balance = self.balance.subtract(amount)
        
        # Calculate capital gains tax (simplified)
        # Assume all gains are long-term after conversion
        if balance_before.amount > 0 and self.original_balance.amount > 0:
            # Calculate the gain ratio based on balance before withdrawal
            if balance_before.amount > self.original_balance.amount:
                # We have gains
                gain_ratio = (balance_before.amount - self.original_balance.amount) / balance_before.amount
                taxable_gains = actual_withdrawal.multiply(gain_ratio)
                tax_owed = taxable_gains.multiply(self.capital_gains_tax_rate)
            else:
                # No gains, no tax
                tax_owed = Money(Decimal('0'))
        elif actual_withdrawal.amount > 0:
            # Conservative: if we can't determine basis, tax the entire withdrawal
            tax_owed = actual_withdrawal.multiply(self.capital_gains_tax_rate)
        else:
            tax_owed = Money(Decimal('0'))
        
        return actual_withdrawal, tax_owed
    
    def deposit(self, amount: Money) -> None:
        """Deposit to private stock account"""
        self.balance = self.balance.add(amount)
    
    def apply_returns(self, year: int) -> Money:
        """Apply investment returns"""
        import random
        
        # Private stock may have higher volatility
        stock_value = self.balance.multiply(self.stock_allocation)
        stock_return = Decimal(str(random.gauss(
            float(self.stock_return),
            float(self.stock_volatility)
        )))
        stock_growth = stock_value.multiply(stock_return)
        
        # Cash portion (if any)
        cash_value = self.balance.multiply(self.cash_allocation)
        cash_growth = cash_value.multiply(self.cash_return)
        
        # Total return
        total_return = stock_growth.add(cash_growth)
        self.balance = self.balance.add(total_return)
        
        # Mark as converted if we've reached conversion year
        if not self.is_converted and self.is_liquid(year):
            self.convert_to_liquid()
        
        return total_return
    
    def get_balance(self) -> Money:
        """Get current balance"""
        return self.balance


@dataclass
class InheritanceAccount(Account):
    """
    Inheritance account representing expected future inheritance
    Cannot be accessed until inheritance year (when benefactor passes)
    No inheritance tax assumed (under estate tax exemption)
    """
    
    inheritance_year: int  # Years from portfolio start when inheritance is received
    asset_allocation: Decimal = Decimal('0.60')  # Mix of stocks/bonds/cash
    growth_rate: Decimal = Decimal('0.06')  # Expected growth rate (conservative)
    volatility: Decimal = Decimal('0.12')  # Lower volatility (conservative portfolio)
    is_step_up_basis: bool = True  # Step-up in basis at inheritance (no capital gains)
    
    def __init__(
        self,
        account_id: str,
        expected_amount: Money,
        inheritance_year: int,
        asset_allocation: Decimal = Decimal('0.60'),
        growth_rate: Decimal = Decimal('0.06'),
        volatility: Decimal = Decimal('0.12'),
        is_step_up_basis: bool = True,
        name: Optional[str] = None
    ):
        super().__init__(account_id, AccountType.INHERITANCE, expected_amount, name)
        self.inheritance_year = inheritance_year
        self.asset_allocation = asset_allocation
        self.cash_allocation = Decimal('1') - asset_allocation
        self.cash_return = Decimal('0.02')
        self.growth_rate = growth_rate
        self.volatility = volatility
        self.is_step_up_basis = is_step_up_basis
        self.is_received = False
        self.original_amount = expected_amount
    
    def is_available(self, year: int) -> bool:
        """Check if inheritance has been received"""
        return year >= self.inheritance_year
    
    def receive_inheritance(self) -> None:
        """Mark the inheritance as received"""
        self.is_received = True
        # With step-up basis, the new cost basis is the current value
        if self.is_step_up_basis:
            self.original_amount = self.balance
    
    def withdraw(self, amount: Money, age: int = 65, year: int = 0) -> Tuple[Money, Money]:
        """
        Withdraw from inheritance account
        Can only withdraw after inheritance is received
        """
        # Cannot withdraw before inheritance
        if not self.is_available(year):
            return Money(Decimal('0')), Money(Decimal('0'))
        
        # Store balance before withdrawal
        balance_before = self.balance
        
        # Process withdrawal
        if amount.amount > self.balance.amount:
            actual_withdrawal = self.balance
            self.balance = Money(Decimal('0'))
        else:
            actual_withdrawal = amount
            self.balance = self.balance.subtract(amount)
        
        # Calculate taxes
        if self.is_step_up_basis:
            # With step-up basis, only gains since inheritance are taxable
            if balance_before.amount > self.original_amount.amount:
                gain_ratio = (balance_before.amount - self.original_amount.amount) / balance_before.amount
                taxable_gains = actual_withdrawal.multiply(gain_ratio)
                # Long-term capital gains rate on post-inheritance gains
                tax_owed = taxable_gains.multiply(Decimal('0.15'))
            else:
                tax_owed = Money(Decimal('0'))
        else:
            # Without step-up basis (rare), gains from original basis are taxable
            # This would apply to inherited IRAs or similar
            if balance_before.amount > 0:
                tax_owed = actual_withdrawal.multiply(Decimal('0.15'))
            else:
                tax_owed = Money(Decimal('0'))
        
        return actual_withdrawal, tax_owed
    
    def deposit(self, amount: Money) -> None:
        """Deposit to inheritance account (typically not used)"""
        self.balance = self.balance.add(amount)
    
    def apply_returns(self, year: int) -> Money:
        """Apply investment returns (inheritance continues to grow until received)"""
        import random
        
        # Calculate blended return based on asset allocation
        # Stock portion uses growth_rate and volatility
        stock_value = self.balance.multiply(self.asset_allocation)
        stock_return = Decimal(str(random.gauss(
            float(self.growth_rate),
            float(self.volatility)
        )))
        stock_growth = stock_value.multiply(stock_return)
        
        # Cash/bond portion with stable return
        cash_value = self.balance.multiply(self.cash_allocation)
        cash_growth = cash_value.multiply(self.cash_return)
        
        # Total return
        total_return = stock_growth.add(cash_growth)
        self.balance = self.balance.add(total_return)
        
        # Mark as received if we've reached inheritance year
        if not self.is_received and self.is_available(year):
            self.receive_inheritance()
        
        return total_return
    
    def get_balance(self) -> Money:
        """Get current expected/actual balance"""
        return self.balance


@dataclass
class Mortgage(Account):
    """Mortgage liability"""
    
    original_balance: Money
    interest_rate: Decimal
    remaining_years: int
    monthly_payment: Money
    
    def __init__(
        self,
        account_id: str,
        balance: Money,  # Current balance (negative for liability)
        original_balance: Money,
        interest_rate: Decimal,
        remaining_years: int,
        name: Optional[str] = None
    ):
        # Store as negative balance since it's a liability
        if balance.amount > 0:
            balance = Money(-balance.amount)
        super().__init__(account_id, AccountType.MORTGAGE, balance, name)
        self.original_balance = original_balance
        self.interest_rate = interest_rate
        self.remaining_years = remaining_years
        self.monthly_payment = self._calculate_monthly_payment()
    
    def _calculate_monthly_payment(self) -> Money:
        """Calculate monthly payment using amortization formula"""
        if self.remaining_years <= 0:
            return Money(Decimal('0'))
        
        P = abs(self.balance.amount)  # Principal (positive value)
        r = self.interest_rate / Decimal('12')  # Monthly rate
        n = self.remaining_years * 12  # Total months
        
        if r == 0:
            payment = P / n
        else:
            payment = P * (r * (Decimal('1') + r) ** n) / ((Decimal('1') + r) ** n - Decimal('1'))
        
        return Money(payment)
    
    def withdraw(self, amount: Money, age: int = 65) -> Tuple[Money, Money]:
        """Make payment on mortgage (withdraw is actually a payment here)"""
        # For mortgage, withdrawal means making a payment (reducing liability)
        payment = min(amount.amount, abs(self.balance.amount))
        self.balance = self.balance.add(Money(payment))  # Reduce negative balance
        
        if self.balance.amount >= 0:
            self.balance = Money(Decimal('0'))
            self.remaining_years = 0
        
        return Money(payment), Money(Decimal('0'))  # No tax on mortgage payments
    
    def deposit(self, amount: Money) -> None:
        """Make extra payment on mortgage"""
        self.withdraw(amount)
    
    def apply_returns(self, year: int) -> Money:
        """Apply interest (increases liability if not paid)"""
        if self.balance.amount >= 0:  # Mortgage paid off
            return Money(Decimal('0'))
        
        # Calculate annual interest on remaining balance
        interest = Money(abs(self.balance.amount)).multiply(self.interest_rate)
        
        # Make annual payment (12 monthly payments)
        annual_payment = self.monthly_payment.multiply(Decimal('12'))
        
        # Apply payment to balance
        if annual_payment.amount > abs(self.balance.amount):
            self.balance = Money(Decimal('0'))
            self.remaining_years = 0
        else:
            # Reduce principal
            principal_reduction = annual_payment.subtract(interest)
            self.balance = self.balance.add(principal_reduction)
            self.remaining_years = max(0, self.remaining_years - 1)
        
        return Money(-interest.amount)  # Return negative for interest paid
    
    def get_annual_payment(self) -> Money:
        """Get total annual payment"""
        return self.monthly_payment.multiply(Decimal('12'))
    
    def is_paid_off(self) -> bool:
        """Check if mortgage is paid off"""
        return self.balance.amount >= 0 or self.remaining_years <= 0


class IncomeAccount(Account):
    """
    Income account representing regular income streams (salary, pension, social security, etc.)
    Income is automatically deposited based on start year and duration
    """
    
    def __init__(
        self,
        account_id: str,
        annual_income: Money,
        start_year: int,  # Years from current age when income starts
        duration_years: int,  # How many years income continues
        annual_adjustment: Decimal = Decimal('0'),  # Annual increase/decrease rate
        tax_rate: Decimal = Decimal('0.22'),  # Tax rate on income
        name: Optional[str] = None
    ):
        # Start with zero balance - income will be added during simulation
        super().__init__(account_id, AccountType.INCOME, Money(Decimal('0')), name)
        self.annual_income = annual_income
        self.start_year = start_year
        self.duration_years = duration_years
        self.annual_adjustment = annual_adjustment
        self.tax_rate = tax_rate
        self.years_active = 0  # Track how many years income has been active
        self.original_income = annual_income
    
    def is_active(self, year: int) -> bool:
        """Check if income is active in given year (0-indexed)"""
        return self.start_year <= year < (self.start_year + self.duration_years)
    
    def get_annual_income(self, year: int) -> Tuple[Money, Money]:
        """
        Get income for the year
        Returns: (gross_income, after_tax_income)
        """
        if not self.is_active(year):
            return Money(Decimal('0')), Money(Decimal('0'))
        
        # Calculate years since income started
        years_since_start = year - self.start_year
        
        # Apply annual adjustments
        adjustment_factor = (Decimal('1') + self.annual_adjustment) ** years_since_start
        adjusted_income = Money(self.original_income.amount * adjustment_factor)
        
        # Calculate taxes
        taxes = adjusted_income.multiply(self.tax_rate)
        after_tax = adjusted_income.subtract(taxes)
        
        return adjusted_income, after_tax
    
    def withdraw(self, amount: Money, age: int = 65) -> Tuple[Money, Money]:
        """
        Income accounts don't support withdrawals - income is automatic
        Returns zero withdrawal
        """
        return Money(Decimal('0')), Money(Decimal('0'))
    
    def deposit(self, amount: Money) -> None:
        """Income accounts track income separately, balance stays at 0"""
        # Income is handled through get_annual_income, not deposits
        pass
    
    def apply_returns(self, year: int) -> Money:
        """
        Apply income for the year (if active)
        Returns the after-tax income amount
        """
        gross, after_tax = self.get_annual_income(year)
        if after_tax.amount > 0:
            # Track that income was received but don't change balance
            # The income will be added to other accounts during simulation
            self.years_active += 1
        return after_tax
    
    def get_balance(self) -> Money:
        """Income accounts always show zero balance"""
        return Money(Decimal('0'))
    
    def get_remaining_income(self, current_year: int) -> Money:
        """Calculate total remaining income (pre-tax)"""
        if current_year >= self.start_year + self.duration_years:
            return Money(Decimal('0'))
        
        total = Decimal('0')
        for year in range(max(current_year, self.start_year), self.start_year + self.duration_years):
            gross, _ = self.get_annual_income(year)
            total += gross.amount
        
        return Money(total)