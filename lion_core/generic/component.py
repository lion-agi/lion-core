"""Core Component class for the Lion framework.

This module defines the Component class, which extends the Element class
and provides additional functionality for managing metadata, extra fields,
and content. It includes methods for conversion, serialization, and field
management.

Classes:
    Component: Extended base class for components in the Lion framework.
"""

from __future__ import annotations
from typing import Any, TypeVar, ClassVar, Type

from pydantic import (
    Field,
    field_serializer,
)
from pydantic.fields import FieldInfo

from ..abc.element import Element
from ..libs import nget, ninsert, nset, npop
from ..util.sys_util import SysUtil


T = TypeVar("T", bound="Component")


class Component(Element):
    """Extended base class for components in the Lion framework.

    This class builds upon the Element class, adding support for metadata,
    extra fields, and content. It provides methods for conversion,
    serialization, and field management.

    Attributes:
        metadata (dict[str, Any]): Additional metadata for the component.
        content (Any): The main content of the component.
        extra_fields (dict[str, Any]): Extra fields not in the base model.
    """

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the component",
    )

    content: Any = Field(
        default=None,
        description="The main content of the Element",
    )

    embedding: list = Field(default_factory=list)

    extra_fields: dict[str, Any] = Field(default_factory=dict)

    _class_registry: ClassVar[dict[str, Type[Component]]] = {}

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        """Initialize subclass and register it in the class registry."""
        super().__pydantic_init_subclass__(**kwargs)
        cls._class_registry[cls.__name__] = cls

    # Refactor to use converter

    # @classmethod
    # def from_obj(cls: Type[T], obj: Any, converter_key: str) -> T:
    #     """Create a Component instance from any object using a converter.

    #     Args:
    #         obj: The object to convert.
    #         converter_key: The key for the converter to use.

    #     Returns:
    #         An instance of the Component class or its subclass.
    #     """
    #     dict_data = convert_from(obj, converter_key)
    #     return cls.from_dict(dict_data)

    # @classmethod
    # def from_dict(
    #     cls: Type[T],
    #     data: dict[str, Any],
    #     validation_config: dict[str, Any] = {},
    #     **kwargs,
    # ) -> T:
    #     """Create a Component or its subclass instance from a dictionary.

    #     This method overrides Element's from_dict to handle additional
    #     attributes specific to Component.

    #     Args:
    #         data: The dictionary to create the instance from.
    #         validation_config: Configuration for validation.
    #         **kwargs: Additional keyword arguments.

    #     Returns:
    #         An instance of the Component class or its subclass.

    #     Raises:
    #         ValueError: If the dictionary is invalid for deserialization.
    #     """
    #     try:
    #         # Combine input data with additional kwargs
    #         combined_data = {**data, **kwargs}

    #         # Extract the class name and remove it from the data
    #         lion_class = combined_data.pop("lion_class", cls.__name__)

    #         # Extract Component-specific data
    #         metadata = combined_data.pop("metadata", {})
    #         content = combined_data.pop("content", None)
    #         extra_fields = combined_data.pop("extra_fields", {})

    #         # Get the appropriate class
    #         target_class = cls._get_class(lion_class)

    #         # Use Element's from_dict for base attributes
    #         base_instance = super().from_dict(combined_data)

    #         # Create the instance using the target class
    #         instance = target_class(
    #             **base_instance.model_dump(),
    #             metadata=metadata,
    #             content=content,
    #         )

    #         # Add extra fields
    #         for name, value in extra_fields.items():
    #             if isinstance(value, dict):
    #                 instance.add_field(name, FieldInfo(**value))
    #             else:
    #                 instance.add_field(name, FieldInfo(default=value))

    #         # Perform any additional validation
    #         return target_class.model_validate(
    #             instance.model_dump(), **validation_config
    #         )
    #     except ValidationError as e:
    #         raise ValueError("Invalid dictionary for deserialization.") from e

    # @model_validator(mode="before")
    # @classmethod
    # def _process_generic_dict(cls, data: Any) -> Any:
    #     """Process input data before model validation.

    #     Args:
    #         data: The input data to process.

    #     Returns:
    #         The processed data.
    #     """
    #     if not isinstance(data, dict):
    #         return data

    #     meta_ = data.pop("metadata", {})
    #     extra_fields = data.pop("extra_fields", {})

    #     for key in list(data.keys()):
    #         if key not in BASE_LION_FIELDS and key not in cls.model_fields:
    #             extra_fields[key] = data.pop(key)

    #     if not data.get("content", None):
    #         for field in ["data", "text", "page_content", "chunk_content"]:
    #             if field in extra_fields:
    #                 data["content"] = extra_fields.pop(field)
    #                 break

    #     data["metadata"] = meta_
    #     data["_extra_fields"] = extra_fields
    #     return data

    # def to_obj(self, converter_key: str) -> Any:
    #     """Convert this Component instance to another object type.

    #     Args:
    #         converter_key: The key for the converter to use.

    #     Returns:
    #         The converted object.
    #     """
    #     return convert_to(self, converter_key)

    # def to_dict(self, **kwargs) -> dict[str, Any]:
    #     """Convert the component to a dictionary.

    #     Args:
    #         **kwargs: Additional keyword arguments for model_dump.

    #     Returns:
    #         A dictionary representation of the component.
    #     """
    #     dict_ = super().to_dict(**kwargs)
    #     dict_["extra_fields"] = {
    #         k: v.model_dump() if isinstance(v, FieldInfo) else v
    #         for k, v in self._extra_fields.items()
    #     }
    #     return dict_

    @field_serializer("metadata")
    def serialize_dict(self, value: dict[str, Any], _info) -> dict[str, Any]:
        """Custom serializer for dictionary fields.

        Args:
            value: The dictionary to serialize.
            _info: Additional serialization information (unused).

        Returns:
            The serialized dictionary.
        """
        return {k: v for k, v in value.items() if v is not None}

    @property
    def all_fields(self) -> dict[str, Any]:
        """Get all fields of the component, including extra fields."""
        return {**self.model_fields, **self.extra_fields}

    def add_field(
        self,
        name: str,
        value: Any = ...,
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
            raise ValueError(f"Field '{name}' already exists")

        self.update_field(
            name=name, value=value, annotation=annotation, field_obj=field_obj, **kwargs
        )

    def update_field(
        self,
        name: str,
        value: Any = ...,
        annotation: Any = None,
        field_obj: FieldInfo | None = None,
        **kwargs,
    ) -> None:
        """Update an existing field in the component's extra fields.

        Args:
            name: The name of the field to add.
            value: The value of the field.
            annotation: Type annotation for the field.
            field_obj: A pre-configured FieldInfo object.
            **kwargs: Additional keyword arguments for Field.
        """

        if field_obj is None:
            field_obj = Field(**kwargs)
        if annotation:
            field_obj.annotation = annotation
        self.extra_fields[name] = field_obj

        instance_value = (
            SysUtil.copy(value) if value is not ... else SysUtil.copy(field_obj.default)
        )
        if field_obj.default_factory and value is ...:
            instance_value = field_obj.default_factory()
        setattr(self, name, instance_value)

        self._add_last_update(name)

    def _add_last_update(self, name: str) -> None:
        """Add or update the last update timestamp for a field.

        Args:
            name: The name of the field being updated.
        """
        current_time = SysUtil.time(type_="datetime", iso=True)
        nset(self.metadata, ["last_updated", name], current_time)

    def meta_pop(self, indices: list[str], default: Any = ...) -> Any:
        """Remove and return an item from the metadata.

        Args:
            indices: The path to the item in the metadata.
            default: The default value to return if the item is not found.

        Returns:
            The removed item or the default value.
        """
        return npop(self.metadata, indices, default)

    def meta_insert(self, indices: list[str], value: Any) -> None:
        """Insert a value into the metadata at the specified indices.

        Args:
            indices: The path where to insert the value.
            value: The value to insert.
        """
        ninsert(self.metadata, indices, value)

    def meta_set(self, indices: list[str], value: Any) -> None:
        """Set a value in the metadata at the specified indices.

        Args:
            indices: The path where to set the value.
            value: The value to set.
        """
        if not self.meta_get(indices):
            self.meta_insert(indices, value)
        else:
            nset(self.metadata, indices, value)

    def meta_get(self, indices: list[str], default: Any = ...) -> Any:
        """Get a value from the metadata at the specified indices.

        Args:
            indices: The path to the value in the metadata.
            default: The default value to return if the item is not found.

        Returns:
            The value at the specified indices or the default value.
        """
        return nget(self.metadata, indices, default)

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
            f"metadata={truncate_dict(self.metadata)}, "
            f"extra_fields={truncate_dict(self.extra_fields)})"
        )


# File: lion_core/generic/component.py
