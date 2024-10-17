from typing import Any

from lionabc import AbstractElement
from lionfuncs import copy, to_dict, to_num, validate_str
from pydantic import BaseModel, Field, create_model, field_validator

from lion_core.operative.utils import prepare_fields


class ReasonModel(BaseModel):

    title: str | None = None
    content: str | None = None
    confidence_score: float | None = Field(  # -1 means failed to parse
        None,
        description=(
            "Provide an objective numeric confidence score between 0 and"
            " 1 (with 3 decimal places) indicating how likely you "
            "successfully achieved the task according to user expectation."
            " Interpret the score as:\n"
            "- **1**: Very confident in a good job.\n"
            "- **0**: Not confident at all.\n"
            "- **[0.8, 1]**: You can continue the path of reasoning if "
            "needed.\n"
            "- **[0.5, 0.8)**: Recheck your reasoning and consider "
            "reverting to a "
            "previous, more confident reasoning path.\n"
            "- **[0, 0.5)**: Stop because the reasoning is starting "
            "to be off track."
        ),
        examples=[0.821, 0.257, 0.923, 0.439],
    )

    @field_validator("confidence_score", mode="before")
    def validate_confidence_score(cls, value: Any) -> float:
        try:
            return to_num(
                value,
                upper_bound=1,
                lower_bound=0,
                num_type=float,
                precision=3,
            )
        except Exception:
            return -1


class ActionRequestModel(BaseModel):

    function: str | None = Field(
        None,
        title="Function",
        description=(
            "Specify the name of the function to execute. **Choose "
            "from the provided "
            "`tool_schema`; do not invent function names.**"
        ),
        examples=["print", "add", "len"],
    )
    arguments: dict[str, Any] = Field(
        {},
        title="Arguments",
        description=(
            "Provide the arguments to pass to the function as a "
            "dictionary. **Use "
            "argument names and types as specified in the "
            "`tool_schema`; do not "
            "invent argument names.**"
        ),
        examples=[{"num1": 1, "num2": 2}, {"x": "hello", "y": "world"}],
    )

    @field_validator("function", mode="before")
    def validate_function(cls, value: Any) -> str:
        return validate_str(value, "function")

    @field_validator("arguments", mode="before")
    def validate_arguments(cls, value: Any) -> dict[str, Any]:
        return to_dict(
            value,
            fuzzy_parse=True,
            suppress=True,
            recursive=True,
        )


class ActionResponseModel(BaseModel):

    function: str
    arguments: dict[str, Any]
    output: Any


class OperativeModel(BaseModel, AbstractElement):

    def to_dict(self):
        return self.model_dump()


class StepModel(BaseModel):

    reason: ReasonModel | None = Field(
        None,
        title="Reason",
        description="a concise reasoning for the step",
    )
    action_responses: list[ActionResponseModel] = []
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
    action_required: bool = False

    @classmethod
    def parse_request_to_response(
        cls,
        request: OperativeModel,
        exclude_fields: list | dict | None = None,
        include_fields: list | dict | None = None,
        action_responses: list[ActionResponseModel] | None = None,
    ) -> OperativeModel:
        response_model = cls.as_response_model(
            request,
            exclude_fields=exclude_fields,
            include_fields=include_fields,
        )

        config = request.to_dict()
        if (
            action_responses
            and "action_responses" in response_model.model_fields
        ):
            config["action_responses"] = action_responses
        return response_model(**config)

    @classmethod
    def as_request_model(
        cls,
        reason: bool = False,
        actions: bool = False,
        exclude_fields: list | dict | None = None,
        include_fields: list | dict | None = None,
        operative_model: type[OperativeModel] | None = None,
        **kwargs,
    ):
        operative_model = operative_model or OperativeModel
        fields = copy(cls.model_fields)
        fields.pop("action_responses", None)

        fields = prepare_fields(
            exclude_fields=exclude_fields,
            include_fields=include_fields,
            **fields,
            **kwargs,
        )

        if not reason:
            fields.pop("reason", None)
        if not actions:
            fields.pop("action_requests", None)
            fields.pop("action_required", None)

        return create_model(
            operative_model.class_name() + "StepRequest",
            __base__=operative_model,
            **fields,
        )

    @classmethod
    def as_response_model(
        cls,
        request: OperativeModel,
        exclude_fields: list | dict | None = None,
        include_fields: list | dict | None = None,
        operative_model: type[OperativeModel] | None = None,
        **kwargs,
    ):
        operative_model = operative_model or OperativeModel
        fields = copy(cls.model_fields)
        fields: dict = prepare_fields(
            exclude_fields=exclude_fields,
            include_fields=include_fields,
            **fields,
            **kwargs,
        )

        if ("action_required" not in request.model_fields) or (
            not request.action_required
        ):
            fields.pop("action_required", None)
            fields.pop("action_responses", None)
            fields.pop("action_requests", None)

        return create_model(
            operative_model.class_name() + "StepResponse",
            __base__=operative_model,
            **fields,
        )


__all__ = [
    "OperativeModel",
    "StepModel",
    "ActionRequestModel",
    "ActionResponseModel",
    "ReasonModel",
]
