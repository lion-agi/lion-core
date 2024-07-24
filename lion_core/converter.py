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

from typing import Any, Protocol, runtime_checkable, TypeVar
import json

T = TypeVar("T")


@runtime_checkable
class Converter(Protocol):
    """Protocol for converter objects."""

    @staticmethod
    def from_obj(target_class: type, obj: Any) -> dict:
        """Convert an object to a lion instance."""

    @staticmethod
    def to_obj(**kwargs) -> Any:
        """Convert a lion instance to an object."""


class DictConverter(Converter):

    @staticmethod
    def from_obj(cls, obj: dict, **kwargs) -> dict:
        return obj

    @staticmethod
    def to_obj(self, **kwargs):
        return self.to_dict(**kwargs)


class JsonConverter(Converter):

    @staticmethod
    def from_obj(cls, obj: str, **kwargs):
        try:
            return json.loads(obj, **kwargs)
        except Exception as e:
            raise ValueError("Failed to convert from JSON.") from e

    @staticmethod
    def to_obj(self, **kwargs):
        return json.dumps(self.to_dict(**kwargs))


class ConverterRegistry:
    """Registry for managing converters in the Lion framework."""

    _converters: dict[str, Converter] = {}

    @classmethod
    def register(
        cls,
        key: str,
        converter: Converter | Any,
    ) -> None:
        """
        Register a converter for a specific key and optionally for types.

        Args:
            key: The key to associate with this converter.
            converter: An object with from_obj and to_obj methods.

        Raises:
            ValueError: If the converter doesn't have required methods.
        """
        if not hasattr(converter, "from_obj") or not hasattr(converter, "to_obj"):
            raise ValueError("Converter must have 'from_obj' and 'to_obj' methods")

        cls._converters[key] = converter

    @classmethod
    def get(cls, key: str) -> Converter:
        """
        Get a converter by key.

        Args:
            key: The key of the converter.

        Returns:
            The converter associated with the key.

        Raises:
            KeyError: If no converter is registered for the key.
        """
        try:
            return cls._converters[key]
        except KeyError:
            raise KeyError(f"No converter found for {key}. Check if it is registered.")

    @classmethod
    def convert_from(
        cls, target_class, obj: Any, key: str | None = None
    ) -> dict[str, Any]:
        """
        Convert an object to a dictionary using the specified converter.

        Args:
            obj: The object to convert.
            key: The key of the converter to use. If None, auto-detect.

        Returns:
            The converted object as a dictionary.

        Raises:
            KeyError: If the specified key is not found.
            TypeError: If no suitable converter is found for auto-detection.
        """
        if key is None:
            key = obj.__class__.__name__
        converter = cls.get(key)
        return converter.from_obj(target_class, obj)

    @classmethod
    def convert_to(cls, obj: Any, key: str | type, **kwargs) -> Any:
        """
        Convert an object to another type using the specified converter.

        Args:
            obj: The object to convert.
            key: The key of the converter to use.

        Returns:
            The converted object.

        Raises:
            KeyError: If the specified key is not found.
        """
        if not isinstance(key, str):
            key = key.__name__
        converter = cls.get(key)
        return converter.to_obj(obj, **kwargs)


ConverterRegistry.register("dict", DictConverter())
ConverterRegistry.register("json", JsonConverter())

# File: lionagi/core/converter.py
