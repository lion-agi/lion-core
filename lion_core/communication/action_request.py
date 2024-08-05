from typing import Any, Callable, override

from lion_core.libs import to_dict, to_str, fuzzy_parse_json
from lion_core.generic.note import Note
from lion_core.communication.message import (
    RoledMessage,
    MessageRole,
    MessageFlag,
)


def prepare_action_request(func: str | Callable, arguments: dict) -> Note:
    def _prepare_arguments(_arg: Any) -> dict[str, Any]:
        """Prepare and validate the arguments for an action request."""
        if not isinstance(_arg, dict):
            try:
                _arg = to_dict(
                    to_str(_arg),
                    str_type="json",
                    parser=fuzzy_parse_json,
                )
            except ValueError:
                _arg = to_dict(to_str(_arg), str_type="xml")
            except Exception as e:
                raise ValueError(f"Invalid arguments: {e}") from e

        if isinstance(arguments, dict):
            return arguments
        raise ValueError(f"Invalid arguments: {arguments}")

    arguments = _prepare_arguments(arguments)
    return Note(**{"action_request": {"function": func, "arguments": arguments}})


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
        message_flags = [func, arguments, sender, recipient]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
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
