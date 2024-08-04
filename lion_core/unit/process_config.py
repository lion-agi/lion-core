from typing import Any, Literal, TYPE_CHECKING

from lion_core.abc import Observable

from lion_core.task.base import BaseTask
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.message import MessageFlag
from lion_core.communication.instruction import Instruction
from lion_core.communication.action_request import ActionRequest


if TYPE_CHECKING:
    from lion_core.session.branch import Branch


def process_chat_config(
    branch: Branch,
    *,
    task: BaseTask = None,
    sender: Observable | str | None = None,
    recipient: Observable | str | None = None,
    instruction: Any = None,
    context: Any = None,
    request_fields: dict | MessageFlag = None,
    system: Any = None,
    action_request: ActionRequest | None = None,
    images: list | MessageFlag = None,
    image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
    system_datetime: bool | str | None | MessageFlag = None,
    metadata: Any = None,
    delete_previous_system: bool = False,
    tools: bool | None = None,
    system_metadata: Any = None,
    model_config: dict | None = None,
    **kwargs: Any,  # additional model parameters
):

    if system:
        branch.add_message(
            system=system,
            system_datetime=system_datetime,
            metadata=system_metadata,
            delete_previous_system=delete_previous_system,
        )

    if not task:
        branch.add_message(
            instruction=instruction,
            context=context,
            sender=sender,
            recipient=recipient,
            request_fields=request_fields,
            images=images,
            image_detail=image_detail,
            metadata=metadata,
            action_request=action_request,
        )
    else:
        branch.add_message(
            instruction=Instruction.from_form(task),
            context=context,
            sender=sender,
            recipient=recipient,
            images=images,
            image_detail=image_detail,
            metadata=metadata,
            action_request=action_request,
        )

    if "tool_parsed" in kwargs:
        kwargs.pop("tool_parsed")
        tool_kwarg = {"tools": tools}
        kwargs = tool_kwarg | kwargs
    elif tools and branch.has_tools:
        kwargs = branch.tool_manager.get_tool_schema(tools=tools, **kwargs)

    config = {**model_config, **kwargs}
    if sender is not None:
        config["sender"] = sender

    return config


__all__ = ["process_chat_config"]
