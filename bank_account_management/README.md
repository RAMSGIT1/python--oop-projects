# Bank Account Management System

A Python application modeling standard retail banking transactions with strict Object-Oriented Programming (OOP) paradigms.

## Features
- Create Savings and Current accounts with distinct business constraints.
- Process deposits and withdrawals with balance and boundary protections.
- Track real-time timestamped transaction logs for every account.
- Prevent invalid financial operations (overdrawing savings below ₹500, current overdraft threshold capped at ₹2000).
- Persistent CSV-based data storage (`bank_accounts.csv`).

## OOP Architecture
1. **Abstraction**: `Account` acts as an abstract base class via `abc.ABC` and `@abstractmethod`, guaranteeing polymorphic behavior for `withdraw()` and `get_details()`.
2. **Inheritance**: `SavingsAccount` and `CurrentAccount` inherit baseline financial behavior from `Account` and override withdrawal rules.
3. **Encapsulation**: Private attributes `__balance` and `__transaction_history` are read-only via properties, mutable only through `deposit()` and protected `_deduct()`.
4. **File Handling**: Standard structured serialization using Python's `csv` module.
5. **Exception Handling**: Custom exceptions (`AccountNotFoundError`, `InsufficientFundsError`, `DuplicateAccountError`, `InvalidAmountError`) prevent illegal states.

## How to Run
```bash
python bank_management.py