"""Core Element class for the Lion framework.

This module defines the Element class, which serves as a base for all
elements in the Lion framework. It combines AbstractElement and Temporal
characteristics with Pydantic's BaseModel for robust data validation.

Classes:
    Element: Base class for all elements in the Lion framework.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, BaseModel, ConfigDict, AliasChoices

from lion_core.setting import LION_ID_CONFIG
from lion_core.libs import SysUtil
from .tao import AbstractElement
from .concepts import Temporal


_INIT_CLASS = {}


class Element(AbstractElement, Temporal, BaseModel):
    """Base class for all elements in the Lion framework.

    This class combines AbstractElement and Temporal characteristics
    with Pydantic's BaseModel for robust data validation and serialization.

    Attributes:
        ln_id (str): A unique identifier for the element.
        timestamp (float): Creation timestamp of the element.

    Class Methods:
        class_name(): Returns the name of the class.
        from_dict(data: dict): Creates an Element instance from a dictionary.

    Methods:
        __str__(): Returns a string representation of the Element.
    """

    ln_id: str = Field(
        default_factory=lambda: SysUtil.id(**LION_ID_CONFIG),
        title="Lion ID",
        description="A unique identifier for the component",
        frozen=True,
        validation_alias=AliasChoices("id", "id_", "ID", "ID_")
    )

    timestamp: float = Field(
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

    def __init_subclass__(cls, **kwargs):
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
        return f"{self.class_name()}(ln_id={self.ln_id[:6]}.., timestamp={timestamp_str})"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Element:
        """Create an Element instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing element data.

        Returns:
            Element: An instance of the Element class or its subclass.

        Raises:
            ValueError: If the dictionary is invalid for deserialization.
        """
        class_name = data.get("class_name", cls.__name__)
        element_class = _INIT_CLASS.get(class_name, cls)
        try:
            return element_class(**data)
        except Exception as e:
            raise ValueError(f"Invalid dictionary for deserialization: {e}") from e
        
        
# lion_core/abc/element.py