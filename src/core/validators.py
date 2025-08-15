"""Input validation for retirement planning calculations"""

from decimal import Decimal
from typing import Any, Union, Optional
from dataclasses import dataclass

@dataclass
class ValidationError(Exception):
    """Custom exception for validation errors"""
    field: str
    value: Any
    message: str
    
    def __str__(self):
        return f"Validation error for {self.field}: {self.message} (value: {self.value})"


class RetirementValidator:
    """Validates inputs for retirement planning calculations"""
    
    @staticmethod
    def validate_decimal(value: Any, field_name: str, min_value: Optional[Decimal] = None, 
                        max_value: Optional[Decimal] = None) -> Decimal:
        """Validate and convert to Decimal with bounds checking"""
        try:
            decimal_value = Decimal(str(value))
        except (ValueError, TypeError, Exception):
            raise ValidationError(field_name, value, f"Must be a valid number")
        
        if min_value is not None and decimal_value < min_value:
            raise ValidationError(field_name, value, f"Must be >= {min_value}")
        
        if max_value is not None and decimal_value > max_value:
            raise ValidationError(field_name, value, f"Must be <= {max_value}")
        
        return decimal_value
    
    @staticmethod
    def validate_percentage(value: Any, field_name: str) -> Decimal:
        """Validate percentage (0-1 range)"""
        return RetirementValidator.validate_decimal(value, field_name, Decimal('0'), Decimal('1'))
    
    @staticmethod
    def validate_age(value: Any, field_name: str = "age") -> int:
        """Validate age (18-120 range)"""
        try:
            age = int(value)
        except (ValueError, TypeError):
            raise ValidationError(field_name, value, "Must be a valid integer")
        
        if age < 18 or age > 120:
            raise ValidationError(field_name, value, "Must be between 18 and 120")
        
        return age
    
    @staticmethod
    def validate_years(value: Any, field_name: str = "years") -> int:
        """Validate year duration (1-100 range)"""
        try:
            years = int(value)
        except (ValueError, TypeError):
            raise ValidationError(field_name, value, "Must be a valid integer")
        
        if years < 1 or years > 100:
            raise ValidationError(field_name, value, "Must be between 1 and 100")
        
        return years
    
    @staticmethod
    def validate_portfolio_inputs(balance: Any, stock_allocation: Any, 
                                 stock_return: Any, stock_volatility: Any) -> dict:
        """Validate portfolio inputs"""
        return {
            'balance': RetirementValidator.validate_decimal(balance, 'balance', Decimal('0')),
            'stock_allocation': RetirementValidator.validate_percentage(stock_allocation, 'stock_allocation'),
            'stock_return': RetirementValidator.validate_decimal(stock_return, 'stock_return', 
                                                                 Decimal('-0.5'), Decimal('0.5')),
            'stock_volatility': RetirementValidator.validate_decimal(stock_volatility, 'stock_volatility', 
                                                                    Decimal('0'), Decimal('1'))
        }