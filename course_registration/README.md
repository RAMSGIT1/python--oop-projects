# Project 10 — Course Registration System

A Python console application that manages university course registration, seat capacities, credit calculations, and student enrollment schedules under Object-Oriented Programming (OOP) paradigms.

## Features
- **Catalog Management**: Add courses with credit weights and seat capacities.
- **Enrollment & Dropping**: Register and drop courses with seat limit checks and duplicate prevention.
- **Schedule Inquiries**: Display student schedules and calculate total registered credit loads.
- **Seat Availability Tracking**: Real-time remaining seat counters.
- **Dual-File CSV Persistence**: Automatically saves and loads records via `reg_students.csv` and `reg_courses.csv`.

## OOP Architecture
1. **Abstraction**: `AcademicEntity` defines an abstract base class using `abc.ABC` with `@abstractmethod` `get_details()`.
2. **Inheritance**: `Course` and `EnrolledStudent` inherit entity identity attributes (`entity_id`, `name`) from `AcademicEntity`.
3. **Encapsulation**: Private attributes (`__credits`, `__capacity`, `__enrolled_students`) are protected by properties and validated mutating methods.
4. **File Handling**: Automatic reading/writing of student and course enrollment records using Python's `csv` library.
5. **Exception Handling**: Domain-specific custom exceptions (`CourseNotFoundError`, `StudentNotFoundError`, `CourseCapacityFullError`, `AlreadyEnrolledError`, `NotEnrolledError`, `DuplicateRecordError`).

## File Structure
- `course_registration.py`: Main executable containing the class hierarchy, manager, and CLI menu.
- `reg_students.csv`: Persistent database of enrolled students.
- `reg_courses.csv`: Persistent database of courses, limits, and enrollments.
- `README.md`: System documentation and architectural overview.

## How to Run
```bash
python course_registration.py