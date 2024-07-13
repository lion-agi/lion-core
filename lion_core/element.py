"""
Core Element class for the Lion framework.

Provides functionality for identification, timestamping, and dynamic
class management. Integrates with Pydantic for data validation and
serialization.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

from lion_core.abc import AbstractElement, Observable, Temporal
from lion_core.setting import LION_ID_CONFIG, TIME_CONFIG
from .sys_util import SysUtil
from .class_registry import LION_CLASS_REGISTRY


class Element(BaseModel, AbstractElement, Observable, Temporal):
    """
    Base class for all elements in the Lion framework.

    Provides core functionality for identification, timestamping, and
    class registration. Integrates with Pydantic for data validation
    and uses mixins for additional characteristics.
    """

    ln_id: str = Field(
        default_factory=lambda: SysUtil.id(**LION_ID_CONFIG),
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
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize and register subclasses in the global class registry."""
        super().__pydantic_init_subclass__(**kwargs)
        LION_CLASS_REGISTRY[cls.__name__] = cls

    @classmethod
    def class_name(cls) -> str:
        """Get the name of the class."""
        return cls.__name__

    @property
    def _created_datetime(self) -> datetime:
        """Get the creation datetime of the Element."""
        return datetime.fromtimestamp(self.timestamp, tz=TIME_CONFIG["tz"])

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

    def __eq__(self, other: Any) -> bool:
        """Check ln_id equality with another object."""
        if not isinstance(other, Element):
            return NotImplemented
        return self.ln_id == other.ln_id
