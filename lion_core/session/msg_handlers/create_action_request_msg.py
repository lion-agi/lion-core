from typing import Any

from lionabc.exceptions import LionValueError

from lion_core.communication.action_request import ActionRequest
from lion_core.operative.step_model import ActionRequestModel


def create_action_request(
    *,
    action_request_model: ActionRequestModel,
    sender: Any,
    recipient: Any,
    action_request: ActionRequest | None = None,
) -> ActionRequest:
    """Creates or returns an ActionRequest instance.

    Args:
        action_request_model: Model with function and arguments.
        sender: Request sender.
        recipient: Request recipient.
        action_request: Existing ActionRequest, if any.

    Returns:
        ActionRequest: New or existing instance.

    Raises:
        LionValueError: If action_request is invalid.
        ValueError: If sender or recipient is None.
    """
    if action_request:
        if not isinstance(action_request, ActionRequest):
            raise LionValueError(
                "Error: action request must be an instance of ActionRequest."
            )
        return action_request

    return ActionRequest(
        function=action_request_model.function,
        arguments=action_request_model.arguments,
        sender=sender,
        recipient=recipient,
    )
