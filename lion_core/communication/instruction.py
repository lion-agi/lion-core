from __future__ import annotations
from typing import Any, Literal
from lion_core.record.form import Form
from lion_core.communication.message import RoledMessage, MessageRole, MessageCloneFlag
from lion_core.communication.utils import (
    prepare_instruction_content,
    format_image_content,
)


class Instruction(RoledMessage):
    """Represents an instruction message in the system."""

    def __init__(
        self,
        instruction: Any | MessageCloneFlag,
        context: Any | MessageCloneFlag = None,
        images: list | MessageCloneFlag = None,
        sender: Any | MessageCloneFlag = None,
        recipient: Any | MessageCloneFlag = None,
        requested_fields: dict | MessageCloneFlag = None,
        image_detail: Literal["low", "high", "auto"] | MessageCloneFlag = None,
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
        if all(
            x == MessageCloneFlag.MESSAGE_CLONE
            for x in [
                instruction,
                context,
                images,
                sender,
                recipient,
                requested_fields,
                image_detail,
            ]
        ):
            super().__init__(role=MessageRole.USER)
            return

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
        images: str | None = None,
        image_detail: str | None = None,
    ) -> Instruction:
        """
        Creates an Instruction instance from a form.

        Args:
            form: The form containing instruction details.
            sender: The sender of the instruction.
            recipient: The recipient of the instruction.
            images: The image content in base64 encoding.

        Returns:
            The created Instruction instance.
        """
        return cls(
            **form.instruction_dict,
            images=images,
            sender=sender,
            recipient=recipient,
            image_detail=image_detail,
        )

    def _format_content(self) -> dict[str, Any]:
        _msg = super()._format_content()
        if isinstance(_msg["content"], str):
            return _msg

        else:
            content = _msg["content"]
            content.pop("images")
            content.pop("image_detail")
            text_content = str(content)
            content = format_image_content(
                text_content,
                self.content.get(["images"]),
                self.content.get(["image_detail"]),
            )
            _msg["content"] = content
            return _msg


# File: lion_core/communication/instruction.py
