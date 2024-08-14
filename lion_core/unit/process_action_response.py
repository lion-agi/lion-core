from typing import Callable
from lion_core.libs import lcall
from lion_core.communication.action_request import ActionRequest
from lion_core.session.branch import Branch


async def process_action_response(
    branch: Branch,
    action_requests: list[ActionRequest],
    responses: list,
    response_parser: Callable = None,
    parser_kwargs: dict = None,
) -> list:
    responses = [responses] if not isinstance(responses, list) else responses

    results = []
    if response_parser:
        results = await lcall(
            response_parser,
            responses,
            **(parser_kwargs or {}),
        )

    results = results or responses

    for request, result in zip(action_requests, results):
        if result is not None:
            branch.add_message(
                action_request=request,
                func_outputs=result,
                sender=request.recipient,
                recipient=request.sender,
            )
