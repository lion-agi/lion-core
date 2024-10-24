from collections.abc import Callable
from functools import lru_cache
from typing import Any, Literal

from lionabc import Observable
from lionfuncs import copy, validate_boolean
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    create_model,
    field_validator,
)
from pydantic.fields import FieldInfo

from lion_core.communication import (
    ActionRequest,
    ActionResponse,
    AssistantResponse,
    Instruction,
    System,
)
from lion_core.operative.action_model import (
    ActionRequestModel,
    ActionResponseModel,
)
from lion_core.operative.step_model import StepModel

from .msg_handlers import (
    create_action_request,
    create_action_response,
    create_assistant_response,
    create_instruction,
    create_system_message,
)


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
    action_request_model: ActionRequestModel = None,
    action_response_model: ActionResponseModel = None,
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
        return create_assistant_response(
            sender=sender,
            recipient=recipient,
            assistant_response=assistant_response,
        )
    return create_instruction(
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


@lru_cache(maxsize=1024)
def create_action(
    data=None,
    action_request_model: ActionRequestModel = None,
    output=None,
) -> list[ActionRequestModel] | ActionResponseModel | None:

    try:
        if data:
            return ActionRequestModel.create(data)

        return ActionResponseModel.create(
            action_request_model=action_request_model, output=output
        )
    except Exception:
        pass


@lru_cache(maxsize=1024)
def create_step_request_model(
    reason: bool = False,
    actions: bool = False,
    exclude_fields: list | dict | None = None,
    include_fields: list | dict | None = None,
    operative_model: type[BaseModel] | None = None,
    config_dict: ConfigDict | None = None,
    doc: str | None = None,
    validators: dict[str, Callable] | None = None,
    use_base_kwargs: bool = False,
    inherit_base: bool = True,
    field_descriptions: dict[str, str] | None = None,
    extra_fields: dict[str, FieldInfo] | None = None,
):
    extra_fields = extra_fields or {}
    extra_fields.update(StepModel.model_fields)

    fields = copy(extra_fields)

    if not reason:
        exclude_fields.append("reason")

    if not actions:
        exclude_fields.extend(["action_requests", "action_required"])

    else:
        validators = validators or {}
        validators["action_required"] = validate_action_required

    fields, class_kwargs, name = _prepare_fields(
        exclude_fields=exclude_fields,
        include_fields=include_fields,
        field_descriptions=field_descriptions,
        operative_model=operative_model,
        use_base_kwargs=use_base_kwargs,
        **fields,
    )
    if name == "BaseModel":
        name == "StepModel"

    return create_model(
        name + "Request",
        __config__=config_dict,
        __doc__=doc,
        __base__=operative_model if inherit_base else BaseModel,
        __validators__=validators,
        __cls_kwargs__=class_kwargs,
        **fields,
    )


def create_step_response(
    step_request: BaseModel,
    operative_model: type[BaseModel] | None = None,
    exclude_fields=None,
    **kwargs,
):
    """
    kwargs for field values
    """
    action_required = False
    if (
        "action_required" in step_request.model_fields
        and step_request.action_required
    ):
        action_required = True

    model = create_step_response_model(
        step_request=type(step_request),
        operative_model=operative_model or BaseModel,
        exclude_fields=exclude_fields or [],
        action_required=action_required,
    )

    dict_ = step_request.model_dump()
    dict_.update(kwargs)
    return model.model_validate(dict_)


@lru_cache(maxsize=1024)
def create_step_response_model(
    step_request: type[BaseModel],
    operative_model: type[BaseModel] | BaseModel,
    exclude_fields: list = [],
    action_required: bool = False,
) -> type[BaseModel]:

    operative_model = step_request
    fields = copy(StepModel.model_fields)
    fields.update(step_request.model_fields)

    if not action_required:
        exclude_fields.extend(
            ["action_responses", "action_required", "action_requests"]
        )

    for k in list(fields.keys()):
        if k in exclude_fields:
            fields.pop(k, None)

    name = None
    if hasattr(operative_model, "class_name"):
        if callable(operative_model.class_name):
            name = operative_model.class_name()
        else:
            name = operative_model.class_name
    else:
        name = operative_model.__name__
        if name == "BaseModel":
            name = "StepModel"

    return create_model(name + "Response", __base__=BaseModel, **fields)


def _prepare_fields(
    exclude_fields: list | dict | None = None,
    include_fields: list | dict | None = None,
    field_descriptions: dict = None,
    use_base_kwargs: bool = False,
    operative_model=None,
    **kwargs,
):
    kwargs = copy(kwargs)
    operative_model = operative_model or BaseModel

    if exclude_fields:
        exclude_fields = (
            list(exclude_fields.keys())
            if isinstance(exclude_fields, dict)
            else exclude_fields
        )

    if include_fields:
        include_fields = (
            list(include_fields.keys())
            if isinstance(include_fields, dict)
            else include_fields
        )

    if exclude_fields and include_fields:
        for i in include_fields:
            if i in exclude_fields:
                raise ValueError(
                    f"Field {i} is repeated. Operation include "
                    "fields and exclude fields cannot have common elements."
                )

    if exclude_fields:
        for i in exclude_fields:
            kwargs.pop(i, None)

    if include_fields:
        for i in list(kwargs.keys()):
            if i not in include_fields:
                kwargs.pop(i, None)

    fields = {k: (v.annotation, v) for k, v in kwargs.items()}

    if field_descriptions:
        for field_name, description in field_descriptions.items():
            if field_name in fields:
                field_info = fields[field_name]
                if isinstance(field_info, tuple):
                    fields[field_name] = (
                        field_info[0],
                        Field(..., description=description),
                    )
                elif isinstance(field_info, FieldInfo):
                    fields[field_name] = field_info.model_copy(
                        update={"description": description}
                    )

    # Prepare class attributes
    class_kwargs = {}
    if use_base_kwargs:
        class_kwargs.update(
            {
                k: getattr(operative_model, k)
                for k in operative_model.__dict__
                if not k.startswith("__")
            }
        )

    class_kwargs = {k: v for k, v in class_kwargs.items() if k in fields}

    name = None
    if hasattr(operative_model, "class_name"):
        if callable(operative_model.class_name):
            name = operative_model.class_name()
        else:
            name = operative_model.class_name
    else:
        name = operative_model.__name__

    return fields, class_kwargs, name


@field_validator("action_required", mode="before")
def validate_action_required(cls, value: Any) -> bool:
    try:
        return validate_boolean(value)
    except Exception:
        return False
