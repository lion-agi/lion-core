"""
Defines the Progression class for managing ordered sequences in the Lion framework.

This module provides the Progression class, a flexible container for ordered
lists of Lion IDs. It supports various operations including addition, removal,
and manipulation of elements, as well as list-like indexing and slicing.

Key components:
- Progression: Main class for handling ordered sequences of Lion IDs.
- progression: Utility function for creating Progression instances.

The Progression class is a core data structure in Lion, designed to work
seamlessly with other Lion components and support complex data manipulations.
"""

from __future__ import annotations

import contextlib
from typing import Any, Iterator

from pydantic import Field, ConfigDict

from lion_core.abc.container import Ordering
from lion_core.libs import to_list
from lion_core.sys_util import SysUtil
from lion_core.generic.element import Element
from lion_core.exceptions import ItemNotFoundError
from .util import validate_order, to_list_type


class Progression(Element, Ordering):
    """
    A flexible, ordered sequence container for managing and manipulating lists of items.

    The Progression class is a core component in the Lion framework, designed to maintain
    an ordered list of item identifiers (Lion IDs) while providing a rich set of operations
    for manipulation and access. It combines list-like functionality with additional
    features specific to the Lion framework.

    Key features:
    - Maintains an ordered list of item identifiers (Lion IDs)
    - Supports both list-like indexing and Lion ID-based operations
    - Provides methods for adding, removing, and manipulating items
    - Implements common sequence operations (len, iter, contain, etc.)
    - Supports arithmetic operations for combining progressions

    Attributes:
        name (str | None): Optional name for the progression.
        order (list[str]): The ordered list of item identifiers (Lion IDs).

    Args:
        order (list[str] | None, optional): Initial order of items.
        name (str | None, optional): Name for the progression.
    """

    name: str | None = Field(
        None,
        title="Name",
        description="The name of the progression.",
    )
    order: list[str] = Field(
        default_factory=list,
        title="Order",
        description="The order of the progression.",
    )
    model_config = ConfigDict(
        extra="forbid",
    )

    def __init__(self, order=None, name=None):
        super().__init__(order=validate_order(order), name=name)

    def __contains__(self, item: Any) -> bool:
        """
        Check if item(s) are in the progression.

        Args:
            item: The item or items to check for.

        Returns:
            bool: True if the item(s) are in the progression, False otherwise.
        """
        if item is None or not self.order:
            return False

        if isinstance(item, str):
            if SysUtil.is_str_id(item):
                return item in self.order

        if isinstance(item, Ordering) and item.order <= self.order:
            return True

        if isinstance(item, Element):
            return item.ln_id in self.order

        item = to_list_type(item) if not isinstance(item, list) else item
        return all(i in self for i in item)

    def __list__(self) -> list[str]:
        """
        Return a copy of the order.

        Returns:
            list[str]: A copy of the progression's order.
        """
        return self.order[:]

    def __len__(self) -> int:
        """
        Get the length of the progression.

        Returns:
            int: The number of items in the progression.
        """
        return len(self.order)

    def __getitem__(self, key: int | slice) -> str | Progression:
        """
        Get an item or slice of items from the progression.

        Args:
            key: An integer index or slice object.

        Returns:
            str | Progression: The item at the given index or a new Progression with the sliced items.

        Raises:
            ItemNotFoundError: If the requested index or slice is out of range.
        """
        try:
            if isinstance(key, slice):
                a = self.order[key]
                if len(a) < abs(key.stop - key.start):
                    raise ItemNotFoundError(
                        f"Requested more items than available: {key}"
                    )
                return Progression(order=a)

            a = self.order[key]
            if isinstance(a, list) and len(a) > 1:
                return Progression(order=a)
            elif isinstance(a, list) and len(a) == 1:
                return a[0]
            return a
        except IndexError:
            raise ItemNotFoundError(f"index {key}")

    def __setitem__(self, key: int | slice, value: Any) -> None:
        """
        Set an item or slice of items in the progression.

        Args:
            key: An integer index or slice object.
            value: The item(s) to set.
        """
        a = validate_order(value)
        self.order[key] = a
        self.order = to_list(self.order, flatten=True)

    def __delitem__(self, key: int | slice) -> None:
        """
        Delete an item or slice of items from the progression.

        Args:
            key: An integer index or slice object.
        """
        del self.order[key]

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over the items in the progression.

        Returns:
            Iterator[str]: An iterator over the Lion IDs in the progression.
        """
        return iter(self.order)

    def __next__(self) -> str:
        """
        Return the next item in the progression.

        Returns:
            str: The next Lion ID in the progression.

        Raises:
            StopIteration: If there are no more items in the progression.
        """
        try:
            return next(iter(self.order))
        except StopIteration:
            raise StopIteration("No more items in the progression")

    def size(self) -> int:
        """
        Get the size of the progression.

        Returns:
            int: The number of items in the progression.
        """
        return len(self)

    def clear(self) -> None:
        """Clear the progression."""
        self.order.clear()

    def copy(self) -> Progression:
        """
        Create a deep copy of the progression.

        Returns:
            Progression: A new Progression instance with the same items.
        """
        return self.model_copy(deep=True)

    def keys(self) -> Iterator[int]:
        """
        Get the indices of the progression.

        Returns:
            Iterator[int]: An iterator over the indices of the progression.
        """
        yield from range(len(self))

    def values(self) -> Iterator[str]:
        """
        Get the values of the progression.

        Returns:
            Iterator[str]: An iterator over the Lion IDs in the progression.
        """
        yield from self.order

    def items(self) -> Iterator[tuple[int, str]]:
        """
        Get the items of the progression as (index, value) pairs.

        Returns:
            Iterator[tuple[int, str]]: An iterator over (index, Lion ID) pairs.
        """
        yield from enumerate(self.order)

    def append(self, item: Any) -> None:
        """
        Append an item to the end of the progression.

        Args:
            item: The item to append.
        """
        id_ = SysUtil.get_lion_id(item)
        self.order.extend(id_)

    def pop(self, index: int | None = None) -> str:
        """
        Remove and return an item from the progression.

        Args:
            index: The index of the item to remove. If None, removes the last item.

        Returns:
            str: The Lion ID of the removed item.

        Raises:
            ItemNotFoundError: If the progression is empty or the index is out of range.
        """
        try:
            if index is None:
                return self.order.pop()
            return self.order.pop(index)
        except IndexError as e:
            raise ItemNotFoundError("None") from e

    def include(self, item: Any) -> bool:
        """
        Include item(s) in the progression.

        If the item is not already in the progression, it will be added.

        Args:
            item: The item(s) to include.

        Returns:
            bool: True if the item(s) were included, False if already present.
        """
        if item not in self:
            self.extend(item)
        return item in self

    def exclude(self, item: int | Any) -> bool:
        """
        Exclude an item or items from the progression.

        Args:
            item: The item(s) to exclude or the number of items to remove from the start.

        Returns:
            bool: True if the item(s) were excluded, False otherwise.

        Raises:
            IndexError: If trying to remove more items than available.
        """
        if isinstance(item, int) and item > 0:
            if item > len(self):
                raise IndexError("Cannot remove more items than available.")
            for _ in range(item):
                self.popleft()
            return True
        if isinstance(item, Progression):
            for i in item:
                while i in self:
                    self.remove(i)
        for i in (a := validate_order(item)):
            while i in self:
                self.remove(i)
        return a not in self

    def is_empty(self) -> bool:
        """
        Check if the progression is empty.

        Returns:
            bool: True if the progression is empty, False otherwise.
        """
        return not self.order

    def __reverse__(self) -> Iterator[str]:
        """
        Return a reversed progression.

        Returns:
            Iterator[str]: An iterator over the reversed Lion IDs in the progression.
        """
        return progression(reversed(self.order), name=self.name)

    def __eq__(self, other: object) -> bool:
        """
        Compare two Progression instances for equality.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if the progressions are equal, False otherwise.
        """
        if not isinstance(other, Progression):
            return NotImplemented
        return self.order == other.order and self.name == other.name

    def index(self, item: Any, start: int = 0, end: int | None = None) -> int:
        """
        Return the index of an item in the progression.

        Args:
            item: The item to find.
            start: The index to start searching from.
            end: The index to end searching at.

        Returns:
            int: The index of the item.

        Raises:
            ValueError: If the item is not found.
        """
        return self.order.index(SysUtil.get_lion_id(item), start, end)

    def remove(self, item: Any) -> None:
        """
        Remove the next occurrence of an item from the progression.

        Args:
            item: The item to remove.

        Raises:
            ItemNotFoundError: If the item is not found in the progression.
        """
        if item in self:
            item = validate_order(item)
            l_: list = SysUtil.copy(self.order)

            with contextlib.suppress(ValueError):
                for i in item:
                    l_.remove(i)
                self.order = l_
                return

        raise ItemNotFoundError(f"{item}")

    def popleft(self) -> str:
        """
        Remove and return the leftmost item from the progression.

        Returns:
            str: The Lion ID of the removed item.

        Raises:
            ItemNotFoundError: If the progression is empty.
        """
        try:
            return self.order.pop(0)
        except IndexError as e:
            raise ItemNotFoundError from e

    def extend(self, item: Progression | Any) -> None:
        """
        Extend the progression from the right with item(s).

        Args:
            item: The item(s) to add to the progression.
        """
        if isinstance(item, Progression):
            self.order.extend(item.order)
            return
        order = validate_order(item)
        self.order.extend(order)

    def count(self, item: Any) -> int:
        """
        Return the number of occurrences of an item in the progression.

        Args:
            item: The item to count.

        Returns:
            int: The number of occurrences of the item.
        """
        if not self.order or item not in self:
            return 0
        return self.order.count(SysUtil.get_lion_id(item))

    def __bool__(self) -> bool:
        """
        Check if the container is considered True.

        This method allows containers to be used in boolean contexts,
        typically based on whether they contain elements.
        """
        return not self.is_empty()

    def __add__(self, other: Any) -> Progression:
        """
        Add an item or items to the end of the progression.

        Args:
            other: The item(s) to add.

        Returns:
            Progression: A new Progression with the added item(s).
        """
        _copy = self.copy()
        _copy.include(other)
        return _copy

    def __radd__(self, other: Any) -> Progression:
        """
        Add this progression to another item or progression.

        Args:
            other: The item or progression to add to.

        Returns:
            Progression: A new Progression with the combined items.
        """
        if not isinstance(other, Progression):
            _copy = self.copy()
            l_: list = SysUtil.copy(_copy.order, deep=True)
            l_.insert(0, SysUtil.get_lion_id(other))
            _copy.order = l_
            return _copy

        return other + self

    def __iadd__(self, other: Any) -> Progression:
        """
        Add an item to the end of the progression in-place.

        Args:
            other: The item to add.

        Returns:
            Progression: The modified progression.
        """
        self.order.append(SysUtil.get_lion_id(other))
        return self

    def __isub__(self, other: Any) -> Progression:
        """
        Remove an item from the progression in-place.

        Args:
            other: The item to remove.

        Returns:
            Progression: The modified progression.
        """
        self.remove(other)
        return self

    def __sub__(self, other: Any) -> Progression:
        """
        Remove an item or items from the progression.

        Args:
            other: The item(s) to remove.

        Returns:
            Progression: A new Progression without the specified item(s).
        """
        _copy = self.copy()
        _copy.remove(other)
        return _copy

    def __repr__(self) -> str:
        """
        Return a string representation of the progression.

        Returns:
            str: A string representation of the progression.
        """
        return f"Progression({self.order})"

    def __str__(self) -> str:
        """
        Return a string representation of the progression.

        Returns:
            str: A string representation of the progression.

        Examples:
            >>> p = Progression([MyElement(value=1), MyElement(value=2)], name="Test")
            >>> str(p)
            'Progression(name=Test, size=2, items=['ln_...', 'ln_...'])'
        """
        if len(a := str(self.order)) > 50:
            a = a[:50] + "..."
        return f"Progression(name={self.name}, size={len(self)}, items={a})"

    def insert(self, index: int, item: Any) -> None:
        """
        Insert an item at the specified index.

        Args:
            index: The index at which to insert the item.
            item: The item to insert.
        """
        self.order.insert(index, SysUtil.get_lion_id(item))


def progression(order: list[str] | None = None, name: str | None = None) -> Progression:
    """
    Create a new Progression instance.

    Args:
        order: The initial order of items in the progression.
        name: The name of the progression.

    Returns:
        A new Progression instance.
    """
    return Progression(order=order, name=name)


# File: lion_core/container/progression.py
