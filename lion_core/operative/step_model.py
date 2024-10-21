import logging
from collections.abc import Callable
from typing import Any

from lionfuncs import validate_boolean
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    create_model,
    field_validator,
)
from pydantic.fields import FieldInfo

from .action_model import ActRequestModel, ActResponseModel
from .reason_model import ReasonModel
from .utils import prepare_fields


class StepModel(BaseModel):
    title: str | None = Field(
        None,
        title="Title",
        description="Provide a concise title summarizing the step.",
    )
    content: str | None = Field(
        None,
        title="Content",
        description="Describe the content of the step in detail.",
    )
    reason: ReasonModel | None = Field(
        None,
        title="Reason",
        description="**a concise reasoning for the step**",
    )
    action_responses: list[ActResponseModel] = Field(
        [], description="**Do not fill**"
    )
    action_requests: list[ActRequestModel] = Field(
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
        request_model: BaseModel,
        data: dict,
        exclude_fields: list | dict | None = None,
        operative_model: type[BaseModel] | None = None,
        config_dict: ConfigDict | None = None,
        doc: str | None = None,
        validators: dict[str, Callable] | None = None,
        use_base_kwargs: bool = False,
        inherit_base: bool = True,
        field_descriptions: dict[str, str] | None = None,
        frozen: bool = False,
        extra_fields: dict[str, FieldInfo] | None = None,
        use_all_fields: bool = True,
    ) -> BaseModel:
        response_model = cls.as_response_model(
            request_model=request_model,
            exclude_fields=exclude_fields,
            operative_model=operative_model,
            config_dict=config_dict,
            doc=doc,
            validators=validators,
            use_base_kwargs=use_base_kwargs,
            inherit_base=inherit_base,
            field_descriptions=field_descriptions,
            frozen=frozen,
            extra_fields=extra_fields,
            use_all_fields=use_all_fields,
        )
        return response_model.model_validate(data)

    @classmethod
    def as_request_model(
        cls,
        reason: bool = False,
        actions: bool = False,
        exclude_fields: list | dict | None = None,
        operative_model: type[BaseModel] | None = None,
        config_dict: ConfigDict | None = None,
        doc: str | None = None,
        validators: dict[str, Callable] | None = None,
        use_base_kwargs: bool = False,
        inherit_base: bool = True,
        field_descriptions: dict[str, str] | None = None,
        frozen: bool = False,
        extra_fields: dict[str, FieldInfo] | None = None,
        use_all_fields: bool = True,
    ) -> type[BaseModel]:
        """kwargs, extra fields, dict[str: FieldInfo]"""

        exclude_fields = exclude_fields or []
        exclude_fields.append("action_responses")

        if not reason:
            exclude_fields.append("reason")

        if not actions:
            exclude_fields.extend(["action_requests", "action_required"])

        else:
            validators = validators or {}
            validators["action_required"] = cls.validate_action_required

        fields, class_kwargs, name = prepare_fields(
            cls,
            exclude_fields=exclude_fields,
            use_all_fields=use_all_fields,
            field_descriptions=field_descriptions,
            operative_model=operative_model,
            use_base_kwargs=use_base_kwargs,
            **(extra_fields or {}),
        )

        model: type[BaseModel] = create_model(
            name + "Request",
            __config__=config_dict,
            __doc__=doc,
            __base__=operative_model if inherit_base else BaseModel,
            __validators__=validators,
            __cls_kwargs__=class_kwargs,
            **fields,
        )
        if frozen:
            model.model_config.frozen = True
        return model

    @classmethod
    def as_response_model(
        cls,
        request_model: BaseModel,
        exclude_fields: list | dict | None = None,
        operative_model: type[BaseModel] | None = None,
        config_dict: ConfigDict | None = None,
        doc: str | None = None,
        validators: dict[str, Callable] | None = None,
        use_base_kwargs: bool = False,
        inherit_base: bool = True,
        field_descriptions: dict[str, str] | None = None,
        frozen: bool = False,
        extra_fields: dict[str, FieldInfo] | None = None,
        use_all_fields: bool = True,
    ) -> type[BaseModel]:

        exclude_fields = exclude_fields or []

        if ("action_required" not in request_model.model_fields) or (
            not request_model.action_required
        ):
            exclude_fields.extend(
                ["action_responses", "action_required", "action_requests"]
            )
        if "reason" not in request_model.model_fields:
            exclude_fields.extend(["reason"])

        fields, class_kwargs, name = prepare_fields(
            cls,
            exclude_fields=exclude_fields,
            use_all_fields=use_all_fields,
            field_descriptions=field_descriptions,
            operative_model=operative_model,
            use_base_kwargs=use_base_kwargs,
            **(extra_fields or {}),
        )

        model: type[BaseModel] = create_model(
            name + "Response",
            __config__=config_dict,
            __doc__=doc,
            __base__=operative_model if inherit_base else BaseModel,
            __validators__=validators,
            __cls_kwargs__=class_kwargs,
            **fields,
        )
        if frozen:
            model.model_config.frozen = True
        return model


__all__ = ["StepModel"]
