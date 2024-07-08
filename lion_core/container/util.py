"""
Utility functions and classes for the Lion framework's container module.

This module provides essential utility functions for data conversion and 
validation, as well as the infrastructure for the PileLoader system. It 
includes functions for type conversion, order validation, and Element 
creation, along with the PileLoader protocol and registry for flexible 
data loading into Pile objects.
"""

from collections.abc import Mapping, Generator, Sequence
from collections import deque
from typing import Any, TypeVar, Type, Protocol, Union, Dict, cast

from lion_core.abc.element import Element
from lion_core.generic.component import Component
from lion_core.exceptions import LionIDError, LionTypeError, LionValueError
from lion_core.util.sys_util import SysUtil
from lion_core.abc.space import Ordering, Record

T = TypeVar("T", bound=Element)


def to_list_type(value: Any) -> list[Any]:
    """
    Convert the provided value to a list.

    This function handles various input types including Element, Mapping,
    Record, tuple, list, set, Generator, and deque. It ensures that the
    output is always a list, facilitating consistent data handling.

    Args:
        value: The value to convert to a list.

    Returns:
        A list containing the converted value(s).

    Raises:
        TypeError: If the value cannot be converted to a list.
    """
    if isinstance(value, Element) and not isinstance(value, Record):
        return [value]
    if isinstance(value, (Mapping, Record)):
        return list(value.values())
    if isinstance(value, (tuple, set, Generator, deque, list)):
        return list(value)
    return [value]


def validate_order(value: Any) -> list[str]:
    """
    Validate and convert the order field to a list of strings.

    This function ensures that the input value represents a valid order
    and converts it to a standardized list of strings. It handles various
    input types including string, Ordering, and Element.

    Args:
        value: The value to validate and convert.

    Returns:
        A list of strings representing the validated and converted order.

    Raises:
        LionIDError: If the value contains invalid types or Lion IDs.
    """
    if value is None:
        return []
    if isinstance(value, str) and len(value) == 32:
        return [value]
    if isinstance(value, Ordering):
        return value.order
    if isinstance(value, Element):
        return [value.ln_id]

    try:
        return [i for item in to_list_type(value) if (i := SysUtil.get_lion_id(item))]
    except Exception as e:
        raise LionIDError("Must only contain valid Lion IDs.") from e


def convert_to_lion_object(item: Any) -> Element:
    """
    Convert an item to a Lion framework object (Element or its subclass).

    This function handles the conversion of various input types to Lion
    framework objects. It can process existing Element instances,
    dictionaries with 'lion_class' specifications, and other data types.

    Args:
        item: The item to convert to a Lion framework object.

    Returns:
        An instance of Element or its subclass.

    Note:
        If the input is not an Element or a dictionary with 'lion_class',
        it will be wrapped in a basic Element instance.
    """
    if isinstance(item, Element):
        return item
    if isinstance(item, dict):
        if "lion_class" in item:
            try:
                class_type = SysUtil.mor(item["lion_class"])
                if issubclass(class_type, Component):
                    return Component.from_dict(item)
                return class_type.from_dict(item)
            except ValueError:
                return Element.from_dict(item)
        return Element.from_dict(item)
    return Element(content=item)


class PileLoader(Protocol[T]):
    """
    Protocol defining the interface for pile loader classes.

    This protocol ensures that all pile loader implementations provide
    the necessary methods for loading data into Pile objects.
    """

    @classmethod
    def from_obj(cls, obj: T) -> Union[Dict[str, Element], Sequence[Element]]:
        """Convert an object to a dictionary or sequence of Elements."""
        ...

    @classmethod
    def can_load(cls, obj: Any) -> bool:
        """Check if the loader can handle the given object."""
        ...


class PileLoaderRegistry:
    """
    Registry for PileLoader classes.

    This class manages the registration and retrieval of PileLoader classes,
    allowing for flexible and extensible data loading into Pile objects.
    """

    _loaders: Dict[str, Type[PileLoader]] = {}

    @classmethod
    def register(cls, key: str, loader: Type[PileLoader]) -> None:
        """Register a PileLoader class with the given key."""
        cls._loaders[key] = loader

    @classmethod
    def get(cls, key: str) -> Type[PileLoader]:
        """
        Get a PileLoader class by its key.

        Args:
            key: The identifier for the loader.

        Returns:
            The registered PileLoader class.

        Raises:
            KeyError: If no loader is registered for the given key.
        """
        if key not in cls._loaders:
            raise KeyError(f"No loader registered for key: {key}")
        return cls._loaders[key]

    @classmethod
    def load_from(
        cls, obj: Any, key: str | None = None
    ) -> Union[Dict[str, Element], Sequence[Element]]:
        """
        Load data into a dictionary or sequence of Elements using a loader.

        This method attempts to load the given object using either a
        specified loader or by trying all registered loaders.

        Args:
            obj: The object to load.
            key: Optional key to specify which loader to use.

        Returns:
            A dictionary or sequence of Elements.

        Raises:
            LionValueError: If the specified loader can't handle the data.
            LionTypeError: If no suitable loader is found for the data.
        """
        if key:
            loader = cls.get(key)
            if loader.can_load(obj):
                return loader.from_obj(obj)
            raise LionValueError(f"Loader {key} cannot load the provided data")

        for loader in cls._loaders.values():
            if loader.can_load(obj):
                return loader.from_obj(obj)

        raise LionTypeError(
            f"No suitable loader found for the provided data type: {type(obj)}"
        )


def register_pile_loader(key: str, loader: Type[PileLoader]) -> None:
    """
    Register a PileLoader with the PileLoaderRegistry.

    This function provides a convenient way to add new loaders to the registry.

    Args:
        key: The identifier for the loader.
        loader: The PileLoader class to register.
    """
    PileLoaderRegistry.register(key, loader)


def load_pile(
    obj: Any, key: str | None = None
) -> Union[Dict[str, Element], Sequence[Element]]:
    """
    Load data into a dictionary or sequence of Elements.

    This function uses the PileLoaderRegistry to load the given object
    into a format suitable for creating a Pile.

    Args:
        obj: The object to load.
        key: Optional key to specify which loader to use.

    Returns:
        A dictionary or sequence of Elements.

    Raises:
        LionValueError: If the specified loader can't handle the data.
        LionTypeError: If no suitable loader is found for the data.
    """
    return PileLoaderRegistry.load_from(obj, key)


# File: lion_core/container/util.py
