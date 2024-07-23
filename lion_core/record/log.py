"""Base module for logging in the Lion framework."""

from __future__ import annotations
from typing import Any

from pydantic import Field
from lion_core.abc import ImmutableRecord
from lion_core.generic.note import Note
from lion_core.generic.element import Element


class BaseLog(Element, ImmutableRecord):

    content: Note = Field(
        None,
        title="Log Content",
        description="The content of the log entry.",
        frozen=True,
    )

    loginfo: Note = Field(
        None,
        title="Log Info",
        description="Metadata about the log entry.",
        frozen=True,
    )

    def __init__(
        self, *, content: dict | Note = None, loginfo: Note | dict = None, **data: Any
    ) -> None:
        if content:
            if isinstance(content, dict):
                data = {**content, **data}
            elif isinstance(content, Note):
                data = {**content.to_dict(), **data}

        content_ = Note(content=data)
        loginfo_ = Note(**loginfo) if isinstance(loginfo, dict) else loginfo
        super().__init__(content=content_, loginfo=loginfo_)

    def to_dict(self):
        d = super().to_dict()
        d["content"] = self.content.to_dict()
        d["loginfo"] = self.loginfo.to_dict()
        return d

    @classmethod
    def from_dict(cls, dict_):
        if "lion_class" in dict_ and dict_["lion_class"] == "BaseLog":
            dict_.pop("lion_class")

        content = Note.from_dict(dict_["content"])
        loginfo = Note.from_dict(dict_["loginfo"])
        return cls(content=content, loginfo=loginfo)


# File: lion_core/log/base.py
