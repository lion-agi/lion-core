from abc import abstractmethod
from collections.abc import Iterable
from typing import Any

from lion_core.abc._characteristic import Traversal
from lion_core.abc._concept import AbstractElement, AbstractSpace


class Container(AbstractSpace, AbstractElement):
    """Container for items."""

    @abstractmethod
    def __contains__(self, item: object) -> bool:
        """Check if an item is in the space."""


class Ordering(Container):
    """Container with a defined order. Subclass must have order attribute."""

    order: list[str]


class Collective(Container):
    """Container representing a collection of items."""

    @abstractmethod
    def items(self) -> Iterable[Any]:
        """
        Get the items in the collective.

        Returns:
            Iterable: The items in the collective.
        """

    @abstractmethod
    def values(self) -> Iterable[Any]:
        """
        Get the values in the collective.

        Returns:
            Iterable: The values in the collective.
        """

    @abstractmethod
    def keys(self) -> Iterable[Any]:
        """
        Get the keys in the collective.

        Returns:
            Iterable: The keys in the collective.
        """


class Structure(Container, Traversal):
    """Traversable container structure"""


__all__ = ["Container", "Ordering", "Collective", "Structure"]
