from lionabc.exceptions import LionValueError

from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse
from lion_core.operative.operative import ActionResponseModel


def create_action_response(
    *,
    action_request: ActionRequest,
    action_response_model: ActionResponseModel,
    sender,
    action_response: ActionResponse = None,
):
    if not isinstance(action_request, ActionRequest):
        raise LionValueError(
            "Error: please provide a corresponding action request for an "
            "action response."
        )

    if action_response:
        if not isinstance(action_response, ActionResponse):
            raise LionValueError(
                "Error: action response must be an instance of ActionResponse."
            )
        action_response.update_request(
            action_request=action_request,
            func_output=action_response_model.output,
        )
        return action_response

    return ActionResponse(
        action_request=action_request,
        sender=sender,
        func_outputs=action_response_model.output,
    )