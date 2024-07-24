from typing import Any, Callable

from lion_core.abc import BaseiModel
from lion_core.generic.pile import Pile, pile
from lion_core.generic.progression import progression

from lion_core.generic.exchange import Exchange
from lion_core.action.tool import Tool
from lion_core.action.tool_manager import ToolManager
from lion_core.communication.message import RoledMessage
from lion_core.communication.system import System
from lion_core.communication.instruction import Instruction
from lion_core.communication.assistant_response import AssistantResponse
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse
from lion_core.communication.mail_manager import MailManager
from lion_core.communication.mail import Mail
from lion_core.session.utils import validate_messages, validate_system, create_message
from lion_core.session.base import BaseSession


class Branch(BaseSession):

    def __init__(
        self,
        system: System,
        messages: Pile,
        tool_manager: ToolManager,
        mail_manager: MailManager,
        mailbox: Exchange,
        name: str,
    ):
        super().__init__()
        self.system = system
        self.messages = messages
        self.tool_manager = tool_manager
        self.mail_manager = mail_manager
        self.mailbox = mailbox
        self.name = name

    @staticmethod
    def validate_system(
        system: Any,
        sender,
        recipient,
        system_datetime,
        system_datetime_strftime,
        **kwargs,
    ) -> None:
        return validate_system(
            system,
            sender=sender,
            recipient=recipient,
            system_datetime=system_datetime,
            system_datetime_strftime=system_datetime_strftime,
            **kwargs,
        )

    @staticmethod
    def validate_messages(value: Any):
        # will return a new pile
        return pile(validate_messages(value), RoledMessage)

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
