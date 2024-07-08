from __future__ import annotations
from collections.abc import Sequence
from typing import Any, TypeVar, Type, Iterable, AsyncIterable, ClassVar
import asyncio

from pydantic import Field, PrivateAttr
from pydantic.config import ConfigDict

from lion_core.libs import to_list
from lion_core.abc.space import Record, Ordering
from lion_core.abc.element import Element
from lion_core.exceptions import ItemNotFoundError, LionTypeError, LionValueError
from lion_core.util.sys_util import SysUtil
from lion_core.generic.component import Component
from .util import convert_to_lion_object, PileLoader, PileLoaderRegistry

T = TypeVar("T", bound=Element)


class Pile(Component, Record[T]):
    """A flexible, ordered collection of Elements with nested structure support.

    Pile provides a powerful interface for storing, retrieving, and manipulating
    collections of Elements. It supports various access patterns, including
    key-based, index-based, and slice-based access, as well as nested structures.

    Attributes:
        use_obj (bool): Flag to determine if objects should be used directly.
        _pile (dict[str, T]): The internal storage for pile items.
        item_type (set[Type[Element]] | None): Set of allowed types for items.
        order (list[str]): List specifying the order of items in the pile.
    """

    use_obj: bool = Field(
        default=False,
        description="Flag to determine if objects should be used directly.",
    )
    _pile: dict[str, T] = PrivateAttr(default_factory=dict)
    item_type: set[Type[Element]] | None = Field(
        default=None, description="Set of allowed types for items in the pile."
    )
    order: list[str] = Field(
        default_factory=list,
        description="List specifying the order of items in the pile.",
    )
    _loaders: ClassVar[dict[str, Type["PileLoader"]]] = {}
    model_config = ConfigDict(extra="forbid")

    def __init__(
        self,
        items: Any = None,
        item_type: set[Type[Element]] | None = None,
        order: list[str] | None = None,
        use_obj: bool = False,
        **kwargs,
    ):
        """Initialize a Pile instance.

        Args:
            items: Initial items for the pile.
            item_type: Allowed types for items in the pile.
            order: Initial order of items.
            use_obj: Whether to use objects directly.
            **kwargs: Additional keyword arguments for the Component constructor.

        Example:
            >>> from lion_core.abc.element import Element
            >>> class MyElement(Element):
            ...     pass
            >>> pile = Pile({"a": MyElement(), "b": MyElement()}, item_type={MyElement})
            >>> len(pile)
            2
        """
        super().__init__(**kwargs)
        self.use_obj = use_obj
        self._pile = self._validate_pile(items or {})
        self.item_type = self._validate_item_type(item_type)
        self.order = order or list(self._pile.keys())

    def __getitem__(self, key: Any) -> T | Pile[T]:
        """Get item(s) from the pile by key, index, slice, or iterable.

        Args:
            key: The key, index, slice, or iterable of keys/indices.

        Returns:
            The requested item(s) or a new Pile containing the requested items.

        Raises:
            ItemNotFoundError: If the key or index is not found in the pile.

        Examples:
            >>> pile = Pile({"a": Element(), "b": Element(), "c": Element()})
            >>> pile["a"]  # Returns the element with key "a"
            >>> pile[0]  # Returns the first element
            >>> pile[1:3]  # Returns a new Pile with elements at index 1 and 2
            >>> pile[["a", "c"]]  # Returns a new Pile with elements "a" and "c"
            >>> pile[[0, 2]]  # Returns a new Pile with the first and third elements
            >>> pile[slice(0, 2), slice(1, 3)]  # Returns a Pile of Piles for multiple slices
        """
        if isinstance(key, (int, slice)):
            return self._get_by_index_or_slice(key)
        elif isinstance(key, Iterable) and not isinstance(key, str):
            return self._get_by_iterable(key)
        else:
            return self._get_by_key(key)

    def _get_by_key(self, key: Any) -> T:
        """Get item by key."""
        try:
            key = SysUtil.get_lion_id(key)
            return self._pile[key]
        except (ValueError, KeyError):
            raise ItemNotFoundError(f"Key {key} not found in pile.")

    def _get_by_index_or_slice(self, key: int | slice) -> T | Pile[T]:
        """Get item(s) by index or slice."""
        try:
            if isinstance(key, int):
                return self._pile[self.order[key]]
            else:
                _keys = self.order[key]
                return Pile({k: self._pile[k] for k in _keys}, self.item_type, _keys)
        except IndexError:
            raise ItemNotFoundError(f"Index {key} out of range.")

    def _get_by_iterable(self, keys: Iterable) -> Pile[T] | Pile[Pile[T]]:
        """Get items by iterable of keys, indices, or slices.

        If there is more than one slice object in the input, this method returns
        a Pile of Piles. Otherwise, it returns a flat Pile.
        """
        result = {}
        result_order = []
        slice_count = 0

        for k in keys:
            try:
                if isinstance(k, int):
                    k = self.order[k]
                    item = self._get_by_key(k)
                elif isinstance(k, slice):
                    item = self._get_by_index_or_slice(k)
                    slice_count += 1
                    k = f"slice({k.start}:{k.stop}:{k.step})"
                else:
                    item = self._get_by_key(k)

                result[k] = item
                result_order.append(k)
            except ItemNotFoundError:
                continue  # Skip items that are not found

        if slice_count > 1:
            # Return a Pile of Piles for multiple slices
            return Pile(
                {
                    k: (v if isinstance(v, Pile) else Pile({k: v}))
                    for k, v in result.items()
                },
                item_type={Pile},
                order=result_order,
            )
        else:
            # Return a flat Pile
            flat_result = {}
            flat_order = []
            for k in result_order:
                v = result[k]
                if isinstance(v, Pile):
                    flat_result.update(v._pile)
                    flat_order.extend(v.order)
                else:
                    flat_result[k] = v
                    flat_order.append(k)
            return Pile(flat_result, self.item_type, flat_order)

    def __setitem__(self, key: Any, value: T | dict[str, T]) -> None:
        """Set item(s) in the pile.

        Args:
            key: The key, index, slice, or iterable of keys/indices to set items.
            value: The item or dictionary of items to set.

        Raises:
            ValueError: If the number of items doesn't match the specified
                        keys/indices.

        Examples:
            >>> pile = Pile()
            >>> pile["a"] = Element()  # Sets an element with key "a"
            >>> pile[0] = Element()  # Sets an element at the first position
            >>> pile[1:3] = {"b": Element(), "c": Element()}  # Sets elements at positions 1 and 2
            >>> pile[["d", "e"]] = {"d": Element(), "e": Element()}  # Sets elements with keys "d" and "e"
        """
        if isinstance(key, (int, slice)):
            self._set_by_index_or_slice(key, value)
        elif isinstance(key, Iterable) and not isinstance(key, str):
            self._set_by_iterable(key, value)
        else:
            self._set_by_key(key, value)

    def _set_by_key(self, key: Any, value: T) -> None:
        """Set item by key."""
        key = SysUtil.get_lion_id(key)
        self._pile[key] = value
        if key not in self.order:
            self.order.append(key)

    def _set_by_index_or_slice(self, key: int | slice, value: T | dict[str, T]) -> None:
        """Set item(s) by index or slice."""
        if isinstance(key, int):
            if key < 0:
                key = len(self) + key
            if key < 0 or key >= len(self):
                raise IndexError("Pile index out of range")
            existing_key = self.order[key]
            if isinstance(value, dict):
                if len(value) != 1:
                    raise ValueError("Cannot assign multiple items to a single index")
                new_key, new_value = next(iter(value.items()))
            else:
                new_key, new_value = existing_key, value
            self._pile[new_key] = new_value
            self.order[key] = new_key
        else:  # slice
            if isinstance(value, dict):
                items = value
            elif isinstance(value, Pile):
                items = value._pile
            else:
                raise ValueError("Slice assignment expects a dict or Pile")

            slice_range = range(*key.indices(len(self)))
            if len(slice_range) != len(items):
                raise ValueError("Slice assignment length does not match value length")

            for i, (new_key, new_value) in zip(slice_range, items.items()):
                self._pile[new_key] = new_value
                if i < len(self.order):
                    self.order[i] = new_key
                else:
                    self.order.append(new_key)

    def _set_by_iterable(self, keys: Iterable, values: dict[str, T] | Pile[T]) -> None:
        """Set items by iterable of keys or indices."""
        if isinstance(values, Pile):
            values = values._pile
        elif not isinstance(values, dict):
            raise ValueError("Expected a dictionary or Pile for multiple assignments")

        if len(keys) != len(values):
            raise ValueError("Number of keys does not match number of values")

        for k, v in zip(keys, values.values()):
            if isinstance(k, int):
                self._set_by_index_or_slice(k, {next(iter(values.keys())): v})
            else:
                self._set_by_key(k, v)

    def __len__(self) -> int:
        """Get the number of items in the pile.

        Returns:
            The number of items in the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> len(pile)
            2
        """
        return len(self.order)

    def __iter__(self) -> Iterable[T]:
        """Return an iterator over the items in the pile.

        Yields:
            The items in the pile in their specified order.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> for item in pile:
            ...     print(item)  # Prints each element
        """
        for key in self.order:
            yield self._pile[key]

    async def __aiter__(self) -> AsyncIterable[T]:
        """Return an async iterator over the items in the pile.

        Yields:
            The items in the pile in their specified order.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> async for item in pile:
            ...     print(item)  # Prints each element asynchronously
        """
        for key in self.order:
            yield self._pile[key]

    def keys(self) -> Iterable[str]:
        """Get the keys of the pile in their specified order.

        Returns:
            An iterable of keys in the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> list(pile.keys())
            ['a', 'b']
        """
        return self.order

    def values(self) -> Iterable[T]:
        """Get the values of the pile in their specified order.

        Returns:
            An iterable of values in the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> list(pile.values())  # Returns [Element(), Element()]
        """
        return (self._pile[key] for key in self.order)

    def items(self) -> Iterable[tuple[str, T]]:
        """Get the items of the pile as (key, value) pairs in their order.

        Returns:
            An iterable of (key, value) tuples.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> list(pile.items())  # Returns [('a', Element()), ('b', Element())]
        """
        return ((key, self._pile[key]) for key in self.order)

    def get(self, key: Any, default: Any = ...) -> T | None:
        """Get an item from the pile with a default value if not found.

        Args:
            key: The key of the item to get.
            default: The default value to return if the key is not found.

        Returns:
            The item if found, otherwise the default value.

        Raises:
            ItemNotFoundError: If the key is not found and no default is provided.

        Example:
            >>> pile = Pile({"a": Element()})
            >>> pile.get("a")  # Returns Element()
            >>> pile.get("b", None)  # Returns None
        """
        try:
            return self[key]
        except ItemNotFoundError:
            if default is ...:
                raise
            return default

    async def aget(self, key: Any, default: Any = ...) -> T | None:
        """Asynchronously get an item from the pile.

        This method is a coroutine.

        Args:
            key: The key of the item to get.
            default: The default value to return if the key is not found.

        Returns:
            The item if found, otherwise the default value.

        Raises:
            ItemNotFoundError: If the key is not found and no default is provided.

        Example:
            >>> pile = Pile({"a": Element()})
            >>> await pile.aget("a")  # Returns Element()
            >>> await pile.aget("b", None)  # Returns None
        """
        return await asyncio.to_thread(self.get, key, default)

    def pop(self, key: Any) -> T:
        """Remove and return an item from the pile.

        Args:
            key: The key of the item to remove.

        Returns:
            The removed item.

        Raises:
            ItemNotFoundError: If the key is not found in the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> pile.pop("a")  # Returns and removes Element()
            >>> pile.pop("c")  # Raises ItemNotFoundError
        """
        try:
            key = SysUtil.get_lion_id(key)
            item = self._pile.pop(key)
            self.order.remove(key)
            return item
        except (ValueError, KeyError):
            raise ItemNotFoundError(f"Key {key} not found in pile.")

    def pop(self, key: Any) -> T:
        """Remove and return an item from the pile.

        Args:
            key: The key of the item to remove.

        Returns:
            The removed item.

        Raises:
            ItemNotFoundError: If the key is not found in the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> pile.pop("a")  # Returns and removes Element()
            >>> pile.pop("c")  # Raises ItemNotFoundError
        """
        try:
            key = SysUtil.get_lion_id(key)
            item = self._pile.pop(key)
            self.order.remove(key)
            return item
        except (ValueError, KeyError):
            raise ItemNotFoundError(f"Key {key} not found in pile.")

    async def apop(self, key: Any) -> T:
        """Asynchronously remove and return an item from the pile.

        This method is a coroutine.

        Args:
            key: The key of the item to remove.

        Returns:
            The removed item.

        Raises:
            ItemNotFoundError: If the key is not found in the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> await pile.apop("a")  # Returns and removes Element()
            >>> await pile.apop("c")  # Raises ItemNotFoundError
        """
        return await asyncio.to_thread(self.pop, key)

    def remove(self, item: T) -> None:
        """Remove an item from the pile.

        Args:
            item: The item to remove.

        Raises:
            ItemNotFoundError: If the item is not found in the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> element = pile["a"]
            >>> pile.remove(element)  # Removes the element
            >>> pile.remove(element)  # Raises ItemNotFoundError
        """
        key = SysUtil.get_lion_id(item)
        if key in self._pile:
            del self._pile[key]
            self.order.remove(key)
        else:
            raise ItemNotFoundError(f"Item {key} not found in pile.")

    async def aremove(self, item: T) -> None:
        """Asynchronously remove an item from the pile.

        This method is a coroutine.

        Args:
            item: The item to remove.

        Raises:
            ItemNotFoundError: If the item is not found in the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> element = pile["a"]
            >>> await pile.aremove(element)  # Removes the element
            >>> await pile.aremove(element)  # Raises ItemNotFoundError
        """
        await asyncio.to_thread(self.remove, item)

    def exclude(self, item: T) -> bool:
        """Exclude an item from the pile.

        Args:
            item: The item to exclude.

        Returns:
            True if the item was not in the pile or was successfully removed,
            False if an error occurred during removal.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> element = pile["a"]
            >>> pile.exclude(element)  # Returns True
            >>> pile.exclude(Element())  # Returns True (item wasn't in pile)
        """
        key = SysUtil.get_lion_id(item)
        if key not in self._pile:
            return True
        try:
            del self._pile[key]
            self.order.remove(key)
            return True
        except Exception:
            return False

    async def aexclude(self, item: T) -> bool:
        """Asynchronously exclude an item from the pile.

        This method is a coroutine.

        Args:
            item: The item to exclude.

        Returns:
            True if the item was not in the pile or was successfully removed,
            False if an error occurred during removal.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> element = pile["a"]
            >>> await pile.aexclude(element)  # Returns True
            >>> await pile.aexclude(Element())  # Returns True (item wasn't in pile)
        """
        return await asyncio.to_thread(self.exclude, item)

    def include(self, item: T) -> bool:
        """Include an item in the pile.

        Args:
            item: The item to include.

        Returns:
            True if the item was already in the pile or was successfully added,
            False if an error occurred during addition.

        Example:
            >>> pile = Pile()
            >>> element = Element()
            >>> pile.include(element)  # Returns True
            >>> pile.include(element)  # Returns True (item was already in pile)
        """
        key = SysUtil.get_lion_id(item)
        if key in self._pile:
            return True
        try:
            self._pile[key] = item
            self.order.append(key)
            return True
        except Exception:
            return False

    async def ainclude(self, item: T) -> bool:
        """Asynchronously include an item in the pile.

        This method is a coroutine.

        Args:
            item: The item to include.

        Returns:
            True if the item was already in the pile or was successfully added,
            False if an error occurred during addition.

        Example:
            >>> pile = Pile()
            >>> element = Element()
            >>> await pile.ainclude(element)  # Returns True
            >>> await pile.ainclude(element)  # Returns True (item was already in pile)
        """
        return await asyncio.to_thread(self.include, item)

    def clear(self) -> None:
        """Remove all items from the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> pile.clear()
            >>> len(pile)
            0
        """
        self._pile.clear()
        self.order.clear()

    async def aclear(self) -> None:
        """Asynchronously remove all items from the pile.

        This method is a coroutine.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> await pile.aclear()
            >>> len(pile)
            0
        """
        await asyncio.to_thread(self.clear)

    def is_empty(self) -> bool:
        """Check if the pile is empty.

        Returns:
            True if the pile is empty, False otherwise.

        Example:
            >>> pile = Pile()
            >>> pile.is_empty()
            True
            >>> pile["a"] = Element()
            >>> pile.is_empty()
            False
        """
        return len(self.order) == 0

    def size(self) -> int:
        """Get the number of items in the pile.

        Returns:
            The number of items in the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> pile.size()
            2
        """
        return len(self.order)

    def to_dict(self) -> dict[str, Any]:
        """Convert the Pile to a dictionary.

        Returns:
            A dictionary representation of the Pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> pile_dict = pile.to_dict()
            >>> isinstance(pile_dict, dict)
            True
        """
        return {
            "items": {k: v.to_dict() for k, v in self._pile.items()},
            "item_type": (
                [t.__name__ for t in self.item_type] if self.item_type else None
            ),
            "order": self.order,
            "use_obj": self.use_obj,
        }

    @classmethod
    def from_dict(cls: Type[Pile[T]], data: dict[str, Any]) -> Pile[T]:
        """Create a Pile instance from a dictionary.

        Args:
            data: A dictionary containing Pile data.

        Returns:
            A new Pile instance.

        Example:
            >>> pile_data = {
            ...     "items": {"a": {"ln_id": "a"}, "b": {"ln_id": "b"}},
            ...     "item_type": ["Element"],
            ...     "order": ["a", "b"],
            ...     "use_obj": False
            ... }
            >>> pile = Pile.from_dict(pile_data)
            >>> isinstance(pile, Pile)
            True
        """
        items = {}
        for key, item_data in data.get("items", {}).items():
            if isinstance(item_data, dict) and "lion_class" in item_data:
                items[key] = Component.from_dict(item_data)
            else:
                items[key] = item_data

        item_type = None
        if data.get("item_type"):
            item_type = set()
            for type_name in data["item_type"]:
                try:
                    type_class = SysUtil._get_class(type_name)
                    if issubclass(type_class, Element):
                        item_type.add(type_class)
                    else:
                        raise LionTypeError(f"{type_name} is not a subclass of Element")
                except ValueError as e:
                    raise LionTypeError(f"Unable to find class {type_name}: {e}")

        return cls(
            items=items,
            item_type=item_type,
            order=data.get("order"),
            use_obj=data.get("use_obj", False),
        )

    def flatten(self, recursive: bool = True, max_depth: int = None) -> Pile[T]:
        """Recursively flatten a nested Pile into a flat Pile.

        Args:
            recursive: If True, flatten nested Piles recursively.
            max_depth: Maximum depth to flatten. None means no limit.

        Returns:
            A new Pile instance with nested structures flattened.

        Example:
            >>> element1, element2, element3, element4 = Element(), Element(), Element(), Element()
            >>> nested_pile = Pile({
            ...     "a": element1,
            ...     "b": Pile({"c": element2, "d": Pile({"e": element3})}),
            ...     "f": element4
            ... })
            >>> flat_pile = nested_pile.flatten()
            >>> list(flat_pile.keys())  # Returns ['a', 'c', 'e', 'f']
            >>> len(flat_pile)  # Returns 4
        """
        flattened_items = {}
        flattened_order = []

        def _flatten(pile: Pile, prefix: str = "", depth: int = 0):
            for key in pile.order:
                value = pile._pile[key]
                if (
                    isinstance(value, Pile)
                    and recursive
                    and (max_depth is None or depth < max_depth)
                ):
                    _flatten(value, f"{prefix}{key}.", depth + 1)
                else:
                    flat_key = f"{prefix}{key}"
                    flattened_items[flat_key] = value
                    flattened_order.append(flat_key)

        _flatten(self)
        return Pile(flattened_items, item_type=self.item_type, order=flattened_order)

    def _validate_item_type(
        self, value: set[Type[Element]] | None
    ) -> set[Type[Element]] | None:
        """Validate and convert the item_type field."""
        if value is None:
            return None

        value = SysUtil.to_list(value)

        for i in value:
            if not isinstance(i, type) or not issubclass(i, Element):
                raise LionTypeError(
                    "Invalid item type. Expected a subclass of Element."
                )

        if len(value) != len(set(value)):
            raise LionValueError("Detected duplicated item types in item_type.")

        return set(value) if value else None

    def _validate_pile(self, value: Any) -> dict[str, T]:
        """Validate and convert the items to be added to the pile."""
        if value == {}:
            return {}

        if isinstance(value, Element):
            return {value.ln_id: value}

        if self.use_obj:
            if not isinstance(value, list):
                value = [value]
            if isinstance(value[0], (Record, Ordering)):
                return {getattr(i, "ln_id"): i for i in value}

        value = to_list(value, flatten=True, dropna=True)
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

    @classmethod
    def register_loader(cls, key: str, loader: Type["PileLoader"]) -> None:
        """Register a PileLoader for a specific key."""
        cls._loaders[key] = loader

    @classmethod
    def get_loader(cls, key: str) -> Type["PileLoader"]:
        """Get a registered PileLoader by key."""
        if key not in cls._loaders:
            raise KeyError(f"No loader registered for key: {key}")
        return cls._loaders[key]

    @classmethod
    def load(cls, data: Any, loader_key: str | None = None) -> "Pile":
        """
        Load a Pile from the given data using the specified loader.

        If no loader_key is provided, it attempts to use a suitable
        registered loader or falls back to from_dict.

        Args:
            data: The data to load into a Pile.
            loader_key: Optional key to specify which loader to use.

        Returns:
            A new Pile instance.

        Raises:
            LionValueError: If the specified loader can't handle the data.
            LionTypeError: If no suitable loader is found for the data.
        """
        if loader_key:
            loader = cls.get_loader(loader_key)
            if loader.can_load(data):
                return loader.load(data)
            raise LionValueError(f"Loader {loader_key} cannot load the provided data")

        # Try registered loaders
        for loader in cls._loaders.values():
            if loader.can_load(data):
                return loader.load(data)

        # Fallback to from_dict if data is a dict
        if isinstance(data, dict):
            return cls.from_dict(data)

        # If data is iterable, convert items to Lion objects
        if isinstance(data, (list, tuple, set)):
            items = {
                f"item_{i}": convert_to_lion_object(item) for i, item in enumerate(data)
            }
            return cls(items)

        raise LionTypeError(
            f"No suitable loader found for the provided data type: {type(data)}"
        )


def pile(
    data: Any = None,
    loader: PileLoader | str | None = None,
    registry: PileLoaderRegistry | None = None,
    item_type: Type[Element] | set[Type[Element]] | None = None,
    order: list[str] | None = None,
    use_obj: bool = False,
) -> "Pile[T]":
    """
    Create a Pile instance from various sources.

    This function provides a flexible way to create a Pile, supporting
    different input types and various ways to specify loaders.

    Args:
        data: The data to load into the Pile. Can be None, a dictionary,
              an iterable, or any type supported by the provided loader.
        loader: Optional PileLoader object or a string key for a loader.
        registry: Optional PileLoaderRegistry to use or register.
        item_type: Optional type or set of types allowed for items in the Pile.
        order: Optional list specifying the order of items in the Pile.
        use_obj: Flag to determine if objects should be used directly.

    Returns:
        A new Pile instance.

    Raises:
        LionValueError: If the provided loader can't handle the data.
        LionTypeError: If the data type is not supported.
        KeyError: If a loader key is provided but not found in the registry.

    Examples:
        >>> pile()  # Creates an empty Pile
        >>> pile({"a": Element(), "b": Element()})  # Creates a Pile from a dict
        >>> pile([Element(), Element()])  # Creates a Pile from a list
        >>> pile(data=my_dataframe, loader=DataFrameLoader())  # Uses a custom loader
        >>> pile(data=my_dataframe, loader="dataframe")  # Uses a registered loader
        >>> pile(data=my_data, registry=my_registry)  # Uses a custom registry
    """
    from .pile import Pile  # Local import to avoid circular dependency

    if data is None:
        return Pile(item_type=item_type, order=order, use_obj=use_obj)

    # Handle registry
    if registry is not None:
        Pile._loaders.update(registry._loaders)

    # Handle loader
    if isinstance(loader, str):
        if registry is not None and loader in registry._loaders:
            loader_obj = registry._loaders[loader]
        elif loader in Pile._loaders:
            loader_obj = Pile._loaders[loader]
        else:
            raise KeyError(
                f"Loader key '{loader}' not found in registry or Pile loaders"
            )
        Pile.register_loader(loader, loader_obj)
    elif isinstance(loader, PileLoader):
        loader_obj = loader
        # Generate a unique key for this loader if not already registered
        loader_key = next(
            (k for k, v in Pile._loaders.items() if v == loader_obj), None
        )
        if loader_key is None:
            loader_key = f"loader_{len(Pile._loaders)}"
        Pile.register_loader(loader_key, loader_obj)
    else:
        loader_obj = None

    # Load data
    if loader_obj is not None:
        if loader_obj.can_load(data):
            loaded_data = loader_obj.from_obj(data)
        else:
            raise LionValueError("Provided loader cannot load the given data")
    elif isinstance(data, (dict, list, tuple, set)):
        loaded_data = data
    else:
        # If no loader provided and data is not a standard container,
        # treat it as a single item
        loaded_data = [data]

    return Pile(loaded_data, item_type=item_type, order=order, use_obj=use_obj)


# File: lion_core/container/pile.py
