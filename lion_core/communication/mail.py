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

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Mail instance to a dictionary.

        This method first calls the Element class's to_dict method and
        then updates the resulting dictionary with package-specific
        information.

        Returns:
            A dictionary representation of the Mail instance.
        """
        result = self.model_dump()
        result.update(
            {
                "package_category": self.package.category,
                "package_id": self.package.ln_id,
            }
        )
        return result


# File: lion_core/communication/mail.py
