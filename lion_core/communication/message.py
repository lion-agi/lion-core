"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import annotations

import inspect
from enum import Enum
from typing import Any
from pydantic import Field, field_validator
from lion_core.abc import Relational
from lion_core.generic.note import Note
from lion_core.generic.component import Component
from lion_core.communication.mail import BaseMail


class MessageField(str, Enum):
    """Enum to store message fields for consistent referencing."""

    LION_ID = "lion_id"
    TIMESTAMP = "timestamp"
    ROLE = "role"
    SENDER = "sender"
    RECIPIENT = "recipient"
    CONTENT = "content"


class MessageRole(str, Enum):
    """Enum for possible roles a message can assume in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessageCloneFlag(str, Enum):
    """Enum to signal constructing a clone Message"""

    MESSAGE_CLONE = "MESSAGE_CLONE"


class RoledMessage(Relational, Component, BaseMail):
    """A base class representing a message with validators and properties."""

    content: Note = Field(
        default_factory=Note,
        description="The content of the message.",
    )

    role: MessageRole | None = Field(
        default=None,
        description="The role of the message in the conversation.",
        examples=["system", "user", "assistant"],
    )

    @property
    def image_content(self) -> list[dict[str, Any]] | None:
        """Return image content if present in the message."""
        msg_ = self.chat_msg
        if isinstance(msg_, dict) and isinstance(msg_["content"], list):
            return [i for i in msg_["content"] if i["type"] == "image_url"]
        return None

    @property
    def chat_msg(self) -> dict[str, Any] | None:
        """Return message in chat representation."""
        try:
            return self._format_content()
        except Exception:
            return None

    @field_validator("role")
    def _validate_role(cls, v: Any) -> MessageRole | None:
        if v in MessageRole:
            return MessageRole(v)
        raise ValueError(f"Invalid message role: {v}")

    def _format_content(self) -> dict[str, Any]:
        if self.content.get("images", None):
            content = self.content.to_dict()
        else:
            content = str(self.content.to_dict())
        return {"role": self.role.value, "content": content}

    def clone(self) -> RoledMessage:
        """Creates a copy of the current System object."""

        cls = self.__class__
        signature = inspect.signature(cls.__init__)
        param_num = len(signature.parameters) - 1

        init_args = [MessageCloneFlag.MESSAGE_CLONE] * param_num

        obj = cls(*init_args)
        obj.content = self.content
        obj.metadata.set("clone_from", self)

        return obj

    def __str__(self) -> str:
        """Provide a string representation of the message with content preview."""
        content_preview = (
            f"{str(self.content)[:75]}..."
            if len(str(self.content)) > 75
            else str(self.content)
        )
        return (
            f"Message(role={self.role}, sender={self.sender}, "
            f"content='{content_preview}')"
        )


# File: lion_core/communication/message.py
