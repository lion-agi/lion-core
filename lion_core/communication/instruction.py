import inspect
from typing import Any, Literal, Type

from typing_extensions import override

from lion_core.communication.message import MessageFlag, MessageRole, RoledMessage
from lion_core.exceptions import LionTypeError
from lion_core.form.base import BaseForm
from lion_core.form.form import Form
from lion_core.generic.note import Note, note
from lion_core.setting import LN_UNDEFINED


def prepare_request_response_format(request_fields: dict) -> str:
    return f"""
MUST RETURN JSON-PARSEABLE RESPONSE ENCLOSED BY JSON CODE BLOCKS. ---
```json
{request_fields}
```---
""".strip()


_f = lambda idx, x: (
    {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{idx}",
            "detail": x,
        },
    }
)


def format_image_content(
    text_content: str,
    images: list,
    image_detail: Literal["low", "high", "auto"],
) -> dict[str, Any]:
    content = [{"type": "text", "text": text_content}]

    for i in images:
        content.append(_f(i, image_detail))
    return content


def prepare_instruction_content(
    guidance: str | None = None,
    instruction: str | None = None,
    context: str | dict | list | None = None,
    request_fields: dict | None = None,
    images: str | list | None = None,  # list of base64 encoded images
    image_detail: Literal["low", "high", "auto"] | None = None,
) -> Note:
    """
    Prepares the content for an instruction message.

    This function constructs a `Note` object containing various elements of an instruction,
    such as guidance, instruction text, context, images, and request fields. It also formats
    the request fields into a response format if provided.

    Args:
        guidance (str | None): High-level task guidance or instructions. Defaults to None.
        instruction (str | None): The main instruction or task description. Defaults to "N/A".
        context (str | dict | list | None): Additional context related to the instruction.
            Can be a string, dictionary, or list. Defaults to None.
        request_fields (dict | None): A dictionary of fields that the response should include.
            If provided, the request fields will be formatted into a JSON-parsable response format. Defaults to None.
        images (str | list | None): A list or single base64 encoded string representing images associated with the instruction. Defaults to None.
        image_detail (Literal["low", "high", "auto"] | None): The level of detail for image processing. Defaults to None.

    Returns:
        Note: A `Note` object containing the formatted instruction content.

    Raises:
        None: The function does not raise exceptions under normal operation.
    """

    out_ = {}
    if guidance:
        out_["guidance"] = guidance

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

    return note(
        **{k: v for k, v in out_.items() if v not in [None, LN_UNDEFINED]},
    )


class Instruction(RoledMessage):
    """
    Represents an instruction message in the system.

    The `Instruction` class is used to manage and format instruction messages
    within the LION system. It extends `RoledMessage` and provides functionality
    for handling various types of content, including context, images, and
    requested fields. The class also supports creating instructions from forms
    and updating content dynamically.

    Attributes:
        content (Note): Contains instruction details, context, images, and request fields.
        sender (str): The sender of the instruction, defaults to "user".
        recipient (str): The recipient of the instruction, defaults to "N/A".

    Properties:
        guidance (str): Returns the guidance content.
        instruction (str): Returns the main instruction content.

    Methods:
        update_images(images, image_detail): Adds new images and updates image detail level.
        update_guidance(guidance): Updates the guidance content of the instruction.
        update_request_fields(request_fields): Updates the requested fields in the instruction.
        update_context(*args, **kwargs): Adds new context to the instruction.
        from_form(cls, form, sender, recipient, images, image_detail, ...): Creates an `Instruction` instance from a form.
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
        request_fields: dict | MessageFlag = None,
        image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
        protected_init_params: dict | None = None,
    ):
        """
        Initializes an Instruction instance.

        Args:
            instruction (str|MessageFlag): The main instruction content.
            context (str|dict|list|MessageFlag, optional): Additional context for the instruction.
            guidance (str|MessageFlag, optional): Additional guidance content.
            images (list|MessageFlag, optional): List of images related to the instruction.
            sender (str|MessageFlag, optional): The sender of the instruction. Defaults to "user".
            recipient (str|MessageFlag, optional): The intended recipient of the instruction. Defaults to "N/A".
            request_fields (dict|MessageFlag, optional): Dictionary of fields requested in the response.
            image_detail (Literal["low", "high", "auto"]|MessageFlag, optional): Level of detail for image processing.
            protected_init_params (dict, optional): Protected init parameters for loading.

        Raises:
            LionTypeError: If the provided arguments do not match expected types.
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
                guidance=guidance,
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
    def guidance(self):
        """Returns the guidance content."""
        return self.content.get(["guidance"], None)

    @property
    def instruction(self):
        """Returns the main instruction content."""
        return self.content.get(["instruction"], None)

    def update_images(
        self,
        images: list | str,
        image_detail: Literal["low", "high", "auto"] = None,
    ):
        """
        Adds new images and updates the image detail level.

        Args:
            images (list|str): A list or a single base64-encoded image string.
            image_detail (Literal["low", "high", "auto"], optional): The detail level of the images.
        """
        images = images if isinstance(images, list) else [images]
        _ima: list = self.content.get(["images"], [])
        _ima.extend(images)
        self.content["images"] = _ima

        if image_detail:
            self.content["image_detail"] = image_detail

    def update_guidance(self, guidance: str):
        """
        Updates the guidance content of the instruction.

        Args:
            guidance (str): The new guidance content.

        Raises:
            LionTypeError: If the guidance is not a valid string.
        """
        if guidance and isinstance(guidance, str):
            self.content["guidance"] = guidance
            return
        raise LionTypeError(
            "Invalid guidance. Guidance must be a string.",
        )

    def update_request_fields(self, request_fields: dict):
        """
        Updates the requested fields in the instruction.

        Args:
            request_fields (dict): A dictionary of the requested fields.
        """
        self.content["request_fields"].update(request_fields)
        self.content["request_response_format"] = prepare_request_response_format(
            request_fields=self.content["request_fields"],
        )

    def update_context(self, *args, **kwargs):
        """
        Adds new context to the instruction.

        This method can add additional context from both positional and keyword arguments.
        """
        self.content["context"] = self.content.get("context", [])
        if args:
            self.content["context"].extend(args)
        if kwargs:
            self.content["context"].append(kwargs)

    @override
    def _format_content(self) -> dict[str, Any]:
        """
        Formats the content of the instruction.

        This method handles the conversion of content to the required format, including the integration of images.

        Returns:
            dict[str, Any]: The formatted content.
        """
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
            form (BaseForm | Type[Form]): The form containing instruction details.
            sender (str, optional): The sender of the instruction.
            recipient (Any, optional): The recipient of the instruction.
            images (str, optional): The image content in base64 encoding.
            image_detail (str, optional): The detail level of the images.
            strict (bool, optional): Strict mode for the form validation.
            assignment (str, optional): The assignment description.
            task_description (str, optional): Description of the task.
            fill_inputs (bool, optional): Whether to fill inputs automatically.
            none_as_valid_value (bool, optional): Whether None is considered a valid input.
            input_value_kwargs (dict, optional): Additional kwargs for input values.

        Returns:
            Instruction: The created Instruction instance.

        Raises:
            LionTypeError: If the form is not a valid subclass or instance of `BaseForm`.
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
                "Invalid form. The form must be a subclass or an instance of BaseForm."
            ) from e


__all__ = ["Instruction"]

# File: lion_core/communication/instruction.py
