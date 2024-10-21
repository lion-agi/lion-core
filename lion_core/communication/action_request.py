from collections.abc import Callable
from typing import Any

from lionfuncs import Note, copy, to_dict, to_str
from typing_extensions import override

from lion_core.communication.message import (
    MessageFlag,
    MessageRole,
    RoledMessage,
)


def prepare_action_request(
    function: str | Callable,
    arguments: dict,
) -> Note:
    """
    Prepare an action request Note.

    Args:
        function: The function name or callable to be invoked.
        arguments: The arguments for the function.

    Returns:
        Note: A Note object containing the action request.

    Raises:
        ValueError: If the arguments are invalid.
    """

    def _prepare_arguments(_arg: Any) -> dict[str, Any]:
        if _arg is None:
            return {}
        if not isinstance(_arg, dict):
            try:
                _arg = to_dict(to_str(_arg), str_type="json", fuzzy_parse=True)
            except ValueError:
                _arg = to_dict(to_str(_arg), str_type="xml")
            except Exception as e:
                raise ValueError(f"Invalid arguments: {e}") from e

        if isinstance(_arg, dict):
            return _arg
        raise ValueError(f"Invalid arguments: {_arg}")

    arguments = _prepare_arguments(arguments)
    return Note(
        **{"action_request": {"function": function, "arguments": arguments}},
    )


class ActionRequest(RoledMessage):
    """Represents a request for an action in the system."""

    @override
    def __init__(
        self,
        function: str | Callable | MessageFlag,
        arguments: dict | MessageFlag,
        sender: Any | MessageFlag = None,
        recipient: Any | MessageFlag = None,
        protected_init_params: dict | None = None,
    ) -> None:
        """
        Initialize an ActionRequest instance.

        Args:
            function: The function to be invoked.
            arguments: The arguments for the function.
            sender: The sender of the request.
            recipient: The recipient of the request.
            protected_init_params: Protected initialization parameters.
        """
        message_flags = [function, arguments, sender, recipient]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            protected_init_params = protected_init_params or {}
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        function = function.__name__ if callable(function) else function

        super().__init__(
            role=MessageRole.ASSISTANT,
            content=prepare_action_request(function, arguments),
            sender=sender,
            recipient=recipient,
        )

    @property
    def action_response_id(self) -> str | None:
        """
        Get the ID of the corresponding action response, if any.

        Returns:
            str | None: The ID of the action response, or None if not responded
        """
        return self.content.get("action_response_id", None)

    @property
    def is_responded(self) -> bool:
        """
        Check if the action request has been responded to.

        Returns:
            bool: True if the action request has been responded to, else False.
        """
        return self.action_response_id is not None

    @property
    def request(self) -> dict[str, Any]:
        """
        Get the action request content as a dictionary.

        Returns:
            dict[str, Any]: The action request content.
        """
        a = copy(self.content.get("action_request", {}))
        a.pop("output", None)
        return a

    @property
    def arguments(self) -> dict[str, Any]:
        """
        Get the arguments for the action request.

        Returns:
            dict[str, Any]: The arguments for the action request.
        """
        return self.request.get("arguments", {})

    @property
    def function(self) -> str:
        """
        Get the function name for the action request.

        Returns:
            str: The function name for the action request.
        """
        return self.request.get("function", "")

    @override
    def _format_content(self) -> dict[str, Any]:
        return {"role": self.role.value, "content": self.request}


# File: lion_core/communication/action_request.py
