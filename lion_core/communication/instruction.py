"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import inspect
from typing import Any, Literal, override, Type

from lion_core.setting import LN_UNDEFINED
from lion_core.generic.note import Note, note
from lion_core.form.base import BaseForm
from lion_core.communication.message import (
    RoledMessage,
    MessageRole,
    MessageFlag,
)
from lion_core.form.form import Form


def prepare_request_response_format(request_fields: dict) -> str:
    return f"""
MUST RETURN JSON-PARSEABLE RESPONSE ENCLOSED BY JSON CODE BLOCKS. ---
```json
{request_fields}
```---
""".strip()


def format_image_content(
    text_content: str,
    images: list,
    image_detail: Literal["low", "high", "auto"],
) -> dict[str, Any]:
    content = [{"type": "text", "text": text_content}]

    for i in images:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{i}",
                    "detail": image_detail,
                },
            }
        )
    return content


def prepare_instruction_content(
    instruction: str | None = None,
    context: str | dict | list | None = None,
    request_fields: dict | None = None,
    images: str | list | None = None,  # list of base64 encoded images
    image_detail: Literal["low", "high", "auto"] | None = None,
) -> Note:
    out_ = {}

    out_["instruction"] = instruction or "N/A"
    if context:
        out_["context"] = context if not isinstance(context, str) else [context]
    if images:
        out_["images"] = images if isinstance(images, list) else [images]
        out_["image_detail"] = image_detail or "low"
    if request_fields:
        out_["request_fields"] = request_fields
        out_["request_response_format"] = prepare_request_response_format(
            request_fields
        )

    return note(**{k: v for k, v in out_.items() if v not in [None, LN_UNDEFINED]})


class Instruction(RoledMessage):
    """Represents an instruction message in the system.

    This class extends RoledMessage to handle instruction-specific content,
    including context, images, and request fields. It supports both regular
    initialization and cloning/loading from existing messages.

    Attributes:
        content (Note): Contains instruction details, context, and image info.
        sender (str): The sender of the instruction, defaults to "user".
        recipient (str): The recipient of the instruction, defaults to "N/A".

    Properties:
        instruct (str): Returns the main instruction content.

    Methods:
        update_context(*args, **kwargs): Adds new context to the instruction.
        from_task(cls, task, sender, recipient, images, image_detail):
            Creates an Instruction instance from a BaseTask object.
    """

    @override
    def __init__(
        self,
        instruction: Any | MessageFlag,
        context: Any | MessageFlag = None,
        images: list | MessageFlag = None,
        sender: Any | MessageFlag = None,
        recipient: Any | MessageFlag = None,
        request_fields: dict | MessageFlag = None,
        image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
        protected_init_params: dict | None = None,
    ):
        """Initialize an Instruction instance.

        Args:
            instruction: The main instruction content.
            context: Additional context for the instruction.
            images: List of images related to the instruction.
            sender: The sender of the instruction.
            recipient: The intended recipient of the instruction.
            request_fields: Dictionary of fields requested in the response.
            image_detail: Level of detail for image processing.
            protected_init_params: Protected init parameters for loading.
        """
        message_flags = [
            instruction,
            context,
            images,
            sender,
            recipient,
            request_fields,
            image_detail,
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
                instruction=instruction,
                context=context,
                images=images,
                request_fields=request_fields,
                image_detail=image_detail,
            ),
            sender=sender or "user",
            recipient=recipient or "N/A",
        )

    @property
    def instruct(self):
        """Returns the main instruction content."""
        return self.content.get(["instruction"], None)

    def update_request_fields(self, request_fields: dict):
        self.content["request_fields"].update(request_fields)
        self.content["request_response_format"] = prepare_request_response_format(
            self.content["request_fields"]
        )

    def update_context(self, *args, **kwargs):
        """Adds new context to the instruction."""
        self.content["context"] = self.content.get("context", [])
        if args:
            self.content["context"].extend(args)
        if kwargs:
            self.content["context"].append(kwargs)

    @override
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

    @classmethod
    def from_form(
        cls,
        *,
        form: BaseForm | Type[Form],
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

        if inspect.isclass(form) and issubclass(form, BaseForm):
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
                form,
                assignment=assignment or form.assignment,
                strict=strict,
                task_description=task_description,
                fill_inputs=fill_inputs,
                none_as_valid_value=none_as_valid_value,
                **(input_value_kwargs or {}),
            )

        if isinstance(form, Form):
            self = cls(
                **form.instruction_dict,
                images=images,
                sender=sender,
                recipient=recipient,
                image_detail=image_detail,
            )
            self.metadata.set(["original_form"], form.ln_id)
            return self

        raise ValueError(
            "Invalid form. The form must be a subclass or an instance of BaseForm."
        )


__all__ = ["Instruction"]

# File: lion_core/communication/instruction.py
