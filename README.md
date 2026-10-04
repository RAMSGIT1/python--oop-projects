# Python Object-Oriented Programming (OOP) Capstone Suite

This repository contains 10 production-grade CLI applications demonstrating core Object-Oriented Programming paradigms in Python.

## Core OOP Criteria Implemented
- **Abstraction**: Base classes using Python's native `abc.ABC` and `@abstractmethod`.
- **Inheritance**: Derived subclasses specializing behavior without duplicating logic.
- **Encapsulation**: Private (`__`) and protected (`_`) state variables guarded by `@property` decorators and validation methods.
- **File Handling**: Automatic reading and writing using Python's standard `csv` library.
- **Exception Handling**: Domain-specific custom exceptions preventing invalid runtime states.

## Project Directory
| # | Project Name | Focus Concepts |
|---|---|---|
| 01 | [Student Management System](./01_student_management) | Abstract Person base, mark calculation, student directory |
| 02 | [Library Management System](./02_library_management) | Catalog check-in/out states, ISBN indexing |
| 03 | [Bank Account Management](./03_bank_management) | Savings vs. Current overdraft rules, transaction logging |
| 04 | [Employee Payroll System](./04_employee_payroll) | Salaried vs. Hourly wage structures, automated payslips |
| 05 | [Inventory Management System](./05_inventory_management) | Perishable goods expiration, stock level guardrails |
| 06 | [Quiz Management System](./06_quiz_management) | MCQ & True/False polymorphism, automated scorecard engine |
| 07 | [Hospital Patient Record System](./07_hospital_management) | Inpatient vs. Outpatient billing, clinical records |
| 08 | [Vehicle Rental Management](./08_vehicle_rental) | Car vs. Van cargo tariffs, booking duration engine |
| 09 | [Expense Tracker](./09_expense_tracker) | Cash flow analysis, monthly category breakdowns |
| 10 | [Course Registration System](./10_course_registration) | Seat quotas, duplicate prevention, dual-file CSV persistence |