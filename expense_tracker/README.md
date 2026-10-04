# Expense Tracker

A Python console application modeling personal cash flow accounting, income categorization, expense tracking, and monthly financial summaries using Object-Oriented Programming (OOP) paradigms.

## Features
- **Polymorphic Financial Entries**:
  - **IncomeEntry**: Positive cash flow impacts (+amount).
  - **ExpenseEntry**: Negative cash flow impacts (-amount).
- **Date & Value Validation**: Strict `YYYY-MM-DD` date parsing and non-negative currency checks.
- **Search & Categorization**: Search transactions dynamically by category tag.
- **Monthly Summaries**: Compute total income, total expense, and net savings for any `YYYY-MM` period.
- **Data Persistence**: Persistent record storage using `expenses.csv`.

## OOP Architecture
1. **Abstraction**: `Transaction` serves as an abstract base class via `abc.ABC` with abstract methods `get_net_impact()` and `get_details()`.
2. **Inheritance**: `IncomeEntry` and `ExpenseEntry` extend `Transaction` with specialized cash flow behaviors.
3. **Encapsulation**: Private attributes `__amount`, `__date_str`, and `__description` guarded with validation setters.
4. **File Handling**: Automatic reading/writing using Python's standard `csv` library.
5. **Exception Handling**: Domain-specific custom exceptions (`TransactionNotFoundError`, `DuplicateTransactionError`, `InvalidTransactionError`).

## File Structure
- `expense_tracker.py`: Main executable containing transactions, financial summary engine, and CLI menu.
- `expenses.csv`: Persistent database file storing income and expense transactions.
- `README.md`: System documentation and architectural overview.

## How to Run
```bash
python expense_tracker.py