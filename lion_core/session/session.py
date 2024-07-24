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
from lion_core.sys_utils import SysUtil
from lion_core.generic.pile import pile, Pile
from lion_core.generic.util import to_list_type
from lion_core.generic.exchange import Exchange
from lion_core.communication.mail_manager import MailManager
from lion_core.session.base import BaseSession
from lion_core.session.branch import Branch


class Session(BaseSession):

    def __init__(
        self,
        default_branch: Branch,
        branches: Pile[Branch],
        mail_transfer: Exchange,
    ):
        super().__init__()
        self.branches: Pile[Branch] = branches
        self.default_branch: Branch = default_branch
        self.mail_transfer: Exchange = mail_transfer
        self.mail_manager: MailManager = MailManager([self.mail_transfer])

    @staticmethod
    def validate_branches(value: Any):
        if isinstance(value, Pile):
            for branch in value:
                if not isinstance(branch, Branch):
                    raise ValueError("The branches pile contains non-Branch object")
            return value
        else:
            try:
                value = pile(items=value, item_type=Branch)
                return value
            except Exception as e:
                raise ValueError(f"Invalid branches value. Error:{e}")

    def new_branch(self, **kwargs):
        branch = Branch(**kwargs)
        self.branches.include(branch)
        return branch

    def add_branch(self, branch: Branch):
        self.branches.include(branch)

    def remove_branch(self, branch, delete):
        if branch not in self.branches:
            raise ValueError(
                f"Branch {branch.name or branch.ln_id[:8]}.. does not exist."
            )
        self.branches.exclude(branch)
        if delete:
            del branch

    def change_default_branch(self, branch):
        if branch not in self.branches:
            self.add_branch(branch)
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
