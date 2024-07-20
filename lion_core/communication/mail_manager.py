from collections import deque
import asyncio
from typing import Any

from lion_core.abc import BaseManager
from lion_core.sys_util import SysUtil
from lion_core.generic.util import to_list_type
from lion_core.generic import Pile, pile, Exchange

from .mail import Mail, Package


class MailManager(BaseManager):

    def __init__(self, sources: list[Any]):

        super().__init__()
        self.sources: Pile[Any] = pile()
        self.mails: dict[str, dict[str, deque]] = {}
        self.execute_stop: bool = False

        if sources:
            self.add_sources(sources)

    def add_sources(self, sources: list[Any]) -> None:
        try:
            sources = to_list_type(sources)
            self.sources.include(sources)
            for item in sources:
                self.mails[item.ln_id] = {}
        except Exception as e:
            raise ValueError(f"Failed to add source. Error {e}")

    @staticmethod
    def create_mail(sender: str, recipient: str, category: str, package: Any) -> Mail:
        pack = Package(category=category, package=package)
        mail = Mail(
            sender=sender,
            recipient=recipient,
            package=pack,
        )
        return mail

    def delete_source(self, source_id: str) -> None:
        if source_id not in self.sources:
            raise ValueError(f"Source {source_id} does not exist.")
        self.sources.pop(source_id)
        self.mails.pop(source_id)

    def collect(self, sender: str) -> None:
        if sender not in self.sources:
            raise ValueError(f"Sender source {sender} does not exist.")
        mailbox: Exchange = (
            self.sources[sender]
            if isinstance(self.sources[sender], Exchange)
            else self.sources[sender].mailbox
        )
        while mailbox.pending_outs.size() > 0:
            mail_id = mailbox.pending_outs.popleft()
            mail: Mail = mailbox.pile.pop(mail_id)
            if mail.recipient not in self.sources:
                raise ValueError(f"Recipient source {mail.recipient} does not exist")
            if mail.sender not in self.mails[mail.recipient]:
                self.mails[mail.recipient].update({mail.sender: deque()})
            self.mails[mail.recipient][mail.sender].append(mail)

    def send(self, recipient: str) -> None:
        if recipient not in self.sources:
            raise ValueError(f"Recipient source {recipient} does not exist.")
        if not self.mails[recipient]:
            return
        for key in list(self.mails[recipient].keys()):
            pending_mails = self.mails[recipient].pop(key)
            mailbox = (
                self.sources[recipient]
                if isinstance(self.sources[recipient], Exchange)
                else self.sources[recipient].mailbox
            )
            while pending_mails:
                mail = pending_mails.popleft()
                mailbox.include(mail, "in")

    def collect_all(self) -> None:
        for source in self.sources:
            self.collect(SysUtil.get_id(source))

    def send_all(self) -> None:
        for source in self.sources:
            self.send(SysUtil.get_id(source))

    async def execute(self, refresh_time: int = 1) -> None:
        while not self.execute_stop:
            self.collect_all()
            self.send_all()
            await asyncio.sleep(refresh_time)


# File: lion_core/communication/mail_manager.py
