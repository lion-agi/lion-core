from __future__ import annotations
from typing import Any, TypeVar, Type, Iterable

from pydantic import Field

from lion_core.libs import to_list
from lion_core.util.sys_util import SysUtil
from lion_core.abc.element import Element
from lion_core.exceptions import (
    ItemNotFoundError,
    LionTypeError,
    LionValueError,
    LionIDError,
    LionItemError,
)
from .base import Collective, Container
from .progression import Progression
from .util import to_list_type

T = TypeVar("T", bound=Element)


class Pile(Element, Collective[T]):
    """
    A flexible, ordered collection of Elements that provides both list-like and dictionary-like access.

    The Pile class is a core container in the Lion framework, designed to store and manage
    collections of Element objects. It maintains both the order of items and allows fast
    access by unique identifiers.

    Key features:
    - Maintains order of items while allowing dict-like access
    - Supports type checking of items (optional)
    - Flexible item retrieval (by index, slice, or LionID)
    - Implements common container methods (len, iter, contain)
    - Supports standard operations like update, clear, and flatten

    Attributes:
        use_obj (bool): If True, treat Record and Ordering objects directly.
        pile (dict[str, T]): Internal storage mapping unique identifiers to items.
        item_type (set[Type[Element]] | None): Set of allowed types for items in the pile.
        order (list[str]): List maintaining the order of item identifiers.

    Args:
        items (Any, optional): Initial items to populate the pile.
        item_type (set[Type[Element]] | None, optional): Allowed types for items.
        order (list[str] | None, optional): Initial order of items.
        use_obj (bool, optional): Whether to use objects directly. Defaults to False.

    Examples:
        >>> from lion_core.abc.element import Element
        >>> class MyElement(Element):
        ...     value: int
        >>> p = Pile([MyElement(value=i) for i in range(3)])
        >>> len(p)
        3
        >>> p[0].value
        0
        >>> p[1:].values()
        [MyElement(value=1), MyElement(value=2)]
        >>> 'ln_' in p  # Assuming 'ln_' is the start of a LionID
        True
        >>> p.append(MyElement(value=3))
        >>> p.pop(0).value
        0
        >>> p2 = Pile(item_type={MyElement})
        >>> p2.include(MyElement(value=4))
        True
        >>> p2.include("not an element")
        False  # Raises LionTypeError

    Notes:
        - The Pile class is designed to work with Element subclasses, which must have
          a unique 'ln_id' attribute.
        - When `use_obj` is True, certain objects like Record and Ordering are treated
          directly rather than being decomposed.
        - The class supports both list-like operations (indexing, slicing) and
          dict-like operations (key access) for flexibility.
        - Type checking is performed when `item_type` is specified, ensuring only
          allowed types are added to the Pile.

    Raises:
        LionTypeError: If an item of an invalid type is added when `item_type` is set.
        ItemNotFoundError: When trying to access or remove a non-existent item.
        ValueError: If there's a mismatch between items and provided order.

    See Also:
        Element: The base class for items that can be stored in a Pile.
        Collective: The base class defining the interface for collections in Lion.
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
    order: list[str] = Field(
        default_factory=list,
        description="Progression specifying the order of items in the pile.",
    )

    def __init__(
        self,
        items: Any = None,
        item_type: set[Type[Element]] | None = None,
        order: Progression | None = None,
        use_obj: bool = False,
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
        super().__init__()

        self.use_obj = use_obj or False
        self.pile = self._validate_pile(items or {})
        self.item_type = self._validate_item_type(item_type)

        order = order or list(self.pile.keys())
        if not len(order) == len(self):
            raise LionValueError(
                "The length of the order does not match the length of the pile"
            )
        self.order = order

    def __getitem__(self, key) -> T | "Pile[T]":
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
        try:
            if isinstance(key, (int, slice)):
                # Handle list-like index or slice
                _key = self.order[key]
                _key = [_key] if isinstance(key, int) else _key
                _out = [self.pile.get(i) for i in _key]
                return _out[0] if len(_out) == 1 else pile(_out, self.item_type, _key)
        except IndexError as e:
            raise ItemNotFoundError from e

        keys = to_list_type(key)
        for idx, item in enumerate(keys):
            if isinstance(item, str):
                keys[idx] = item
                continue
            if hasattr(item, "ln_id"):
                keys[idx] = item.ln_id

        if not all(keys):
            raise LionIDError

        try:
            if len(keys) == 1:
                return self.pile.get(keys[0])
            return pile([self.pile.get(i) for i in keys], self.item_type, keys)
        except KeyError as e:
            raise ItemNotFoundError from e

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
        item = self._validate_pile(item)

        if isinstance(key, (int, slice)):
            # Handle list-like index or slice
            try:
                _key = self.order[key]
            except IndexError as e:
                raise e

            if isinstance(_key, str) and len(item) != 1:
                raise ValueError("Cannot assign multiple items to a single item.")

            if isinstance(_key, list) and len(item) != len(_key):
                raise ValueError(
                    "The length of values does not match the length of the slice"
                )

            for k, v in item.items():
                if self.item_type and type(v) not in self.item_type:
                    raise LionTypeError(f"Invalid item type.", self.item_type, type(v))

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
                if SysUtil.get_lion_id(i) not in self.pile:
                    return False
            except LionIDError:
                return False
        return True

    def __len__(self) -> int:
        """Get the number of items in the pile."""
        return len(self.pile)

    def __iter__(self) -> Iterable[T]:
        """Return an iterator over the items in the pile."""
        yield from (self.pile[key] for key in self.order if key in self.pile)

    def keys(self) -> Iterable[str]:
        """Get the keys of the pile in their specified order."""
        return self.order

    def values(self) -> Iterable[T]:
        """Get the values of the pile in their specified order."""
        return (self.pile[key] for key in self.order)

    def items(self) -> Iterable[tuple[str, T]]:
        """Get the items of the pile as (key, value) pairs in their order."""
        return ((key, self.pile[key]) for key in self.order)

    def get(self, key: Any, default=...) -> T | "Pile[T]" | None:
        """
        Retrieve item(s) associated with given key.

        Raises `ItemNotFoundError` if key not found and no default given.
        Returns default if provided and key not found.

        Args:
            key: Key of item(s) to retrieve. Can be single or collection.
            default: Default value if key not found. If not specified
                and key not found, raises `ItemNotFoundError`.

        Returns:
            Retrieved item(s) associated with key. Single items returned
            directly, multiple items in new `Pile`. Returns default if
            provided and key not found.

        Raises:
            ItemNotFoundError: If key not found and no default specified.
        """
        try:
            return self[key]
        except ItemNotFoundError as e:
            if default == ...:
                raise e
            return default

    def pop(self, key: Any, default=...) -> T | "Pile[T]" | None:
        """
        Remove and return item(s) associated with given key.

        Raises `ItemNotFoundError` if key not found and no default given.
        Returns default if provided and key not found.

        Args:
            key: Key of item(s) to remove and return. Can be single key
                or collection of keys.
            default: Default value if key not found. If not specified
                and key not found, raises `ItemNotFoundError`.

        Returns:
            Removed item(s) associated with key. Single items returned
            directly, multiple items in new `Pile`. Returns default if
            provided and key not found.

        Raises:
            ItemNotFoundError: If key not found and no default specified.
        """
        key = to_list_type(key)
        items = []

        for i in key:
            if i not in self:
                if default == ...:
                    raise ItemNotFoundError
                return default

        for i in key:
            _id = SysUtil.get_lion_id(i)
            items.append(self.pile.pop(_id))
            self.order.remove(_id)

        return pile(items) if len(items) > 1 else items[0]

    def remove(self, item: T) -> None:
        """
        Remove an item from the pile.

        Args:
            item: The item to remove.

        Raises:
            ItemNotFoundError: If the item is not found in the pile.
        """
        key = SysUtil.get_lion_id(item)
        if key in self.pile:
            del self.pile[key]
            self.order.remove(key)
        else:
            raise ItemNotFoundError

    def include(self, item: Any) -> bool:
        """
        Include item(s) in pile if not already present.

        Accepts individual items and collections. Adds items if not
        present. Returns `True` if item(s) in pile after operation,
        `False` otherwise.

        Args:
            item: Item(s) to include. Can be single item or collection.

        Returns:
            `True` if item(s) in pile after operation, `False` otherwise.
        """
        item = to_list_type(item)
        if item not in self:
            self[item] = item
        return item in self

    def exclude(self, item: Any) -> bool:
        """
        Exclude item(s) from pile if present.

        Accepts individual items and collections. Removes items if
        present. Returns `True` if item(s) not in pile after operation,
        `False` otherwise.

        Args:
            item: Item(s) to exclude. Can be single item or collection.

        Returns:
            `True` if item(s) not in pile after operation, `False` else.
        """
        item = to_list_type(item)
        for i in item:
            if item in self:
                self.pop(i)
        return item not in self

    def clear(self) -> None:
        """Remove all items from the pile."""
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
        """Check if the pile is empty."""
        return self.order == []

    def size(self) -> int:
        """Get the number of items in the pile."""
        return len(self.order)

    def flatten(self, recursive: bool = True, max_depth: int | None = None) -> Pile[T]:
        """
        Recursively flatten a nested Pile into a flat Pile.

        Args:
            recursive: If True, flatten nested Piles recursively.
            max_depth: Maximum depth to flatten. None means no limit.

        Returns:
            A new Pile instance with nested structures flattened.
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
        return Pile(
            flattened_items,
            item_type=self.item_type,
            order=to_list(flattened_order, flatten=True),
        )

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
            if not issubclass(i, Element):
                raise LionTypeError(
                    "Item type must be a subclass of Element.", Element, type(i)
                )

        if len(value) != len(set(value)):
            raise LionValueError("Detected duplicated item types in item_type.")

        if len(value) > 0:
            return set(value)

    def _validate_pile(self, value: Any) -> dict[str, T]:
        """Validate and convert the items to be added to the pile."""
        if value == {}:
            return {}

        if self.use_obj:
            if not isinstance(value, list):
                value = [value]
            if isinstance(value[0], Container):
                return {getattr(i, "ln_id"): i for i in value}
            if isinstance(value, Element):
                return {value.ln_id: value}

        value = to_list_type(value)
        if self.item_type is not None:
            for i in value:
                if not type(i) in self.item_type:
                    raise LionTypeError(
                        f"Invalid item type in pile. Expected {self.item_type}"
                    )

        if isinstance(value, list):
            if len(value) == 1:
                if isinstance(value[0], dict) and value[0] != {}:
                    k = next(iter(value[0]))
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

    def __iter__(self) -> Iterable[T]:
        """Return an iterator over the items in the pile."""
        yield from (self.pile[key] for key in self.order if key in self.pile)

    def __next__(self):
        try:
            return next(iter(self))
        except StopIteration:
            raise StopIteration("End of pile")

    def __delitem__(self, index) -> None:
        del self[index]

    def append(self, item: T):
        """
        Append item to end of pile.

        Appends item to end of pile. If item is `Pile`, added as single
        item, preserving structure. Only way to add `Pile` into another.
        Other methods assume pile as container only.

        Args:
            item: Item to append. Can be any lion object, including `Pile`.
        """
        self.pile[item.ln_id] = item
        self.order.append(item.ln_id)

    def __list__(self) -> list[T]:
        a = []
        for i in self:
            if not i in a:
                a.append(i)
        return a[:]

    def copy(self):
        return self.model_copy(deep=True)

    def __add__(self, other: T) -> Pile:
        """Create a new pile by including item(s) using `+`.

        Returns a new `Pile` with all items from the current pile plus
        provided item(s). Raises `LionValueError` if item(s) can't be
        included.

        Args:
            other: Item(s) to include. Can be single item or collection.

        Returns:
            New `Pile` with all items from current pile plus item(s).

        Raises:
            LionValueError: If item(s) can't be included.
        """
        _copy = self.copy()
        if _copy.include(other):
            return _copy
        raise LionItemError("Item cannot be included in the pile.")

    def __sub__(self, other) -> Pile:
        """
        Create a new pile by excluding item(s) using `-`.

        Returns a new `Pile` with all items from the current pile except
        provided item(s). Raises `ItemNotFoundError` if item(s) not found.

        Args:
            other: Item(s) to exclude. Can be single item or collection.

        Returns:
            New `Pile` with all items from current pile except item(s).

        Raises:
            ItemNotFoundError: If item(s) not found in pile.
        """
        _copy = self.copy()
        if other not in self:
            raise ItemNotFoundError

        length = len(_copy)
        if not _copy.exclude(other) or len(_copy) == length:
            raise LionItemError("Item cannot be excluded from the pile.")
        return _copy

    def __iadd__(self, other: T) -> Pile:
        """
        Include item(s) in the current pile in place using `+=`.

        Modifies the current pile in-place by including item(s). Returns
        the modified pile.

        Args:
            other: Item(s) to include. Can be single item or collection.
        """
        if self.include(other):
            return self
        raise LionItemError("Item cannot be included in the pile.")

    def __isub__(self, other) -> "Pile":
        """
        Exclude item(s) from the current pile in palce using `-=`.

        Modifies the current pile in-place by excluding item(s). Returns
        the modified pile.

        Args:
            other: Item(s) to exclude. Can be single item or collection.

        Returns:
            Modified pile after excluding item(s).
        """
        self.remove(other)
        return self

    def __radd__(self, other: T) -> "Pile":
        return other + self

    def insert(self, index, item):
        """
        Insert item(s) at specific position.

        Inserts item(s) at specified index. Index must be integer.
        Raises `IndexError` if index out of range.

        Args:
            index: Index to insert item(s). Must be integer.
            item: Item(s) to insert. Can be single item or collection.

        Raises:
            ValueError: If index not an integer.
            IndexError: If index out of range.
        """
        if not isinstance(index, int):
            raise LionTypeError("Index must be an integer.", int, type(index))
        item = self._validate_pile(item)
        for k, v in item.items():
            self.order.insert(index, k)
            self.pile[k] = v


def pile(
    items: Any = None,
    item_type: Type[Element] | set[Type[Element]] | None = None,
    order: list[str] | None = None,
    use_obj: bool = False,
) -> Pile[T]:
    """Create a new Pile instance."""
    return Pile(items, item_type, order, use_obj)
