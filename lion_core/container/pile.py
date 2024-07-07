"""
Pile Module

This module defines the Pile class, a collection of components with ordering and type checking.
It provides functionality for managing, accessing, and manipulating collections of Component objects.
"""

from collections.abc import Iterable
from typing import Any, Generic, Type, TypeVar, Optional, List, Dict, Union

import pandas as pd
from pydantic import Field, field_validator

from lion_core.libs import to_df
from ..abc import (
    AbstractElement,
    ItemNotFoundError,
    LionTypeError,
    LionValueError,
    Ordering,
    Record,
)
from ..element.component import Component, Element
from ..primitive.util import get_lion_id, is_same_dtype, to_list_type, validate_order

T = TypeVar("T", bound=Element)


class Pile(Element, Record, Generic[T]):
    """
    A collection of components with ordering and type checking.

    The Pile class extends Component and Record, providing a flexible container
    for managing collections of Component objects. It supports type checking,
    custom ordering, and various methods for accessing and manipulating the
    contained items.

    Attributes:
        use_obj (bool): Whether to use objects directly.
        pile (Dict[str, T]): The main storage for items in the Pile.
        item_type (Optional[Set[Type[AbstractElement]]]): Allowed types for items in the pile.
        name (Optional[str]): Optional name for the Pile.
        order (List[str]): List maintaining the order of items in the Pile.
    """

    use_obj: bool = False
    pile: Dict[str, T] = Field(default_factory=dict)
    item_type: Optional[set[Type[AbstractElement]]] = Field(default=None)
    name: Optional[str] = None
    order: List[str] = Field(default_factory=list)

    def __init__(
        self,
        items: Optional[Dict[str, T]] = None,
        item_type: Optional[set[Type[AbstractElement]]] = None,
        order: Optional[List[str]] = None,
        use_obj: Optional[bool] = None,
    ):
        """
        Initialize a Pile instance.

        Args:
            items: Initial items for the pile.
            item_type: Allowed types for items in the pile.
            order: Initial order of items.
            use_obj: Whether to use objects directly.

        Raises:
            ValueError: If the length of the order does not match the length of the pile.
        """
        super().__init__()

        self.use_obj = use_obj or False
        self.pile = self._validate_pile(items or {})
        self.item_type = self._validate_item_type(item_type)

        order = order or list(self.pile.keys())
        if len(order) != len(self):
            raise ValueError(
                "The length of the order does not match the length of the pile"
            )
        self.order = order

    def __getitem__(self, key: Any) -> Union[T, "Pile[T]"]:
        """
        Get item(s) from the pile by key.

        Args:
            key: The key to retrieve items. Can be an index, slice, or key.

        Returns:
            The item or a new Pile containing the requested items.

        Raises:
            ItemNotFoundError: If the key is not found in the pile.
        """
        try:
            if isinstance(key, (int, slice)):
                return self._get_by_index_or_slice(key)
            return self._get_by_key(key)
        except (IndexError, KeyError) as e:
            raise ItemNotFoundError(key) from e

    def _get_by_index_or_slice(self, key: Union[int, slice]) -> Union[T, "Pile[T]"]:
        """
        Get item(s) by index or slice.

        Args:
            key: An integer index or slice object.

        Returns:
            The item or a new Pile containing the requested items.
        """
        _key = self.order[key]
        _key = [_key] if isinstance(key, int) else _key
        _out = [self.pile.get(i) for i in _key]
        return _out[0] if len(_out) == 1 else pile(_out, self.item_type, _key)

    def _get_by_key(self, key: Any) -> Union[T, "Pile[T]"]:
        """
        Get item(s) by key.

        Args:
            key: A key or iterable of keys.

        Returns:
            The item or a new Pile containing the requested items.

        Raises:
            LionTypeError: If the key is not a valid LionIDable object.
        """
        keys = to_list_type(key)
        keys = [item.ln_id if hasattr(item, "ln_id") else item for item in keys]

        if not all(keys):
            raise LionTypeError("Invalid item type. Expected LionIDable object(s).")

        if len(keys) == 1:
            return self.pile[keys[0]]
        return pile([self.pile[i] for i in keys], self.item_type, keys)

    def __setitem__(self, key: Any, item: Union[T, Dict[str, T]]) -> None:
        """
        Set item(s) in the pile.

        Args:
            key: The key to set items. Can be an index, slice, or key.
            item: The item or items to set.

        Raises:
            ValueError: If the number of items doesn't match the key.
        """
        item = self._validate_pile(item)

        if isinstance(key, (int, slice)):
            self._set_by_index_or_slice(key, item)
        else:
            self._set_by_key(key, item)

    def _set_by_index_or_slice(
        self, key: Union[int, slice], item: Dict[str, T]
    ) -> None:
        """
        Set item(s) by index or slice.

        Args:
            key: An integer index or slice object.
            item: The item or items to set.

        Raises:
            IndexError: If the index is invalid.
            ValueError: If trying to assign multiple items to a single index.
        """
        try:
            _key = self.order[key]
        except IndexError as e:
            raise IndexError("Invalid index") from e

        if isinstance(_key, str) and len(item) != 1:
            raise ValueError("Cannot assign multiple items to a single item.")

        if isinstance(_key, list) and len(item) != len(_key):
            raise ValueError(
                "The length of values does not match the length of the slice"
            )

        for k, v in item.items():
            self._validate_item_type({k: v})
            self.pile[k] = v
            self.order[key] = k
            self.pile.pop(_key)

    def _set_by_key(self, key: Any, item: Dict[str, T]) -> None:
        """
        Set item(s) by key.

        Args:
            key: A key or iterable of keys.
            item: The item or items to set.

        Raises:
            ValueError: If the number of keys doesn't match the number of items.
        """
        if len(to_list_type(key)) != len(item):
            raise ValueError("The length of keys does not match the length of values")

        self.pile.update(item)
        self.order.extend(item.keys())

    def __contains__(self, item: Any) -> bool:
        """
        Check if an item is in the pile.

        Args:
            item: The item to check for.

        Returns:
            True if the item is in the pile, False otherwise.
        """
        item = to_list_type(item)
        for i in item:
            try:
                a = i if isinstance(i, str) else get_lion_id(i)
                if a not in self.pile:
                    return False
            except Exception:
                return False
        return True

    def pop(self, key: Any, default: Any = ...) -> Union[T, "Pile[T]", None]:
        """
        Remove and return an item from the pile.

        Args:
            key: The key of the item to remove.
            default: The value to return if the key is not found.

        Returns:
            The removed item or a new Pile containing the removed items.

        Raises:
            ItemNotFoundError: If the key is not found and no default is provided.
        """
        key = to_list_type(key)
        items = []

        for i in key:
            if i not in self:
                if default == ...:
                    raise ItemNotFoundError(i)
                return default

        for i in key:
            _id = get_lion_id(i)
            items.append(self.pile.pop(_id))
            self.order.remove(_id)

        return pile(items) if len(items) > 1 else items[0]

    def get(self, key: Any, default: Any = ...) -> Union[T, "Pile[T]", None]:
        """
        Get an item from the pile.

        Args:
            key: The key of the item to get.
            default: The value to return if the key is not found.

        Returns:
            The item or a new Pile containing the requested items.

        Raises:
            ItemNotFoundError: If the key is not found and no default is provided.
        """
        try:
            return self[key]
        except ItemNotFoundError as e:
            if default == ...:
                raise ItemNotFoundError(
                    str(e)[:15] + ".." if len(str(e)) > 15 else str(e)
                )
            return default

    def update(self, other: Any) -> None:
        """
        Update the pile with items from another iterable.

        Args:
            other: The iterable to update from.
        """
        p = pile(other)
        self[p] = p

    def clear(self) -> None:
        """Clear all items from the pile."""
        self.pile.clear()
        self.order.clear()

    def include(self, item: Any) -> bool:
        """
        Include an item in the pile if it's not already present.

        Args:
            item: The item to include.

        Returns:
            True if the item was included, False if it was already present.
        """
        item = to_list_type(item)
        if item not in self:
            self[item] = item
        return item in self

    def exclude(self, item: Any) -> bool:
        """
        Exclude an item from the pile if it's present.

        Args:
            item: The item to exclude.

        Returns:
            True if the item was excluded, False if it wasn't present.
        """
        item = to_list_type(item)
        for i in item:
            if item in self:
                self.pop(i)
        return item not in self

    def is_homogenous(self) -> bool:
        """
        Check if all items in the pile are of the same type.

        Returns:
            True if all items are of the same type, False otherwise.
        """
        return len(self.pile) < 2 or all(is_same_dtype(self.pile.values()))

    def is_empty(self) -> bool:
        """
        Check if the pile is empty.

        Returns:
            True if the pile is empty, False otherwise.
        """
        return not self.pile

    def __iter__(self):
        """
        Return an iterator over the items in the pile.

        Yields:
            The items in the pile in their specified order.
        """
        return iter(self.values())

    def __len__(self) -> int:
        """
        Get the number of items in the pile.

        Returns:
            The number of items in the pile.
        """
        return len(self.pile)

    def __add__(self, other: T) -> "Pile":
        """
        Create a new Pile with the items from this pile and the other item.

        Args:
            other: The item to add.

        Returns:
            A new Pile instance.

        Raises:
            LionValueError: If the item cannot be included in the pile.
        """
        _copy = self.model_copy(deep=True)
        if _copy.include(other):
            return _copy
        raise LionValueError("Item cannot be included in the pile.")

    def __sub__(self, other) -> "Pile":
        """
        Create a new Pile with the items from this pile, excluding the other item.

        Args:
            other: The item to exclude.

        Returns:
            A new Pile instance.

        Raises:
            ItemNotFoundError: If the item is not in the pile.
            LionValueError: If the item cannot be excluded from the pile.
        """
        _copy = self.model_copy(deep=True)
        if other not in self:
            raise ItemNotFoundError("Item not found in the pile.")

        length = len(_copy)
        if not _copy.exclude(other) or len(_copy) == length:
            raise LionValueError("Item cannot be excluded from the pile.")
        return _copy

    def __iadd__(self, other: T) -> "Pile":
        """
        Add an item to this pile in-place.

        Args:
            other: The item to add.

        Returns:
            This Pile instance.
        """
        return self + other

    def __isub__(self, other) -> "Pile":
        """
        Remove an item from this pile in-place.

        Args:
            other: The item to remove.

        Returns:
            This Pile instance.
        """
        return self - other

    def __radd__(self, other: T) -> "Pile":
        """
        Add this pile to another item, creating a new Pile.

        Args:
            other: The item to add this pile to.

        Returns:
            A new Pile instance.
        """
        return other + self

    def size(self) -> int:
        """
        Get the total size of the pile.

        Returns:
            The sum of the lengths of all items in the pile.
        """
        return sum(len(i) for i in self)

    def insert(self, index: int, item: T) -> None:
        """
        Insert an item at a specific index in the pile.

        Args:
            index: The index at which to insert the item.
            item: The item to insert.

        Raises:
            ValueError: If the index is not an integer.
        """
        if not isinstance(index, int):
            raise ValueError("Index must be an integer for pile insertion.")
        item = self._validate_pile(item)
        for k, v in item.items():
            self.order.insert(index, k)
            self.pile[k] = v

    def append(self, item: T) -> None:
        """
        Append an item to the end of the pile.

        Args:
            item: The item to append.
        """
        self.pile[item.ln_id] = item
        self.order.append(item.ln_id)

    def keys(self) -> List[str]:
        """
        Get the keys of the pile in their specified order.

        Returns:
            An iterator over the keys of the pile.
        """
        return self.order

    def values(self) -> Iterable[T]:
        """
        Get the values of the pile in their specified order.

        Yields:
            The values of the pile in order.
        """
        yield from (self.pile.get(i) for i in self.order)

    def items(self) -> Iterable[tuple[str, T]]:
        """
        Get the items of the pile as (key, value) pairs in their specified order.

        Yields:
            Tuples of (key, value) for each item in the pile.
        """
        yield from ((i, self.pile.get(i)) for i in self.order)

    @field_validator("order", mode="before")
    def _validate_order(cls, value):
        """
        Validate the order of items in the pile.

        Args:
            value: The order to validate.

        Returns:
            The validated order.

        Raises:
            ValueError: If the order is invalid.
        """
        return validate_order(value)

    def _validate_item_type(
        self, value: Optional[set[Type[AbstractElement]]]
    ) -> Optional[set[Type[AbstractElement]]]:
        """
        Validate the item type for the pile.

        Args:
            value: The item type to validate.

        Returns:
            The validated item type as a set.

        Raises:
            LionTypeError: If the item type is not a subclass of AbstractElement.
            LionValueError: If there are duplicate item types.
        """
        if value is None:
            return None

        value = to_list_type(value)

        for i in value:
            if not isinstance(i, type) or not issubclass(i, AbstractElement):
                raise LionTypeError(
                    "Invalid item type. Expected a subclass of AbstractElement."
                )

        if len(value) != len(set(value)):
            raise LionValueError("Detected duplicated item types in item_type.")

        return set(value) if value else None

    def _validate_pile(self, value: Any) -> Dict[str, T]:
        """
        Validate the items to be added to the pile.

        Args:
            value: The item or items to validate.

        Returns:
            A dictionary of validated items.

        Raises:
            LionTypeError: If an item doesn't match the specified item_type.
            LionValueError: If the value is invalid for the pile.
        """
        if value == {}:
            return value

        if isinstance(value, Element):
            return {value.ln_id: value}

        if self.use_obj:
            if not isinstance(value, list):
                value = [value]
            if isinstance(value[0], (Record, Ordering)):
                return {getattr(i, "ln_id"): i for i in value}

        value = to_list_type(value)
        if self.item_type is not None:
            for i in value:
                if not isinstance(i, tuple(self.item_type)):
                    raise LionTypeError(
                        f"Invalid item type in pile. Expected {self.item_type}"
                    )

        if isinstance(value, list):
            if len(value) == 1:
                if isinstance(value[0], dict) and value[0] != {}:
                    k = list(value[0].keys())[0]
                    v = value[0][k]
                    return {k: v}

                k = getattr(value[0], "ln_id", None)
                if k:
                    return {k: value[0]}

            return {i.ln_id: i for i in value}

        raise LionValueError("Invalid pile value")

    def to_df(self) -> pd.DataFrame:
        """
        Convert the pile to a pandas DataFrame.

        Returns:
            A pandas DataFrame representation of the pile.
        """
        dicts_ = []
        for i in self.values():
            _dict = i.to_dict()
            if _dict.get("embedding", None):
                _dict["embedding"] = str(_dict.get("embedding"))
            dicts_.append(_dict)
        return to_df(dicts_)

    def to_csv(self, file_name: str, **kwargs) -> None:
        """
        Save the pile to a CSV file.

        Args:
            file_name: The name of the file to save to.
            **kwargs: Additional keyword arguments to pass to pandas to_csv method.
        """
        self.to_df().to_csv(file_name, index=False, **kwargs)

    @classmethod
    def from_csv(cls, file_name: str, **kwargs) -> "Pile[T]":
        """
        Create a Pile instance from a CSV file.

        Args:
            file_name: The name of the CSV file to read from.
            **kwargs: Additional keyword arguments to pass to pandas read_csv method.

        Returns:
            A new Pile instance containing the items from the CSV file.
        """
        df = pd.read_csv(file_name, **kwargs)
        items = [Component.from_dict(i) for _, i in df.iterrows()]
        return cls(items)

    def __list__(self) -> List[T]:
        """
        Convert the pile to a list.

        Returns:
            A list of all values in the pile.
        """
        return list(self.pile.values())

    def __str__(self) -> str:
        """
        Get a string representation of the pile.

        Returns:
            A string representation of the pile's DataFrame.
        """
        return str(self.to_df())

    def __repr__(self) -> str:
        """
        Get a detailed string representation of the pile.

        Returns:
            A detailed string representation of the pile's DataFrame.
        """
        return repr(self.to_df())


def pile(
    items: Optional[Iterable[T]] = None,
    item_type: Optional[set[Type]] = None,
    order: Optional[List[str]] = None,
    use_obj: Optional[bool] = None,
    csv_file: Optional[str] = None,
    df: Optional[pd.DataFrame] = None,
    **kwargs,
) -> Pile[T]:
    """
    Create a Pile instance with various input options.

    This function provides a flexible way to create a Pile instance from
    different types of input data.

    Args:
        items: Initial items for the pile.
        item_type: Allowed types for items in the pile.
        order: Initial order of items.
        use_obj: Whether to use objects directly.
        csv_file: Path to a CSV file to create the pile from.
        df: Pandas DataFrame to create the pile from.
        **kwargs: Additional keyword arguments to pass to Pile constructor or CSV reader.

    Returns:
        A new Pile instance.

    Raises:
        ValueError: If multiple input sources are provided simultaneously.
    """
    if sum(x is not None for x in (items, csv_file, df)) > 1:
        raise ValueError("Only one of items, csv_file, or df should be provided.")

    if csv_file:
        return Pile.from_csv(csv_file, **kwargs)
    if df is not None:
        return Pile.from_df(df)
    return Pile(items, item_type, order, use_obj)
