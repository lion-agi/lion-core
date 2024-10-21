from lion_core.communication import AssistantResponse


def create_assistant_response_message(
    sender,
    recipient,
    assistant_response,
) -> AssistantResponse:
    if isinstance(assistant_response, AssistantResponse):
        return assistant_response
    return AssistantResponse(
        assistant_response=assistant_response,
        sender=sender,
        recipient=recipient,
    )
