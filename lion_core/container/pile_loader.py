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

from lion_core.abc.element import Element
from lion_core.exceptions import LionValueError, LionTypeError

T = TypeVar("T")


@runtime_checkable
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


# File: lion_core/container/pile_loader.py
