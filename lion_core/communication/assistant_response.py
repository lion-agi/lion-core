from typing import Any

from lionfuncs import to_dict, to_str
from pydantic import BaseModel
from typing_extensions import override

from lion_core.communication.message import (
    MessageFlag,
    MessageRole,
    RoledMessage,
)


class AssistantResponse(RoledMessage):
    """Represents a response from an assistant in the system."""

    @override
    def __init__(
        self,
        assistant_response: BaseModel | MessageFlag,
        sender: Any | MessageFlag,
        recipient: Any | MessageFlag,
        protected_init_params: dict | None = None,
    ) -> None:
        """Initialize an AssistantResponse instance.

        Args:
            assistant_response: The content of the assistant's response.
            sender: The sender of the response, typically the assistant.
            recipient: The recipient of the response.
            protected_init_params: Optional parameters for protected init.
        """
        message_flags = [assistant_response, sender, recipient]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",
            recipient=recipient,
        )

        if assistant_response:
            # must be response.choices[0].message.content
            if isinstance(assistant_response, BaseModel):
                self.content["assistant_response"] = (
                    assistant_response.choices[0].message.content or ""
                )
                self.metadata["model_response"] = to_dict(
                    assistant_response,
                    use_model_dump=True,
                    exclude_none=True,
                    exclude_unset=True,
                )
            # or response[i].choices[0].delta.content
            elif isinstance(assistant_response, list):
                msg = "".join(
                    [
                        i.choices[0].delta.content or ""
                        for i in assistant_response
                    ]
                )
                self.content["assistant_response"] = msg
                self.metadata["model_response"] = [
                    to_dict(
                        i,
                        use_model_dump=True,
                        exclude_none=True,
                        exclude_unset=True,
                    )
                    for i in assistant_response
                ]
            elif (
                isinstance(assistant_response, dict)
                and "content" in assistant_response
            ):
                self.content["assistant_response"] = assistant_response[
                    "content"
                ]
            elif isinstance(assistant_response, str):
                self.content["assistant_response"] = assistant_response
            else:
                self.content["assistant_response"] = to_str(assistant_response)
        else:
            self.content["assistant_response"] = ""

    @property
    def response(self) -> Any:
        """Return the assistant response content."""
        return self.content.get("assistant_response")

    @override
    def _format_content(self) -> dict[str, Any]:
        return {"role": self.role.value, "content": self.response}


# File: lion_core/communication/assistant_response.py
