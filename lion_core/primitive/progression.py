"""Progression module for the Lion framework.

This module defines the Progression class, a collection of ordered items with
various manipulation methods. It provides functionality for managing, accessing,
and modifying ordered sequences of items.

Classes:
    Progression: A collection of ordered items with various manipulation methods.

Functions:
    progression: Factory function to create a new Progression instance.
"""

from __future__ import annotations

import contextlib
from typing import Any, Iterator, Tuple

from pydantic import Field, field_validator

from lion_core.libs import SysUtil
from ..abc import Ordering, ItemNotFoundError, AbstractElement
from .util import validate_order, get_lion_id


class Progression(AbstractElement, Ordering):
    """A collection of ordered items with various manipulation methods.

    This class provides functionality for managing, accessing, and modifying
    ordered sequences of items. It supports various operations such as
    appending, extending, removing, and accessing items by index or slice.

    Attributes:
        name (str | None): The name of the progression.
        order (list[str]): The ordered list of item IDs in the progression.
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
    def _validate_order(cls, value: Any) -> list[str]:
        """Validate and convert the order field."""
        return validate_order(value)

    def __contains__(self, item: Any) -> bool:
        """Check if an item or items are in the progression.

        Args:
            item: The item or items to check for.

        Returns:
            True if the item(s) are in the progression, False otherwise.
        """
        if not item:
            return False
        if isinstance(item, Progression):
            return all(i in self.order for i in item.order)
        if isinstance(item, (AbstractElement, str)) and len(
            a := get_lion_id(item)
        ) == 32:
            return a in self.order
        item = self._validate_order(item)
        return all(i in self.order for i in item)

    def __len__(self) -> int:
        """Get the length of the progression."""
        return len(self.order)

    def keys(self) -> Iterator[int]:
        """Get the indices of the progression."""
        yield from range(len(self))

    def values(self) -> Iterator[str]:
        """Get the values of the progression."""
        yield from self.order

    def items(self) -> Iterator[Tuple[int, str]]:
        """Get the items of the progression as (index, value) pairs."""
        for idx, item in enumerate(self.order):
            yield idx, item

    def size(self) -> int:
        """Get the size of the progression."""
        return len(self)

    def copy(self) -> Progression:
        """Create a deep copy of the progression."""
        return self.model_copy()

    def append(self, item: Any) -> None:
        """Append an item to the end of the progression.

        Args:
            item: The item to append.
        """
        id_ = get_lion_id(item)
        self.order.append(id_)

    def extend(self, item: Progression | Any) -> None:
        """Extend the progression from the right with item(s).

        Args:
            item: The item(s) to extend the progression with.
        """
        if isinstance(item, Progression):
            self.order.extend(item.order)
            return
        order = self._validate_order(item)
        self.order.extend(order)

    def include(self, item: Any) -> bool:
        """Include item(s) in the progression.

        If the item is not already in the progression, it will be added.

        Args:
            item: The item(s) to include.

        Returns:
            True if the item(s) were included, False if already present.
        """
        if item not in self:
            self.extend(item)
        return item in self

    def __getitem__(self, key: int | slice) -> str | Progression:
        """Get an item or slice of items from the progression.

        Args:
            key: The index or slice to retrieve.

        Returns:
            The item(s) at the specified index or slice.

        Raises:
            ItemNotFoundError: If the index is out of range.
        """
        with contextlib.suppress(IndexError):
            a = self.order[key]
            if isinstance(a, list) and len(a) > 1:
                return Progression(order=a)
            elif isinstance(a, list) and len(a) == 1:
                return a[0]
            return a

        raise ItemNotFoundError(f"index {key}")

    def remove(self, item: Any) -> None:
        """Remove the next occurrence of an item from the progression.

        Args:
            item: The item to remove.

        Raises:
            ItemNotFoundError: If the item is not found in the progression.
        """
        if item in self:
            item = self._validate_order(item)
            l_ = SysUtil.copy(self.order)

            with contextlib.suppress(Exception):
                for i in item:
                    l_.remove(i)
                self.order = l_
                return

        raise ItemNotFoundError(f"{item}")

    def __list__(self) -> list[str]:
        """Convert the progression to a list."""
        return self.order

    def popleft(self) -> str:
        """Remove and return the leftmost item from the progression.

        Returns:
            The leftmost item.

        Raises:
            ItemNotFoundError: If the progression is empty.
        """
        try:
            return self.order.pop(0)
        except IndexError as e:
            raise ItemNotFoundError("None") from e

    def pop(self, index: int | None = None) -> str:
        """Remove and return an item from the progression.

        Args:
            index: The index of the item to remove. If None, removes the last.

        Returns:
            The removed item.

        Raises:
            ItemNotFoundError: If index is out of range or progression is empty.
        """
        try:
            return self.order.pop(index)
        except IndexError as e:
            raise ItemNotFoundError("None") from e

    def exclude(self, item: int | Any) -> bool:
        """Exclude an item or items from the progression.

        Args:
            item: The item(s) to exclude. If int, excludes that many from left.

        Returns:
            True if the item(s) were excluded, False otherwise.

        Raises:
            IndexError: If trying to remove more items than available when int.
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
        for i in (a := self._validate_order(item)):
            while i in self:
                self.remove(i)
        return a not in self

    def __add__(self, other: Any) -> Progression:
        """Add an item or items to the end of the progression.

        Args:
            other: The item(s) to add.

        Returns:
            A new Progression instance with the added item(s).
        """
        _copy = self.copy()
        _copy.include(other)
        return _copy

    def __radd__(self, other: Any) -> Progression:
        """Add this progression to another item or progression.

        Args:
            other: The item or progression to add this progression to.

        Returns:
            A new Progression instance with the combined items.
        """
        if not isinstance(other, Progression):
            _copy = self.copy()
            l_ = SysUtil.copy(_copy.order)
            l_.insert(0, get_lion_id(other))
            _copy.order = l_
            return _copy

        return other + self

    def __setitem__(self, key: int | slice, value: Any) -> None:
        """Set an item or slice of items in the progression.

        Args:
            key: The index or slice to set.
            value: The value(s) to set.
        """
        a = self._validate_order(value)
        self.order[key] = a

    def __iadd__(self, other: Any) -> Progression:
        """Add an item or items to the end of the progression in-place.

        Args:
            other: The item(s) to add.

        Returns:
            This Progression instance with the added item(s).
        """
        return self + other

    def __isub__(self, other: Any) -> Progression:
        """Remove an item or items from the beginning of the progression.

        Args:
            other: The item(s) to remove.

        Returns:
            This Progression instance with the item(s) removed.
        """
        return self - other

    def __sub__(self, other: Any) -> Progression:
        """Remove an item or items from the progression.

        Args:
            other: The item(s) to remove.

        Returns:
            A new Progression instance with the item(s) removed.
        """
        _copy = self.copy()
        _copy.remove(other)
        return _copy

    def __iter__(self) -> Iterator[str]:
        """Iterate over the items in the progression."""
        return iter(self.order)

    def __next__(self) -> str:
        """Return the next item in the progression."""
        return self.popleft()

    def __repr__(self) -> str:
        """Return a string representation of the progression."""
        return f"Progression({self.order})"

    def __str__(self) -> str:
        """Return a string representation of the progression."""
        return f"Progression({self.order})"

    def __reversed__(self) -> Iterator[str]:
        """Return a reversed progression."""
        return reversed(self.order)

    def clear(self) -> None:
        """Clear the progression."""
        self.order = []

    def to_dict(self) -> dict[str, Any]:
        """Convert the progression to a dictionary.

        Returns:
            A dictionary representation of the progression.
        """
        return {
            "ln_id": self.ln_id,
            "created": self.timestamp,
            "order": self.order,
            "name": self.name,
        }

    def __bool__(self) -> bool:
        """Check if the progression is considered True."""
        return True

    def __eq__(self, other: object) -> bool:
        """Compare two Progression instances for equality.

        Args:
            other: The object to compare with.

        Returns:
            True if the progressions are equal, False otherwise.
        """
        if not isinstance(other, Progression):
            return NotImplemented
        return self.order == other.order and self.name == other.name

    def __hash__(self) -> int:
        """Return a hash value for the Progression instance."""
        return hash((tuple(self.order), self.name))


def progression(
    order: list[str] | None = None, name: str | None = None
) -> Progression:
    """Create a new Progression instance.

    Args:
        order: The initial order of items in the progression.
        name: The name of the progression.

    Returns:
        A new Progression instance.
    """
    return Progression(order=order, name=name)