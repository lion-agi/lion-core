from typing import Any

from lion_core.abc import BaseiModel
from lion_core.generic import Pile, pile, progression

from lion_core.generic.exchange import Exchange
from lion_core.action.tool import Tool
from lion_core.action.tool_manager import ToolManager
from lion_core.communication import (
    RoledMessage,
    System,
    Instruction,
    AssistantResponse,
    ActionRequest,
    ActionResponse,
    create_message,
    MailManager,
    Mail,
)
from lion_core.record.log_manager import LogManager
from lion_core.imodel.model_manager import ModelManager
from .base import BaseSession
from .utils import validate_messages, validate_system


class Branch(BaseSession):

    def __init__(
        self,
        system: System,
        messages: Pile[RoledMessage],
        tool_manager: ToolManager,
        model_manager: ModelManager,
        log_manager: LogManager,
        mail_manager: MailManager,
        mailbox: Exchange,
        name: str,
    ):
        super().__init__()
        self.system = system
        self.messages = messages
        self.tool_manager = tool_manager
        self.model_manager = model_manager
        self.log_manager = log_manager
        self.mail_manager = mail_manager
        self.mailbox = mailbox
        self.name = name

    @staticmethod
    def validate_system(
        system: Any, sender, recipient, system_datetime, **kwargs
    ) -> None:
        return validate_system(
            system,
            sender=sender,
            recipient=recipient,
            system_datetime=system_datetime,
            **kwargs,
        )

    @staticmethod
    def validate_messages(value: Any):
        # will return a new pile
        return pile(validate_messages(value), RoledMessage)

    def include_message(
        self,
        *,
        system,  # system node - JSON serializable
        instruction,  # Instruction node - JSON serializable
        context,  # JSON serializable
        assistant_response,  # JSON
        function,
        arguments,
        func_outputs,
        action_request,  # ActionRequest node
        action_response,  # ActionResponse node
        images,
        sender,  # str
        recipient,  # str
        requested_fields,  # dict[str, str]
        metadata,  # extra metadata
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
            arguments=arguments,
            func_outputs=func_outputs,
            action_request=action_request,
            action_response=action_response,
            sender=sender,
            images=images,
            recipient=recipient,
            requested_fields=requested_fields,
            **kwargs,
        )

        if isinstance(_msg, System):
            _msg.recipient = self.ln_id  # the branch itself, system is to the branch
            self._remove_system()
            self.system = _msg

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

    def change_system(self, system: System, delete_previous):
        old_system = self.system
        self.system = system
        self.messages[0] = self.system  # system must be in first message position

        if delete_previous:
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
        message: bool,
        tool: bool,
        imodel: bool,
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
