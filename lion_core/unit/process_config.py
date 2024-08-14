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

"""
Module for processing chat configuration in the Lion framework.

This module provides functionality to configure chat settings for a Branch object,
including handling of system messages, instructions, and model configurations.
"""

from typing import Any, Literal, TYPE_CHECKING

from lion_core.abc import Observable
from lion_core.form.base import BaseForm
from lion_core.form.form import Form
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.message import MessageFlag
from lion_core.communication.instruction import Instruction

if TYPE_CHECKING:
    from lion_core.session.branch import Branch


def process_chat_config(
    branch: "Branch",
    *,
    instruction: Any = None,
    context: Any = None,
    form: BaseForm | None = None,
    sender: Observable | str | None = None,
    recipient: Observable | str | None = None,
    request_fields: dict | MessageFlag | None = None,
    system: Any = None,
    guidance: Any = None,
    strict_form: bool = False,
    output_fields: dict | None = None,
    action_request: ActionRequest | None = None,
    images: list | MessageFlag | None = None,
    image_detail: Literal["low", "high", "auto"] | MessageFlag | None = None,
    system_datetime: bool | str | MessageFlag | None = None,
    metadata: Any = None,
    delete_previous_system: bool = False,
    tools: bool | None = None,
    system_metadata: Any = None,
    model_config: dict | None = None,
    assignment: str = None,  # if use form, must provide assignment
    task_description: str = None,
    fill_inputs: bool = True,
    none_as_valid_value: bool = False,
    input_fields_value_kwargs: dict = None,
    same_form_output_fields=None,
    **kwargs: Any,  # additional model parameters
) -> dict:

    message_kwargs = {
        "context": context,
        "sender": sender,
        "recipient": recipient,
        "images": images,
        "image_detail": image_detail,
        "metadata": metadata,
        "action_request": action_request,
        "guidance": guidance,
        "same_form_output_fields": same_form_output_fields,
    }

    if instruction:
        message_kwargs["instruction"] = instruction
        message_kwargs["request_fields"] = request_fields

    if not form:
        form = Form.from_form(
            form=form,
            guidance=guidance,
            assignment=assignment,
            strict=strict_form,
            task_description=task_description,
            fill_inputs=fill_inputs,
            none_as_valid_value=none_as_valid_value,
            output_fields=output_fields,
            input_value_kwargs=input_fields_value_kwargs,
        )

    if isinstance(form, Form):
        message_kwargs["instruction"] = Instruction.from_form(
            form=form,
            sender=sender,
            recipient=recipient,
            images=images,
            image_detail=image_detail,
            strict=strict_form,
            assignment=assignment,
            task_description=task_description,
            fill_inputs=fill_inputs,
        )

    if system:
        branch.add_message(
            system=system,
            system_datetime=system_datetime,
            metadata=system_metadata,
            delete_previous_system=delete_previous_system,
        )

    branch.add_message(**message_kwargs)

    config = model_config or {}
    config.update(kwargs)

    if "tool_parsed" in config:
        config.pop("tool_parsed")
        config["tools"] = tools
    elif tools and branch.has_tools:
        config.update(
            branch.tool_manager.get_tool_schema(tools=tools),
        )

    if sender is not None:
        config["sender"] = sender

    return config


__all__ = ["process_chat_config"]

# File: lion_core/chat/process_config.py
