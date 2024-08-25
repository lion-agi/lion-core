import json
from typing import Any, Protocol, TypeVar, runtime_checkable

from lion_core.generic.element import Element
from lion_core.libs import to_dict

T = TypeVar("T", bound=Element)


@runtime_checkable
class Converter(Protocol):
    """Protocol for converter objects."""

    @classmethod
    def from_obj(cls, target_class: type, obj: Any, **kwargs) -> dict:
        """Convert an object to a lion instance."""
        if not isinstance(obj, dict):
            return cls.process_obj_to_dict(obj, **kwargs)
        return obj

    @staticmethod
    def to_obj(self: T, **kwargs) -> Any:
        """Convert a lion instance to an object."""
        raise NotImplementedError

    @classmethod
    def process_obj_to_dict(cls, obj: Any, **kwargs) -> dict:
        """process an object into a valid lion obj dictionary."""
        return to_dict(obj, **kwargs)


class JsonConverter(Converter):

    @staticmethod
    def to_obj(self: T, **kwargs):
        return json.dumps(self.to_dict(**kwargs))

    @classmethod
    def process_obj_to_dict(cls, obj: Any, **kwargs) -> dict:
        """process an object into a valid lion obj dictionary."""
        return to_dict(obj, str_type="json", **kwargs)


class ConverterRegistry:
    """Registry for managing converters in the Lion framework."""

    _converters: dict[str, type[Converter]] = {}

    @classmethod
    def registry_keys(cls) -> list[str]:
        return list(cls._converters.keys())

    @classmethod
    def register(cls, key: str, converter: type[Converter]):
        if not issubclass(converter, Converter):
            raise ValueError(
                "Converter must be a subclass of the Converter protocol."
            )
        cls._converters[key] = converter

    @classmethod
    def get(cls, key: str) -> Converter:
        try:
            return cls._converters[key]
        except KeyError:
            raise KeyError(
                f"No converter found for {key}. Check if it is registered."
            )

    @classmethod
    def convert_from(
        cls, target_class: type[Element], obj: Any, key: str | None = None
    ) -> dict[str, Any]:
        converter = cls.get(key)
        return converter.from_obj(target_class, obj)

    @classmethod
    def convert_to(cls, self: Any, key: str | type, **kwargs) -> Any:
        if not isinstance(key, str):
            key = key.__name__
        converter = cls.get(key)
        return converter.to_obj(self, **kwargs)


# File: lionagi/core/converter.py
