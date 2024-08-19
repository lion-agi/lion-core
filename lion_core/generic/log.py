"""Base module for logging in the Lion framework."""

from pydantic import Field, field_serializer

from lion_core.abc import ImmutableRecord
from lion_core.generic.element import Element
from lion_core.generic.note import Note
from lion_core.libs import to_dict


class BaseLog(Element, ImmutableRecord):

    content: Note = Field(
        default_factory=Note,
        title="Log Content",
        description="The content of the log entry.",
    )

    loginfo: Note = Field(
        default_factory=Note,
        title="Log Info",
        description="Metadata about the log entry.",
    )

    def __init__(self, content: Note, loginfo: Note, **kwargs):
        super().__init__(**kwargs)
        self.content = self._validate_note(content)
        self.loginfo = self._validate_note(loginfo)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            content=cls._validate_note(data.get("content", {})),
            loginfo=cls._validate_note(data.get("loginfo", {})),
        )

    def _validate_note(cls, value):
        if not value:
            return Note()
        if isinstance(value, Note):
            return value
        if isinstance(value, dict):
            return Note(**value)
        try:
            return Note(**to_dict(value))
        except Exception as e:
            raise e

    @field_serializer("content", "loginfo")
    def _serialize_note(self, value):
        return value.to_dict()

    def to_dict(self):
        return {
            "content": self.content.to_dict(),
            "loginfo": self.loginfo.to_dict(),
        }

    def to_note(self):
        return Note(**self.to_dict())


__all__ = ["BaseLog"]
# File: lion_core/generic/log.py
