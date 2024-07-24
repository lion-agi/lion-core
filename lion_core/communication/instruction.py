from __future__ import annotations
from typing import Any
from lion_core.record.form import Form
from lion_core.communication.message import RoledMessage, MessageRole
from lion_core.communication.utils import (
    prepare_instruction_content,
    format_image_content,
)


class Instruction(RoledMessage):
    """Represents an instruction message in the system."""

    def __init__(
        self,
        instruction: Any,
        context: Any = None,
        images: list = None,
        sender: Any = None,
        recipient: Any = None,
        requested_fields: dict = None,
        image_detail: str = None,
    ):
        """
        Initialize an Instruction instance.

        Args:
            instruction: The main instruction content.
            context: Additional context for the instruction.
            images: List of images related to the instruction.
            sender: The sender of the instruction.
            recipient: The intended recipient of the instruction.
            requested_fields: Dictionary of fields requested in the response.
            image_detail: Level of detail for image processing.
        """
        super().__init__(
            role=MessageRole.USER,
            content=prepare_instruction_content(
                instruction=instruction,
                context=context,
                images=images,
                requested_fields=requested_fields,
                image_detail=image_detail,
            ),
            sender=sender or "user",
            recipient=recipient or "N/A",
        )

    @property
    def instruct(self):
        """Returns the instruction content."""
        return self.content.get("instruction", None)

    @classmethod
    def from_form(
        cls,
        form: Form,
        sender: str | None = None,
        recipient: Any = None,
        image: str | None = None,
        image_detail: str | None = None,
    ) -> Instruction:
        """
        Creates an Instruction instance from a form.

        Args:
            form: The form containing instruction details.
            sender: The sender of the instruction.
            recipient: The recipient of the instruction.
            image: The image content in base64 encoding.

        Returns:
            The created Instruction instance.
        """
        return cls(
            **form.instruction_dict,
            image=image,
            sender=sender,
            recipient=recipient,
            image_detail=image_detail,
        )

    def _format_content(self) -> dict[str, Any]:
        _msg = super()._format_content()
        if isinstance(_msg["content"], str):
            return _msg

        return format_image_content(
            _msg, self.content.get("images"), self.content.get("image_detail")
        )


# File: lion_core/communication/instruction.py
