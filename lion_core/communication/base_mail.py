from typing import Any

from pydantic import Field, field_validator

from lion_core.sys_utils import SysUtil
from lion_core.generic.element import Element
from lion_core.exceptions import LionIDError, LionValueError


def validate_sender_recipient(value: Any) -> str:
    """Validate the sender and recipient fields."""
    if value in ["system", "user", "N/A", "assistant"]:
        return value

    if value is None:
        return "N/A"

    try:
        return SysUtil.get_id(value)
    except LionIDError as e:
        raise LionValueError("Invalid sender or recipient") from e


class BaseMail(Element):
    """Base class for mail-like communication in LION."""

    sender: str = Field(
        "N/A",
        title="Sender",
        description=(
            "The ID of the sender node, or 'system', 'user', "
            "or 'assistant'."
        ),
    )

    recipient: str = Field(
        "N/A",
        title="Recipient",
        description=(
            "The ID of the recipient node, or 'system', 'user', "
            "or 'assistant'."
        ),
    )

    @field_validator("sender", "recipient", mode="before")
    @classmethod
    def _validate_sender_recipient(cls, value: Any) -> str:
        """Validate the sender and recipient fields."""
        return validate_sender_recipient(value)


# File: lion_core/communication/base.py