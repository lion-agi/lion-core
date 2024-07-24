from typing import Any
from lion_core.communication.utils import format_system_content
from lion_core.communication.message import RoledMessage, MessageRole


class System(RoledMessage):
    """Represents a system message in an LLM conversation."""

    def __init__(
        self,
        system: Any = None,
        sender: str | None = None,
        recipient: str | None = None,
        with_datetime: bool | str | None = None,
    ):
        """
        Initialize a System message instance.

        Args:
            system: The main content of the system message.
            sender: The sender of the system message.
            recipient: The intended recipient of the system message.
            with_datetime: Flag or string to include datetime in the message.
        """
        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content=format_system_content(with_datetime, system),
            recipient=recipient or "N/A",
        )

    @property
    def system_info(self) -> Any:
        """system information stored in the message content."""
        return self.content.get("system_info", None)


# File: lion_core/communication/system.py
