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
from collections.abc import Mapping, Sequence
from functools import singledispatch
from typing import Any, Callable

from lion_core.abc import Observable
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse
from lion_core.communication.assistant_response import AssistantResponse
from lion_core.communication.instruction import Instruction
from lion_core.communication.message import RoledMessage
from lion_core.communication.system import System
from lion_core.generic.pile import Pile
from lion_core.libs import to_dict, strip_lower, nget, to_list
from lion_core.setting import LionUndefined, LN_UNDEFINED
from lion_core.sys_utils import SysUtil

"""
messages:
1. a single message object, or a single dict that can be converted to a message object
2. a sequence of message objects, or a sequence of dicts that can be converted to message objects
3. a pile of message objects
"""

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


@singledispatch
def validate_message(messages: Any) -> list[RoledMessage] | RoledMessage:
    raise NotImplementedError(f"Invalid messages type: {type(messages)}")


@to_dict.register(LionUndefined)
@to_dict.register(type(None))
def _(messages):
    return []


@validate_message.register(RoledMessage)
def _(messages):
    return messages


@validate_message.register(dict)
def _(messages):
    try:
        return RoledMessage.from_dict(messages)
    except Exception as e:
        raise ValueError(f"Error in creating message object: {e}")


@validate_message.register(str)
def _(messages):
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
        raise ValueError(f"Error in converting string to dict: {e1}, {e}")


@validate_message.register(Mapping)
def _(messages):
    try:
        _d = to_dict(messages)
        return validate_message(_d)
    except Exception as e:
        raise e


@validate_message.register(Sequence)
def _(messages):
    try:
        _lst_d = to_dict(messages)
        if not isinstance(_lst_d, list):
            messages = [messages]
        return to_list([validate_message(d) for d in _lst_d if d], faltten_=True)
    except Exception as e:
        raise e


@validate_message.register(Pile)
def _(messages):
    if messages.is_empty():
        return []
    return to_list([validate_message(d) for d in messages.values() if d], flatten_=True)


def validate_system(
    system: Any = None, sender=None, recipient=None, system_datetime=None
) -> None:

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


def _handle_action(
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
                "Error: please provide an corresponding action request for an action response."
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


def create_message(
    *,
    sender: Observable | str | None = None,
    recipient: Observable | str | None = None,
    # message parameters
    instruction: Instruction | Any = None,
    context: Any = None,
    system: System | Any = None,
    assistant_response: AssistantResponse | str | dict | None = None,
    action_request: ActionRequest | None = None,
    action_response: ActionResponse | None = None,
    # additional parameters
    images=None,
    requested_fields=None,
    image_detail=None,
    func=None,
    arguments=None,
    func_output=None,
    system_datetime=None,
):

    if (
        a := _handle_action(
            sender=sender,
            recipient=recipient,
            action_request=action_request,
            action_response=action_response,
            func=func,
            arguments=arguments,
            func_output=func_output,
        )
    ) is not None:
        return a

    a = {
        "system": system,
        "instruction": instruction,
        "assistant_response": assistant_response,
    }

    a = {k: v for k, v in a.items() if v is not None}

    if not len(a) == 1:
        raise ValueError("Error: Message can only have one role")

    if not func_output:
        for _, v in a.items():
            if isinstance(v, RoledMessage):
                if isinstance(v, Instruction):
                    if context:
                        v.add_context(context)
                    if requested_fields:
                        v._update_requested_fields(requested_fields)
                return v

    if system:
        return System(
            system=system,
            sender=sender,
            recipient=recipient,
            system_datetime=system_datetime,
            system_datetime_strftime=system_datetime_strftime,
        )

    elif assistant_response:
        return AssistantResponse(
            assistant_response=assistant_response,
            sender=sender,
            recipient=recipient,
        )

    else:
        if image:
            image = image if isinstance(image, list) else [image]

        return Instruction(
            instruction=instruction,
            context=context,
            sender=sender,
            recipient=recipient,
            request_fields=requested_fields,
            images=image,
            **kwargs,
        )


def parse_action_request(response: dict | str) -> list[ActionRequest] | None:
    """Parses an action request from the response."""
    message = to_dict(response) if not isinstance(response, dict) else response
    content_ = None

    if strip_lower(nget(message, ["content"])) == "none":
        content_ = _handle_action_request(message)

    elif nget(message, ["content", "tool_uses"], None):
        content_ = message["content"]["tool_uses"]

    else:
        json_block_pattern = re.compile(r"```json\n({.*?tool_uses.*?})\n```", re.DOTALL)

        # Find the JSON block in the text
        match = json_block_pattern.search(str(message["content"]))
        if match:
            json_block = match.group(1)
            parsed_json = json.loads(json_block)
            if "tool_uses" in parsed_json:
                content_ = parsed_json["tool_uses"]
            elif "actions" in parsed_json:
                content_ = parsed_json["actions"]
            else:
                content_ = []

    if isinstance(content_, dict):
        content_ = [content_]

    if isinstance(content_, list) and not content_ == []:
        outs = []
        for func_calling in content_:
            if "recipient_name" in func_calling:
                func_calling["action"] = func_calling["recipient_name"].split(".")[1]
                func_calling["arguments"] = func_calling["parameters"]
            elif "function" in func_calling:
                func_calling["action"] = func_calling["function"]
                if "parameters" in func_calling:
                    func_calling["arguments"] = func_calling["parameters"]
                elif "arguments" in func_calling:
                    func_calling["arguments"] = func_calling["arguments"]

            msg = ActionRequest(
                function=func_calling["action"]
                .replace("action_", "")
                .replace("recipient_", ""),
                arguments=func_calling["arguments"],
            )
            outs.append(msg)
        return outs

    else:
        try:
            _content = to_dict(message["content"])
            if "action_request" in _content:
                content_ = _content["action_request"]

            if isinstance(content_, dict):
                content_ = [content_]

            if isinstance(content_, list):
                outs = []
                for func_calling in content_:
                    if "function" in func_calling:
                        func_calling["action"] = func_calling["function"]
                        if "parameters" in func_calling:
                            func_calling["arguments"] = func_calling["parameters"]
                        elif "arguments" in func_calling:
                            func_calling["arguments"] = func_calling["arguments"]
                    msg = ActionRequest(
                        function=func_calling["action"]
                        .replace("action_", "")
                        .replace("recipient_", ""),
                        arguments=func_calling["arguments"],
                    )
                    outs.append(msg)
                return outs
        except:
            return None
    return None


def _handle_action_request(response: dict) -> list[dict]:
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
            "Response message must be one of regular response or function calling"
        )


# File: lion_core/communication/util.py
