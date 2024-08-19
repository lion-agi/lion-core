import inspect
from enum import Enum
from typing import Any
from typing_extensions import override
from pydantic import Field, field_validator
from lion_core.abc import Relational
from lion_core.sys_utils import SysUtil
from lion_core._class_registry import get_class
from lion_core.generic.note import Note
from lion_core.generic.component import Component
from lion_core.communication.base_mail import BaseMail


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


class MessageFlag(str, Enum):
    """Enum to signal constructing a clone Message"""

    MESSAGE_CLONE = "MESSAGE_CLONE"
    MESSAGE_LOAD = "MESSAGE_LOAD"


class RoledMessage(Relational, Component, BaseMail):
    """
    A base class representing a message with roles, validators, and properties.

    The `RoledMessage` class is designed to encapsulate a message within a system
    where each message has a specific role, such as "system", "user", or "assistant".
    It includes functionality for validating the role, managing the content,
    handling images, and generating chat-friendly representations of the message.

    Inherits:
        - Relational: Provides relationship management features.
        - Component: Adds component-based functionalities.
        - BaseMail: Introduces sender and recipient fields for message routing.

    Attributes:
        content (Note): The content of the message, stored in a `Note` object.
        role (MessageRole | None): The role of the message in the conversation.
            It can be one of "system", "user", or "assistant".

    Properties:
        image_content (list[dict[str, Any]] | None): Returns the image content
            if present in the message, otherwise returns None.
        chat_msg (dict[str, Any] | None): Returns the message in a chat
            representation format, or None if an error occurs.

    Methods:
        clone() -> "RoledMessage":
            Creates a clone of the current `RoledMessage` object.
        from_dict(cls, data: dict, **kwargs) -> "RoledMessage":
            Loads a `RoledMessage` object from a dictionary.
        __str__() -> str:
            Provides a string representation of the message with a content preview.
    """

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
        """Validates the role of the message."""
        if v in [r.value for r in MessageRole]:
            return MessageRole(v)
        raise ValueError(f"Invalid message role: {v}")

    def _format_content(self) -> dict[str, Any]:
        """Format the message content for chat representation."""
        if self.content.get("images", None):
            content = self.content.to_dict()
        else:
            content = str(self.content.to_dict())
        return {"role": self.role.value, "content": content}

    def clone(self) -> "RoledMessage":
        """
        Creates a copy of the current `RoledMessage` object.

        The clone will have the same role and content as the original message,
        and will be marked with metadata indicating that it was cloned.

        Returns:
            RoledMessage: A new `RoledMessage` instance with identical content
                and role as the original.
        """

        cls = self.__class__
        signature = inspect.signature(cls.__init__)
        param_num = len(signature.parameters) - 2

        init_args = [MessageFlag.MESSAGE_CLONE] * param_num

        obj = cls(*init_args)
        obj.role = self.role
        obj.content = self.content
        obj.metadata.set("clone_from", self)

        return obj

    @override
    @classmethod
    def from_dict(cls, data: dict, **kwargs) -> "RoledMessage":
        """
        Loads a `RoledMessage` object from a dictionary.

        Args:
            data (dict): The dictionary containing the message data.
            **kwargs: Additional keyword arguments.

        Returns:
            RoledMessage: An instance of `RoledMessage` populated with the
                data from the dictionary.
        """
        data = SysUtil.copy(data)
        if "lion_class" in data:
            cls = get_class(data.pop("lion_class"))
        signature = inspect.signature(cls.__init__)
        param_num = len(signature.parameters) - 2

        init_args = [MessageFlag.MESSAGE_LOAD] * param_num

        extra_fields = {}
        for k, v in list(data.items()):
            if k not in cls.model_fields:
                extra_fields[k] = data.pop(k)

        obj = cls(*init_args, protected_init_params=data)

        for k, v in extra_fields.items():
            obj.add_field(name=k, value=v)

        metadata = data.get("metadata", {})
        last_updated = metadata.get("last_updated", None)
        if last_updated is not None:
            obj.metadata.set(["last_updated"], last_updated)
        return obj

    @override
    def __str__(self) -> str:
        """
        Provides a string representation of the message with a content preview.

        The preview is truncated to 75 characters to give a brief overview
        of the message content.

        Returns:
            str: A string summarizing the message role, sender, and a preview
                of the content.
        """
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
