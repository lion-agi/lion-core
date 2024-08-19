"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from enum import Enum
from typing import Any

from lion_core.abc import Observable, Temporal
from lion_core.sys_utils import SysUtil


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
    """Validate the category field."""
    if value is None:
        raise ValueError("Package category cannot be None.")
    if isinstance(value, PackageCategory):
        return value
    try:
        return PackageCategory(value)
    except ValueError as e:
        raise ValueError("Invalid value for category.") from e


class Package(Observable, Temporal):
    """a package in the Lion framework's communication system."""

    def __init__(
        self,
        category: PackageCategory | str,
        package: Any,
        request_source: Any = None,
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
