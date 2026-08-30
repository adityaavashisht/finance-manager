# transaction_adapter.py

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory

class TransactionAdapter:
    """Adapts a third-party transaction into the app's Transaction interface."""

    # Maps the vocabulary used by external providers onto our own categories.
    _CATEGORY_BY_EXTERNAL_TYPE = {
        "income": TransactionCategory.INCOME,
        "expense": TransactionCategory.EXPENSE,
    }

    def __init__(self, external_transaction):
        self.external_transaction = external_transaction

    def to_transaction(self):
        """Convert an external transaction to a standard Transaction."""
        external_type = str(self.external_transaction.typ).lower()
        try:
            category = self._CATEGORY_BY_EXTERNAL_TYPE[external_type]
        except KeyError:
            raise ValueError(
                f"Unsupported external transaction type: "
                f"{self.external_transaction.typ!r}"
            ) from None
        return Transaction(self.external_transaction.amount, category)