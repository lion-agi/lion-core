from __future__ import annotations

from typing import Any
from pydantic import Field, BaseModel, ConfigDict
from lion_core.libs import (
    nget,
    ninsert,
    nset,
    npop,
    flatten,
)
from lion_core.setting import LN_UNDEFINED


class Note(BaseModel):
    """A container for managing nested dictionary data structures."""

    content: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        # extra="allow",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )

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

        if not self.get(indices, None):
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

    def keys(self, flat: bool = False):
        """
        Get the keys of the Note.

        Args:
            flat: If True, return flattened keys.

        Returns:
            An iterator of keys.
        """
        if flat:
            return flatten(self.content).keys()
        return self.content.keys()

    def values(self, flat: bool = False):
        """
        Get the values of the Note.

        Args:
            flat: If True, return flattened values.

        Returns:
            An iterator of values.
        """
        if flat:
            return flatten(self.content).values()
        return self.content.values()

    def items(self, flat: bool = False):
        """
        Get the items of the Note.

        Args:
            flat: If True, return flattened items.

        Returns:
            An iterator of (key, value) pairs.
        """
        if flat:
            return flatten(self.content).items()
        return self.content.items()

    def to_dict(self, **kwargs) -> dict[str, Any]:
        """
        Convert the Note to a dictionary.

        Returns:
            A dictionary representation of the Note.
        """
        return self.model_dump(**kwargs)

    @classmethod
    def from_dict(cls, dict_: dict[str, Any]) -> Note:
        """
        Create a Note from a dictionary.

        Args:
            dict_: The dictionary to create the Note from.

        Returns:
            A Note object.
        """
        return cls(content=dict_)
