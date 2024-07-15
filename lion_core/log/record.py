"""
Provides the Record class for managing nested data structures in lion-core.

This module implements a flexible container for handling complex, nested
dictionary and list data with an intuitive API for data manipulation.
"""

from typing import Any, Iterator
from pydantic import Field, BaseModel
from lion_core.libs import (
    nget,
    ninsert,
    nset,
    npop,
    get_flattened_keys,
    flatten,)
from lion_core.abc import MutableRecord
from lion_core.sys_util import LN_UNDEFINED



class RecordContent(BaseModel):
    """
    A Pydantic model for the content of a Record.
    """








class Record(MutableRecord):
    """
    A container class for managing nested dictionary/list data structures.

    This class provides methods for inserting, retrieving, updating, and
    removing data from nested structures using a list of indices for navigation.

    Attributes:
        content (dict[str, Any]): The internal dictionary storing the nested data.
    """
    content: dict[str, Any] = Field(default_factory=dict)
    

    def pop(self, indices: list[str], default: Any = LN_UNDEFINED) -> Any:
        """
        Remove and return an item from the nested structure.

        Args:
            indices: The path to the item to be removed.
            default: The value to return if the item is not found.

        Returns:
            The removed item or the default value.
        """
        return npop(self.content, indices, default)

    def insert(self, indices: list[str], value: Any) -> None:
        """
        Insert a value into the nested structure at the specified indices.

        Args:
            indices: The path where to insert the value.
            value: The value to insert.
        """
        ninsert(self.content, indices, value)

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
            nset(self.content, indices, value)

    def get(self, indices: list[str], default: Any = LN_UNDEFINED) -> Any:
        """
        Get a value from the nested structure at the specified indices.

        Args:
            indices: The path to the value in the nested structure.
            default: The default value to return if the item is not found.

        Returns:
            The value at the specified indices or the default value.
        """
        return nget(self.content, indices, default)

    def keys(self, flat: bool = False) -> Iterator[str]:
        """
        Get the keys of the Record.

        Args:
            flat: If True, return flattened keys.

        Returns:
            An iterator of keys.
        """
        if flat:
            return get_flattened_keys(self.content)
        return iter(self.content.keys())

    def values(self, flat: bool = False) -> Iterator[Any]:
        """
        Get the values of the Record.

        Args:
            flat: If True, return flattened values.

        Returns:
            An iterator of values.
        """
        if flat:
            return (v for v in flatten(self.content).values())
        return iter(self.content.values())

    def items(self, flat: bool = False) -> Iterator[tuple[str, Any]]:
        """
        Get the items of the Record.

        Args:
            flat: If True, return flattened items.

        Returns:
            An iterator of (key, value) pairs.
        """
        if flat:
            return ((k, v) for k, v in flatten(self.content).items())
        return iter(self.content.items())


# File: lion_core/container/record.py
