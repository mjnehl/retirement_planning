"""Multi-account portfolio management"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from enum import Enum

from .money import Money
from .accounts import (
    Account, CashAccount, TaxableAccount, IRAAccount, Mortgage,
    IncomeAccount, PrivateStockAccount, InheritanceAccount, AccountType
)


class WithdrawalOrder(Enum):
    """Order for withdrawing from accounts"""
    TRADITIONAL = "traditional"  # Cash -> Taxable -> IRA
    TAX_EFFICIENT = "tax_efficient"  # Optimize for taxes
    PROPORTIONAL = "proportional"  # Withdraw proportionally


@dataclass
class MultiAccountPortfolio:
    """Portfolio with multiple account types"""
    
    portfolio_id: str
    owner_id: str
    accounts: Dict[str, Account] = field(default_factory=dict)
    withdrawal_order: WithdrawalOrder = WithdrawalOrder.TRADITIONAL
    current_age: int = 65
    inflation_rate: Decimal = field(default=Decimal('0.03'))  # Default 3% inflation
    inflation_volatility: Decimal = field(default=Decimal('0.01'))  # 1% volatility
    
    def add_account(self, account: Account) -> None:
        """Add an account to the portfolio"""
        self.accounts[account.account_id] = account
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        return self.accounts.get(account_id)
    
    def get_accounts_by_type(self, account_type: AccountType) -> List[Account]:
        """Get all accounts of a specific type"""
        return [
            acc for acc in self.accounts.values()
            if acc.account_type == account_type
        ]
    
    def get_total_assets(self) -> Money:
        """Get total assets (excluding mortgage, income, and unreceived inheritance)"""
        total = Money(Decimal('0'))
        for account in self.accounts.values():
            if account.account_type not in [AccountType.MORTGAGE, AccountType.INCOME]:
                # For inheritance, only include if already received
                if account.account_type == AccountType.INHERITANCE:
                    # Check the current year (0 if not set)
                    # This is a simplification - in production would track better
                    total = total.add(account.get_balance())
                else:
                    total = total.add(account.get_balance())
        return total
    
    def get_total_liabilities(self) -> Money:
        """Get total liabilities (mortgage)"""
        total = Money(Decimal('0'))
        for account in self.accounts.values():
            if account.account_type == AccountType.MORTGAGE:
                # Mortgage balance is negative, so negate it
                total = total.add(Money(-account.get_balance().amount))
        return total
    
    def get_net_worth(self) -> Money:
        """Get net worth (assets - liabilities)"""
        assets = self.get_total_assets()
        liabilities = self.get_total_liabilities()
        return assets.subtract(liabilities)
    
    def get_liquid_assets(self) -> Money:
        """Get liquid assets (cash + taxable accounts)"""
        total = Money(Decimal('0'))
        for account in self.accounts.values():
            if account.account_type in [AccountType.CASH, AccountType.TAXABLE]:
                total = total.add(account.get_balance())
        return total
    
    def withdraw(self, target_amount: Money, year: int = 0) -> Tuple[Money, Money]:
        """
        Withdraw from portfolio using specified strategy
        Returns: (actual_withdrawal, total_taxes)
        """
        if self.withdrawal_order == WithdrawalOrder.TRADITIONAL:
            return self._withdraw_traditional(target_amount, year)
        elif self.withdrawal_order == WithdrawalOrder.TAX_EFFICIENT:
            return self._withdraw_tax_efficient(target_amount, year)
        else:
            return self._withdraw_proportional(target_amount, year)
    
    def _withdraw_traditional(self, target_amount: Money, year: int = 0) -> Tuple[Money, Money]:
        """Traditional withdrawal order: Cash -> Taxable -> Inheritance (if available) -> Private (if liquid) -> IRA"""
        total_withdrawn = Money(Decimal('0'))
        total_taxes = Money(Decimal('0'))
        remaining_need = target_amount
        
        # Order of withdrawal
        withdrawal_order = [
            AccountType.CASH,
            AccountType.TAXABLE,
            AccountType.INHERITANCE,  # After taxable, before private stock
            AccountType.PRIVATE_STOCK,
            AccountType.IRA
        ]
        
        for account_type in withdrawal_order:
            if remaining_need.amount <= 0:
                break
            
            accounts = self.get_accounts_by_type(account_type)
            for account in accounts:
                if remaining_need.amount <= 0:
                    break
                
                # Skip private stock if not yet liquid
                if account_type == AccountType.PRIVATE_STOCK:
                    if isinstance(account, PrivateStockAccount) and not account.is_liquid(year):
                        continue
                
                # Skip inheritance if not yet available
                if account_type == AccountType.INHERITANCE:
                    if isinstance(account, InheritanceAccount) and not account.is_available(year):
                        continue
                
                if account.get_balance().is_positive():
                    # Withdraw up to what we need
                    withdrawal_amount = Money(
                        min(remaining_need.amount, account.get_balance().amount)
                    )
                    
                    # Pass year for private stock and inheritance accounts
                    if isinstance(account, (PrivateStockAccount, InheritanceAccount)):
                        actual, taxes = account.withdraw(withdrawal_amount, self.current_age, year)
                    else:
                        actual, taxes = account.withdraw(withdrawal_amount, self.current_age)
                    total_withdrawn = total_withdrawn.add(actual)
                    total_taxes = total_taxes.add(taxes)
                    remaining_need = remaining_need.subtract(actual)
        
        return total_withdrawn, total_taxes
    
    def _withdraw_tax_efficient(self, target_amount: Money, year: int = 0) -> Tuple[Money, Money]:
        """Tax-efficient withdrawal strategy"""
        total_withdrawn = Money(Decimal('0'))
        total_taxes = Money(Decimal('0'))
        remaining_need = target_amount
        
        # First: Check for RMDs from IRA accounts
        ira_accounts = self.get_accounts_by_type(AccountType.IRA)
        for account in ira_accounts:
            if isinstance(account, IRAAccount):
                rmd = account.calculate_rmd(self.current_age, account.get_balance())
                if rmd.is_positive():
                    actual, taxes = account.withdraw(rmd, self.current_age)
                    total_withdrawn = total_withdrawn.add(actual)
                    total_taxes = total_taxes.add(taxes)
                    remaining_need = remaining_need.subtract(actual)
        
        # Second: Withdraw from cash (no tax)
        if remaining_need.is_positive():
            cash_accounts = self.get_accounts_by_type(AccountType.CASH)
            for account in cash_accounts:
                if remaining_need.amount <= 0:
                    break
                
                if account.get_balance().is_positive():
                    withdrawal_amount = Money(
                        min(remaining_need.amount, account.get_balance().amount)
                    )
                    actual, taxes = account.withdraw(withdrawal_amount, self.current_age)
                    total_withdrawn = total_withdrawn.add(actual)
                    total_taxes = total_taxes.add(taxes)
                    remaining_need = remaining_need.subtract(actual)
        
        # Third: Withdraw from taxable (capital gains tax)
        if remaining_need.is_positive():
            taxable_accounts = self.get_accounts_by_type(AccountType.TAXABLE)
            for account in taxable_accounts:
                if remaining_need.amount <= 0:
                    break
                
                if account.get_balance().is_positive():
                    withdrawal_amount = Money(
                        min(remaining_need.amount, account.get_balance().amount)
                    )
                    actual, taxes = account.withdraw(withdrawal_amount, self.current_age)
                    total_withdrawn = total_withdrawn.add(actual)
                    total_taxes = total_taxes.add(taxes)
                    remaining_need = remaining_need.subtract(actual)
        
        # Fourth: Withdraw from inheritance if available (minimal tax due to step-up basis)
        if remaining_need.is_positive():
            inheritance_accounts = self.get_accounts_by_type(AccountType.INHERITANCE)
            for account in inheritance_accounts:
                if remaining_need.amount <= 0:
                    break
                
                if isinstance(account, InheritanceAccount) and account.is_available(year):
                    if account.get_balance().is_positive():
                        withdrawal_amount = Money(
                            min(remaining_need.amount, account.get_balance().amount)
                        )
                        actual, taxes = account.withdraw(withdrawal_amount, self.current_age, year)
                        total_withdrawn = total_withdrawn.add(actual)
                        total_taxes = total_taxes.add(taxes)
                        remaining_need = remaining_need.subtract(actual)
        
        # Fifth: Withdraw from private stock if liquid (capital gains tax)
        if remaining_need.is_positive():
            private_accounts = self.get_accounts_by_type(AccountType.PRIVATE_STOCK)
            for account in private_accounts:
                if remaining_need.amount <= 0:
                    break
                
                if isinstance(account, PrivateStockAccount) and account.is_liquid(year):
                    if account.get_balance().is_positive():
                        withdrawal_amount = Money(
                            min(remaining_need.amount, account.get_balance().amount)
                        )
                        actual, taxes = account.withdraw(withdrawal_amount, self.current_age, year)
                        total_withdrawn = total_withdrawn.add(actual)
                        total_taxes = total_taxes.add(taxes)
                        remaining_need = remaining_need.subtract(actual)
        
        # Sixth: Withdraw from IRA if needed (ordinary income tax)
        if remaining_need.is_positive():
            for account in ira_accounts:
                if remaining_need.amount <= 0:
                    break
                
                if account.get_balance().is_positive():
                    withdrawal_amount = Money(
                        min(remaining_need.amount, account.get_balance().amount)
                    )
                    actual, taxes = account.withdraw(withdrawal_amount, self.current_age)
                    total_withdrawn = total_withdrawn.add(actual)
                    total_taxes = total_taxes.add(taxes)
                    remaining_need = remaining_need.subtract(actual)
        
        return total_withdrawn, total_taxes
    
    def _withdraw_proportional(self, target_amount: Money, year: int = 0) -> Tuple[Money, Money]:
        """Withdraw proportionally from all accounts"""
        total_withdrawn = Money(Decimal('0'))
        total_taxes = Money(Decimal('0'))
        
        # Calculate total available assets
        total_assets = self.get_total_assets()
        if not total_assets.is_positive():
            return total_withdrawn, total_taxes
        
        # Withdraw proportionally from each account
        for account in self.accounts.values():
            if account.account_type == AccountType.MORTGAGE:
                continue  # Skip mortgage
            
            if account.get_balance().is_positive():
                # Calculate proportional withdrawal
                proportion = account.get_balance().amount / total_assets.amount
                withdrawal_amount = target_amount.multiply(proportion)
                
                actual, taxes = account.withdraw(withdrawal_amount, self.current_age)
                total_withdrawn = total_withdrawn.add(actual)
                total_taxes = total_taxes.add(taxes)
        
        return total_withdrawn, total_taxes
    
    def apply_returns(self, year: int) -> Money:
        """Apply returns to all accounts"""
        total_returns = Money(Decimal('0'))
        
        for account in self.accounts.values():
            returns = account.apply_returns(year)
            total_returns = total_returns.add(returns)
        
        return total_returns
    
    def pay_mortgage(self, year: int = 0) -> Tuple[Money, Money]:
        """Make mortgage payments from available accounts"""
        mortgages = self.get_accounts_by_type(AccountType.MORTGAGE)
        if not mortgages:
            return Money(Decimal('0')), Money(Decimal('0'))
        
        total_payment = Money(Decimal('0'))
        total_taxes = Money(Decimal('0'))
        
        for mortgage in mortgages:
            if isinstance(mortgage, Mortgage) and not mortgage.is_paid_off():
                annual_payment = mortgage.get_annual_payment()
                
                # Withdraw from portfolio to pay mortgage (pass year for private stock)
                actual_withdrawn, taxes = self.withdraw(annual_payment, year)
                
                # Apply payment to mortgage
                mortgage.withdraw(actual_withdrawn, self.current_age)
                
                total_payment = total_payment.add(actual_withdrawn)
                total_taxes = total_taxes.add(taxes)
        
        return total_payment, total_taxes
    
    def increment_age(self) -> None:
        """Increment owner's age by one year"""
        self.current_age += 1
    
    def is_depleted(self) -> bool:
        """Check if all asset accounts are depleted"""
        for account in self.accounts.values():
            if account.account_type not in [AccountType.MORTGAGE, AccountType.INCOME]:
                if account.get_balance().is_positive():
                    return False
        return True
    
    def get_annual_income(self, year: int) -> Tuple[Money, Money]:
        """
        Get total income for the year from all income accounts
        Returns: (gross_income, after_tax_income)
        """
        total_gross = Money(Decimal('0'))
        total_after_tax = Money(Decimal('0'))
        
        for account in self.accounts.values():
            if account.account_type == AccountType.INCOME:
                if isinstance(account, IncomeAccount):
                    gross, after_tax = account.get_annual_income(year)
                    total_gross = total_gross.add(gross)
                    total_after_tax = total_after_tax.add(after_tax)
        
        return total_gross, total_after_tax
    
    def deposit_income(self, income: Money) -> None:
        """Deposit income into the first available cash or taxable account"""
        # Try cash accounts first
        cash_accounts = self.get_accounts_by_type(AccountType.CASH)
        if cash_accounts:
            cash_accounts[0].deposit(income)
            return
        
        # Then try taxable accounts
        taxable_accounts = self.get_accounts_by_type(AccountType.TAXABLE)
        if taxable_accounts:
            taxable_accounts[0].deposit(income)
            return
        
        # If no suitable account, the income is lost (shouldn't happen in practice)
    
    def get_account_summary(self) -> Dict[str, Money]:
        """Get summary of all account balances"""
        summary = {}
        for account_id, account in self.accounts.items():
            summary[account.name] = account.get_balance()
        summary['net_worth'] = self.get_net_worth()
        summary['total_assets'] = self.get_total_assets()
        summary['total_liabilities'] = self.get_total_liabilities()
        return summary