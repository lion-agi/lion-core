from typing import Any, Literal

from pydantic import BaseModel

from lion_core.communication import Instruction


def create_instruction(
    sender: Any = None,
    recipient: Any = None,
    instruction: str | dict = None,
    context: Any = None,
    guidance: str | dict = None,
    request_fields: list | dict = None,
    request_model: type[BaseModel] | BaseModel = None,
    plain_content: str = None,
    images: list = None,
    image_detail: Literal["low", "high", "auto"] | None = None,
    **kwargs,
) -> Instruction:
    """Create or update an Instruction.

    Args:
        sender: The sender of the instruction.
        recipient: The recipient of the instruction.
        instruction: Existing Instruction or instruction content.
        context: Additional context for the instruction.
        guidance: Guidance information.
        request_fields: Fields for the request.
        request_model: Model for the request.
        plain_content: Plain text content.
        images: List of images.
        image_detail: Image detail level.
        **kwargs: Additional keyword arguments.

    Returns:
        Instruction: New or updated Instruction instance.
    """
    if isinstance(instruction, Instruction):
        instruction.update(
            context,
            guidance=guidance,
            request_fields=request_fields,
            plain_content=plain_content,
            request_model=request_model,
            images=images,
            image_detail=image_detail,
            **kwargs,
        )
        if sender:
            instruction.sender = sender
        if recipient:
            instruction.recipient = recipient
    else:
        instruction = Instruction(
            sender=sender,
            recipient=recipient,
            instruction=instruction,
            context=context,
            guidance=guidance,
            request_fields=request_fields,
            request_model=request_model,
            plain_content=plain_content,
            images=images,
            image_detail=image_detail,
            **kwargs,
        )
    return instruction
