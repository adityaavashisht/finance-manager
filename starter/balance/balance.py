# balance.py

from transaction.transaction_category import TransactionCategory

class Balance:
    """Singleton to track the balance."""

    _instance = None

    def __init__(self):
        """Initialize the balance. Prevent direct instantiation."""
        if Balance._instance is not None:
            raise RuntimeError(
                "Balance is a singleton; use Balance.get_instance() instead."
            )
        self._net_balance = 0.0
        self._observers = []
        Balance._instance = self

    @classmethod
    def get_instance(cls):
        """Return the one and only Balance instance, creating it on first use."""
        if cls._instance is None:
            cls()
        return cls._instance

    # --- Observer registry ------------------------------------------------

    def register_observer(self, observer):
        """Subscribe an observer to balance changes."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer):
        """Unsubscribe a previously registered observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def clear_observers(self):
        """Detach every observer."""
        self._observers.clear()

    def _notify_observers(self, transaction):
        """Push the new balance to every registered observer."""
        for observer in self._observers:
            observer.update(self._net_balance, transaction)

    # --- Balance state ----------------------------------------------------

    def reset(self):
        """Reset the net balance to zero."""
        self._net_balance = 0.0

    def add_income(self, amount):
        """Add income to the balance."""
        self._net_balance += amount

    def add_expense(self, amount):
        """Subtract expense from the balance."""
        self._net_balance -= amount

    def apply_transaction(self, transaction):
        """
        Apply a Transaction object to update the balance.

        Args:
            transaction (Transaction): The transaction to apply.
        """
        self._apply(transaction, reverse=False)

    def revert_transaction(self, transaction):
        """Undo a previously applied transaction and notify observers."""
        self._apply(transaction, reverse=True)

    def _apply(self, transaction, reverse):
        """Apply a transaction in either direction, then notify observers."""
        if transaction.category is TransactionCategory.INCOME:
            is_credit = not reverse
        elif transaction.category is TransactionCategory.EXPENSE:
            is_credit = reverse
        else:
            raise ValueError(
                f"Unknown transaction category: {transaction.category!r}"
            )

        if is_credit:
            self.add_income(transaction.amount)
        else:
            self.add_expense(transaction.amount)

        self._notify_observers(transaction)

    def get_balance(self):
        """Get the current net balance."""
        return self._net_balance

    def summary(self):
        """Return a summary string of the net balance."""
        return f"Net balance: ${self._net_balance:.2f}"
    
