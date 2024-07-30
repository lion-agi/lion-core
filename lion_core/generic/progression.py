"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import annotations

import contextlib
from typing import Any, Iterator, override

from pydantic import Field, field_validator

from lion_core.abc._space import Ordering
from lion_core.libs import to_list
from lion_core.sys_utils import SysUtil
from lion_core.generic.element import Element
from lion_core.exceptions import ItemNotFoundError, LionTypeError
from lion_core.generic.util import validate_order, to_list_type


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

    @field_validator("order", mode="before")
    def _validate_order(cls, value):
        return validate_order(value)

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

        item = to_list_type(item) if not isinstance(item, list) else item

        check = False
        for i in item:
            check = False
            if isinstance(i, str):
                check = i in self.order

            elif isinstance(i, Element):
                check = i.ln_id in self.order

            if not check:
                return False

        return check

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
        if not isinstance(key, int | slice):
            raise TypeError(
                f"indices must be integers or slices, not {key.__class__.__name__}"
            )

        try:
            a = self.order[key]
            if not a:
                raise ItemNotFoundError(f"index {key} item not found")
            if isinstance(key, slice):
                return Progression(order=a)
            else:
                return a
        except IndexError:
            raise ItemNotFoundError(f"index {key} item not found")

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

    def append(self, item: Any) -> None:
        """
        Append an item to the end of the progression.

        Args:
            item: The item to append.
        """
        item_ = validate_order(item)
        self.order.extend(item_)

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
            raise ItemNotFoundError("pop index out of range") from e

    def include(self, item: Any):
        """
        Include item(s) in the progression.

        If the item is not already in the progression, it will be added.

        Args:
            item: The item(s) to include.

        Returns:
            bool: True if the item(s) were included, False if already present.
        """
        item_ = validate_order(item)
        for i in item_:
            if i not in self.order:
                self.order.append(i)

    def exclude(self, item: int | Any):
        """
        Exclude an item or items from the progression.

        Args:
            item: The item(s) to exclude or the number of items to remove from the start.

        Returns:
            bool: True if the item(s) were excluded, False otherwise.

        Raises:
            IndexError: If trying to remove more items than available.
        """
        for i in validate_order(item):
            while i in self:
                self.remove(i)

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

    @override
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
        return (
            self.order.index(SysUtil.get_id(item), start, end)
            if end
            else self.order.index(SysUtil.get_id(item), start)
        )

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
            l_ = list(self.order)

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
        if not isinstance(item, Progression):
            raise LionTypeError(expected_type=Progression, actual_type=type(item))
        self.order.extend(item.order)

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
        return self.order.count(SysUtil.get_id(item))

    @override
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
        other = validate_order(other)
        new_order = list(self)
        new_order.extend(other)
        return Progression(order=new_order)

    def __radd__(self, other: Any) -> Progression:
        """
        Add this progression to another item or progression.

        Args:
            other: The item or progression to add to.

        Returns:
            Progression: A new Progression with the combined items.
        """

        return self + other

    def __iadd__(self, other: Any) -> Progression:
        """
        Add an item to the end of the progression in-place.

        Args:
            other: The item to add.

        Returns:
            Progression: The modified progression.
        """
        self.append(other)
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
        other = validate_order(other)
        new_order = list(self)
        for i in other:
            new_order.remove(i)
        return Progression(order=new_order)

    @override
    def __repr__(self) -> str:
        """
        Return a string representation of the progression.

        Returns:
            str: A string representation of the progression.
        """
        return f"Progression({self.order})"

    @override
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
        item_ = validate_order(item)
        for i in reversed(item_):
            self.order.insert(index, SysUtil.get_id(i))


def progression(order: Any = None, name: str | None = None) -> Progression:
    """
    Create a new Progression instance.

    Args:
        order: The initial order of items in the progression.
        name: The name of the progression.

    Returns:
        A new Progression instance.
    """
    return Progression(order=order, name=name)


# File: lion_core/generic/progression.py
