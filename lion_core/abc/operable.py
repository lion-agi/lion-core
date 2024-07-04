# lion_core/abc/operable.py

"""
LionAGI: Operable Classes

This module defines abstract classes that extend the Operable concept,
representing various types of operations that can be performed in the LionAGI
system.
"""

from abc import abstractmethod
from typing import Any
from .tao import AbstractCharacteristic


class Operable(AbstractCharacteristic):
    """an entity that can carry out operations."""


class Decidable(Operable):
    """A class representing operations that can make decisions."""

    @abstractmethod
    async def apply(self, *args: Any, **kwargs: Any) -> bool:
        """Make a decision based on the given inputs.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            bool: The decision result (True or False).
        """


class Relatable(Operable):
    """A class representing operations that can relate elements."""

    @abstractmethod
    async def relate(self, *args: Any, **kwargs: Any) -> Any:
        """Establish a relationship between the given elements."""


class Sendable(Operable):
    """A class representing operations that can send information."""

    @abstractmethod
    async def send(self, *args: Any, **kwargs: Any) -> Any:
        """Send information to a specified destination."""


class Actionable(Operable):
    """A class representing operations that can invoke actions."""

    @abstractmethod
    async def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """Invoke a specified action."""


class Workable(Operable):
    """A class representing operations that can perform tasks."""

    @abstractmethod
    async def perform(self, task: str, *args: Any, **kwargs: Any) -> Any:
        """Perform a specified task."""
