"""
Core Element class for the Lion framework.

This module defines the Element class, which serves as a base for all
elements in the Lion framework. It extends AbstractElement and incorporates
Pydantic's BaseModel for robust data validation.

Classes:
    Element: Base class for all elements in the Lion framework.
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Any, Type, TypeVar

from pydantic import Field, BaseModel, ConfigDict, AliasChoices

from lion_core.util.settings import LION_ID_CONFIG
from lion_core.libs import SysUtil
from .concept import AbstractElement, Observable, Temporal


T = TypeVar("T", bound=AbstractElement)


_INIT_CLASS = {}


class Element(AbstractElement, Observable, Temporal, BaseModel):
    """Base class for all elements in the Lion framework.

    This class extends AbstractElement and incorporates Pydantic's BaseModel
    for robust data validation and serialization. It provides a foundation
    for creating and managing elements within the Lion framework.

    Attributes:
        ln_id (str): A unique identifier for the element.
        timestamp (float): Creation timestamp of the element.

    Class Attributes:
        model_config (ConfigDict): Configuration for the Pydantic model.
    """

    ln_id: str = Field(
        default_factory=lambda: SysUtil.id(**LION_ID_CONFIG),
        title="Lion ID",
        description="A unique identifier for the component",
        frozen=True,
        validation_alias=AliasChoices("id", "id_", "ID", "ID_"),
    )

    timestamp: time = Field(
        default_factory=SysUtil.time,
        title="Creation Timestamp",
        frozen=True,
        alias="created",
    )

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    def __init_subclass__(cls: Type[Element], **kwargs):
        """Register subclasses in the _INIT_CLASS dictionary."""
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in _INIT_CLASS:
            _INIT_CLASS[cls.__name__] = cls

    @classmethod
    def class_name(cls) -> str:
        """Get the name of the class.

        Returns:
            str: The name of the class.
        """
        return cls.__name__

    def __str__(self) -> str:
        """Return a string representation of the Element.

        Returns:
            str: A string representation of the Element.
        """
        timestamp_str = datetime.fromtimestamp(self.timestamp).isoformat(
            timespec="minutes"
        )
        return (
            f"{self.class_name()}(ln_id={self.ln_id[:6]}.., "
            f"timestamp={timestamp_str})"
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Element:
        """Create an Element instance from a dictionary.

        Args:
            data: A dictionary containing element data.

        Returns:
            An instance of the Element class or its subclass.

        Raises:
            ValueError: If the dictionary is invalid for deserialization.
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid dictionary for deserialization: Not a dict")
        class_name = data.get("class_name", cls.__name__)
        element_class = _INIT_CLASS.get(class_name, cls)
        try:
            return element_class(**data)
        except Exception as e:
            raise ValueError(f"Invalid dictionary for deserialization: {e}") from e

    def to_dict(self, **kwargs) -> dict[str, Any]:
        """Convert the Element instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Element instance.
        """
        kwargs["by_alias"] = kwargs.pop("by_alias", True)
        return {
            "class_name": self.class_name(),
            **self.model_dump(by_alias=True, **kwargs),
        }


# File: lion_core/abc/element.py
