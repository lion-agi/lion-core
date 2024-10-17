from lion_core.communication.assistant_response import AssistantResponse


def create_assistant_response(
    sender,
    recipient,
    assistant_response,
):
    if isinstance(assistant_response, AssistantResponse):
        return assistant_response
    return AssistantResponse(
        assistant_response=assistant_response,
        sender=sender,
        recipient=recipient,
    )
