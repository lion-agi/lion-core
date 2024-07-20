"""Base module for mail-like communication in the Lion framework."""

from typing import Any
from pydantic import Field, field_validator
from lion_core.exceptions import LionTypeError, LionIDError
from lion_core.sys_util import SysUtil
from lion_core.generic import Element


class BaseMail(Element):
    """
    Base class for mail-like communication in the Lion framework.

    This class extends the Element class and provides basic functionality
    for sender and recipient handling in a communication system.

    Attributes:
        sender: The ID of the sender node, or 'system', 'user', or 'assistant'.
        recipient: The ID of the recipient node, or 'system', 'user', or 'assistant'.
    """

    sender: str = Field(
        "N/A",
        title="Sender",
        description="The ID of the sender node, or 'system', 'user', or 'assistant'.",
    )

    recipient: str = Field(
        "N/A",
        title="Recipient",
        description="The ID of the recipient node, or 'system', 'user', or 'assistant'.",
    )

    @field_validator("sender", "recipient", mode="before")
    @classmethod
    def _validate_sender_recipient(cls, value: Any) -> str:
        """Validate the sender and recipient fields.

        This method ensures that the sender and recipient fields contain
        valid values, either predefined strings or valid Lion IDs.

        Args:
            value: The value to validate.

        Returns:
            The validated value.

        Raises:
            LionTypeError: If the value is invalid.
        """
        if value in ["system", "user", "N/A", "assistant"]:
            return value

        if value is None:
            return "N/A"

        try:
            return SysUtil.get_id(value)
        except LionIDError:
            raise LionTypeError(f"Invalid sender or recipient type: {type(value)}")


# File: lion_core/communication/base.py
