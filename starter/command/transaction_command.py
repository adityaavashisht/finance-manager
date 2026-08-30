# transaction_command.py

class ICommand:
    """Interface for an operation that can be executed and undone."""

    def execute(self):
        """Perform the operation."""
        raise NotImplementedError("Subclasses must implement execute method.")

    def undo(self):
        """Reverse the operation."""
        raise NotImplementedError("Subclasses must implement undo method.")


class ApplyTransactionCommand(ICommand):
    """Applies one Transaction to an injected Balance, and can take it back."""

    def __init__(self, balance, transaction):
        self.balance = balance
        self.transaction = transaction

    def execute(self):
        self.balance.apply_transaction(self.transaction)

    def undo(self):
        self.balance.revert_transaction(self.transaction)

    def __str__(self):
        return f"ApplyTransactionCommand({self.transaction})"

    __repr__ = __str__