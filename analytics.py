"""
analytics.py - Financial calculations and category breakdowns for Personal Expense Tracker.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from models import Transaction, TRANSACTION_TYPE_INCOME, TRANSACTION_TYPE_EXPENSE


@dataclass
class CategoryStat:
    category: str
    total_amount: float
    count: int
    percentage: float  # 0.0 to 100.0


@dataclass
class FinancialSummary:
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int
    expense_categories: List[CategoryStat]
    income_categories: List[CategoryStat]
    top_expense_category: str = "N/A"
    savings_rate: float = 0.0  # Percentage of income saved


def calculate_summary(transactions: List[Transaction]) -> FinancialSummary:
    """
    Computes financial metrics, totals, net balance, and category breakdowns.
    """
    total_income = 0.0
    total_expenses = 0.0

    expense_by_cat: Dict[str, Dict[str, Any]] = {}
    income_by_cat: Dict[str, Dict[str, Any]] = {}

    for t in transactions:
        if t.type == TRANSACTION_TYPE_INCOME:
            total_income += t.amount
            if t.category not in income_by_cat:
                income_by_cat[t.category] = {"total": 0.0, "count": 0}
            income_by_cat[t.category]["total"] += t.amount
            income_by_cat[t.category]["count"] += 1
        elif t.type == TRANSACTION_TYPE_EXPENSE:
            total_expenses += t.amount
            if t.category not in expense_by_cat:
                expense_by_cat[t.category] = {"total": 0.0, "count": 0}
            expense_by_cat[t.category]["total"] += t.amount
            expense_by_cat[t.category]["count"] += 1

    net_balance = total_income - total_expenses

    # Compute category statistics for expenses
    expense_stats: List[CategoryStat] = []
    for cat, info in expense_by_cat.items():
        pct = (info["total"] / total_expenses * 100.0) if total_expenses > 0 else 0.0
        expense_stats.append(
            CategoryStat(
                category=cat,
                total_amount=round(info["total"], 2),
                count=info["count"],
                percentage=round(pct, 1)
            )
        )
    # Sort expenses descending by total amount
    expense_stats.sort(key=lambda s: s.total_amount, reverse=True)

    # Compute category statistics for income
    income_stats: List[CategoryStat] = []
    for cat, info in income_by_cat.items():
        pct = (info["total"] / total_income * 100.0) if total_income > 0 else 0.0
        income_stats.append(
            CategoryStat(
                category=cat,
                total_amount=round(info["total"], 2),
                count=info["count"],
                percentage=round(pct, 1)
            )
        )
    income_stats.sort(key=lambda s: s.total_amount, reverse=True)

    top_expense = expense_stats[0].category if expense_stats else "N/A"
    savings_rate = (net_balance / total_income * 100.0) if total_income > 0 else 0.0

    return FinancialSummary(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_balance=round(net_balance, 2),
        transaction_count=len(transactions),
        expense_categories=expense_stats,
        income_categories=income_stats,
        top_expense_category=top_expense,
        savings_rate=round(savings_rate, 1)
    )


def generate_ascii_bar(percentage: float, width: int = 20) -> str:
    """
    Renders a text-based progress bar for percentages (0 - 100%).
    Example: [##########..........]  50.0%
    """
    clamped_pct = max(0.0, min(100.0, percentage))
    filled_len = int(round((clamped_pct / 100.0) * width))
    bar = "#" * filled_len + "." * (width - filled_len)
    return f"[{bar}] {clamped_pct:>5.1f}%"

