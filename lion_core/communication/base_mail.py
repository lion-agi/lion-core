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

from typing import Any

from pydantic import Field, field_validator

from lion_core.sys_utils import SysUtil
from lion_core.generic.element import Element
from lion_core.exceptions import LionIDError, LionValueError


def validate_sender_recipient(value: Any) -> str:
    """
    Validates the sender and recipient fields for mail-like communication in the LION system.

    This function ensures that the provided value for sender or recipient is valid.
    Valid values include predefined identifiers like 'system', 'user', 'assistant',
    'N/A', or a valid ID returned by `SysUtil.get_id`.

    Args:
        value (Any): The value to validate, which can be a string identifier or an object
                     that can be converted into an ID.

    Returns:
        str: The validated and standardized sender or recipient ID.

    Raises:
        LionValueError: If the value cannot be validated as a valid sender or recipient.
    """
    if value in ["system", "user", "N/A", "assistant"]:
        return value

    if value is None:
        return "N/A"

    try:
        return SysUtil.get_id(value)
    except LionIDError as e:
        raise LionValueError("Invalid sender or recipient") from e


class BaseMail(Element):
    """
    Base class for mail-like communication in the LION system.

    The `BaseMail` class serves as a foundation for creating mail-like messages
    within the LION system. It includes sender and recipient fields, which are
    validated to ensure they conform to expected formats.

    Attributes:
        sender (str): The ID of the sender node. Valid values include 'system',
                      'user', 'assistant', or a valid node ID.
        recipient (str): The ID of the recipient node. Valid values include 'system',
                         'user', 'assistant', or a valid node ID.
    """

    sender: str = Field(
        "N/A",
        title="Sender",
        description=(
            "The ID of the sender node, or 'system', 'user', " "or 'assistant'."
        ),
    )

    recipient: str = Field(
        "N/A",
        title="Recipient",
        description=(
            "The ID of the recipient node, or 'system', 'user', " "or 'assistant'."
        ),
    )

    @field_validator("sender", "recipient", mode="before")
    @classmethod
    def _validate_sender_recipient(cls, value: Any) -> str:
        """
        Validate the sender and recipient fields.

        This method ensures that the `sender` and `recipient` fields of a `BaseMail`
        instance are valid. It uses the `validate_sender_recipient` function to
        perform the validation.

        Args:
            value (Any): The value to validate for the sender or recipient.

        Returns:
            str: The validated sender or recipient ID.

        Raises:
            LionValueError: If the value cannot be validated as a valid sender or recipient.
        """
        return validate_sender_recipient(value)


# File: lion_core/communication/base.py
