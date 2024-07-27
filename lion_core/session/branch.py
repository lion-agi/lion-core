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

from typing import Any, Callable

from pydantic import Field

from lion_core.abc import BaseiModel
from lion_core.libs import to_list

from lion_core.generic import (
    pile,
    Pile,
    progression,
    Progression,
    Exchange,
    to_list_type,
)

from lion_core.action import Tool, ToolManager

from lion_core.communication import (
    RoledMessage,
    System,
    Instruction,
    AssistantResponse,
    ActionRequest,
    ActionResponse,
    Mail,
)

from lion_core.session.utils import validate_message, validate_system, create_message

from lion_core.session.base import BaseSession
from lion_core.converter import Converter, ConverterRegistry


class BranchConverterRegistry(ConverterRegistry): ...


class Branch(BaseSession):

    messages: Pile | None = Field(None)
    tool_manager: ToolManager | None = Field(None)
    mailbox: Exchange | None = Field(None)
    progress: Progression | None = Field(None)

    def __init__(
        self,
        system: System = None,
        system_sender: Any = None,
        system_datetime: bool | str | None = None,
        messages: Pile = None,
        tools: Any = None,
        tool_manager: ToolManager = None,
        mail_box: Exchange = None,
        name: str = None,
        progress: Progression = None,
    ):
        super().__init__()

        system = validate_system(
            system,
            sender=system_sender,
            recipient=self.ln_id,
            system_datetime=system_datetime,
        )

        if messages:
            messages = pile(
                to_list(
                    validate_message(to_list_type(messages)), dropna=True, flatten=True
                ),
                RoledMessage,
            )

        self.system = system
        self.messages = messages or pile(self.system, RoledMessage)
        self.tool_manager = tool_manager or ToolManager()
        self.mailbox = mail_box or Exchange()
        self.name = name or "user"
        self.progress = progress or progression()

        if tools:
            self.tool_manager.register_tools(tools)

    def add_message(
        self,
        *,
        system: dict | str | System | None = None,
        instruction: dict | str | Instruction | None = None,
        context: dict | str | None = None,
        assistant_response: dict | str | AssistantResponse | None = None,
        function: str | Callable | None = None,
        argument: dict | None = None,
        func_output: Any = None,
        action_request: ActionRequest = None,
        action_response: Any = None,
        image: str | list[str] = None,
        sender: Any = None,
        recipient: Any = None,
        requested_fields: dict[str, str] | None = None,
        system_datetime: bool | str | None = None,
        system_datetime_strftime: str | None = None,
        metadata: Any = None,  # extra metadata
        delete_previous_system: bool = False,
        **kwargs,  # additional context fields
    ) -> bool:
        if assistant_response:
            sender = self.ln_id

        _msg = create_message(
            system=system,
            instruction=instruction,
            context=context,
            assistant_response=assistant_response,
            function=function,
            argument=argument,
            func_output=func_output,
            action_request=action_request,
            action_response=action_response,
            sender=sender,
            image=image,
            recipient=recipient,
            requested_fields=requested_fields,
            system_datetime=system_datetime,
            system_datetime_strftime=system_datetime_strftime,
            **kwargs,
        )

        if isinstance(_msg, System):
            _msg.recipient = self.ln_id  # the branch itself, system is to the branch
            self.change_system(_msg, delete_previous_system=delete_previous_system)

        if isinstance(_msg, Instruction):
            _msg.sender = sender or self.user
            _msg.recipient = recipient or self.ln_id

        if isinstance(_msg, AssistantResponse):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or "user"

        if isinstance(_msg, ActionRequest):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or "N/A"

        if isinstance(_msg, ActionResponse):
            _msg.sender = sender or "N/A"
            _msg.recipient = recipient or self.ln_id

        if metadata:
            _msg.metadata.insert(["extra"], metadata)

        return self.messages.include(_msg)

    def clear_messages(self):
        self.messages.clear()
        self.messages.include(self.system)

    def change_system(self, system: System, delete_previous_system: bool = False):
        old_system = self.system
        self.system = system
        self.messages[0] = self.system  # system must be in first message position

        if delete_previous_system:
            del old_system

    def send(
        self, recipient: str, category: str, package: Any, request_source: str
    ) -> None:
        mail = self.mail_manager.create_mail(
            sender=self.ln_id,
            recipient=recipient,
            category=category,
            package=package,
            request_source=request_source,
        )
        self.mailbox.include(mail, "out")

    def receive(
        self,
        sender: str,
        message: bool = False,
        tool: bool = False,
        imodel: bool = False,
    ) -> None:
        """
        Receives mail from a sender.

        Args:
            sender (str): The ID of the sender.
            message (bool, optional): Whether to process message mails. Defaults to True.
            tool (bool, optional): Whether to process tool mails. Defaults to True.
            imodel (bool, optional): Whether to process imodel mails. Defaults to True.

        Raises:
            ValueError: If the sender does not exist or the mail category is invalid.
        """
        skipped_requests = progression()
        if sender not in self.mailbox.pending_ins.keys():
            raise ValueError(f"No package from {sender}")
        while self.mailbox.pending_ins[sender].size() > 0:
            mail_id = self.mailbox.pending_ins[sender].popleft()
            mail: Mail = self.mailbox.pile[mail_id]

            if mail.category == "message" and message:
                if not isinstance(mail.package.package, RoledMessage):
                    raise ValueError("Invalid message format")
                new_message = mail.package.package.clone()
                new_message.sender = mail.sender
                new_message.recipient = self.ln_id
                self.messages.include(new_message)
                self.mailbox.pile.pop(mail_id)

            elif mail.category == "tool" and tool:
                if not isinstance(mail.package.package, Tool):
                    raise ValueError("Invalid tools format")
                self.tool_manager.register_tools(mail.package.package)
                self.mailbox.pile.pop(mail_id)

            elif mail.category == "imodel" and imodel:
                if not isinstance(mail.package.package, BaseiModel):
                    raise ValueError("Invalid iModel format")
                self.imodel = mail.package.package
                self.mailbox.pile.pop(mail_id)

            else:
                skipped_requests.append(mail)

        self.mailbox.pending_ins[sender] = skipped_requests

        if self.mailbox.pending_ins[sender].size() == 0:
            self.mailbox.pending_ins.pop(sender)

    def receive_all(self) -> None:
        """
        Receives mail from all senders.
        """
        for key in list(self.mailbox.pending_ins.keys()):
            self.receive(key)
