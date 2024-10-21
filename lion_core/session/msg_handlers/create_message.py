from typing import Any, Literal

from lionabc import Observable
from pydantic import BaseModel

from lion_core.communication import (
    ActionRequest,
    ActionResponse,
    AssistantResponse,
    Instruction,
    System,
)
from lion_core.operative.action_model import ActRequestModel, ActResponseModel

from .create_action_request_msg import create_action_request
from .create_action_response_msg import create_action_response
from .create_assistant_response_msg import create_assistant_response_message
from .create_instruction_msg import create_instruction_message
from .create_system_msg import create_system_message


def create_message(
    sender: Observable | str = None,
    recipient: Observable | str = None,
    instruction: Instruction | str | dict = None,
    context: Any = None,
    guidance: str | dict = None,
    plain_content: str = None,
    request_fields: list[str] | dict = None,
    request_model: type[BaseModel] | BaseModel = None,
    system: System | str | dict = None,
    system_sender: Observable | str = None,
    system_datetime: bool | str = None,
    images: list = None,
    image_detail: Literal["low", "high", "auto"] | None = None,
    assistant_response: AssistantResponse | str = None,
    action_request: ActionRequest = None,
    action_response: ActionResponse = None,
    action_request_model: ActRequestModel = None,
    action_response_model: ActResponseModel = None,
):
    """Create a message based on the provided parameters.

    Args:
        sender: The sender of the message.
        recipient: The recipient of the message.
        instruction: Instruction content or object.
        context: Additional context for the message.
        guidance: Guidance information.
        plain_content: Plain text content.
        request_fields: Fields for the request.
        request_model: Model for the request.
        system: System message content or object.
        system_sender: The sender of the system message.
        system_datetime: System datetime information.
        images: List of images.
        image_detail: Image detail level.
        assistant_response: Assistant response content or object.
        action_request: Action request message.
        action_response: Action response message.
        action_request_model: Action request model.
        action_response_model: Action response model.

    Returns:
        A message object of the appropriate type.

    Raises:
        ValueError: If multiple message roles are provided or if an
            action response is provided without an action request.
    """
    """kwargs for additional instruction context"""
    if (
        len(
            [
                i
                for i in [instruction, system, assistant_response]
                if i is not None
            ],
        )
        > 1
    ):
        raise ValueError("Error: Message can only have one role")

    if action_response_model or action_response:
        if not action_request:
            raise ValueError(
                "Error: Action response must have an action request."
            )
        return create_action_response(
            action_request=action_request,
            action_response_model=action_response_model,
            sender=sender,
            action_response=action_response,
        )
    if action_request_model or action_request:
        return create_action_request(
            action_request_model=action_request_model,
            sender=sender,
            recipient=recipient,
            action_request=action_request,
        )
    if system:
        return create_system_message(
            system=system,
            sender=system_sender,
            recipient=recipient,
            system_datetime=system_datetime,
        )
    if assistant_response:
        return create_assistant_response_message(
            sender=sender,
            recipient=recipient,
            assistant_response=assistant_response,
        )
    return create_instruction_message(
        sender=sender,
        recipient=recipient,
        instruction=instruction,
        context=context,
        guidance=guidance,
        request_fields=request_fields,
        images=images,
        image_detail=image_detail,
        request_model=request_model,
        plain_content=plain_content,
    )
