from collections import deque
import asyncio
from typing import Any

from lion_core.abc import BaseManager
from lion_core.sys_util import SysUtil
from lion_core.generic.util import to_list_type
from lion_core.generic import Pile, pile, Exchange

from .mail import Mail, Package


class MailManager(BaseManager):
    """
    Manages the sending, receiving, and storage of mail items.

    This class acts as a central hub for managing mail transactions within
    a system. It allows for the addition and deletion of sources, and it
    handles the collection and dispatch of mails to and from these sources.

    Attributes:
        sources: A pile of managed sources.
        mails: A nested dictionary storing queued mail items.
        execute_stop: A flag indicating whether to stop execution.
    """

    def __init__(self, sources: list[Any] | None = None):
        """
        Initializes the MailManager with optional sources.

        Args:
            sources: A list of sources to be managed by the MailManager.
        """
        super().__init__()
        self.sources: Pile[Any] = pile()
        self.mails: dict[str, dict[str, deque]] = {}
        self.execute_stop: bool = False

        if sources:
            self.add_sources(sources)

    def add_sources(self, sources: list[Any]) -> None:
        """
        Adds new sources to the MailManager.

        Args:
            sources: A list of sources to be added.

        Raises:
            ValueError: If failed to add sources.
        """
        try:
            sources = to_list_type(sources)
            self.sources.include(sources)
            for item in sources:
                self.mails[item.ln_id] = {}
        except Exception as e:
            raise ValueError(f"Failed to add source. Error {e}")

    @staticmethod
    def create_mail(sender: str, recipient: str, category: str, package: Any) -> Mail:
        """
        Creates a mail item.

        Args:
            sender: The sender of the mail.
            recipient: The recipient of the mail.
            category: The category of the mail.
            package: The content of the package.

        Returns:
            The created mail object.
        """
        pack = Package(category=category, package=package)
        mail = Mail(
            sender=sender,
            recipient=recipient,
            package=pack,
        )
        return mail

    def delete_source(self, source_id: str) -> None:
        """
        Deletes a source from the MailManager.

        Args:
            source_id: The ID of the source to be deleted.

        Raises:
            ValueError: If the source does not exist.
        """
        if source_id not in self.sources:
            raise ValueError(f"Source {source_id} does not exist.")
        self.sources.pop(source_id)
        self.mails.pop(source_id)

    def collect(self, sender: str) -> None:
        """
        Collects mails from a sender's outbox and queues them for the recipient.

        Args:
            sender: The ID of the sender.

        Raises:
            ValueError: If the sender or recipient source does not exist.
        """
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
        """
        Sends mails to a recipient's inbox.

        Args:
            recipient: The ID of the recipient.

        Raises:
            ValueError: If the recipient source does not exist.
        """
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
        """Collects mails from all sources."""
        for source in self.sources:
            self.collect(SysUtil.get_lion_id(source))

    def send_all(self) -> None:
        """Sends mails to all sources."""
        for source in self.sources:
            self.send(SysUtil.get_lion_id(source))

    async def execute(self, refresh_time: int = 1) -> None:
        """
        Continuously collects and sends mails until execution is stopped.

        Args:
            refresh_time: The time in seconds to wait between each cycle.
                Defaults to 1.
        """
        while not self.execute_stop:
            self.collect_all()
            self.send_all()
            await asyncio.sleep(refresh_time)


# File: lion_core/communication/mail_manager.py
