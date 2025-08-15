"""Base classes for domain models"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict


class Entity(ABC):
    """Base entity class"""
    @abstractmethod
    def get_id(self) -> str:
        pass


class ValueObject(ABC):
    """Base value object"""
    pass


class Calculator(ABC):
    """Base calculator interface"""
    @abstractmethod
    def calculate(self, *args, **kwargs) -> Any:
        pass


class Strategy(ABC):
    """Base strategy interface"""
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass