from typing import Any

from lion_core.communication import AssistantResponse


def create_assistant_response(
    sender: Any = None,
    recipient: Any = None,
    assistant_response: AssistantResponse | Any = None,
) -> AssistantResponse:
    """Create or return an AssistantResponse.

    Args:
        sender: The sender of the response.
        recipient: The recipient of the response.
        assistant_response: Existing AssistantResponse or response content.

    Returns:
        AssistantResponse: New or existing AssistantResponse instance.
    """
    if isinstance(assistant_response, AssistantResponse):
        if sender:
            assistant_response.sender = sender
        if recipient:
            assistant_response.recipient = recipient
        return assistant_response

    return AssistantResponse(
        assistant_response=assistant_response,
        sender=sender,
        recipient=recipient,
    )
