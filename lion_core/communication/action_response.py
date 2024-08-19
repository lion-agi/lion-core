"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any
from typing_extensions import override

from lion_core.exceptions import LionValueError
from lion_core.generic.note import Note
from lion_core.communication.message import RoledMessage, MessageRole, MessageFlag
from lion_core.communication.action_request import ActionRequest


def prepare_action_response_content(
    action_request: ActionRequest,
    func_output: Any,
) -> Note:
    """
    Prepare the content for an action response.

    This function takes an `ActionRequest` object and the output from the function
    it requested. It then prepares a `Note` containing the response content, which
    includes the original request details and the function's output.

    Args:
        action_request (ActionRequest): The original action request to respond to.
        func_output (Any): The output from the function specified in the action request.

    Returns:
        Note: A `Note` object containing the formatted action response content.

    Raises:
        LionValueError: If the action request has already been responded to.
    """
    if action_request.is_responded:
        raise LionValueError("Action request already responded to")

    dict_ = action_request.request_dict
    dict_["output"] = func_output
    content = Note(action_request_id=action_request.ln_id)
    content["action_response"] = dict_
    return content


class ActionResponse(RoledMessage):
    """
    Represents a response to an action request in the system.

    The `ActionResponse` class encapsulates the response to an `ActionRequest`.
    It includes the function's output, links the response back to the original
    request, and allows for tracking the completion of an action.

    Attributes:
        action_request (ActionRequest | MessageFlag): The original action request to respond to.
        sender (Any | MessageFlag): The sender of the action response, typically the component executing the action.
        func_output (Any | MessageFlag): The output from the function specified in the action request.
        protected_init_params (dict | None): Optional parameters for protected initialization.
    """

    @override
    def __init__(
        self,
        action_request: ActionRequest | MessageFlag,
        sender: Any | MessageFlag,
        func_output: Any | MessageFlag,
        protected_init_params: dict | None = None,
    ):
        """
        Initializes an ActionResponse instance.

        Args:
            action_request (ActionRequest | MessageFlag): The original action request to respond to.
            sender (Any | MessageFlag): The sender of the action response, typically the component executing the action.
            func_output (Any | MessageFlag): The output from the function specified in the action request.
            protected_init_params (dict | None, optional): Optional parameters for protected initialization.
        """
        message_flags = [
            action_request,
            sender,
            func_output,
        ]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",  # sender is the actionable component
            recipient=action_request.sender,
            content=prepare_action_response_content(
                action_request=action_request,
                func_output=func_output,
            ),
        )
        self.update_request(
            action_request=action_request,
            func_output=func_output,
        )

    @property
    def func_output(self) -> Any:
        """
        Get the function output from the action response.

        Returns:
            Any: The output produced by the function invoked as part of the action request.
        """
        return self.content.get(["action_response", "output"])

    @property
    def response_dict(self) -> dict[str, Any]:
        """
        Get the action response as a dictionary.

        Returns:
            dict[str, Any]: The action response content, formatted as a dictionary.
        """
        return self.content.get("action_response", {})

    @property
    def action_request_id(self) -> str | None:
        """
        Get the ID of the corresponding action request.

        Returns:
            str | None: The ID of the action request that this response corresponds to, or None if not set.
        """
        return self.content.get("action_request_id", None)

    def update_request(self, action_request: ActionRequest, func_output):
        """
        Update the action response with a new request and output.

        Args:
            action_request (ActionRequest): The original action request being responded to.
            func_output (Any): The output from the function specified in the action request.

        This method updates the content of the `ActionResponse` with new details from the
        provided `ActionRequest` and function output, and links the response back to the
        original request.
        """
        self.content = prepare_action_response_content(
            action_request=action_request,
            func_output=func_output,
        )
        action_request.content.set(
            ["action_response_id"],
            self.ln_id,
        )


# File: lion_core/communication/action_response.py
