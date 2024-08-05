from typing import Any, override

from lion_core.communication.message import (
    RoledMessage,
    MessageRole,
    MessageFlag,
)


class AssistantResponse(RoledMessage):
    """Represents a response from an assistant in the system."""

    @override
    def __init__(
        self,
        assistant_response: dict | MessageFlag,
        sender: Any | MessageFlag,
        recipient: Any | MessageFlag,
        protected_init_params: dict | None = None,
    ):
        message_flags = [assistant_response, sender, recipient]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",
            recipient=recipient,
        )
        if assistant_response:
            if isinstance(assistant_response, str):
                assistant_response = {"content": assistant_response}
            elif isinstance(assistant_response, dict):
                if not "content" in assistant_response:
                    a_ = {}
                    a_["content"] = assistant_response
                    assistant_response = a_
        else:
            assistant_response = {"content": ""}

        self.content["assistant_response"] = assistant_response.get("content", "")

    @property
    def response(self) -> Any:
        """Return the assistant response content."""
        return self.content.get("assistant_response")


# File: lion_core/communication/assistant_response.py
