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
from pydantic import Field

from lion_core.abc import Signal
from lion_core.generic.element import Element
from lion_core.generic.exchange import Exchange
from lion_core.communication.mail import Mail
from lion_core.communication.package import Package


class StartMail(Element, Signal):
    """a start mail node that triggers the initiation of a process."""

    mailbox: Exchange = Field(
        default_factory=Exchange, description="The pending start mail"
    )

    @override
    def trigger(
        self,
        context: Any,
        structure_id: str,
        executable_id: str,
    ) -> None:
        """
        Triggers the start mail by including it in the mailbox.

        Args:
            context: The context to be included in the start mail.
            structure_id: The ID of the structure to be initiated.
            executable_id: The ID of the executable to receive the start mail.
        """
        start_mail_content = {"context": context, "structure_id": structure_id}
        pack = Package(category="start", package=start_mail_content)
        start_mail = Mail(
            sender=self.ln_id,
            recipient=executable_id,
            package=pack,
        )
        self.mailbox.include(start_mail, "out")


# File: lion_core/communication/start_mail.py
