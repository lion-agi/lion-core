import pytest
from lion_core.generic.pile import Pile
from lion_core.generic.progression import Progression
from lion_core.generic.exchange import Exchange
from lion_core.communication.package import Package, PackageCategory
from lion_core.exceptions import ItemExistsError, LionValueError
from lion_core.sys_utils import SysUtil
from lion_core.communication.mail import Mail


def create_mail(sender, recipient, package_category, package):
    package = Package(category=package_category, package=package)
    return Mail(sender=sender, recipient=recipient, package=package)


@pytest.fixture
def exchange():
    return Exchange()


@pytest.fixture
def mock_mail():
    return create_mail(
        sender=SysUtil.id(),
        recipient=SysUtil.id(),
        package=Package(category=PackageCategory.MESSAGE, package="test content"),
    )


def test_exchange_init(exchange):
    assert isinstance(exchange.pile, Pile)
    assert isinstance(exchange.pending_ins, dict)
    assert isinstance(exchange.pending_outs, Progression)


def test_include_incoming_mail(exchange, mock_mail):
    exchange.include(mock_mail, "in")
    assert mock_mail in exchange.pile
    assert mock_mail.sender in exchange.pending_ins
    assert mock_mail in exchange.pending_ins[mock_mail.sender]


def test_include_outgoing_mail(exchange, mock_mail):
    exchange.include(mock_mail, "out")
    assert mock_mail in exchange.pile
    assert mock_mail in exchange.pending_outs


def test_include_duplicate_mail(exchange, mock_mail):
    exchange.include(mock_mail, "in")
    with pytest.raises(ItemExistsError):
        exchange.include(mock_mail, "in")


def test_include_invalid_direction(exchange, mock_mail):
    with pytest.raises(LionValueError):
        exchange.include(mock_mail, "invalid")


def test_include_invalid_item(exchange):
    with pytest.raises(LionValueError):
        exchange.include("not a mail", "in")


def test_exclude_mail(exchange, mock_mail):
    exchange.include(mock_mail, "in")
    exchange.exclude(mock_mail)
    assert mock_mail not in exchange.pile
    assert mock_mail not in exchange.pending_ins[mock_mail.sender]


def test_contains(exchange, mock_mail):
    assert mock_mail not in exchange
    exchange.include(mock_mail, "in")
    assert mock_mail in exchange


def test_len(exchange, mock_mail):
    assert len(exchange) == 0
    exchange.include(mock_mail, "in")
    assert len(exchange) == 1


def test_bool(exchange, mock_mail):
    assert not exchange
    exchange.include(mock_mail, "in")
    assert exchange


def test_senders_property(exchange):
    mail1 = create_mail(SysUtil.id(), SysUtil.id(), PackageCategory.MESSAGE, "test1")
    mail2 = create_mail(SysUtil.id(), SysUtil.id(), PackageCategory.MESSAGE, "test2")
    exchange.include(mail1, "in")
    exchange.include(mail2, "in")
    assert set(exchange.senders) == {mail1.sender, mail2.sender}


@pytest.mark.asyncio
async def test_async_operations(exchange, mock_mail):
    await exchange.include(mock_mail, "in")
    assert mock_mail in exchange


@pytest.mark.parametrize("num_mails", [10, 100, 1000])
def test_performance_with_many_mails(exchange, num_mails):
    mails = [
        Mail(SysUtil.id(), SysUtil.id(), Package(PackageCategory.MESSAGE, f"test{i}"))
        for i in range(num_mails)
    ]
    for mail in mails:
        exchange.include(mail, "in")
    assert len(exchange) == num_mails


def test_consistency_between_pile_and_pending(exchange):
    mails = [
        Mail(SysUtil.id(), SysUtil.id(), Package(PackageCategory.MESSAGE, f"test{i}"))
        for i in range(5)
    ]
    for mail in mails:
        exchange.include(mail, "in")
    assert len(exchange.pile) == len(mails)
    assert len(exchange.pending_ins[mails[0].sender]) == len(mails)


def test_exclude_nonexistent_mail(exchange, mock_mail):
    exchange.exclude(mock_mail)  # Should not raise an exception


def test_multiple_senders(exchange):
    for i in range(5):
        mail = Mail(
            SysUtil.id(), SysUtil.id(), Package(PackageCategory.MESSAGE, f"test{i}")
        )
        exchange.include(mail, "in")
    assert len(exchange.senders) == 5


def test_incoming_outgoing_separation(exchange):
    in_mail = Mail(SysUtil.id(), SysUtil.id(), Package(PackageCategory.MESSAGE, "in"))
    out_mail = Mail(SysUtil.id(), SysUtil.id(), Package(PackageCategory.MESSAGE, "out"))
    exchange.include(in_mail, "in")
    exchange.include(out_mail, "out")
    assert in_mail in exchange.pending_ins[in_mail.sender]
    assert out_mail in exchange.pending_outs


@pytest.mark.parametrize("direction", ["in", "out"])
def test_order_preservation(exchange, direction):
    mails = [
        Mail(SysUtil.id(), SysUtil.id(), Package(PackageCategory.MESSAGE, f"test{i}"))
        for i in range(5)
    ]
    for mail in mails:
        exchange.include(mail, direction)
    if direction == "in":
        assert list(exchange.pending_ins[mails[0].sender]) == mails
    else:
        assert list(exchange.pending_outs) == mails


def test_exclude_updates_all_collections(exchange):
    mail = Mail(SysUtil.id(), SysUtil.id(), Package(PackageCategory.MESSAGE, "test"))
    exchange.include(mail, "in")
    exchange.include(mail, "out")
    exchange.exclude(mail)
    assert mail not in exchange.pile
    assert mail not in exchange.pending_ins[mail.sender]
    assert mail not in exchange.pending_outs


def test_include_with_different_package_types(exchange):
    for category in PackageCategory:
        mail = Mail(SysUtil.id(), SysUtil.id(), Package(category, "test"))
        exchange.include(mail, "in")
        assert mail in exchange


def test_memory_usage(exchange):
    import sys

    initial_size = sys.getsizeof(exchange)
    for _ in range(1000):
        mail = Mail(
            SysUtil.id(), SysUtil.id(), Package(PackageCategory.MESSAGE, "test")
        )
        exchange.include(mail, "in")
    final_size = sys.getsizeof(exchange)
    assert final_size > initial_size


def test_thread_safety(exchange):
    import threading

    def add_mails():
        for _ in range(1000):
            mail = Mail(
                SysUtil.id(), SysUtil.id(), Package(PackageCategory.MESSAGE, "test")
            )
            exchange.include(mail, "in")

    threads = [threading.Thread(target=add_mails) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(exchange) == 10000


def test_subclass_compatibility(exchange):
    class CustomMail(BaseMail):
        def __init__(self, sender, recipient, package):
            super().__init__(
                sender=SysUtil.id(),
                recipient=SysUtil.id(),
                package=package,
            )

    custom_mail = CustomMail(
        sender=SysUtil.id(),
        recipient=SysUtil.id(),
        package=Package(category=PackageCategory.MESSAGE, package="test"),
    )
    exchange.include(custom_mail, "in")
    assert custom_mail in exchange
