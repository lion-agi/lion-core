"""Abstract container classes for the Lion framework."""

from abc import abstractmethod
from .concept import AbstractSpace, AbstractElement
from .characteristic import Traversal


class Container(AbstractSpace, AbstractElement):
    """
    Abstract container or storage space. Subclasses should implement
    __contains__ to define membership criteria.
    """

    @abstractmethod
    def __contains__(self, item) -> bool:
        """
        Check if an item is in the container.

        Args:
            item: The item to check.

        Returns:
            bool: True if the item is in the container, False otherwise.
        """


class Ordering(Container):
    """Container with a defined order. Subclass must have order attribute."""


class Collective(Container):
    """Container representing a collection of items."""

    @abstractmethod
    def items(self):
        """
        Get the items in the collective.

        Returns:
            Iterable: The items in the collective.
        """


class Structure(Container, Traversal):
    """
    Container with traversable structure, combining Container and Traversal
    characteristics.
    """
