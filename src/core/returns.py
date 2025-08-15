"""Return calculation strategies"""

from abc import abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
import random
import math

from .base import Calculator


class ReturnCalculator(Calculator):
    """Base return calculator"""
    
    @abstractmethod
    def calculate_return(self, year: int) -> Decimal:
        pass
    
    def calculate(self, *args, **kwargs) -> Decimal:
        return self.calculate_return(*args, **kwargs)


@dataclass
class MonteCarloReturns(ReturnCalculator):
    """Monte Carlo return generator"""
    
    mean_return: Decimal
    volatility: Decimal
    
    def calculate_return(self, year: int) -> Decimal:
        """Generate random return from normal distribution
        
        Note: year parameter not used in basic Monte Carlo, 
        but kept for interface consistency
        """
        return_value = random.gauss(
            float(self.mean_return),
            float(self.volatility)
        )
        return Decimal(str(return_value))


@dataclass
class HistoricalReturns(ReturnCalculator):
    """Historical returns sampler"""
    
    historical_data: list[Decimal]
    sequential: bool = False
    start_year_offset: int = 0  # Which year in history to start from
    current_index: int = field(default=0, init=False)
    
    def calculate_return(self, year: int) -> Decimal:
        """Sample from historical data, either sequentially or randomly"""
        if self.sequential:
            # Use year to index into historical data sequentially
            index = (self.start_year_offset + year) % len(self.historical_data)
            return_value = self.historical_data[index]
        else:
            # Random sampling (year not used)
            return_value = random.choice(self.historical_data)
        return return_value


@dataclass
class RegimeBasedReturns(ReturnCalculator):
    """Market regime-based returns"""
    
    bull_params: tuple[Decimal, Decimal]  # (mean, std)
    bear_params: tuple[Decimal, Decimal]
    normal_params: tuple[Decimal, Decimal]
    regime_probabilities: dict[str, Decimal]
    current_regime: str = field(default='normal', init=False)
    regime_duration: dict[str, int] = field(default_factory=lambda: {
        'bull': 4, 'bear': 2, 'normal': 3
    })
    years_in_regime: int = field(default=0, init=False)
    
    def calculate_return(self, year: int) -> Decimal:
        """Generate returns based on market regime with persistence"""
        # Check if regime should change based on typical duration
        if self.years_in_regime >= self.regime_duration.get(self.current_regime, 3):
            # Time to potentially transition
            regimes = list(self.regime_probabilities.keys())
            probs = [float(self.regime_probabilities[r]) for r in regimes]
            self.current_regime = random.choices(regimes, weights=probs)[0]
            self.years_in_regime = 0
        
        self.years_in_regime += 1
        
        # Get parameters for current regime
        if self.current_regime == 'bull':
            mean, std = self.bull_params
        elif self.current_regime == 'bear':
            mean, std = self.bear_params
        else:
            mean, std = self.normal_params
        
        return_value = random.gauss(float(mean), float(std))
        return Decimal(str(return_value))


@dataclass
class GlidepathReturns(ReturnCalculator):
    """Returns that follow a glide path, reducing risk over time"""
    
    initial_stock_allocation: Decimal = Decimal('0.70')  # 70% stocks at start
    final_stock_allocation: Decimal = Decimal('0.30')    # 30% stocks at end
    stock_return: Decimal = Decimal('0.10')
    stock_volatility: Decimal = Decimal('0.20')
    bond_return: Decimal = Decimal('0.04')
    bond_volatility: Decimal = Decimal('0.05')
    total_years: int = 30
    
    def calculate_return(self, year: int) -> Decimal:
        """Calculate return based on glide path allocation"""
        # Calculate current stock allocation based on year
        progress = min(year / self.total_years, 1.0)
        stock_weight = self.initial_stock_allocation - (
            (self.initial_stock_allocation - self.final_stock_allocation) * Decimal(str(progress))
        )
        bond_weight = Decimal('1') - stock_weight
        
        # Generate returns for each asset class
        stock_return = random.gauss(float(self.stock_return), float(self.stock_volatility))
        bond_return = random.gauss(float(self.bond_return), float(self.bond_volatility))
        
        # Calculate weighted return
        portfolio_return = (
            stock_weight * Decimal(str(stock_return)) +
            bond_weight * Decimal(str(bond_return))
        )
        
        return portfolio_return


@dataclass
class SequenceAwareReturns(ReturnCalculator):
    """Returns that model sequence of returns risk"""
    
    mean_return: Decimal
    volatility: Decimal
    bad_sequence_probability: Decimal = Decimal('0.20')  # 20% chance of bad sequence
    bad_years_at_start: int = 5  # Number of bad years at beginning
    has_bad_sequence: bool = field(default=False, init=False)
    
    def __post_init__(self):
        """Determine if this simulation will have a bad sequence"""
        self.has_bad_sequence = random.random() < float(self.bad_sequence_probability)
    
    def calculate_return(self, year: int) -> Decimal:
        """Generate returns with potential bad sequence at start"""
        if self.has_bad_sequence and year < self.bad_years_at_start:
            # Bad returns in early years (sequence risk)
            return Decimal(str(random.gauss(
                float(self.mean_return) - 0.15,  # Much worse returns
                float(self.volatility) * 1.5      # Higher volatility
            )))
        else:
            # Normal returns
            return Decimal(str(random.gauss(
                float(self.mean_return),
                float(self.volatility)
            )))


@dataclass
class CyclicalReturns(ReturnCalculator):
    """Returns that follow economic cycles"""
    
    cycle_length: int = 7  # Years per economic cycle
    peak_return: Decimal = Decimal('0.15')
    trough_return: Decimal = Decimal('-0.05')
    base_volatility: Decimal = Decimal('0.15')
    phase_shift: float = field(default_factory=lambda: random.random() * 2 * math.pi)
    
    def calculate_return(self, year: int) -> Decimal:
        """Generate cyclical returns based on year"""
        # Calculate position in cycle (0 to 2π) with random phase shift
        cycle_position = (year % self.cycle_length) / self.cycle_length * 2 * math.pi + self.phase_shift
        
        # Sine wave for returns
        cycle_factor = math.sin(cycle_position)
        
        # Interpolate between trough and peak
        mean_return = (
            self.trough_return + 
            (self.peak_return - self.trough_return) * Decimal(str((cycle_factor + 1) / 2))
        )
        
        # Add randomness
        return_value = random.gauss(float(mean_return), float(self.base_volatility))
        return Decimal(str(return_value))


@dataclass
class MeanRevertingReturns(ReturnCalculator):
    """Returns that exhibit mean reversion over time"""
    
    long_term_mean: Decimal = Decimal('0.07')
    reversion_speed: Decimal = Decimal('0.3')  # Speed of reversion
    volatility: Decimal = Decimal('0.15')
    previous_returns: list[Decimal] = field(default_factory=list, init=False)
    
    def calculate_return(self, year: int) -> Decimal:
        """Generate mean-reverting returns"""
        if year == 0 or not self.previous_returns:
            # First year, use long-term mean
            base_return = self.long_term_mean
        else:
            # Calculate recent average
            recent_window = min(3, len(self.previous_returns))
            recent_avg = sum(self.previous_returns[-recent_window:]) / recent_window
            
            # Mean reversion adjustment
            reversion = self.reversion_speed * (self.long_term_mean - recent_avg)
            base_return = recent_avg + reversion
        
        # Add random component
        return_value = float(base_return) + random.gauss(0, float(self.volatility))
        return_value = Decimal(str(return_value))
        
        # Store for next calculation
        self.previous_returns.append(return_value)
        
        return return_value


@dataclass
class AgeBasedReturns(ReturnCalculator):
    """Returns based on investor age and risk tolerance"""
    
    starting_age: int = 65
    life_expectancy: int = 95
    young_retiree_return: Decimal = Decimal('0.08')
    young_retiree_vol: Decimal = Decimal('0.18')
    old_retiree_return: Decimal = Decimal('0.04')
    old_retiree_vol: Decimal = Decimal('0.08')
    
    def calculate_return(self, year: int) -> Decimal:
        """Calculate returns based on retiree age"""
        current_age = self.starting_age + year
        
        # Interpolate between young and old retiree parameters
        age_factor = min((current_age - self.starting_age) / 20, 1.0)  # Full transition over 20 years
        
        mean_return = (
            self.young_retiree_return * Decimal(str(1 - age_factor)) +
            self.old_retiree_return * Decimal(str(age_factor))
        )
        
        volatility = (
            self.young_retiree_vol * Decimal(str(1 - age_factor)) +
            self.old_retiree_vol * Decimal(str(age_factor))
        )
        
        return Decimal(str(random.gauss(float(mean_return), float(volatility))))


@dataclass
class FatTailReturns(ReturnCalculator):
    """Return calculator with fat tails (Student's t-distribution)"""
    
    mean_return: Decimal
    scale: Decimal  # Similar to standard deviation
    degrees_of_freedom: int = 5  # Lower = fatter tails
    
    def calculate_return(self, year: int) -> Decimal:
        """Calculate return with fat tails for extreme events"""
        # Generate from standard normal
        z = random.gauss(0, 1)
        
        # Generate from chi-squared
        chi_sq = sum(random.gauss(0, 1) ** 2 for _ in range(self.degrees_of_freedom))
        
        # Create t-distributed variable
        t_value = z / math.sqrt(chi_sq / self.degrees_of_freedom)
        
        # Scale and shift
        return_value = float(self.mean_return) + float(self.scale) * t_value
        
        return Decimal(str(return_value))


@dataclass
class MultiAssetReturns(ReturnCalculator):
    """Return calculator for multiple asset classes with correlations"""
    
    asset_returns: dict[str, Decimal]  # Asset class -> expected return
    asset_volatilities: dict[str, Decimal]  # Asset class -> volatility
    allocation: dict[str, Decimal]  # Asset class -> percentage
    correlation_matrix: dict[tuple[str, str], Decimal] = field(default_factory=dict)
    
    def calculate_return(self, year: int) -> Decimal:
        """Calculate portfolio return with asset correlations"""
        portfolio_return = Decimal('0')
        
        # Simple approach: generate returns for each asset
        # Note: For true correlation, would need Cholesky decomposition
        for asset, weight in self.allocation.items():
            if weight > 0:
                mean = self.asset_returns.get(asset, Decimal('0'))
                vol = self.asset_volatilities.get(asset, Decimal('0.1'))
                asset_return = Decimal(str(random.gauss(float(mean), float(vol))))
                portfolio_return += (weight / Decimal('100')) * asset_return
        
        return portfolio_return


@dataclass
class StressTestReturns(ReturnCalculator):
    """Returns for stress testing with configurable crisis periods"""
    
    normal_return: Decimal = Decimal('0.07')
    normal_volatility: Decimal = Decimal('0.15')
    crisis_return: Decimal = Decimal('-0.20')
    crisis_volatility: Decimal = Decimal('0.35')
    crisis_years: list[int] = field(default_factory=lambda: [3, 4])  # Years when crisis occurs
    
    def calculate_return(self, year: int) -> Decimal:
        """Generate returns with crisis periods"""
        if year in self.crisis_years:
            # Crisis period
            return Decimal(str(random.gauss(
                float(self.crisis_return),
                float(self.crisis_volatility)
            )))
        else:
            # Normal period
            return Decimal(str(random.gauss(
                float(self.normal_return),
                float(self.normal_volatility)
            )))