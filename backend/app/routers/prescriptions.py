from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Doctor, InventoryItem, Patient, Prescription, StockMovement, User
from ..schemas import DispenseIn, PrescriptionIn
from ..utils import doctor_for_user, log_action, patient_for_user, to_dict

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


def prescription_out(db: Session, rx: Prescription) -> dict:
    data = to_dict(rx)
    patient = db.get(Patient, rx.patient_id)
    doctor = db.get(Doctor, rx.doctor_id)
    doctor_user = db.get(User, doctor.user_id) if doctor else None
    data["patient_name"] = patient.full_name if patient else None
    data["doctor_name"] = doctor_user.full_name if doctor_user else None
    return data


@router.post("", status_code=201)
def create_prescription(
    data: PrescriptionIn, db: Session = Depends(get_db), user: User = Depends(require_roles("doctor"))
):
    doctor = doctor_for_user(db, user)
    if doctor is None:
        raise HTTPException(status_code=400, detail="This account has no doctor profile")
    if db.get(Patient, data.patient_id) is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    if data.item_id and db.get(InventoryItem, data.item_id) is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    rx = Prescription(doctor_id=doctor.id, **data.model_dump())
    db.add(rx)
    db.commit()
    log_action(db, user.id, "create_prescription", f"prescription {rx.id}")
    return prescription_out(db, rx)


@router.get("")
def list_prescriptions(status: str = "", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Prescription).order_by(Prescription.created_at.desc())
    if user.role == "patient":
        patient = patient_for_user(db, user)
        if patient is None:
            return []
        stmt = stmt.where(Prescription.patient_id == patient.id)
    elif user.role == "doctor":
        doctor = doctor_for_user(db, user)
        if doctor is None:
            return []
        stmt = stmt.where(Prescription.doctor_id == doctor.id)
    if status:
        stmt = stmt.where(Prescription.status == status)
    return [prescription_out(db, r) for r in db.scalars(stmt.limit(300)).all()]


@router.post("/{prescription_id}/dispense")
def dispense(
    prescription_id: int,
    data: DispenseIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "nurse")),
):
    """Marks the prescription dispensed and, if it is linked to an inventory item, deducts the stock."""
    rx = db.get(Prescription, prescription_id)
    if rx is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    if rx.status == "dispensed":
        raise HTTPException(status_code=409, detail="Already dispensed")
    if rx.item_id:
        item = db.get(InventoryItem, rx.item_id)
        if item.quantity < data.quantity:
            raise HTTPException(status_code=409, detail=f"Not enough stock (only {item.quantity} available)")
        item.quantity -= data.quantity
        db.add(
            StockMovement(
                item_id=item.id, change=-data.quantity, reason=f"Dispensed prescription #{rx.id}", user_id=user.id
            )
        )
    rx.status = "dispensed"
    db.commit()
    log_action(db, user.id, "dispense", f"prescription {rx.id}")
    return prescription_out(db, rx)
