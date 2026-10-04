import csv
import os
from abc import ABC, abstractmethod


# ==========================================
# 1. Custom Exceptions
# ==========================================
class CourseNotFoundError(Exception):
    """Raised when a course code is not found in the catalog."""
    pass


class StudentNotFoundError(Exception):
    """Raised when a student ID does not exist."""
    pass


class CourseCapacityFullError(Exception):
    """Raised when attempting to enroll in a full course."""
    pass


class AlreadyEnrolledError(Exception):
    """Raised when a student attempts to enroll in a course twice."""
    pass


class NotEnrolledError(Exception):
    """Raised when a student attempts to drop a course they are not enrolled in."""
    pass


class DuplicateRecordError(Exception):
    """Raised when attempting to add an existing student or course ID."""
    pass


# ==========================================
# 2. Abstraction: Base Class
# ==========================================
class AcademicEntity(ABC):
    """Abstract base class representing an academic entity."""

    def __init__(self, entity_id: str, name: str):
        self._entity_id = entity_id  # Protected
        self._name = name

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value.strip():
            raise ValueError("Entity name cannot be empty.")
        self._name = value.strip()

    @abstractmethod
    def get_details(self) -> str:
        """Returns formatted string representation of entity metadata."""
        pass


# ==========================================
# 3. Inheritance & Encapsulation: Subclasses
# ==========================================
class Course(AcademicEntity):
    """Represents an academic course with seat limits and enrolled student tracking."""

    def __init__(self, course_code: str, title: str, credits: int, capacity: int, enrolled_students: list[str] | None = None):
        super().__init__(entity_id=course_code, name=title)
        self.set_credits(credits)
        self.set_capacity(capacity)
        self.__enrolled_students = list(enrolled_students) if enrolled_students is not None else []

    @property
    def course_code(self) -> str:
        return self.entity_id

    @property
    def title(self) -> str:
        return self.name

    @property
    def credits(self) -> int:
        return self.__credits

    def set_credits(self, value: int):
        if value <= 0:
            raise ValueError("Course credits must be at least 1.")
        self.__credits = value

    @property
    def capacity(self) -> int:
        return self.__capacity

    def set_capacity(self, value: int):
        if value <= 0:
            raise ValueError("Course capacity must be at least 1.")
        self.__capacity = value

    @property
    def enrolled_students(self) -> list[str]:
        return self.__enrolled_students

    @property
    def available_seats(self) -> int:
        return self.__capacity - len(self.__enrolled_students)

    def enroll(self, student_id: str):
        if student_id in self.__enrolled_students:
            raise AlreadyEnrolledError(f"Student '{student_id}' is already enrolled in '{self.course_code}'.")
        if self.available_seats <= 0:
            raise CourseCapacityFullError(f"Cannot enroll in '{self.course_code}'. Course capacity is full.")
        self.__enrolled_students.append(student_id)

    def drop(self, student_id: str):
        if student_id not in self.__enrolled_students:
            raise NotEnrolledError(f"Student '{student_id}' is not enrolled in '{self.course_code}'.")
        self.__enrolled_students.remove(student_id)

    def get_details(self) -> str:
        return (f"Code: {self.course_code:<8} | Title: {self.title:<25} | Credits: {self.__credits:<2} | "
                f"Enrolled: {len(self.__enrolled_students)}/{self.__capacity} (Seats: {self.available_seats})")


class EnrolledStudent(AcademicEntity):
    """Represents a student and their registered courses."""

    def __init__(self, student_id: str, name: str, major: str):
        super().__init__(entity_id=student_id, name=name)
        self._major = major

    @property
    def student_id(self) -> str:
        return self.entity_id

    @property
    def major(self) -> str:
        return self._major

    def get_details(self) -> str:
        return f"Student ID: {self.student_id:<8} | Name: {self.name:<20} | Major: {self._major}"


# ==========================================
# 4. Management Class: RegistrationManager
# ==========================================
class RegistrationManager:
    """Coordinates student and course catalogs, registrations, and CSV persistence."""

    def __init__(self, students_file: str = "reg_students.csv", courses_file: str = "reg_courses.csv"):
        self.students_file = students_file
        self.courses_file = courses_file
        self.students: dict[str, EnrolledStudent] = {}
        self.courses: dict[str, Course] = {}
        self.load_from_files()

    def add_student(self, student_id: str, name: str, major: str):
        if student_id in self.students:
            raise DuplicateRecordError(f"Student ID '{student_id}' already exists.")
        self.students[student_id] = EnrolledStudent(student_id, name, major)
        print(f"✓ Student '{name}' (ID: {student_id}) added successfully.")

    def add_course(self, code: str, title: str, credits: int, capacity: int):
        if code in self.courses:
            raise DuplicateRecordError(f"Course code '{code}' already exists.")
        self.courses[code] = Course(code, title, credits, capacity)
        print(f"✓ Course '{title}' ({code}) added with capacity {capacity}.")

    def register_course(self, student_id: str, course_code: str):
        if student_id not in self.students:
            raise StudentNotFoundError(f"Student ID '{student_id}' not found.")
        if course_code not in self.courses:
            raise CourseNotFoundError(f"Course code '{course_code}' not found.")

        self.courses[course_code].enroll(student_id)
        print(f"✓ Student '{self.students[student_id].name}' successfully enrolled in '{course_code}'.")

    def drop_course(self, student_id: str, course_code: str):
        if student_id not in self.students:
            raise StudentNotFoundError(f"Student ID '{student_id}' not found.")
        if course_code not in self.courses:
            raise CourseNotFoundError(f"Course code '{course_code}' not found.")

        self.courses[course_code].drop(student_id)
        print(f"✓ Student '{self.students[student_id].name}' dropped from '{course_code}'.")

    def display_courses(self):
        if not self.courses:
            print("No courses catalogued.")
            return

        print("\n" + "=" * 80)
        print("COURSE CATALOG".center(80))
        print("=" * 80)
        for c in self.courses.values():
            print(c.get_details())
        print("=" * 80)

    def display_students(self):
        if not self.students:
            print("No students registered.")
            return

        print("\n" + "=" * 80)
        print("STUDENT DIRECTORY".center(80))
        print("=" * 80)
        for s in self.students.values():
            print(s.get_details())
        print("=" * 80)

    def display_student_schedule(self, student_id: str):
        if student_id not in self.students:
            raise StudentNotFoundError(f"Student ID '{student_id}' not found.")

        student = self.students[student_id]
        enrolled_in = [c for c in self.courses.values() if student_id in c.enrolled_students]
        total_credits = sum(c.credits for c in enrolled_in)

        print("\n" + "=" * 80)
        print(f"ENROLLMENT SCHEDULE FOR: {student.name} ({student.student_id})".center(80))
        print("=" * 80)
        if not enrolled_in:
            print("No active course enrollments.")
        else:
            for c in enrolled_in:
                print(f" • [{c.course_code}] {c.title:<30} ({c.credits} Credits)")
            print("-" * 80)
            print(f"Total Registered Credits: {total_credits}")
        print("=" * 80)

    # --- File Handling (CSV) ---
    def save_to_files(self):
        try:
            with open(self.students_file, mode="w", newline="", encoding="utf-8") as sf:
                writer = csv.writer(sf)
                writer.writerow(["student_id", "name", "major"])
                for s in self.students.values():
                    writer.writerow([s.student_id, s.name, s.major])

            with open(self.courses_file, mode="w", newline="", encoding="utf-8") as cf:
                writer = csv.writer(cf)
                writer.writerow(["course_code", "title", "credits", "capacity", "enrolled_students"])
                for c in self.courses.values():
                    enrolled_str = ";".join(c.enrolled_students)
                    writer.writerow([c.course_code, c.title, c.credits, c.capacity, enrolled_str])

            print(f"✓ Data saved to '{self.students_file}' and '{self.courses_file}'.")
        except IOError as e:
            print(f"File Error: Could not save records ({e}).")

    def load_from_files(self):
        if os.path.exists(self.students_file):
            try:
                with open(self.students_file, mode="r", newline="", encoding="utf-8") as sf:
                    reader = csv.DictReader(sf)
                    for row in reader:
                        s_id = row["student_id"]
                        self.students[s_id] = EnrolledStudent(s_id, row["name"], row["major"])
            except Exception as e:
                print(f"Warning: Issue reading students file ({e}).")

        if os.path.exists(self.courses_file):
            try:
                with open(self.courses_file, mode="r", newline="", encoding="utf-8") as cf:
                    reader = csv.DictReader(cf)
                    for row in reader:
                        code = row["course_code"]
                        title = row["title"]
                        credits = int(row["credits"])
                        capacity = int(row["capacity"])
                        raw_enrolled = row.get("enrolled_students", "")
                        enrolled = [s.strip() for s in raw_enrolled.split(";") if s.strip()] if raw_enrolled else []
                        self.courses[code] = Course(code, title, credits, capacity, enrolled)
            except Exception as e:
                print(f"Warning: Issue reading courses file ({e}).")


# ==========================================
# 5. CLI Interface Loop
# ==========================================
def main():
    manager = RegistrationManager()

    while True:
        print("\n=== COURSE REGISTRATION SYSTEM ===")
        print("1. Add Student")
        print("2. Add Course")
        print("3. Register Student for Course")
        print("4. Drop Course")
        print("5. View Student Schedule")
        print("6. Display All Courses")
        print("7. Display All Students")
        print("8. Save Records")
        print("9. Save & Exit")

        choice = input("Enter choice (1-9): ").strip()

        try:
            if choice == "1":
                s_id = input("Student ID (e.g. S101): ").strip()
                name = input("Student Full Name: ").strip()
                major = input("Major / Department: ").strip()
                manager.add_student(s_id, name, major)

            elif choice == "2":
                code = input("Course Code (e.g. CS101): ").strip().upper()
                title = input("Course Title: ").strip()
                credits = int(input("Course Credits: ").strip())
                cap = int(input("Max Seat Capacity: ").strip())
                manager.add_course(code, title, credits, capacity=cap)

            elif choice == "3":
                s_id = input("Student ID: ").strip()
                code = input("Course Code to Enroll: ").strip().upper()
                manager.register_course(s_id, code)

            elif choice == "4":
                s_id = input("Student ID: ").strip()
                code = input("Course Code to Drop: ").strip().upper()
                manager.drop_course(s_id, code)

            elif choice == "5":
                s_id = input("Enter Student ID: ").strip()
                manager.display_student_schedule(s_id)

            elif choice == "6":
                manager.display_courses()

            elif choice == "7":
                manager.display_students()

            elif choice == "8":
                manager.save_to_files()

            elif choice == "9":
                manager.save_to_files()
                print("Exiting application. Goodbye!")
                break

            else:
                print("Invalid choice. Select from 1 to 9.")

        except (CourseNotFoundError, StudentNotFoundError, CourseCapacityFullError,
                AlreadyEnrolledError, NotEnrolledError, DuplicateRecordError) as err:
            print(f"Registration Error: {err}")
        except ValueError as ve:
            print(f"Input Error: Please provide valid entries ({ve}).")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()