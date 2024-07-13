"""
Provides the Record class for managing nested data structures in lion-core.

This module implements a flexible container for handling complex, nested
dictionary and list data with an intuitive API for data manipulation.
"""

from typing import Any

from lion_core.libs import nget, ninsert, nset, npop
from lion_core.util.undefined import LN_UNDEFINED
from lion_core.util.sys_util import SysUtil

from lion_core._abc import Container


class Record(Container):
    """
    A container class for managing nested dictionary/list data structures.

    This class provides methods for inserting, retrieving, updating, and
    removing data from nested structures using a list of indices for navigation.

    Attributes:
        _items (dict[str, Any]): The internal dictionary storing the nested data.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize a new Record instance.

        Args:
            **kwargs: Initial key-value pairs to populate the record.
        """
        self._items: dict[str, Any] = kwargs

    def serialize(self, dropna: bool = False) -> dict[str, Any]:
        """
        Serialize the record's data to a dictionary.

        Args:
            dropna: If True, exclude None values from the result.

        Returns:
            A serialized copy of the record's data.
        """
        if dropna:
            return {k: v for k, v in self._items.items() if v is not None}
        return SysUtil.copy(self._items)

    def pop(self, indices: list[str], default: Any = LN_UNDEFINED) -> Any:
        """
        Remove and return an item from the nested structure.

        Args:
            indices: The path to the item to be removed.
            default: The value to return if the item is not found.

        Returns:
            The removed item or the default value.
        """
        return npop(self._items, indices, default)

    def insert(self, indices: list[str], value: Any) -> None:
        """
        Insert a value into the nested structure at the specified indices.

        Args:
            indices: The path where to insert the value.
            value: The value to insert.
        """
        ninsert(self._items, indices, value)

    def set(self, indices: list[str], value: Any) -> None:
        """
        Set a value in the nested structure at the specified indices.

        If the path doesn't exist, it will be created.

        Args:
            indices: The path where to set the value.
            value: The value to set.
        """
        if not self.get(indices):
            self.insert(indices, value)
        else:
            nset(self._items, indices, value)

    def get(self, indices: list[str], default: Any = LN_UNDEFINED) -> Any:
        """
        Get a value from the nested structure at the specified indices.

        Args:
            indices: The path to the value in the nested structure.
            default: The default value to return if the item is not found.

        Returns:
            The value at the specified indices or the default value.
        """
        return nget(self._items, indices, default)

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def items(self):
        return self._items.items()


# File: lion_core/container/record.py
