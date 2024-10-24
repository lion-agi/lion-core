from lionabc.exceptions import LionValueError

from lion_core.communication import ActionRequest, ActionResponse
from lion_core.operative.step_model import ActionResponseModel


def create_action_response(
    *,
    action_request: ActionRequest,
    action_response_model: ActionResponseModel = None,
    action_response: ActionResponse | None = None,
) -> ActionResponse:
    """Creates or updates an ActionResponse based on the given parameters.

    Args:
        action_request: The corresponding ActionRequest.
        action_response_model: Model containing the response data.
        sender: The sender of the response. Defaults to None.
        action_response: Existing ActionResponse to update.
            Defaults to None.

    Returns:
        ActionResponse: A new or updated ActionResponse instance.

    Raises:
        LionValueError: If action_request is not an ActionRequest or
            if action_response is provided but not an ActionResponse.
    """
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
        if action_request.is_responded:
            raise ValueError("Error: action request already has a response.")
        action_request.content["action_response_id"] = action_response.ln_id
        return action_response

    return ActionResponse(
        action_request=action_request,
        output=action_response_model.output,
    )
