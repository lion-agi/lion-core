"""
Module defining the core Element class for the Lion framework.

This module contains the Element class, which serves as the foundation
for all objects within the Lion framework. It provides essential
attributes and methods for identification, timestamping, and dynamic
class management.

The Element class is designed to be extensible and integrates with
Pydantic for robust data validation and serialization.

Key components:
- Element: The base class for all Lion framework objects.
- LION_CLASS_REGISTRY: Global registry for Element subclasses.

Usage:
    from lion_core.abc.element import Element

    class MyCustomElement(Element):
        # Custom attributes and methods

    instance = MyCustomElement()
"""

from __future__ import annotations

from datetime import time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, AliasChoices

from lion_core.abc.concept import AbstractElement
from lion_core.abc.characteristic import Observable, Temporal
from lion_core.settings import LION_ID_CONFIG
from lion_core.util.sys_util import SysUtil
from lion_core.util.class_registry_util import LION_CLASS_REGISTRY, get_class


class Element(BaseModel, AbstractElement, Observable, Temporal):
    """
    Base class for all elements in the Lion framework.

    This class provides core functionality for identification, timestamping,
    and class registration. It integrates with Pydantic for data validation
    and uses mixins for additional characteristics.

    Attributes:
        ln_id: A unique identifier for the element.
        timestamp: The creation timestamp of the element.

    Class Methods:
        __pydantic_init_subclass__: Automatically registers subclasses.
        _get_class: Retrieves classes by name from the registry.
        class_name: Returns the name of the class.

    Usage:
        class MyElement(Element):
            custom_field: str

        element = MyElement(custom_field="value")
        print(element.ln_id)  # Unique identifier
        print(element.timestamp)  # Creation time
    """

    ln_id: str = Field(
        default_factory=lambda: SysUtil.id(**LION_ID_CONFIG),
        title="Lion ID",
        description="A unique identifier for the element",
        frozen=True,
        validation_alias=AliasChoices("id", "id_", "ID", "ID_"),
    )

    timestamp: time = Field(
        default_factory=lambda: SysUtil.time(type_="datetime"),
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

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """
        Initialize and register subclasses in the global class registry.

        This method is automatically called when a subclass of Element
        is created, ensuring that all subclasses are properly registered
        for dynamic class retrieval.

        Args:
            **kwargs: Additional keyword arguments passed to the superclass.
        """
        super().__pydantic_init_subclass__(**kwargs)
        LION_CLASS_REGISTRY[cls.__name__] = cls

    @classmethod
    def class_name(cls) -> str:
        """
        Get the name of the class.

        Returns:
            The name of the class.
        """
        return cls.__name__

    def __str__(self) -> str:
        """
        Return a string representation of the Element.

        Returns:
            A string containing the class name, truncated ln_id,
            and formatted timestamp.
        """
        timestamp_str = self.timestamp.isoformat(timespec="minutes")
        return (
            f"{self.class_name()}(ln_id={self.ln_id[:6]}.., "
            f"timestamp={timestamp_str})"
        )


# File: lion_core/abc/element.py
