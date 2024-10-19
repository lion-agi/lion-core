import inspect
from typing import Any, Literal

from lionabc.exceptions import LionTypeError
from pydantic import BaseModel
from typing_extensions import override

from lion_core.communication.message import (
    MessageFlag,
    MessageRole,
    RoledMessage,
)
from lion_core.form.base import BaseForm
from lion_core.form.form import Form

from .utils import (
    format_image_content,
    format_text_content,
    prepare_instruction_content,
    prepare_request_response_format,
)


class Instruction(RoledMessage):
    """Represents an instruction message in the system."""

    @override
    def __init__(
        self,
        instruction: Any | MessageFlag = None,
        context: Any | MessageFlag = None,
        guidance: Any | MessageFlag = None,
        images: list | MessageFlag = None,
        sender: Any | MessageFlag = None,
        recipient: Any | MessageFlag = None,
        request_fields: dict | list | MessageFlag = None,
        request_model: BaseModel | MessageFlag = None,
        plain_content: str | None = None,
        image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
        protected_init_params: dict | None = None,
    ) -> None:
        """Initialize an Instruction instance."""
        message_flags = [
            instruction,
            context,
            images,
            sender,
            recipient,
            request_fields,
            image_detail,
            plain_content,
            request_model,
        ]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
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
    def guidance(self):
        """Return the guidance content."""
        return self.content.get(["guidance"], None)

    @property
    def instruction(self):
        """Return the main instruction content."""
        if "plain_content" in self.content:
            return self.content.get(["plain_content"])
        else:
            return self.content.get(["instruction"], None)

    def update_images(
        self,
        images: list | str,
        image_detail: Literal["low", "high", "auto"] = None,
    ) -> None:
        """Add new images and update the image detail level."""
        images = images if isinstance(images, list) else [images]
        _ima: list = self.content.get(["images"], [])
        _ima.extend(images)
        self.content["images"] = _ima

        if image_detail:
            self.content["image_detail"] = image_detail

    def update_guidance(self, guidance: str) -> None:
        """Update the guidance content of the instruction."""
        if guidance and isinstance(guidance, str):
            self.content["guidance"] = guidance
            return
        raise LionTypeError(
            "Invalid guidance. Guidance must be a string.",
        )

    def update_request_fields(self, request_fields: dict) -> None:
        """Update the requested fields in the instruction."""
        self.content["request_fields"].update(request_fields)
        format_ = prepare_request_response_format(
            request_fields=self.content["request_fields"],
        )
        self.content["request_response_format"] = format_

    def update_context(self, *args, **kwargs) -> None:
        """Add new context to the instruction."""
        self.content["context"] = self.content.get("context", [])
        if args:
            self.content["context"].extend(args)
        if kwargs:
            self.content["context"].append(kwargs)

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
    ) -> "Instruction":
        """Create an Instruction instance from a form."""
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
