# Quiz Management System

An interactive console-based quiz engine implementing Object-Oriented Programming (OOP) principles in Python.

## Features
- Dynamic polymorphic questions: Multiple Choice Questions (MCQ) and True/False (TF).
- Automated answer validation and real-time score grading.
- Persistent file storage for question banks (`questions.csv`) and candidate results (`quiz_results.csv`).
- Comprehensive input sanitization and custom exception handling.

## OOP Architecture
1. **Abstraction**: `Question` is an abstract base class built with `abc.ABC` and `@abstractmethod` decorators (`display()` and `check_answer()`).
2. **Inheritance**: `MCQQuestion` and `TrueFalseQuestion` inherit from `Question`, supplying type-specific rendering and answer verification.
3. **Encapsulation**: Private attributes `__correct_option` and `__correct_answer` conceal correct answers from external inspection.
4. **File Handling**: Question datasets and candidate performance metrics are managed using Python's standard `csv` library.
5. **Exception Handling**: Employs `QuestionLoadError` and `InvalidAnswerError` to isolate parsing problems and user input mistakes.

## How to Run
```bash
python quiz_management.py