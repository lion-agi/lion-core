from __future__ import annotations

import inspect
from typing import Any, Literal

from lionabc.exceptions import LionTypeError
from lionfuncs import break_down_pydantic_annotation, copy, to_str
from pydantic import BaseModel
from typing_extensions import override

from lion_core.communication.message import (
    MessageFlag,
    MessageRole,
    RoledMessage,
)
from lion_core.communication.utils import (
    format_image_content,
    format_text_content,
    prepare_instruction_content,
    prepare_request_response_format,
)
from lion_core.form.base import BaseForm
from lion_core.form.form import Form


class Instruction(RoledMessage):
    """
    Represents an instruction message in the system.

    This class encapsulates various components of an instruction, including
    the main instruction content, guidance, context, and request fields.
    """

    @override
    def __init__(
        self,
        instruction: Any | MessageFlag,
        context: Any | MessageFlag = None,
        guidance: Any | MessageFlag = None,
        images: list | MessageFlag = None,
        sender: Any | MessageFlag = None,
        recipient: Any | MessageFlag = None,
        request_fields: dict | list | MessageFlag = None,
        plain_content: str | MessageFlag = None,
        image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
        request_model: BaseModel | MessageFlag = None,
        protected_init_params: dict | None = None,
    ) -> None:
        """
        Initialize an Instruction instance.

        Args:
            instruction: The main instruction content.
            context: Additional context for the instruction.
            guidance: Guidance information for the instruction.
            images: List of images associated with the instruction.
            sender: The sender of the instruction.
            recipient: The recipient of the instruction.
            request_fields: Fields requested in the instruction.
            plain_content: Plain text content of the instruction.
            image_detail: Level of detail for images.
            request_model: A BaseModel for structured requests.
            protected_init_params: Protected initialization parameters.
        """
        message_flags = [
            instruction,
            context,
            guidance,
            images,
            sender,
            recipient,
            request_fields,
            plain_content,
            image_detail,
            request_model,
        ]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            protected_init_params = protected_init_params or {}
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.USER)
            return

        super().__init__(
            role=MessageRole.USER,
            content=prepare_instruction_content(
                guidance=guidance,
                instruction=instruction,
                context=context,
                images=images,
                request_fields=request_fields,
                plain_content=plain_content,
                image_detail=image_detail,
                request_model=request_model,
            ),
            sender=sender or "user",
            recipient=recipient or "N/A",
        )

    @property
    def guidance(self) -> str | None:
        """Return the guidance content of the instruction."""
        return self.content.get(["guidance"], None)

    @property
    def instruction(self) -> str | dict | None:
        """Return the main instruction content."""
        if "plain_content" in self.content:
            return self.content["plain_content"]
        else:
            return self.content.get(["instruction"], None)

    def update_instruction(
        self, instruction: str | dict = None, plain_content: str | None = None
    ) -> None:
        """
        Update the instruction content.

        Args:
            instruction: New instruction content.
            plain_content: New plain text content.
        """
        if instruction:
            self.content["instruction"] = instruction
        if plain_content:
            self.content["plain_content"] = plain_content

    def update_images(
        self,
        images: list | str,
        image_detail: Literal["low", "high", "auto"] = None,
    ) -> None:
        """
        Add new images and update the image detail level.

        Args:
            images: New images to add.
            image_detail: New image detail level.
        """
        images = images if isinstance(images, list) else [images]
        _ima: list = self.content.get(["images"], [])
        _ima.extend(images)
        self.content["images"] = _ima

        if image_detail:
            self.content["image_detail"] = image_detail

    def update_guidance(self, guidance: str) -> None:
        """
        Update the guidance content of the instruction.

        Args:
            guidance: New guidance content.

        Raises:
            LionTypeError: If guidance is not a string.
        """
        if guidance:
            self.content["guidance"] = (
                to_str(guidance) if not isinstance(guidance, str) else guidance
            )
            return
        raise LionTypeError(
            "Invalid guidance. Guidance must be a string.",
        )

    def update_request_model(
        self, request_model: BaseModel | type[BaseModel]
    ) -> None:
        """
        Update the request model and related fields.

        Args:
            request_model: New request model.
        """
        request_fields = break_down_pydantic_annotation(request_model)
        self.update_context(
            respond_schema_info=request_model.model_json_schema()
        )
        self.content["request_fields"] = {}
        self.update_request_fields(request_fields)

    def update_request_fields(self, request_fields: dict) -> None:
        """
        Update the requested fields in the instruction.

        Args:
            request_fields: New request fields to update.
        """
        self.content["request_fields"].update(request_fields)
        format_ = prepare_request_response_format(
            request_fields=self.content["request_fields"],
        )
        self.content["request_response_format"] = format_

    def update_context(self, *args, **kwargs) -> None:
        """
        Add new context to the instruction.

        Args:
            *args: Positional arguments to add to context.
            **kwargs: Keyword arguments to add to context.
        """
        self.content["context"] = self.content.get("context", [])
        if args:
            self.content["context"].extend(args)
        if kwargs:
            kwargs = copy(kwargs)
            for k, v in kwargs.items():
                self.content["context"].append({k: v})

    def update(
        self,
        *args,
        guidance: str | None = None,
        instruction: str | dict | None = None,
        request_fields: dict | list[str] | None = None,
        plain_content: str | None = None,
        request_model: BaseModel | None = None,
        images: str | list | None = None,
        image_detail: Literal["low", "high", "auto"] | None = None,
        **kwargs,
    ):
        """
        Update multiple aspects of the instruction.

        Args:
            *args: Positional arguments for context update.
            guidance: New guidance content.
            instruction: New instruction content.
            request_fields: New request fields.
            plain_content: New plain text content.
            request_model: New request model.
            images: New images to add.
            image_detail: New image detail level.
            **kwargs: Additional keyword arguments for context update.

        Raises:
            ValueError: If both request_model and request_fields are provided.
        """
        if request_model and request_fields:
            raise ValueError(
                "You cannot pass both request_model and request_fields "
                "to create_instruction"
            )
        if guidance:
            self.update_guidance(guidance)
        if instruction or plain_content:
            self.update_instruction(instruction, plain_content)
        if request_fields:
            self.update_request_fields(request_fields)
        if request_model:
            self.update_request_model(request_model)
        if images:
            self.update_images(images, image_detail)
        self.update_context(*args, **kwargs)

    @override
    def _format_content(self) -> dict[str, Any]:
        """Format the content of the instruction."""

        content = self.content.to_dict()
        text_content = format_text_content(content)
        if "images" not in content:
            return {"role": self.role.value, "content": text_content}
        else:
            content = format_image_content(
                text_content=text_content,
                images=self.content.get(["images"]),
                image_detail=self.content.get(["image_detail"]),
            )
            return {"role": self.role.value, "content": content}

    @classmethod
    def from_form(
        cls,
        form: BaseForm | type[Form],
        *,
        sender: str | None = None,
        recipient: Any = None,
        images: str | None = None,
        image_detail: str | None = None,
        strict: bool = None,
        assignment: str = None,
        task_description: str = None,
        fill_inputs: bool = True,
        none_as_valid_value: bool = False,
        input_value_kwargs: dict = None,
    ) -> Instruction:
        """
        Create an Instruction instance from a form.

        Args:
            form: The form to create the instruction from.
            sender: The sender of the instruction.
            recipient: The recipient of the instruction.
            images: Images to include in the instruction.
            image_detail: Image detail level.
            strict: Whether to use strict mode.
            assignment: Assignment for the form.
            task_description: Description of the task.
            fill_inputs: Whether to fill input fields.
            none_as_valid_value: Whether to treat None as a valid value.
            input_value_kwargs: Additional keyword arguments for input values.

        Returns:
            An Instruction instance created from the form.

        Raises:
            LionTypeError: If the form is invalid.
        """
        try:
            if inspect.isclass(form) and issubclass(form, Form):
                form = form(
                    strict=strict,
                    assignment=assignment,
                    task_description=task_description,
                    fill_inputs=fill_inputs,
                    none_as_valid_value=none_as_valid_value,
                    **(input_value_kwargs or {}),
                )

            elif isinstance(form, BaseForm) and not isinstance(form, Form):
                form = Form.from_form(
                    form=form,
                    assignment=assignment or form.assignment,
                    strict=strict,
                    task_description=task_description,
                    fill_inputs=fill_inputs,
                    none_as_valid_value=none_as_valid_value,
                    **(input_value_kwargs or {}),
                )

            if isinstance(form, Form):
                self = cls(
                    guidance=form.guidance,
                    images=images,
                    sender=sender,
                    recipient=recipient,
                    image_detail=image_detail,
                    **form.instruction_dict,
                )
                self.metadata.set(["original_form"], form.ln_id)
                return self
        except Exception as e:
            raise LionTypeError(
                "Invalid form. The form must be a subclass or an instance "
                "of BaseForm."
            ) from e


__all__ = ["Instruction"]

# File: lion_core/communication/instruction.py
