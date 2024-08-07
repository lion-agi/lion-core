"""
Module for processing action requests in the Lion framework.

This module provides functionality to handle action requests, including
parsing, validation, and execution of associated functions.
"""

import asyncio
from typing import Any, TYPE_CHECKING

from lion_core.exceptions import ItemNotFoundError
from lion_core.action.function_calling import FunctionCalling
from lion_core.communication.action_request import ActionRequest
from lion_core.session.utils import parse_action_request

if TYPE_CHECKING:
    from lion_core.session.branch import Branch


async def process_action_request(
    branch: "Branch",
    *,
    _msg: dict | None = None,
    action_request: list[ActionRequest] | dict | str | None = None,
) -> Any:
    """
    Process action requests for a given branch.

    Args:
        branch: The Branch object to process action requests for.
        _msg: Optional message dictionary to parse for action requests.
        action_request: Pre-parsed action requests or raw data to parse.

    Returns:
        The results of the action requests or False if no requests were found.

    Raises:
        ItemNotFoundError: If a requested tool is not found in the registry.
    """
    action_requests: list[ActionRequest] = action_request or parse_action_request(_msg)
    if not action_requests:
        return _msg or False

    tasks = []
    for request in action_requests:
        func_name = request.content.get(["action_request", "function"], "")
        if func_name in branch.tool_manager:
            tool = branch.tool_manager.registry[func_name]
            request.recipient = tool.ln_id
        else:
            raise ItemNotFoundError(f"Tool {func_name} not found in registry")
        branch.add_message(action_request=request, recipient=request.recipient)

        args = request.content["action_request", "arguments"]
        func_call = FunctionCalling(tool, args)
        tasks.append(asyncio.create_task(func_call.invoke()))

    results = await asyncio.gather(*tasks)

    for request, result in zip(action_requests, results):
        if result is not None:
            branch.add_message(
                action_request=request,
                func_outputs=result,
                sender=request.recipient,
                recipient=request.sender,
            )

    return results


__all__ = ["process_action_request"]

# File: lion_core/action/processing.py
