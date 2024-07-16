"""
Utility functions and classes for Lion framework data handling and conversion.

This module provides:
1. Functions for validating Lion IDs and converting data types.
2. A PileLoader system for flexible data loading into Pile objects.

Key components:
- Utility functions: is_str_id, to_list_type, validate_order
- PileLoader: Protocol for implementing custom data loaders
- PileLoaderRegistry: Management of PileLoader implementations
- Helper functions: register_pile_loader, load_pile
"""

from collections import deque
from collections.abc import Generator, Mapping
from typing import (
    Any,
    Dict,
    Sequence,
    Type,
    TypeVar,
    Union,
    Protocol,
    runtime_checkable,
)

from lion_core.abc.container import Collective, Ordering
from lion_core.exceptions import LionIDError, LionValueError, LionTypeError
from lion_core.sys_util import SysUtil
from lion_core.generic.element import Element

T = TypeVar("T")


def to_list_type(value: Any) -> list[Any]:
    """
    Convert input to a list format compatible with Lion framework.

    Args:
        value: Input of any type to be converted.

    Returns:
        A list representation of the input value.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if SysUtil.is_str_id(value) else []
    if isinstance(value, (Collective, Mapping)):
        return list(value.values())
    if isinstance(value, Element):
        return [value]
    if isinstance(value, (list, tuple, set, deque, Generator)):
        return list(value)
    return [value]


def validate_order(value: Any) -> list[str]:
    """
    Validate and standardize order representation for Lion framework.

    Args:
        value: Input to be validated and converted.

    Returns:
        A list of strings representing valid Lion IDs.

    Raises:
        LionIDError: If input contains invalid types or Lion IDs.
    """
    if value is None:
        return []
    if isinstance(value, str) and SysUtil.is_str_id(value):
        return [value]
    if isinstance(value, Ordering):
        return value.order
    if isinstance(value, Element):
        return [value.ln_id]

    try:
        result = []
        for item in to_list_type(value):
            if isinstance(item, str) and SysUtil.is_str_id(item):
                result.append(item)
            elif isinstance(item, Element):
                result.append(item.ln_id)
            else:
                id_ = SysUtil.get_lion_id(item)
                if id_:
                    result.append(id_)
        return result
    except Exception as e:
        raise LionIDError("Must only contain valid Lion IDs.") from e


@runtime_checkable
class PileLoader(Protocol[T]):
    """Protocol defining the interface for pile loader classes."""

    @classmethod
    def from_obj(cls, obj: T) -> Union[Dict[str, T], Sequence[T]]:
        """
        Convert an object to a dictionary or sequence of Elements.

        Args:
            obj: Object to convert.

        Returns:
            Dictionary or sequence of Elements.
        """

    @classmethod
    def can_load(cls, obj: Any) -> bool:
        """
        Check if the loader can handle the given object.

        Args:
            obj: Object to check.

        Returns:
            True if the loader can handle the object, False otherwise.
        """


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
