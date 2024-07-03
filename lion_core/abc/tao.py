"""
Core abstractions for the Lion framework.

This module defines fundamental abstract base classes that form the
foundation of the Lion framework's conceptual model. These abstractions
represent core philosophical and mathematical concepts such as existence,
measurement, entity, time, state, agency, description, change, and logic.

Classes:
    Abstraction: The notion of 'being' or 'existing'.
    AbstractSpace: A Borel Space, representing a set and a σ-field.
    AbstractElement: A distinct entity within a space.
    AbstractObservation: A static snapshot state of a space.
    AbstractObserver: An entity capable of observing a space.
    AbstractCharacteristic: A property of an element.
    AbstractEvent: A change in a space.
    AbstractCondition: A check of state.
"""

from abc import ABC, abstractmethod
from typing import Any

class Abstraction(ABC):
    """The notion of 'being' or 'existing'."""

class AbstractSpace(Abstraction):
    """A Borel Space, the existence of a set and a σ-field."""

class AbstractElement(Abstraction):
    """A distinct entity within a space."""

class AbstractObservation(Abstraction):
    """Represents static snapshot state of a space."""

class AbstractObserver(Abstraction):
    """An entity capable of observing a space."""

class AbstractCharacteristic(Abstraction):
    """A property of an element."""

class AbstractEvent(Abstraction):
    """Represents a change in a space."""

class AbstractCondition(Abstraction):
    """Represents a check of state."""

    @abstractmethod
    async def applies(self, *args: Any, **kwargs: Any) -> bool:
        """Check if the condition applies.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            bool: True if the condition applies, False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement applies method.")
    
    
# lion_core/abc/tao.py