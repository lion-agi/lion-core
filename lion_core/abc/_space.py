from abc import abstractmethod
from collections.abc import Iterable
from typing import Any

from lion_core.abc._characteristic import Traversal
from lion_core.abc._concept import AbstractElement, AbstractSpace


class Container(AbstractSpace, AbstractElement):
    """Container for items."""


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


class Structure(Container, Traversal):
    """Traversable container structure"""


__all__ = ["Container", "Ordering", "Collective", "Structure"]
