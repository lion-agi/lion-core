import json
from typing import Any, Protocol, TypeVar, runtime_checkable

from lion_core.generic.element import Element
from lion_core.libs import to_dict

T = TypeVar("T", bound=Element)


@runtime_checkable
class Converter(Protocol):
    """Protocol for converter objects.

    Subclasses need to implement the following methods:
    - convert_obj_to_sub_dict
    - convert_sub_to_obj_dict
    - to_obj
    """

    _object: str

    @classmethod
    def object(cls) -> str:
        """Return the object type of the converter."""
        return cls._object

    @classmethod
    def from_obj(
        cls,
        subject_class: type[Element],
        object_: Any,
        **kwargs: Any,
    ) -> dict:
        """Convert an object to a dictionary representation.

        Args:
            subject_class: The target Element subclass.
            object_: The object to convert.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary representation of the object.
        """
        return cls.convert_obj_to_sub_dict(object_=object_, **kwargs)

    @classmethod
    def convert_obj_to_sub_dict(cls, object_: Any, **kwargs: Any) -> dict:
        """Process an object into a valid lion obj dictionary.

        Args:
            object_: The object to convert.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary representation of the object.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError

    @classmethod
    def convert_sub_to_obj_dict(cls, subject: T, **kwargs) -> dict:
        """Process a dictionary into an object class dictionary.

        Args:
            subject: The subject to convert.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary representation of the subject.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError

    @classmethod
    def to_obj(
        cls,
        subject: T,
        *,
        convert_kwargs: dict = {},
        **kwargs: Any,
    ) -> dict:
        """Convert a subject to an object representation.

        Args:
            subject: The subject to convert.
            convert_kwargs: Kwargs for convert_sub_to_obj_dict.
            **kwargs: Additional keyword arguments.

        Returns:
            An object representation of the subject.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError


class JsonConverter(Converter):
    """JSON converter implementation."""

    _object = "json"

    @classmethod
    def convert_obj_to_sub_dict(cls, object_: str, **kwargs: Any) -> dict:
        """Convert a JSON string to a dictionary.

        Args:
            object_: JSON string to convert.
            **kwargs: Additional arguments for json.loads.

        Returns:
            A dictionary representation of the JSON string.
        """
        kwargs["str_type"] = "json"
        return to_dict(object_, **kwargs)

    @classmethod
    def convert_sub_to_obj_dict(cls, subject: T, **kwargs: Any) -> dict:
        """Convert a subject to a dictionary.

        Args:
            subject: The subject to convert.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary representation of the subject.
        """
        return subject.to_dict(**kwargs)

    @classmethod
    def to_obj(
        cls,
        subject: T,
        *,
        convert_kwargs: dict = {},
        **kwargs: Any,
    ) -> Any:
        """Convert a subject to a JSON string.

        Args:
            subject: The subject to convert.
            convert_kwargs: Kwargs for convert_sub_to_obj_dict.
            **kwargs: Additional arguments for json.dumps.

        Returns:
            A JSON string representation of the subject.
        """
        _dict = cls.convert_sub_to_obj_dict(subject=subject, **convert_kwargs)
        return json.dumps(obj=_dict, **kwargs)


class ConverterRegistry:
    """Registry for managing converters in the Lion framework."""

    _converters: dict[str, Converter] = {}

    @classmethod
    def registry_object_keys(cls) -> list[str]:
        """Get a list of registered object keys.

        Returns:
            A list of registered object keys.
        """
        return list(cls._converters.keys())

    @classmethod
    def register(cls, converter: type[Converter]) -> None:
        """Register a converter.

        Args:
            converter: The converter class to register.

        Raises:
            ValueError: If the converter is not a subclass of Converter.
        """
        if not issubclass(converter, Converter):
            err_msg = (
                "In order to register the converter, it needs to be a "
                "subclass of the `Converter` protocol. "
            )
            if isinstance(converter, Converter):
                err_msg += (
                    f"The converter value received <{converter.object()}> "
                    "is an instance. Did you mean to register the class?"
                )
            raise ValueError(err_msg)

        cls._converters[converter.object()] = converter()

    @classmethod
    def get(cls, object_key: str, /) -> Converter:
        """Get a converter by its object key.

        Args:
            object_key: The object key of the converter.

        Returns:
            The converter class.

        Raises:
            KeyError: If no converter is found for the given key.
        """
        try:
            return cls._converters[object_key]
        except KeyError:
            raise KeyError(
                f"No converter found for {object_key}. "
                "Check if it is registered."
            )

    @classmethod
    def convert_from(
        cls,
        subject_class: type[Element],
        object_: Any,
        object_key: str = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Convert an object to a dictionary using a specific converter.

        Args:
            subject_class: The target Element subclass.
            obj: The object to convert.
            key: The object key of the converter to use.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary representation of the object.
        """
        converter = cls.get(object_key)
        return converter.from_obj(
            subject_class=subject_class,
            object_=object_,
            **kwargs,
        )

    @classmethod
    def convert_to(
        cls,
        subject: Any,
        object_key: str | type,
        **kwargs,
    ) -> Any:
        """Convert a subject to an object using a specific converter.

        Args:
            subject: The subject to convert.
            key: The object key or type of the converter to use.
            **kwargs: Additional keyword arguments.

        Returns:
            The converted object.
        """
        if not isinstance(object_key, str):
            object_key = object_key.__name__
        converter = cls.get(object_key)
        return converter.to_obj(subject=subject, **kwargs)


# File: lionagi/core/converter.py
