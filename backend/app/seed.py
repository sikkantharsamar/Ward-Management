"""Creates demo data. Run from the backend folder:  python -m app.seed"""
from datetime import date, datetime, timedelta

from sqlalchemy import select

from . import models
from .database import Base, SessionLocal, engine
from .security import hash_password
from .timeutil import utcnow

DEMO_PASSWORD = "Password@123"


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.scalars(select(models.User).where(models.User.email == "admin@ward.local")).first():
            print("Demo data already exists. Delete ward.db to start fresh.")
            return

        def make_user(email, name, role):
            user = models.User(email=email, full_name=name, hashed_password=hash_password(DEMO_PASSWORD), role=role)
            db.add(user)
            db.flush()
            return user

        make_user("admin@ward.local", "Demo Admin", "admin")
        doctor_user = make_user("doctor@ward.local", "Dr. Demo Doctor", "doctor")
        nurse_user = make_user("nurse@ward.local", "Nurse Demo", "nurse")
        patient_user = make_user("patient@ward.local", "Demo Patient", "patient")

        building = models.Building(name="Main Building")
        db.add(building)
        db.flush()
        ward = models.Ward(building_id=building.id, name="Ward A (Infectious Diseases)", ward_type="isolation")
        db.add(ward)
        db.flush()

        doctor = models.Doctor(user_id=doctor_user.id, specialization="Infectious Diseases", phone="0771111111")
        nurse = models.Nurse(user_id=nurse_user.id, ward_id=ward.id, phone="0772222222")
        patient = models.Patient(
            user_id=patient_user.id,
            patient_no="P0000001",
            full_name="Demo Patient",
            date_of_birth=date(1990, 5, 17),
            gender="Female",
            phone="0773333333",
            allergies="Penicillin",
            medical_condition="Dengue fever",
            special_needs="Weak grip: cannot press the normal button",
        )
        db.add_all([doctor, nurse, patient])
        db.flush()
        db.add(models.Guardian(patient_id=patient.id, full_name="Demo Guardian", relationship_type="Mother", phone="0774444444"))

        beds = []
        for n in range(1, 7):
            bed = models.Bed(ward_id=ward.id, bed_number=f"A{n}", device_key=f"demo-key-bed-{n}")
            db.add(bed)
            beds.append(bed)
        db.flush()

        beds[0].status = "occupied"
        db.add(
            models.Admission(
                patient_id=patient.id, bed_id=beds[0].id, doctor_id=doctor.id, nurse_id=nurse.id, diagnosis="Dengue fever"
            )
        )

        paracetamol = models.InventoryItem(name="Paracetamol 500mg", category="medicine", unit="tablet", quantity=200, reorder_level=50)
        db.add_all(
            [
                paracetamol,
                models.InventoryItem(name="IV Saline 500ml", category="supply", unit="bag", quantity=40, reorder_level=20),
                models.InventoryItem(name="Surgical Gloves", category="supply", unit="box", quantity=12, reorder_level=30),
                models.InventoryItem(name="Face Masks", category="supply", unit="box", quantity=80, reorder_level=25),
            ]
        )
        db.add(
            models.Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                scheduled_at=datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=1, hours=1),
                reason="Review",
            )
        )
        db.commit()
        print("Demo data created. All demo accounts use the password:", DEMO_PASSWORD)
        print("  admin@ward.local   (admin)")
        print("  doctor@ward.local  (doctor)")
        print("  nurse@ward.local   (nurse)")
        print("  patient@ward.local (patient, admitted to bed A1)")
        print("Demo device keys: demo-key-bed-1 ... demo-key-bed-6")
    finally:
        db.close()


if __name__ == "__main__":
    run()
