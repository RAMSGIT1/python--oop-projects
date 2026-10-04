import csv
import datetime
import os
from abc import ABC, abstractmethod


# ==========================================
# 1. Custom Exceptions
# ==========================================
class AccountNotFoundError(Exception):
    """Raised when an account number does not exist."""

    pass


class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds balance/overdraft boundaries."""

    pass


class DuplicateAccountError(Exception):
    """Raised when attempting to create an account with an existing ID."""

    pass


class InvalidAmountError(Exception):
    """Raised for non-positive or irrational transaction amounts."""

    pass


# ==========================================
# 2. Abstraction: Base Class
# ==========================================
class Account(ABC):
    """Abstract base class representing a generic financial account."""

    def __init__(
        self,
        account_no: str,
        account_holder: str,
        initial_balance: float = 0.0,
        history: list[str] | None = None,
    ):
        self._account_no = account_no
        self._account_holder = account_holder
        self.__balance = initial_balance
        self.__transaction_history = (
            history
            if history is not None
            else [f"{self._get_timestamp()} - Account created with ₹{initial_balance:.2f}"]
        )

    @staticmethod
    def _get_timestamp() -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- Encapsulation ---
    @property
    def account_no(self) -> str:
        return self._account_no

    @property
    def account_holder(self) -> str:
        return self._account_holder

    @property
    def balance(self) -> float:
        return self.__balance

    @property
    def history(self) -> list[str]:
        return self.__transaction_history

    def deposit(self, amount: float):
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be greater than zero.")
        self.__balance += amount
        self.__transaction_history.append(
            f"{self._get_timestamp()} - Deposited: ₹{amount:.2f} | Balance: ₹{self.__balance:.2f}"
        )

    def _deduct(self, amount: float, description: str):
        """Internal helper for approved withdrawals."""
        self.__balance -= amount
        self.__transaction_history.append(
            f"{self._get_timestamp()} - {description}: ₹{amount:.2f} | Balance: ₹{self.__balance:.2f}"
        )

    @abstractmethod
    def withdraw(self, amount: float):
        """Abstract method enforced on specific account rules."""
        pass

    @abstractmethod
    def get_details(self) -> str:
        """Abstract method for formatted account metadata."""
        pass


# ==========================================
# 3. Inheritance & Encapsulation: Subclasses
# ==========================================
class SavingsAccount(Account):
    """Derived class with a mandatory minimum balance constraint."""

    MINIMUM_BALANCE = 500.0

    def withdraw(self, amount: float):
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be greater than zero.")
        if (self.balance - amount) < self.MINIMUM_BALANCE:
            raise InsufficientFundsError(
                f"Withdrawal denied. Savings account requires a minimum balance of ₹{self.MINIMUM_BALANCE:.2f}."
            )
        self._deduct(amount, "Withdrawal (Savings)")

    def get_details(self) -> str:
        return (
            f"Type: Savings | Acc No: {self.account_no} | Holder: {self.account_holder:<18} | "
            f"Balance: ₹{self.balance:<10.2f} | Min Bal: ₹{self.MINIMUM_BALANCE:.2f}"
        )


class CurrentAccount(Account):
    """Derived class with an overdraft facility."""

    OVERDRAFT_LIMIT = 2000.0

    def withdraw(self, amount: float):
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be greater than zero.")
        if (self.balance - amount) < -self.OVERDRAFT_LIMIT:
            raise InsufficientFundsError(
                f"Withdrawal denied. Exceeds permissible overdraft limit of ₹{self.OVERDRAFT_LIMIT:.2f}."
            )
        self._deduct(amount, "Withdrawal (Current)")

    def get_details(self) -> str:
        return (
            f"Type: Current | Acc No: {self.account_no} | Holder: {self.account_holder:<18} | "
            f"Balance: ₹{self.balance:<10.2f} | Overdraft: ₹{self.OVERDRAFT_LIMIT:.2f}"
        )


# ==========================================
# 4. Management Class: BankManager
# ==========================================
class BankManager:
    """Coordinates account records, transactions, and CSV persistence."""

    def __init__(self, filename: str = "bank_accounts.csv"):
        self.filename = filename
        self.accounts: dict[str, Account] = {}
        self.load_from_file()

    def create_account(
        self, acc_type: str, account_no: str, holder: str, initial_balance: float
    ):
        if account_no in self.accounts:
            raise DuplicateAccountError(
                f"Account with number '{account_no}' already exists."
            )

        acc_type_clean = acc_type.strip().lower()
        if acc_type_clean == "savings":
            if initial_balance < SavingsAccount.MINIMUM_BALANCE:
                raise InvalidAmountError(
                    f"Initial balance for Savings must be at least ₹{SavingsAccount.MINIMUM_BALANCE:.2f}."
                )
            account = SavingsAccount(account_no, holder, initial_balance)
        elif acc_type_clean == "current":
            if initial_balance < 0:
                raise InvalidAmountError("Initial balance cannot be negative.")
            account = CurrentAccount(account_no, holder, initial_balance)
        else:
            raise ValueError("Invalid account type. Choose 'Savings' or 'Current'.")

        self.accounts[account_no] = account
        print(f"✓ {acc_type.capitalize()} account created for '{holder}'.")

    def get_account(self, account_no: str) -> Account:
        if account_no not in self.accounts:
            raise AccountNotFoundError(f"Account '{account_no}' not found.")
        return self.accounts[account_no]

    def deposit(self, account_no: str, amount: float):
        account = self.get_account(account_no)
        account.deposit(amount)
        print(f"✓ Deposited ₹{amount:.2f}. New Balance: ₹{account.balance:.2f}")

    def withdraw(self, account_no: str, amount: float):
        account = self.get_account(account_no)
        account.withdraw(amount)
        print(f"✓ Withdrew ₹{amount:.2f}. New Balance: ₹{account.balance:.2f}")

    def display_statement(self, account_no: str):
        account = self.get_account(account_no)
        print("\n" + "=" * 60)
        print(f"TRANSACTION HISTORY: {account.account_no}".center(60))
        print("=" * 60)
        for log in account.history:
            print(f" • {log}")
        print("-" * 60)
        print(f"Current Available Balance: ₹{account.balance:.2f}")
        print("=" * 60)

    def display_all_accounts(self):
        if not self.accounts:
            print("No bank accounts registered.")
            return

        print("\n" + "=" * 75)
        print("ALL ACTIVE ACCOUNTS".center(75))
        print("=" * 75)
        for acc in self.accounts.values():
            print(acc.get_details())
        print("=" * 75)

    # --- File Handling (CSV) ---
    def save_to_file(self):
        try:
            with open(self.filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["acc_type", "account_no", "holder", "balance", "history"]
                )
                for acc in self.accounts.values():
                    acc_type = "Savings" if isinstance(acc, SavingsAccount) else "Current"
                    history_str = "::".join(acc.history)
                    writer.writerow(
                        [acc_type, acc.account_no, acc.account_holder, acc.balance, history_str]
                    )
            print(f"✓ Bank records saved to '{self.filename}'.")
        except IOError as e:
            print(f"File Error: Could not save records ({e}).")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    acc_type = row["acc_type"]
                    acc_no = row["account_no"]
                    holder = row["holder"]
                    balance = float(row["balance"])
                    history = (
                        row["history"].split("::")
                        if row.get("history")
                        else []
                    )

                    if acc_type == "Savings":
                        self.accounts[acc_no] = SavingsAccount(
                            acc_no, holder, balance, history
                        )
                    elif acc_type == "Current":
                        self.accounts[acc_no] = CurrentAccount(
                            acc_no, holder, balance, history
                        )
        except (IOError, KeyError, ValueError) as e:
            print(f"Warning: Issue reading '{self.filename}' ({e}). Starting fresh.")


# ==========================================
# 5. CLI Interface Loop
# ==========================================
def main():
    bank = BankManager()

    while True:
        print("\n=== BANK ACCOUNT MANAGEMENT SYSTEM ===")
        print("1. Create New Account (Savings / Current)")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Check Balance & Details")
        print("5. View Transaction History")
        print("6. List All Accounts")
        print("7. Save Records")
        print("8. Save & Exit")

        choice = input("Enter choice (1-8): ").strip()

        try:
            if choice == "1":
                acc_type = input("Account Type (Savings / Current): ").strip()
                acc_no = input("Enter Account Number: ").strip()
                holder = input("Enter Account Holder Name: ").strip()
                balance = float(input("Enter Initial Deposit: ").strip())
                bank.create_account(acc_type, acc_no, holder, balance)

            elif choice == "2":
                acc_no = input("Enter Account Number: ").strip()
                amt = float(input("Enter Amount to Deposit: ").strip())
                bank.deposit(acc_no, amt)

            elif choice == "3":
                acc_no = input("Enter Account Number: ").strip()
                amt = float(input("Enter Amount to Withdraw: ").strip())
                bank.withdraw(acc_no, amt)

            elif choice == "4":
                acc_no = input("Enter Account Number: ").strip()
                account = bank.get_account(acc_no)
                print(f"\n{account.get_details()}")

            elif choice == "5":
                acc_no = input("Enter Account Number: ").strip()
                bank.display_statement(acc_no)

            elif choice == "6":
                bank.display_all_accounts()

            elif choice == "7":
                bank.save_to_file()

            elif choice == "8":
                bank.save_to_file()
                print("Exiting application. Goodbye!")
                break

            else:
                print("Invalid selection. Choose between 1 and 8.")

        except (
            AccountNotFoundError,
            InsufficientFundsError,
            DuplicateAccountError,
            InvalidAmountError,
        ) as custom_err:
            print(f"Banking Error: {custom_err}")
        except ValueError as ve:
            print(f"Input Error: Please provide valid numeric inputs ({ve}).")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()