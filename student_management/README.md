# Student Management System

A Python console application demonstrating core Object-Oriented Programming (OOP) concepts.

## Features
- Add, search, update, and delete student records.
- Track individual student marks and calculate averages.
- Calculate total class average.
- Persistent storage using CSV (`students.csv`).
- Input validation and custom exception handling.

## OOP Concepts Implemented
1. **Abstraction**: `Person` is an abstract base class utilizing `abc.ABC` and `@abstractmethod`.
2. **Inheritance**: `Student` inherits common fields (`name`, `age`) from `Person`.
3. **Encapsulation**: Private attributes `__roll_no` and `__marks` protected with Python properties (`@property`) and setters with boundary checks.
4. **File Handling**: Automatic reading/writing using Python's native `csv` library.
5. **Exception Handling**: Catches invalid input types, file failures, and utilizes custom exceptions (`StudentNotFoundError`, `DuplicateStudentError`).

## How to Run
```bash
python student_management.py