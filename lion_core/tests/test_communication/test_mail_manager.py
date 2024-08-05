import pytest
import asyncio
from collections import deque
from unittest.mock import MagicMock, patch
from lion_core.communication.mail_manager import MailManager
from lion_core.generic.pile import Pile
from lion_core.generic.exchange import Exchange
from lion_core.communication.mail import Mail
from lion_core.communication.package import Package, PackageCategory


# Helper functions and fixtures
@pytest.fixture
def mock_source():
    source = MagicMock()
    source.ln_id = "source_id"
    source.mailbox = Exchange()
    return source


@pytest.fixture
def mail_manager(mock_source):
    manager = MailManager([mock_source])
    return manager


def create_mock_mail(sender, recipient, category, content):
    package = Package(category=category, package=content)
    return Mail(sender=sender, recipient=recipient, package=package)


# Basic functionality tests
def test_mail_manager_init():
    manager = MailManager()
    assert isinstance(manager.sources, Pile)
    assert isinstance(manager.mails, dict)
    assert manager.execute_stop is False


def test_mail_manager_add_sources(mail_manager, mock_source):
    new_source = MagicMock()
    new_source.ln_id = "new_source_id"
    mail_manager.add_sources(new_source)
    assert "new_source_id" in mail_manager.mails
    assert len(mail_manager.sources) == 2


def test_mail_manager_create_mail():
    mail = MailManager.create_mail("sender", "recipient", "category", "content")
    assert isinstance(mail, Mail)
    assert mail.sender == "sender"
    assert mail.recipient == "recipient"
    assert mail.package.category == "category"
    assert mail.package.package == "content"


def test_mail_manager_delete_source(mail_manager, mock_source):
    mail_manager.delete_source(mock_source.ln_id)
    assert mock_source.ln_id not in mail_manager.sources
    assert mock_source.ln_id not in mail_manager.mails


def test_mail_manager_collect(mail_manager, mock_source):
    mock_mail = create_mock_mail("sender", mock_source.ln_id, "category", "content")
    mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect(mock_source.ln_id)
    assert len(mail_manager.mails[mock_source.ln_id]["sender"]) == 1


def test_mail_manager_send(mail_manager, mock_source):
    mock_mail = create_mock_mail("sender", mock_source.ln_id, "category", "content")
    mail_manager.mails[mock_source.ln_id] = {"sender": deque([mock_mail])}
    mail_manager.send(mock_source.ln_id)
    assert len(mock_source.mailbox.pile) == 1


def test_mail_manager_collect_all(mail_manager, mock_source):
    mock_mail = create_mock_mail("sender", mock_source.ln_id, "category", "content")
    mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect_all()
    assert len(mail_manager.mails[mock_source.ln_id]["sender"]) == 1


def test_mail_manager_send_all(mail_manager, mock_source):
    mock_mail = create_mock_mail("sender", mock_source.ln_id, "category", "content")
    mail_manager.mails[mock_source.ln_id] = {"sender": deque([mock_mail])}
    mail_manager.send_all()
    assert len(mock_source.mailbox.pile) == 1


@pytest.mark.asyncio
async def test_mail_manager_execute(mail_manager):
    with patch.object(mail_manager, "collect_all") as mock_collect_all, patch.object(
        mail_manager, "send_all"
    ) as mock_send_all:
        mail_manager.execute_stop = False
        task = asyncio.create_task(mail_manager.execute(refresh_time=0.1))
        await asyncio.sleep(0.3)
        mail_manager.execute_stop = True
        await task
        assert mock_collect_all.call_count >= 2
        assert mock_send_all.call_count >= 2


# Edge cases and additional tests
def test_mail_manager_add_invalid_source():
    manager = MailManager()
    with pytest.raises(ValueError):
        manager.add_sources("invalid_source")


def test_mail_manager_delete_nonexistent_source(mail_manager):
    with pytest.raises(ValueError):
        mail_manager.delete_source("nonexistent_id")


def test_mail_manager_collect_nonexistent_sender(mail_manager):
    with pytest.raises(ValueError):
        mail_manager.collect("nonexistent_sender")


def test_mail_manager_send_nonexistent_recipient(mail_manager):
    with pytest.raises(ValueError):
        mail_manager.send("nonexistent_recipient")


def test_mail_manager_collect_with_nonexistent_recipient(mail_manager, mock_source):
    mock_mail = create_mock_mail("sender", "nonexistent", "category", "content")
    mock_source.mailbox.include(mock_mail, "out")
    with pytest.raises(ValueError):
        mail_manager.collect(mock_source.ln_id)


def test_mail_manager_send_empty_mail_queue(mail_manager, mock_source):
    mail_manager.send(mock_source.ln_id)
    assert len(mock_source.mailbox.pile) == 0


def test_mail_manager_large_number_of_sources():
    large_number = 1000
    sources = [MagicMock(ln_id=f"source_{i}") for i in range(large_number)]
    manager = MailManager(sources)
    assert len(manager.sources) == large_number
    assert len(manager.mails) == large_number


def test_mail_manager_large_number_of_mails(mail_manager, mock_source):
    large_number = 1000
    for i in range(large_number):
        mock_mail = create_mock_mail(
            f"sender_{i}", mock_source.ln_id, "category", f"content_{i}"
        )
        mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect(mock_source.ln_id)
    assert (
        sum(len(queue) for queue in mail_manager.mails[mock_source.ln_id].values())
        == large_number
    )


def test_mail_manager_multiple_senders_same_recipient(mail_manager, mock_source):
    senders = ["sender1", "sender2", "sender3"]
    for sender in senders:
        mock_mail = create_mock_mail(sender, mock_source.ln_id, "category", "content")
        mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect(mock_source.ln_id)
    assert len(mail_manager.mails[mock_source.ln_id]) == len(senders)


def test_mail_manager_collect_and_send_cycle(mail_manager, mock_source):
    mock_mail = create_mock_mail("sender", mock_source.ln_id, "category", "content")
    mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect_all()
    assert len(mail_manager.mails[mock_source.ln_id]["sender"]) == 1
    mail_manager.send_all()
    assert len(mock_source.mailbox.pile) == 1
    assert len(mail_manager.mails[mock_source.ln_id]) == 0


@pytest.mark.asyncio
async def test_mail_manager_execute_with_interruption(mail_manager):
    async def interrupt():
        await asyncio.sleep(0.2)
        mail_manager.execute_stop = True

    with patch.object(mail_manager, "collect_all") as mock_collect_all, patch.object(
        mail_manager, "send_all"
    ) as mock_send_all:
        interrupt_task = asyncio.create_task(interrupt())
        await mail_manager.execute(refresh_time=0.1)
        await interrupt_task
        assert mock_collect_all.call_count > 0
        assert mock_send_all.call_count > 0


def test_mail_manager_with_various_package_categories(mail_manager, mock_source):
    categories = list(PackageCategory)
    for category in categories:
        mock_mail = create_mock_mail("sender", mock_source.ln_id, category, "content")
        mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect(mock_source.ln_id)
    assert len(mail_manager.mails[mock_source.ln_id]["sender"]) == len(categories)


def test_mail_manager_with_custom_exchange(mail_manager):
    custom_exchange = Exchange()
    custom_source = MagicMock(ln_id="custom_source")
    mail_manager.add_sources(custom_source)
    mail_manager.sources["custom_source"] = custom_exchange
    mock_mail = create_mock_mail("sender", "custom_source", "category", "content")
    custom_exchange.include(mock_mail, "out")
    mail_manager.collect("custom_source")
    assert len(mail_manager.mails["custom_source"]["sender"]) == 1


# Performance test
@pytest.mark.asyncio
async def test_mail_manager_performance():
    large_number = 10000
    sources = [MagicMock(ln_id=f"source_{i}", mailbox=Exchange()) for i in range(100)]
    manager = MailManager(sources)

    for source in sources:
        for i in range(large_number // 100):
            mock_mail = create_mock_mail(
                "sender", source.ln_id, "category", f"content_{i}"
            )
            source.mailbox.include(mock_mail, "out")

    start_time = asyncio.get_event_loop().time()
    await manager.execute(refresh_time=0)
    end_time = asyncio.get_event_loop().time()

    assert (
        end_time - start_time < 5
    )  # Should process 10,000 mails in less than 5 seconds


# Thread safety test
@pytest.mark.asyncio
async def test_mail_manager_thread_safety():
    manager = MailManager()
    source = MagicMock(ln_id="source", mailbox=Exchange())
    manager.add_sources(source)

    async def add_and_collect():
        for _ in range(100):
            mock_mail = create_mock_mail("sender", "source", "category", "content")
            source.mailbox.include(mock_mail, "out")
        manager.collect("source")

    tasks = [asyncio.create_task(add_and_collect()) for _ in range(10)]
    await asyncio.gather(*tasks)

    total_mails = sum(len(queue) for queue in manager.mails["source"].values())
    assert total_mails == 1000  # 10 tasks * 100 mails each


# Test with invalid UTF-8 sequences
def test_mail_manager_with_invalid_utf8(mail_manager, mock_source):
    invalid_utf8 = b"Invalid UTF-8: \xff"
    with pytest.raises(UnicodeDecodeError):
        create_mock_mail(
            "sender", mock_source.ln_id, "category", invalid_utf8.decode("utf-8")
        )


# Test mail manager with very large mail content
def test_mail_manager_with_large_mail_content(mail_manager, mock_source):
    large_content = "a" * 1000000  # 1MB of content
    mock_mail = create_mock_mail("sender", mock_source.ln_id, "category", large_content)
    mock_source.mailbox.include(mock_mail, "out")
    mail_manager.collect(mock_source.ln_id)
    assert len(mail_manager.mails[mock_source.ln_id]["sender"]) == 1
    assert (
        len(mail_manager.mails[mock_source.ln_id]["sender"][0].package.package)
        == 1000000
    )
