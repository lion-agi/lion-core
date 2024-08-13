from typing import Any, Callable, Literal

from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse
from lion_core.communication.message import MessageFlag

from lion_core.session.msg_handlers.action_msg import handle_action
from lion_core.session.msg_handlers.instruction_msg import handle_instruction
from lion_core.session.msg_handlers.assistant_msg import handle_assistant
from lion_core.session.msg_handlers.system_msg import handle_system


def create_message(
    sender: Any | MessageFlag,
    recipient: Any | MessageFlag,
    instruction: Any | MessageFlag,
    context: Any | MessageFlag,
    guidance: Any | MessageFlag,
    request_fields: dict | MessageFlag,
    system: Any,
    system_datetime: bool | str | None | MessageFlag,
    images: list | MessageFlag,
    image_detail: Literal["low", "high", "auto"] | MessageFlag,
    assistant_response: str | dict | None | MessageFlag,
    action_request: ActionRequest | None,
    action_response: ActionResponse | None,
    func: str | Callable | MessageFlag,
    arguments: dict | MessageFlag,
    func_output: Any | MessageFlag,
):
    a = handle_action(
        sender=sender,
        recipient=recipient,
        action_request=action_request,
        action_response=action_response,
        func=func,
        arguments=arguments,
        func_output=func_output,
    )
    if a is not None:
        return a

    if len({k: v for k, v in a.items() if v is not [None]}) != 1:
        raise ValueError("Error: Message can only have one role")

    a = handle_system(
        system=system,
        sender=sender,
        recipient=recipient,
        system_datetime=system_datetime,
    )
    if a is not None:
        return a

    a = handle_assistant(
        sender=sender,
        recipient=recipient,
        assistant_response=assistant_response,
    )

    if a is not None:
        return a

    return handle_instruction(
        sender=sender,
        recipient=recipient,
        instruction=instruction,
        context=context,
        guidance=guidance,
        request_fields=request_fields,
        images=images,
        image_detail=image_detail,
    )
