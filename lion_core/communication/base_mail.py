from typing import Any

from lionabc import Communicatable
from lionabc.exceptions import LionIDError, LionValueError
from pydantic import Field, field_validator

from lion_core.generic import Element
from lion_core.sys_utils import SysUtil


def validate_sender_recipient(value: Any, /) -> str:
    """
    Validate the sender and recipient fields for mail-like communication.

    Args:
        value (Any): The value to validate.

    Returns:
        str: The validated sender or recipient value.

    Raises:
        LionValueError: If the value is not a valid sender or recipient.
    """
    if value in ["system", "user", "N/A", "assistant"]:
        return value

    if value is None:
        return "N/A"

    try:
        return SysUtil.get_id(value)
    except LionIDError as e:
        raise LionValueError("Invalid sender or recipient") from e


class BaseMail(Element, Communicatable):
    """
    Base class for mail-like communication in the LION system.

    Attributes:
        sender (str): The ID of the sender node.
        recipient (str): The ID of the recipient node.
    """

    sender: str = Field(
        default="N/A",
        title="Sender",
        description="The ID of the sender node or a role.",
    )

    recipient: str = Field(
        default="N/A",
        title="Recipient",
        description="The ID of the recipient node, or a role",
    )

    @field_validator("sender", "recipient", mode="before")
    @classmethod
    def _validate_sender_recipient(cls, value: Any) -> str:
        return validate_sender_recipient(value)


# File: lion_core/communication/base.py
