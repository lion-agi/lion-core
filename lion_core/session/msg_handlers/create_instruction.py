from typing import Any, Literal

from lion_core.communication.instruction import Instruction
from lion_core.communication.message import MessageFlag


def create_instruction(
    sender: Any | MessageFlag = None,
    recipient: Any | MessageFlag = None,
    instruction: Any | MessageFlag = None,
    context: Any | MessageFlag = None,
    guidance: Any | MessageFlag = None,
    request_fields: dict | MessageFlag = None,
    plain_content=None,
    images: list | MessageFlag = None,
    image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
):
    if isinstance(instruction, Instruction):
        if context:
            instruction.update_context(context)
        if request_fields:
            instruction.update_request_fields(
                request_fields=request_fields,
            )
        if images:
            instruction.update_images(
                images=images,
                image_detail=image_detail,
            )
        if guidance:
            instruction.update_guidance(
                guidance=guidance,
            )
        if plain_content:
            instruction.content["plain_content"] = plain_content
        return instruction

    return Instruction(
        instruction=instruction,
        context=context,
        guidance=guidance,
        images=images,
        sender=sender,
        recipient=recipient,
        request_fields=request_fields,
        image_detail=image_detail,
        plain_content=plain_content,
    )
