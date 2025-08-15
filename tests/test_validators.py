"""Unit tests for input validators"""

import unittest
from decimal import Decimal
import sys
sys.path.append('../src')
from core.validators import RetirementValidator, ValidationError


class TestRetirementValidator(unittest.TestCase):
    """Test input validation functionality"""
    
    def test_validate_decimal_valid(self):
        """Test valid decimal conversion"""
        result = RetirementValidator.validate_decimal('100.5', 'test_field')
        self.assertEqual(result, Decimal('100.5'))
        
        result = RetirementValidator.validate_decimal(100, 'test_field')
        self.assertEqual(result, Decimal('100'))
    
    def test_validate_decimal_invalid(self):
        """Test invalid decimal inputs"""
        with self.assertRaises(ValidationError) as context:
            RetirementValidator.validate_decimal('not_a_number', 'test_field')
        self.assertIn('Must be a valid number', str(context.exception))
    
    def test_validate_decimal_bounds(self):
        """Test decimal bounds checking"""
        # Within bounds
        result = RetirementValidator.validate_decimal('50', 'test_field', 
                                                     Decimal('0'), Decimal('100'))
        self.assertEqual(result, Decimal('50'))
        
        # Below minimum
        with self.assertRaises(ValidationError) as context:
            RetirementValidator.validate_decimal('-10', 'test_field', 
                                                Decimal('0'), Decimal('100'))
        self.assertIn('Must be >= 0', str(context.exception))
        
        # Above maximum
        with self.assertRaises(ValidationError) as context:
            RetirementValidator.validate_decimal('150', 'test_field', 
                                                Decimal('0'), Decimal('100'))
        self.assertIn('Must be <= 100', str(context.exception))
    
    def test_validate_percentage(self):
        """Test percentage validation (0-1 range)"""
        # Valid percentages
        result = RetirementValidator.validate_percentage('0.5', 'allocation')
        self.assertEqual(result, Decimal('0.5'))
        
        result = RetirementValidator.validate_percentage('0', 'allocation')
        self.assertEqual(result, Decimal('0'))
        
        result = RetirementValidator.validate_percentage('1', 'allocation')
        self.assertEqual(result, Decimal('1'))
        
        # Invalid percentages
        with self.assertRaises(ValidationError):
            RetirementValidator.validate_percentage('1.5', 'allocation')
        
        with self.assertRaises(ValidationError):
            RetirementValidator.validate_percentage('-0.1', 'allocation')
    
    def test_validate_age(self):
        """Test age validation"""
        # Valid ages
        result = RetirementValidator.validate_age(65)
        self.assertEqual(result, 65)
        
        result = RetirementValidator.validate_age('30')
        self.assertEqual(result, 30)
        
        # Invalid ages
        with self.assertRaises(ValidationError) as context:
            RetirementValidator.validate_age(15)
        self.assertIn('Must be between 18 and 120', str(context.exception))
        
        with self.assertRaises(ValidationError) as context:
            RetirementValidator.validate_age(150)
        self.assertIn('Must be between 18 and 120', str(context.exception))
        
        with self.assertRaises(ValidationError) as context:
            RetirementValidator.validate_age('not_an_age')
        self.assertIn('Must be a valid integer', str(context.exception))
    
    def test_validate_years(self):
        """Test years validation"""
        # Valid years
        result = RetirementValidator.validate_years(30)
        self.assertEqual(result, 30)
        
        result = RetirementValidator.validate_years('25')
        self.assertEqual(result, 25)
        
        # Invalid years
        with self.assertRaises(ValidationError) as context:
            RetirementValidator.validate_years(0)
        self.assertIn('Must be between 1 and 100', str(context.exception))
        
        with self.assertRaises(ValidationError) as context:
            RetirementValidator.validate_years(150)
        self.assertIn('Must be between 1 and 100', str(context.exception))
    
    def test_validate_portfolio_inputs(self):
        """Test portfolio input validation"""
        # Valid inputs
        result = RetirementValidator.validate_portfolio_inputs(
            balance='100000',
            stock_allocation='0.7',
            stock_return='0.08',
            stock_volatility='0.15'
        )
        
        self.assertEqual(result['balance'], Decimal('100000'))
        self.assertEqual(result['stock_allocation'], Decimal('0.7'))
        self.assertEqual(result['stock_return'], Decimal('0.08'))
        self.assertEqual(result['stock_volatility'], Decimal('0.15'))
        
        # Invalid balance (negative)
        with self.assertRaises(ValidationError):
            RetirementValidator.validate_portfolio_inputs(
                balance='-1000',
                stock_allocation='0.7',
                stock_return='0.08',
                stock_volatility='0.15'
            )
        
        # Invalid allocation (> 1)
        with self.assertRaises(ValidationError):
            RetirementValidator.validate_portfolio_inputs(
                balance='100000',
                stock_allocation='1.5',
                stock_return='0.08',
                stock_volatility='0.15'
            )
        
        # Invalid return (too extreme)
        with self.assertRaises(ValidationError):
            RetirementValidator.validate_portfolio_inputs(
                balance='100000',
                stock_allocation='0.7',
                stock_return='0.75',  # 75% return too high
                stock_volatility='0.15'
            )
        
        # Invalid volatility (negative)
        with self.assertRaises(ValidationError):
            RetirementValidator.validate_portfolio_inputs(
                balance='100000',
                stock_allocation='0.7',
                stock_return='0.08',
                stock_volatility='-0.15'
            )
    
    def test_validation_error_message(self):
        """Test ValidationError message formatting"""
        error = ValidationError('test_field', 123, 'Value is invalid')
        self.assertEqual(str(error), 
                        'Validation error for test_field: Value is invalid (value: 123)')


if __name__ == '__main__':
    unittest.main()