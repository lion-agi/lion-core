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

from pydantic import Field
from lion_core.abc import BaseiModel
from lion_core.sys_utils import SysUtil
from lion_core.generic import pile, Pile, Progression, progression
from lion_core.generic.util import to_list_type
from lion_core.generic.exchange import Exchange
from lion_core.generic.flow import Flow, flow
from lion_core.communication.mail_manager import MailManager
from lion_core.session.base import BaseSession
from lion_core.session.branch import Branch
from lion_core.exceptions import ItemNotFoundError
from lion_core.graph.node import Node

from lion_core.action.tool import Tool
from lion_core.action.tool_manager import ToolManager
from lion_core.communication.system import System

from lion_core.session.utils import validate_message, validate_system, create_message


class Session(BaseSession):

    branches: Pile[Branch] | None = Field(
        default_factory=lambda: pile({}, item_type=Branch, strict=False),
    )

    default_branch: Branch | None = Field(None)

    mail_transfer: Exchange | None = Field(
        default_factory=Exchange,
        description="The exchange system for mail transfer.",
    )

    mail_manager: MailManager | None = Field(None)
    conversations: Flow | None = Field(None)
    name: str | None = Field(None)

    def __init__(
        self,
        system: System | dict | str | list = None,
        *,
        system_sender: Any = None,
        system_datetime: bool | str | None = None,
        default_branch: Branch | str | None = None,
        default_branch_name: str | None = None,
        branches: Pile[Branch] | None = None,
        mail_transfer: Exchange | None = None,
        branch_user: str | None = None,
        session_user: str | None = None,
        session_name: str | None = None,
        tools: Any = None,
        tool_manager: ToolManager | None = None,
        imodel: BaseiModel | None = None,
    ):
        super().__init__()

        if not isinstance(system, System):
            system = System(
                system=system,
                sender=system_sender,
                system_datetime=system_datetime,
                recipient=self.ln_id,
            )

        if default_branch is None:
            if branches and len(branches) > 0:
                default_branch = branches[0]
                if default_branch_name:
                    default_branch.name = default_branch_name
                if tool_manager:
                    default_branch.tool_manager = tool_manager
                if tools:
                    default_branch.tool_manager.register_tools(tools)
                if branch_user:
                    default_branch.user = branch_user

            elif branches is None:
                branches = pile()
                default_branch = self.new_branch(
                    system=system.clone(),
                    system_sender=system_sender,
                    system_datetime=system_datetime,
                    user=branch_user,
                    imodel=imodel,
                    name=default_branch_name,
                    tool_manager=tool_manager,
                    tools=tools,
                )
                branches += default_branch
        if tools:
            self.default_branch.tool_manager.register_tools(tools)

        self.imodel = imodel or self.default_branch.imodel
        self.system = system
        self.default_branch = default_branch
        self.branches = branches or pile({}, item_type=Branch, strict=False)
        self.mail_transfer = mail_transfer or Exchange()
        self.mail_manager = MailManager([self.mail_transfer])
        self.user = session_user or "user"
        self.name = session_name or f"Session_{self.ln_id[-5:]}"

        p = pile({}, item_type=Progression, strict=False)
        for branch in self.branches:
            progression = branch.progress
            progression.name = branch.name
            p += progression

        self.conversations = flow(p, self.default_branch.name)

    def new_branch(
        self,
        system: System | None = None,
        system_sender: str | None = None,
        user: str | None = None,
        messages: Pile = None,
        progress: Progression = None,
        tool_manager: ToolManager = None,
        tools: Any = None,
        imodel=None,
    ):
        """
        Creates a new branch and adds it to the session.

        Args:
            system (System, optional): The system message for the branch.
            system_sender (str, optional): The sender of the system message.
            user (str, optional): The user associated with the branch.
            messages (Pile, optional): The pile of messages for the branch.
            progress (Progression, optional): The progression of messages.
            tool_manager (ToolManager, optional): The tool manager for the branch.
            tools (Any, optional): The tools to register with the tool manager.
            imodel (iModel, optional): The model associated with the branch.

        Returns:
            Branch: The created branch.
        """
        if system is None:
            system = self.system.clone()
            system.sender = self.ln_id
            system_sender = self.ln_id
        branch = Branch(
            system=system,
            system_sender=system_sender,
            user=user,
            messages=messages,
            progress=progress,
            tool_manager=tool_manager,
            tools=tools,
            imodel=imodel or self.imodel,
        )
        self.branches.append(branch)
        self.mail_manager.add_sources(branch)
        if self.default_branch is None:
            self.default_branch = branch
        return branch

    def remove_branch(
        self,
        branch: Branch | str,  # the branch to delete
        delete: bool = False,  # whether to delete the branch from memory
    ):
        if branch not in self.branches:
            raise ItemNotFoundError(
                f"Branch {branch.name or branch.ln_id[:8]}.. does not exist."
            )

        branch: Branch = self.branches[branch]
        branch_id = branch.ln_id

        self.conversations.exclude(prog=branch.progress)
        self.branches.exclude(branch)
        self.mail_manager.delete_source(branch_id)

        if self.default_branch == branch:
            if self.branches.is_empty() == 0:
                self.default_branch = None
            else:
                self.default_branch = self.branches[0]

        if delete:
            del branch

    def split_branch(self, branch):
        """
        Splits a branch, creating a new branch with the same messages and tools.

        Args:
            branch (Branch | str): The branch or its ID to split.

        Returns:
            Branch: The newly created branch.
        """
        branch = self.branches[branch]
        system = branch.system.clone() if branch.system else None
        if system:
            system.sender = branch.ln_id
        progress = progression()
        messages = pile()

        for id_ in branch.progress:
            clone_message = branch.messages[id_].clone()
            progress.append(clone_message.ln_id)
            messages.append(clone_message)

        tools = (
            list(branch.tool_manager.registry.values())
            if branch.tool_manager.registry
            else None
        )
        branch_clone = Branch(
            system=system,
            system_sender=branch.ln_id,
            user=branch.user,
            progress=progress,
            messages=messages,
            tools=tools,
        )
        for message in branch_clone.messages:
            message.sender = branch.ln_id
            message.recipient = branch_clone.ln_id
        self.branches.append(branch_clone)
        self.mail_manager.add_sources(branch_clone)
        return branch_clone

    def change_default_branch(self, branch):
        """
        Changes the default branch of the session.

        Args:
            branch (Branch | str): The branch or its ID to set as the default.
        """
        branch = self.branches[branch]
        self.default_branch = branch

    def collect(self, from_: Branch | str | Pile[Branch] | None):
        """
        Collects mail from specified branches.

        Args:
            from_ (Branch | str | Pile[Branch], optional): The branches to collect mail from.
                If None, collects mail from all branches.
        """
        if from_ is None:
            self.mail_manager.collect_all()
        else:
            try:
                sources = to_list_type(from_)
                for source in sources:
                    self.mail_manager.collect(SysUtil.get_id(source))
            except Exception as e:
                raise ValueError(f"Failed to collect mail. Error: {e}")

    def send(self, to_: Branch | str | Pile[Branch] | None):
        """
        Sends mail to specified branches.

        Args:
            to_ (Branch | str | Pile[Branch], optional): The branches to send mail to.
                If None, sends mail to all branches.
        """
        if to_ is None:
            self.mail_manager.send_all()
        else:
            try:
                sources = to_list_type(to_)
                for source in sources:
                    self.mail_manager.send(SysUtil.get_id(source))
            except Exception as e:
                raise ValueError(f"Failed to send mail. Error: {e}")

    def collect_send_all(self, receive_all):
        """
        Collects and sends mail for all branches, optionally receiving all mail.

        Args:
            receive_all (bool, optional): Whether to receive all mail for all branches.
        """
        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches:
                branch.receive_all()
