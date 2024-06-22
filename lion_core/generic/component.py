"""
Provides the Component class for flexible data representation and conversion.

This module defines the Component class, which serves as a versatile base for
creating and manipulating data objects. It offers methods for conversion
between various data formats and provides a robust foundation for building
more specialized data structures.

Key features:
- Flexible initialization from various data types
- Conversion to different formats (dict, JSON, XML, etc.)
- Metadata and extra fields support
- Subclass registration mechanism
"""

from typing import Any, TypeVar
from pandas import DataFrame, Series
from pydantic import BaseModel, Field, ValidationError, AliasChoices
from lion_core.abc import Temporal, LionTypeError
from lion_core.libs import SysUtils
import lion_core.libs as libs
from lion_core.setting import base_lion_fields
from lion_core.generic._mixins import ComponentMixin

T = TypeVar("T")

_init_class = {}


class Component(Temporal, BaseModel, ComponentMixin):
    """
    A versatile base component class with common attributes and methods.

    This class provides a foundation for creating data objects with built-in
    support for metadata, content, and various conversion methods. It can be
    used as-is or subclassed for more specific use cases.

    Attributes:
        ln_id (str): A unique identifier for the component.
        timestamp (str): Creation timestamp of the component.
        metadata (dict): Additional metadata for the component.
        extra_fields (dict): Additional fields for the component.
        content (Any): Optional content of the component.

    Example:
        >>> comp = Component(content="Hello, World!")
        >>> comp.ln_id
        'ln_abc123de-f456-gh78-i90j-klmnop123456'
        >>> comp.content
        'Hello, World!'
    """

    ln_id: str = Field(
        default_factory=lambda: SysUtils.id(
            n=28,
            random_hyphen=True,
            num_hyphens=4,
            hyphen_start_index=6,
            hyphen_end_index=24
        ),
        title="Lion ID",
        description="A 32 character unique identifier for the component",
        frozen=True,
        validation_alias=AliasChoices("node_id", "id_", "id"),
    )

    timestamp: str = Field(
        default_factory=SysUtils.time,
        title="Creation Timestamp",
        frozen=True,
        alias="created",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("meta", "info"),
        description="Additional metadata for the component.",
    )

    extra_fields: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional fields for the component.",
        validation_alias=AliasChoices(
            "extra", "additional_fields", "schema_extra", "extra_schema"
        ),
    )

    content: Any = Field(
        default=None,
        description="The optional content of the node.",
        validation_alias=AliasChoices(
            "text", "page_content", "chunk_content", "data"
        ),
    )

    class Config:
        """Model configuration settings."""

        extra = "allow"
        arbitrary_types_allowed = True
        populate_by_name = True
        use_enum_values = True

    def __init_subclass__(cls, **kwargs):
        """Register subclasses in the _init_class dictionary."""
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in _init_class:
            _init_class[cls.__name__] = cls

    @property
    def class_name(self) -> str:
        """Get the class name."""
        return self._class_name()

    @classmethod
    def _class_name(cls) -> str:
        """Get the class name."""
        return cls.__name__

    @classmethod
    def from_obj(cls, obj: Any, /, **kwargs) -> T:
        """
        Create a Component instance from various object types.

        This method serves as a flexible factory for creating Component
        instances from different data structures.

        Args:
            obj: The object to convert.
            **kwargs: Additional keyword arguments for customization.

        Returns:
            An instance of the Component class.

        Raises:
            LionTypeError: If the object type is unsupported.

        Examples:
            >>> comp = Component.from_obj({"content": "Hello", "meta": {"key": "value"}})
            >>> comp.content
            'Hello'
            >>> comp.metadata
            {'key': 'value'}

            >>> comp = Component.from_obj("[1, 2, 3]", fuzzy_parse=True)
            >>> comp.content
            [1, 2, 3]
        """
        if isinstance(obj, (dict, str, list, Series, DataFrame, BaseModel)):
            return cls._dispatch_from_obj(obj, **kwargs)

        type_ = str(type(obj))

        if "llama_index" in type_:
            return cls._from_llama_index(obj)
        elif "langchain" in type_:
            return cls._from_langchain(obj)

        raise LionTypeError(f"Unsupported type: {type(obj)}")

    def astype(self, type_name: str, **kwargs) -> T:
        """
        Convert the component to a specified type.

        This method allows for easy conversion of the Component instance
        to various data formats or structures.

        Args:
            type_name: The target type name (e.g., "json", "dict", "xml").
            **kwargs: Additional keyword arguments for the conversion.

        Returns:
            The converted object.

        Raises:
            LionTypeError: If the target type is unsupported.

        Examples:
            >>> comp = Component(content="Test", metadata={"key": "value"})
            >>> comp.astype("dict")
            {'ln_id': '...', 'timestamp': '...', 'content': 'Test', 'metadata': {'key': 'value'}, ...}

            >>> comp.astype("json_str")
            '{"ln_id": "...", "timestamp": "...", "content": "Test", "metadata": {"key": "value"}, ...}'
        """
        match libs.strip_lower(type_name):
            case "json_str" | "str":
                return self._to_json_str(**kwargs)
            case "json" | "dict":
                return self.to_dict(**kwargs)
            case "xml" | "xml_str":
                return self._to_xml(**kwargs)
            case "pd_series":
                return self.to_pd_series(**kwargs)
            case "llama_index" | "llama":
                return self.to_llama_index_node(**kwargs)
            case "langchain" | "lc":
                return self.to_langchain_doc(**kwargs)
            case "pydantic" | "pydanticmodel":
                return BaseModel(**self.to_dict(**kwargs))
            case "list":
                return [self]
            case _:
                raise LionTypeError(f"Unsupported type: {type_name}")

    def to_dict(self, *args, dropna=False, **kwargs) -> dict[str, Any]:
        """
        Convert the component to a dictionary.

        This method provides a complete dictionary representation of the
        Component, including all fields and metadata.

        Args:
            *args: Additional positional arguments.
            dropna: Whether to drop None values from the resulting dict.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary representation of the component.

        Example:
            >>> comp = Component(content="Test", metadata={"key": "value"})
            >>> comp.to_dict()
            {'ln_id': '...', 'timestamp': '...', 'content': 'Test', 'metadata': {'key': 'value'}, ...}
        """
        dict_ = self.model_dump(*args, by_alias=True, **kwargs)

        for field_name in list(self.extra_fields.keys()):
            if field_name not in dict_:
                dict_[field_name] = getattr(self, field_name, None)

        dict_.pop("extra_fields", None)
        dict_["lion_class"] = self.class_name
        if dropna:
            dict_ = {k: v for k, v in dict_.items() if v is not None}
        return dict_

    @classmethod
    def _dispatch_from_obj(cls, obj: Any, **kwargs) -> T:
        """
        Dispatch the from_obj method based on the input type.

        This internal method determines the appropriate conversion method
        based on the type of the input object.

        Args:
            obj: The object to convert.
            **kwargs: Additional keyword arguments.

        Returns:
            An instance of the Component class.
        """
        if isinstance(obj, dict):
            return cls._from_dict(obj, **kwargs)
        elif isinstance(obj, str):
            return cls._from_str(obj, **kwargs)
        elif isinstance(obj, list):
            return cls._from_list(obj, **kwargs)
        elif isinstance(obj, Series):
            return cls._from_pd_series(obj, **kwargs)
        elif isinstance(obj, DataFrame):
            return cls._from_pd_dataframe(obj, **kwargs)
        elif isinstance(obj, BaseModel):
            return cls._from_base_model(obj, **kwargs)

    @classmethod
    def _from_dict(cls, obj: dict, /, *args, **kwargs) -> T:
        """
        Create a Component instance from a dictionary.

        This method handles the conversion of a dictionary to a Component
        instance, including processing of special fields and validation.

        Args:
            obj: The dictionary to convert.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            An instance of the Component class.

        Raises:
            ValueError: If the dictionary is invalid for deserialization.
        """
        try:
            dict_ = {**obj, **kwargs}
            if "embedding" in dict_:
                dict_["embedding"] = cls._validate_embedding(
                    dict_["embedding"]
                )

            if "lion_class" in dict_:
                cls = _init_class.get(dict_.pop("lion_class"), cls)

            if "lc" in dict_:
                dict_ = cls._process_langchain_dict(dict_)
            else:
                dict_ = cls._process_generic_dict(dict_)

            return cls.model_validate(dict_, *args, **kwargs)

        except ValidationError as e:
            raise ValueError("Invalid dictionary for deserialization.") from e

    @classmethod
    def _process_generic_dict(cls, dict_: dict) -> dict:
        """
        Process a generic dictionary for component creation.

        This method handles the preprocessing of a dictionary before it's
        used to create a Component instance, ensuring all necessary fields
        are present and correctly formatted.

        Args:
            dict_: The dictionary to process.

        Returns:
            The processed dictionary.
        """
        meta_ = dict_.pop("metadata", None) or {}

        if not isinstance(meta_, dict):
            meta_ = {"extra_meta": meta_}

        for key in list(dict_.keys()):
            if key not in base_lion_fields:
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
                SysUtils.id(
                    n=28,
                    prefix="ln_",
                    random_hyphen=True,
                    num_hyphens=4,
                    hyphen_start_index=6,
                    hyphen_end_index=24,
                )
            )
        if "timestamp" not in dict_:
            dict_["timestamp"] = SysUtils.time()
        if "metadata" not in dict_:
            dict_["metadata"] = {}
        if "extra_fields" not in dict_:
            dict_["extra_fields"] = {}
        return dict_

    @classmethod
    def _from_str(cls, obj: str, /, *args, fuzzy_parse: bool = False,
                  **kwargs) -> T:
        """
        Create a Component instance from a JSON string.

        This method handles the conversion of a JSON string to a Component
        instance, with an option for fuzzy parsing of imperfect JSON.

        Args:
            obj: The JSON string to convert.
            *args: Additional positional arguments.
            fuzzy_parse: Whether to use fuzzy parsing for imperfect JSON.
            **kwargs: Additional keyword arguments.

        Returns:
            An instance of the Component class.

        Raises:
            ValueError: If the JSON is invalid for deserialization.
        """
        obj = libs.fuzzy_parse_json(obj) if fuzzy_parse else libs.to_dict(obj)
        try:
            return cls.from_obj(obj, *args, **kwargs)
        except ValidationError as e:
            raise ValueError("Invalid JSON for deserialization: ") from e

    @classmethod
    def _from_list(cls, obj: list, /, *args, **kwargs) -> list[T]:
        """
        Create a list of node instances from a list of objects.

        This method converts each item in the input list to a Component
        instance.

        Args:
            obj: The list of objects to convert.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A list of Component instances.
        """
        return [cls.from_obj(item, *args, **kwargs) for item in obj]

    def _to_xml(self, *args, dropna=False, **kwargs) -> str:
        """
        Convert the component to an XML string.

        This method provides an XML representation of the Component,
        useful for integration with XML-based systems.

        Args:
            *args: Additional positional arguments.
            dropna: Whether to drop None values from the resulting XML.
            **kwargs: Additional keyword arguments.

        Returns:
            An XML string representation of the component.
        """
        import xml.etree.ElementTree as ET

        root = ET.Element(self.__class__.__name__)

        def convert(dict_obj: dict, parent: ET.Element) -> None:
            for key, val in dict_obj.items():
                if isinstance(val, dict):
                    element = ET.SubElement(parent, key)
                    convert(val, element)
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(val)

        convert(self.to_dict(*args, dropna=dropna, **kwargs), root)
        return ET.tostring(root, encoding="unicode")

    def _to_json_str(self, *args, dropna=False, **kwargs) -> str:
        """
        Convert the component to a JSON string.

        This method provides a JSON string representation of the Component,
        useful for data exchange and serialization.

        Args:
            *args: Additional positional arguments.
            dropna: Whether to drop None values from the resulting JSON.
            **kwargs: Additional keyword arguments.

        Returns:
            A JSON string representation of the component.
        """
        dict_ = self.to_dict(*args, dropna=dropna, **kwargs)
        return libs.to_str(dict_)

    def __str__(self):
        """Return a string representation of the component."""
        dict_ = self.to_dict()
        return Series(dict_).__str__()

    def __repr__(self):
        dict_ = self.to_dict()
        return Series(dict_).__repr__()

    def __len__(self):
        return 1
