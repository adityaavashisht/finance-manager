import unittest
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction_adapter import TransactionAdapter
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory

class TestTransactionAdapter(unittest.TestCase):

    def test_adapter_converts_freelance_income(self):
        ext_txn = ExternalFreelanceIncome(500, "INV-12345", "Website development")
        adapter = TransactionAdapter(ext_txn)
        txn = adapter.to_transaction()
        self.assertEqual(txn, Transaction(500, TransactionCategory.INCOME))

class TestTransactionAdapterEdgeCases(unittest.TestCase):

    def test_adapter_maps_expense_type_case_insensitively(self):
        class ExternalExpense:
            def __init__(self):
                self.amount = 42
                self.typ = "EXPENSE"

        txn = TransactionAdapter(ExternalExpense()).to_transaction()
        self.assertEqual(txn, Transaction(42, TransactionCategory.EXPENSE))

    def test_adapter_rejects_unknown_type(self):
        class ExternalRefund:
            def __init__(self):
                self.amount = 10
                self.typ = "refund"

        with self.assertRaises(ValueError):
            TransactionAdapter(ExternalRefund()).to_transaction()

    def test_adapter_drops_provider_only_fields(self):
        ext = ExternalFreelanceIncome(500, "INV-12345", "Website development")
        txn = TransactionAdapter(ext).to_transaction()

        self.assertFalse(hasattr(txn, "invoice_id"))
        self.assertFalse(hasattr(txn, "description"))


if __name__ == "__main__":
    unittest.main()
