from typing import Any

from typing_extensions import override

from lion_core.communication.message import (
    MessageFlag,
    MessageRole,
    RoledMessage,
)
from lion_core.communication.utils import format_system_content


class System(RoledMessage):
    """
    Represents a system message in a language model conversation.

    This class extends RoledMessage to provide functionality specific to
    system messages, which are typically used to set the context or provide
    instructions to the language model.

    Example:
        >>> system_msg = System(
            system="You are a helpful assistant.",
            system_datetime=True
            )
        >>> print(system_msg.system_info)
        'You are a helpful assistant. System Date: 2023-06-01T12:00:00'
    """

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
            system_message: The content of the system message.
            sender: The sender of the system message.
            recipient: The recipient of the system message.
            system_datetime: Flag to include system datetime in the message.
            protected_init_params: Protected initialization parameters.

        Raises:
            ValueError: If invalid combination of parameters is provided.
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
        """
        Retrieve the system information stored in the message content.

        Returns:
            Any: The system information.
        """
        return self.content.get("system_info", None)

    @override
    def _format_content(self) -> dict[str, Any]:
        return {"role": self.role.value, "content": self.system_info}


# File: lion_core/communication/system.py
