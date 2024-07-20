"""Package module for the Lion framework's communication system."""

from enum import Enum
from typing import Any

from lion_core.abc import Observable, Temporal
from lion_core.sys_util import SysUtil


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


def validate_category(value: Any) -> PackageCategory:
    """
    Validate the category field.

    This method ensures that the category field contains a valid
    PackageCategory value.

    Args:
        value: The value to validate.

    Returns:
        The validated PackageCategory value.

    Raises:
        ValueError: If the value is None or not a valid PackageCategory.
    """
    if value is None:
        raise ValueError("Package category cannot be None.")
    if isinstance(value, PackageCategory):
        return value
    try:
        return PackageCategory(value)
    except ValueError as e:
        raise ValueError("Invalid value for category.") from e


class Package(Observable, Temporal):
    """
    Represents a package in the Lion framework's communication system.

    This class provides functionality for categorizing and packaging data
    for communication between components.

    Attributes:
        request_source: The source of the request.
        category: The category of the package.
        package: The content of the package to be delivered.
    """

    def __init__(
        self,
        category: PackageCategory | str,
        package: Any,
        request_source: Any,
    ):
        """
        Initialize a Package instance.

        Args:
            category: The category of the package.
            package: The content of the package to be delivered.
            request_source: The source of the request.

        Raises:
            ValueError: If the category is invalid or None.
        """
        self.ln_id = SysUtil.id()
        self.timestamp = SysUtil.time(type_="timestamp")
        self.request_source = request_source
        self.category = validate_category(category)
        self.package = package

    __slots__ = ("ln_id", "timestamp", "request_source", "category", "package")


# File: lion_core/communication/package.py
