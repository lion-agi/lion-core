from lionabc.exceptions import LionValueError

from lion_core.communication.action_request import ActionRequest
from lion_core.operative.step_model import ActRequestModel


def create_action_request_message(
    *,
    act_request_model: ActRequestModel,
    sender,
    recipient,
    action_request_message: ActionRequest = None,
) -> ActionRequest:
    if action_request_message:
        if not isinstance(action_request_message, ActionRequest):
            raise LionValueError(
                "Error: action request must be an instance of ActionRequest."
            )
        return action_request_message

    return ActionRequest(
        function=act_request_model.function,
        arguments=act_request_model.arguments,
        sender=sender,
        recipient=recipient,
    )
