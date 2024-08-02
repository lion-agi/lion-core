from typing import Any, override
from lion_core.communication.utils import format_system_content
from lion_core.communication.message import RoledMessage, MessageRole, MessageFlag


class System(RoledMessage):
    """Represents a system message in an LLM conversation."""

    @override
    def __init__(
        self,
        system: Any | MessageFlag = None,
        sender: str | None | MessageFlag = None,
        recipient: str | None | MessageFlag = None,
        system_datetime: bool | str | None | MessageFlag = None,
        protected_init_params: dict | None = None
    ):
        """
        Initialize a System message instance.

        Args:
            system: The main content of the system message.
            sender: The sender of the system message.
            recipient: The intended recipient of the system message.
            system_datetime: Flag or string to include datetime in the message.
        """
        if all(
            x == MessageFlag.MESSAGE_LOAD
            for x in [system, sender, recipient, system_datetime]
        ):
            super().__init__(**protected_init_params)
            return
        
        if all(
            x == MessageFlag.MESSAGE_CLONE
            for x in [system, sender, recipient, system_datetime]
        ):
            super().__init__(role=MessageRole.SYSTEM)
            return

        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content=format_system_content(system_datetime, system),
            recipient=recipient or "N/A",
        )

    @property
    def system_info(self) -> Any:
        """system information stored in the message content."""
        return self.content.get("system_info", None)


# File: lion_core/communication/system.py
