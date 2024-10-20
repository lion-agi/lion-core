import logging
from typing import Any

from lionfuncs import copy, validate_boolean
from pydantic import BaseModel, Field, create_model, field_validator

from .action_model import ActionRequestModel, ActionResponseModel
from .reason_model import ReasonModel
from .utils import prepare_fields


class StepModel(BaseModel):
    title: str = Field(
        ...,
        title="Title",
        description="Provide a concise title summarizing the step.",
    )
    content: str = Field(
        ...,
        title="Content",
        description="Describe the content of the step in detail.",
    )
    reason: ReasonModel | None = Field(
        None,
        title="Reason",
        description="**a concise reasoning for the step**",
    )
    action_responses: list[ActionResponseModel] = Field(
        [], description="**Do not fill**"
    )
    action_requests: list[ActionRequestModel] = Field(
        [],
        title="Actions",
        description=(
            "List of actions to be performed if `action_required` "
            "is **True**. Leave empty if no action is required. "
            "**When providing actions, you must choose from the "
            "provided `tool_schemas`. Do not invent function or "
            "argument names.**"
        ),
    )
    action_required: bool = Field(
        False,
        title="Action Required",
        description=(
            "Specify whether the step requires actions to be "
            "performed. If **True**, the actions in `action_requests` "
            "must be performed. If **False**, the actions in "
            "`action_requests` are optional. If no tool_schemas"
            " are provided, this field is ignored."
        ),
    )

    @field_validator("action_required", mode="before")
    def validate_action_required(cls, value: Any) -> bool:
        try:
            return validate_boolean(value)
        except Exception as e:
            logging.error(
                f"Failed to convert {value} to a boolean. Error: {e}"
            )
            return False

    @classmethod
    def parse_request_to_response(
        cls,
        request: BaseModel,
        operative_model: type[BaseModel],
        exclude_fields: list | dict | None = None,
        include_fields: list | dict | None = None,
        **kwargs,
    ) -> BaseModel:
        response_model = cls.as_response_model(
            request,
            exclude_fields=exclude_fields,
            include_fields=include_fields,
            operative_model=operative_model,
        )
        return response_model(**kwargs)

    @classmethod
    def as_request_model(
        cls,
        reason: bool = False,
        actions: bool = False,
        exclude_fields: list | dict | None = None,
        include_fields: list | dict | None = None,
        operative_model: type[BaseModel] | None = None,
        **kwargs,
    ):
        operative_model = operative_model or BaseModel
        fields = copy(cls.model_fields)

        fields = prepare_fields(
            exclude_fields=exclude_fields,
            include_fields=include_fields,
            **fields,
            **kwargs,
        )
        fields.pop("action_responses", None)

        if not reason:
            fields.pop("reason", None)
        if not actions:
            fields.pop("action_requests", None)
            fields.pop("action_required", None)

        name = None
        if hasattr(operative_model, "class_name"):
            name = operative_model.class_name()
        else:
            name = operative_model.__name__
            if name == "BaseModel":
                name = cls.__name__

        return create_model(
            name + "Request",
            __base__=operative_model,
            **fields,
        )

    @classmethod
    def as_response_model(
        cls,
        request_model: BaseModel,
        exclude_fields: list | dict | None = None,
        include_fields: list | dict | None = None,
        operative_model: type[BaseModel] | None = None,
        **kwargs,
    ):
        operative_model = operative_model or BaseModel
        fields = copy(cls.model_fields)
        fields: dict = prepare_fields(
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            **fields,
            **kwargs,
        )

        if ("action_required" not in request_model.model_fields) or (
            not request_model.action_required
        ):
            fields.pop("action_required", None)
            fields.pop("action_responses", None)
            fields.pop("action_requests", None)

        if "reason" not in request_model.model_fields:
            fields.pop("reason", None)

        name = None
        if hasattr(operative_model, "class_name"):
            if callable(operative_model.class_name):
                name = operative_model.class_name()
            else:
                name = operative_model.class_name
        else:
            name = operative_model.__name__
            if name == "BaseModel":
                name = cls.__name__

        return create_model(
            name + "Response",
            __base__=operative_model,
            **fields,
        )


__all__ = ["StepModel"]
