from lionabc.exceptions import LionValueError

from lion_core.communication import ActionRequest, ActionResponse
from lion_core.operative.step_model import ActResponseModel


def create_action_response_message(
    *,
    action_request_message: ActionRequest,
    act_response_model: ActResponseModel,
    sender=None,
    action_response_message: ActionResponse = None,
) -> ActionResponse:
    if not isinstance(action_request_message, ActionRequest):
        raise LionValueError(
            "Error: please provide a corresponding action request for an "
            "action response."
        )

    if action_response_message:
        if not isinstance(action_response_message, ActionResponse):
            raise LionValueError(
                "Error: action response must be an instance of ActionResponse."
            )
        if act_response_model:
            action_response_message.update_request(
                action_request=action_request_message,
                func_output=act_response_model.output,
            )
        else:
            action_response_message.update_request(
                action_request=action_request_message,
            )
        return action_response_message

    return ActionResponse(
        action_request=action_request_message,
        sender=sender,
        func_output=act_response_model.output,
    )
