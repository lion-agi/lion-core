import json
from typing import Any, Callable
from pydantic import Field
from lion_core.libs import fuzzy_parse_json, to_str
from .message import RoledMessage, MessageRole


class ActionRequest(RoledMessage):
    """
    Represents a request for an action with function and arguments.

    Inherits from `RoledMessage` and provides attributes specific to action
    requests.

    Attributes:
        function: The name of the function to be called.
        arguments: The keyword arguments to be passed to the function.
        action_response: The ID of the action response that this request
            corresponds to.
    """

    function: str | None = Field(
        None, description="The name of the function to be called"
    )

    arguments: dict | None = Field(
        None, description="The keyword arguments to be passed to the function"
    )

    action_response: str | None = Field(
        None,
        description="The id of the action response that this request corresponds to",
    )

    def __init__(
        self,
        function: str | Callable | None = None,
        arguments: dict | None = None,
        sender: str | None = None,
        recipient: str | None = None,
        **kwargs: Any,
    ):
        """
        Initializes the ActionRequest.

        Args:
            function: The function to be called.
            arguments: The keyword arguments for the function.
            sender: The sender of the request.
            recipient: The recipient of the request.
            **kwargs: Additional keyword arguments.
        """
        function = function.__name__ if callable(function) else function
        arguments = _prepare_arguments(arguments)

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender,
            recipient=recipient,
            content={"action_request": {"function": function, "arguments": arguments}},
            **kwargs,
        )
        self.function = function
        self.arguments = arguments

    def is_responded(self) -> bool:
        """
        Checks if the action request has been responded to.

        Returns:
            True if the action request has a response, otherwise False.
        """
        return self.action_response is not None

    def clone(self, **kwargs: Any) -> "ActionRequest":
        """
        Creates a copy of the current ActionRequest object.

        This method clones the current object, preserving its function and
        arguments. It also retains the original `action_response` and metadata,
        while allowing for the addition of new attributes through keyword
        arguments.

        Args:
            **kwargs: Optional keyword arguments to be included in the cloned
                object.

        Returns:
            A new instance of the object with the same function, arguments,
            and additional keyword arguments.
        """
        arguments = json.dumps(self.arguments)
        request_copy = ActionRequest(
            function=self.function, arguments=json.loads(arguments), **kwargs
        )
        request_copy.action_response = self.action_response
        request_copy.metadata["origin_ln_id"] = self.ln_id
        return request_copy


def _prepare_arguments(arguments: Any) -> dict:
    """
    Prepares the arguments for the action request.

    Args:
        arguments: The arguments to be prepared.

    Returns:
        The prepared arguments.

    Raises:
        ValueError: If the arguments are invalid.
    """
    if not isinstance(arguments, dict):
        try:
            arguments = fuzzy_parse_json(to_str(arguments))
        except Exception as e:
            raise ValueError(f"Invalid arguments: {e}") from e
    if isinstance(arguments, dict):
        return arguments
    raise ValueError(f"Invalid arguments: {arguments}")


# File: lion_core/communication/action_request.py
