from typing import Any

from typing_extensions import override

from lion_core.communication.message import MessageFlag, MessageRole, RoledMessage
from lion_core.generic.note import Note
from lion_core.sys_utils import SysUtil

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


def format_system_content(
    system_datetime: bool | str | None,
    system_message: str,
) -> Note:
    """
    Format the system content with optional datetime information.

    This function creates a system message formatted as a `Note` object, optionally
    including a timestamp. The timestamp can be automatically generated in ISO format
    or provided as a string.

    Args:
        system_datetime (bool | str | None): A flag or string indicating whether to include
            a datetime in the system message.
            - If `False` or `None`, no datetime is included.
            - If `True`, the current system datetime is appended in ISO format.
            - If a string is provided, it is appended as the datetime.
        system_message (str): The content of the system message. If not provided,
            a default system message is used.

    Returns:
        Note: A `Note` object containing the formatted system content with the optional datetime.

    Example:
        >>> format_system_content(True, "System maintenance complete")
        Note with content: "System maintenance complete. System Date: 2024-08-19T12:34"

        >>> format_system_content("2024-08-19", "System update scheduled")
        Note with content: "System update scheduled. System Date: 2024-08-19"
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
    """
    Represents a system message in a language model (LLM) conversation.

    The `System` class is a specialized type of `RoledMessage` that encapsulates
    messages from the system within a conversation. These messages may include
    system-related information such as updates, notifications, or status reports.

    Inherits:
        - RoledMessage: Provides basic message structure, including content and role.

    Attributes:
        content (Note): The content of the system message, formatted with optional datetime.
        role (MessageRole): The role of the message, set to "system".

    Properties:
        system_info (Any): Retrieves the system information stored in the message content.

    Methods:
        __init__(self, system, sender, recipient, system_datetime, protected_init_params):
            Initializes a new `System` message instance.
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
        Initialize a `System` message instance.

        This constructor initializes a `System` message with optional content, sender,
        recipient, and datetime information. The system message can be created fresh,
        loaded from a previous state, or cloned from an existing instance.

        Args:
            system (Any | MessageFlag, optional): The main content of the system message.
                Defaults to None.
            sender (str | None | MessageFlag, optional): The sender of the system message.
                Defaults to None.
            recipient (str | None | MessageFlag, optional): The intended recipient of the system message.
                Defaults to None.
            system_datetime (bool | str | None | MessageFlag, optional): A flag or string to include
                datetime in the message. Defaults to None.
            protected_init_params (dict | None, optional): Protected initialization parameters
                for message loading. Defaults to None.
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

        This property accesses the `system_info` field in the message content,
        which typically contains the formatted system message along with any
        datetime information.

        Returns:
            Any: The system information stored in the message content.
        """
        return self.content.get("system_info", None)


# File: lion_core/communication/system.py
