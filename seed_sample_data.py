import sys
from models import Transaction
from storage import StorageManager

# Ensure stdout supports UTF-8 on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass



def populate_demo_data():
    storage = StorageManager("expenses.json")
    
    sample_transactions = [
        Transaction(id=1, date="2026-09-01", type="income", category="Salary", amount=75000.00, description="Monthly Salary"),
        Transaction(id=2, date="2026-09-02", type="expense", category="Rent & Housing", amount=18000.00, description="Apartment rent"),
        Transaction(id=3, date="2026-09-03", type="expense", category="Groceries", amount=4500.00, description="Monthly supermarket groceries"),
        Transaction(id=4, date="2026-09-05", type="expense", category="Utilities & Bills", amount=1850.00, description="Electricity & broadband bill"),
        Transaction(id=5, date="2026-09-07", type="income", category="Freelance & Consulting", amount=15000.00, description="Web design project"),
        Transaction(id=6, date="2026-09-08", type="expense", category="Food & Dining", amount=1250.00, description="Weekend dinner with friends"),
        Transaction(id=7, date="2026-09-10", type="expense", category="Transportation", amount=800.00, description="Metro recharge & cab fares"),
        Transaction(id=8, date="2026-09-12", type="expense", category="Entertainment", amount=699.00, description="OTT streaming subscription"),
    ]

    storage.save_transactions(sample_transactions)
    print("✔ Successfully populated 'expenses.json' with 8 sample transactions (in ₹)!")
    print("  Run 'python main.py' to explore the transaction history and summary report.")



if __name__ == "__main__":
    populate_demo_data()
