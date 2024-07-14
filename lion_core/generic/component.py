"""
Core Component class for the Lion framework.

This module defines the Component class, which extends the BaseComponent
class and provides additional functionality for managing metadata, extra
fields, and content. It includes methods for conversion, serialization,
and field management.

Classes:
    Component: Extended base class for components in the Lion framework.
"""

from __future__ import annotations
from typing import Any, TypeVar, ClassVar, Type

from pydantic import Field, model_serializer, field_serializer
from pydantic import field_validator
from pydantic.fields import FieldInfo

from lion_core.sys_util import SysUtil, LN_UNDEFINED
from lion_core.exceptions import LionValueError
from lion_core.converter import ConverterRegistry
from .base import BaseComponent

T = TypeVar("T", bound="BaseComponent")

DEFAULT_SERIALIZATION_INCLUDE: set[str] = {
    "metadata",
    "content",
    "ln_id",
    "timestamp",
    "extra_fields",
    "embedding",
}


class Component(BaseComponent):
    """Extended base class for components in the Lion framework."""

    extra_fields: dict[str, FieldInfo] = Field(
        default={},
        description="Additional fields for the component",
    )

    embedding: list[float] = Field(default=[])

    _converter_registry: ClassVar[Type[ConverterRegistry]] = ConverterRegistry

    @field_serializer("extra_fields")
    def _serialize_extra_fields(self, value: dict[str, FieldInfo]) -> dict[str, Any]:
        """Custom serializer for extra fields."""
        return {k: v.model_dump() for k, v in value.items()}

    @field_validator("extra_fields")
    def _validate_extra_fields(cls, value: Any) -> dict[str, FieldInfo]:
        """Custom validator for extra fields."""
        if not isinstance(value, dict):
            raise LionValueError("Extra fields must be a dictionary")
        return {k: Field(**v) if isinstance(v, dict) else v for k, v in value.items()}

    @model_serializer
    def serialize(self, **kwargs) -> dict[str, Any]:
        kwargs["include"] = kwargs.get("include", DEFAULT_SERIALIZATION_INCLUDE)
        return super().serialize(**kwargs)

    def add_field(
        self,
        name: str,
        value: Any = LN_UNDEFINED,
        annotation: Any = None,
        field_obj: FieldInfo | None = None,
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

        # if we are not provided with a field object,
        if field_obj is LN_UNDEFINED:

            # we first check we check whether the field already exist
            field_obj = self.all_fields.get(name, LN_UNDEFINED)

        # if not, we create a new field object
        if field_obj is LN_UNDEFINED:
            field_obj = Field(**kwargs)

            # and add it to the extra fields
            self.extra_fields[name] = field_obj

        # if already exist, we update the field object with the provided kwargs
        else:
            for k, v in kwargs.items():
                setattr(field_obj, k, v)

        # if annotation is provided, we update the field object annotation directly
        if not annotation is LN_UNDEFINED:
            field_obj.annotation = annotation
        else:

            # else we assign Any if no existing annotation
            if not field_obj.annotation:
                field_obj.annotation = Any

        # now we can check value
        if not value is LN_UNDEFINED:
            value = SysUtil.copy(value)

        else:
            # if there is already existing value, we return
            if getattr(self, name, LN_UNDEFINED) is not LN_UNDEFINED:
                return

            # if not, we check whether there is a default value or default factory
            if hasattr(field_obj, "default"):
                value = SysUtil.copy(field_obj.default)

            elif hasattr(field_obj, "default_factory"):
                value = field_obj.default_factory()

            # if not, we set it to None
            else:
                value = None

        setattr(self, name, value)
        self._add_last_update(name)

    def _add_last_update(self, name: str) -> None:
        """Add or update the last update timestamp for a field.

        Args:
            name: The name of the field being updated.
        """
        current_time = SysUtil.time()
        self.metadata.set(["last_updated", name], current_time)

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
            return self.extra_fields[name].default
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

        return (
            f"{self.__class__.__name__}("
            f"ln_id={repr(self.ln_id)}, "
            f"timestamp={self._created_datetime}, "
            f"content={content_repr}, "
            f"metadata={truncate_dict(self.metadata.serialize())}, "
            f"extra_fields={truncate_dict(self.extra_fields)})"
        )


# File: lion_core/generic/component.py
