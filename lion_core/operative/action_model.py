from __future__ import annotations

from typing import Any

from lionfuncs import to_dict
from pydantic import BaseModel, Field, field_validator

from lion_core.action import FunctionCalling
from lion_core.communication import ActionRequest, ActionResponse

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
    def parse_to_model(
        cls,
        action_request_message: ActionRequest = None,
        text: str | None = None,
        function: str | None = None,
        arguments: dict[str, Any] = {},
    ) -> list[ActionRequestModel]:
        if action_request_message and isinstance(
            action_request_message, ActionRequest
        ):
            return [
                cls(
                    function=action_request_message.function,
                    arguments=action_request_message.arguments,
                )
            ]
        if function and arguments:
            return [cls(function=function, arguments=arguments)]

        if text:
            _dicts = parse_action_request(text)
            _dicts = [i for i in _dicts if i]
            if _dicts:
                return [cls(**i) for i in _dicts]
        return []

    def to_message(self) -> ActionRequest:
        return ActionRequest(
            function=self.function,
            arguments=self.arguments,
        )


class ActionResponseModel(BaseModel):

    function: str
    arguments: dict[str, Any]
    output: Any

    @classmethod
    def parse_to_model(
        cls,
        action_request_message: ActionRequest,
        output: Any,
    ) -> ActionResponseModel:
        return cls(
            function=action_request_message.function,
            arguments=action_request_message.arguments,
            output=output,
        )

    def to_message(
        self,
        action_request_message: ActionRequest,
        func_call: FunctionCalling = None,
    ) -> ActionResponse:
        act_res = ActionResponse(
            action_request=action_request_message,
            sender=func_call.func_tool.ln_id if func_call else None,
            func_output=self.output,
        )
        if func_call:
            log = func_call.to_log()
            act_res.metadata["log"] = log.to_dict()
        return act_res
