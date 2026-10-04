import csv
import datetime
import os
from abc import ABC, abstractmethod


# ==========================================
# 1. Custom Exceptions
# ==========================================
class TransactionNotFoundError(Exception):
    """Raised when an entry ID cannot be located."""
    pass


class DuplicateTransactionError(Exception):
    """Raised when registering an entry ID that already exists."""
    pass


class InvalidTransactionError(Exception):
    """Raised when monetary amounts or dates are invalid."""
    pass


# ==========================================
# 2. Abstraction: Base Class
# ==========================================
class Transaction(ABC):
    """Abstract base class representing any monetary entry."""

    def __init__(self, trans_id: str, date_str: str, category: str, amount: float, description: str):
        self._trans_id = trans_id  # Protected
        self._category = category
        self.set_date(date_str)
        self.set_amount(amount)
        self.set_description(description)

    @property
    def trans_id(self) -> str:
        return self._trans_id

    @property
    def category(self) -> str:
        return self._category

    @property
    def date_str(self) -> str:
        return self.__date_str

    def set_date(self, date_str: str):
        try:
            # Validate standard YYYY-MM-DD format
            datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d")
            self.__date_str = date_str.strip()
        except ValueError:
            raise InvalidTransactionError("Date must be formatted as YYYY-MM-DD.")

    @property
    def amount(self) -> float:
        return self.__amount

    def set_amount(self, value: float):
        if value <= 0:
            raise InvalidTransactionError("Amount must be strictly greater than zero.")
        self.__amount = round(value, 2)

    @property
    def description(self) -> str:
        return self.__description

    def set_description(self, desc: str):
        if not desc.strip():
            raise ValueError("Description cannot be blank.")
        self.__description = desc.strip()

    @abstractmethod
    def get_net_impact(self) -> float:
        """Returns signed numeric cash flow impact (+ for income, - for expense)."""
        pass

    @abstractmethod
    def get_details(self) -> str:
        """Returns formatted string summary of transaction."""
        pass


# ==========================================
# 3. Inheritance & Encapsulation: Subclasses
# ==========================================
class IncomeEntry(Transaction):
    """Cash inflow entry."""

    def get_net_impact(self) -> float:
        return self.amount

    def get_details(self) -> str:
        return (f"Type: Income  | ID: {self.trans_id:<6} | Date: {self.date_str} | "
                f"Category: {self.category:<12} | Amount: +₹{self.amount:<9.2f} | Note: {self.description}")


class ExpenseEntry(Transaction):
    """Cash outflow entry."""

    def get_net_impact(self) -> float:
        return -self.amount

    def get_details(self) -> str:
        return (f"Type: Expense | ID: {self.trans_id:<6} | Date: {self.date_str} | "
                f"Category: {self.category:<12} | Amount: -₹{self.amount:<9.2f} | Note: {self.description}")


# ==========================================
# 4. Management Class: ExpenseTracker
# ==========================================
class ExpenseTracker:
    """Coordinates transaction entries, summaries, search, and CSV persistence."""

    def __init__(self, filename: str = "expenses.csv"):
        self.filename = filename
        self.records: dict[str, Transaction] = {}
        self.load_from_file()

    def add_income(self, trans_id: str, date_str: str, category: str, amount: float, desc: str):
        if trans_id in self.records:
            raise DuplicateTransactionError(f"Transaction ID '{trans_id}' already exists.")
        entry = IncomeEntry(trans_id, date_str, category, amount, desc)
        self.records[trans_id] = entry
        print(f"✓ Income of ₹{amount:.2f} logged under '{category}'.")

    def add_expense(self, trans_id: str, date_str: str, category: str, amount: float, desc: str):
        if trans_id in self.records:
            raise DuplicateTransactionError(f"Transaction ID '{trans_id}' already exists.")
        entry = ExpenseEntry(trans_id, date_str, category, amount, desc)
        self.records[trans_id] = entry
        print(f"✓ Expense of ₹{amount:.2f} logged under '{category}'.")

    def search_by_category(self, category: str) -> list[Transaction]:
        cat_clean = category.strip().lower()
        return [r for r in self.records.values() if r.category.lower() == cat_clean]

    def display_monthly_summary(self, year_month: str):
        """Generates summary for a given month format YYYY-MM."""
        matched = [r for r in self.records.values() if r.date_str.startswith(year_month)]
        if not matched:
            print(f"No records found for period: {year_month}")
            return

        total_income = sum(r.amount for r in matched if isinstance(r, IncomeEntry))
        total_expense = sum(r.amount for r in matched if isinstance(r, ExpenseEntry))
        net_savings = total_income - total_expense

        print("\n" + "=" * 80)
        print(f"FINANCIAL SUMMARY FOR: {year_month}".center(80))
        print("=" * 80)
        for r in matched:
            print(r.get_details())
        print("-" * 80)
        print(f"Total Income   : ₹{total_income:>10.2f}")
        print(f"Total Expenses : ₹{total_expense:>10.2f}")
        print(f"Net Savings    : ₹{net_savings:>10.2f}")
        print("=" * 80)

    def display_all(self):
        if not self.records:
            print("No transactions recorded.")
            return

        print("\n" + "=" * 90)
        print("ALL TRANSACTIONS".center(90))
        print("=" * 90)
        total_balance = sum(r.get_net_impact() for r in self.records.values())
        for r in self.records.values():
            print(r.get_details())
        print("-" * 90)
        print(f"Current Net Balance: ₹{total_balance:,.2f}")
        print("=" * 90)

    # --- File Handling (CSV) ---
    def save_to_file(self):
        try:
            with open(self.filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["type", "id", "date", "category", "amount", "description"])
                for r in self.records.values():
                    t_type = "Income" if isinstance(r, IncomeEntry) else "Expense"
                    writer.writerow([t_type, r.trans_id, r.date_str, r.category, r.amount, r.description])
            print(f"✓ Data successfully saved to '{self.filename}'.")
        except IOError as e:
            print(f"File Error: Could not save records ({e}).")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    t_type = row["type"]
                    t_id = row["id"]
                    t_date = row["date"]
                    cat = row["category"]
                    amt = float(row["amount"])
                    desc = row["description"]

                    if t_type == "Income":
                        self.records[t_id] = IncomeEntry(t_id, t_date, cat, amt, desc)
                    elif t_type == "Expense":
                        self.records[t_id] = ExpenseEntry(t_id, t_date, cat, amt, desc)
        except (IOError, KeyError, ValueError) as e:
            print(f"Warning: Issue reading '{self.filename}' ({e}). Starting fresh.")


# ==========================================
# 5. CLI Interface Loop
# ==========================================
def main():
    tracker = ExpenseTracker()

    while True:
        print("\n=== EXPENSE TRACKER ===")
        print("1. Record Income")
        print("2. Record Expense")
        print("3. View All Transactions & Net Balance")
        print("4. Monthly Summary Report (YYYY-MM)")
        print("5. Search Transactions by Category")
        print("6. Save Records")
        print("7. Save & Exit")

        choice = input("Enter choice (1-7): ").strip()

        try:
            if choice in ("1", "2"):
                t_id = input("Transaction ID (e.g. T01): ").strip()
                date_str = input("Date (YYYY-MM-DD, e.g. 2026-10-04): ").strip()
                category = input("Category (e.g. Salary, Food, Rent): ").strip()
                amount = float(input("Amount (₹): ").strip())
                desc = input("Description: ").strip()

                if choice == "1":
                    tracker.add_income(t_id, date_str, category, amount, desc)
                else:
                    tracker.add_expense(t_id, date_str, category, amount, desc)

            elif choice == "3":
                tracker.display_all()

            elif choice == "4":
                ym = input("Enter Year & Month (YYYY-MM): ").strip()
                tracker.display_monthly_summary(ym)

            elif choice == "5":
                cat = input("Enter Category Name: ").strip()
                matches = tracker.search_by_category(cat)
                if not matches:
                    print(f"No records found under category '{cat}'.")
                else:
                    print(f"\nFound {len(matches)} record(s):")
                    for m in matches:
                        print(f"  {m.get_details()}")

            elif choice == "6":
                tracker.save_to_file()

            elif choice == "7":
                tracker.save_to_file()
                print("Exiting application. Goodbye!")
                break

            else:
                print("Invalid choice. Select from 1 to 7.")

        except (TransactionNotFoundError, DuplicateTransactionError, InvalidTransactionError) as err:
            print(f"Transaction Error: {err}")
        except ValueError as ve:
            print(f"Input Error: Please provide valid entries ({ve}).")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()