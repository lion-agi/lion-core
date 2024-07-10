"""Abstract space classes for the Lion framework."""

from abc import ABC, abstractmethod
from typing import Any, Iterable, TypeVar, Generic

from ..abc.concept import AbstractSpace
from ..abc.element import Element

T = TypeVar("T", bound=Element)


class Container(AbstractSpace):
    """A container that is both an element and an abstract space."""


class Ordering(Container):
    """A container with a defined order."""


class Collective(Container, Generic[T], ABC):
    """
    An abstract base class for record-like structures in the Lion framework.

    This class defines a set of common operations that should be implemented
    by its subclasses to provide consistent behavior across different types
    of records or collections.
    """

    @abstractmethod
    def __getitem__(self, key: Any) -> T:
        """
        Retrieve an item or items from the record.

        Args:
            key: The key or index to retrieve items.

        Returns:
            The item(s) corresponding to the given key.
        """
        pass

    @abstractmethod
    def __setitem__(self, key: Any, value: T) -> None:
        """
        Set an item or items in the record.

        Args:
            key: The key or index to set.
            value: The value to set.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """
        Get the number of items in the record.

        Returns:
            The number of items in the record.
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterable[T]:
        """
        Return an iterator over the items in the record.

        Yields:
            Items in the record.
        """
        pass

    @abstractmethod
    def __contains__(self, item: Any) -> bool:
        """
        Check if an item is in the record.

        Args:
            item: The item to check for.

        Returns:
            True if the item is in the record, False otherwise.
        """
        pass

    @abstractmethod
    def keys(self) -> Iterable[Any]:
        """
        Get the keys or indices of the record.

        Returns:
            An iterable of keys or indices.
        """
        pass

    @abstractmethod
    def values(self) -> Iterable[T]:
        """
        Get the values of the record.

        Returns:
            An iterable of values.
        """
        pass

    @abstractmethod
    def items(self) -> Iterable[tuple[Any, T]]:
        """
        Get the items of the record as (key, value) pairs.

        Returns:
            An iterable of (key, value) tuples.
        """
        pass

    @abstractmethod
    def get(self, key: Any, default: Any = None) -> T:
        """
        Get an item from the record with a default value if not found.

        Args:
            key: The key of the item to get.
            default: The default value to return if the key is not found.

        Returns:
            The item if found, otherwise the default value.
        """
        pass

    @abstractmethod
    def pop(self, key: Any, default: Any = None) -> T:
        """
        Remove and return an item from the record.

        Args:
            key: The key of the item to remove.
            default: The default value to return if the key is not found.

        Returns:
            The removed item if found, otherwise the default value.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Remove all items from the record."""
        pass

    @abstractmethod
    def update(self, other: Any) -> None:
        """
        Update the record with items from another record or iterable.

        Args:
            other: The record or iterable to update from.
        """
        pass

    @abstractmethod
    def copy(self) -> "Collective[T]":
        """
        Create a shallow copy of the record.

        Returns:
            A new Record instance with the same items.
        """
        pass

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
        pass

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
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Check if the record is empty.

        Returns:
            True if the record is empty, False otherwise.
        """
        pass

    @abstractmethod
    def size(self) -> int:
        """
        Get the total size of the record.

        Returns:
            The total size of the record, which may differ from __len__
            depending on the implementation.
        """
        pass

    def __bool__(self) -> bool:
        """
        Check if the record is considered True.

        Returns:
            True if the record is not empty, False otherwise.
        """
        return not self.is_empty()


# File: lion_core/container/base.py
