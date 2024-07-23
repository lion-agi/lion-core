"""Mail module for the Lion framework's communication system."""

from typing import Any
from pydantic import Field, field_validator
from lion_core.exceptions import LionTypeError, LionIDError
from lion_core.sys_util import SysUtil
from .base import BaseCommunication
from .package import PackageCategory, Package


class Mail(BaseCommunication):
    """a mail component with sender, recipient, and package."""

    package: Package = Field(
        ...,
        title="Package",
        description="The package to be delivered.",
    )

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
        """Validate the sender and recipient fields."""
        if value in ["system", "user", "N/A", "assistant"]:
            return value

        if value is None:
            return "N/A"

        try:
            return SysUtil.get_id(value)
        except LionIDError:
            raise LionTypeError(f"Invalid sender or recipient type: {type(value)}")

    @property
    def category(self) -> PackageCategory:
        """Return the category of the package."""
        return self.package.category

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Serialize the Mail object to a dictionary."""
        d = super().to_dict(**kwargs)
        d["package_id"] = self.package.ln_id
        d["package_category"] = self.package.category
        return d


# File: lion_core/communication/mail.py
