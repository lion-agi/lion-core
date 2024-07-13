"""Abstract space classes for the Lion framework."""

from abc import abstractmethod
from typing import Any, TypeVar, Generic, Optional

from .concept import AbstractSpace

T = TypeVar("T")


class Container(AbstractSpace):
    """A container that is both an element and an abstract space."""

    @abstractmethod
    def __list__(self) -> list:
        """Return the ordering as a list."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of items."""

    @abstractmethod
    def __getitem__(self, index: int) -> Any:
        """Get item at index."""

    @abstractmethod
    def __setitem__(self, index: int, item: Any) -> None:
        """Set item at index."""

    @abstractmethod
    def __delitem__(self, index: int) -> None:
        """Delete item at index."""

    @abstractmethod
    def __iter__(self) -> Any:
        """Return an iterator for the ordering."""

    @abstractmethod
    def __next__(self) -> Any:
        """Return the next item in the ordering."""

    @abstractmethod
    def size(self) -> int:
        """Return the size of the container. Similar to numpy.size()"""

    @abstractmethod
    def clear(self) -> None:
        """Remove all items from the container."""

    @abstractmethod
    def copy(self) -> "Container":
        """Return a shallow copy of the container."""

    @abstractmethod
    def keys(self) -> Any:
        """Return a key for the ordering."""

    @abstractmethod
    def values(self) -> Any:
        """Return the values of the ordering."""

    @abstractmethod
    def items(self) -> Any:
        """Return the items of the ordering as (key, value) pairs."""

    @abstractmethod
    def append(self, *args, **kwargs) -> None:
        """Add an item to the end of the ordering."""

    @abstractmethod
    def pop(self, *args, **kwargs) -> Any:
        """Remove and return item at index (default last)."""

    @abstractmethod
    def include(self, item: T) -> bool:
        """
        Include an item in the record if not already present.

        Args:
            item: The item to include.

        Returns:
            True if the item was included, False if exception occurred or
            the item wasn't a member of the record when function exited.
        """

    @abstractmethod
    def exclude(self, item: T) -> bool:
        """
        Exclude an item from the record if present.

        Args:
            item: The item to exclude.

        Returns:
            True if the item was excluded, False if exception occurred or
            the item still is a member of the record when function exited.
        """

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Check if the record is empty.

        Returns:
            True if the record is empty, False otherwise.
        """

    def __bool__(self) -> bool:
        """
        Check if the record is considered True.

        Returns:
            True if the record is not empty, False otherwise.
        """
        return not self.is_empty()


class Ordering(Container):
    """A container with a defined order."""

    @abstractmethod
    def __reverse__(self) -> "Ordering":
        """Return a reversed copy of the ordering."""

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Return True if the orderings are equal, False otherwise."""

    @abstractmethod
    def index(self, item: Any, start: int = 0, end: Optional[int] = None) -> int:
        """Return first index of item. Raise ValueError if not found."""

    @abstractmethod
    def remove(self, item: Any) -> None:
        """Remove the first occurrence of an item from the ordering."""

    @abstractmethod
    def popleft(self) -> Any:
        """Remove and return first item in the ordering."""

    @abstractmethod
    def extend(self, *args, **kwargs) -> None:
        """Add multiple items to the end of the ordering."""

    @abstractmethod
    def count(self, *args, **kwargs) -> int:
        """Return number of occurrences of item."""


class Index(Ordering):
    ...



class Collective(Container, Generic[T]):
    """
    An abstract base class for record-like structures in the Lion framework.

    This class defines a set of common operations that should be implemented
    by its subclasses to provide consistent behavior across different types
    of records or collections.
    """

    @abstractmethod
    def update(self, other: Any) -> None:
        """
        Update the record with items from another record or iterable.

        Args:
            other: The record or iterable to update from.
        """

    @abstractmethod
    def get(self, key: Any, default: Any = ...) -> T:
        """Return item at key if key in ordering, else default."""


# File: lion_core/container/base.py
