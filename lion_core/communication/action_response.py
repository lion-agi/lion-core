import json
from typing import Any
from pydantic import Field
from .message import RoledMessage, MessageRole
from .action_request import ActionRequest


# action response must correlates to a specific action request
class ActionResponse(RoledMessage):
    """
    Represents a response to a specific action request.

    Inherits from `RoledMessage` and provides attributes specific to action
    responses.

    Attributes:
        action_request: The ID of the action request this response corresponds to.
        function: The name of the function called.
        arguments: The keyword arguments provided.
        func_outputs: The output of the function call.
    """

    action_request: str | None = Field(
        None,
        description="The id of the action request that this response corresponds to",
    )

    function: str | None = Field(None, description="The name of the function called")
    arguments: dict | None = Field(None, description="The keyword arguments provided")
    func_outputs: Any | None = Field(
        None, description="The output of the function call"
    )

    def __init__(
        self,
        action_request: ActionRequest,
        sender: str | None = None,
        func_outputs: Any = None,
        **kwargs: Any,
    ):
        """
        Initializes the ActionResponse.

        Args:
            action_request: The action request this response corresponds to.
            sender: The sender of the action request.
            func_outputs: The output of the function call.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If the action request has already been responded to.
        """
        if action_request.is_responded():
            raise ValueError("Action request has already been responded to")

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",  # sender is the actionable component
            recipient=action_request.sender,  # recipient is the assistant who made the request
            content={
                "action_response": {
                    "function": action_request.function,
                    "arguments": action_request.arguments,
                    "output": func_outputs,
                }
            },
            **kwargs,
        )
        self.update_request(action_request)
        self.func_outputs = func_outputs

    def update_request(self, action_request: ActionRequest) -> None:
        """
        Updates the action request details in the action response.

        Args:
            action_request: The action request to update from.
        """
        self.function = action_request.function
        self.arguments = action_request.arguments
        self.action_request = action_request.ln_id
        action_request.action_response = self.ln_id

    def _to_dict(self) -> dict:
        """
        Converts the action response to a dictionary.

        Returns:
            A dictionary representation of the action response.
        """
        return {
            "function": self.function,
            "arguments": self.arguments,
            "output": self.func_outputs,
        }

    def clone(self, **kwargs: Any) -> "ActionResponse":
        """
        Creates a copy of the current object with optional additional arguments.

        This method clones the current object, preserving its function and
        arguments. It also retains the original `action_request`, `func_outputs`,
        and metadata, while allowing for the addition of new attributes through
        keyword arguments.

        Args:
            **kwargs: Optional keyword arguments to be included in the cloned object.

        Returns:
            A new instance of the object with the same function, arguments,
            and additional keyword arguments.
        """

        arguments = json.dumps(self.arguments)
        action_request = ActionRequest(
            function=self.function, arguments=json.loads(arguments)
        )
        action_response_copy = ActionResponse(action_request=action_request, **kwargs)
        action_response_copy.action_request = self.action_request
        action_response_copy.func_outputs = self.func_outputs
        action_response_copy.metadata["origin_ln_id"] = self.ln_id
        return action_response_copy


# File: lion_core/communication/action_response.py
