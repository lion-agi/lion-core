"""Base module for logging in the Lion framework."""

from pydantic import Field, field_serializer, field_validator
from lion_core.libs import to_dict
from lion_core.abc import ImmutableRecord
from lion_core.generic.note import Note
from lion_core.generic.element import Element


class BaseLog(Element, ImmutableRecord):

    content: Note = Field(
        default_factory=Note,
        title="Log Content",
        description="The content of the log entry.",
        frozen=True,
    )

    loginfo: Note = Field(
        default_factory=Note,
        title="Log Info",
        description="Metadata about the log entry.",
        frozen=True,
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
        if isinstance(value, Note):
            return value
        if isinstance(value, dict):
            return Note.from_dict(value)
        try:
            return Note.from_dict(to_dict(value))
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


# File: lion_core/log/base.py
