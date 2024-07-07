"""
Core Component class for the Lion framework.

This module defines the Component class, which extends the Element class
and provides additional functionality for managing metadata, extra fields,
and content. It includes methods for conversion, serialization, and field
management.

Classes:
    Component: Extended base class for components in the Lion framework.
"""

from __future__ import annotations
from typing import Any, TypeVar, Type

from pydantic import (
    Field,
    ValidationError,
    model_validator,
    field_serializer,
    PrivateAttr,
)
from pydantic.fields import FieldInfo

from lion_core.util.settings import BASE_LION_FIELDS, ConverterRegistry
from lion_core.libs import SysUtil, nget, ninsert, nset, npop
from lion_core.abc.element import Element

T = TypeVar("T", bound="Component")


class Component(Element):
    """
    Extended base class for components in the Lion framework.

    This class builds upon the Element class, adding support for metadata,
    extra fields, and content. It provides methods for conversion,
    serialization, and field management.

    Attributes:
        metadata (dict): Additional metadata for the component.
        content (Any): The main content of the component.
        _extra_fields (dict): Extra fields not defined in the base model.
    """

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the component",
    )

    content: Any = Field(
        default=None,
        description="The main content of the component",
    )

    _extra_fields: dict[str, Any] = PrivateAttr(default_factory=dict)

    @property
    def extra_fields(self) -> dict[str, Any]:
        """Get all extra fields of the component."""
        return self._extra_fields

    @property
    def all_fields(self) -> dict[str, Any]:
        """Get all fields of the component, including extra fields."""
        return {**self.model_fields, **self._extra_fields}

    @classmethod
    def from_obj(cls: Type[T], obj: Any, converter_key: str) -> T:
        """Create a Component instance from any object using a converter."""
        dict_data = ConverterRegistry.convert_from(obj, converter_key)
        return cls.from_dict(dict_data)

    @classmethod
    def from_dict(cls: Type[T], obj: dict, validation_config: dict = {}, **kwargs) -> T:
        """Create a Component or its subclass instance from a dictionary."""
        try:
            dict_ = {**obj, **kwargs}
            extra_fields = dict_.pop("extra_fields", {})
            instance = cls.model_validate(dict_, **validation_config)
            for name, value in extra_fields.items():
                if isinstance(value, dict):
                    instance.add_field(name, FieldInfo(**value))
                else:
                    instance.add_field(name, FieldInfo(default=value))
            return instance
        except ValidationError as e:
            raise ValueError("Invalid dictionary for deserialization.") from e

    @model_validator(mode="before")
    @classmethod
    def _process_generic_dict(cls, data: Any) -> Any:
        """Process input data before model validation."""
        if not isinstance(data, dict):
            return data

        meta_ = data.pop("metadata", {})
        extra_fields = data.pop("extra_fields", {})

        for key in list(data.keys()):
            if key not in BASE_LION_FIELDS and key not in cls.model_fields:
                extra_fields[key] = data.pop(key)

        if not data.get("content", None):
            for field in ["data", "text", "page_content", "chunk_content"]:
                if field in extra_fields:
                    data["content"] = extra_fields.pop(field)
                    break

        data["metadata"] = meta_
        data["_extra_fields"] = extra_fields
        return data

    def to_obj(self, converter_key: str) -> Any:
        """Convert this Component instance to another object type."""
        return ConverterRegistry.convert_to(self, converter_key)

    def to_dict(self, **kwargs) -> dict[str, Any]:
        """Convert the component to a dictionary."""
        dict_ = self.model_dump(by_alias=True, exclude_none=True, **kwargs)
        dict_["lion_class"] = self.class_name()
        dict_["extra_fields"] = {
            k: v.model_dump() if isinstance(v, FieldInfo) else v
            for k, v in self._extra_fields.items()
        }
        return dict_

    @field_serializer("metadata")
    def serialize_dict(self, value: dict, _info):
        """Custom serializer for dictionary fields."""
        return {k: v for k, v in value.items() if v is not None}

    def add_field(
        self,
        field_name,
        value=...,
        annotation=None,
        default=None,
        field_obj=None,
        **kwargs,
    ):
        """Add a new field to the component's extra fields."""
        if field_name in self.all_fields:
            raise ValueError(f"Field '{field_name}' already exists")

        if field_obj is None:
            field_obj: FieldInfo = Field(default=default, **kwargs)
            field_obj.annotation = annotation

        self._extra_fields[field_name] = field_obj
        if value is ...:
            setattr(self, field_name, SysUtil.copy(field_obj.default))
        else:
            setattr(self, field_name, SysUtil.copy(value))

        self._add_last_update(field_name)

    def update_field(self, name: str, field: FieldInfo) -> None:
        """Update an existing field in the component's extra fields."""
        if name not in self._extra_fields:
            raise ValueError(f"Field '{name}' does not exist in extra fields")
        self._extra_fields[name] = field
        current_value = getattr(self, name, field.default)
        setattr(self, name, SysUtil.copy(current_value))
        self._add_last_update(name)

    def _add_last_update(self, name: str) -> None:
        """Add or update the last update timestamp for a field."""
        current_time = SysUtil.time()
        nset(self.metadata, ["last_updated", name], current_time)

    def _meta_pop(self, indices, default=...) -> Any:
        """Remove and return an item from the metadata."""
        return npop(self.metadata, indices, default)

    def _meta_insert(self, indices, value) -> None:
        """Insert a value into the metadata at the specified indices."""
        ninsert(self.metadata, indices, value)

    def _meta_set(self, indices, value) -> None:
        """Set a value in the metadata at the specified indices."""
        if not self._meta_get(indices):
            self._meta_insert(indices, value)
        else:
            nset(self.metadata, indices, value)

    def _meta_get(self, indices, default=...) -> Any:
        """Get a value from the metadata at the specified indices."""
        return nget(self.metadata, indices, default)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute and update the last update timestamp."""
        if name == "metadata":
            raise AttributeError("Cannot directly assign to metadata.")

        if name in self._extra_fields:
            if isinstance(self._extra_fields[name], FieldInfo):
                self._extra_fields[name].default = value
            else:
                self._extra_fields[name] = FieldInfo(default=value)

        super().__setattr__(name, value)
        self._add_last_update(name)

    def __getattr__(self, name: str) -> Any:
        """Get an attribute, handling extra fields."""
        if name in self._extra_fields:
            return self._extra_fields[name].default
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
            f"timestamp={self.timestamp.isoformat()}, "
            f"content='{content_preview}', "
            f"metadata_keys={list(self.metadata.keys())}, "
            f"extra_fields_keys={list(self._extra_fields.keys())})"
        )

    def __repr__(self) -> str:
        """Return a detailed string representation of the component."""

        def truncate_dict(d, max_items=5, max_str_len=50):
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
            f"timestamp={self.timestamp.isoformat()}, "
            f"content={content_repr}, "
            f"metadata={truncate_dict(self.metadata)}, "
            f"extra_fields={truncate_dict(self._extra_fields)})"
        )


# File: lion_core/observable/generic/component.py
