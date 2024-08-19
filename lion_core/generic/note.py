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

from functools import singledispatchmethod
from collections.abc import Mapping
from typing import Any
from typing_extensions import override
from pydantic import Field, BaseModel, ConfigDict, field_serializer
from lion_core.abc import Container
from lion_core.libs import (
    nget,
    ninsert,
    nset,
    npop,
    flatten,
    to_dict,
    fuzzy_parse_json,
)
from lion_core.setting import LN_UNDEFINED
from lion_core.sys_utils import SysUtil
from lion_core.generic.element import Element


class Note(BaseModel, Container):
    """A container for managing nested dictionary data structures."""

    content: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    def __init__(self, **kwargs):
        super().__init__()
        self.content = kwargs

    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        cls.update.register(cls, cls._update_with_note)

    @field_serializer("content")
    def _serialize_content(self, value: Any) -> dict[str, Any]:
        from lion_core.communication.base_mail import BaseMail

        output_dict = SysUtil.copy(value, deep=True)
        origin_obj = output_dict.pop("clone_from", None)

        if origin_obj and isinstance(origin_obj, BaseMail):
            info_dict = {
                "clone_from_info": {
                    "original_ln_id": origin_obj.ln_id,
                    "original_timestamp": origin_obj.timestamp,
                    "original_sender": origin_obj.sender,
                    "original_recipient": origin_obj.recipient,
                }
            }
            output_dict.update(info_dict)
        return output_dict

    def pop(self, indices: list[str] | str, default: Any = LN_UNDEFINED, /) -> Any:
        """
        Remove and return an item from the nested structure.

        Args:
            indices: The path to the item to be removed.
            default: The value to return if the item is not found.

        Returns:
            The removed item or the default value.
        """
        if isinstance(indices, str):
            indices = [indices]
        return npop(self.content, indices, default)

    def insert(self, indices: list[str] | str, value: Any, /) -> None:
        """
        Insert a value into the nested structure at the specified indices.

        Args:
            indices: The path where to insert the value.
            value: The value to insert.
        """
        if isinstance(indices, str):
            indices = [indices]
        ninsert(self.content, indices, value)

    def set(self, indices: list[str] | str, value: Any, /) -> None:
        """
        Set a value in the nested structure at the specified indices.
        If the path doesn't exist, it will be created.

        Args:
            indices: The path where to set the value.
            value: The value to set.
        """
        if isinstance(indices, str):
            indices = [indices]

        if not self.get(indices, None):
            self.insert(indices, value)
        else:
            nset(self.content, indices, value)

    def get(self, indices: list[str] | str, default: Any = LN_UNDEFINED, /) -> Any:
        """
        Get a value from the nested structure at the specified indices.

        Args:
            indices: The path to the value in the nested structure.
            default: The default value to return if the item is not found.

        Returns:
            The value at the specified indices or the default value.
        """
        if isinstance(indices, str):
            indices = [indices]
        return nget(self.content, indices, default)

    def keys(self, /, flat: bool = False) -> list:
        """
        Get the keys of the Note.

        Args:
            flat: If True, return flattened keys.

        Returns:
            An iterator of keys.
        """
        if flat:
            return flatten(self.content).keys()
        return list(self.content.keys())

    def values(self, /, flat: bool = False):
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

    def items(self, /, flat: bool = False):
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
        output_dict = self.model_dump(**kwargs)
        return output_dict["content"]

    def clear(self):
        """
        Clear the content of the Note.
        """
        self.content.clear()

    @singledispatchmethod
    def update(self, items: Any, indices: list[str | int] = None, /):
        try:
            d_ = to_dict(items)
            if isinstance(d_, dict):
                self.update(d_, indices)
            else:
                self.set(indices, [d_] if not isinstance(d_, list) else d_)
        except Exception as e:
            raise TypeError(f"Invalid input type for update: {type(items)}") from e

    @update.register(dict)
    def _(self, items: dict, indices: list[str | int] = None, /):
        if indices:
            a = self.get(indices, {}).update(items)
            self.set(indices, a)
            return

        self.content.update(items)

    @update.register(Mapping)
    def _(self, items: Mapping, indices: list[str | int] = None, /):
        return self.update(dict(items), indices)

    @update.register(str)
    def _(self, items: str, indices: list[str | int] = None, /):

        item_: dict | None = to_dict(
            items,
            str_type="json",
            parser=fuzzy_parse_json,
            suppress=True,
        )
        if item_ is None:
            item_ = to_dict(
                items,
                str_type="xml",
                suppress=True,
            )

        if not isinstance(item_, dict):
            raise ValueError(f"Invalid input type for update: {type(items)}")
        self.update(item_, indices)

    @update.register(Element)
    def _(self, items: Element, indices: list[str | int] = None, /):
        self.update(items.to_dict(), indices)

    def _update_with_note(self, items: "Note", indices: list[str | int] = None, /):
        self.update(items.content, indices)

    @classmethod
    def from_dict(cls, kwargs) -> "Note":
        """
        Create a Note from a dictionary.

        Returns:
            A Note object.
        """
        return cls(**kwargs)

    def __contains__(self, indices: str | list) -> bool:
        return self.content.get(indices, LN_UNDEFINED) is not LN_UNDEFINED

    def __len__(self) -> int:
        return len(self.content)

    def __iter__(self):
        return iter(self.content)

    def __next__(self):
        return next(iter(self.content))

    @override
    def __str__(self) -> str:
        return str(self.content)

    @override
    def __repr__(self) -> str:
        return repr(self.content)

    def __getitem__(self, *indices) -> Any:
        indices = list(indices[0]) if isinstance(indices[0], tuple) else list(indices)
        return self.get(indices)

    def __setitem__(self, indices: str | tuple, value: Any) -> None:
        self.set(indices, value)


def note(**kwargs) -> Note:
    """
    Create a Note object from keyword arguments.

    Returns:
        A Note object.
    """
    return Note(**kwargs)


__all__ = ["Note", "note"]

# File : lion_core/generic/note.py
