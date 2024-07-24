"""Mail module for the Lion framework's communication system."""

from pydantic import Field
from lion_core.communication.base import BaseMail
from lion_core.communication.package import PackageCategory, Package


class Mail(BaseMail):
    """a mail component with sender, recipient, and package."""

    package: Package = Field(
        ...,
        title="Package",
        description="The package to be delivered.",
    )

    @property
    def category(self) -> PackageCategory:
        """Return the category of the package."""
        return self.package.category


# File: lion_core/communication/mail.py
