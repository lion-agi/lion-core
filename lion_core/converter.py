import json
from typing import Any, Protocol, TypeVar, runtime_checkable

from lionfuncs import to_dict

from lion_core.generic.element import Element

T = TypeVar("T", bound=Element)


@runtime_checkable
class Converter(Protocol):
    """
    Protocol for converter objects.

    Subclasses need to implement the following methods:
    - from_obj
    - to_obj
    """

    obj_key: str

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[Element],
        obj: Any,
        /,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """kwargs for to_dict"""
        return to_dict(obj)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ) -> dict:
        raise NotImplementedError


class JsonConverter(Converter):

    obj_key = "json"

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ) -> Any:
        """
        kwargs for
        """
        dict_ = subj.to_dict(**kwargs)
        return json.dumps(dict_)


class ConverterRegistry:

    _converters: dict[str, Converter] = {}

    @classmethod
    def list_obj_keys(cls) -> list[str]:
        return list(cls._converters.keys())

    @classmethod
    def register(cls, converter: type[Converter], /) -> None:
        if not isinstance(converter, type(Converter)):
            err_msg = (
                "In order to register the converter, it needs to be a "
                "subclass of the `Converter` protocol. "
            )
            if isinstance(converter, Converter):
                err_msg += (
                    f"The converter value received <{converter.obj_key}> "
                    "is an instance. Did you mean to register the class?"
                )
            raise ValueError(err_msg)

        cls._converters[converter.obj_key] = converter()

    @classmethod
    def get(cls, obj_key: str, /) -> Converter:
        try:
            return cls._converters[obj_key]
        except KeyError:
            raise KeyError(
                f"No converter found for {obj_key}. "
                "Check if it is registered."
            )

    @classmethod
    def convert_from(
        cls,
        subj_cls: type[Element],
        obj: Any,
        obj_key: str = None,
        /,
        **kwargs,
    ) -> dict[str, Any]:
        converter = cls.get(obj_key)
        return converter.from_obj(subj_cls, obj, **kwargs)

    @classmethod
    def convert_to(
        cls,
        subj: Any,
        obj_key: str | type,
        /,
        **kwargs,
    ) -> Any:
        try:
            if not isinstance(obj_key, str):
                obj_key = obj_key.__name__
            converter = cls.get(obj_key)
            return converter.to_obj(subj, **kwargs)
        except KeyError:
            raise KeyError(
                f"No converter found for <{obj_key}>. "
                "Check if it is registered."
            )


# File: lionagi/core/converter.py
