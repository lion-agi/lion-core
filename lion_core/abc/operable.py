# lion_core/abc/operable.py

"""
LionAGI: Operable Classes

This module defines abstract classes that extend the Operable concept,
representing various types of operations that can be performed in the LionAGI
system.
"""

from abc import abstractmethod
from typing import Any
from functools import partial
from lion_core.settings import lion_category
from .tao import AbstractCharacteristic


operable_category = partial(
    lion_category,
    abstraction_level="abstract",
    functionality="base",
    domain_specificity="core",
    visibility_scope="public",
    optimization_level="unoptimized",
    testing_category="not_tested",
    documentation_status="undocumented",
    version_control="experimental",
    filepaths=["lion_core", "abc", "operable.py"],
    author="ocean",
    created_at="2024-07-01",
)


@operable_category(
    core_concept="characteristic", parent_class=["AbstractCharacteristic"]
)
class Operable(AbstractCharacteristic):
    """an entity that can carry out operations."""


@operable_category(core_concept="characteristic", parent_class=["Operable"])
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


@operable_category(core_concept="characteristic", parent_class=["Operable"])
class Relatable(Operable):
    """A class representing operations that can relate elements."""

    @abstractmethod
    async def relate(self, *args: Any, **kwargs: Any) -> Any:
        """Establish a relationship between the given elements."""


@operable_category(core_concept="characteristic", parent_class=["Operable"])
class Sendable(Operable):
    """A class representing operations that can send information."""

    @abstractmethod
    async def send(self, *args: Any, **kwargs: Any) -> Any:
        """Send information to a specified destination."""


@operable_category(core_concept="characteristic", parent_class=["Operable"])
class Actionable(Operable):
    """A class representing operations that can invoke actions."""

    @abstractmethod
    async def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """Invoke a specified action."""


@operable_category(core_concept="characteristic", parent_class=["Operable"])
class Workable(Operable):
    """A class representing operations that can perform tasks."""

    @abstractmethod
    async def perform(self, task: str, *args: Any, **kwargs: Any) -> Any:
        """Perform a specified task."""
