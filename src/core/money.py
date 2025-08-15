"""Money value object"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Immutable money value object"""
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        return Money(self.amount * Decimal(str(factor)), self.currency)
    
    def divide(self, divisor: Decimal) -> 'Money':
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / Decimal(str(divisor)), self.currency)
    
    def is_positive(self) -> bool:
        return self.amount > 0
    
    def is_zero(self) -> bool:
        return self.amount == 0
    
    def __str__(self) -> str:
        return f"{self.currency} {self.amount:,.2f}"