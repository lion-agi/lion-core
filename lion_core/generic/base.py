"""Module containing the BaseComponent class for the Lion framework."""

from typing import Any, ClassVar, Type, TypeVar

from pydantic import Field, ConfigDict, model_serializer

from lion_core.element import Element
from lion_core.container.record import Record
from lion_core.converter import ConverterRegistry, Converter

# Default fields to include in serialization
DEFAULT_SERIALIZATION_INCLUDE: set[str] = {"metadata", "content", "ln_id", "timestamp"}

T = TypeVar("T", bound="BaseComponent")


class BaseComponent(Element):
    """
    Base class for components in the Lion framework.

    This class extends the Element class and provides additional
    functionality for metadata handling, content storage, and
    conversion operations using the ConverterRegistry.

    Attributes:
        metadata (Record): Additional metadata for the component.
        content (Any): The main content of the Component.
    """

    metadata: Record = Field(
        default_factory=Record,
        description="Additional metadata for the component",
    )

    content: Any = Field(
        default=None,
        description="The main content of the Component",
    )

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="allow",  # Allow extra fields
    )

    _converter_registry: ClassVar[Type[ConverterRegistry]] | ClassVar[Converter] = (
        ConverterRegistry
    )

    @model_serializer
    def _serialize(self, **kwargs: Any) -> dict[str, Any]:
        """
        Serialize the BaseComponent to a dictionary.

        This method extends the serialization process of the Element class
        to include additional fields specific to BaseComponent.

        Args:
            **kwargs: Additional keyword arguments for serialization.

        Returns:
            A dictionary representation of the BaseComponent.
        """
        kwargs["include"] = kwargs.get("include", DEFAULT_SERIALIZATION_INCLUDE)
        return super()._serialize(**kwargs)

    @classmethod
    def _deserialize(
        cls, data: dict[str, Any], *, unflat: bool = False
    ) -> "BaseComponent":
        """
        Deserialize a dictionary into a BaseComponent instance.

        This method extends the deserialization process of the Element class
        to handle the metadata field specific to BaseComponent.

        Args:
            data: A dictionary containing BaseComponent data.
            unflat: If True, unflatten the metadata before deserialization.

        Returns:
            An instance of the BaseComponent class or its subclass.
        """
        data["metadata"] = Record.deserialize(data["metadata"], unflat=unflat)
        return super()._deserialize(data)

    @classmethod
    def get_converter_registry(cls) -> ConverterRegistry:
        """
        Get the converter registry for the class.

        Returns:
            The ConverterRegistry instance for the class.
        """
        if isinstance(cls._converter_registry, type):
            cls._converter_registry = cls._converter_registry()
        return cls._converter_registry

    def convert_to(self, key: str = "dict", /, **kwargs: Any) -> Any:
        """
        Convert the component to a specified type using the ConverterRegistry.

        Args:
            key: The key of the converter to use.
            **kwargs: Additional keyword arguments for conversion.

        Returns:
            The converted component in the specified type.
        """
        return self.get_converter_registry().convert_to(self, key, **kwargs)

    @classmethod
    def convert_from(cls, obj: Any, key: str = "dict", /, *, unflat: bool = False) -> T:
        """
        Convert data to create a new component instance using the ConverterRegistry.

        Args:
            obj: The object to convert from.
            key: The key of the converter to use.
            unflat: If True, unflatten the data before deserialization.

        Returns:
            A new instance of the BaseComponent class or its subclass.
        """
        data = cls.get_converter_registry().convert_from(obj, key)
        return cls._deserialize(data, unflat=unflat)

    @classmethod
    def register_converter(cls, key: str, converter: Type[Converter]) -> None:
        """Register a new converter."""
        cls.get_converter_registry().register(key, converter)

    def copy(self, deep=True):
        return self.model_copy(deep=deep)


# File: lion_core/generic/base.py
