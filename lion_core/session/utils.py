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

import json
import re
from collections.abc import Mapping
from functools import singledispatch
from typing import Any, Callable, Literal

from lion_core.abc import Observable
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse
from lion_core.communication.assistant_response import AssistantResponse
from lion_core.communication.instruction import Instruction
from lion_core.communication.message import RoledMessage, MessageFlag
from lion_core.communication.system import System
from lion_core.generic.pile import Pile
from lion_core.generic.note import Note
from lion_core.libs import to_dict, strip_lower, nget, to_list
from lion_core.setting import LionUndefined, LN_UNDEFINED

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


@singledispatch
def validate_message(messages: Any) -> list[RoledMessage] | RoledMessage:
    """
    Validate and convert input messages to RoledMessage objects.

    Args:
        messages: Input messages of various types.

    Returns:
        A single RoledMessage or a list of RoledMessages.

    Raises:
        NotImplementedError: If the input type is not supported.
    """
    raise NotImplementedError(f"Invalid messages type: {type(messages)}")


@to_dict.register(LionUndefined)
@to_dict.register(type(None))
def _(messages):
    """Handle None or LionUndefined inputs."""
    return []


@validate_message.register(RoledMessage)
def _(messages, strict=False):
    """Handle RoledMessage inputs."""
    return [messages]


@validate_message.register(dict)
def _(messages, strict=False):
    """Handle dictionary inputs."""
    try:
        return [RoledMessage.from_dict(messages)]
    except Exception as e:
        if strict:
            raise ValueError(f"Error in creating message object: {e}")
        else:
            return []


@validate_message.register(str)
def _(messages, strict=False):
    """Handle string inputs."""
    e1 = None
    try:
        try:
            _d = to_dict(messages, str_type="json")
            return validate_message(_d)
        except ValueError as e:
            e1 = e
            _d = to_dict(messages, str_type="xml")
            return validate_message(_d)
    except ValueError as e:
        if strict:
            raise ValueError(f"Error in converting string to dict: {e1}, {e}")
        else:
            return []


@validate_message.register(Mapping)
def _(messages, strict=False):
    """Handle mapping inputs."""
    try:
        _d = to_dict(messages)
        return validate_message(_d)
    except Exception as e:
        if strict:
            raise e
        else:
            return []


@validate_message.register(list)
def _(messages, strict=False):
    try:
        return to_list([validate_message(d) for d in messages], faltten_=True)
    except Exception as e:
        if strict:
            raise e
        return []


@validate_message.register(Pile)
def _(messages: Pile, strict=False):
    if messages.is_empty():
        return []
    return validate_message(list(messages), strict=strict)


def validate_system(
    system: Any = None, sender=None, recipient=None, system_datetime=None
) -> System:
    """
    Validate and create a System message.

    Args:
        system: The system message content.
        sender: The sender of the system message.
        recipient: The recipient of the system message.
        system_datetime: The datetime for the system message.

    Returns:
        A validated System message.
    """

    config = {
        "sender": sender,
        "recipient": recipient,
        "system_datetime": system_datetime,
    }
    config = {k: v for k, v in config.items() if v not in [None, LN_UNDEFINED]}

    if not system:
        return System(DEFAULT_SYSTEM, **config)
    if isinstance(system, System):
        if config:
            for k, v in config.items():
                setattr(system, k, v)
        return system
    return System(system, **config)


def create_message(
    sender: Observable | str | None = None,
    recipient: Observable | str | None = None,
    instruction: Any = None,
    context: Any = None,
    request_fields: dict | MessageFlag = None,
    system: Any = None,
    assistant_response: Any = None,
    action_request: ActionRequest | None = None,
    action_response: ActionResponse | None = None,
    images: list | MessageFlag = None,
    image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
    system_datetime: bool | str | None | MessageFlag = None,
    func: str | Callable | MessageFlag = None,
    arguments: dict | MessageFlag = None,
    func_output: Any | MessageFlag = None,
):
    """
    Create a message based on the provided parameters.

    This function creates different types of messages (System, Instruction,
    AssistantResponse, ActionRequest, ActionResponse) based on the input.

    Args:
        sender: The sender of the message.
        recipient: The recipient of the message.
        instruction: The instruction content.
        context: Additional context for the message.
        request_fields: Fields requested in the response.
        system: System message content.
        assistant_response: Assistant's response content.
        action_request: An ActionRequest object.
        action_response: An ActionResponse object.
        images: List of images related to the message.
        image_detail: Level of detail for image processing.
        system_datetime: Datetime for system messages.
        func: Function name or callable for action requests.
        arguments: Arguments for action requests.
        func_output: Function output for action responses.

    Returns:
        A message object of the appropriate type.

    Raises:
        ValueError: If the input parameters are invalid or inconsistent.
    """

    out_ = _handle_action_message(
        sender=sender,
        recipient=recipient,
        action_request=action_request,
        action_response=action_response,
        func=func,
        arguments=arguments,
        func_output=func_output,
    )

    if out_ is not None:
        return out_

    a = {
        "system": system,
        "instruction": instruction,
        "assistant_response": assistant_response,
    }

    a = {k: v for k, v in a.items() if v is not None}

    if len(a) != 1:
        raise ValueError("Error: Message can only have one role")

    for _, v in a.items():
        if isinstance(v, RoledMessage):
            if isinstance(v, Instruction):
                if context:
                    v.update_context(context)
                if request_fields:
                    v.update_request_fields(request_fields)
            return v

    if system:
        return System(
            system=system,
            sender=sender,
            recipient=recipient,
            system_datetime=system_datetime,
        )
    elif assistant_response:
        return AssistantResponse(
            assistant_response=assistant_response,
            sender=sender,
            recipient=recipient,
        )
    else:
        return Instruction(
            instruction=instruction,
            context=context,
            sender=sender,
            recipient=recipient,
            request_fields=request_fields,
            images=images,
            image_detail=image_detail,
        )


def parse_action_request(response: dict | str) -> list[ActionRequest] | None:
    """Parses an action request from the response."""
    message = to_dict(response) if not isinstance(response, dict) else response
    msg = Note(**message)
    content_ = None

    if strip_lower(msg.get(["content"], "")) == "none":
        content_ = _extract_action_request_content(message)
    elif msg.get(["content", "tool_uses"], None):
        content_ = msg["content", "tool_uses"]
    else:
        content_ = _extract_tool_use_json_block(str(msg.get(["content"], "")))

    if isinstance(content_, dict):
        content_ = [content_]

    if isinstance(content_, list) and content_:
        return _extract_action_request(content_)
    else:
        try:
            _content = to_dict(msg["content"])
            if "action_request" in _content:
                content_ = _content["action_request"]

            if isinstance(content_, dict):
                content_ = [content_]

            if isinstance(content_, list):
                return _extract_action_request(content_)
        except Exception:
            return None

    return None


def _handle_action_message(
    sender: Observable | str | None = None,
    recipient: Observable | str | None = None,
    action_request: ActionRequest | None = None,
    action_response: ActionResponse | None = None,
    func: str | Callable | None = None,
    arguments: dict | None = None,
    func_output: Any = None,
) -> ActionRequest | ActionResponse | None:
    if func_output or action_response:
        if not action_request or not isinstance(action_request, ActionRequest):
            raise ValueError(
                "Error: please provide a corresponding action request for an "
                "action response."
            )

        if isinstance(action_response, ActionResponse):
            action_response.update_request(
                action_request=action_request, func_output=func_output
            )
            return action_response

        return ActionResponse(
            action_request=action_request,
            sender=sender,
            func_outputs=func_output,
        )

    if action_request:
        if not isinstance(action_request, ActionRequest):
            raise ValueError(
                "Error: action request must be an instance of ActionRequest."
            )
        return action_request

    if func:
        if callable(func):
            func = func.__name__
        if not arguments:
            raise ValueError("Error: please provide arguments for the function.")
        return ActionRequest(
            function=func,
            arguments=arguments,
            sender=sender,
            recipient=recipient,
        )


def _extract_action_request_content(response: dict) -> list[dict]:
    """Handles the action request parsing from the response."""
    try:
        tool_count = 0
        func_list = []
        while tool_count < len(response["tool_calls"]):
            _path = ["tool_calls", tool_count, "type"]

            if nget(response, _path) == "function":
                _path1 = ["tool_calls", tool_count, "function", "name"]
                _path2 = ["tool_calls", tool_count, "function", "arguments"]

                func_content = {
                    "action": f"action_{nget(response, _path1)}",
                    "arguments": nget(response, _path2),
                }
                func_list.append(func_content)
            tool_count += 1
        return func_list
    except:
        raise ValueError(
            "Response message must be one of regular response or function " "calling"
        )


def _extract_tool_use_json_block(_s: str) -> list | None:
    content_ = None
    json_block_pattern = re.compile(r"```json\n({.*?tool_uses.*?})\n```", re.DOTALL)

    match = json_block_pattern.search(_s)
    if match:
        json_block = match.group(1)
        parsed_json = json.loads(json_block)
        if "tool_uses" in parsed_json:
            content_ = parsed_json["tool_uses"]
        elif "actions" in parsed_json:
            content_ = parsed_json["actions"]
        else:
            content_ = []

    return content_


def _extract_action_request(content_: list[dict]) -> list[ActionRequest]:
    outs = []
    for request_ in content_:
        if "recipient_name" in request_:
            request_["action"] = request_.pop("recipient_name").split(".")[1]
        elif "function" in request_:
            request_["action"] = request_.pop("function")

        if "parameters" in request_:
            request_["arguments"] = request_["parameters"]
        elif "arguments" in request_:
            request_["arguments"] = request_["arguments"]

        f = lambda x: x.replace("action_", "").replace("recipient_", "")

        msg = ActionRequest(
            func=f(request_["action"]),
            arguments=request_["arguments"],
        )
        outs.append(msg)

    return outs


# File: lion_core/communication/util.py
