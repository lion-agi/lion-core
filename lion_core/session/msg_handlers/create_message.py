from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse

from .create_action_request import create_action_request
from .create_action_response import create_action_response
from .create_assistant_response import create_assistant_response
from .create_instruction import create_instruction
from .create_system import create_system


def create_message(
    sender=None,
    recipient=None,
    instruction=None,
    context=None,
    guidance=None,
    request_fields=None,
    system=None,
    system_sender=None,
    system_datetime=None,
    images=None,
    image_detail=None,
    assistant_response=None,
    action_request: ActionRequest = None,
    action_response: ActionResponse = None,
    action_request_model=None,
    action_response_model=None,
):
    if (
        len(
            [
                i
                for i in [instruction, system, assistant_response]
                if i is not None
            ],
        )
        != 1
    ):
        raise ValueError("Error: Message can only have one role")

    if action_response_model or action_response:
        return create_action_response(
            action_request=action_request,
            action_response_model=action_response_model,
            sender=sender,
            action_response=action_response,
        )
    if action_request_model or action_request:
        return create_action_request(
            sender=sender,
            recipient=recipient,
            action_request_model=action_request_model,
            action_request=action_request,
        )
    if system:
        return create_system(
            system=system,
            sender=system_sender,
            recipient=recipient,
            system_datetime=system_datetime,
        )
    if assistant_response:
        return create_assistant_response(
            sender=sender,
            recipient=recipient,
            assistant_response=assistant_response,
        )
    return create_instruction(
        sender=sender,
        recipient=recipient,
        instruction=instruction,
        context=context,
        guidance=guidance,
        request_fields=request_fields,
        images=images,
        image_detail=image_detail,
    )
