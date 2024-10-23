from __future__ import annotations

from typing import Any

from lionfuncs import to_dict
from pydantic import BaseModel, Field, field_validator

from .utils import parse_action_request


class ActionRequestModel(BaseModel):

    function: str | None = Field(
        None,
        title="Function",
        description=(
            "Specify the name of the function to execute. **Choose "
            "from the provided "
            "`tool_schemas`; do not invent function names.**"
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
            "`tool_schemas`; do not "
            "invent argument names.**"
        ),
        examples=[{"num1": 1, "num2": 2}, {"x": "hello", "y": "world"}],
    )

    @field_validator("arguments", mode="before")
    def validate_arguments(cls, value: Any) -> dict[str, Any]:
        return to_dict(
            value,
            fuzzy_parse=True,
            suppress=True,
            recursive=True,
        )

    @classmethod
    def create(cls, data: Any, /) -> list[ActionRequestModel]:

        if (
            hasattr(data, "function")
            and isinstance(data.function, str)
            and hasattr(data, "arguments")
        ):
            data = {"function": data.function, "arguments": data.arguments}

        _dicts = parse_action_request(data)
        if _dicts:
            return [cls.model_validate(i) for i in _dicts]

        return []


class ActionResponseModel(BaseModel):

    function: str
    arguments: dict[str, Any]
    output: Any

    @classmethod
    def create(cls, action_request_model: ActionRequestModel, output: Any):
        return cls(
            function=action_request_model.function,
            arguments=action_request_model.arguments,
            output=output,
        )
