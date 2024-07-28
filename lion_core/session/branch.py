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

from typing import Any, Callable, ClassVar, override

from pydantic import Field

from lion_core.abc import BaseiModel
from lion_core.imodel.imodel import iModel
from lion_core.libs import is_same_dtype

from lion_core.generic import (
    pile,
    Pile,
    progression,
    Progression,
    Exchange,
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

from lion_core.session.utils import create_message

from lion_core.session.base import BaseSession
from lion_core.converter import ConverterRegistry


class BranchConverterRegistry(ConverterRegistry): ...


class Branch(BaseSession):
    """Represents a branch in the conversation tree with tools and messages."""

    messages: Pile | None = Field(None)
    tool_manager: ToolManager = Field(default_factory=ToolManager)
    mailbox: Exchange | None = Field(None)
    name: str | None = Field(None)

    order: Progression = Field(default_factory=progression)

    _converter_registry: ClassVar = BranchConverterRegistry

    def __init__(
        self,
        system: System | str | dict | None = None,
        system_sender: str | None = None,
        system_datetime: str | bool | None = None,
        user: str | None = None,
        messages: Pile | None = None,
        tool_manager: ToolManager = None,
        progress: Progression = None,
        mailbox: Exchange = None,
        tools: Any = None,
        imodel: BaseiModel = None,
        name: str | None = None,
    ):
        """
        Initialize a Branch instance.

        Args:
            system (System | str | dict | None): The system message. Can be a
                System Node, string, JSON-serializable dict, or None. If not a
                System Node, one will be created. If None, a default system
                message is used.
            system_sender (str | None): The sender of the system message.
            system_datetime (str | bool | None): Datetime for system message.
                If True, adds current datetime. If str, adds that string.
            user (str | None): The user identifier. Defaults to "user".
            messages (Pile | None): Initial messages for the branch.
            tool_manager (ToolManager | None): Custom tool manager. If None, a
                new one is created.
            mailbox (Exchange | None): Custom mailbox. If None, a new one is
                created.
            tools (Any): Tools to be registered. Can be individual Tool or
                Callable objects, or collections thereof. Cannot be bool.
            imodel (iModel | None): Custom iModel. If None, a new one is
                created.
            name (str | None): Optional name for the branch.
        """
        super().__init__()

        if not isinstance(system, System):
            system = System(
                system=(
                    system or "You are a helpful assistant. Let's think step by step."
                ),
                sender=system_sender,
                recipient=self.ln_id,
                with_datetime=system_datetime,
            )

        if not messages:
            messages = pile(items={}, item_type=RoledMessage, order=None, strict=False)

        user = user or "user"
        tool_manager = tool_manager or ToolManager()
        mailbox = mailbox or Exchange()
        imodel = imodel or iModel()

        self.messages = messages
        self.tool_manager = tool_manager
        self.mailbox = mailbox
        self.name = name
        self.user = user
        self.imodel = imodel
        self.order = progress or progression()

        if tools:
            self.tool_manager.register_tools(tools)

        self.set_system(system)

    def set_system(self, system: System) -> None:
        """
        Set or update the system message.

        Args:
            system (System): The new system message to set.
        """
        if len(self.order) < 1:
            self.messages.include(system)
            self.system = system
            self.order[0] = self.system
        else:
            self.change_system(system, delete_previous_system=True)
            self.order[0] = self.system

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
        for i in reversed(self.order):
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
                for i in self.order
                if isinstance(self.messages[i], AssistantResponse)
            ]
        )

    def update_last_instruction_meta(self, meta: dict) -> None:
        """
        Update metadata of the last instruction.

        Args:
            meta (dict): Metadata to update.
        """
        for i in reversed(self.order):
            if isinstance(self.messages[i], Instruction):
                self.messages[i].metadata.update(["extra"], meta)
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

    def clear(self) -> None:
        """Clear all messages in the branch."""
        self.messages.clear()
        self.order.clear()

    def to_chat_messages(self) -> list[dict[str, Any]]:
        """
        Convert messages to a list of chat message dictionaries.

        Returns:
            list[dict[str, Any]]: A list of chat message dictionaries.
        """
        return [self.messages[i].chat_msg for i in self.order]

    def _is_invoked(self) -> bool:
        """Check if the last message is an ActionResponse."""
        return isinstance(self.messages[-1], ActionResponse)
