from __future__ import annotations

import contextlib
from typing import Any, Iterator

from pydantic import Field, ConfigDict

from lion_core.libs import to_list
from lion_core.util.sys_util import SysUtil
from lion_core.container.base import Ordering
from lion_core.abc.element import Element
from lion_core.exceptions import ItemNotFoundError
from .util import validate_order, is_str_id, to_list_type


class Progression(Element, Ordering):
    """
    A container of ordered items with various manipulation methods.

    This class provides functionality for managing, accessing, and modifying
    ordered sequences of items. It supports common operations such as appending,
    extending, removing, and accessing items by index or slice. The class
    maintains order using unique identifiers (Lion IDs) for each item.

    Attributes:
        name (str | None): The name of the progression.
        order (list[str]): The ordered list of item identifiers.

    Example:
        >>> prog = Progression(name="My Progression")
        >>> prog.append(item1)
        >>> prog.extend([item2, item3])
        >>> first_item = prog[0]
        >>> sub_prog = prog[1:3]
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
        """Check if item(s) are in the progression."""
        if item is None or not self.order:
            return False

        if isinstance(item, str):
            if is_str_id(item):
                return item in self.order

        # for progression, we have two cases
        # first we check whether the progression.order is a subset of self.order
        if isinstance(item, Ordering) and item.order <= self.order:
            return True

        # if not, we treat progression input as an ordinary element
        if isinstance(item, Element):
            return item.ln_id in self.order

        item = to_list_type(item) if not isinstance(item, list) else item
        return all(i in self for i in item)

    def __list__(self) -> list[str]:
        """Return a copy of the order."""
        return self.order[:]

    def __len__(self) -> int:
        """Get the length of the progression."""
        return len(self.order)

    def __getitem__(self, key: int | slice) -> str | Progression:
        """Get an item or slice of items from the progression."""
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
        """Set an item or slice of items in the progression."""
        a = validate_order(value)
        self.order[key] = a
        self.order = to_list(self.order, flatten=True)

    def __delitem__(self, key: int | slice) -> None:
        """Delete an item or slice of items from the progression."""
        del self.order[key]

    def __iter__(self) -> Iterator[str]:
        """Iterate over the items in the progression."""
        return iter(self.order)

    def __next__(self) -> str:
        """Return the next item in the progression."""
        try:
            return next(iter(self.order))
        except StopIteration:
            raise StopIteration("No more items in the progression")

    def size(self) -> int:
        """Get the size of the progression."""
        return len(self)

    def clear(self) -> None:
        """Clear the progression."""
        self.order.clear()

    def copy(self) -> Progression:
        """Create a deep copy of the progression."""
        return self.model_copy(deep=True)

    def keys(self) -> Iterator[int]:
        """Get the indices of the progression."""
        yield from range(len(self))

    def values(self) -> Iterator[str]:
        """Get the values of the progression."""
        yield from self.order

    def items(self) -> Iterator[tuple[int, str]]:
        """Get the items of the progression as (index, value) pairs."""
        yield from enumerate(self.order)

    def append(self, item: Any) -> None:
        """Append an item to the end of the progression."""
        id_ = SysUtil.get_lion_id(item)
        self.order.extend(id_)

    def pop(self, index: int | None = None) -> str:
        """Remove and return an item from the progression."""
        try:
            if index is None:
                return self.order.pop()
            return self.order.pop(index)
        except IndexError as e:
            raise ItemNotFoundError("None") from e

    def include(self, item: Any) -> bool:
        """Include item(s) in the progression.

        If the item is not already in the progression, it will be added.

        Returns:
            True if the item(s) were included, False if already present.
        """
        if item not in self:
            self.extend(item)
        return item in self

    def exclude(self, item: int | Any) -> bool:
        """Exclude an item or items from the progression."""
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
        """Check if the progression is empty."""
        return not self.order

    def __reverse__(self) -> Iterator[str]:
        """Return a reversed progression."""
        return progression(reversed(self.order), name=self.name)

    def __eq__(self, other: object) -> bool:
        """Compare two Progression instances for equality."""
        if not isinstance(other, Progression):
            return NotImplemented
        return self.order == other.order and self.name == other.name

    def index(self, item: Any, start: int = 0, end: int | None = None) -> int:
        """Return the index of an item in the progression."""
        return self.order.index(SysUtil.get_lion_id(item), start, end)

    def remove(self, item: Any) -> None:
        """Remove the next occurrence of an item from the progression."""
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
        """Remove and return the leftmost item from the progression."""
        try:
            return self.order.pop(0)
        except IndexError as e:
            raise ItemNotFoundError from e

    def extend(self, item: Progression | Any) -> None:
        """Extend the progression from the right with item(s)."""
        if isinstance(item, Progression):
            self.order.extend(item.order)
            return
        order = validate_order(item)
        self.order.extend(order)

    def count(self, item: Any) -> int:
        """Return the number of occurrences of an item in the progression."""
        return self.order.count(SysUtil.get_lion_id(item))

    def __add__(self, other: Any) -> Progression:
        """Add an item or items to the end of the progression."""
        _copy = self.copy()
        _copy.include(other)
        return _copy

    def __radd__(self, other: Any) -> Progression:
        """Add this progression to another item or progression."""
        if not isinstance(other, Progression):
            _copy = self.copy()
            l_: list = SysUtil.copy(_copy.order, deep=True)
            l_.insert(0, SysUtil.get_lion_id(other))
            _copy.order = l_
            return _copy

        return other + self

    def __iadd__(self, other: Any) -> Progression:
        """Add an item to the end of the progression in-place."""
        self.order.append(SysUtil.get_lion_id(other))
        return self

    def __isub__(self, other: Any) -> Progression:
        """Remove an item from the progression in-place."""
        self.remove(other)
        return self

    def __sub__(self, other: Any) -> Progression:
        """Remove an item or items from the progression."""
        _copy = self.copy()
        _copy.remove(other)
        return _copy

    def __repr__(self) -> str:
        """Return a string representation of the progression."""
        return f"Progression({self.order})"

    def __str__(self) -> str:
        """Return a string representation of the progression."""
        if len(a := str(self.order)) > 50:
            a = a[:50] + "..."
        return f"Progression(name={self.name}, size={len(self)}, items={a})"

    def insert(self, index: int, item: Any) -> None:
        """Insert an item at the specified index."""
        self.order.insert(index, SysUtil.get_lion_id(item))


def progression(order: list[str] | None = None, name: str | None = None) -> Progression:
    """Create a new Progression instance.

    Args:
        order: The initial order of items in the progression.
        name: The name of the progression.

    Returns:
        A new Progression instance.
    """
    return Progression(order=order, name=name)


# File: lion_core/container/progression.py
