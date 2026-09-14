"""
storage.py - Data persistence layer for Personal Expense Tracker.
Handles saving and loading transactions to/from a local JSON file (expenses.json).
"""

import json
import os
import shutil
from datetime import datetime
from typing import List, Optional
from models import Transaction


DEFAULT_STORAGE_FILE = "expenses.json"


class StorageManager:
    """Manages persistent JSON storage of transactions."""

    def __init__(self, filepath: str = DEFAULT_STORAGE_FILE):
        self.filepath = filepath

    def load_transactions(self) -> List[Transaction]:
        """
        Loads transactions from the JSON file.
        Gracefully handles non-existent files, empty files, and corrupted data.
        """
        if not os.path.exists(self.filepath):
            return []

        if os.path.getsize(self.filepath) == 0:
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            if not isinstance(raw_data, list):
                self._backup_corrupted_file()
                return []

            transactions = []
            for item in raw_data:
                try:
                    transactions.append(Transaction.from_dict(item))
                except (ValueError, KeyError, TypeError):
                    # Skip malformed items or ignore invalid entries
                    continue

            return transactions

        except (json.JSONDecodeError, OSError):
            self._backup_corrupted_file()
            return []

    def save_transactions(self, transactions: List[Transaction]) -> None:
        """
        Saves a list of Transaction objects to the JSON file.
        Uses formatted JSON with 2-space indentation.
        """
        data = [t.to_dict() for t in transactions]

        # Write to a temporary file first for atomic-like safety
        temp_filepath = f"{self.filepath}.tmp"
        try:
            with open(temp_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Replace actual file
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            os.rename(temp_filepath, self.filepath)
        except OSError:
            # Fallback to direct write if renaming fails
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except OSError:
                    pass

    def add_transaction(self, transaction: Transaction) -> None:
        """Appends a new transaction and saves it to disk."""
        transactions = self.load_transactions()
        transactions.append(transaction)
        self.save_transactions(transactions)

    def delete_transaction(self, transaction_id: int) -> bool:
        """Deletes a transaction by ID. Returns True if found and deleted, False otherwise."""
        transactions = self.load_transactions()
        initial_count = len(transactions)
        transactions = [t for t in transactions if t.id != transaction_id]
        if len(transactions) < initial_count:
            self.save_transactions(transactions)
            return True
        return False

    def get_next_id(self) -> int:
        """Computes the next auto-incrementing transaction ID."""
        transactions = self.load_transactions()
        if not transactions:
            return 1
        return max(t.id for t in transactions) + 1

    def clear_all(self) -> None:
        """Clears all transactions and updates the storage file."""
        self.save_transactions([])

    def _backup_corrupted_file(self) -> None:
        """Creates a backup of corrupted JSON file to prevent complete data loss."""
        if os.path.exists(self.filepath):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.filepath}.corrupt_{timestamp}.bak"
            try:
                shutil.copyfile(self.filepath, backup_path)
            except OSError:
                pass
