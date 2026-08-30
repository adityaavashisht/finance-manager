import unittest

from balance.balance import Balance
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class BalanceTestCase(unittest.TestCase):
    """Shared fixture: the singleton balance, reset and observer-free."""

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()

    def tearDown(self):
        self.balance.clear_observers()
        self.balance.reset()


class TestBalanceSingleton(BalanceTestCase):

    def test_get_instance_always_returns_same_object(self):
        self.assertIs(Balance.get_instance(), Balance.get_instance())

    def test_direct_instantiation_is_blocked(self):
        Balance.get_instance()  # guarantee the singleton already exists
        with self.assertRaises(RuntimeError):
            Balance()

    def test_state_is_shared_across_handles(self):
        first = Balance.get_instance()
        second = Balance.get_instance()
        first.add_income(25)
        self.assertEqual(second.get_balance(), 25)

    def test_summary_formats_to_two_decimals(self):
        self.balance.add_income(1375)
        self.assertEqual(self.balance.summary(), "Net balance: $1375.00")


class TestRevertTransaction(BalanceTestCase):

    def test_revert_income_subtracts(self):
        txn = Transaction(300, TransactionCategory.INCOME)
        self.balance.apply_transaction(txn)
        self.balance.revert_transaction(txn)
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_revert_expense_adds_back(self):
        txn = Transaction(75, TransactionCategory.EXPENSE)
        self.balance.apply_transaction(txn)
        self.assertEqual(self.balance.get_balance(), -75)

        self.balance.revert_transaction(txn)
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_revert_invalid_category_raises(self):
        class FakeCategory:
            pass

        with self.assertRaises(ValueError):
            self.balance.revert_transaction(Transaction(10, FakeCategory()))


if __name__ == "__main__":
    unittest.main()
