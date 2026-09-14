"""
models.py - Data models for Personal Expense Tracker.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


TRANSACTION_TYPE_INCOME = "income"
TRANSACTION_TYPE_EXPENSE = "expense"
VALID_TRANSACTION_TYPES = (TRANSACTION_TYPE_INCOME, TRANSACTION_TYPE_EXPENSE)


@dataclass
class Transaction:
    id: int
    date: str  # Format: YYYY-MM-DD
    type: str  # "income" or "expense"
    category: str
    amount: float
    description: str = ""

    def __post_init__(self):
        # Validate type
        normalized_type = self.type.strip().lower()
        if normalized_type not in VALID_TRANSACTION_TYPES:
            raise ValueError(f"Invalid transaction type '{self.type}'. Must be 'income' or 'expense'.")
        self.type = normalized_type

        # Validate amount
        try:
            self.amount = float(self.amount)
        except (ValueError, TypeError):
            raise ValueError(f"Amount must be a numeric value, got: {self.amount}")

        if self.amount <= 0:
            raise ValueError(f"Amount must be a positive number greater than 0, got: {self.amount}")

        # Validate category
        cleaned_category = self.category.strip()
        if not cleaned_category:
            raise ValueError("Category cannot be empty.")
        self.category = cleaned_category.title()

        # Validate and clean description
        self.description = self.description.strip() if self.description else ""

        # Validate date
        cleaned_date = self.date.strip()
        try:
            datetime.strptime(cleaned_date, "%Y-%m-%d")
            self.date = cleaned_date
        except ValueError:
            raise ValueError(f"Invalid date format '{self.date}'. Expected YYYY-MM-DD.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to a dictionary suitable for JSON serialization."""
        return {
            "id": self.id,
            "date": self.date,
            "type": self.type,
            "category": self.category,
            "amount": round(self.amount, 2),
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """Construct a Transaction instance from a dictionary."""
        return cls(
            id=int(data["id"]),
            date=str(data["date"]),
            type=str(data["type"]),
            category=str(data["category"]),
            amount=float(data["amount"]),
            description=str(data.get("description", ""))
        )
