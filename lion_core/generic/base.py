"""Module containing the BaseComponent class for the Lion framework."""

from abc import abstractmethod
from typing import Any

from pydantic import Field, ConfigDict, field_serializer

from lion_core.element import Element
from lion_core.container.record import Record


class BaseComponent(Element):
    """
    Base class for components in the Lion framework.

    This class extends the Element class and overrides its model config
    to allow extra fields.
    """

    metadata: Record = Field(
        default_factory=Record,
        description="Additional metadata for the component",
    )

    content: Any = Field(
        default=None,
        description="The main content of the Element",
    )

    # override element model config to allow extra fields
    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    @field_serializer("metadata")
    def _serialize_meta(self, value: Record, _info) -> dict[str, Any]:
        """Custom serializer for dictionary fields."""
        return value.serialize(dropna=True)

    @abstractmethod
    def convert_to(self, *args, **kwargs) -> Any:
        """Convert the component to a specified type."""

    @classmethod
    @abstractmethod
    def convert_from(cls, *args, **kwargs) -> Any:
        """Convert data to create a new component instance."""


# File: lion_core/generic/base.py
