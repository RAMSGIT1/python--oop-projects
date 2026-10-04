# Library Management System

A complete CLI application implementing core Object-Oriented Programming (OOP) paradigms for catalog and inventory management.

## Features
- Add new books to the library catalog.
- Search items dynamically by Title, Author, or ISBN.
- Issue and return books with strict state verification.
- Filter to display only currently available books or the entire catalog.
- Persistent CSV file storage (`library_books.csv`).

## OOP Architecture
1. **Abstraction**: `LibraryItem` is an abstract base class utilizing `abc.ABC` and the `@abstractmethod` decorator to define an item contract.
2. **Inheritance**: `Book` extends `LibraryItem` with book-specific attributes (`author`, `is_issued`, `issued_to`).
3. **Encapsulation**: Private attributes (`__author`, `__is_issued`, `__issued_to`) accessed strictly via `@property` getters and methods that guard the internal state.
4. **File Handling**: Automatic persistence through standard Python CSV readers and writers.
5. **Exception Handling**: Custom application exceptions (`BookNotFoundError`, `BookUnavailableError`, `BookNotIssuedError`, `DuplicateBookError`) alongside standard `ValueError` handling.

## How to Run
```bash
python library_management.py