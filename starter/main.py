"""This module serves as the entry point for the program."""
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from balance.balance_observer import PrintObserver
from command.transaction_command import ApplyTransactionCommand
from command.transaction_invoker import TransactionInvoker
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_adapter import TransactionAdapter
from transaction.external_income_transaction import ExternalFreelanceIncome

LOW_BALANCE_THRESHOLD = 100


def main():
    print("Adding transactions...")

    # Singleton: one shared balance, plus Observers wired in via injection.
    balance = Balance.get_instance()
    balance.register_observer(PrintObserver())
    balance.register_observer(LowBalanceAlertObserver(LOW_BALANCE_THRESHOLD))

    # Create standard transactions
    transactions = [
        Transaction(100, TransactionCategory.INCOME),
        Transaction(50, TransactionCategory.EXPENSE),
        Transaction(200, TransactionCategory.INCOME),
        Transaction(75, TransactionCategory.EXPENSE),
    ]

    # Create an external income transaction (via Adapter pattern)
    freelance_income = ExternalFreelanceIncome(1200, "INV-98765", "Mobile App Project")
    adapter = TransactionAdapter(freelance_income)
    adapted_transaction = adapter.to_transaction()

    all_transactions = transactions + [adapted_transaction]

    # Command: every transaction goes through the invoker, so it stays undoable.
    invoker = TransactionInvoker()
    for transaction in all_transactions:
        invoker.run(ApplyTransactionCommand(balance, transaction))

    print(f"\n{balance.summary()}")

    print("\nUndoing the last transaction (the freelance invoice)...")
    invoker.undo()
    print(balance.summary())

    print("\nRedoing it...")
    invoker.redo()
    print(balance.summary())


if __name__ == "__main__":
    main()