"""Base module for logging in the Lion framework."""

from __future__ import annotations
from typing import Any

from pydantic import BaseModel, Field, model_serializer, ConfigDict

from lion_core.primitives.note import Note
from lion_core.primitives.element import Element


from .base import ImmutableRecord


DEFAULT_SERIALIZATION_INCLUDE: set[str] = {"ln_id", "timestamp", "content", "loginfo"}


class LogInfo(BaseModel):

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )


class BaseLog(Element, ImmutableRecord):

    content: Note = Field(
        ...,
        title="Log Content",
        description="The content of the log entry.",
        frozen=True,
    )

    loginfo: LogInfo = Field(
        ...,
        title="Log Info",
        description="Metadata about the log entry.",
        frozen=True,
    )

    def __init__(self, *, loginfo: LogInfo | dict = None, **data: Any) -> None:
        content = Note(**data)
        loginfo = LogInfo(**loginfo) if isinstance(loginfo, dict) else loginfo
        super().__init__(content=content, loginfo=loginfo)

    @model_serializer
    def serialize(self, **kwargs: Any) -> dict:
        kwargs["include"] = kwargs.get("include", DEFAULT_SERIALIZATION_INCLUDE)
        return super().serialize(**kwargs)


# File: lion_core/log/base.py
