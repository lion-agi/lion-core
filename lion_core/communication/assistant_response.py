from typing import Any
from lion_core.communication.message import RoledMessage, MessageRole, MessageCloneFlag


class AssistantResponse(RoledMessage):
    """Represents a response from an assistant in the system."""

    def __init__(
        self,
        assistant_response: dict | MessageCloneFlag,
        sender: Any | MessageCloneFlag,
        recipient: Any | MessageCloneFlag,
    ):
        if all(
            x == MessageCloneFlag.MESSAGE_CLONE
            for x in [assistant_response, sender, recipient]
        ):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",
            recipient=recipient,
        )
        self.content["assistant_response"] = assistant_response.get("content", "")

    @property
    def response(self) -> Any:
        """Return the assistant response content."""
        return self.content.get("assistant_response")


# File: lion_core/communication/assistant_response.py
