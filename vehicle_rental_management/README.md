# Vehicle Rental Management System

A Python console application modeling vehicle cataloging, rental bookings, return settlements, and dynamic rate calculation under Object-Oriented Programming (OOP) paradigms.

## Features
- **Polymorphic Pricing Models**:
  - **Car**: Standard daily rate plus daily insurance surcharge.
  - **Van**: Daily rate plus tonnage-based cargo capacity charge.
- **Rental Workflows**: Book vehicles with renter association and state validation.
- **Return & Settlement**: Calculate accurate final charges based on duration of use.
- **Catalog Filtering**: Query available vehicles versus full fleet inventory.
- **Data Persistence**: Read and write vehicle records using standard CSV storage (`vehicles.csv`).

## OOP Architecture
1. **Abstraction**: `Vehicle` serves as an abstract base class using `abc.ABC` with abstract methods `calculate_rental(days)` and `get_details()`.
2. **Inheritance**: `Car` and `Van` inherit common identity and booking mechanics from `Vehicle`.
3. **Encapsulation**: Attributes `__daily_rate`, `__is_rented`, and `__rented_by` are private and altered solely through guarded public methods.
4. **File Handling**: Automatic loading and serialization using Python's standard `csv` library.
5. **Exception Handling**: Domain-specific custom exceptions (`VehicleNotFoundError`, `VehicleUnavailableError`, `VehicleNotRentedError`, `DuplicateVehicleError`, `InvalidRentalDurationError`).

## File Structure
- `vehicle_rental.py`: Main executable containing the class hierarchy, manager, and CLI menu.
- `vehicles.csv`: Persistent database file storing car and van records.
- `README.md`: System documentation and architectural overview.

## How to Run
```bash
python vehicle_rental.py