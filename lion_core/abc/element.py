"""
Core Element class for the Lion framework.

Defines the Element class, serving as a base for all elements in the
framework. Extends AbstractElement and uses Pydantic's BaseModel for
data validation and serialization.

Classes:
    Element: Base class for all elements in the Lion framework.
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Any, TypeVar, ClassVar, Type

from pydantic import Field, BaseModel, ConfigDict, AliasChoices

from ..settings import LION_ID_CONFIG
from ..libs import SysUtil
from .concept import AbstractElement, Observable, Temporal


T = TypeVar("T", bound="Element")


class Element(AbstractElement, Observable, Temporal, BaseModel):
    """Base class for all elements in the Lion framework.

    This class extends AbstractElement and incorporates Pydantic's BaseModel
    for robust data validation and serialization. It provides a foundation
    for creating and managing elements within the Lion framework.

    Attributes:
        ln_id (str): A unique identifier for the element.
        timestamp (time): Creation timestamp of the element.

    Class Attributes:
        model_config (ConfigDict): Configuration for the Pydantic model.
        _class_registry (ClassVar[dict]): Registry for subclasses.
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

    content: Any = Field(
        default=None,
        description="The main content of the Element",
    )

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    _class_registry: ClassVar[dict[str, Type[Element]]] = {}

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        """Initialize subclass and register it in the class registry."""
        super().__pydantic_init_subclass__(**kwargs)
        cls._class_registry[cls.__name__] = cls

    @classmethod
    def get_class(cls, class_name: str) -> Type[Element]:
        """
        Get the class by name, using the class registry or MOR if not found.

        Args:
            class_name (str): The name of the class to retrieve.

        Returns:
            Type[Element]: The requested class.

        Raises:
            ValueError: If the class is not found in the registry or by MOR.
        """
        if class_name in cls._class_registry:
            return cls._class_registry[class_name]

        try:
            found_class = SysUtil.mor(class_name)
            if issubclass(found_class, Element):
                cls._class_registry[class_name] = found_class
                return found_class
            else:
                raise ValueError(f"{class_name} is not a subclass of Element")
        except ValueError as e:
            raise ValueError(f"Unable to find class {class_name}: {e}")

    @classmethod
    def from_dict(
        cls: Type[T],
        data: dict[str, Any],
        validation_config: dict[str, Any] = {},
        **kwargs,
    ) -> T:
        """Create an Element or its subclass instance from a dictionary.

        This method creates an instance based on the 'lion_class' key in the
        input dictionary. It uses the appropriate class to create the instance
        and performs validation.

        Args:
            data: The dictionary to create the instance from.
            validation_config: Configuration for validation.
            **kwargs: Additional keyword arguments.

        Returns:
            An instance of the Element class or its subclass.

        Raises:
            ValueError: If the dictionary is invalid for deserialization.
        """
        try:
            # Combine input data with additional kwargs
            combined_data = {**data, **kwargs}

            # Extract the class name and remove it from the data
            lion_class = combined_data.pop("lion_class", cls.__name__)

            # Get the appropriate class
            target_class = cls.get_class(lion_class)

            # Create and validate the instance
            instance = target_class(**combined_data)
            return target_class.model_validate(
                instance.model_dump(), **validation_config
            )
        except Exception as e:
            raise ValueError(f"Invalid data for deserialization: {e}")

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

    def to_dict(self, **kwargs) -> dict[str, Any]:
        """Convert the Element instance to a dictionary.

        Args:
            **kwargs: Additional arguments to pass to model_dump.

        Returns:
            dict: A dictionary representation of the Element instance.
        """
        kwargs["by_alias"] = kwargs.get("by_alias", True)
        return {
            "lion_class": self.class_name(),
            **self.model_dump(**kwargs),
        }


# File: lion_core/abc/element.py
