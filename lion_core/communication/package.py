"""Package module for the Lion framework's communication system."""

from enum import Enum
from typing import Any
from pydantic import field_validator, Field
from ..generic.component import Component
from ..exceptions import LionValueError


class PackageCategory(str, Enum):
    """Enumeration of package categories in the Lion framework."""

    MESSAGE = "message"
    TOOL = "tool"
    IMODEL = "imodel"
    NODE = "node"
    NODE_LIST = "node_list"
    NODE_ID = "node_id"
    START = "start"
    END = "end"
    CONDITION = "condition"
    SIGNAL = "signal"


class Package(Component):
    """Represents a package in the Lion framework's communication system.

    This class extends the Component class and provides functionality for
    categorizing and packaging data for communication between components.

    Attributes:
        request_source (str | None): The source of the request.
        category (PackageCategory): The category of the package.
        package (Any): The content of the package to be delivered.
    """

    request_source: str | None = Field(
        None,
        title="Request Source",
        description="The source of the request.",
    )

    category: PackageCategory = Field(
        None,
        title="Category",
        description="The category of the package.",
    )

    package: Any = Field(
        None,
        title="Package",
        description="The package to be delivered.",
    )

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, value: Any) -> PackageCategory:
        """Validate the category field.

        This method ensures that the category field contains a valid
        PackageCategory value.

        Args:
            value: The value to validate.

        Returns:
            The validated PackageCategory value.

        Raises:
            LionValueError: If the value is None or not a valid
                PackageCategory.
        """
        if value is None:
            raise LionValueError("Package category cannot be None.")
        if isinstance(value, PackageCategory):
            return value
        try:
            return PackageCategory(value)
        except ValueError as e:
            raise LionValueError("Invalid value for category.") from e


# File: lion_core/communication/package.py
