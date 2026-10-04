import csv
import os
from abc import ABC, abstractmethod


# ==========================================
# 1. Custom Exceptions
# ==========================================
class EmployeeNotFoundError(Exception):
    """Raised when an employee record is not found."""

    pass


class DuplicateEmployeeError(Exception):
    """Raised when an employee ID already exists."""

    pass


class InvalidCompensationError(Exception):
    """Raised for non-positive or irrational wage inputs."""

    pass


# ==========================================
# 2. Abstraction: Base Class
# ==========================================
class Employee(ABC):
    """Abstract base class for all employee variations."""

    def __init__(self, emp_id: str, name: str, department: str):
        self._emp_id = emp_id  # Protected
        self._name = name
        self._department = department

    @property
    def emp_id(self) -> str:
        return self._emp_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def department(self) -> str:
        return self._department

    @abstractmethod
    def calculate_salary(self) -> float:
        """Calculates net take-home salary."""
        pass

    @abstractmethod
    def generate_payslip(self) -> str:
        """Returns a formatted payslip statement."""
        pass


# ==========================================
# 3. Inheritance & Encapsulation: Subclasses
# ==========================================
class SalariedEmployee(Employee):
    """Full-time staff paid a fixed monthly salary with deductions."""

    def __init__(
        self,
        emp_id: str,
        name: str,
        department: str,
        monthly_salary: float,
        deductions: float = 0.0,
    ):
        super().__init__(emp_id, name, department)
        self.set_compensation(monthly_salary, deductions)

    def set_compensation(self, monthly_salary: float, deductions: float):
        if monthly_salary <= 0:
            raise InvalidCompensationError("Monthly salary must be greater than zero.")
        if deductions < 0 or deductions >= monthly_salary:
            raise InvalidCompensationError(
                "Deductions cannot be negative or exceed monthly salary."
            )
        self.__monthly_salary = monthly_salary
        self.__deductions = deductions

    @property
    def monthly_salary(self) -> float:
        return self.__monthly_salary

    @property
    def deductions(self) -> float:
        return self.__deductions

    def calculate_salary(self) -> float:
        return round(self.__monthly_salary - self.__deductions, 2)

    def generate_payslip(self) -> str:
        return (
            f"╔════════════════════════════════════════════════╗\n"
            f"║                PAYSLIP (SALARIED)              ║\n"
            f"╠════════════════════════════════════════════════╣\n"
            f"  Emp ID       : {self.emp_id:<30}\n"
            f"  Name         : {self.name:<30}\n"
            f"  Department   : {self.department:<30}\n"
            f"  Gross Salary : ₹{self.__monthly_salary:<29.2f}\n"
            f"  Deductions   : ₹{self.__deductions:<29.2f}\n"
            f"  ----------------------------------------------  \n"
            f"  Net Payout   : ₹{self.calculate_salary():<29.2f}\n"
            f"╚════════════════════════════════════════════════╝"
        )


class HourlyEmployee(Employee):
    """Contract staff paid based on hours logged (with 1.5x overtime > 160h)."""

    STANDARD_HOURS_CAP = 160.0

    def __init__(
        self,
        emp_id: str,
        name: str,
        department: str,
        hourly_rate: float,
        hours_worked: float = 0.0,
    ):
        super().__init__(emp_id, name, department)
        self.set_hours_and_rate(hourly_rate, hours_worked)

    def set_hours_and_rate(self, hourly_rate: float, hours_worked: float):
        if hourly_rate <= 0:
            raise InvalidCompensationError("Hourly rate must be greater than zero.")
        if hours_worked < 0 or hours_worked > 300:
            raise InvalidCompensationError("Hours worked must be between 0 and 300.")
        self.__hourly_rate = hourly_rate
        self.__hours_worked = hours_worked

    @property
    def hourly_rate(self) -> float:
        return self.__hourly_rate

    @property
    def hours_worked(self) -> float:
        return self.__hours_worked

    def calculate_salary(self) -> float:
        if self.__hours_worked <= self.STANDARD_HOURS_CAP:
            return round(self.__hours_worked * self.__hourly_rate, 2)
        # Overtime calculation: regular hours + 1.5x rate for extra hours
        regular_pay = self.STANDARD_HOURS_CAP * self.__hourly_rate
        overtime_hours = self.__hours_worked - self.STANDARD_HOURS_CAP
        overtime_pay = overtime_hours * (self.__hourly_rate * 1.5)
        return round(regular_pay + overtime_pay, 2)

    def generate_payslip(self) -> str:
        ot_hours = max(0.0, self.__hours_worked - self.STANDARD_HOURS_CAP)
        return (
            f"╔════════════════════════════════════════════════╗\n"
            f"║                 PAYSLIP (HOURLY)               ║\n"
            f"╠════════════════════════════════════════════════╣\n"
            f"  Emp ID       : {self.emp_id:<30}\n"
            f"  Name         : {self.name:<30}\n"
            f"  Department   : {self.department:<30}\n"
            f"  Hourly Rate  : ₹{self.__hourly_rate:<29.2f}\n"
            f"  Hours Logged : {self.__hours_worked:<30.1f}\n"
            f"  Overtime Hrs : {ot_hours:<30.1f}\n"
            f"  ----------------------------------------------  \n"
            f"  Net Payout   : ₹{self.calculate_salary():<29.2f}\n"
            f"╚════════════════════════════════════════════════╝"
        )


# ==========================================
# 4. Management Class: PayrollManager
# ==========================================
class PayrollManager:
    """Manages the employee registry and persistence."""

    def __init__(self, filename: str = "payroll_data.csv"):
        self.filename = filename
        self.employees: dict[str, Employee] = {}
        self.load_from_file()

    def add_salaried_employee(
        self,
        emp_id: str,
        name: str,
        dept: str,
        monthly_salary: float,
        deductions: float,
    ):
        if emp_id in self.employees:
            raise DuplicateEmployeeError(f"Employee ID '{emp_id}' is already registered.")
        emp = SalariedEmployee(emp_id, name, dept, monthly_salary, deductions)
        self.employees[emp_id] = emp
        print(f"✓ Salaried employee '{name}' added successfully.")

    def add_hourly_employee(
        self, emp_id: str, name: str, dept: str, hourly_rate: float, hours: float
    ):
        if emp_id in self.employees:
            raise DuplicateEmployeeError(f"Employee ID '{emp_id}' is already registered.")
        emp = HourlyEmployee(emp_id, name, dept, hourly_rate, hours)
        self.employees[emp_id] = emp
        print(f"✓ Hourly employee '{name}' added successfully.")

    def search_employee(self, emp_id: str) -> Employee:
        if emp_id not in self.employees:
            raise EmployeeNotFoundError(f"Employee '{emp_id}' not found.")
        return self.employees[emp_id]

    def display_all(self):
        if not self.employees:
            print("No employee records found.")
            return

        print("\n" + "=" * 70)
        print("EMPLOYEE DIRECTORY".center(70))
        print("=" * 70)
        print(
            f"{'ID':<8} | {'Name':<20} | {'Dept':<12} | {'Type':<10} | {'Net Pay':<12}"
        )
        print("-" * 70)
        for emp in self.employees.values():
            e_type = "Salaried" if isinstance(emp, SalariedEmployee) else "Hourly"
            print(
                f"{emp.emp_id:<8} | {emp.name:<20} | {emp.department:<12} | "
                f"{e_type:<10} | ₹{emp.calculate_salary():<10.2f}"
            )
        print("=" * 70)

    def total_payroll_expense(self) -> float:
        return round(sum(e.calculate_salary() for e in self.employees.values()), 2)

    # --- File Handling (CSV) ---
    def save_to_file(self):
        try:
            with open(self.filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["type", "emp_id", "name", "dept", "param1", "param2"]
                )
                for emp in self.employees.values():
                    if isinstance(emp, SalariedEmployee):
                        writer.writerow(
                            [
                                "Salaried",
                                emp.emp_id,
                                emp.name,
                                emp.department,
                                emp.monthly_salary,
                                emp.deductions,
                            ]
                        )
                    elif isinstance(emp, HourlyEmployee):
                        writer.writerow(
                            [
                                "Hourly",
                                emp.emp_id,
                                emp.name,
                                emp.department,
                                emp.hourly_rate,
                                emp.hours_worked,
                            ]
                        )
            print(f"✓ Payroll records saved to '{self.filename}'.")
        except IOError as e:
            print(f"File Error: Could not save payroll ({e}).")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    e_type = row["type"]
                    emp_id = row["emp_id"]
                    name = row["name"]
                    dept = row["dept"]
                    p1 = float(row["param1"])
                    p2 = float(row["param2"])

                    if e_type == "Salaried":
                        self.employees[emp_id] = SalariedEmployee(
                            emp_id, name, dept, p1, p2
                        )
                    elif e_type == "Hourly":
                        self.employees[emp_id] = HourlyEmployee(
                            emp_id, name, dept, p1, p2
                        )
        except (IOError, KeyError, ValueError) as e:
            print(f"Warning: Issue reading '{self.filename}' ({e}). Starting fresh.")


# ==========================================
# 5. CLI Interface Loop
# ==========================================
def main():
    manager = PayrollManager()

    while True:
        print("\n=== EMPLOYEE PAYROLL SYSTEM ===")
        print("1. Add Salaried Employee")
        print("2. Add Hourly Employee")
        print("3. Search Employee")
        print("4. Generate Individual Payslip")
        print("5. View All Employees")
        print("6. Total Company Payroll Expense")
        print("7. Save Records")
        print("8. Save & Exit")

        choice = input("Enter choice (1-8): ").strip()

        try:
            if choice == "1":
                emp_id = input("Employee ID: ").strip()
                name = input("Full Name: ").strip()
                dept = input("Department: ").strip()
                salary = float(input("Monthly Gross Salary: ").strip())
                deductions = float(input("Monthly Deductions (Taxes/PF): ").strip())
                manager.add_salaried_employee(emp_id, name, dept, salary, deductions)

            elif choice == "2":
                emp_id = input("Employee ID: ").strip()
                name = input("Full Name: ").strip()
                dept = input("Department: ").strip()
                rate = float(input("Hourly Rate: ").strip())
                hours = float(input("Hours Worked this Month: ").strip())
                manager.add_hourly_employee(emp_id, name, dept, rate, hours)

            elif choice == "3":
                emp_id = input("Enter Employee ID: ").strip()
                emp = manager.search_employee(emp_id)
                e_type = "Salaried" if isinstance(emp, SalariedEmployee) else "Hourly"
                print(
                    f"\nFound: [{emp.emp_id}] {emp.name} | Dept: {emp.department} | "
                    f"Type: {e_type} | Net: ₹{emp.calculate_salary():.2f}"
                )

            elif choice == "4":
                emp_id = input("Enter Employee ID for Payslip: ").strip()
                emp = manager.search_employee(emp_id)
                print("\n" + emp.generate_payslip())

            elif choice == "5":
                manager.display_all()

            elif choice == "6":
                total = manager.total_payroll_expense()
                print(f"\nTotal Company Payroll Outlay: ₹{total:,.2f}")

            elif choice == "7":
                manager.save_to_file()

            elif choice == "8":
                manager.save_to_file()
                print("Exiting application. Goodbye!")
                break

            else:
                print("Invalid choice. Select an option from 1 to 8.")

        except (
            EmployeeNotFoundError,
            DuplicateEmployeeError,
            InvalidCompensationError,
        ) as err:
            print(f"Payroll Error: {err}")
        except ValueError as ve:
            print(f"Input Error: Please enter valid numbers ({ve}).")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()