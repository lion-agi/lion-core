"""
Converter Utility Module

This module defines the Converter protocol and ConverterRegistry class
for managing conversions between Component objects and other types.
"""

from typing import Any, Type, Dict, Protocol
from abc import abstractmethod
from ..element.element import Element


class Converter(Protocol):
    """Protocol defining the interface for converter classes."""

    @classmethod
    @abstractmethod
    def from_obj(cls, obj: Any) -> dict:
        """Convert an object to a dictionary suitable for Component creation."""
        pass

    @classmethod
    @abstractmethod
    def to_obj(cls, component: Element) -> Any:
        """Convert a Component to another object type."""
        pass


class ConverterRegistry:
    """Registry for managing converters."""

    _converters: Dict[str, Type[Converter]] = {}

    @classmethod
    def register(cls, key: str, converter: Type[Converter]):
        """Register a converter for a specific key."""
        cls._converters[key] = converter

    @classmethod
    def get(cls, key: str) -> Type[Converter]:
        """Get a converter by key."""
        if key not in cls._converters:
            raise KeyError(f"No converter registered for key: {key}")
        return cls._converters[key]

    @classmethod
    def convert_from(cls, obj: Any, key: str) -> dict:
        """Convert an object to a dictionary using the specified converter."""
        converter = cls.get(key)
        return converter.from_obj(obj)

    @classmethod
    def convert_to(cls, component: Element, key: str) -> Any:
        """Convert a Component to another object using the specified converter."""
        converter = cls.get(key)
        return converter.to_obj(component)
