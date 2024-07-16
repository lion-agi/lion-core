"""Converter Registry for managing data conversion in the Lion framework."""

from typing import Any, Protocol, runtime_checkable, TypeVar


T = TypeVar("T")


@runtime_checkable
class Converter(Protocol):
    """Protocol for converter objects."""

    @staticmethod
    def from_obj(obj: Any) -> dict[str, Any]:
        """Convert an object to a dictionary."""

    @staticmethod
    def to_obj(obj: Any) -> Any:
        """Convert a dictionary to an object."""


class ConverterRegistry:
    """Registry for managing converters in the Lion framework."""

    _converters: dict[str, Converter] = {}
    _type_mapping: dict[type[Any], str] = {}

    @classmethod
    def register(
        cls,
        key: str,
        converter: Converter | Any,
        for_types: type[Any] | tuple[type[Any], ...] | None = None,
    ) -> None:
        """
        Register a converter for a specific key and optionally for types.

        Args:
            key: The key to associate with this converter.
            converter: An object with from_obj and to_obj methods.
            for_types: Type(s) this converter should be used for.

        Raises:
            ValueError: If the converter doesn't have required methods.
        """
        if not hasattr(converter, "from_obj") or not hasattr(converter, "to_obj"):
            raise ValueError("Converter must have 'from_obj' and 'to_obj' methods")

        cls._converters[key] = converter
        if for_types is not None:
            if isinstance(for_types, type):
                for_types = (for_types,)
            for t in for_types:
                cls._type_mapping[t] = key

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
        if key not in cls._converters:
            raise KeyError(f"No converter registered for key: {key}")
        return cls._converters[key]

    @classmethod
    def get_converter_for_type(cls, obj: Any) -> Converter:
        """
        Get the appropriate converter for a given object based on its type.

        Args:
            obj: The object to find a converter for.

        Returns:
            The appropriate converter for the object's type.

        Raises:
            TypeError: If no converter is found for the object's type.
        """
        for t in type(obj).__mro__:
            if t in cls._type_mapping:
                return cls.get(cls._type_mapping[t])
        raise TypeError(f"No converter found for type: {type(obj)}")

    @classmethod
    def convert_from(cls, obj: Any, key: str | None = None) -> dict[str, Any]:
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
            converter = cls.get_converter_for_type(obj)
        else:
            converter = cls.get(key)
        return converter.from_obj(obj)

    @classmethod
    def convert_to(cls, obj: Any, key: str) -> Any:
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
        converter = cls.get(key)
        return converter.to_obj(obj)


# File: lionagi/core/converter.py