"""
Module for processing chat interactions in the Lion framework.

This module provides the main function for handling chat processing,
including configuration, completion, action requests, and validation.
"""

from typing import Any, Literal, TYPE_CHECKING

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
    images=None,
    image_path=None,
    image_detail: Literal["low", "high", "auto"] = None,
    system_datetime: bool | str | None = None,
    metadata: Any = None,
    delete_previous_system: bool = False,
    tools: bool | None = None,
    system_metadata: Any = None,
    model_config: dict | None = None,
    clear_messages: bool = False,
    fill_value: Any = None,
    fill_mapping: dict[str, Any] | None = None,
    validator: BaseProcessor | None = None,
    rulebook=None,
    strict_validation: bool = False,
    use_annotation: bool = True,
    return_branch: bool = False,
    **kwargs: Any,
) -> tuple["Branch", Any] | Any:
    """
    Process chat interaction.

    Args:
        branch: The branch to process the chat for.
        form: The form associated with the chat.
        sender: Sender of the message.
        recipient: Recipient of the message.
        instruction: Instruction for the chat.
        context: Additional context for the chat.
        request_fields: Fields requested in the response.
        system: System message configuration.
        action_request: Action request for the chat.
        imodel: The iModel to use for chat completion.
        images: Image data for the chat.
        image_path: Path to an image file.
        image_detail: Detail level for image processing.
        system_datetime: Datetime for the system message.
        metadata: Additional metadata for the instruction.
        delete_previous_system: Whether to delete the previous system message.
        tools: Whether to include tools in the configuration.
        system_metadata: Additional system metadata.
        model_config: Additional model configuration.
        clear_messages: Whether to clear existing messages.
        fill_value: Value to use for filling unmatched fields.
        fill_mapping: Mapping for filling unmatched fields.
        validator: The validator to use for form validation.
        rulebook: Optional rulebook for validation.
        strict_validation: Whether to use strict validation.
        use_annotation: Whether to use annotation for validation.
        return_branch: Whether to return the branch along with the result.
        **kwargs: Additional keyword arguments for the model.

    Returns:
        The processed result, optionally including the branch.
    """
    if clear_messages:
        branch.clear()

    config = process_chat_config(
        branch,
        form=form,
        sender=sender,
        recipient=recipient,
        instruction=instruction,
        context=context,
        request_fields=request_fields,
        system=system,
        action_request=action_request,
        images=images,
        image_path=image_path,
        image_detail=image_detail,
        system_datetime=system_datetime,
        metadata=metadata,
        delete_previous_system=delete_previous_system,
        tools=tools,
        system_metadata=system_metadata,
        model_config=model_config,
        **kwargs,
    )

    imodel = imodel or branch.imodel
    payload, completion = await imodel.chat(branch.to_chat_messages(), **config)
    costs = imodel.endpoints.get(["chat/completions", "model", "costs"], (0, 0))

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
