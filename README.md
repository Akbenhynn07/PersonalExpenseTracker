# Personal Expense Tracker (CLI)

A lightweight, robust, and interactive Command-Line Personal Expense Tracker built in Python. Effortlessly log daily income and expenses, view structured transaction histories, analyze financial health with category-wise visual summaries, and reliably persist data across sessions using local JSON storage.

---

## Project Demo Video

> **Watch the 1–2 minute walkthrough video below** demonstrating:
> 1. Adding sample income and expense transactions with live input validation.
> 2. Generating the summary report with percentage breakdown bars.
> 3. Closing and restarting the application to verify that data persists seamlessly in `expenses.json`.

https://github.com/user-attachments/assets/4e6c80d0-f63b-4a5e-95de-e1653f9cd190

```
=============================================================
             PERSONAL EXPENSE TRACKER CLI v1.0               
=============================================================

--- MAIN MENU ---
 [1] [+] Add Transaction (Income / Expense)
 [2] [=] View Transaction History
 [3] [%] Summary & Category Breakdown Report
 [4] [?] Search & Filter Transactions
 [5] [x] Delete a Transaction
 [6] [i] View Data File Info
 [7] [q] Exit
```
---

## Key Features

- **Transaction Management**: Record transactions with amount, type (`income` or `expense`), category, date (defaults to today `YYYY-MM-DD`), and optional notes.
- **Tabular History View**: Clean, aligned ASCII table output displaying ID, Date, Type, Category, Amount (color-coded green for income, red for expenses), and Description.
- **Financial Analytics & Visual Breakdowns**:
  - Calculates Total Income, Total Expenses, Net Balance (Surplus/Deficit), and Savings Rate.
  - Generates spending and earnings breakdown by category sorted by amount with visual ASCII progress bars (`[#####.....] 50.0%`).
- **Automatic Data Persistence**: Automatically loads from and writes to `expenses.json`. Data is immediately saved after any addition or deletion, ensuring zero data loss across restarts.
- **Graceful Input Validation**:
  - Rejects zero and negative amounts without crashing.
  - Enforces non-empty category names and provides recommended preset categories + custom entry.
  - Validates date formats (`YYYY-MM-DD`).
  - Handles invalid menu choices and unexpected input loops gracefully.
  - Protects against corrupted storage files with automatic timestamped backup recovery.
- **Zero External Dependencies**: Powered purely by the Python 3 standard library (`json`, `datetime`, `dataclasses`, `os`, `sys`). Runs instantly on Windows, macOS, and Linux without needing `pip install`.

---

## Repository Structure

```
Personal Expense Tracker/
│
├── main.py              # Application entry point
├── cli.py               # Interactive CLI interface, menu loops & formatting
├── models.py            # Transaction dataclass & business validation logic
├── storage.py           # Persistent JSON storage manager (expenses.json)
├── analytics.py         # Financial calculations, metrics & ASCII progress bar generator
├── seed_sample_data.py  # Utility to populate sample income and expense data
├── test_tracker.py      # Automated unit & integration test suite (15 tests)
├── requirements.txt     # Dependency declaration (Standard Library - zero dependencies)
├── expenses.json        # Persistent data storage file (created automatically)
├── .gitignore           # Git ignore file for temporary & cache files
└── README.md            # Comprehensive project documentation
```

---

## Getting Started

### Prerequisites
- Python 3.8 or higher installed on your system.
- Check your installation:
  ```bash
  python --version
  ```

### Installation
1. Clone this repository or download the project files:
   ```bash
   git clone https://github.com/Akbenhynn07/PersonalExpenseTracker.git
   cd PersonalExpenseTracker
   ```


2. (Optional) Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Since this application relies entirely on the Python Standard Library, no external packages are required!*

---

## How to Run the Application

Start the interactive CLI:
```bash
python main.py
```

### Quick Demo with Sample Data
To pre-populate `expenses.json` with realistic sample transactions for instant demonstration:
```bash
python seed_sample_data.py
python main.py
```

---

## Walkthrough & Sample Usage

### 1. Adding a Transaction (Income or Expense)
Select `1` from the main menu:
```text
--- ADD NEW TRANSACTION ---
Select Transaction Type:
  [1] [-] Expense
  [2] [+] Income
? Enter choice (1/2 or 'e'/'i'): 1
? Enter Amount (₹): 1250.00

Select Category:
  [1] Food & Dining
  [2] Groceries
  [3] Rent & Housing
  [4] Utilities & Bills
  [5] Transportation
  [6] Entertainment
  [7] Shopping
  [8] Health & Fitness
  [9] Education
  [10] Travel
  [11] Other Expense
  [0] Custom Category (type your own)
? Choose category number (or type name): 1
? Date (YYYY-MM-DD) [Enter for 2026-09-14]: 
? Description / Note [Optional]: Dinner with friends

[OK] Transaction added successfully!
  ID: 1 | Date: 2026-09-14 | EXPENSE: ₹1250.00 | Category: Food & Dining
```

---

### 2. Viewing History
Select `2` to display all recorded transactions:
```text
====================================================================================
 ALL TRANSACTIONS (8 total)
====================================================================================
 ID   | Date       | Type     | Category           |     Amount (₹) | Description       
------------------------------------------------------------------------------------
 1    | 2026-09-01 | +INCOME  | Salary             | +₹   75000.00 | Monthly Salary    
 2    | 2026-09-02 | -EXPENSE | Rent & Housing     | -₹   18000.00 | Apartment rent    
 3    | 2026-09-03 | -EXPENSE | Groceries          | -₹    4500.00 | Monthly superma...
 4    | 2026-09-05 | -EXPENSE | Utilities & Bills  | -₹    1850.00 | Electricity & b...
 5    | 2026-09-07 | +INCOME  | Freelance & Con... | +₹   15000.00 | Web design project
 6    | 2026-09-08 | -EXPENSE | Food & Dining      | -₹    1250.00 | Weekend dinner ...
 7    | 2026-09-10 | -EXPENSE | Transportation     | -₹     800.00 | Metro recharge ...
 8    | 2026-09-12 | -EXPENSE | Entertainment      | -₹     699.00 | OTT streaming s...
====================================================================================
```

---

### 3. Running the Summary Report
Select `3` to calculate financial metrics and category breakdowns:
```text
=============================================================
                FINANCIAL SUMMARY REPORT
=============================================================
 Total Transactions Recorded : 8
 Total Income Received       : +₹90,000.00
 Total Expenses Spent        : -₹27,099.00
 Net Balance Remaining       : +₹62,901.00 (Surplus (Healthy))
 Savings Rate                : 69.9%
 Top Expense Category        : Rent & Housing
-------------------------------------------------------------

[-] EXPENSE BREAKDOWN BY CATEGORY:
 Category               | Count |    Total (₹) | Visual Proportion           
--------------------------------------------------------------------------
 Rent & Housing         | 1     | ₹   18000.00 | [##########.....]  66.4%
 Groceries              | 1     | ₹    4500.00 | [##.............]  16.6%
 Utilities & Bills      | 1     | ₹    1850.00 | [#..............]   6.8%
 Food & Dining          | 1     | ₹    1250.00 | [#..............]   4.6%
 Transportation         | 1     | ₹     800.00 | [...............]   3.0%
 Entertainment          | 1     | ₹     699.00 | [...............]   2.6%

[+] INCOME BREAKDOWN BY CATEGORY:
 Category               | Count |    Total (₹) | Visual Proportion           
--------------------------------------------------------------------------
 Salary                 | 1     | ₹   75000.00 | [############...]  83.3%
 Freelance & Consulting | 1     | ₹   15000.00 | [###............]  16.7%

=============================================================
```

---

### 4. Data Persistence Across Restarts
1. Add any transaction or run `seed_sample_data.py`.
2. Exit the program with `7` (`q`).
3. Re-run `python main.py` and choose `2` (View History) or `3` (Summary Report).
4. All transactions and calculated balances remain preserved intact inside `expenses.json`.

Example structure of `expenses.json`:
```json
[
  {
    "id": 1,
    "date": "2026-09-01",
    "type": "income",
    "category": "Salary",
    "amount": 75000.0,
    "description": "Monthly Salary"
  },
  {
    "id": 2,
    "date": "2026-09-02",
    "type": "expense",
    "category": "Rent & Housing",
    "amount": 18000.0,
    "description": "Apartment rent"
  }
]
```


---

## Running Automated Tests

A comprehensive suite of 15 automated unit and integration tests is included in `test_tracker.py`.

To run the test suite:
```bash
python -m unittest test_tracker.py -v
```

### Test Coverage Highlights:
- **Models**: Validates transaction initialization, positive amount constraints, non-empty category names, valid date formats, and dictionary conversion.
- **Storage**: Verifies file creation, saving, reloading across fresh storage instances, auto-incrementing ID sequences, transaction deletion, and automatic corrupted-file recovery.
- **Analytics**: Verifies net balance calculation, savings rate math, expense/income category percentage calculations, descending ranking, and ASCII bar generation.

---

## Input Validation & Edge Case Handling

| Input Scenario | Program Behavior |
|---|---|
| **Negative or Zero Amount (`-50`, `0`)** | Displays error message and prompts again without crashing. |
| **Non-Numeric Amount (`abc`, `$100`)** | Gracefully reprompts for valid numeric float. |
| **Empty Category (`""`)** | Prompts for a non-empty name or selection. |
| **Invalid Date Format (`14/09/2026`)** | Prompts for standard `YYYY-MM-DD` format. |
| **Invalid Menu Option (`99`, `foo`)** | Displays invalid choice warning and displays main menu again. |
| **Corrupted `expenses.json` File** | Backs up the corrupted file with a timestamp and starts clean. |
| **Empty Storage File** | Returns empty transaction list without raising `JSONDecodeError`. |

---

## License
This project is open-source and available under the [MIT License](LICENSE).
