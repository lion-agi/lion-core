from __future__ import annotations
from typing import Any, Callable, override

from lion_core.communication.message import RoledMessage, MessageRole, MessageFlag
from lion_core.communication.utils import prepare_action_request


class ActionRequest(RoledMessage):
    """Represents a request for an action in the system."""

    @override
    def __init__(
        self,
        func: str | Callable | MessageFlag,
        arguments: dict | MessageFlag,
        sender: Any | MessageFlag,
        recipient: Any | MessageFlag,
        protected_init_params: dict | None = None,
    ):
        if all(
            x == MessageFlag.MESSAGE_LOAD for x in [func, arguments, sender, recipient]
        ):
            super().__init__(**protected_init_params)
            return

        if all(
            x == MessageFlag.MESSAGE_CLONE for x in [func, arguments, sender, recipient]
        ):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        func = func.__name__ if callable(func) else func

        super().__init__(
            role=MessageRole.ASSISTANT,
            content=prepare_action_request(func, arguments),
            sender=sender,
            recipient=recipient,
        )

    @property
    def is_responded(self) -> bool:
        """Check if the action request has been responded to."""
        return self.action_response_id is not None

    @property
    def request_dict(self) -> dict[str, Any]:
        """Get the action request as a dictionary."""
        return self.content.get("action_request", {})

    @property
    def action_response_id(self) -> str | None:
        """Get the ID of the corresponding action response, if any."""
        return self.content.get("action_response_id", None)


# File: lion_core/communication/action_request.py
