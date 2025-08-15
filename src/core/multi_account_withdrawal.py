"""Withdrawal strategies for multi-account portfolios"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from .base import Strategy
from .money import Money
from .multi_account_portfolio import MultiAccountPortfolio, WithdrawalOrder


class MultiAccountWithdrawalStrategy(Strategy):
    """Base withdrawal strategy for multi-account portfolios"""
    
    def execute(self, *args, **kwargs) -> Money:
        return self.calculate_withdrawal(*args, **kwargs)
    
    def calculate_withdrawal(
        self,
        portfolio: MultiAccountPortfolio,
        year: int,
        previous_withdrawal: Optional[Money] = None
    ) -> Money:
        """Calculate withdrawal amount for the year"""
        raise NotImplementedError


@dataclass
class MultiAccountFixedWithdrawal(MultiAccountWithdrawalStrategy):
    """Fixed withdrawal with inflation adjustment from multiple accounts"""
    
    initial_withdrawal: Money
    inflation_rate: Optional[Decimal] = None  # If None, use portfolio's inflation rate
    pay_mortgage_first: bool = True
    withdrawal_order: WithdrawalOrder = WithdrawalOrder.TAX_EFFICIENT
    
    def calculate_withdrawal(
        self,
        portfolio: MultiAccountPortfolio,
        year: int,
        previous_withdrawal: Optional[Money] = None
    ) -> Money:
        """Calculate withdrawal for living expenses (after mortgage)"""
        
        # Use portfolio inflation if not specified
        inflation = self.inflation_rate if self.inflation_rate is not None else portfolio.inflation_rate
        
        # Calculate base withdrawal with inflation adjustment
        if year == 0:
            base_withdrawal = self.initial_withdrawal
        else:
            inflation_multiplier = (Decimal('1') + inflation) ** year
            base_withdrawal = self.initial_withdrawal.multiply(inflation_multiplier)
        
        # Set withdrawal order
        portfolio.withdrawal_order = self.withdrawal_order
        
        # If paying mortgage first, that's handled separately in simulation
        # This returns the amount needed for living expenses
        return base_withdrawal


@dataclass
class MultiAccountPercentageWithdrawal(MultiAccountWithdrawalStrategy):
    """Percentage-based withdrawal from total portfolio value"""
    
    withdrawal_rate: Decimal  # As percentage (e.g., 4.0 for 4%)
    min_withdrawal: Optional[Money] = None
    max_withdrawal: Optional[Money] = None
    withdrawal_order: WithdrawalOrder = WithdrawalOrder.TAX_EFFICIENT
    
    def calculate_withdrawal(
        self,
        portfolio: MultiAccountPortfolio,
        year: int,
        previous_withdrawal: Optional[Money] = None
    ) -> Money:
        """Calculate withdrawal as percentage of total assets"""
        
        # Calculate withdrawal based on total portfolio value
        total_assets = portfolio.get_total_assets()
        withdrawal = total_assets.multiply(self.withdrawal_rate / Decimal('100'))
        
        # Apply min/max constraints
        if self.min_withdrawal and withdrawal.amount < self.min_withdrawal.amount:
            withdrawal = self.min_withdrawal
        if self.max_withdrawal and withdrawal.amount > self.max_withdrawal.amount:
            withdrawal = self.max_withdrawal
        
        # Set withdrawal order
        portfolio.withdrawal_order = self.withdrawal_order
        
        return withdrawal


@dataclass
class MultiAccountDynamicWithdrawal(MultiAccountWithdrawalStrategy):
    """Dynamic withdrawal based on portfolio performance"""
    
    base_withdrawal: Money
    min_rate: Decimal = Decimal('3.0')  # Minimum 3%
    max_rate: Decimal = Decimal('6.0')  # Maximum 6%
    target_balance_multiple: Decimal = Decimal('25')  # Target 25x annual expenses
    adjustment_factor: Decimal = Decimal('0.1')
    withdrawal_order: WithdrawalOrder = WithdrawalOrder.TAX_EFFICIENT
    
    def calculate_withdrawal(
        self,
        portfolio: MultiAccountPortfolio,
        year: int,
        previous_withdrawal: Optional[Money] = None
    ) -> Money:
        """Dynamically adjust withdrawal based on portfolio health"""
        
        total_assets = portfolio.get_total_assets()
        
        if year == 0 or previous_withdrawal is None:
            withdrawal = self.base_withdrawal
        else:
            # Check portfolio health
            target_balance = self.base_withdrawal.multiply(self.target_balance_multiple)
            
            if total_assets.amount > target_balance.amount * Decimal('1.2'):
                # Portfolio doing well, can increase withdrawal
                increase = self.base_withdrawal.multiply(self.adjustment_factor)
                withdrawal = previous_withdrawal.add(increase)
                
                # Check against max rate
                max_withdrawal = total_assets.multiply(self.max_rate / Decimal('100'))
                if withdrawal.amount > max_withdrawal.amount:
                    withdrawal = max_withdrawal
            
            elif total_assets.amount < target_balance.amount * Decimal('0.8'):
                # Portfolio struggling, decrease withdrawal
                decrease = self.base_withdrawal.multiply(self.adjustment_factor)
                withdrawal = previous_withdrawal.subtract(decrease)
                
                # Check against min rate
                min_withdrawal = total_assets.multiply(self.min_rate / Decimal('100'))
                if withdrawal.amount < min_withdrawal.amount:
                    withdrawal = min_withdrawal
            
            else:
                # Portfolio on track, adjust for inflation
                withdrawal = previous_withdrawal.multiply(Decimal('1.03'))
        
        # Set withdrawal order
        portfolio.withdrawal_order = self.withdrawal_order
        
        return withdrawal


@dataclass
class MultiAccountBucketWithdrawal(MultiAccountWithdrawalStrategy):
    """Bucket strategy using different account types"""
    
    annual_expenses: Money
    years_in_cash: int = 2  # Keep 2 years expenses in cash
    years_in_taxable: int = 5  # Next 5 years in taxable
    # Remainder in IRA for long-term growth
    
    rebalance_annually: bool = True
    withdrawal_order: WithdrawalOrder = WithdrawalOrder.TRADITIONAL
    
    def calculate_withdrawal(
        self,
        portfolio: MultiAccountPortfolio,
        year: int,
        previous_withdrawal: Optional[Money] = None
    ) -> Money:
        """Implement bucket strategy across accounts"""
        
        # Base withdrawal is annual expenses with inflation
        withdrawal = self.annual_expenses.multiply(
            (Decimal('1.03') ** year)  # 3% inflation
        )
        
        if self.rebalance_annually and year > 0:
            self._rebalance_buckets(portfolio)
        
        # Set withdrawal order (bucket strategy typically uses traditional order)
        portfolio.withdrawal_order = self.withdrawal_order
        
        return withdrawal
    
    def _rebalance_buckets(self, portfolio: MultiAccountPortfolio) -> None:
        """Rebalance money between buckets"""
        # This is simplified - in reality would move money between accounts
        # to maintain target bucket allocations
        pass