from typing import Any, override

from lion_core.sys_utils import SysUtil
from lion_core.generic.note import Note
from lion_core.communication.message import (
    RoledMessage,
    MessageRole,
    MessageFlag,
)

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


def format_system_content(
    system_datetime: bool | str | None, system_message: str
) -> Note:
    """
    Format the system content with optional datetime.

    Args:
        system_datetime: Flag or string to include datetime.
        system_message: The system message content.

    Returns:
        Note: Formatted system content.
    """
    system_message = system_message or DEFAULT_SYSTEM
    if not system_datetime:
        return Note(system_info=str(system_message))
    if isinstance(system_datetime, str):
        return Note(system_info=f"{system_message}. System Date: {system_datetime}")
    if system_datetime:
        date = SysUtil.time(type_="iso", timespec="minutes")
        return Note(system_info=f"{system_message}. System Date: {date}")


class System(RoledMessage):
    """Represents a system message in an LLM conversation."""

    @override
    def __init__(
        self,
        system: Any | MessageFlag = None,
        sender: str | None | MessageFlag = None,
        recipient: str | None | MessageFlag = None,
        system_datetime: bool | str | None | MessageFlag = None,
        protected_init_params: dict | None = None,
    ):
        """
        Initialize a System message instance.

        Args:
            system: The main content of the system message.
            sender: The sender of the system message.
            recipient: The intended recipient of the system message.
            system_datetime: Flag or string to include datetime in the message.
            protected_init_params: Protected initialization parameters for
                message loading.
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
            content=format_system_content(
                system_datetime=system_datetime, system_message=system
            ),
            recipient=recipient or "N/A",
        )

    @property
    def system_info(self) -> Any:
        """Get system information stored in the message content."""
        return self.content.get("system_info", None)


# File: lion_core/communication/system.py
