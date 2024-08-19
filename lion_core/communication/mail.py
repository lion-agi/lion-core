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

from typing import Any
from typing_extensions import override
from pydantic import Field, field_validator
from lion_core.exceptions import LionValueError
from lion_core.communication.base_mail import BaseMail
from lion_core.communication.package import PackageCategory, Package


class Mail(BaseMail):
    """
    A mail component with sender, recipient, and package.

    The `Mail` class represents a communication component that includes the
    sender, recipient, and the package to be delivered. It extends the
    `BaseMail` class, adding a `package` field and methods for validating
    sender and recipient information.

    Attributes:
        sender (str): The ID of the sender node. Valid values include 'system',
            'user', or 'assistant'.
        recipient (str): The ID of the recipient node. Valid values include
            'system', 'user', or 'assistant'.
        package (Package): The package to be delivered, which includes the
            content and metadata.

    Properties:
        category (PackageCategory): The category of the package.

    Methods:
        _validate_sender_recipient(cls, value: Any) -> str: Validates the
            sender and recipient fields to ensure they are not 'N/A'.
    """

    sender: str = Field(
        ...,
        title="Sender",
        description="The ID of the sender node, or 'system', 'user', "
        "or 'assistant'.",
    )

    recipient: str = Field(
        ...,
        title="Recipient",
        description="The ID of the recipient node, or 'system', 'user', "
        "or 'assistant'.",
    )

    package: Package = Field(
        ...,
        title="Package",
        description="The package to be delivered.",
    )

    @property
    def category(self) -> PackageCategory:
        """
        Returns the category of the package.

        The `category` property extracts and returns the `PackageCategory`
        associated with the `package`.

        Returns:
            PackageCategory: The category of the package.
        """
        return self.package.category

    @override
    @field_validator("sender", "recipient", mode="before")
    @classmethod
    def _validate_sender_recipient(cls, value: Any) -> str:
        """
        Validates the sender and recipient fields.

        This method overrides the base validation to ensure that the sender
        and recipient are valid and not 'N/A'. It relies on the parent
        validation logic and adds an additional check.

        Args:
            value (Any): The value to validate, typically a string representing
            a node ID or a predefined value like 'system'.

        Returns:
            str: The validated sender or recipient value.

        Raises:
            LionValueError: If the value is 'N/A', indicating an invalid sender
            or recipient for `Mail`.
        """
        value = super()._validate_sender_recipient(value)
        if value == "N/A":
            raise LionValueError(f"Invalid sender or recipient for Mail")
        return value


# File: lion_core/communication/mail.py
