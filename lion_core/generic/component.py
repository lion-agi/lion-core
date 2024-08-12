"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from collections import deque
from functools import singledispatchmethod
from typing import Any, TypeVar, ClassVar, Type
from typing_extensions import Annotated, override

from pydantic import Field, field_serializer, field_validator
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from lion_core.libs import strip_lower
from lion_core.sys_utils import SysUtil
from lion_core.setting import LN_UNDEFINED
from lion_core.exceptions import LionValueError
from lion_core._class_registry import get_class
from lion_core.converter import Converter
from lion_core.generic.component_converter import ComponentConverterRegistry
from lion_core.generic.element import Element
from lion_core.generic.note import Note

T = TypeVar("T", bound=Element)

DEFAULT_SERIALIZATION_INCLUDE: set[str] = {
    "metadata",
    "content",
    "ln_id",
    "timestamp",
    "embedding",
}


NAMED_FIELD = Annotated[str, Field(..., alias="field")]


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

    _converter_registry: ClassVar = ComponentConverterRegistry

    @field_serializer("metadata")
    def _serialize_metadata(self, value):
        return value.to_dict()

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
        """
        Get all fields including model fields and extra fields.

        Returns:
            dict[str, FieldInfo]: A dictionary containing all fields.
        """
        return {**self.model_fields, **self.extra_fields}

    def add_field(
        self,
        field_name: NAMED_FIELD,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo = LN_UNDEFINED,
        **kwargs,
    ) -> None:
        """
        Add a new field to the component's extra fields.

        Args:
            name: The name of the field to add.
            value: The value of the field. Defaults to `LN_UNDEFINED`.
            annotation: Type annotation for the field. Defaults to `LN_UNDEFINED`.
            field_obj: A pre-configured FieldInfo object. Defaults to `LN_UNDEFINED`.
            **kwargs: Additional keyword arguments for Field configuration.

        Raises:
            LionValueError: If the field already exists.
        """
        if field_name in self.all_fields:
            raise LionValueError(f"Field '{field_name}' already exists")

        self.update_field(
            field_name=field_name,
            value=value,
            annotation=annotation,
            field_obj=field_obj,
            **kwargs,
        )

    # when updating field, we do not check the validity of annotation
    # meaning current value will not get validated, and can lead to errors when storing and loading
    # if you change annotation to a type that is not compatible with the current value
    def update_field(
        self,
        field_name: NAMED_FIELD,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo | Any = LN_UNDEFINED,
        **kwargs,
    ) -> None:
        """
        Update an existing field or create a new one if it doesn't exist.

        Args:
            name: The name of the field to update or create.
            value: The new value for the field. Defaults to LN_UNDEFINED.
            annotation: Type annotation for the field. Defaults to LN_UNDEFINED.
            field_obj: A pre-configured FieldInfo object. Defaults to LN_UNDEFINED.
            **kwargs: Additional keyword arguments for Field configuration.

        Raises:
            ValueError: If both 'default' and 'default_factory' are provided in kwargs.
        """

        # pydanitc Field object cannot have both default and default_factory
        if "default" in kwargs and "default_factory" in kwargs:
            raise ValueError("Cannot provide both 'default' and 'default_factory'")

        # if passing kwargs
        if field_obj is LN_UNDEFINED:
            # check if field exists
            field_obj = self.all_fields.get(field_name, LN_UNDEFINED)

            if field_obj:  # existing field
                for k, v in kwargs.items():
                    setattr(field_obj, k, v)
            else:
                field_obj = Field(**kwargs)

        else:  # passing field_obj directly
            if not isinstance(field_obj, FieldInfo):
                raise ValueError(
                    "Invalid field_obj. It should be a pydantic FieldInfo object."
                )

        if annotation is not LN_UNDEFINED:
            field_obj.annotation = annotation
        if not field_obj.annotation:
            field_obj.annotation = Any

        self.extra_fields[field_name] = field_obj

        if value is not LN_UNDEFINED:
            value = SysUtil.copy(value)

        else:
            if getattr(self, field_name, LN_UNDEFINED) is not LN_UNDEFINED:
                value = getattr(self, field_name)

            elif getattr(field_obj, "default") is not PydanticUndefined:
                value = SysUtil.copy(field_obj.default)

            elif getattr(field_obj, "default_factory"):
                value = field_obj.default_factory()

            else:
                value = LN_UNDEFINED

        setattr(self, field_name, value)
        self._add_last_update(field_name)

    def _add_last_update(self, field_name: NAMED_FIELD) -> None:
        current_time = SysUtil.time()
        self.metadata.set(["last_updated", field_name], current_time)

    @override
    def to_dict(self, **kwargs) -> dict:
        """
        Convert the component to a dictionary representation.

        Args:
            **kwargs: Additional arguments to pass to model_dump.

        Returns:
            dict[str, Any]: A dictionary representation of the component.
        """
        dict_ = self.model_dump(**kwargs)
        if isinstance(self.content, Note):
            dict_["content"] = dict_["content"]["content"]
        extra_fields = dict_.pop("extra_fields", {})
        dict_ = {**dict_, **extra_fields, "lion_class": self.class_name()}
        return dict_

    @override
    @classmethod
    def from_dict(cls, data: dict, **kwargs) -> T:
        """
        Create a component instance from a dictionary.

        Args:
            data: The dictionary containing component data.
            **kwargs: Additional arguments for Pydantic model validation.

        Returns:
            T: An instance of the Component class or its subclass.
        """
        data = SysUtil.copy(data)
        if "lion_class" in data:
            cls = get_class(data.pop("lion_class"))
        if cls.from_dict.__func__ != Component.from_dict.__func__:
            return cls.from_dict(data, **kwargs)

        extra_fields = {}
        for k, v in list(data.items()):
            if k not in cls.model_fields:
                extra_fields[k] = data.pop(k)
        obj = cls.model_validate(data, **kwargs)
        for k, v in extra_fields.items():
            obj.add_field(field_name=k, value=v)

        metadata = data.get("metadata", {})
        last_updated = metadata.get("last_updated", None)
        if last_updated is not None:
            obj.metadata.set(["last_updated"], last_updated)
        return obj

    @override
    def __setattr__(self, field_name: str, value: Any) -> None:
        if field_name == "metadata":
            raise AttributeError("Cannot directly assign to metadata.")
        elif field_name == "extra_fields":
            raise AttributeError("Cannot directly assign to extra_fields")
        if field_name in self.extra_fields:
            object.__setattr__(self, field_name, value)
        else:
            super().__setattr__(field_name, value)

        self._add_last_update(field_name)

    @override
    def __getattr__(self, field_name: str) -> Any:
        if field_name in self.extra_fields:
            return (
                self.extra_fields[field_name].default
                if self.extra_fields[field_name].default is not PydanticUndefined
                else LN_UNDEFINED
            )
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{field_name}'"
        )

    @override
    def __str__(self) -> str:
        """Return a concise string representation of the component."""
        content_preview = str(self.content)[:50]
        if len(content_preview) == 50:
            content_preview += "..."

        output_str = (
            f"{self.__class__.__name__}("
            f"ln_id={self.ln_id[:8]}..., "
            f"timestamp={str(self._created_datetime)[:-6]}, "
            f"content='{content_preview}', "
            f"metadata_keys={list(self.metadata.keys())}, "
        )

        for i, j in self.model_dump().items():
            if i not in ["ln_id", "timestamp", "metadata", "content", "embedding"]:
                if isinstance(j, dict):
                    output_str += f"{i}={list(j.keys())}, "
                elif isinstance(j, str):
                    j_preview = j[:50]
                    if len(j_preview) == 50:
                        j_preview = j_preview + "..."
                    output_str += f"{i}={j_preview}, "
                else:
                    output_str += f"{i}={j}, "

        output_str += f"extra_fields_keys={list(self.extra_fields.keys())})"

        return output_str

    @override
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

        repr_str = (
            f"{self.class_name()}("
            f"ln_id={repr(self.ln_id)}, "
            f"timestamp={str(self._created_datetime)[:-6]}, "
            f"content={content_repr}, "
            f"metadata={truncate_dict(self.metadata.content)}, "
        )

        for i, j in dict_.items():
            if i not in ["ln_id", "timestamp", "metadata", "content", "embedding"]:
                if isinstance(j, dict):
                    repr_str += f"{i}={truncate_dict(j)}, "
                elif isinstance(j, str):
                    j_repr = j
                    if len(j) > 100:
                        j_repr = j[:97] + "..."
                    repr_str += f"{i}={j_repr}, "
                else:
                    repr_str += f"{i}={j}, "

        repr_str += f"extra_fields={truncate_dict(extra_fields)})"
        return repr_str

    # converter methods
    @classmethod
    def get_converter_registry(cls) -> ComponentConverterRegistry:
        """Get the converter registry for the class."""
        if isinstance(cls._converter_registry, type):
            cls._converter_registry = cls._converter_registry()
        return cls._converter_registry

    def convert_to(self, key: str = "dict", /, **kwargs: Any) -> Any:
        """Convert the component to a specified type using the ConverterRegistry."""
        return self.get_converter_registry().convert_to(self, key, **kwargs)

    @classmethod
    def convert_from(cls, obj: Any, key: str = "dict", /, **kwargs) -> T:
        """Convert data to create a new component instance using the ConverterRegistry."""
        data = cls.get_converter_registry().convert_from(cls, obj, key)
        return cls.from_dict(data, **kwargs)

    @classmethod
    def register_converter(cls, key: str, converter: Type[Converter]) -> None:
        """Register a new converter. Can be used for both a class and/or an instance."""
        cls.get_converter_registry().register(key, converter)

    # field management methods
    def field_setattr(self, field_name: str, attr: Any, value: Any, /):
        if not field_name in self.all_fields:
            raise KeyError(f"Field {field_name} not found in object all fields.")

        if field_name in self.model_fields:
            if hasattr(self.model_fields[field_name], attr):
                self.model_fields[field_name].__setattr__(attr, value)
            else:
                self.model_fields[field_name].json_schema_extra[attr] = value

        elif field_name in self.extra_fields:
            if hasattr(self.extra_fields[field_name], attr):
                self.extra_fields[field_name].__setattr__(attr, value)
            else:
                self.model_fields[field_name].json_schema_extra[attr] = value

    def field_hasattr(self, field_name: str, attr: str, /) -> bool:
        """Check if a field has a specific attribute."""

        if (field := self.all_fields.get(field_name, None)) is None:
            raise KeyError(f"Field {field_name} not found in model fields.")

        if attr not in str(field):
            try:
                a = (
                    attr in self.all_fields[field_name].json_schema_extra
                    and self.all_fields[field_name].json_schema_extra[attr]
                    is not LN_UNDEFINED
                )
                return a if isinstance(a, bool) else False
            except Exception:
                return False
        return True

    def field_getattr(
        self, field_name: str, attr: str, default: Any = LN_UNDEFINED, /
    ) -> Any:
        """Get the value of a field attribute."""

        if strip_lower(attr, chars="s") == "annotation":
            return self._field_annotation(field_name)

        try:
            if not field_name in self.all_fields:
                raise KeyError(f"Field {field_name} not found in object all fields.")

            if not self.field_hasattr(field_name, attr):
                raise AttributeError(f"field {field_name} has no attribute {attr}")

            field = self.all_fields[field_name]

            if (a := getattr(field, attr, LN_UNDEFINED)) is LN_UNDEFINED:
                if (
                    b := field.json_schema_extra.get(attr, LN_UNDEFINED)
                ) is not LN_UNDEFINED:
                    return b
            else:
                return a

            if default is not LN_UNDEFINED:
                return default
            raise AttributeError(f"field {field_name} has no attribute {attr}")

        except Exception as e:
            if default is not LN_UNDEFINED:
                return default
            raise AttributeError(f"field {field_name} has no attribute {attr}") from e

    @singledispatchmethod
    def _field_annotation(self, field_name: Any, /) -> dict[str, Any]:
        """
        Get field annotation for a given field.

        Args:
            field: The field to get annotation for.

        Returns:
            A dictionary containing the field annotation.
        """
        return {}

    @_field_annotation.register(str)
    def _(self, field_name: str, /) -> dict[str, Any]:
        dict_ = {field_name: self.all_fields[field_name].annotation}
        for _f, _anno in dict_.items():
            if "|" in str(_anno):
                _anno = str(_anno)
                _anno = _anno.split("|")
                dict_[_f] = [str(i).lower().strip() for i in _anno]
            else:
                dict_[_f] = [_anno.__name__] if _anno else None
        return dict_

    @_field_annotation.register(deque)
    @_field_annotation.register(set)
    @_field_annotation.register(list)
    @_field_annotation.register(tuple)
    def _(self, field_name, /) -> dict[str, Any]:
        dict_ = {}
        for f in field_name:
            dict_.update(self._field_annotation(f))
        return dict_


# File: lion_core/generic/component.py
