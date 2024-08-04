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

from __future__ import annotations

from typing import Any, Callable, ClassVar, override, Literal

from pydantic import Field

from lion_core.abc import BaseiModel, Observable
from lion_core.libs import is_same_dtype
from lion_core.converter import ConverterRegistry
from lion_core.generic.pile import pile, Pile
from lion_core.generic.progression import prog, Progression
from lion_core.generic.exchange import Exchange

from lion_core.imodel.imodel import iModel
from lion_core.action import Tool, ToolManager
from lion_core.communication.message import RoledMessage
from lion_core.communication.system import System
from lion_core.communication.instruction import Instruction
from lion_core.communication.assistant_response import AssistantResponse
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse
from lion_core.communication.message import RoledMessage, MessageFlag
from lion_core.communication.package import Package
from lion_core.communication.mail import Mail
from lion_core.session.base import BaseSession
from lion_core.session.utils import validate_message, create_message


class BranchConverterRegistry(ConverterRegistry):
    """Registry for Branch converters."""

    pass


class Branch(BaseSession):
    """
    Represents a branch in the conversation tree with tools and messages.

    This class manages a conversation branch, including messages, tools,
    and communication within the branch.
    """

    messages: Pile | None = Field(None)
    tool_manager: ToolManager | None = Field(None)
    mailbox: Exchange | None = Field(None)
    progress: Progression | None = Field(None)

    _converter_registry: ClassVar = BranchConverterRegistry

    def __init__(
        self,
        system: Any = None,
        system_sender: str | None = None,
        system_datetime: Any = None,
        name: str | None = None,
        user: str | None = None,
        imodel: iModel | None = None,
        messages: Pile | None = None,
        tool_manager: ToolManager | None = None,
        mailbox: Exchange | None = None,
        progress: Progression | None = None,
        tools: Any = None,
    ):
        """
        Initialize a Branch instance.

        Args:
            system: System message for the branch.
            system_sender: Sender of the system message.
            system_datetime: Datetime for the system message.
            name: Name of the branch.
            user: User identifier for the branch.
            imodel: iModel for the branch.
            messages: Initial messages for the branch.
            tool_manager: Tool manager for the branch.
            mailbox: Mailbox for the branch.
            progress: Progress tracker for the branch.
            tools: Tools to be registered in the branch.
        """

        super().__init__(
            system=system,
            system_sender=system_sender,
            system_datetime=system_datetime,
            name=name,
            user=user,
            imodel=imodel,
        )
        self.messages = pile(validate_message(messages), {RoledMessage}, strict=False)

        self.progress = progress or prog(list(self.messages), name=self.name)

        if self.system not in self.messages:
            self.messages.include(self.system)
            self.progress.insert(0, self.system)

        self.tool_manager = tool_manager or ToolManager()
        self.mailbox = mailbox or Exchange()

        if tools:
            self.tool_manager.register_tools(tools)

    def set_system(self, system: System) -> None:
        """
        Set or update the system message for the branch.

        Args:
            system: The new system message.
        """
        if len(self.progress) < 1:
            self.messages.include(system)
            self.system = system
            self.progress[0] = self.system
        else:
            self._change_system(system, delete_previous_system=True)
            self.progress[0] = self.system

    def add_message(
        self,
        *,
        sender: Observable | str | None = None,
        recipient: Observable | str | None = None,
        instruction: Any = None,
        context: Any = None,
        request_fields: dict | MessageFlag = None,
        system: Any = None,
        assistant_response: Any = None,
        action_request: ActionRequest | None = None,
        action_response: ActionResponse | None = None,
        images: list | MessageFlag = None,
        image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
        system_datetime: bool | str | None | MessageFlag = None,
        func: str | Callable | MessageFlag = None,
        arguments: dict | MessageFlag = None,
        func_output: Any | MessageFlag = None,
        metadata: Any = None,
        delete_previous_system: bool = False,
    ) -> bool:
        """
        Add a message to the branch.

        Args:
            Various parameters for different types of messages and metadata.

        Returns:
            bool: True if the message was successfully added.
        """
        if assistant_response:
            sender = self.ln_id

        _msg = create_message(
            sender=sender,
            recipient=recipient,
            instruction=instruction,
            context=context,
            request_fields=request_fields,
            system=system,
            assistant_response=assistant_response,
            action_request=action_request,
            action_response=action_response,
            images=images,
            image_detail=image_detail,
            system_datetime=system_datetime,
            func=func,
            arguments=arguments,
            func_output=func_output,
        )

        if isinstance(_msg, System):
            _msg.recipient = self.ln_id  # the branch itself, system is to the branch
            self._change_system(_msg, delete_previous_system)

        if isinstance(_msg, Instruction):
            _msg.sender = sender or self.user
            _msg.recipient = recipient or self.ln_id

        if isinstance(_msg, AssistantResponse):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or self.user or "user"

        if isinstance(_msg, ActionRequest):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or "N/A"

        if isinstance(_msg, ActionResponse):
            _msg.sender = sender or "N/A"
            _msg.recipient = recipient or self.ln_id

        if metadata:
            _msg.metadata.update(metadata, ["extra"])

        return self.messages.include(_msg)

    def clear_messages(self) -> None:
        """Clear all messages except the system message."""
        self.messages.clear()
        self.progress.clear()
        self.messages.include(self.system)
        self.progress.insert(0, self.system)

    def _change_system(self, system: System, delete_previous_system: bool = False):
        """
        Change the system message.

        Args:
            system: The new system message.
            delete_previous_system: If True, delete the previous system message.
        """
        old_system = self.system
        self.system = system
        self.messages[0] = self.system  # system must be in first message position

        if delete_previous_system:
            del old_system

    def send(
        self, recipient: str, category: str, package: Any, request_source: str
    ) -> None:
        """
        Send a mail to a recipient.

        Args:
            recipient: The recipient's ID.
            category: The category of the mail.
            package: The content of the mail.
            request_source: The source of the request.
        """
        package = Package(
            category=category, package=package, request_source=request_source
        )

        mail = Mail(
            sender=self.ln_id,
            recipient=recipient,
            package=package,
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
        skipped_requests = prog()
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

    @override
    @classmethod
    def convert_from(cls, obj: Any, key: str = "DataFrame", **kwargs) -> Branch:
        p = cls.get_converter_registry().convert_from(obj, key=key, **kwargs)
        return cls(messages=p, **kwargs)

    @override
    def convert_to(self, key: str, /, **kwargs: Any) -> Any:
        return self.get_converter_registry().convert_to(self, key=key, **kwargs)

    @property
    def last_response(self) -> AssistantResponse | None:
        """
        Get the last assistant response.

        Returns:
            AssistantResponse | None: The last assistant response, if any.
        """
        for i in reversed(self.progress):
            if isinstance(self.messages[i], AssistantResponse):
                return self.messages[i]

    @property
    def assistant_responses(self) -> Pile:
        """
        Get all assistant responses as a Pile.

        Returns:
            Pile: A Pile containing all assistant responses.
        """
        return pile(
            [
                self.messages[i]
                for i in self.progress
                if isinstance(self.messages[i], AssistantResponse)
            ]
        )

    def update_last_instruction_meta(self, meta: dict) -> None:
        """
        Update metadata of the last instruction.

        Args:
            meta (dict): Metadata to update.
        """
        for i in reversed(self.progress):
            if isinstance(self.messages[i], Instruction):
                self.messages[i].metadata.update(meta, ["extra"])
                return

    def has_tools(self) -> bool:
        """
        Check if the branch has any registered tools.

        Returns:
            bool: True if tools are registered, False otherwise.
        """
        return self.tool_manager.registry != {}

    def register_tools(self, tools: Any) -> None:
        """
        Register new tools to the tool manager.

        Args:
            tools (Any): Tools to be registered.
        """
        self.tool_manager.register_tools(tools=tools)

    def delete_tools(self, tools: Any, verbose: bool = True) -> bool:
        """
        Delete specified tools from the tool manager.

        Args:
            tools (Any): Tools to be deleted.
            verbose (bool): If True, print status messages.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not isinstance(tools, list):
            tools = [tools]
        if is_same_dtype(tools, str):
            for act_ in tools:
                if act_ in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_)
            if verbose:
                print("tools successfully deleted")
            return True
        elif is_same_dtype(tools, Tool):
            for act_ in tools:
                if act_.function_name in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_.function_name)
            if verbose:
                print("tools successfully deleted")
            return True
        if verbose:
            print("tools deletion failed")
        return False

    def to_chat_messages(self) -> list[dict[str, Any]]:
        """
        Convert messages to a list of chat message dictionaries.

        Returns:
            list[dict[str, Any]]: A list of chat message dictionaries.
        """
        return [self.messages[i].chat_msg for i in self.progress]

    def _is_invoked(self) -> bool:
        """Check if the last message is an ActionResponse."""
        return isinstance(self.messages[-1], ActionResponse)


# File: lion_core/session/branch.py
