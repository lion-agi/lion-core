import json
from typing import Any
from ..setting import BASE_LION_FIELDS
from .message import RoledMessage, MessageRole
from lion_core.record.form import Form

class Instruction(RoledMessage):
    """
    Represents an instruction message with context and requested fields.

    Inherits from `RoledMessage` and provides methods to manage context
    and requested fields specific to instructions.

    Attributes:
        instruction: The instruction content.
        context: Additional context for the instruction.
        sender: The sender of the instruction.
        recipient: The recipient of the instruction.
        requested_fields: Fields requested in the instruction.
    """

    def __init__(
        self,
        instruction: Any = None,
        context: Any = None,
        images: list | None = None,
        sender: Any = None,
        recipient: Any = None,
        requested_fields: dict | None = None,
        additional_context: dict | None = None,
        image_detail: str | None = None,
        **kwargs: Any,
    ):
        """
        Initializes the Instruction message.

        Args:
            instruction: The instruction content (JSON serializable).
            context: Additional context for the instruction.
            images: List of image contents in base64 encoding.
            sender: The sender of the instruction.
            recipient: The recipient of the instruction.
            requested_fields: Fields requested in the instruction.
            additional_context: Additional context fields to be added.
            image_detail: Detail level for image processing.
            **kwargs: Additional keyword arguments.
        """
        if not instruction:
            if "metadata" in kwargs and "instruction" in kwargs["metadata"]:
                instruction = kwargs["metadata"].pop("instruction")

        super().__init__(
            role=MessageRole.USER,
            sender=sender or "user",
            content={"instruction": instruction or "N/A"},
            recipient=recipient or "N/A",
            **kwargs,
        )

        additional_context = additional_context or {}
        self._initiate_content(
            context=context,
            requested_fields=requested_fields,
            images=images,
            image_detail=image_detail or "low",
            **additional_context,
        )

    @property
    def instruct(self):
        """Returns the instruction content."""
        return self.content["instruction"]

    def _check_chat_msg(self):
        text_msg = super()._check_chat_msg()
        if "images" not in self.content:
            return text_msg

        text_msg["content"].pop("images", None)
        text_msg["content"].pop("image_detail", None)
        text_msg["content"] = [
            {"type": "text", "text": text_msg["content"]},
        ]

        for i in self.content["images"]:
            text_msg["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{i}",
                        "detail": self.content["image_detail"],
                    },
                }
            )
        return text_msg

    def _add_context(self, context: Any = None, **kwargs: Any) -> None:
        """
        Adds context to the instruction message.

        Args:
            context: Additional context to be added.
            **kwargs: Additional context fields to be added.
        """
        if "context" not in self.content:
            self.content["context"] = {}
        if isinstance(context, dict):
            self.content["context"].update({**context, **kwargs})
        elif isinstance(context, str):
            self.content["context"]["additional_context"] = context

    def _update_requested_fields(self, requested_fields: dict) -> None:
        """
        Updates the requested fields in the instruction message.

        Args:
            requested_fields: The fields requested in the instruction.
        """
        if "context" not in self.content:
            self.content["context"] = {}
            self.content["context"]["requested_fields"] = {}
        self.content["context"]["requested_fields"].update(requested_fields)

    def _initiate_content(
        self,
        context: Any,
        requested_fields: dict | None,
        images: list | None,
        image_detail: str,
        **kwargs: Any,
    ) -> None:
        """
        Processes context and requested fields to update message content.

        Args:
            context: Additional context for the instruction.
            requested_fields: Fields requested in the instruction.
            images: List of image contents.
            image_detail: Detail level for image processing.
            **kwargs: Additional context fields to be added.
        """
        if context:
            context = {"context": context} if not isinstance(context, dict) else context
            if (
                additional_context := {
                    k: v for k, v in kwargs.items() if k not in BASE_LION_FIELDS
                }
            ) != {}:
                context["additional_context"] = additional_context
            self.content.update(context)

        if not requested_fields in [None, {}]:
            self.content["requested_fields"] = self._format_requested_fields(
                requested_fields
            )

        if images:
            self.content["images"] = images if isinstance(images, list) else [images]
            self.content["image_detail"] = image_detail

    def clone(self, **kwargs: Any) -> "Instruction":
        """
        Creates a copy of the current Instruction object.

        This method clones the current object, preserving its content.
        It also retains the original metadata, while allowing
        for the addition of new attributes through keyword arguments.

        Args:
            **kwargs: Optional keyword arguments for the cloned object.

        Returns:
            A new instance with the same content and additional kwargs.
        """
        content = json.dumps(self.content)
        instruction_copy = Instruction(**kwargs)
        instruction_copy.content = json.loads(content)
        instruction_copy.metadata.set("origin_ln_id", self.ln_id)
        return instruction_copy

    @staticmethod
    def _format_requested_fields(requested_fields: dict) -> dict:
        """
        Formats the requested fields into a JSON-parseable response format.

        Args:
            requested_fields: The fields requested in the instruction.

        Returns:
            The formatted requested fields.
        """
        format_ = f"""
        MUST RETURN JSON-PARSEABLE RESPONSE ENCLOSED BY JSON CODE BLOCKS. ----
        ```json
        {requested_fields}
        ```---
        """
        return {"response_format": format_.strip()}

    @classmethod
    def from_form(
        cls,
        form: Form,
        sender: str | None = None,
        recipient: Any = None,
        image: str | None = None,
    ) -> "Instruction":
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
        )


# File: lion_core/communication/instruction.py
