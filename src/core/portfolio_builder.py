"""Portfolio builder utilities for easy portfolio construction"""

from decimal import Decimal
from typing import Optional, Dict, Any

from .money import Money
from .accounts import (
    CashAccount, TaxableAccount, IRAAccount, Mortgage, IncomeAccount, 
    PrivateStockAccount, InheritanceAccount, Account
)
from .multi_account_portfolio import MultiAccountPortfolio, WithdrawalOrder


class PortfolioBuilder:
    """Builder class for creating portfolios with fluent interface"""
    
    def __init__(self, portfolio_id: str = "portfolio_001", owner_id: str = "owner_001"):
        self.portfolio = MultiAccountPortfolio(
            portfolio_id=portfolio_id,
            owner_id=owner_id,
            current_age=65,
            withdrawal_order=WithdrawalOrder.TAX_EFFICIENT
        )
        self._account_counter = 0
    
    def with_age(self, age: int) -> 'PortfolioBuilder':
        """Set the owner's current age"""
        self.portfolio.current_age = age
        return self
    
    def with_withdrawal_order(self, order: WithdrawalOrder) -> 'PortfolioBuilder':
        """Set the withdrawal order strategy"""
        self.portfolio.withdrawal_order = order
        return self
    
    def with_inflation(self, rate: Decimal, volatility: Decimal = Decimal('0.01')) -> 'PortfolioBuilder':
        """Set portfolio inflation parameters"""
        self.portfolio.inflation_rate = rate
        self.portfolio.inflation_volatility = volatility
        return self
    
    def add_cash_account(
        self, 
        balance: Decimal,
        annual_return: Decimal = Decimal('0.025'),
        name: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> 'PortfolioBuilder':
        """Add a cash/savings account"""
        if account_id is None:
            self._account_counter += 1
            account_id = f"cash_{self._account_counter:03d}"
        
        account = CashAccount(
            account_id=account_id,
            balance=Money(balance),
            annual_return=annual_return,
            name=name or "Cash Account"
        )
        self.portfolio.add_account(account)
        return self
    
    def add_taxable_account(
        self,
        balance: Decimal,
        stock_allocation: Decimal = Decimal('0.80'),
        stock_return: Optional[Decimal] = None,
        stock_volatility: Optional[Decimal] = None,
        dividend_yield: Optional[Decimal] = None,
        capital_gains_tax_rate: Optional[Decimal] = None,
        name: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> 'PortfolioBuilder':
        """Add a taxable investment account"""
        if account_id is None:
            self._account_counter += 1
            account_id = f"taxable_{self._account_counter:03d}"
        
        account = TaxableAccount(
            account_id=account_id,
            balance=Money(balance),
            stock_allocation=stock_allocation,
            name=name or "Taxable Account"
        )
        
        # Override optional parameters if provided
        if stock_return is not None:
            account.stock_return = stock_return
        if stock_volatility is not None:
            account.stock_volatility = stock_volatility
        if dividend_yield is not None:
            account.dividend_yield = dividend_yield
        if capital_gains_tax_rate is not None:
            account.capital_gains_tax_rate = capital_gains_tax_rate
        
        self.portfolio.add_account(account)
        return self
    
    def add_private_stock_account(
        self,
        balance: Decimal,
        conversion_year: int,  # Years from now when stock becomes liquid
        stock_allocation: Decimal = Decimal('1.0'),
        stock_return: Optional[Decimal] = None,
        stock_volatility: Optional[Decimal] = None,
        capital_gains_tax_rate: Optional[Decimal] = None,
        name: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> 'PortfolioBuilder':
        """Add a private stock account (RSUs, private equity, etc.)"""
        if account_id is None:
            self._account_counter += 1
            account_id = f"private_{self._account_counter:03d}"
        
        account = PrivateStockAccount(
            account_id=account_id,
            balance=Money(balance),
            conversion_year=conversion_year,
            stock_allocation=stock_allocation,
            name=name or "Private Stock"
        )
        
        # Override optional parameters if provided
        if stock_return is not None:
            account.stock_return = stock_return
        if stock_volatility is not None:
            account.stock_volatility = stock_volatility
        if capital_gains_tax_rate is not None:
            account.capital_gains_tax_rate = capital_gains_tax_rate
        
        self.portfolio.add_account(account)
        return self
    
    def add_ira_account(
        self,
        balance: Decimal,
        stock_allocation: Decimal = Decimal('0.70'),
        stock_return: Optional[Decimal] = None,
        stock_volatility: Optional[Decimal] = None,
        ordinary_income_tax_rate: Optional[Decimal] = None,
        early_withdrawal_penalty: Optional[Decimal] = None,
        name: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> 'PortfolioBuilder':
        """Add a traditional IRA account"""
        if account_id is None:
            self._account_counter += 1
            account_id = f"ira_{self._account_counter:03d}"
        
        account = IRAAccount(
            account_id=account_id,
            balance=Money(balance),
            stock_allocation=stock_allocation,
            name=name or "Traditional IRA"
        )
        
        # Override optional parameters if provided
        if stock_return is not None:
            account.stock_return = stock_return
        if stock_volatility is not None:
            account.stock_volatility = stock_volatility
        if ordinary_income_tax_rate is not None:
            account.ordinary_income_tax_rate = ordinary_income_tax_rate
        if early_withdrawal_penalty is not None:
            account.early_withdrawal_penalty = early_withdrawal_penalty
        
        self.portfolio.add_account(account)
        return self
    
    def add_mortgage(
        self,
        balance: Decimal,
        interest_rate: Decimal,
        remaining_years: int,
        name: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> 'PortfolioBuilder':
        """Add a mortgage liability"""
        if account_id is None:
            self._account_counter += 1
            account_id = f"mortgage_{self._account_counter:03d}"
        
        account = Mortgage(
            account_id=account_id,
            balance=Money(balance),
            original_balance=Money(balance),
            interest_rate=interest_rate,
            remaining_years=remaining_years,
            name=name or "Mortgage"
        )
        self.portfolio.add_account(account)
        return self
    
    def add_income_account(
        self,
        annual_income: Decimal,
        start_year: int,
        duration_years: int,
        annual_adjustment: Decimal = Decimal('0'),
        tax_rate: Decimal = Decimal('0.22'),
        name: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> 'PortfolioBuilder':
        """Add an income account (salary, pension, social security)"""
        if account_id is None:
            self._account_counter += 1
            account_id = f"income_{self._account_counter:03d}"
        
        account = IncomeAccount(
            account_id=account_id,
            annual_income=Money(annual_income),
            start_year=start_year,
            duration_years=duration_years,
            annual_adjustment=annual_adjustment,
            tax_rate=tax_rate,
            name=name or "Income Stream"
        )
        self.portfolio.add_account(account)
        return self
    
    def add_inheritance_account(
        self,
        expected_amount: Decimal,
        inheritance_year: int,  # Years from now when inheritance is expected
        asset_allocation: Decimal = Decimal('0.60'),  # Conservative mix
        growth_rate: Decimal = Decimal('0.06'),  # Expected growth rate
        volatility: Decimal = Decimal('0.12'),  # Growth volatility
        is_step_up_basis: bool = True,  # Step-up in basis at death (no capital gains)
        name: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> 'PortfolioBuilder':
        """Add an expected inheritance"""
        if account_id is None:
            self._account_counter += 1
            account_id = f"inheritance_{self._account_counter:03d}"
        
        account = InheritanceAccount(
            account_id=account_id,
            expected_amount=Money(expected_amount),
            inheritance_year=inheritance_year,
            asset_allocation=asset_allocation,
            growth_rate=growth_rate,
            volatility=volatility,
            is_step_up_basis=is_step_up_basis,
            name=name or "Expected Inheritance"
        )
        self.portfolio.add_account(account)
        return self
    
    def add_custom_account(self, account: Account) -> 'PortfolioBuilder':
        """Add a custom account directly"""
        self.portfolio.add_account(account)
        return self
    
    def build(self) -> MultiAccountPortfolio:
        """Build and return the portfolio"""
        return self.portfolio
    
    def summary(self) -> Dict[str, Any]:
        """Get a summary of the portfolio"""
        return {
            'total_assets': self.portfolio.get_total_assets(),
            'total_liabilities': self.portfolio.get_total_liabilities(),
            'net_worth': self.portfolio.get_net_worth(),
            'accounts': self.portfolio.get_account_summary(),
            'num_accounts': len(self.portfolio.accounts),
            'current_age': self.portfolio.current_age,
            'withdrawal_order': self.portfolio.withdrawal_order.value
        }


def create_simple_portfolio(
    balance: Decimal,
    mean_return: Decimal = Decimal('0.07'),
    volatility: Decimal = Decimal('0.18'),
    age: int = 65
) -> MultiAccountPortfolio:
    """Create a simple single-account portfolio"""
    return (PortfolioBuilder()
            .with_age(age)
            .with_withdrawal_order(WithdrawalOrder.TRADITIONAL)
            .add_taxable_account(
                balance=balance,
                stock_allocation=Decimal('1.0'),
                stock_return=mean_return,
                stock_volatility=volatility,
                capital_gains_tax_rate=Decimal('0'),  # No taxes for simple
                dividend_yield=Decimal('0'),
                name="Simple Portfolio"
            )
            .build())


def create_traditional_retirement_portfolio(
    cash: Decimal,
    taxable: Decimal,
    ira: Decimal,
    mortgage: Decimal = Decimal('0'),
    mortgage_rate: Decimal = Decimal('0.04'),
    mortgage_years: int = 15,
    age: int = 65
) -> MultiAccountPortfolio:
    """Create a traditional retirement portfolio with standard accounts"""
    builder = (PortfolioBuilder()
               .with_age(age)
               .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT))
    
    if cash > 0:
        builder.add_cash_account(cash, name="Emergency Fund")
    
    if taxable > 0:
        builder.add_taxable_account(
            taxable,
            stock_allocation=Decimal('0.80'),
            name="Brokerage Account"
        )
    
    if ira > 0:
        builder.add_ira_account(
            ira,
            stock_allocation=Decimal('0.70'),
            name="Traditional IRA"
        )
    
    if mortgage > 0:
        builder.add_mortgage(
            mortgage,
            mortgage_rate,
            mortgage_years,
            name="Home Mortgage"
        )
    
    return builder.build()


def create_conservative_portfolio(
    total_value: Decimal,
    age: int = 65
) -> MultiAccountPortfolio:
    """Create a conservative portfolio with high cash/bond allocation"""
    cash_portion = total_value * Decimal('0.20')  # 20% cash
    bond_heavy_portion = total_value * Decimal('0.50')  # 50% in bond-heavy account
    balanced_portion = total_value * Decimal('0.30')  # 30% balanced
    
    return (PortfolioBuilder()
            .with_age(age)
            .with_withdrawal_order(WithdrawalOrder.TAX_EFFICIENT)
            .add_cash_account(
                cash_portion,
                annual_return=Decimal('0.03'),
                name="Cash Reserve"
            )
            .add_taxable_account(
                bond_heavy_portion,
                stock_allocation=Decimal('0.30'),  # 30% stocks, 70% bonds
                stock_return=Decimal('0.08'),
                stock_volatility=Decimal('0.12'),
                name="Conservative Account"
            )
            .add_taxable_account(
                balanced_portion,
                stock_allocation=Decimal('0.50'),  # 50/50 balanced
                name="Balanced Account"
            )
            .build())


def create_aggressive_portfolio(
    total_value: Decimal,
    age: int = 65
) -> MultiAccountPortfolio:
    """Create an aggressive portfolio with high stock allocation"""
    cash_portion = total_value * Decimal('0.05')  # Only 5% cash
    aggressive_portion = total_value * Decimal('0.95')  # 95% in stocks
    
    return (PortfolioBuilder()
            .with_age(age)
            .with_withdrawal_order(WithdrawalOrder.TRADITIONAL)
            .add_cash_account(
                cash_portion,
                annual_return=Decimal('0.02'),
                name="Minimal Cash"
            )
            .add_taxable_account(
                aggressive_portion,
                stock_allocation=Decimal('0.95'),  # 95% stocks
                stock_return=Decimal('0.10'),
                stock_volatility=Decimal('0.22'),
                name="Growth Portfolio"
            )
            .build())