from datetime import datetime
from typing import Any, TypeVar

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator
from typing_extensions import override

from lion_core._class_registry import LION_CLASS_REGISTRY, get_class
from lion_core.abc._characteristic import Observable, Temporal
from lion_core.abc._concept import AbstractElement
from lion_core.exceptions import LionIDError
from lion_core.setting import TIME_CONFIG
from lion_core.sys_utils import SysUtil

T = TypeVar("T", bound="Element")


class Element(BaseModel, AbstractElement, Observable, Temporal):
    """Base class in the Lion framework."""

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
    def created_datetime(self) -> datetime:
        """Get the creation datetime of the Element."""
        return datetime.fromtimestamp(self.timestamp, tz=TIME_CONFIG["tz"])

    @field_validator("ln_id", mode="before")
    def _validate_id(cls, value) -> str:
        try:
            return SysUtil.get_id(value)
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

    @classmethod
    def from_dict(cls, data, **kwargs) -> T:
        """create an instance of the Element or its subclass from a dictionary."""
        if "lion_class" in data:
            cls = get_class(data.pop("lion_class"))
        if cls.from_dict.__func__ != Element.from_dict.__func__:
            return cls.from_dict(data, **kwargs)
        return cls.model_validate(data, **kwargs)

    def to_dict(self, **kwargs) -> dict:
        """Convert the Element to a dictionary representation."""
        dict_ = self.model_dump(**kwargs)
        dict_["lion_class"] = self.class_name()
        return dict_

    @override
    def __str__(self) -> str:
        timestamp_str = self.created_datetime.isoformat(timespec="minutes")
        return (
            f"{self.class_name()}(ln_id={self.ln_id[:6]}.., "
            f"timestamp={timestamp_str})"
        )

    def __hash__(self) -> int:
        return hash(self.ln_id)

    def __bool__(self) -> bool:
        """Always True"""
        return True

    def __len__(self) -> int:
        """Return the length of the Element."""
        return 1


__all__ = ["Element"]

# File: lion_core/generic/element.py
