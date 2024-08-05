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

import asyncio
from typing import Any, TypeVar, Type, Iterable, override, Generic, AsyncIterator

from pydantic import Field, field_serializer

from lion_core.abc._characteristic import Observable
from lion_core.abc._space import Collective
from lion_core.sys_utils import SysUtil
from lion_core.generic.component import Element
from lion_core.exceptions import (
    ItemNotFoundError,
    LionTypeError,
    LionValueError,
    ItemExistsError,
)
from lion_core.generic.progression import Progression, prog
from lion_core.generic.utils import to_list_type, validate_order
from lion_core.setting import LN_UNDEFINED

T = TypeVar("T", bound=Observable)


class Pile(Element, Collective, Generic[T]):
    """
    A flexible, ordered collection of Elements with list and dict-like access.

    The Pile class is a core container in the Lion framework, designed to store
    and manage collections of Element objects. It maintains both the order of
    items and allows fast access by unique identifiers.

    Attributes:
        pile_ (dict[str, T]): Internal storage mapping identifiers to items.
        item_type (set[Type[Element]] | None): Set of allowed item types.
        order (list[str]): List maintaining the order of item identifiers.
    """

    pile_: dict[str, T] = Field(default_factory=dict)
    item_type: set[Type[Observable]] | None = Field(
        default=None,
        description="Set of allowed types for items in the pile.",
        exclude=True,
    )
    order: Progression = Field(
        default_factory=prog,
        description="Progression specifying the order of items in the pile.",
        exclude=True,
    )
    strict: bool = Field(
        default=False,
        description="Specify if enforce a strict type check if item_type is defined",
    )

    @override
    def __init__(
        self,
        items: Any = None,
        item_type: set[Type[Observable]] | None = None,
        order: Progression | list | None = None,
        strict: bool = False,
        **kwargs,
    ):
        """
        Initialize a Pile instance.

        Args:
            items: Initial items for the pile.
            item_type: Allowed types for items in the pile.
            order: Initial order of items (as Progression).
        """
        _config = {}
        if "ln_id" in kwargs:
            _config["ln_id"] = kwargs["ln_id"]
        if "created" in kwargs:
            _config["created"] = kwargs["created"]

        super().__init__(**_config)
        self.strict = strict
        self.item_type = self._validate_item_type(item_type)
        self.pile_ = self._validate_pile(items or kwargs.get("pile_", {}))
        self.order = self._validate_order(order)

    def __getitem__(self, key) -> T | "Pile":
        """
        Retrieve items from the pile using a key.

        Supports multiple types of key access:
        - By index or slice (list-like access)
        - By LionID (dictionary-like access)
        - By other complex types if item is of LionIDable

        Args:
            key: Key to retrieve items.

        Returns:
            The requested item(s). Single items returned directly,
            multiple items returned in a new `Pile` instance.

        Raises:
            ItemNotFoundError: If requested item(s) not found.
            LionTypeError: If provided key is invalid.
        """
        if key is None:
            raise ValueError("getitem key not provided.")
        if isinstance(key, int):
            try:
                result_id = self.order[key]
                return self.pile_[result_id]
            except Exception as e:
                raise ItemNotFoundError(f"index {key}. Error: {e}")

        elif isinstance(key, slice):
            try:
                result_ids = self.order[key]
                result = []
                for i in result_ids:
                    result.append(self.pile_[i])
                return Pile(items=result, item_type=self.item_type)
            except Exception as e:
                raise ItemNotFoundError(f"index {key}. Error: {e}")

        elif isinstance(key, str):
            try:
                return self.pile_[key]
            except Exception as e:
                raise ItemNotFoundError(f"key {key}. Error: {e}")

        else:
            key = to_list_type(key)
            result = []
            try:
                for k in key:
                    result_id = SysUtil.get_id(k)
                    result.append(self.pile_[result_id])

                if len(result) == 0:
                    raise ItemNotFoundError(f"key {key} item not found")
                if len(result) == 1:
                    return result[0]
                else:
                    return Pile(items=result, item_type=self.item_type)
            except Exception as e:
                raise ItemNotFoundError(f"Key {key}. Error:{e}")

    def __setitem__(self, key, item) -> None:
        """
        Set new values in the pile using various key types.

        Handles single/multiple assignments, ensures type consistency.
        Supports index/slice, LionID, and LionIDable key access.

        Args:
            key: Key to set items. Can be index, slice, LionID, LionIDable.
            item: Item(s) to set. Can be single item or collection.

        Raises:
            ValueError: Length mismatch or multiple items to single key.
            LionTypeError: Item type doesn't match allowed types.
        """
        item_dict = self._validate_pile(item)

        item_order = []
        for i in item_dict.keys():
            if i in self.order:
                raise ItemExistsError(f"item {i} already exists in the pile")
            item_order.append(i)
        if isinstance(key, int | slice):
            try:
                delete_order = (
                    list(self.order[key])
                    if isinstance(self.order[key], Progression)
                    else [self.order[key]]
                )
                self.order[key] = item_order
                for i in delete_order:
                    self.pile_.pop(i)
                self.pile_.update(item_dict)
            except Exception as e:
                raise ValueError(f"Failed to set pile. Error: {e}")
        else:
            key = to_list_type(key)
            if len(key) != len(item_order):
                raise KeyError(f"Invalid key {key}. Key and item does not match.")
            for k in key:
                if SysUtil.get_id(k) not in item_order:
                    raise KeyError(
                        f"Invalid key {SysUtil.get_id(k)}. Key and item does not match."
                    )
            self.order += key
            self.pile_.update(item_dict)

    def __contains__(self, item: Any) -> bool:
        """
        Check if item(s) are present in the pile.

        Args:
            item: Item(s) to check. Can be single item or collection.

        Returns:
            bool: True if all items are found, False otherwise.
        """
        return item in self.order

    @override
    def __len__(self) -> int:
        """
        Get the number of items in the pile.

        Returns:
            int: The number of items in the pile.
        """
        return len(self.pile_)

    def __iter__(self) -> Iterable:
        """
        Return an iterator over the items in the pile.

        Yields:
            The items in the pile in their specified order.
        """

        yield from (self.pile_[key] for key in self.order)

    def keys(self) -> list:
        """
        Get the keys of the pile in their specified order.

        Returns:
            An iterable of keys (LionIDs) in the pile.
        """
        return list(self.order)

    def values(self) -> list:
        """
        Get the values of the pile in their specified order.

        Returns:
            An iterable of values (Elements) in the pile.
        """
        return [self.pile_[key] for key in self.order]

    def items(self) -> list[tuple[str, T]]:
        """
        Get the items of the pile as (key, value) pairs in their order.

        Returns:
            An iterable of (key, value) pairs.
        """
        return [(key, self.pile_[key]) for key in self.order]

    def get(self, key: Any, default=LN_UNDEFINED) -> T | "Pile" | None:
        """
        Retrieve item(s) associated with given key.

        Args:
            key: Key of item(s) to retrieve. Can be single or collection.
            default: Default value if key not found.

        Returns:
            Retrieved item(s) or default if key not found.

        Raises:
            ItemNotFoundError: If key not found and no default specified.
        """
        if isinstance(key, int | slice):
            try:
                return self[key]
            except Exception as e:
                if default is LN_UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default
        else:
            check = None
            if isinstance(key, list):
                check = True
                for i in key:
                    if type(i) is not int:
                        check = False
                        break
            try:
                if not check:
                    key = validate_order(key)
                result = []
                for k in key:
                    result.append(self[k])
                if len(result) == 0:
                    raise ItemNotFoundError(f"key {key} item not found")
                if len(result) == 1:
                    return result[0]
                else:
                    return Pile(items=result, item_type=self.item_type)
            except Exception as e:
                if default is LN_UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default

    def pop(self, key: Any, default=LN_UNDEFINED) -> T | "Pile" | None:
        """
        Remove and return item(s) associated with given key.

        Args:
            key: Key of item(s) to remove. Can be single or collection.
            default: Default value if key not found.

        Returns:
            Removed item(s) or default if key not found.

        Raises:
            ItemNotFoundError: If key not found and no default specified.
        """
        if isinstance(key, int | slice):
            try:
                pop_items = self.order[key]
                pop_items = [pop_items] if isinstance(pop_items, str) else pop_items
                result = []
                for i in pop_items:
                    self.order.remove(i)
                    result.append(self.pile_.pop(i))
                result = (
                    Pile(items=result, item_type=self.item_type)
                    if len(result) > 1
                    else result[0]
                )
                return result
            except Exception as e:
                if default is LN_UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default
        else:
            try:
                key = validate_order(key)
                result = []
                for k in key:
                    self.order.remove(k)
                    result.append(self.pile_.pop(k))
                if len(result) == 0:
                    raise ItemNotFoundError(f"key {key} item not found")
                elif len(result) == 1:
                    return result[0]
                else:
                    return Pile(items=result, item_type=self.item_type, order=key)
            except Exception as e:
                if default is LN_UNDEFINED:
                    raise ItemNotFoundError(f"Item not found. Error: {e}")
                return default

    def remove(self, item: T) -> None:
        """
        Remove an item from the pile.

        Args:
            item: The item to remove.

        Raises:
            ItemNotFoundError: If the item is not found in the pile.
        """
        if item in self:
            self.pop(item)
            return
        raise ItemNotFoundError(f"{item}")

    def include(self, item: Any):
        """
        Include item(s) in pile if not already present.

        Args:
            item: Item(s) to include. Can be single item or collection.
        """
        item_dict = self._validate_pile(item)

        item_order = []
        for i in item_dict.keys():
            if i not in self.order:
                item_order.append(i)

        self.order.append(item_order)
        self.pile_.update(item_dict)

    def exclude(self, item: Any):
        """
        Exclude item(s) from pile if present.

        Args:
            item: Item(s) to exclude. Can be single item or collection.
        """
        item = to_list_type(item)
        exclude_list = []
        for i in item:
            if i in self:
                exclude_list.append(i)
        if exclude_list:
            self.pop(exclude_list)

    def clear(self) -> None:
        """Remove all items from the pile."""
        self.pile_.clear()
        self.order.clear()

    def update(self, other: Any):
        """
        Update pile with another collection of items.

        Args:
            other: Collection to update with. Can be any LionIDable.
        """
        self.include(other)

    def is_empty(self) -> bool:
        """
        Check if the pile is empty.

        Returns:
            bool: True if the pile is empty, False otherwise.
        """
        return len(self.order) == 0

    def size(self) -> int:
        """
        Get the number of items in the pile.

        Returns:
            int: The number of items in the pile.
        """
        return len(self.order)

    def _validate_item_type(self, value):
        """
        Validate the item type for the pile.

        Ensures that the provided item type is a subclass of Element or iModel.
        Raises an error if the validation fails.

        Args:
            value: The item type to validate. Can be a single type or a list of types.

        Returns:
            set: A set of validated item types.

        Raises:
            LionTypeError: If an invalid item type is provided.
            LionValueError: If duplicate item types are detected.
        """
        if value is None:
            return None

        value = to_list_type(value)

        for i in value:
            if not issubclass(i, Observable):
                raise LionTypeError(
                    "Item type must be a subclass of Observable.", Observable, type(i)
                )

        if len(value) != len(set(value)):
            raise LionValueError("Detected duplicated item types in item_type.")

        if len(value) > 0:
            return set(value)

    def _validate_pile(self, value: Any) -> dict[str, T]:
        """Validate and convert the items to be added to the pile."""
        if not value:
            return {}

        value = to_list_type(value)

        result = {}
        for i in value:
            if self.item_type:
                if self.strict:
                    if type(i) not in self.item_type:
                        raise LionTypeError(
                            f"Invalid item type in pile. Expected {self.item_type}"
                        )
                else:
                    if not any(issubclass(type(i), t) for t in self.item_type):
                        raise LionTypeError(
                            f"Invalid item type in pile. Expected {self.item_type} or the subclasses"
                        )
            else:
                if not isinstance(i, Observable):
                    raise LionValueError(f"Invalid pile item {i}")

            result[i.ln_id] = i

        return result

    def _validate_order(self, value: Progression):
        if not value:
            return Progression(order=list(self.pile_.keys()))

        if isinstance(value, Progression):
            value = list(value)
        else:
            value = to_list_type(value)

        value_set = set(value)
        if len(value_set) != len(value):
            raise LionValueError("There are duplicate elements in the order")
        if len(value_set) != len(self.pile_.keys()):
            raise LionValueError(
                "The length of the order does not match the length of the pile"
            )

        for i in value_set:
            if SysUtil.get_id(i) not in self.pile_.keys():
                raise LionValueError(
                    f"The order does not match the pile. {i} not found in the pile."
                )

        return Progression(order=value)

    @override
    def __str__(self) -> str:
        return f"Pile({len(self)})"

    @override
    def __repr__(self) -> str:
        length = len(self)
        if length == 0:
            return "Pile()"
        elif length == 1:
            return f"Pile({next(iter(self.pile_.values())).__repr__()})"
        else:
            return f"Pile({length})"

    def __next__(self):
        try:
            return next(iter(self))
        except StopIteration:
            raise StopIteration("End of pile")

    def append(self, item: T):
        """
        Append item to end of pile.

        Args:
            item: Item to append. Can be any lion object, including `Pile`.
        """
        self.update(item)

    def __list__(self) -> list:
        """
        Convert the pile to a list of unique items.

        Returns:
            list: A list containing unique items from the pile.
        """
        return self.values()

    def __add__(self, other: T) -> "Pile":
        """
        Create a new pile by including item(s) using `+`.

        Args:
            other: Item(s) to include. Can be single item or collection.

        Returns:
            Pile: New Pile with all items from current pile plus item(s).

        Raises:
            LionItemError: If item(s) can't be included.
        """
        result = Pile(items=self.values(), item_type=self.item_type, order=self.order)
        result.include(other)
        return result

    def __sub__(self, other) -> "Pile":
        """
        Create a new pile by excluding item(s) using `-`.

        Args:
            other: Item(s) to exclude. Can be single item or collection.

        Returns:
            Pile: New Pile with all items from current pile except item(s).

        Raises:
            ItemNotFoundError: If item(s) not found in pile.
        """
        result = Pile(items=self.values(), item_type=self.item_type, order=self.order)
        result.pop(other)
        return result

    def __iadd__(self, other: T) -> "Pile":
        """
        Include item(s) in the current pile in place using `+=`.

        Args:
            other: Item(s) to include. Can be single item or collection.

        Returns:
            Pile: The modified pile.
        """
        self.include(other)
        return self

    def __isub__(self, other) -> "Pile":
        """
        Exclude item(s) from the current pile in place using `-=`.

        Args:
            other: Item(s) to exclude. Can be single item or collection.

        Returns:
            Pile: The modified pile.
        """
        result = Pile(items=self.values(), item_type=self.item_type, order=self.order)
        result.pop(other)
        self.remove(other)
        return self

    def __radd__(self, other: T) -> "Pile":
        return self + other

    def insert(self, index, item):
        """
        Insert item(s) at specific position.

        Args:
            index: Index to insert item(s). Must be integer.
            item: Item(s) to insert. Can be single item or collection.

        Raises:
            ValueError: If index not an integer.
            IndexError: If index out of range.
        """
        item_dict = self._validate_pile(item)

        item_order = []
        for i in item_dict.keys():
            if i in self.order:
                raise ItemExistsError(f"item {i} already exists in the pile")
            item_order.append(i)
        self.order.insert(index, item_order)
        self.pile_.update(item_dict)

    @override
    def __bool__(self) -> bool:
        return not self.is_empty()

    @field_serializer("pile_")
    def _(self, value):
        return [i.to_dict() for i in value.values()]

    @classmethod
    def from_dict(cls, data) -> T:
        items = data.pop("pile_", [])
        items = [Element.from_dict(i) for i in items]
        return cls(items=items, **data)

    def __aiter__(self) -> AsyncIterator[T]:
        """
        Return an asynchronous iterator over the items in the pile.

        Returns:
            AsyncIterator[T]: An asynchronous iterator over the pile's items.
        """
        return self.AsyncPileIterator(self)

    async def __anext__(self) -> T:
        """
        Return the next item in the pile asynchronously.

        Returns:
            T: The next item in the pile.

        Raises:
            StopAsyncIteration: When there are no more items in the pile.
        """
        try:
            return await anext(self.AsyncPileIterator(self))
        except StopAsyncIteration:
            raise StopAsyncIteration("End of pile")

    class AsyncPileIterator:
        def __init__(self, pile: "Pile[T]"):
            self.pile = pile
            self.index = 0

        def __aiter__(self) -> AsyncIterator[T]:
            return self

        async def __anext__(self) -> T:
            if self.index >= len(self.pile):
                raise StopAsyncIteration
            item = self.pile[self.pile.order[self.index]]
            self.index += 1
            await asyncio.sleep(0)  # Yield control to the event loop
            return item


def pile(
    items: Any = None,
    item_type: Type[Observable] | set[Type[Observable]] | None = None,
    order: list[str] | None = None,
    strict: bool = False,
) -> Pile:
    """
    Create a new Pile instance.

    Args:
        items: Initial items for the pile.
        item_type: Allowed types for items in the pile.
        order: Initial order of items.

    Returns:
        Pile: A new Pile instance.
    """

    return Pile(items=items, item_type=item_type, order=order, strict=strict)
