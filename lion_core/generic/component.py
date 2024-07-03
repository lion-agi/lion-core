"""Core Component class for the Lion framework.

This module defines the Component class, which extends the Element class
and provides additional functionality for managing metadata, extra fields,
and content. It includes methods for conversion, serialization, and field
management.

Classes:
    Component: Extended base class for components in the Lion framework.
"""

from __future__ import annotations
from typing import Any, TypeVar, Type
from datetime import datetime
from copy import copy

from pydantic import Field, ValidationError
from pydantic.main import FieldInfo, AliasChoices

from lion_core.setting import BASE_LION_FIELDS
from lion_core.libs import SysUtil, nget, ninsert, nset, npop
from lion_core.abc import Element, _INIT_CLASS
from lion_core.util import ConverterRegistry

T = TypeVar("T", bound="Component")


class Component(Element):
    """Extended base class for components in the Lion framework.

    This class builds upon the Element class, adding support for metadata,
    extra fields, and content. It provides methods for conversion,
    serialization, and field management.

    Attributes:
        metadata (dict): Additional metadata for the component.
        extra_fields (dict): Extra fields not defined in the base model.
        content (Any): The main content of the component.
    """

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("meta", "info"),
    )

    extra_fields: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices(
            "extra", "additional_fields", "schema_extra", "extra_schema"
        ),
    )

    content: Any = Field(
        default=None,
        validation_alias=AliasChoices("text", "page_content", "chunk_content", "data"),
    )

    def all_fields(self) -> dict[str, Any]:
        """Get all fields of the component, including extra fields."""
        return {**self.model_fields, **self.extra_fields}

    @classmethod
    def from_obj(cls: Type[T], obj: Any, converter_key: str) -> T:
        """Create a Component instance from any object using a converter."""
        dict_data = ConverterRegistry.convert_from(obj, converter_key)
        return cls.from_dict(dict_data)

    @classmethod
    def from_dict(cls: Type[T], obj: dict, **kwargs) -> T:
        """Create a Component or its subclass instance from a dictionary."""
        try:
            dict_ = {**obj, **kwargs}

            if "lion_class" in dict_:
                class_name = dict_.pop("lion_class")
                if class_name not in _INIT_CLASS:
                    raise ValueError(f"Subclass {class_name} not registered")
                target_cls = _INIT_CLASS[class_name]
            else:
                target_cls = cls

            dict_ = target_cls._process_generic_dict(dict_)
            instance = target_cls.model_validate(dict_)

            for key, field_info in instance.extra_fields.items():
                value = dict_.get(key, field_info.default)
                setattr(instance, key, copy(value))

            return instance
        except ValidationError as e:
            raise ValueError("Invalid dictionary for deserialization.") from e

    @classmethod
    def _process_generic_dict(cls, dict_: dict) -> dict:
        """Process a generic dictionary for component creation."""
        meta_ = dict_.pop("metadata", None) or {}
        if not isinstance(meta_, dict):
            meta_ = {"extra_meta": meta_}

        for key in list(dict_.keys()):
            if key not in BASE_LION_FIELDS and key not in cls.model_fields:
                meta_[key] = dict_.pop(key)

        if not dict_.get("content", None):
            for field in ["page_content", "text", "chunk_content", "data"]:
                if field in meta_:
                    dict_["content"] = meta_.pop(field)
                    break

        dict_["metadata"] = meta_

        if "ln_id" not in dict_:
            dict_["ln_id"] = meta_.pop(
                "ln_id",
                SysUtil.id(
                    n=28,
                    prefix="ln_",
                    random_hyphen=True,
                    num_hyphens=4,
                    hyphen_start_index=6,
                    hyphen_end_index=24,
                ),
            )
        if "timestamp" not in dict_:
            dict_["timestamp"] = SysUtil.time()

        extra_fields = {}
        for key, value in meta_.items():
            if key not in BASE_LION_FIELDS and key not in cls.model_fields:
                extra_fields[key] = FieldInfo(default=value)

        dict_["extra_fields"] = extra_fields
        return dict_

    def to_obj(self, convert_registry: ConverterRegistry, converter_key: str) -> Any:
        """Convert this Component instance to another object type."""
        return convert_registry.convert_to(self, converter_key)

    def to_dict(self, by_alias=True, **kwargs) -> dict[str, Any]:
        """Convert the component to a dictionary."""
        dict_ = self.model_dump(by_alias=by_alias, **kwargs)
        for field_name in self.extra_fields:
            dict_[field_name] = getattr(self, field_name)
        dict_["lion_class"] = self.__class__.__name__
        return dict_

    def add_field(self, name: str, field: FieldInfo) -> None:
        """Add a new field to the component's extra fields."""
        if name in self.all_fields:
            raise ValueError(f"Field '{name}' already exists")
        self.extra_fields[name] = field
        setattr(self, name, copy(field.default))
        self._add_last_update(name)

    def update_field(self, name: str, field: FieldInfo) -> None:
        """Update an existing field in the component's extra fields."""
        if name not in self.extra_fields:
            raise ValueError(f"Field '{name}' does not exist in extra fields")
        self.extra_fields[name] = field
        current_value = getattr(self, name, field.default)
        setattr(self, name, copy(current_value))
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

    def __init_subclass__(cls, **kwargs):
        """Register subclasses in the _INIT_CLASS dictionary."""
        super().__init_subclass__(**kwargs)
        _INIT_CLASS[cls.__name__] = cls

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute and update the last update timestamp."""
        if name == "metadata":
            raise AttributeError("Cannot directly assign to metadata.")

        if name in self.extra_fields:
            self.extra_fields[name] = Field(default=value)

        super().__setattr__(name, value)
        self._add_last_update(name)

    def __str__(self) -> str:
        """Return a concise string representation of the component."""
        content_preview = str(self.content)[:50]
        if len(content_preview) == 50:
            content_preview += "..."

        return (
            f"{self.__class__.__name__}("
            f"ln_id={self.ln_id[:8]}..., "
            f"timestamp={datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M')}, "
            f"content='{content_preview}', "
            f"metadata_keys={list(self.metadata.keys())}, "
            f"extra_fields_keys={list(self.extra_fields.keys())})"
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
            f"timestamp={self.timestamp}, "
            f"content={content_repr}, "
            f"metadata={truncate_dict(self.metadata)}, "
            f"extra_fields={truncate_dict(self.extra_fields)})"
        )
        

# Path: lion_core/generic/component.py
