import asyncio
from typing import Any, TYPE_CHECKING

from lion_core.exceptions import ItemNotFoundError

from lion_core.action.function_calling import FunctionCalling
from lion_core.communication.action_request import ActionRequest
from lion_core.session.utils import parse_action_request

if TYPE_CHECKING:
    from lion_core.session.branch import Branch


async def process_action_request(
    branch: Branch,
    *,
    _msg: dict | None = None,
    action_request: list[ActionRequest] | dict | str | None = None,
) -> Any:

    action_request: list[ActionRequest] = action_request or parse_action_request(_msg)
    if not action_request:
        return _msg or False

    for i in action_request:
        if i.content.get(["action_request", "function"], "") in branch.tool_manager:
            i.recipient = branch.tool_manager.registry[
                i.content["action_request", "function"]
            ].ln_id

        else:
            raise ItemNotFoundError(
                f"Tool {i.content.get(["action_request", "function"], "N/A")} not "
                "found in registry"
            )
        branch.add_message(action_request=i, recipient=i.recipient)

    tasks = []
    for i in action_request:
        func_ = i.content["action_request", "function"]
        args_ = i.content["action_request", "arguments"]

        tool = branch.tool_manager.registry[func_]
        func_call = FunctionCalling(tool, args_)
        tasks.append(asyncio.create_task(func_call.invoke()))

    results = await asyncio.gather(*tasks)

    for idx, item in enumerate(results):
        if item is not None:
            branch.add_message(
                action_request=action_request[idx],
                func_outputs=item,
                sender=action_request[idx].recipient,
                recipient=action_request[idx].sender,
            )
