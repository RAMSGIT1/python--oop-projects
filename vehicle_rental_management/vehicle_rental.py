import csv
import os
from abc import ABC, abstractmethod


# ==========================================
# 1. Custom Exceptions
# ==========================================
class VehicleNotFoundError(Exception):
    """Raised when a vehicle ID does not exist."""
    pass


class VehicleUnavailableError(Exception):
    """Raised when trying to rent a vehicle that is already booked."""
    pass


class VehicleNotRentedError(Exception):
    """Raised when trying to return a vehicle that is not rented out."""
    pass


class DuplicateVehicleError(Exception):
    """Raised when registering an ID that already exists."""
    pass


class InvalidRentalDurationError(Exception):
    """Raised when requested rental days are non-positive."""
    pass


# ==========================================
# 2. Abstraction: Base Class
# ==========================================
class Vehicle(ABC):
    """Abstract base class representing a generic rental vehicle."""

    def __init__(self, vehicle_id: str, make: str, model: str, daily_rate: float,
                 is_rented: bool = False, rented_by: str = ""):
        self._vehicle_id = vehicle_id  # Protected
        self._make = make
        self._model = model
        self.__daily_rate = daily_rate  # Private
        self.__is_rented = is_rented
        self.__rented_by = rented_by

    @property
    def vehicle_id(self) -> str:
        return self._vehicle_id

    @property
    def make(self) -> str:
        return self._make

    @property
    def model(self) -> str:
        return self._model

    @property
    def daily_rate(self) -> float:
        return self.__daily_rate

    @property
    def is_rented(self) -> bool:
        return self.__is_rented

    @property
    def rented_by(self) -> str:
        return self.__rented_by

    def rent_vehicle(self, customer_name: str):
        if self.__is_rented:
            raise VehicleUnavailableError(
                f"Vehicle '{self._vehicle_id}' is already rented to {self.__rented_by}."
            )
        if not customer_name.strip():
            raise ValueError("Customer name cannot be blank.")
        self.__is_rented = True
        self.__rented_by = customer_name.strip()

    def return_vehicle(self):
        if not self.__is_rented:
            raise VehicleNotRentedError(
                f"Vehicle '{self._vehicle_id}' is not currently marked as rented."
            )
        self.__is_rented = False
        self.__rented_by = ""

    @abstractmethod
    def calculate_rental(self, days: int) -> float:
        """Calculates total rental cost for a given duration in days."""
        pass

    @abstractmethod
    def get_details(self) -> str:
        """Formatted vehicle details and status."""
        pass


# ==========================================
# 3. Inheritance & Encapsulation: Subclasses
# ==========================================
class Car(Vehicle):
    """Passenger car with standard insurance fee."""

    INSURANCE_PER_DAY = 200.0

    def __init__(self, vehicle_id: str, make: str, model: str, daily_rate: float,
                 seats: int, is_rented: bool = False, rented_by: str = ""):
        super().__init__(vehicle_id, make, model, daily_rate, is_rented, rented_by)
        self.__seats = seats

    @property
    def seats(self) -> int:
        return self.__seats

    def calculate_rental(self, days: int) -> float:
        if days <= 0:
            raise InvalidRentalDurationError("Rental duration must be at least 1 day.")
        base = self.daily_rate * days
        insurance = self.INSURANCE_PER_DAY * days
        return round(base + insurance, 2)

    def get_details(self) -> str:
        status = f"Rented to {self.rented_by}" if self.is_rented else "Available"
        return (f"Type: Car | ID: {self.vehicle_id:<6} | Make: {self.make:<10} | Model: {self.model:<10} | "
                f"Seats: {self.__seats:<2} | Rate: ₹{self.daily_rate:<7.2f}/day | Status: {status}")


class Van(Vehicle):
    """Cargo / passenger van with load surcharge."""

    SURCHARGE_PER_TON = 350.0

    def __init__(self, vehicle_id: str, make: str, model: str, daily_rate: float,
                 cargo_tonnage: float, is_rented: bool = False, rented_by: str = ""):
        super().__init__(vehicle_id, make, model, daily_rate, is_rented, rented_by)
        self.__cargo_tonnage = cargo_tonnage

    @property
    def cargo_tonnage(self) -> float:
        return self.__cargo_tonnage

    def calculate_rental(self, days: int) -> float:
        if days <= 0:
            raise InvalidRentalDurationError("Rental duration must be at least 1 day.")
        base = self.daily_rate * days
        capacity_fee = self.__cargo_tonnage * self.SURCHARGE_PER_TON * days
        return round(base + capacity_fee, 2)

    def get_details(self) -> str:
        status = f"Rented to {self.rented_by}" if self.is_rented else "Available"
        return (f"Type: Van | ID: {self.vehicle_id:<6} | Make: {self.make:<10} | Model: {self.model:<10} | "
                f"Load: {self.__cargo_tonnage:<3.1f}T | Rate: ₹{self.daily_rate:<7.2f}/day | Status: {status}")


# ==========================================
# 4. Management Class: RentalManager
# ==========================================
class RentalManager:
    """Manages vehicle inventory, bookings, invoicing, and CSV persistence."""

    def __init__(self, filename: str = "vehicles.csv"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, filename)
        self.vehicles: dict[str, Vehicle] = {}
        self.load_from_file()

    def add_car(self, v_id: str, make: str, model: str, rate: float, seats: int):
        if v_id in self.vehicles:
            raise DuplicateVehicleError(f"Vehicle ID '{v_id}' already registered.")
        car = Car(v_id, make, model, rate, seats)
        self.vehicles[v_id] = car
        print(f"✓ Car '{make} {model}' added successfully.")

    def add_van(self, v_id: str, make: str, model: str, rate: float, tonnage: float):
        if v_id in self.vehicles:
            raise DuplicateVehicleError(f"Vehicle ID '{v_id}' already registered.")
        van = Van(v_id, make, model, rate, tonnage)
        self.vehicles[v_id] = van
        print(f"✓ Van '{make} {model}' added successfully.")

    def search_vehicle(self, v_id: str) -> Vehicle:
        if v_id not in self.vehicles:
            raise VehicleNotFoundError(f"Vehicle '{v_id}' not found.")
        return self.vehicles[v_id]

    def rent_vehicle(self, v_id: str, customer: str, days: int) -> float:
        vehicle = self.search_vehicle(v_id)
        vehicle.rent_vehicle(customer)
        total_fare = vehicle.calculate_rental(days)
        print(f"✓ '{vehicle.make} {vehicle.model}' rented to {customer} for {days} day(s).")
        print(f"  Estimated total charge: ₹{total_fare:,.2f}")
        return total_fare

    def return_vehicle(self, v_id: str, days_used: int) -> float:
        vehicle = self.search_vehicle(v_id)
        fare = vehicle.calculate_rental(days_used)
        borrower = vehicle.rented_by
        vehicle.return_vehicle()
        print(f"✓ '{vehicle.make} {vehicle.model}' returned by {borrower}.")
        print(f"  Final rental settlement ({days_used} days): ₹{fare:,.2f}")
        return fare

    def display_all(self, only_available: bool = False):
        items = [v for v in self.vehicles.values() if not v.is_rented] if only_available else list(self.vehicles.values())
        header = "AVAILABLE VEHICLES" if only_available else "FULL VEHICLE FLEET"

        if not items:
            print(f"No records found for: {header}.")
            return

        print("\n" + "=" * 90)
        print(header.center(90))
        print("=" * 90)
        for v in items:
            print(v.get_details())
        print("=" * 90)

    # --- File Handling (CSV) ---
    def save_to_file(self):
        try:
            with open(self.filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["type", "id", "make", "model", "rate", "spec", "is_rented", "rented_by"])
                for v in self.vehicles.values():
                    if isinstance(v, Car):
                        v_type = "Car"
                        spec = v.seats
                    elif isinstance(v, Van):
                        v_type = "Van"
                        spec = v.cargo_tonnage
                    else:
                        raise TypeError(f"Unsupported vehicle type: {type(v).__name__}")

                    writer.writerow([v_type, v.vehicle_id, v.make, v.model, v.daily_rate, spec, v.is_rented, v.rented_by])
            print(f"✓ Vehicle records saved to '{self.filename}'.")
        except IOError as e:
            print(f"File Error: Could not save vehicles ({e}).")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    v_type = row["type"]
                    v_id = row["id"]
                    make = row["make"]
                    model = row["model"]
                    rate = float(row["rate"])
                    spec = float(row["spec"])
                    is_rented = row["is_rented"].lower() == "true"
                    rented_by = row.get("rented_by", "")

                    if v_type == "Car":
                        self.vehicles[v_id] = Car(v_id, make, model, rate, int(spec), is_rented, rented_by)
                    elif v_type == "Van":
                        self.vehicles[v_id] = Van(v_id, make, model, rate, spec, is_rented, rented_by)
        except (IOError, KeyError, ValueError) as e:
            print(f"Warning: Issue reading '{self.filename}' ({e}). Starting fresh.")


# ==========================================
# 5. CLI Interface Loop
# ==========================================
def main():
    manager = RentalManager()

    while True:
        print("\n=== VEHICLE RENTAL MANAGEMENT SYSTEM ===")
        print("1. Add Car")
        print("2. Add Van")
        print("3. Rent Vehicle")
        print("4. Return Vehicle & Settle Bill")
        print("5. Search Vehicle")
        print("6. Display Available Vehicles")
        print("7. Display Full Fleet")
        print("8. Save Records")
        print("9. Save & Exit")

        choice = input("Enter choice (1-9): ").strip()

        try:
            if choice == "1":
                v_id = input("Vehicle ID (e.g. C01): ").strip()
                make = input("Make (e.g. Maruti): ").strip()
                model = input("Model (e.g. Swift): ").strip()
                rate = float(input("Daily Rental Rate (₹): ").strip())
                seats = int(input("Number of Seats: ").strip())
                manager.add_car(v_id, make, model, rate, seats)

            elif choice == "2":
                v_id = input("Vehicle ID (e.g. V01): ").strip()
                make = input("Make (e.g. Tata): ").strip()
                model = input("Model (e.g. Winger): ").strip()
                rate = float(input("Daily Rental Rate (₹): ").strip())
                tonnage = float(input("Cargo Capacity (Tons): ").strip())
                manager.add_van(v_id, make, model, rate, tonnage)

            elif choice == "3":
                v_id = input("Enter Vehicle ID to rent: ").strip()
                cust = input("Enter Customer Name: ").strip()
                days = int(input("Enter Rental Duration (Days): ").strip())
                manager.rent_vehicle(v_id, cust, days)

            elif choice == "4":
                v_id = input("Enter Vehicle ID to return: ").strip()
                days = int(input("Enter Actual Days Used: ").strip())
                manager.return_vehicle(v_id, days)

            elif choice == "5":
                v_id = input("Enter Vehicle ID to search: ").strip()
                vehicle = manager.search_vehicle(v_id)
                print(f"\n{vehicle.get_details()}")

            elif choice == "6":
                manager.display_all(only_available=True)

            elif choice == "7":
                manager.display_all(only_available=False)

            elif choice == "8":
                manager.save_to_file()

            elif choice == "9":
                manager.save_to_file()
                print("Exiting application. Goodbye!")
                break

            else:
                print("Invalid choice. Select from 1 to 9.")

        except (VehicleNotFoundError, VehicleUnavailableError, VehicleNotRentedError,
                DuplicateVehicleError, InvalidRentalDurationError) as err:
            print(f"Rental Operation Error: {err}")
        except ValueError as ve:
            print(f"Input Error: Please provide valid entries ({ve}).")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()