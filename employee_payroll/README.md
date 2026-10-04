# Employee Payroll System

A modular Python console application implementing polymorphic payroll calculations and payslip reporting.

## Features
- Support for multiple contract models: Monthly Salaried vs. Hourly with overtime calculations.
- Automatic generation of formatted payslips.
- Aggregate expenditure calculation across departments.
- Strict data sanitization and boundary checking.
- Persistent file storage (`payroll_data.csv`).

## OOP Architecture
1. **Abstraction**: `Employee` uses `abc.ABC` with abstract methods `calculate_salary()` and `generate_payslip()`.
2. **Inheritance**: `SalariedEmployee` and `HourlyEmployee` extend `Employee`, implementing their own formulas.
3. **Encapsulation**: Financial metrics (`__monthly_salary`, `__hourly_rate`, `__hours_worked`) are kept private and accessible via validation-guarded setters and getters.
4. **File Handling**: Direct serializing and deserializing of polymorphic records using Python's standard `csv` module.
5. **Exception Handling**: Built with custom exceptions (`EmployeeNotFoundError`, `DuplicateEmployeeError`, `InvalidCompensationError`).

## How to Run
```bash
python employee_payroll.py