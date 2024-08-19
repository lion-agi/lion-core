"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Callable
from typing_extensions import override

from lion_core.libs import to_dict, to_str, fuzzy_parse_json
from lion_core.generic.note import Note
from lion_core.communication.message import (
    RoledMessage,
    MessageRole,
    MessageFlag,
)


def prepare_action_request(
    func: str | Callable,
    arguments: dict,
) -> Note:
    """
    Prepare an action request by formatting the function and arguments into a structured note.

    Args:
        func (str | Callable): The function name or a callable that represents the action to be performed.
        arguments (dict): The arguments to be passed to the function. This can be a dictionary or a
                          serialized string (JSON/XML).

    Returns:
        Note: A Note object containing the formatted action request.

    Raises:
        ValueError: If the arguments cannot be converted to a dictionary or are otherwise invalid.
    """

    def _prepare_arguments(_arg: Any) -> dict[str, Any]:
        """
        Prepare and validate the arguments for an action request.

        Args:
            _arg (Any): The arguments to be prepared. Can be in dict, JSON, or XML format.

        Returns:
            dict[str, Any]: The prepared and validated arguments as a dictionary.

        Raises:
            ValueError: If the arguments are not valid or cannot be parsed.
        """
        if _arg is None:
            return {}
        if not isinstance(_arg, dict):
            try:
                _arg = to_dict(
                    to_str(_arg),
                    str_type="json",
                    parser=fuzzy_parse_json,
                )
            except ValueError:
                _arg = to_dict(to_str(_arg), str_type="xml")
            except Exception as e:
                raise ValueError(f"Invalid arguments: {e}") from e

        if isinstance(_arg, dict):
            return _arg
        raise ValueError(f"Invalid arguments: {_arg}")

    arguments = _prepare_arguments(arguments)
    return Note(
        **{"action_request": {"function": func, "arguments": arguments}},
    )


class ActionRequest(RoledMessage):
    """
    Represents a request for an action in the system.

    The `ActionRequest` class is used to encapsulate a request for performing
    an action. It includes the function to be called, the arguments for that function,
    and the sender/recipient of the request.

    Attributes:
        func (str | Callable | MessageFlag): The function to be invoked, either as a string,
                                             callable, or a MessageFlag.
        arguments (dict | MessageFlag): The arguments for the function, either as a dictionary
                                        or a MessageFlag.
        sender (Any | MessageFlag): The sender of the action request.
        recipient (Any | MessageFlag): The recipient of the action request.
        protected_init_params (dict | None): Optional parameters for protected initialization.
    """

    @override
    def __init__(
        self,
        func: str | Callable | MessageFlag,
        arguments: dict | MessageFlag,
        sender: Any | MessageFlag,
        recipient: Any | MessageFlag,
        protected_init_params: dict | None = None,
    ):
        """
        Initializes an ActionRequest instance.

        Args:
            func (str | Callable | MessageFlag): The function to be invoked.
            arguments (dict | MessageFlag): The arguments for the function.
            sender (Any | MessageFlag): The sender of the request.
            recipient (Any | MessageFlag): The recipient of the request.
            protected_init_params (dict | None, optional): Optional parameters for
                                                           protected initialization.
        """
        message_flags = [func, arguments, sender, recipient]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        func = func.__name__ if callable(func) else func

        super().__init__(
            role=MessageRole.ASSISTANT,
            content=prepare_action_request(func, arguments),
            sender=sender,
            recipient=recipient,
        )

    @property
    def is_responded(self) -> bool:
        """
        Check if the action request has been responded to.

        Returns:
            bool: True if the action request has been responded to, otherwise False.
        """
        return self.action_response_id is not None

    @property
    def request_dict(self) -> dict[str, Any]:
        """
        Get the action request content as a dictionary.

        Returns:
            dict[str, Any]: The action request content.
        """
        return self.content.get("action_request", {})

    @property
    def action_response_id(self) -> str | None:
        """
        Get the ID of the corresponding action response, if any.

        Returns:
            str | None: The ID of the action response, or None if not responded.
        """
        return self.content.get("action_response_id", None)


# File: lion_core/communication/action_request.py
