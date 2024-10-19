from lionabc.exceptions import LionValueError

from lion_core.communication.action_request import ActionRequest
from lion_core.operative.operative import ActionRequestModel
from lion_core.session.msg_handlers.utils import extract_action_blocks


def create_action_request_model(
    response: str,
) -> list[ActionRequestModel]:

    action_requests = extract_action_blocks(response)
    out = []
    if action_requests:
        for i in action_requests:
            try:
                a = ActionRequestModel.model_validate(i)
                out.append(a)
            except Exception:
                pass

    return out


def create_action_request(
    *,
    action_request_model: ActionRequestModel,
    sender,
    recipient,
    action_request: ActionRequest = None,
):
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
