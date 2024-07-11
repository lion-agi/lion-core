from __future__ import annotations
import asyncio
from collections.abc import Iterable
from typing import Any, TypeVar, Type, AsyncIterable

from pydantic import Field

from lion_core.container.base import Collective, Ordering
from lion_core.abc.element import Element
from lion_core.exceptions import ItemNotFoundError, LionItemError, LionTypeError, LionValueError
from lion_core.util.sys_util import SysUtil
from lion_core.generic.component import Component
from .progression import Progression
from .util import PileLoader, PileLoaderRegistry, convert_to_lion_object, to_list_type

T = TypeVar("T", bound=Element)

class Pile(Component, Collective[T]):
    """
    A flexible, ordered collection of Elements.

    Attributes:
        use_obj (bool): If True, treat Record and Ordering as objects.
        pile (dict[str, T]): Maps unique identifiers to items.
        item_type (set[Type[Element]] | None): Allowed item types.
        order (Progression): Order of item identifiers.
    """

    use_obj: bool = Field(
        default=False,
        description="Flag to determine if objects should be used directly.",
    )
    pile: dict[str, T] = Field(default_factory=dict)
    item_type: set[Type[Element]] | None = Field(
        default=None,
        description="Set of allowed types for items in the pile.",
    )
    order: Progression = Field(
        default_factory=Progression,
        description="Progression specifying the order of items in the pile.",
    )

    def __init__(
        self,
        items: Any = None,
        item_type: set[Type[Element]] | None = None,
        order: Progression | None = None,
        use_obj: bool = False,
        **kwargs
    ):
        """
        Initialize a Pile instance.

        Args:
            items: Initial items for the pile.
            item_type: Allowed types for items in the pile.
            order: Initial order of items (as Progression).
            use_obj: Whether to use objects directly.
            **kwargs: Additional keyword arguments for the Component constructor.
        """
        super().__init__(**kwargs)
        self.use_obj = use_obj
        self.item_type = self._validate_item_type(item_type)
        self.pile = self._validate_pile(items or {})
        self.order = order or Progression(list(self.pile.keys()))

    def __getitem__(self, key: Any) -> T | Pile[T]:
        """
        Retrieve items from the pile using a key.

        Args:
            key: Key to retrieve items.

        Returns:
            The requested item(s).

        Raises:
            LionItemError: If requested item(s) not found.
            LionTypeError: If provided key is invalid.
        """
        try:
            if isinstance(key, (int, slice)):
                _key = self.order[key]
                _key = [_key] if isinstance(key, int) else _key
                _out = [self.pile.get(i) for i in _key]
                return _out[0] if len(_out) == 1 else Pile(_out, self.item_type, _key)
        except IndexError as e:
            raise LionItemError(key) from e

        keys = to_list_type(key)
        for idx, item in enumerate(keys):
            if isinstance(item, str):
                keys[idx] = item
            elif hasattr(item, "ln_id"):
                keys[idx] = item.ln_id
            else:
                raise LionTypeError(f"Invalid key type: {type(item)}")

        try:
            if len(keys) == 1:
                return self.pile.get(keys[0])
            return Pile([self.pile.get(i) for i in keys], self.item_type, keys)
        except KeyError as e:
            raise LionItemError(key) from e

    def __setitem__(self, key: Any, item: T | dict[str, T]) -> None:
        """
        Set new values in the pile using various key types.

        Args:
            key: Key to set items. Can be index, slice, or string.
            item: Item(s) to set. Can be single item or collection.

        Raises:
            ValueError: Length mismatch or multiple items to single key.
            LionTypeError: Item type doesn't match allowed types.
        """
        item = self._validate_pile(item)

        if isinstance(key, (int, slice)):
            try:
                _key = self.order[key]
            except IndexError as e:
                raise LionItemError("Index out of range") from e

            if isinstance(_key, str) and len(item) != 1:
                raise ValueError("Cannot assign multiple items to a single item.")

            if isinstance(_key, list) and len(item) != len(_key):
                raise ValueError(
                    "The length of values does not match the length of the slice"
                )

            for k, v in item.items():
                if self.item_type and type(v) not in self.item_type:
                    raise LionTypeError(f"Invalid item type. Expected {self.item_type}")

                self.pile[k] = v
                self.order[key] = k
                self.pile.pop(_key)
            return

        if len(to_list_type(key)) != len(item):
            raise ValueError("The length of keys does not match the length of values")

        self.pile.update(item)
        self.order.extend(item.keys())

    def __contains__(self, item: Any) -> bool:
        """
        Check if item(s) are present in the pile.

        Args:
            item: Item(s) to check. Can be single item or collection.

        Returns:
            bool: True if all items are found, False otherwise.
        """
        item = to_list_type(item)
        for i in item:
            try:
                a = i if isinstance(i, str) else SysUtil.get_lion_id(i)
                if a not in self.pile:
                    return False
            except Exception:
                return False
        return True

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
            yield self.pile[key]

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
        return (self.pile[key] for key in self.order)

    def items(self) -> Iterable[tuple[str, T]]:
        """Get the items of the pile as (key, value) pairs in their order.

        Returns:
            An iterable of (key, value) tuples.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> list(pile.items())  # Returns [('a', Element()), ('b', Element())]
        """
        return ((key, self.pile[key]) for key in self.order)

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
            item = self.pile.pop(key)
            self.order.remove(key)
            return item
        except (ValueError, KeyError):
            raise ItemNotFoundError(f"Key {key} not found in pile.")


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
        if key in self.pile:
            del self.pile[key]
            self.order.remove(key)
        else:
            raise ItemNotFoundError(f"Item {key} not found in pile.")

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
        if key not in self.pile:
            return True
        try:
            del self.pile[key]
            self.order.remove(key)
            return True
        except Exception:
            return False

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
        if key in self.pile:
            return True
        try:
            self.pile[key] = item
            self.order.append(key)
            return True
        except Exception:
            return False

    def clear(self) -> None:
        """Remove all items from the pile.

        Example:
            >>> pile = Pile({"a": Element(), "b": Element()})
            >>> pile.clear()
            >>> len(pile)
            0
        """
        self.pile.clear()
        self.order.clear()

    def update(self, other: Any):
        """
        Update pile with another collection of items.

        Accepts `Pile` or any iterable. Provided items added to current
        pile, overwriting existing items with same keys.

        Args:
            other: Collection to update with. Can be any LionIDable
        """
        p = pile(other)
        self[p] = p

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
            "items": {k: v.to_dict() for k, v in self.pile.items()},
            "item_type": (
                [t.__name__ for t in self.item_type] if self.item_type else None
            ),
            "order": self.order,
            "use_obj": self.use_obj,
        }
        
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
                value = pile.pile[key]
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
            if isinstance(value[0], (Collective, Ordering)):
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

    def __str__(self) -> str:
        return f"Pile({len(self)})"

    def __repr__(self) -> str:
        length = len(self)
        if length == 0:
            return "Pile()"
        elif length == 1:
            return f"Pile({next(iter(self.pile.values())).__repr__()})"
        else:
            return f"Pile({length})"

def pile(
    items: Any = None,
    item_type: Type[Element] | set[Type[Element]] | None = None,
    order: list[str] | None = None,
    use_obj: bool = False,
) -> "Pile[T]":
    
    return Pile(items, item_type, order, use_obj)
    
    
# File: lion_core/container/pile.py
