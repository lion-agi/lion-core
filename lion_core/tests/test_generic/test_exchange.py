import pytest
from unittest.mock import Mock

from lion_core.generic.pile import Pile
from lion_core.generic.progression import Progression
from lion_core.communication.mail import Mail
from lion_core.communication.package import Package
from lion_core.generic.exchange import Exchange


class TestExchange:

    @pytest.fixture
    def mock_mail(self):
        return Mock(spec=Mail)

    @pytest.fixture
    def exchange(self):
        return Exchange()

    def test_initialization(self, exchange):
        assert isinstance(exchange.pile, Pile)
        assert isinstance(exchange.pending_ins, dict)
        assert isinstance(exchange.pending_outs, Progression)
        assert len(exchange) == 0
        assert not exchange

    def test_include_incoming_mail(self, exchange, mock_mail):
        mock_mail.sender = "sender1"
        exchange.include(mock_mail, "in")
        assert mock_mail in exchange.pile
        assert "sender1" in exchange.pending_ins
        assert mock_mail in exchange.pending_ins["sender1"]

    def test_include_outgoing_mail(self, exchange, mock_mail):
        exchange.include(mock_mail, "out")
        assert mock_mail in exchange.pile
        assert mock_mail in exchange.pending_outs

    def test_include_invalid_direction(self, exchange, mock_mail):
        with pytest.raises(ValueError):
            exchange.include(mock_mail, "invalid")

    def test_include_duplicate_mail(self, exchange, mock_mail):
        exchange.include(mock_mail, "in")
        with pytest.raises(Exception):  # Specific exception type should be used
            exchange.include(mock_mail, "in")

    def test_exclude_mail(self, exchange, mock_mail):
        mock_mail.sender = "sender1"
        exchange.include(mock_mail, "in")
        exchange.exclude(mock_mail)
        assert mock_mail not in exchange.pile
        assert mock_mail not in exchange.pending_ins["sender1"]

    def test_contains(self, exchange, mock_mail):
        exchange.include(mock_mail, "in")
        assert mock_mail in exchange

    def test_len(self, exchange, mock_mail):
        assert len(exchange) == 0
        exchange.include(mock_mail, "in")
        assert len(exchange) == 1

    def test_bool(self, exchange, mock_mail):
        assert not exchange
        exchange.include(mock_mail, "in")
        assert exchange

    def test_senders_property(self, exchange):
        mail1 = Mock(spec=Mail, sender="sender1")
        mail2 = Mock(spec=Mail, sender="sender2")
        exchange.include(mail1, "in")
        exchange.include(mail2, "in")
        assert set(exchange.senders) == {"sender1", "sender2"}

    @pytest.mark.asyncio
    async def test_async_operations(self, exchange, mock_mail):
        await exchange.include(mock_mail, "in")
        assert mock_mail in exchange

    def test_invalid_mail_type(self, exchange):
        with pytest.raises(ValueError):
            exchange.include("not a mail", "in")

    @pytest.mark.parametrize("num_mails", [10, 100, 1000])
    def test_performance_with_many_mails(self, exchange, num_mails):
        mails = [Mock(spec=Mail, sender=f"sender{i}") for i in range(num_mails)]
        for mail in mails:
            exchange.include(mail, "in")
        assert len(exchange) == num_mails

    def test_consistency_between_pile_and_pending(self, exchange):
        mails = [Mock(spec=Mail, sender="sender1") for _ in range(5)]
        for mail in mails:
            exchange.include(mail, "in")
        assert set(exchange.pile) == set(exchange.pending_ins["sender1"])

    def test_exclude_nonexistent_mail(self, exchange, mock_mail):
        exchange.exclude(mock_mail)  # Should not raise an exception

    def test_multiple_senders(self, exchange):
        for i in range(5):
            mail = Mock(spec=Mail, sender=f"sender{i}")
            exchange.include(mail, "in")
        assert len(exchange.senders) == 5

    def test_incoming_outgoing_separation(self, exchange):
        in_mail = Mock(spec=Mail, sender="sender1")
        out_mail = Mock(spec=Mail, sender="sender1")
        exchange.include(in_mail, "in")
        exchange.include(out_mail, "out")
        assert in_mail in exchange.pending_ins["sender1"]
        assert out_mail in exchange.pending_outs
        assert in_mail not in exchange.pending_outs
        assert out_mail not in exchange.pending_ins["sender1"]

    @pytest.mark.parametrize("direction", ["in", "out"])
    def test_order_preservation(self, exchange, direction):
        mails = [Mock(spec=Mail, sender="sender1") for _ in range(5)]
        for mail in mails:
            exchange.include(mail, direction)
        if direction == "in":
            assert list(exchange.pending_ins["sender1"]) == mails
        else:
            assert list(exchange.pending_outs) == mails

    def test_exclude_updates_all_collections(self, exchange):
        mail = Mock(spec=Mail, sender="sender1")
        exchange.include(mail, "in")
        exchange.exclude(mail)
        assert mail not in exchange.pile
        assert mail not in exchange.pending_ins["sender1"]
        assert mail not in exchange.pending_outs

    def test_include_with_different_package_types(self, exchange):
        mail_types = [
            "MESSAGE",
            "TOOL",
            "IMODEL",
            "NODE",
            "NODE_LIST",
            "NODE_ID",
            "START",
            "END",
            "CONDITION",
            "SIGNAL",
        ]
        for mail_type in mail_types:
            package = Package(category=mail_type, package="test")
            mail = Mail(sender="sender1", recipient="recipient1", package=package)
            exchange.include(mail, "in")
            assert mail in exchange

    def test_memory_usage(self, exchange):
        import sys

        initial_size = sys.getsizeof(exchange)
        for _ in range(1000):
            mail = Mock(spec=Mail, sender="sender1")
            exchange.include(mail, "in")
        final_size = sys.getsizeof(exchange)
        assert final_size > initial_size
        # You might want to set a reasonable threshold for size increase

    def test_thread_safety(self, exchange):
        import threading

        def add_mails():
            for _ in range(1000):
                mail = Mock(spec=Mail, sender="sender1")
                exchange.include(mail, "in")

        threads = [threading.Thread(target=add_mails) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(exchange) == 10000

    def test_error_handling(self, exchange):
        with pytest.raises(ValueError):
            exchange.include(None, "in")
        with pytest.raises(ValueError):
            exchange.include(Mock(spec=Mail), "invalid_direction")

    def test_custom_pile_and_progression(self, exchange):
        custom_pile = Pile()
        custom_progression = Progression()
        custom_exchange = Exchange(pile=custom_pile, pending_outs=custom_progression)
        assert custom_exchange.pile is custom_pile
        assert custom_exchange.pending_outs is custom_progression

    def test_subclass_compatibility(self, exchange):
        class CustomMail(Mail):
            pass

        custom_mail = CustomMail(
            sender="sender1",
            recipient="recipient1",
            package=Package(category="MESSAGE", package="test"),
        )
        exchange.include(custom_mail, "in")
        assert custom_mail in exchange


# Path: tests/test_generic/test_exchange.py
