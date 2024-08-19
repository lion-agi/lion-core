from typing import Any, Protocol, Sequence, Type, TypeVar, runtime_checkable

from lion_core.exceptions import LionTypeError, LionValueError

T = TypeVar("T")


@runtime_checkable
class PileLoader(Protocol[T]):
    """Protocol defining the interface for pile loader classes."""

    @staticmethod
    def from_obj(cls, obj: T) -> dict | Sequence[dict]: ...

    @staticmethod
    def can_load(cls, obj: Any) -> bool: ...


class PileLoaderRegistry:
    _loaders: dict[str, PileLoader] = {}

    @classmethod
    def register(cls, key: str, loader: PileLoader | Type[PileLoader]) -> None:
        """Register a PileLoader class with the given key."""
        if issubclass(loader, PileLoader):
            cls._loaders[key] = loader()
        elif isinstance(loader, PileLoader):
            cls._loaders[key] = loader
        else:
            raise LionTypeError(
                f"Invalid loader class provided. Must be a subclass of PileLoader."
            )

    @classmethod
    def get(cls, key: str) -> Type[PileLoader]:
        if key not in cls._loaders:
            raise KeyError(f"No loader registered for key: {key}")
        return cls._loaders[key]

    @classmethod
    def load_from(cls, obj: Any, key: str | None = None) -> list[dict]:
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
