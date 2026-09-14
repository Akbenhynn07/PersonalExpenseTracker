"""
test_tracker.py - Automated Unit & Integration Tests for Personal Expense Tracker.
"""

import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime

from models import Transaction, TRANSACTION_TYPE_INCOME, TRANSACTION_TYPE_EXPENSE
from storage import StorageManager
from analytics import calculate_summary, generate_ascii_bar


class TestTransactionModel(unittest.TestCase):
    def test_valid_transaction(self):
        tx = Transaction(
            id=1,
            date="2026-09-14",
            type="expense",
            category="Groceries",
            amount=45.50,
            description="Weekly supermarket trip"
        )
        self.assertEqual(tx.id, 1)
        self.assertEqual(tx.amount, 45.50)
        self.assertEqual(tx.type, "expense")
        self.assertEqual(tx.category, "Groceries")

    def test_transaction_type_normalization(self):
        tx = Transaction(id=1, date="2026-09-14", type="  INCOME ", category="Salary", amount=3000.0)
        self.assertEqual(tx.type, "income")

    def test_invalid_type_raises_error(self):
        with self.assertRaises(ValueError):
            Transaction(id=1, date="2026-09-14", type="investment", category="Stocks", amount=100.0)

    def test_negative_or_zero_amount_raises_error(self):
        with self.assertRaises(ValueError):
            Transaction(id=1, date="2026-09-14", type="expense", category="Food", amount=0.0)
        with self.assertRaises(ValueError):
            Transaction(id=1, date="2026-09-14", type="expense", category="Food", amount=-25.0)

    def test_empty_category_raises_error(self):
        with self.assertRaises(ValueError):
            Transaction(id=1, date="2026-09-14", type="expense", category="   ", amount=10.0)

    def test_invalid_date_format_raises_error(self):
        with self.assertRaises(ValueError):
            Transaction(id=1, date="14-09-2026", type="expense", category="Food", amount=10.0)
        with self.assertRaises(ValueError):
            Transaction(id=1, date="not-a-date", type="expense", category="Food", amount=10.0)

    def test_to_dict_and_from_dict(self):
        tx = Transaction(
            id=42,
            date="2026-09-14",
            type="income",
            category="Freelance",
            amount=750.25,
            description="Client web development"
        )
        d = tx.to_dict()
        reconstructed = Transaction.from_dict(d)
        self.assertEqual(tx, reconstructed)


class TestStorageManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_expenses.json")
        self.storage = StorageManager(self.test_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_load_nonexistent_file(self):
        transactions = self.storage.load_transactions()
        self.assertEqual(transactions, [])

    def test_save_and_load_transactions(self):
        tx1 = Transaction(id=1, date="2026-09-14", type="income", category="Salary", amount=3500.0)
        tx2 = Transaction(id=2, date="2026-09-14", type="expense", category="Rent", amount=1200.0)
        
        self.storage.save_transactions([tx1, tx2])
        loaded = self.storage.load_transactions()

        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].id, 1)
        self.assertEqual(loaded[0].amount, 3500.0)
        self.assertEqual(loaded[1].category, "Rent")

    def test_add_transaction_and_id_generation(self):
        self.assertEqual(self.storage.get_next_id(), 1)
        tx1 = Transaction(id=self.storage.get_next_id(), date="2026-09-14", type="expense", category="Food", amount=20.0)
        self.storage.add_transaction(tx1)

        self.assertEqual(self.storage.get_next_id(), 2)
        tx2 = Transaction(id=self.storage.get_next_id(), date="2026-09-14", type="expense", category="Coffee", amount=5.0)
        self.storage.add_transaction(tx2)

        loaded = self.storage.load_transactions()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[1].id, 2)

    def test_delete_transaction(self):
        tx1 = Transaction(id=1, date="2026-09-14", type="income", category="Salary", amount=3000.0)
        tx2 = Transaction(id=2, date="2026-09-14", type="expense", category="Food", amount=50.0)
        self.storage.save_transactions([tx1, tx2])

        deleted = self.storage.delete_transaction(1)
        self.assertTrue(deleted)

        remaining = self.storage.load_transactions()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].id, 2)

        # Deleting nonexistent ID returns False
        self.assertFalse(self.storage.delete_transaction(999))

    def test_corrupted_json_recovery(self):
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("{ this is invalid json content ]]]")

        loaded = self.storage.load_transactions()
        self.assertEqual(loaded, [])
        # Verify a backup was created
        backups = [f for f in os.listdir(self.test_dir) if "corrupt" in f]
        self.assertTrue(len(backups) > 0)


class TestAnalytics(unittest.TestCase):
    def test_empty_summary(self):
        summary = calculate_summary([])
        self.assertEqual(summary.total_income, 0.0)
        self.assertEqual(summary.total_expenses, 0.0)
        self.assertEqual(summary.net_balance, 0.0)
        self.assertEqual(summary.transaction_count, 0)
        self.assertEqual(summary.expense_categories, [])
        self.assertEqual(summary.income_categories, [])

    def test_summary_calculations_and_breakdown(self):
        txs = [
            Transaction(id=1, date="2026-09-10", type="income", category="Salary", amount=5000.0),
            Transaction(id=2, date="2026-09-11", type="income", category="Freelance", amount=1000.0),
            Transaction(id=3, date="2026-09-12", type="expense", category="Rent", amount=1500.0),
            Transaction(id=4, date="2026-09-13", type="expense", category="Food", amount=300.0),
            Transaction(id=5, date="2026-09-14", type="expense", category="Food", amount=200.0),
        ]

        summary = calculate_summary(txs)
        self.assertEqual(summary.total_income, 6000.0)
        self.assertEqual(summary.total_expenses, 2000.0)
        self.assertEqual(summary.net_balance, 4000.0)
        self.assertEqual(summary.transaction_count, 5)
        self.assertEqual(summary.top_expense_category, "Rent")
        self.assertAlmostEqual(summary.savings_rate, 66.7, places=1)

        # Rent should be 1500 / 2000 = 75.0%
        # Food should be (300+200) / 2000 = 500 / 2000 = 25.0%
        self.assertEqual(len(summary.expense_categories), 2)
        self.assertEqual(summary.expense_categories[0].category, "Rent")
        self.assertEqual(summary.expense_categories[0].total_amount, 1500.0)
        self.assertEqual(summary.expense_categories[0].percentage, 75.0)

        self.assertEqual(summary.expense_categories[1].category, "Food")
        self.assertEqual(summary.expense_categories[1].total_amount, 500.0)
        self.assertEqual(summary.expense_categories[1].count, 2)
        self.assertEqual(summary.expense_categories[1].percentage, 25.0)

    def test_ascii_bar_generation(self):
        bar_50 = generate_ascii_bar(50.0, width=10)
        self.assertIn("#####.....", bar_50)
        self.assertIn("50.0%", bar_50)



if __name__ == "__main__":
    unittest.main()
