"""Mail module for the Lion framework's communication system."""

from typing import Any
from pydantic import Field
from .base import BaseMail
from .package import PackageCategory, Package


class Mail(BaseMail):
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
