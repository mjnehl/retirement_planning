"""Inflation adjustment models for retirement planning"""

from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np


class InflationType(Enum):
    """Types of inflation models"""
    CONSTANT = "constant"
    VARIABLE = "variable"
    HISTORICAL = "historical"
    STOCHASTIC = "stochastic"


@dataclass
class InflationProjection:
    """Inflation projection results"""
    year: int
    rate: Decimal
    cumulative_factor: Decimal
    adjusted_value: Decimal
    confidence_interval: Optional[Tuple[Decimal, Decimal]] = None


class InflationModel:
    """Base class for inflation models"""
    
    # Historical CPI data (simplified)
    HISTORICAL_CPI = {
        2024: 310.3,
        2023: 304.7,
        2022: 296.8,
        2021: 273.7,
        2020: 260.3,
        2019: 256.9,
        2018: 252.1,
        2017: 246.8,
        2016: 241.4,
        2015: 238.6,
        2010: 219.2,
        2005: 196.8,
        2000: 174.0,
        1995: 153.5,
        1990: 131.6,
        1985: 108.4,
        1980: 86.3
    }
    
    # Category-specific inflation rates
    CATEGORY_RATES = {
        'healthcare': Decimal('0.045'),  # 4.5% - typically higher
        'education': Decimal('0.05'),    # 5.0% - typically higher
        'housing': Decimal('0.035'),     # 3.5% - moderate
        'food': Decimal('0.03'),         # 3.0% - close to general
        'energy': Decimal('0.04'),       # 4.0% - volatile
        'general': Decimal('0.03'),      # 3.0% - overall CPI
        'recreation': Decimal('0.025'),  # 2.5% - below average
        'apparel': Decimal('0.01')       # 1.0% - often deflationary
    }
    
    def __init__(self, base_rate: Decimal = Decimal('0.03')):
        """
        Initialize inflation model
        
        Args:
            base_rate: Base inflation rate (default 3%)
        """
        self.base_rate = base_rate
    
    def project_value(self,
                     initial_value: Decimal,
                     years: int,
                     category: str = 'general') -> List[InflationProjection]:
        """
        Project future values with inflation
        
        Args:
            initial_value: Starting value
            years: Number of years to project
            category: Spending category for specific inflation
        
        Returns:
            List of inflation projections by year
        """
        projections = []
        cumulative_factor = Decimal('1')
        current_value = initial_value
        
        for year in range(1, years + 1):
            # Get inflation rate for this year
            rate = self.get_inflation_rate(year, category)
            
            # Update cumulative factor
            cumulative_factor *= (Decimal('1') + rate)
            
            # Calculate adjusted value
            current_value = initial_value * cumulative_factor
            
            projections.append(InflationProjection(
                year=year,
                rate=rate,
                cumulative_factor=cumulative_factor,
                adjusted_value=current_value
            ))
        
        return projections
    
    def get_inflation_rate(self, year: int, category: str = 'general') -> Decimal:
        """
        Get inflation rate for a specific year and category
        Override in subclasses for different models
        """
        return self.CATEGORY_RATES.get(category, self.base_rate)
    
    def calculate_real_return(self,
                            nominal_return: Decimal,
                            inflation_rate: Optional[Decimal] = None) -> Decimal:
        """
        Calculate real return adjusted for inflation
        
        Args:
            nominal_return: Nominal (stated) return
            inflation_rate: Inflation rate (uses base_rate if not provided)
        
        Returns:
            Real return rate
        """
        if inflation_rate is None:
            inflation_rate = self.base_rate
        
        # Fisher equation: (1 + real) = (1 + nominal) / (1 + inflation)
        real_return = ((Decimal('1') + nominal_return) / 
                      (Decimal('1') + inflation_rate)) - Decimal('1')
        
        return real_return
    
    def calculate_purchasing_power(self,
                                  amount: Decimal,
                                  years: int,
                                  inflation_rate: Optional[Decimal] = None) -> Decimal:
        """
        Calculate future purchasing power of current dollars
        
        Args:
            amount: Current dollar amount
            years: Years in the future
            inflation_rate: Inflation rate (uses base_rate if not provided)
        
        Returns:
            Purchasing power in today's dollars
        """
        if inflation_rate is None:
            inflation_rate = self.base_rate
        
        # Discount by inflation
        purchasing_power = amount / ((Decimal('1') + inflation_rate) ** years)
        
        return purchasing_power.quantize(Decimal('0.01'))


class ConstantInflationModel(InflationModel):
    """Simple constant inflation rate model"""
    
    def get_inflation_rate(self, year: int, category: str = 'general') -> Decimal:
        """Return constant rate regardless of year"""
        return self.CATEGORY_RATES.get(category, self.base_rate)


class VariableInflationModel(InflationModel):
    """Variable inflation model with different phases"""
    
    def __init__(self, 
                phase_rates: List[Tuple[int, Decimal]],
                base_rate: Decimal = Decimal('0.03')):
        """
        Initialize variable inflation model
        
        Args:
            phase_rates: List of (year_threshold, rate) tuples
            base_rate: Default rate
        """
        super().__init__(base_rate)
        self.phase_rates = sorted(phase_rates, key=lambda x: x[0])
    
    def get_inflation_rate(self, year: int, category: str = 'general') -> Decimal:
        """Get rate based on year phase"""
        category_multiplier = self.CATEGORY_RATES.get(category, self.base_rate) / self.base_rate
        
        for year_threshold, rate in self.phase_rates:
            if year <= year_threshold:
                return rate * category_multiplier
        
        # Use last rate for years beyond phases
        if self.phase_rates:
            return self.phase_rates[-1][1] * category_multiplier
        
        return self.base_rate * category_multiplier


class HistoricalInflationModel(InflationModel):
    """Model based on historical CPI data"""
    
    def __init__(self, lookback_years: int = 10):
        """
        Initialize historical model
        
        Args:
            lookback_years: Years of history to use for projection
        """
        self.lookback_years = lookback_years
        super().__init__(self._calculate_historical_average())
    
    def _calculate_historical_average(self) -> Decimal:
        """Calculate average inflation from historical data"""
        years = sorted(self.HISTORICAL_CPI.keys(), reverse=True)
        
        if len(years) < 2:
            return Decimal('0.03')  # Default if insufficient data
        
        # Calculate year-over-year rates
        rates = []
        for i in range(min(self.lookback_years, len(years) - 1)):
            if i + 1 < len(years):
                current_cpi = self.HISTORICAL_CPI[years[i]]
                prev_cpi = self.HISTORICAL_CPI[years[i + 1]]
                rate = (current_cpi - prev_cpi) / prev_cpi
                rates.append(Decimal(str(rate)))
        
        if rates:
            return sum(rates) / len(rates)
        
        return Decimal('0.03')
    
    def get_inflation_rate(self, year: int, category: str = 'general') -> Decimal:
        """Get rate based on historical average"""
        category_multiplier = self.CATEGORY_RATES.get(category, self.base_rate) / Decimal('0.03')
        return self.base_rate * category_multiplier


class StochasticInflationModel(InflationModel):
    """Stochastic (random) inflation model with mean reversion"""
    
    def __init__(self,
                mean_rate: Decimal = Decimal('0.03'),
                volatility: Decimal = Decimal('0.01'),
                mean_reversion_speed: Decimal = Decimal('0.1'),
                random_seed: Optional[int] = None):
        """
        Initialize stochastic model
        
        Args:
            mean_rate: Long-term mean inflation rate
            volatility: Volatility of inflation
            mean_reversion_speed: Speed of reversion to mean
            random_seed: Random seed for reproducibility
        """
        super().__init__(mean_rate)
        self.mean_rate = mean_rate
        self.volatility = volatility
        self.mean_reversion_speed = mean_reversion_speed
        self.current_rate = mean_rate
        
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def get_inflation_rate(self, year: int, category: str = 'general') -> Decimal:
        """Generate stochastic inflation rate"""
        # Ornstein-Uhlenbeck process for mean reversion
        dt = 1  # Annual steps
        
        # Mean reversion term
        drift = self.mean_reversion_speed * (self.mean_rate - self.current_rate) * dt
        
        # Random shock
        shock = self.volatility * np.sqrt(dt) * np.random.normal()
        
        # Update rate
        self.current_rate = self.current_rate + drift + Decimal(str(shock))
        
        # Apply category adjustment
        category_multiplier = self.CATEGORY_RATES.get(category, self.base_rate) / Decimal('0.03')
        
        # Ensure non-negative
        return max(Decimal('0'), self.current_rate * category_multiplier)
    
    def simulate_paths(self,
                       years: int,
                       num_simulations: int = 1000,
                       category: str = 'general') -> Dict[str, any]:
        """
        Simulate multiple inflation paths
        
        Args:
            years: Number of years
            num_simulations: Number of simulation paths
            category: Spending category
        
        Returns:
            Dictionary with statistics
        """
        paths = np.zeros((num_simulations, years))
        
        for sim in range(num_simulations):
            self.current_rate = self.mean_rate  # Reset
            for year in range(years):
                rate = self.get_inflation_rate(year + 1, category)
                paths[sim, year] = float(rate)
        
        return {
            'mean_path': np.mean(paths, axis=0),
            'median_path': np.median(paths, axis=0),
            'std_path': np.std(paths, axis=0),
            'percentile_5': np.percentile(paths, 5, axis=0),
            'percentile_95': np.percentile(paths, 95, axis=0),
            'all_paths': paths
        }


class AdaptiveInflationModel(InflationModel):
    """Adaptive model that adjusts based on economic indicators"""
    
    def __init__(self,
                base_rate: Decimal = Decimal('0.03'),
                unemployment_target: Decimal = Decimal('0.04'),
                gdp_growth_target: Decimal = Decimal('0.025')):
        """
        Initialize adaptive model
        
        Args:
            base_rate: Base inflation rate
            unemployment_target: Target unemployment rate
            gdp_growth_target: Target GDP growth rate
        """
        super().__init__(base_rate)
        self.unemployment_target = unemployment_target
        self.gdp_growth_target = gdp_growth_target
    
    def get_inflation_rate(self,
                          year: int,
                          category: str = 'general',
                          unemployment: Optional[Decimal] = None,
                          gdp_growth: Optional[Decimal] = None) -> Decimal:
        """
        Get inflation rate adjusted for economic conditions
        
        Uses simplified Phillips curve relationship
        """
        rate = self.base_rate
        
        # Adjust for unemployment (inverse relationship)
        if unemployment is not None:
            unemployment_gap = unemployment - self.unemployment_target
            # Higher unemployment -> lower inflation
            rate -= unemployment_gap * Decimal('0.5')
        
        # Adjust for GDP growth (positive relationship)
        if gdp_growth is not None:
            growth_gap = gdp_growth - self.gdp_growth_target
            # Higher growth -> higher inflation
            rate += growth_gap * Decimal('0.3')
        
        # Apply category adjustment
        category_multiplier = self.CATEGORY_RATES.get(category, self.base_rate) / Decimal('0.03')
        
        # Ensure reasonable bounds
        rate = max(Decimal('-0.02'), min(Decimal('0.10'), rate))
        
        return rate * category_multiplier


def create_inflation_model(model_type: InflationType = InflationType.CONSTANT,
                          **kwargs) -> InflationModel:
    """
    Factory function to create inflation models
    
    Args:
        model_type: Type of inflation model
        **kwargs: Model-specific parameters
    
    Returns:
        InflationModel instance
    """
    if model_type == InflationType.CONSTANT:
        return ConstantInflationModel(**kwargs)
    elif model_type == InflationType.VARIABLE:
        return VariableInflationModel(**kwargs)
    elif model_type == InflationType.HISTORICAL:
        return HistoricalInflationModel(**kwargs)
    elif model_type == InflationType.STOCHASTIC:
        return StochasticInflationModel(**kwargs)
    else:
        raise ValueError(f"Unknown inflation model type: {model_type}")