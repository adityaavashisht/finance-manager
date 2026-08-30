import unittest

from balance.balance import Balance
from balance.balance_observer import (
    IBalanceObserver,
    LowBalanceAlertObserver,
    PrintObserver,
)
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class RecordingWriter:
    """Test double that captures messages instead of printing them."""

    def __init__(self):
        self.messages = []

    def __call__(self, message):
        self.messages.append(message)


class SpyObserver(IBalanceObserver):
    """Records every (balance, transaction) pair it is notified with."""

    def __init__(self):
        self.calls = []

    def update(self, balance, transaction):
        self.calls.append((balance, transaction))


class ObserverTestCase(unittest.TestCase):
    """Shared fixture: the shared singleton, reset and stripped of observers."""

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()

    def tearDown(self):
        self.balance.clear_observers()
        self.balance.reset()


class TestBalanceObserverRegistry(ObserverTestCase):

    def test_observer_receives_balance_and_transaction(self):
        spy = SpyObserver()
        self.balance.register_observer(spy)

        txn = Transaction(150, TransactionCategory.INCOME)
        self.balance.apply_transaction(txn)

        self.assertEqual(len(spy.calls), 1)
        notified_balance, notified_txn = spy.calls[0]
        self.assertEqual(notified_balance, 150)
        self.assertIs(notified_txn, txn)

    def test_registering_twice_notifies_once(self):
        spy = SpyObserver()
        self.balance.register_observer(spy)
        self.balance.register_observer(spy)

        self.balance.apply_transaction(Transaction(10, TransactionCategory.INCOME))

        self.assertEqual(len(spy.calls), 1)

    def test_unregister_stops_notifications(self):
        spy = SpyObserver()
        self.balance.register_observer(spy)
        self.balance.unregister_observer(spy)

        self.balance.apply_transaction(Transaction(10, TransactionCategory.INCOME))

        self.assertEqual(spy.calls, [])

    def test_clear_observers_detaches_all(self):
        first, second = SpyObserver(), SpyObserver()
        self.balance.register_observer(first)
        self.balance.register_observer(second)
        self.balance.clear_observers()

        self.balance.apply_transaction(Transaction(10, TransactionCategory.INCOME))

        self.assertEqual(first.calls, [])
        self.assertEqual(second.calls, [])

    def test_invalid_category_neither_notifies_nor_mutates(self):
        class FakeCategory:
            pass

        spy = SpyObserver()
        self.balance.register_observer(spy)

        with self.assertRaises(ValueError):
            self.balance.apply_transaction(Transaction(10, FakeCategory()))

        self.assertEqual(spy.calls, [])
        self.assertEqual(self.balance.get_balance(), 0.0)


class TestPrintObserver(ObserverTestCase):

    def test_prints_running_balance_on_each_transaction(self):
        writer = RecordingWriter()
        self.balance.register_observer(PrintObserver(writer=writer))

        self.balance.apply_transaction(Transaction(200, TransactionCategory.INCOME))
        self.balance.apply_transaction(Transaction(50, TransactionCategory.EXPENSE))

        self.assertEqual(len(writer.messages), 2)
        self.assertIn("$200.00", writer.messages[0])
        self.assertIn("$150.00", writer.messages[1])

    def test_default_writer_is_print(self):
        self.assertIs(PrintObserver().writer, print)


class TestLowBalanceAlertNotifier(ObserverTestCase):

    def test_notifier_only_fires_below_threshold(self):
        notifier = RecordingWriter()
        self.balance.register_observer(
            LowBalanceAlertObserver(threshold=100, notifier=notifier)
        )

        self.balance.apply_transaction(Transaction(500, TransactionCategory.INCOME))
        self.assertEqual(notifier.messages, [])

        self.balance.apply_transaction(Transaction(450, TransactionCategory.EXPENSE))
        self.assertEqual(len(notifier.messages), 1)
        self.assertIn("$50.00", notifier.messages[0])

    def test_flag_tracks_current_balance_and_does_not_latch(self):
        observer = LowBalanceAlertObserver(threshold=100, notifier=RecordingWriter())
        self.balance.register_observer(observer)

        self.balance.apply_transaction(Transaction(20, TransactionCategory.INCOME))
        self.assertTrue(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(200, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)


class TestObserverInterface(unittest.TestCase):

    def test_base_update_must_be_overridden(self):
        with self.assertRaises(NotImplementedError):
            IBalanceObserver().update(0, None)


if __name__ == "__main__":
    unittest.main()
