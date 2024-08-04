"""
Module for processing chat configuration in the Lion framework.

This module provides functionality to configure chat settings for a Branch object,
including handling of system messages, instructions, and model configurations.
"""

from typing import Any, Literal, TYPE_CHECKING

from lion_core.abc import Observable
from lion_core.task.base import BaseTask
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.message import MessageFlag
from lion_core.communication.instruction import Instruction

if TYPE_CHECKING:
    from lion_core.session.branch import Branch


def process_chat_config(
    branch: "Branch",
    *,
    task: BaseTask | None = None,
    sender: Observable | str | None = None,
    recipient: Observable | str | None = None,
    instruction: Any = None,
    context: Any = None,
    request_fields: dict | MessageFlag | None = None,
    system: Any = None,
    action_request: ActionRequest | None = None,
    images: list | MessageFlag | None = None,
    image_detail: Literal["low", "high", "auto"] | MessageFlag | None = None,
    system_datetime: bool | str | MessageFlag | None = None,
    metadata: Any = None,
    delete_previous_system: bool = False,
    tools: bool | None = None,
    system_metadata: Any = None,
    model_config: dict | None = None,
    **kwargs: Any,  # additional model parameters
) -> dict:
    """
    Process chat configuration for a Branch object.

    This function handles the configuration of various chat-related settings,
    including system messages, instructions, and model parameters.

    Args:
        branch: The Branch object to configure.
        task: An optional BaseTask object.
        sender: The sender of the message.
        recipient: The recipient of the message.
        instruction: The instruction for the chat.
        context: Additional context for the chat.
        request_fields: Fields to request in the response.
        system: System message configuration.
        action_request: An optional ActionRequest object.
        images: List of images or MessageFlag.
        image_detail: Detail level for images.
        system_datetime: Datetime for the system message.
        metadata: Additional metadata.
        delete_previous_system: Whether to delete the previous system message.
        tools: Boolean flag for tools configuration.
        system_metadata: Metadata for the system message.
        model_config: Additional model configuration.
        **kwargs: Additional keyword arguments for model parameters.

    Returns:
        A dictionary containing the processed chat configuration.
    """
    if system:
        branch.add_message(
            system=system,
            system_datetime=system_datetime,
            metadata=system_metadata,
            delete_previous_system=delete_previous_system,
        )

    message_kwargs = {
        "context": context,
        "sender": sender,
        "recipient": recipient,
        "images": images,
        "image_detail": image_detail,
        "metadata": metadata,
        "action_request": action_request,
    }

    if task:
        message_kwargs["instruction"] = Instruction.from_form(task)
    else:
        message_kwargs["instruction"] = instruction
        message_kwargs["request_fields"] = request_fields

    branch.add_message(**message_kwargs)

    config = model_config or {}
    config.update(kwargs)

    if "tool_parsed" in config:
        config.pop("tool_parsed")
        config["tools"] = tools
    elif tools and branch.has_tools:
        config.update(branch.tool_manager.get_tool_schema(tools=tools))

    if sender is not None:
        config["sender"] = sender

    return config


__all__ = ["process_chat_config"]

# File: lion_core/chat/process_config.py
