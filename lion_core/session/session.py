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

from typing import Any, Type

from pydantic import Field, PrivateAttr

from lion_core.sys_util import SysUtil
from lion_core.setting import LN_UNDEFINED
from lion_core.generic import pile, Pile, Progression, progression
from lion_core.generic.util import to_list_type
from lion_core.generic.exchange import Exchange
from lion_core.generic.flow import Flow, flow
from lion_core.communication import MailManager, RoledMessage
from lion_core.session.base import BaseSession
from lion_core.session.branch import Branch
from lion_core.exceptions import ItemNotFoundError, LionValueError
from lion_core.action.tool_manager import ToolManager
from lion_core.imodel.imodel import iModel


class Session(BaseSession):
    """
    Manages multiple conversation branches and mail transfer in a session.

    Attributes:
        branches (Pile | None): Collection of conversation branches.
        default_branch (Branch | None): The default conversation branch.
        mail_transfer (Exchange | None): Mail transfer system.
        mail_manager (MailManager | None): Manages mail operations.
        conversations (Flow | None): Manages conversation flow.
    """

    branches: Pile | None = Field(None)
    default_branch: Branch | None = Field(None)
    mail_transfer: Exchange | None = Field(None)
    mail_manager: MailManager | None = Field(None)
    conversations: Flow | None = Field(None)
    branch_type: Type[Branch] = PrivateAttr(Branch)

    def __init__(
        self,
        branch_type: Type[Branch] = Branch,
        session_system: Any = None,
        session_system_sender: Any = None,
        session_system_datetime: Any = None,
        session_name: str | None = None,
        session_user: str | None = None,
        session_imodel: iModel | None = None,
        mail_transfer: Exchange | None = None,
        branches: Pile[Branch] | None = None,
        default_branch: Branch | None = None,
        conversations: Flow | None = None,
        branch_system: Any = None,
        branch_system_sender: str | None = None,
        branch_system_datetime: Any = None,
        branch_name: str | None = None,
        branch_user: str | None = None,
        branch_imodel: iModel | None = None,
        branch_messages: Pile | None = None,
        branch_mailbox: Exchange | None = None,
        branch_progress: Progression | None = None,
        tool_manager: ToolManager | None = None,
        tools: Any = None,
    ):
        """
        Initialize a Session instance.

        Args:
            session_system: System message for the session.
            session_system_sender: Sender of the session system message.
            session_system_datetime: Datetime for session system message.
            session_name: Name of the session.
            session_user: User identifier for the session.
            session_imodel: iModel for the session.
            mail_transfer: Mail transfer system.
            branches: Existing branches to include.
            default_branch: Default branch for the session.
            conversations: Existing conversation flow.
            branch_*: Parameters for creating a new branch if needed.
            tool_manager: Tool manager for the branch.
            tools: Tools to be registered.
        """
        super().__init__(
            system=session_system,
            system_sender=session_system_sender,
            system_datetime=session_system_datetime,
            name=session_name,
            user=session_user,
            imodel=session_imodel or branch_imodel,
        )
        if branch_type:
            self.branch_type = branch_type

        if not branches and not default_branch:
            self.default_branch = branch_type(
                system=branch_system,
                system_sender=branch_system_sender
                or self.ln_id,  # the system of branch is the session
                system_datetime=branch_system_datetime,
                user=branch_user or session_user,
                messages=branch_messages,
                progress=branch_progress,
                tool_manager=tool_manager,
                tools=tools,
                imodel=branch_imodel or session_imodel,
                name=branch_name,
                mailbox=branch_mailbox,
            )
            self.branches = pile(self.default_branch, branch_type, strict=False)

        elif branches and not default_branch:
            self.branches = branches
            self.default_branch = branches[0]

        elif not branches and default_branch:
            self.default_branch = default_branch
            self.branches = pile(default_branch, branch_type, strict=False)

        self.mail_transfer = mail_transfer
        self.mail_manager = MailManager([self.mail_transfer])
        if not conversations:
            conversations = flow(
                progressions=[branch.progress for branch in self.branches],
                default_name=self.default_branch.name,
            )
        self.conversations = conversations

    def new_branch(
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
        Create a new branch in the session.

        Args:
            system: System message for the branch.
            system_sender: Sender of the branch system message.
            system_datetime: Datetime for branch system message.
            name: Name of the branch.
            user: User identifier for the branch.
            imodel: iModel for the branch.
            messages: Initial messages for the branch.
            tool_manager: Tool manager for the branch.
            mailbox: Mailbox for the branch.
            progress: Progress tracker for the branch.
            tools: Tools to be registered in the branch.
        """
        if system in [None, LN_UNDEFINED]:
            system = self.system.clone()
            system.sender = self.ln_id
            system_sender = self.ln_id

        branch = self.branch_type(
            system=system,
            system_sender=system_sender,
            system_datetime=system_datetime,
            name=name,
            user=user,
            imodel=imodel or self.imodel,
            messages=messages,
            progress=progress,
            tool_manager=tool_manager,
            mailbox=mailbox,
            tools=tools,
        )
        self.branches.include(branch)
        self.mail_manager.add_sources(branch)
        if self.default_branch is None:
            self.default_branch = branch

    def remove_branch(
        self,
        branch: Branch | str,
        delete: bool = False,
    ):
        """
        Remove a branch from the session.

        Args:
            branch: The branch to remove or its identifier.
            delete: If True, delete the branch from memory.

        Raises:
            ItemNotFoundError: If the branch does not exist.
        """
        if branch not in self.branches:
            raise ItemNotFoundError(
                f"Branch {branch.name or branch.ln_id[:8]}.. does not exist."
            )

        branch: Branch = self.branches[branch]

        self.conversations.exclude(prog=branch.progress)
        self.branches.exclude(branch)
        self.mail_manager.delete_source(branch.ln_id)

        if self.default_branch.ln_id == branch.ln_id:
            if self.branches.is_empty():
                self.default_branch = None
            else:
                self.default_branch = self.branches[0]

        if delete:
            del branch

    def split_branch(self, branch: Branch | str) -> Branch:
        """
        Split a branch, creating a new branch with the same messages and tools.

        Args:
            branch: The branch to split or its identifier.

        Returns:
            The newly created branch.
        """
        branch: Branch = self.branches[branch]
        system = branch.system.clone() if branch.system else None
        if system:
            system.sender = branch.ln_id
        progress = progression()
        messages = pile({}, RoledMessage, strict=False)

        for id_ in branch.progress:
            clone_message: RoledMessage = branch.messages[id_].clone()
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

    def change_default_branch(self, branch: Branch | str):
        """
        Change the default branch of the session.

        Args:
            branch: The branch to set as default or its identifier.
        """
        branch = self.branches[branch]
        if branch and len(branch) == 1:
            self.default_branch = branch
        raise LionValueError("Session can only have one default branch.")

    def collect(self, from_: Branch | str | Pile[Branch] | None = None):
        """
        Collect mail from specified branches.

        Args:
            from_: The branches to collect mail from. If None, collect from all.

        Raises:
            ValueError: If mail collection fails.
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

    def send(self, to_: Branch | str | Pile[Branch] | None = None):
        """
        Send mail to specified branches.

        Args:
            to_: The branches to send mail to. If None, send to all.

        Raises:
            ValueError: If mail sending fails.
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

    def collect_send_all(self, receive_all: bool = False):
        """
        Collect and send mail for all branches, optionally receiving all mail.

        Args:
            receive_all: If True, receive all mail for all branches.
        """
        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches:
                branch.receive_all()


# File: lion_core/session/session.py
