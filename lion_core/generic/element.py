"""
Core Element class for the Lion framework.

Provides functionality for identification, timestamping, and dynamic
class management. Integrates with Pydantic for data validation and
serialization.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator, field_serializer

from lion_core.abc.concept import AbstractElement
from lion_core.abc.characteristic import Temporal, Observable
from lion_core.setting import TIME_CONFIG
from lion_core.sys_util import SysUtil
from lion_core.class_registry import LION_CLASS_REGISTRY
from lion_core.exceptions import LionIDError

T = TypeVar("T", bound="Element")


class Element(BaseModel, AbstractElement, Observable, Temporal):
    """
    Base class for all elements in the Lion framework.

    Provides core functionality for identification, timestamping, and
    class registration. Integrates with Pydantic for data validation
    and uses mixins for additional characteristics.
    """

    ln_id: str = Field(
        default_factory=SysUtil.id,
        title="Lion ID",
        description="Unique identifier for the element",
        frozen=True,
        validation_alias=AliasChoices("id", "id_", "ID", "ID_"),
    )

    timestamp: float = Field(
        default_factory=lambda: SysUtil.time(type_="timestamp"),
        title="Creation Timestamp",
        frozen=True,
        alias="created",
    )

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize and register subclasses in the global class registry."""
        super().__pydantic_init_subclass__(**kwargs)
        LION_CLASS_REGISTRY[cls.__name__] = cls

    @property
    def _created_datetime(self) -> datetime:
        """Get the creation datetime of the Element."""
        return datetime.fromtimestamp(self.timestamp, tz=TIME_CONFIG["tz"])

    @field_validator("ln_id", mode="before")
    def _validate_id(cls, value):
        try:
            return SysUtil.get_lion_id(value)
        except:
            raise LionIDError(f"Invalid lion id: {value}")

    @field_validator("timestamp", mode="before")
    def _validate_timestamp(cls, value):
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Invalid datetime string format: {value}")
        if isinstance(value, datetime):
            return value.timestamp()
        elif isinstance(value, (float | int)):
            return value
        else:
            raise ValueError(f"Unsupported type for time_attr: {type(value)}")

    def to_dict(self, **kwargs):
        dict_ = self.model_dump(**kwargs)
        dict_["lion_class"] = self.class_name()
        return dict_

    def __str__(self) -> str:
        """Return a string representation of the Element."""
        timestamp_str = self._created_datetime.isoformat(timespec="minutes")
        return (
            f"{self.class_name()}(ln_id={self.ln_id[:6]}.., "
            f"timestamp={timestamp_str})"
        )

    def __hash__(self) -> int:
        """Return a hash value for the Element."""
        return hash(self.ln_id)

    def __bool__(self) -> bool:
        """Element is always considered True."""
        return True


# File: lion_core/element.py
