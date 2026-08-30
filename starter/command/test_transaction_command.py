import unittest

from balance.balance import Balance
from command.transaction_command import ApplyTransactionCommand, ICommand
from command.transaction_invoker import TransactionInvoker
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class CommandTestCase(unittest.TestCase):
    """Shared fixture: a clean, observer-free singleton balance."""

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()
        self.invoker = TransactionInvoker()

    def tearDown(self):
        self.balance.clear_observers()
        self.balance.reset()

    def make_command(self, amount, category):
        return ApplyTransactionCommand(self.balance, Transaction(amount, category))


class TestApplyTransactionCommand(CommandTestCase):

    def test_execute_applies_transaction(self):
        self.make_command(100, TransactionCategory.INCOME).execute()
        self.assertEqual(self.balance.get_balance(), 100)

    def test_undo_reverses_execute(self):
        command = self.make_command(100, TransactionCategory.EXPENSE)
        command.execute()
        command.undo()
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_command_uses_the_injected_balance(self):
        """The command must not reach for the global singleton itself."""

        class FakeBalance:
            def __init__(self):
                self.applied = []
                self.reverted = []

            def apply_transaction(self, transaction):
                self.applied.append(transaction)

            def revert_transaction(self, transaction):
                self.reverted.append(transaction)

        fake = FakeBalance()
        txn = Transaction(10, TransactionCategory.INCOME)
        command = ApplyTransactionCommand(fake, txn)

        command.execute()
        command.undo()

        self.assertEqual(fake.applied, [txn])
        self.assertEqual(fake.reverted, [txn])
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_interface_requires_implementation(self):
        with self.assertRaises(NotImplementedError):
            ICommand().execute()
        with self.assertRaises(NotImplementedError):
            ICommand().undo()


class TestTransactionInvoker(CommandTestCase):

    def test_run_executes_and_records_history(self):
        command = self.make_command(100, TransactionCategory.INCOME)
        self.invoker.run(command)

        self.assertEqual(self.balance.get_balance(), 100)
        self.assertEqual(self.invoker.history, (command,))
        self.assertTrue(self.invoker.can_undo())
        self.assertFalse(self.invoker.can_redo())

    def test_undo_then_redo_restores_balance(self):
        self.invoker.run(self.make_command(100, TransactionCategory.INCOME))
        self.invoker.run(self.make_command(30, TransactionCategory.EXPENSE))
        self.assertEqual(self.balance.get_balance(), 70)

        self.invoker.undo()
        self.assertEqual(self.balance.get_balance(), 100)

        self.invoker.redo()
        self.assertEqual(self.balance.get_balance(), 70)

    def test_undo_unwinds_in_reverse_order(self):
        self.invoker.run(self.make_command(100, TransactionCategory.INCOME))
        self.invoker.run(self.make_command(40, TransactionCategory.EXPENSE))

        self.invoker.undo()
        self.invoker.undo()

        self.assertEqual(self.balance.get_balance(), 0.0)
        self.assertEqual(self.invoker.history, ())

    def test_running_a_new_command_clears_the_redo_stack(self):
        self.invoker.run(self.make_command(100, TransactionCategory.INCOME))
        self.invoker.undo()
        self.assertTrue(self.invoker.can_redo())

        self.invoker.run(self.make_command(500, TransactionCategory.INCOME))

        self.assertFalse(self.invoker.can_redo())
        self.assertIsNone(self.invoker.redo())
        self.assertEqual(self.balance.get_balance(), 500)

    def test_undo_and_redo_are_safe_when_empty(self):
        self.assertIsNone(self.invoker.undo())
        self.assertIsNone(self.invoker.redo())
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_history_is_an_immutable_snapshot(self):
        self.invoker.run(self.make_command(100, TransactionCategory.INCOME))
        self.assertIsInstance(self.invoker.history, tuple)


if __name__ == "__main__":
    unittest.main()
