from typing import Any

from lionfuncs import validate_boolean
from pydantic import BaseModel, Field, field_validator

from .action_model import ActionRequestModel, ActionResponseModel
from .reason_model import ReasonModel


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
        except Exception:
            return False
