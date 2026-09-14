"""
main.py - Entry point for Personal Expense Tracker CLI.
"""

import sys
from cli import ExpenseTrackerCLI


def main():
    cli = ExpenseTrackerCLI()
    cli.run()


if __name__ == "__main__":
    main()
