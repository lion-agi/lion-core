"""Converter module for object-Component dictionary transformations.

This module provides a system for converting between arbitrary objects and
the internal dictionary representation used by the Component class. It
enables seamless integration of external data formats with the Lion
framework's Component system.

Key components:
- Converter: Protocol defining the interface for converter classes.
- ConverterRegistry: Registry for managing converters.
- Utility functions: For registering, retrieving, and using converters.

Example usage:

    class MyCustomConverter:
        @classmethod
        def from_obj(cls, obj: Any) -> dict[str, Any]:
            return {
                "content": obj.data,
                "metadata": {"source": obj.source, "timestamp": obj.created_at}
            }

        @classmethod
        def to_obj(cls, component: Element) -> Any:
            return ExternalObject(
                data=component.content,
                source=component.metadata.get("source"),
                created_at=component.metadata.get("timestamp")
            )

    register_converter("my_custom_converter", MyCustomConverter)

    external_obj = ExternalObject(
        data="Hello, world!", source="user", created_at="2023-07-08"
    )
    component = Component.from_obj(external_obj, "my_custom_converter")

    converted_obj = component.to_obj("my_custom_converter")
"""

from __future__ import annotations
from typing import Any, TypeVar, Type, Protocol
from abc import abstractmethod

from lion_core.abc.element import Element


T = TypeVar("T", bound="Converter")

# Make a general converter class

# class Converter(Protocol):
#     """Protocol defining the interface for converter classes.

#     Converters should implement two class methods:
#     - from_obj: Convert an external object to a Component-compatible dict.
#     - to_obj: Convert a Component back to an external object.

#     Example implementation:
#         class MyConverter:
#             @classmethod
#             def from_obj(cls, obj: Any) -> dict[str, Any]:
#                 return {"content": str(obj), "metadata": {"type": type(obj).__name__}}

#             @classmethod
#             def to_obj(cls, component: Element) -> Any:
#                 # Convert Component back to original type if needed
#                 return component.content
#     """

#     @classmethod
#     @abstractmethod
#     def from_obj(cls: Type[T], obj: Any) -> dict[str, Any]:
#         """Convert an object to a Component-compatible dictionary.

#         Args:
#             obj: The object to convert.

#         Returns:
#             A dictionary representation of the object for Component creation.

#         Example:
#             @classmethod
#             def from_obj(cls, obj: CustomType) -> dict[str, Any]:
#                 return {
#                     "content": obj.main_data,
#                     "metadata": {
#                         "id": obj.id,
#                         "created_at": obj.timestamp.isoformat()
#                     }
#                 }
#         """

#     @classmethod
#     @abstractmethod
#     def to_obj(cls: Type[T], component: Element) -> Any:
#         """Convert a Component to another object type.

#         Args:
#             component: The Component to convert.

#         Returns:
#             The converted object.

#         Example:
#             @classmethod
#             def to_obj(cls, component: Element) -> CustomType:
#                 return CustomType(
#                     main_data=component.content,
#                     id=component.metadata.get("id"),
#                     timestamp=datetime.fromisoformat(
#                         component.metadata.get("created_at")
#                     )
#                 )
#         """


# class ConverterRegistry:
#     """Registry for managing converters.

#     This class provides methods to register, retrieve, and use converters.
#     Converters are stored with associated keys for easy lookup.

#     Example usage:
#         class JSONConverter:
#             @classmethod
#             def from_obj(cls, obj: str) -> dict[str, Any]:
#                 import json
#                 data = json.loads(obj)
#                 return {
#                     "content": data.get("content"),
#                     "metadata": data.get("metadata", {})
#                 }

#             @classmethod
#             def to_obj(cls, component: Element) -> str:
#                 import json
#                 return json.dumps({
#                     "content": component.content,
#                     "metadata": component.metadata
#                 })

#         ConverterRegistry.register("json", JSONConverter)

#         json_data = '{"content": "Hello", "metadata": {"source": "API"}}'
#         component_dict = ConverterRegistry.convert_from(json_data, "json")

#         component = Component(**component_dict)
#         json_output = ConverterRegistry.convert_to(component, "json")
#     """

#     _converters: dict[str, Type[Converter]] = {}

#     @classmethod
#     def register(cls, key: str, converter: Type[Converter]) -> None:
#         """Register a converter for a specific key.

#         Args:
#             key: The key to associate with the converter.
#             converter: The converter class to register.

#         Example:
#             ConverterRegistry.register("json", JSONConverter)
#         """
#         cls._converters[key] = converter

#     @classmethod
#     def get(cls, key: str) -> Type[Converter]:
#         """Get a converter by key.

#         Args:
#             key: The key of the converter to retrieve.

#         Returns:
#             The requested converter class.

#         Raises:
#             KeyError: If no converter is registered for the given key.

#         Example:
#             json_converter = ConverterRegistry.get("json")
#         """
#         if key not in cls._converters:
#             raise KeyError(f"No converter registered for key: {key}")
#         return cls._converters[key]

#     @classmethod
#     def convert_from(cls, obj: Any, key: str) -> dict[str, Any]:
#         """Convert an object to a dictionary using the specified converter.

#         Args:
#             obj: The object to convert.
#             key: The key of the converter to use.

#         Returns:
#             A dictionary representation of the object.

#         Example:
#             json_data = '{"content": "Hello", "metadata": {"source": "API"}}'
#             component_dict = ConverterRegistry.convert_from(json_data, "json")
#         """
#         converter = cls.get(key)
#         return converter.from_obj(obj)

#     @classmethod
#     def convert_to(cls, component: Element, key: str) -> Any:
#         """Convert a Component to another object using the specified converter.

#         Args:
#             component: The Component to convert.
#             key: The key of the converter to use.

#         Returns:
#             The converted object.

#         Example:
#             json_output = ConverterRegistry.convert_to(component, "json")
#         """
#         converter = cls.get(key)
#         return converter.to_obj(component)


# def register_converter(key: str, converter: Type[Converter]) -> None:
#     """Utility function to register a converter.

#     Args:
#         key: The key to associate with the converter.
#         converter: The converter class to register.

#     Example:
#         register_converter("json", JSONConverter)
#     """
#     ConverterRegistry.register(key, converter)


# def get_converter(key: str) -> Type[Converter]:
#     """Utility function to get a converter by key.

#     Args:
#         key: The key of the converter to retrieve.

#     Returns:
#         The requested converter class.

#     Raises:
#         KeyError: If no converter is registered for the given key.

#     Example:
#         json_converter = get_converter("json")
#     """
#     return ConverterRegistry.get(key)


# def convert_from(obj: Any, key: str) -> dict[str, Any]:
#     """Utility function to convert an object to a dictionary.

#     Args:
#         obj: The object to convert.
#         key: The key of the converter to use.

#     Returns:
#         A dictionary representation of the object.

#     Example:
#         json_data = '{"content": "Hello", "metadata": {"source": "API"}}'
#         component_dict = convert_from(json_data, "json")
#     """
#     return ConverterRegistry.convert_from(obj, key)


# def convert_to(component: Element, key: str) -> Any:
#     """Utility function to convert a Component to another object.

#     Args:
#         component: The Component to convert.
#         key: The key of the converter to use.

#     Returns:
#         The converted object.

#     Example:
#         json_output = convert_to(component, "json")
#     """
#     return ConverterRegistry.convert_to(component, key)


# # File: lion_core/util/converter.py
