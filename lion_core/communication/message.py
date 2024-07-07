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

from enum import Enum
from ..mail.mail import Field, BaseMail
from ..node.node import Node


# Enums for defining message fields and roles
class MessageField(str, Enum):
    """
    Enum to store message fields for consistent referencing.
    """

    LION_ID = "lion_id"
    TIMESTAMP = "timestamp"
    ROLE = "role"
    SENDER = "sender"
    RECIPIENT = "recipient"
    CONTENT = "content"


class MessageRole(str, Enum):
    """
    Enum for possible roles a message can assume in a conversation.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


# Base class for messages
class RoledMessage(BaseMail, Node):
    """
    A base class representing a message with validators and properties.
    """

    role: MessageRole | None = Field(
        default=None,
        description="The role of the message in the conversation.",
        examples=["system", "user", "assistant"],
    )

    @property
    def image_content(self):
        msg_ = self.chat_msg
        if isinstance(msg_, dict) and isinstance(msg_["content"], list):
            return [i for i in msg_["content"] if i["type"] == "image_url"]

        return None

    @property
    def chat_msg(self) -> dict | None:
        """return message in chat representation"""
        try:
            return self._check_chat_msg()
        except:
            return None

    def _check_chat_msg(self):
        if self.role is None:
            raise ValueError("Message role not set")

        role = self.role.value if isinstance(self.role, Enum) else self.role
        if role not in [i.value for i in MessageRole]:
            raise ValueError(f"Invalid message role: {role}")

        content_dict = self.content.copy()

        if not content_dict.get("images", None):
            if len(content_dict) == 1:
                content_dict = str(list(content_dict.values())[0])
            else:
                content_dict = str(content_dict)

        return {"role": role, "content": content_dict}

    def __str__(self):
        """
        Provides a string representation of the message with content preview.
        """
        content_preview = (
            f"{str(self.content)[:75]}..."
            if len(str(self.content)) > 75
            else str(self.content)
        )
        return f"Message(role={self.role}, sender={self.sender}, content='{content_preview}')"
