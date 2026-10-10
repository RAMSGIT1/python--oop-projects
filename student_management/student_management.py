import csv
import os
from abc import ABC, abstractmethod
from typing import Optional


# ==========================================
# 1. Custom Exceptions
# ==========================================
class StudentNotFoundError(Exception):
    """Raised when a student record cannot be found."""

    pass


class DuplicateStudentError(Exception):
    """Raised when attempting to add an existing roll number."""

    pass


# ==========================================
# 2. Abstraction: Base Class
# ==========================================
class Person(ABC):
    """Abstract base class representing a generic person."""

    def __init__(self, name: str, age: int):
        self._name = name  # Protected attribute
        self._age = age

    @abstractmethod
    def get_details(self) -> str:
        """Abstract method to display formatted entity details."""
        pass


# ==========================================
# 3. Inheritance & Encapsulation: Student Class
# ==========================================
class Student(Person):
    """Derived class representing a student."""

    def __init__(
        self,
        roll_no: str,
        name: str,
        age: int,
        marks: Optional[list[float]] = None,
    ):
        super().__init__(name, age)
        self.__roll_no = roll_no  # Private attribute
        self.__marks = marks if marks is not None else []  # Private attribute

    # --- Encapsulation: Getters and Setters ---
    @property
    def roll_no(self) -> str:
        return self.__roll_no

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        if value <= 0:
            raise ValueError("Age must be a positive integer.")
        self._age = value

    @property
    def marks(self) -> list[float]:
        return self.__marks

    @marks.setter
    def marks(self, new_marks: list[float]):
        for mark in new_marks:
            if not (0 <= mark <= 100):
                raise ValueError("Marks must be between 0 and 100.")
        self.__marks = new_marks

    def calculate_average(self) -> float:
        """Calculates the average marks of the student."""
        if not self.__marks:
            return 0.0
        return round(sum(self.__marks) / len(self.__marks), 2)

    def get_details(self) -> str:
        """Concrete implementation of Person's abstract method."""
        marks_str = ", ".join(map(str, self.__marks)) if self.__marks else "None"
        return (
            f"Roll No: {self.__roll_no} | Name: {self._name} | Age: {self._age} | "
            f"Marks: [{marks_str}] | Avg: {self.calculate_average():.2f}"
        )


# ==========================================
# 4. Management Class: StudentManager
# ==========================================
class StudentManager:
    """Handles business logic, student records, and CSV persistence."""

    def __init__(self, filename: str = "students.csv"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, filename)
        self.students: dict[str, Student] = {}
        self.load_from_file()

    def add_student(self, roll_no: str, name: str, age: int, marks: list[float]):
        if roll_no in self.students:
            raise DuplicateStudentError(
                f"Student with Roll No '{roll_no}' already exists."
            )

        student = Student(roll_no, name, age, marks)
        self.students[roll_no] = student
        print(f"✓ Student '{name}' added successfully.")

    def display_all(self):
        if not self.students:
            print("No student records available.")
            return

        print("\n" + "=" * 70)
        print("STUDENT RECORDS".center(70))
        print("=" * 70)
        for student in self.students.values():
            print(student.get_details())
        print("=" * 70)

    def search_student(self, roll_no: str) -> Student:
        if roll_no not in self.students:
            raise StudentNotFoundError(
                f"Student with Roll No '{roll_no}' was not found."
            )
        return self.students[roll_no]

    def update_student(
        self,
        roll_no: str,
        name: Optional[str] = None,
        age: Optional[int] = None,
        marks: Optional[list[float]] = None,
    ):
        student = self.search_student(roll_no)
        if name:
            student.name = name
        if age:
            student.age = age
        if marks is not None:
            student.marks = marks
        print(f"✓ Record for Roll No '{roll_no}' updated.")

    def delete_student(self, roll_no: str):
        self.search_student(roll_no)  # Raises StudentNotFoundError if missing
        del self.students[roll_no]
        print(f"✓ Student with Roll No '{roll_no}' removed.")

    def calculate_class_average(self) -> float:
        if not self.students:
            return 0.0
        total = sum(s.calculate_average() for s in self.students.values())
        return round(total / len(self.students), 2)

    # --- File Handling (CSV) ---
    def save_to_file(self):
        try:
            with open(
                self.filename, mode="w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                writer.writerow(["roll_no", "name", "age", "marks"])
                for s in self.students.values():
                    marks_joined = ";".join(map(str, s.marks))
                    writer.writerow([s.roll_no, s.name, s.age, marks_joined])
            print(f"✓ Data successfully saved to '{self.filename}'.")
        except IOError as e:
            print(f"File Error: Could not save records ({e}).")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(
                self.filename, mode="r", newline="", encoding="utf-8"
            ) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    roll_no = row["roll_no"]
                    name = row["name"]
                    age = int(row["age"])
                    raw_marks = row["marks"]
                    marks = (
                        [float(m) for m in raw_marks.split(";")]
                        if raw_marks
                        else []
                    )
                    self.students[roll_no] = Student(roll_no, name, age, marks)
        except (IOError, ValueError) as e:
            print(f"Warning: Issue reading '{self.filename}' ({e}). Starting fresh.")


# ==========================================
# 5. CLI Interface Loop
# ==========================================
def main():
    manager = StudentManager()

    while True:
        print("\n=== STUDENT MANAGEMENT SYSTEM ===")
        print("1. Add Student")
        print("2. Display All Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Calculate Overall Class Average")
        print("7. Save Records")
        print("8. Save & Exit")

        choice = input("Enter choice (1-8): ").strip()

        try:
            if choice == "1":
                roll = input("Enter Roll Number: ").strip()
                name = input("Enter Name: ").strip()
                age = int(input("Enter Age: ").strip())
                marks_input = input(
                    "Enter Marks separated by commas (e.g. 85, 90, 78): "
                ).strip()
                marks = (
                    [float(m.strip()) for m in marks_input.split(",") if m.strip()]
                    if marks_input
                    else []
                )
                manager.add_student(roll, name, age, marks)

            elif choice == "2":
                manager.display_all()

            elif choice == "3":
                roll = input("Enter Roll Number to search: ").strip()
                student = manager.search_student(roll)
                print(f"Result: {student.get_details()}")

            elif choice == "4":
                roll = input("Enter Roll Number to update: ").strip()
                print(
                    "Leave field blank if you do not want to change that value."
                )
                name = input("New Name: ").strip()
                age_str = input("New Age: ").strip()
                marks_str = input("New Marks (comma-separated): ").strip()

                age = int(age_str) if age_str else None
                marks = (
                    [float(m.strip()) for m in marks_str.split(",") if m.strip()]
                    if marks_str
                    else None
                )

                manager.update_student(
                    roll, name=name or None, age=age, marks=marks
                )

            elif choice == "5":
                roll = input("Enter Roll Number to delete: ").strip()
                manager.delete_student(roll)

            elif choice == "6":
                avg = manager.calculate_class_average()
                print(f"Overall Class Average: {avg:.2f}")

            elif choice == "7":
                manager.save_to_file()

            elif choice == "8":
                manager.save_to_file()
                print("Exiting application. Goodbye!")
                break

            else:
                print("Invalid selection. Please choose an option from 1 to 8.")

        except ValueError as ve:
            print(f"Input Error: {ve}")
        except (StudentNotFoundError, DuplicateStudentError) as custom_err:
            print(f"Error: {custom_err}")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()