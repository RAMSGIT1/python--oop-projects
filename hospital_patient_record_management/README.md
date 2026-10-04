# Hospital Patient Record System

A Python terminal application designed for clinical record tracking and patient billing under Object-Oriented Programming (OOP) paradigms.

## Features
- Polymorphic medical record tracking: Inpatients (room rates + procedures) and Outpatients (consultations + lab fees).
- Updating clinical diagnoses dynamically.
- Discharge settlement with consolidated invoice calculation.
- Persistent file storage (`patient_records.csv`).
- Guardrails preventing negative billing parameters or malformed identifiers.

## OOP Architecture
1. **Abstraction**: `Patient` is an abstract base class utilizing `abc.ABC` with abstract methods `calculate_bill()` and `get_summary()`.
2. **Inheritance**: `InpatientRecord` and `OutpatientRecord` inherit patient identity fields and implement specialized pricing formulas.
3. **Encapsulation**: Private fields (`__diagnosis`, `__days_admitted`, `__consultation_fee`) are safeguarded by properties and boundary-checked methods.
4. **File Handling**: Direct serialization and deserialization of hospital records using Python's `csv` module.
5. **Exception Handling**: Custom exceptions (`PatientNotFoundError`, `DuplicatePatientError`, `InvalidBillingError`) manage runtime errors.

## How to Run
```bash
python hospital_management.py