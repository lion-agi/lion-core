import asyncio
from collections import deque
from typing import Any

from lion_core.abc import BaseManager
from lion_core.communication.mail import Mail, Package
from lion_core.generic.exchange import Exchange
from lion_core.generic.pile import Pile, pile
from lion_core.generic.utils import to_list_type
from lion_core.sys_utils import SysUtil


class MailManager(BaseManager):
    """
    Manages mail operations for multiple sources in the Lion framework.

    The `MailManager` class is responsible for handling mail-related tasks,
    including collecting and sending mail between different sources in the
    system. It allows for adding sources, creating mails, and managing the
    communication flow in an asynchronous manner.

    Attributes:
        sources (Pile): A collection of sources managed by the `MailManager`.
        mails (dict[str, dict[str, deque]]): A dictionary holding the mails,
            organized by recipient and sender.
        execute_stop (bool): A flag to control the stopping of the asynchronous
            mail execution process.

    Methods:
        add_sources(sources: Any) -> None:
            Adds new sources to the `MailManager`.
        create_mail(sender: str, recipient: str, category: str, package: Any,
            request_source=None) -> Mail:
            Creates a new `Mail` object.
        delete_source(source_id: str) -> None:
            Deletes a source from the `MailManager`.
        collect(sender: str) -> None:
            Collects mail from a specific sender.
        send(recipient: str) -> None:
            Sends mail to a specific recipient.
        collect_all() -> None:
            Collects mail from all sources.
        send_all() -> None:
            Sends mail to all recipients.
        execute(refresh_time: int = 1) -> None:
            Executes the mail collection and sending process asynchronously.
    """

    def __init__(self, sources: list[Any] = None):
        """
        Initializes a `MailManager` instance.

        Args:
            sources (list[Any], optional): A list of initial sources to be
                managed. Defaults to None.
        """
        self.sources: Pile = pile()
        self.mails: dict[str, dict[str, deque]] = {}
        self.execute_stop: bool = False

        if sources:
            self.add_sources(sources)

    def add_sources(self, sources: Any) -> None:
        """
        Adds new sources to the `MailManager`.

        Args:
            sources (Any): The sources to be added. Can be a single source or a
                list of sources.

        Raises:
            ValueError: If the sources cannot be added.
        """
        try:
            sources = to_list_type(sources)
            self.sources.include(sources)
            for item in sources:
                self.mails[item.ln_id] = {}
        except Exception as e:
            raise ValueError(f"Failed to add source.") from e

    @staticmethod
    def create_mail(
        sender: str,
        recipient: str,
        category: str,
        package: Any,
        request_source=None,
    ) -> Mail:
        """
        Creates a new `Mail` object.

        Args:
            sender (str): The ID of the sender.
            recipient (str): The ID of the recipient.
            category (str): The category of the mail.
            package (Any): The content of the mail.
            request_source (Any, optional): The source of the request.
                Defaults to None.

        Returns:
            Mail: A new `Mail` object.
        """
        pack = Package(
            category=category, package=package, request_source=request_source
        )
        mail = Mail(
            sender=sender,
            recipient=recipient,
            package=pack,
        )
        return mail

    def delete_source(self, source_id: str) -> None:
        """
        Deletes a source from the `MailManager`.

        Args:
            source_id (str): The ID of the source to be deleted.

        Raises:
            ValueError: If the source ID does not exist.
        """
        if source_id not in self.sources:
            raise ValueError(f"Source {source_id} does not exist.")
        self.sources.pop(source_id)
        self.mails.pop(source_id)

    def collect(self, sender: str) -> None:
        """
        Collects mail from a specific sender.

        Args:
            sender (str): The ID of the sender to collect mail from.

        Raises:
            ValueError: If the sender or recipient does not exist.
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
        Sends mail to a specific recipient.

        Args:
            recipient (str): The ID of the recipient to send mail to.

        Raises:
            ValueError: If the recipient does not exist.
        """

        if recipient not in self.sources:
            raise ValueError(f"Recipient source {recipient} does not exist.")
        if not self.mails[recipient]:
            return
        for key in list(self.mails[recipient].keys()):
            pending_mails = self.mails[recipient].pop(key)
            mailbox: Exchange = (
                self.sources[recipient]
                if isinstance(self.sources[recipient], Exchange)
                else self.sources[recipient].mailbox
            )
            while pending_mails:
                mail = pending_mails.popleft()
                mailbox.include(mail, "in")

    def collect_all(self) -> None:
        """Collect mail from all sources."""
        for source in self.sources:
            self.collect(SysUtil.get_id(source))

    def send_all(self) -> None:
        """Send mail to all recipients."""
        for source in self.sources:
            self.send(SysUtil.get_id(source))

    async def execute(self, refresh_time: int = 1) -> None:
        """
        Executes the mail collection and sending process asynchronously.

        This method runs an infinite loop that repeatedly collects and sends
        mail at the specified refresh intervals until `execute_stop` is set to
        True.

        Args:
            refresh_time (int, optional): The time interval (in seconds)
                between each execution cycle. Defaults to 1 second.
        """
        while not self.execute_stop:
            self.collect_all()
            self.send_all()
            await asyncio.sleep(refresh_time)


# File: lion_core/communication/mail_manager.py
