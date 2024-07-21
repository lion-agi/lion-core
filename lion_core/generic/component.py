from __future__ import annotations
from typing import Any, TypeVar, ClassVar, Type

from pydantic import (
    Field,
    field_serializer, 
    ConfigDict, 
    field_validator
)
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from lion_core.sys_util import SysUtil
from lion_core.setting import LN_UNDEFINED
from lion_core.exceptions import LionValueError
from .element import Element
from .note import Note


T = TypeVar("T", bound=Element)

DEFAULT_SERIALIZATION_INCLUDE: set[str] = {
    "metadata",
    "content",
    "ln_id",
    "timestamp",
    "extra_fields",
    "embedding",
}


class Component(Element):
    """Extended base class for components in the Lion framework."""

    metadata: Note = Field(
        default_factory=Note,
        description="Additional metadata for the component",
    )

    content: Any = Field(
        default=None,
        description="The main content of the Component",
    )

    embedding: list[float] = Field(default_factory=list)

    extra_fields: dict[str, Any] = Field(default_factory=dict)

    # model_config = ConfigDict(
    #     extra="allow",  # Allow extra fields
    # )

    # _converter_registry: ClassVar[Type[ConverterRegistry]] | ClassVar[Converter] = (
    #     ConverterRegistry
    # )

    @field_serializer("extra_fields")
    def _serialize_extra_fields(self, value: dict[str, FieldInfo]) -> dict[str, Any]:
        """Custom serializer for extra fields."""
        output_dict = {}
        for k in value.keys():
            k_value = self.__dict__.get(k)
            output_dict[k] = k_value
        return output_dict

    @field_validator("extra_fields")
    def _validate_extra_fields(cls, value: Any) -> dict[str, FieldInfo]:
        """Custom validator for extra fields."""
        if not isinstance(value, dict):
            raise LionValueError("Extra fields must be a dictionary")
        return {k: Field(**v) if isinstance(v, dict) else v for k, v in value.items()}

    @property
    def all_fields(self) -> dict[str, FieldInfo]:
        return {**self.model_fields, **self.extra_fields}

    def add_field(
        self,
        name: str,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo = LN_UNDEFINED,
        **kwargs,
    ) -> None:
        """Add a new field to the component's extra fields.

        Args:
            name: The name of the field to add.
            value: The value of the field.
            annotation: Type annotation for the field.
            field_obj: A pre-configured FieldInfo object.
            **kwargs: Additional keyword arguments for Field.

        Raises:
            ValueError: If the field already exists.
        """
        if name in self.all_fields:
            raise LionValueError(f"Field '{name}' already exists")

        self.update_field(
            name=name, value=value, annotation=annotation, field_obj=field_obj, **kwargs
        )

    def update_field(
        self,
        name: str,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo | Any = LN_UNDEFINED,
        **kwargs,
    ) -> None:
        """similar to dictionary update but for single field,
        if not existed, it will create a new field, otherwise update info of the field.
        """

        # pydanitc Field object cannot have both default and default_factory
        if "default" in kwargs and "default_factory" in kwargs:
            raise ValueError("Cannot provide both 'default' and 'default_factory'")

        # if passing kwargs
        if field_obj is LN_UNDEFINED:
            # check if field exists
            field_obj = self.all_fields.get(name, LN_UNDEFINED)

            if field_obj: # existing field
                for k, v in kwargs.items():
                    setattr(field_obj, k, v)
            else:
                field_obj = Field(**kwargs)

        else: # passing field_obj directly
            if not isinstance(field_obj, FieldInfo):
                raise ValueError("Invalid field_obj. It should be a pydantic FieldInfo object.")

        if annotation is not LN_UNDEFINED:
            field_obj.annotation = annotation
        if not field_obj.annotation:
            field_obj.annotation = Any

        self.extra_fields[name] = field_obj

        if value is not LN_UNDEFINED:
            value = SysUtil.copy(value)

        else:
            if getattr(self, name, LN_UNDEFINED) is not LN_UNDEFINED:
                value = getattr(self, name)

            elif getattr(field_obj, "default") is not PydanticUndefined:
                value = SysUtil.copy(field_obj.default)

            elif getattr(field_obj, "default_factory"):
                value = field_obj.default_factory()

            else:
                value = LN_UNDEFINED

        setattr(self, name, value)
        self._add_last_update(name)

    def _add_last_update(self, name: str) -> None:
        """Add or update the last update timestamp for a field.

        Args:
            name: The name of the field being updated.
        """
        current_time = SysUtil.time()
        self.metadata.set(["last_updated", name], current_time)

    def to_dict(self, **kwargs):
        dict_ = self.model_dump(**kwargs)
        extra_fields = dict_.pop("extra_fields", {})
        dict_ = {**dict_, **extra_fields, "lion_class": self.class_name()}
        return dict_

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute and update the last update timestamp.

        Args:
            name: The name of the attribute to set.
            value: The value to set.

        Raises:
            AttributeError: If attempting to directly assign to metadata.
        """
        if name == "metadata":
            raise AttributeError("Cannot directly assign to metadata.")
        if name in self.extra_fields:
            object.__setattr__(self, name, value)
        else:
            super().__setattr__(name, value)

        # super().__setattr__(name, value)
        self._add_last_update(name)

    def __getattr__(self, name: str) -> Any:
        """Get an attribute, handling extra fields.

        Args:
            name: The name of the attribute to get.

        Returns:
            The value of the attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        if name in self.extra_fields:
            return self.extra_fields[name].default if self.extra_fields[name].default is not PydanticUndefined else LN_UNDEFINED
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __str__(self) -> str:
        """Return a concise string representation of the component."""
        content_preview = str(self.content)[:50]
        if len(content_preview) == 50:
            content_preview += "..."

        return (
            f"{self.__class__.__name__}("
            f"ln_id={self.ln_id[:8]}..., "
            f"timestamp={self._created_datetime}, "
            f"content='{content_preview}', "
            f"metadata_keys={list(self.metadata.keys())}, "
            f"extra_fields_keys={list(self.extra_fields.keys())})"
        )

    def __repr__(self) -> str:
        """Return a detailed string representation of the component."""

        def truncate_dict(
            d: dict[str, Any], max_items: int = 5, max_str_len: int = 50
        ) -> dict[str, Any]:
            items = list(d.items())[:max_items]
            truncated = {
                k: (
                    v[:max_str_len] + "..."
                    if isinstance(v, str) and len(v) > max_str_len
                    else v
                )
                for k, v in items
            }
            if len(d) > max_items:
                truncated["..."] = f"({len(d) - max_items} more items)"
            return truncated

        content_repr = repr(self.content)
        if len(content_repr) > 100:
            content_repr = content_repr[:97] + "..."

        dict_ = self.model_dump()
        extra_fields = dict_.pop("extra_fields", {})

        return (
            f"{self.class_name()}("
            f"ln_id={repr(self.ln_id)}, "
            f"timestamp={self._created_datetime}, "
            f"content={content_repr}, "
            f"metadata={truncate_dict(self.metadata.content)}, "
            f"extra_fields={truncate_dict(extra_fields)})"
        )

    # @classmethod
    # def get_converter_registry(cls) -> ConverterRegistry:
    #     """
    #     Get the converter registry for the class.
    #
    #     Returns:
    #         The ConverterRegistry instance for the class.
    #     """
    #     if isinstance(cls._converter_registry, type):
    #         cls._converter_registry = cls._converter_registry()
    #     return cls._converter_registry

    # def convert_to(self, key: str = "dict", /, **kwargs: Any) -> Any:
    #     """
    #     Convert the component to a specified type using the ConverterRegistry.
    #
    #     Args:
    #         key: The key of the converter to use.
    #         **kwargs: Additional keyword arguments for conversion.
    #
    #     Returns:
    #         The converted component in the specified type.
    #     """
    #     return self.get_converter_registry().convert_to(self, key, **kwargs)

    # @classmethod
    # def convert_from(cls, obj: Any, key: str = "dict", /, *, unflat: bool = False) -> T:
    #     """
    #     Convert data to create a new component instance using the ConverterRegistry.
    #
    #     Args:
    #         obj: The object to convert from.
    #         key: The key of the converter to use.
    #         unflat: If True, unflatten the data before deserialization.
    #
    #     Returns:
    #         A new instance of the BaseComponent class or its subclass.
    #     """
    #     data = cls.get_converter_registry().convert_from(obj, key)
    #     return cls.deserialize(data, unflat=unflat)

    # @classmethod
    # def register_converter(cls, key: str, converter: Type[Converter]) -> None:
    #     """Register a new converter."""
    #     cls.get_converter_registry().register(key, converter)


# File: lion_core/generic/component.py
