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

from typing import Any, TYPE_CHECKING

from lion_core.abc import BaseProcessor
from lion_core.communication.action_request import ActionRequest
from lion_core.unit.process_config import process_chat_config
from lion_core.unit.process_completion import (
    parse_chatcompletion,
    parse_model_response,
)
from lion_core.unit.process_action_request import process_action_request
from lion_core.unit.process_validation import process_validation

if TYPE_CHECKING:
    from lion_core.session.branch import Branch


async def process_chat(
    branch: "Branch",
    *,
    form=None,
    sender=None,
    recipient=None,
    instruction: Any = None,
    context: Any = None,
    request_fields=None,
    system: Any = None,
    action_request: ActionRequest | None = None,
    imodel=None,
    tools: bool | None = None,
    clear_messages: bool = False,
    fill_value: Any = None,
    fill_mapping: dict[str, Any] | None = None,
    validator: BaseProcessor | None = None,
    rulebook=None,
    strict_validation: bool = False,
    use_annotation: bool = True,
    return_branch: bool = False,
    costs=(0, 0),
    **kwargs: Any,
) -> tuple["Branch", Any] | Any:

    if clear_messages:
        branch.clear()

    config = process_chat_config(
        branch=branch,
        form=form,
        sender=sender,
        recipient=recipient,
        instruction=instruction,
        context=context,
        request_fields=request_fields,
        system=system,
        action_request=action_request,
        tools=tools,
        **kwargs,
    )

    imodel = imodel or branch.imodel
    payload, completion = await imodel.chat(branch.to_chat_messages(), **config)

    _msg = await parse_chatcompletion(
        branch=branch,
        imodel=imodel,
        payload=payload,
        completion=completion,
        sender=sender,
        costs=costs,
    )

    if _msg is None:
        return None

    _res = parse_model_response(
        content_=_msg,
        request_fields=request_fields,
        fill_value=fill_value,
        fill_mapping=fill_mapping,
        strict=False,
    )

    await process_action_request(
        branch=branch,
        _msg=_res,
        action_request=action_request,
    )

    if form:
        form = await process_validation(
            form=form,
            validator=validator,
            response_=_res,
            rulebook=rulebook,
            strict=strict_validation,
            use_annotation=use_annotation,
        )
        return (branch, form) if return_branch else form.work_fields

    return (branch, _res) if return_branch else _res


__all__ = ["process_chat"]

# File: lion_core/chat/processing.py
