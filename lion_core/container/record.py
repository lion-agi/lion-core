"""
Provides the Record class for managing nested data structures in lion-core.

This module implements a flexible container for handling complex, nested
dictionary and list data with an intuitive API for data manipulation.
"""

from typing import Any, Iterator

from pydantic import BaseModel, Field, model_serializer

from lion_core.abc import Container
from lion_core.libs import (
    nget,
    ninsert,
    nset,
    npop,
    get_flattened_keys,
    flatten,
    unflatten,
)
from lion_core.sys_util import LN_UNDEFINED


class Record(BaseModel, Container):
    """
    A container class for managing nested dictionary/list data structures.

    This class provides methods for inserting, retrieving, updating, and
    removing data from nested structures using a list of indices for navigation.

    Attributes:
        content (dict[str, Any]): The internal dictionary storing the nested data.
    """

    content: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the Record with the given keyword arguments."""
        super().__init__(content=kwargs)

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        """Serialize the Record, excluding None values."""
        return {k: v for k, v in self.content.items() if v is not None}

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

    @classmethod
    def deserialize(cls, data: dict[str, Any], *, unflat: bool = False) -> "Record":
        """
        Deserialize data into a Record instance.

        Args:
            data: The data to deserialize.
            unflat: If True, unflatten the data before deserialization.

        Returns:
            A new Record instance.
        """
        if unflat:
            data = unflatten(data)
        return cls(**data)

    def update(self, other: dict[str, Any] | "Record") -> None:
        """
        Update the Record with the key/value pairs from other.

        If other is a Record instance, its content will be used for updating.

        Args:
            other: A dictionary or Record instance to update from.
        """
        if isinstance(other, Record):
            self.content.update(other.content)
        else:
            self.content.update(other)


# File: lion_core/container/record.py
