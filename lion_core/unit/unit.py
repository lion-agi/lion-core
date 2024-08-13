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

"""
Module for the UnitProcessor class in the Lion framework.

This module provides the UnitProcessor class, which encapsulates various
processing methods for units, including act, action request, chat, direct,
and validation processing.
"""

from typing import Type, TYPE_CHECKING
from lion_core.abc import BaseProcessor
from lion_core.form.base import BaseForm
from lion_core.unit.unit_form import UnitForm
from lion_core.unit.process_act import process_act
from lion_core.unit.process_action_request import process_action_request
from lion_core.unit.process_chat import process_chat
from lion_core.unit.process_direct import process_direct
from lion_core.unit.process_validation import process_validation

if TYPE_CHECKING:
    from lion_core.session.branch import Branch


class UnitProcessor(BaseProcessor):
    """
    Unit processor class for handling various processing tasks.

    This class provides methods for processing acts, action requests, chats,
    direct interactions, and validations within a branch context.

    Attributes:
        default_form (Type[Form]): The default form type to use.
        branch (Branch): The branch associated with this processor.
    """

    default_form: Type[BaseForm] = UnitForm

    def __init__(self, branch: "Branch"):
        """
        Initialize the UnitProcessor.

        Args:
            branch (Branch): The branch to associate with this processor.
        """
        self.branch = branch

    async def process_act(
        self, form: BaseForm, actions: dict = None, return_branch: bool = False
    ):
        """
        Process an act within the branch context.

        Args:
            form (Form): The form to process.
            actions (dict, optional): Actions to process. Defaults to None.
            return_branch (bool): Whether to return the branch. Defaults to False.

        Returns:
            The result of processing the act.
        """
        return await process_act(
            branch=self.branch,
            form=form,
            actions=actions or {},
            return_branch=return_branch,
        )

    async def process_action_request(self, _msg=None, action_request=None):
        """
        Process an action request within the branch context.

        Args:
            _msg: The message to process.
            action_request: The action request to process.
        """
        await process_action_request(
            branch=self.branch,
            msg=_msg,
            action_request=action_request,
        )

    async def process_chat(self, **kwargs):
        """
        Process a chat interaction within the branch context.

        Args:
            **kwargs: Additional keyword arguments for chat processing.

        Returns:
            The result of processing the chat.
        """
        return await process_chat(branch=self.branch, **kwargs)

    async def process_direct(self, **kwargs):
        """
        Process a direct interaction within the branch context.

        Args:
            **kwargs: Additional keyword arguments for direct processing.

        Returns:
            The result of processing the direct interaction.
        """
        return await process_direct(branch=self.branch, **kwargs)

    async def process_validation(self, **kwargs):
        """
        Process a validation within the branch context.

        Args:
            **kwargs: Additional keyword arguments for validation processing.

        Returns:
            The result of processing the validation.
        """
        return await process_validation(branch=self.branch, **kwargs)


__all__ = ["UnitProcessor"]

# File: lion_core/unit/processor.py
