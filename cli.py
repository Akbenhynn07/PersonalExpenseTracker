"""
cli.py - User Interface and Input Validation for Personal Expense Tracker.
"""

import sys
import os
from datetime import datetime
from typing import List, Optional

from models import Transaction, TRANSACTION_TYPE_INCOME, TRANSACTION_TYPE_EXPENSE
from storage import StorageManager, DEFAULT_STORAGE_FILE
from analytics import calculate_summary, generate_ascii_bar, FinancialSummary


# Terminal color styling codes
class Style:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


# Enable ANSI colors and UTF-8 on Windows
def init_terminal():
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            pass
    if os.name == "nt":
        os.system("")  # Enables ANSI escape sequences in Windows Command Prompt/PowerShell



def colorize(text: str, color_code: str) -> str:
    """Helper to wrap text in ANSI colors."""
    return f"{color_code}{text}{Style.RESET}"


# Currency Configuration
CURRENCY_SYMBOL = "₹"

COMMON_EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Rent & Housing",
    "Utilities & Bills",
    "Transportation",
    "Entertainment",
    "Shopping",
    "Health & Fitness",
    "Education",
    "Travel",
    "Other Expense"
]

COMMON_INCOME_CATEGORIES = [
    "Salary",
    "Freelance & Consulting",
    "Business",
    "Investments & Dividends",
    "Gifts & Bonus",
    "Other Income"
]


class ExpenseTrackerCLI:
    def __init__(self, storage: Optional[StorageManager] = None):
        self.storage = storage if storage is not None else StorageManager(DEFAULT_STORAGE_FILE)
        init_terminal()

    # ---------------- Input Helpers with Graceful Validation ----------------

    def prompt_positive_float(self, prompt_text: str) -> float:
        """Prompts for a numeric value and guarantees it is > 0."""
        while True:
            try:
                user_input = input(f"{colorize('?', Style.CYAN)} {prompt_text}: ").strip()
                if not user_input:
                    print(colorize("  [!] Amount cannot be empty. Please enter a valid number.", Style.RED))
                    continue
                amount = float(user_input)
                if amount <= 0:
                    print(colorize("  [!] Amount must be a positive number greater than 0.", Style.RED))
                    continue
                return round(amount, 2)
            except ValueError:
                print(colorize("  [!] Invalid input. Please enter a numeric amount (e.g. 500.00).", Style.RED))

    def prompt_transaction_type(self) -> str:
        """Prompts the user to select Income or Expense."""
        print(f"\n{colorize('Select Transaction Type:', Style.BOLD)}")
        print(f"  [{colorize('1', Style.CYAN)}] [-] Expense")
        print(f"  [{colorize('2', Style.CYAN)}] [+] Income")
        while True:
            choice = input(f"{colorize('?', Style.CYAN)} Enter choice (1/2 or 'e'/'i'): ").strip().lower()
            if choice in ("1", "e", "exp", "expense"):
                return TRANSACTION_TYPE_EXPENSE
            elif choice in ("2", "i", "inc", "income"):
                return TRANSACTION_TYPE_INCOME
            else:
                print(colorize("  [!] Invalid choice. Please enter 1 for Expense or 2 for Income.", Style.RED))

    def prompt_category(self, tx_type: str) -> str:
        """Prompts user to select from recommended categories or enter a custom one."""
        suggestions = COMMON_EXPENSE_CATEGORIES if tx_type == TRANSACTION_TYPE_EXPENSE else COMMON_INCOME_CATEGORIES
        print(f"\n{colorize('Select Category:', Style.BOLD)}")
        for idx, cat in enumerate(suggestions, 1):
            print(f"  [{colorize(str(idx), Style.CYAN)}] {cat}")
        print(f"  [{colorize('0', Style.CYAN)}] Custom Category (type your own)")

        while True:
            choice = input(f"{colorize('?', Style.CYAN)} Choose category number (or type name): ").strip()
            if not choice:
                print(colorize("  [!] Category cannot be empty.", Style.RED))
                continue

            if choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(suggestions):
                    return suggestions[num - 1]
                elif num == 0:
                    while True:
                        custom_cat = input(f"{colorize('?', Style.CYAN)} Enter custom category name: ").strip()
                        if custom_cat:
                            return custom_cat.title()
                        print(colorize("  [!] Category name cannot be empty.", Style.RED))
                else:
                    print(colorize(f"  [!] Please select a number between 0 and {len(suggestions)}.", Style.RED))
            else:
                # User typed a category name directly
                return choice.title()

    def prompt_date(self) -> str:
        """Prompts for a date with default to today (YYYY-MM-DD)."""
        today_str = datetime.today().strftime("%Y-%m-%d")
        while True:
            date_input = input(f"{colorize('?', Style.CYAN)} Date (YYYY-MM-DD) [{colorize('Enter for ' + today_str, Style.DIM)}]: ").strip()
            if not date_input:
                return today_str
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                return date_input
            except ValueError:
                print(colorize("  [!] Invalid date format or date does not exist. Use YYYY-MM-DD (e.g. 2026-09-14).", Style.RED))

    def prompt_description(self) -> str:
        """Prompts for an optional description."""
        desc = input(f"{colorize('?', Style.CYAN)} Description / Note [{colorize('Optional', Style.DIM)}]: ").strip()
        return desc

    # ---------------- Display Formats ----------------

    def print_banner(self):
        """Displays the application banner."""
        banner = f"""
{Style.CYAN}=============================================================
             PERSONAL EXPENSE TRACKER CLI v1.0               
============================================================={Style.RESET}"""
        print(banner)

    def print_menu(self):
        """Displays the main menu options."""
        print(f"\n{colorize('--- MAIN MENU ---', Style.BOLD)}")
        print(f" [{colorize('1', Style.CYAN)}] [+] Add Transaction (Income / Expense)")
        print(f" [{colorize('2', Style.CYAN)}] [=] View Transaction History")
        print(f" [{colorize('3', Style.CYAN)}] [%] Summary & Category Breakdown Report")
        print(f" [{colorize('4', Style.CYAN)}] [?] Search & Filter Transactions")
        print(f" [{colorize('5', Style.CYAN)}] [x] Delete a Transaction")
        print(f" [{colorize('6', Style.CYAN)}] [i] View Data File Info")
        print(f" [{colorize('7', Style.CYAN)}] [q] Exit")

    def display_transactions_table(self, transactions: List[Transaction], title: str = "TRANSACTION HISTORY"):
        """Prints transactions in a clean, aligned tabular format."""
        if not transactions:
            print(f"\n{colorize('[i] No transactions found.', Style.YELLOW)}")
            return

        print(f"\n{colorize('=' * 84, Style.CYAN)}")
        print(f" {colorize(title, Style.BOLD)} ({len(transactions)} total)")
        print(f"{colorize('=' * 84, Style.CYAN)}")

        # Table header
        header = f" {'ID':<4} | {'Date':<10} | {'Type':<8} | {'Category':<18} | {f'Amount ({CURRENCY_SYMBOL})':>14} | {'Description':<18}"
        print(colorize(header, Style.BOLD))
        print(colorize("-" * 84, Style.DIM))

        for t in transactions:
            type_label = t.type.upper()
            if t.type == TRANSACTION_TYPE_INCOME:
                type_display = colorize(f"+{type_label:<7}", Style.GREEN)
                amount_display = colorize(f"+{CURRENCY_SYMBOL}{t.amount:>11.2f}", Style.GREEN)
            else:
                type_display = colorize(f"-{type_label:<7}", Style.RED)
                amount_display = colorize(f"-{CURRENCY_SYMBOL}{t.amount:>11.2f}", Style.RED)

            desc_truncated = (t.description[:15] + "...") if len(t.description) > 18 else t.description
            category_truncated = (t.category[:15] + "...") if len(t.category) > 18 else t.category

            print(f" {t.id:<4} | {t.date:<10} | {type_display} | {category_truncated:<18} | {amount_display} | {desc_truncated:<18}")

        print(colorize("=" * 84, Style.CYAN))

    def display_summary_report(self):
        """Calculates and renders a comprehensive summary and category breakdown."""
        transactions = self.storage.load_transactions()
        if not transactions:
            print(f"\n{colorize('[i] No transactions recorded yet. Add transactions first to view summary.', Style.YELLOW)}")
            return

        summary: FinancialSummary = calculate_summary(transactions)

        print(f"\n{colorize('=============================================================', Style.CYAN)}")
        print(f"                {colorize('FINANCIAL SUMMARY REPORT', Style.BOLD)}")
        print(f"{colorize('=============================================================', Style.CYAN)}")
        print(f" Total Transactions Recorded : {summary.transaction_count}")
        print(f" Total Income Received       : {colorize(f'+{CURRENCY_SYMBOL}{summary.total_income:,.2f}', Style.GREEN)}")
        print(f" Total Expenses Spent        : {colorize(f'-{CURRENCY_SYMBOL}{summary.total_expenses:,.2f}', Style.RED)}")

        if summary.net_balance >= 0:
            net_str = colorize(f"+{CURRENCY_SYMBOL}{summary.net_balance:,.2f}", Style.GREEN + Style.BOLD)
            status_str = colorize("Surplus (Healthy)", Style.GREEN)
        else:
            net_str = colorize(f"-{CURRENCY_SYMBOL}{abs(summary.net_balance):,.2f}", Style.RED + Style.BOLD)
            status_str = colorize("Deficit (Spending exceeds income)", Style.RED)

        print(f" Net Balance Remaining       : {net_str} ({status_str})")
        if summary.total_income > 0:
            print(f" Savings Rate                : {summary.savings_rate:.1f}%")
        print(f" Top Expense Category        : {colorize(summary.top_expense_category, Style.BOLD)}")
        print(f"{colorize('-------------------------------------------------------------', Style.CYAN)}")

        # Expense Breakdown by Category
        print(f"\n{colorize('[-] EXPENSE BREAKDOWN BY CATEGORY:', Style.BOLD)}")
        if not summary.expense_categories:
            print("  No expense transactions recorded.")
        else:
            print(f" {'Category':<22} | {'Count':<5} | {f'Total ({CURRENCY_SYMBOL})':>12} | {'Visual Proportion':<28}")
            print(colorize("-" * 74, Style.DIM))
            for cat in summary.expense_categories:
                bar = generate_ascii_bar(cat.percentage, width=15)
                print(f" {cat.category:<22} | {cat.count:<5} | {CURRENCY_SYMBOL}{cat.total_amount:>11.2f} | {bar}")

        # Income Breakdown by Category
        print(f"\n{colorize('[+] INCOME BREAKDOWN BY CATEGORY:', Style.BOLD)}")
        if not summary.income_categories:
            print("  No income transactions recorded.")
        else:
            print(f" {'Category':<22} | {'Count':<5} | {f'Total ({CURRENCY_SYMBOL})':>12} | {'Visual Proportion':<28}")
            print(colorize("-" * 74, Style.DIM))
            for cat in summary.income_categories:
                bar = generate_ascii_bar(cat.percentage, width=15)
                print(f" {cat.category:<22} | {cat.count:<5} | {CURRENCY_SYMBOL}{cat.total_amount:>11.2f} | {bar}")

        print(f"\n{colorize('=============================================================', Style.CYAN)}")

    # ---------------- Feature Handlers ----------------

    def handle_add_transaction(self):
        """Walks user through adding a transaction with live validation."""
        print(f"\n{colorize('--- ADD NEW TRANSACTION ---', Style.BOLD)}")
        tx_type = self.prompt_transaction_type()
        amount = self.prompt_positive_float(f"Enter Amount ({CURRENCY_SYMBOL})")
        category = self.prompt_category(tx_type)
        date = self.prompt_date()
        description = self.prompt_description()

        next_id = self.storage.get_next_id()
        tx = Transaction(
            id=next_id,
            date=date,
            type=tx_type,
            category=category,
            amount=amount,
            description=description
        )

        self.storage.add_transaction(tx)
        print(f"\n{colorize('[OK] Transaction added successfully!', Style.GREEN)}")
        print(f"  ID: {tx.id} | Date: {tx.date} | {tx.type.upper()}: {CURRENCY_SYMBOL}{tx.amount:.2f} | Category: {tx.category}")


    def handle_view_history(self):
        """Displays all recorded transactions."""
        transactions = self.storage.load_transactions()
        self.display_transactions_table(transactions, "ALL TRANSACTIONS")

    def handle_filter_transactions(self):
        """Search and filter transactions by type, category, or keyword."""
        transactions = self.storage.load_transactions()
        if not transactions:
            print(f"\n{colorize('[i] No transactions available to search.', Style.YELLOW)}")
            return

        print(f"\n{colorize('--- SEARCH & FILTER TRANSACTIONS ---', Style.BOLD)}")
        print(" 1. Filter by Type (Income / Expense)")
        print(" 2. Filter by Category")
        print(" 3. Search in Description / Notes")
        choice = input(f"{colorize('?', Style.CYAN)} Enter filter choice (1-3): ").strip()

        if choice == "1":
            tx_type = self.prompt_transaction_type()
            filtered = [t for t in transactions if t.type == tx_type]
            self.display_transactions_table(filtered, f"FILTERED BY TYPE: {tx_type.upper()}")
        elif choice == "2":
            keyword = input(f"{colorize('?', Style.CYAN)} Enter category name to match: ").strip().lower()
            filtered = [t for t in transactions if keyword in t.category.lower()]
            self.display_transactions_table(filtered, f"FILTERED BY CATEGORY: '{keyword}'")
        elif choice == "3":
            keyword = input(f"{colorize('?', Style.CYAN)} Enter search keyword: ").strip().lower()
            filtered = [t for t in transactions if keyword in t.description.lower()]
            self.display_transactions_table(filtered, f"FILTERED BY KEYWORD: '{keyword}'")
        else:
            print(colorize("  [!] Invalid choice. Returning to main menu.", Style.RED))

    def handle_delete_transaction(self):
        """Allows deleting a transaction by its ID."""
        transactions = self.storage.load_transactions()
        if not transactions:
            print(f"\n{colorize('[i] No transactions to delete.', Style.YELLOW)}")
            return

        self.display_transactions_table(transactions, "SELECT TRANSACTION TO DELETE")
        while True:
            id_input = input(f"\n{colorize('?', Style.CYAN)} Enter Transaction ID to delete (or 'c' to cancel): ").strip()
            if id_input.lower() == 'c':
                print("Deletion cancelled.")
                return
            if not id_input.isdigit():
                print(colorize("  [!] Please enter a valid integer ID.", Style.RED))
                continue

            tx_id = int(id_input)
            confirm = input(f"Are you sure you want to permanently delete Transaction #{tx_id}? (y/N): ").strip().lower()
            if confirm in ("y", "yes"):
                if self.storage.delete_transaction(tx_id):
                    print(colorize(f"[OK] Transaction #{tx_id} deleted successfully.", Style.GREEN))
                    return
                else:
                    print(colorize(f"  [!] Transaction #{tx_id} was not found.", Style.RED))
                    return
            else:
                print("Deletion cancelled.")
                return

    def handle_view_file_info(self):
        """Displays data persistence file location and status."""
        filepath = os.path.abspath(self.storage.filepath)
        exists = os.path.exists(filepath)
        size = os.path.getsize(filepath) if exists else 0
        tx_count = len(self.storage.load_transactions())

        print(f"\n{colorize('--- DATA PERSISTENCE STATUS ---', Style.BOLD)}")
        print(f" Storage File Path : {filepath}")
        print(f" File Exists       : {'Yes' if exists else 'No (Will be created on first transaction)'}")
        print(f" File Size         : {size} bytes")
        print(f" Records Saved     : {tx_count} transactions")

    # ---------------- Main Loop ----------------

    def run(self):
        """Main application execution loop."""
        self.print_banner()
        while True:
            try:
                self.print_menu()
                choice = input(f"\n{colorize('Select an option (1-7):', Style.BOLD)} ").strip()

                if choice == "1":
                    self.handle_add_transaction()
                elif choice == "2":
                    self.handle_view_history()
                elif choice == "3":
                    self.display_summary_report()
                elif choice == "4":
                    self.handle_filter_transactions()
                elif choice == "5":
                    self.handle_delete_transaction()
                elif choice == "6":
                    self.handle_view_file_info()
                elif choice in ("7", "exit", "quit", "q"):
                    print(f"\n{colorize('Thank you for using Personal Expense Tracker! Goodbye.', Style.GREEN)}\n")
                    break
                else:
                    print(colorize("  [!] Invalid choice. Please enter a number between 1 and 7.", Style.RED))

            except (KeyboardInterrupt, EOFError):
                print(f"\n\n{colorize('Session closed. Goodbye!', Style.GREEN)}\n")
                break
            except Exception as e:
                print(colorize(f"\n  [!] An unexpected error occurred: {e}", Style.RED))
                print("  Returning safely to the main menu...\n")

