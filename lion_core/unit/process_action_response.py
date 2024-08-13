from typing import Callable
from lion_core.libs import ucall


async def process_action_response(
    branch,
    action_requests,
    responses: list,
    response_parser: Callable = None,
    parser_kwargs=None,
):
    responses = [responses] if not isinstance(responses, list) else responses

    results = []
    if response_parser:
        for i in result:
            res = await ucall(
                response_parser,
                i,
                **(parser_kwargs or {}),
            )
            results.append(res)

    for request, result in zip(action_requests, results):
        if result is not None:
            branch.add_message(
                action_request=request,
                func_outputs=result,
                sender=request.recipient,
                recipient=request.sender,
            )

    return results
