"""Mail module for the Lion framework's communication system."""

from typing import Any
from pydantic import Field, field_validator
from lion_core.exceptions import LionTypeError, LionIDError
from lion_core.sys_util import SysUtil
from .base import BaseCommunication
from .package import PackageCategory, Package


class Mail(BaseCommunication):
    """
    Represents a mail component with sender, recipient, and package information.

    This class extends the BaseMail class and adds functionality for
    handling packages within the mail system.

    Attributes:
        package: The package to be delivered.
    """

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

    @property
    def category(self) -> PackageCategory:
        """
        Return the category of the package.

        Returns:
            The category of the package.
        """
        return self.package.category

    def serialize(self, **kwargs: Any) -> dict[str, Any]:
        dict_ = super().serialize(**kwargs)
        dict_["package_id"] = self.package.ln_id
        dict_["package_category"] = self.package.category
        return dict_


# File: lion_core/communication/mail.py
