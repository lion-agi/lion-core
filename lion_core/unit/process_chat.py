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
Module for processing chat interactions in the Lion framework.

This module provides the main function for handling chat processing,
including configuration, completion, action requests, and validation.
"""

from typing import Any, Literal, TYPE_CHECKING

from lionagi import iModel

from lion_core.abc import BaseProcessor
from lion_core.generic.progression import Progression


from lion_core.communication.action_request import ActionRequest
from lion_core.unit.process_config import process_chat_config
from lion_core.unit.process_completion import (
    process_chatcompletion,
    process_model_response,
)
from lion_core.unit.process_action_request import process_action_request
from lion_core.unit.process_validation import process_validation

if TYPE_CHECKING:
    from lion_core.session.branch import Branch

from lion_core.abc import Observable
from lion_core.form.base import BaseForm
from lion_core.form.form import Form
from lion_core.generic.note import note, Note
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.message import MessageFlag
from lion_core.communication.instruction import Instruction
from lion_core.unit.process_action_response import process_action_response


async def process_chat(
    branch: Branch,
    *,
    instruction=None,
    context=None,
    form: BaseForm = None,
    sender=None,
    recipient=None,
    request_fields: dict = None,
    system=None,
    guidance: str = None,
    strict_form: bool = False,
    output_fields: list[str] = None,
    action_request: ActionRequest | list[ActionRequest] = None,
    images: list = None,
    image_detail: Literal["low", "high", "auto"] = None,
    system_datetime: bool | str = None,
    metadata=None,
    delete_previous_system: bool = False,
    tools=None,
    system_metadata: dict | Note = None,
    model_config: dict = None,
    assignment: str = None,  # if use form, must provide assignment
    task_description: str = None,
    fill_inputs: bool = True,
    none_as_valid_value: bool = False,
    input_fields_value_kwargs: dict = None,
    same_form_output_fields: bool = None,
    clear_messages: bool = False,
    imodel: iModel = None,
    progress: Progression = None,
    costs=(0, 0),
    fill_value=None,
    fill_mapping: dict = None,
    response_parser=None,
    response_parser_kwargs=None,
    handle_unmatched="ignore",
    validator=None,
    rulebook=None,
    strict_validation=None,
    use_annotation=None,
    return_branch=None,
    **kwargs: Any,  # additional model parameters
):

    if clear_messages:
        branch.clear_messages()

    config = process_chat_config(
        branch=branch,
        instruction=instruction,
        context=context,
        form=form,
        sender=sender,
        recipient=recipient,
        request_fields=request_fields,
        system=system,
        guidance=guidance,
        strict_form=strict_form,
        output_fields=output_fields,
        action_request=action_request,
        images=images,
        image_detail=image_detail,
        system_datetime=system_datetime,
        metadata=metadata,
        delete_previous_system=delete_previous_system,
        tools=tools,
        system_metadata=system_metadata,
        model_config=model_config,
        assignment=assignment,
        task_description=task_description,
        fill_inputs=fill_inputs,
        none_as_valid_value=none_as_valid_value,
        input_fields_value_kwargs=input_fields_value_kwargs,
        same_form_output_fields=same_form_output_fields,
        **kwargs,
    )
    imodel = imodel or branch.imodel
    payload, completion = await imodel.chat(
        branch.to_chat_messages(progress=progress),
        **config,
    )

    message = await process_chatcompletion(
        branch=branch,
        imodel=imodel,
        payload=payload,
        completion=completion,
        sender=sender,
        costs=costs,
    )

    if message is None:
        return None

    response: dict | str = process_model_response(
        content_=message,
        request_fields=request_fields,
        fill_value=fill_value,
        fill_mapping=fill_mapping,
        strict=False,
        handle_unmatched=handle_unmatched,
    )

    action_requests, action_outputs = await process_action_request(
        branch=branch,
        response=response,
        action_request=action_request,
    )

    await process_action_response(
        branch=branch,
        action_requests=action_requests,
        responses=action_outputs,
        response_parser=response_parser,
        parser_kwargs=response_parser_kwargs,
    )

    if form:
        form = await process_validation(
            form=form,
            validator=validator,
            response_=response,
            rulebook=rulebook,
            strict=strict_validation,
            use_annotation=use_annotation,
        )
        return branch, form if return_branch else form.work_fields

    return branch, response if return_branch else response


__all__ = ["process_chat"]

# File: lion_core/chat/processing.py
