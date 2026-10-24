from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import STAFF, get_current_user, require_roles
from ..models import Guardian, Patient, User
from ..schemas import GuardianIn, PatientIn, PatientUpdate
from ..utils import log_action, new_patient_no, patient_detail, patient_for_user, to_dict

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("")
def list_patients(
    q: str = Query("", description="Search by name or patient number"),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*STAFF)),
):
    stmt = select(Patient).order_by(Patient.full_name)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Patient.full_name.ilike(like), Patient.patient_no.ilike(like)))
    return [to_dict(p) for p in db.scalars(stmt.limit(200)).all()]


@router.post("", status_code=201)
def create_patient(data: PatientIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    """Create a patient record for a walk-in / admitted patient who has no website login."""
    patient = Patient(patient_no=new_patient_no(), **data.model_dump())
    db.add(patient)
    db.commit()
    log_action(db, user.id, "create_patient", patient.patient_no)
    return patient_detail(db, patient)


@router.get("/me")
def my_record(db: Session = Depends(get_db), user: User = Depends(require_roles("patient"))):
    patient = patient_for_user(db, user)
    if patient is None:
        raise HTTPException(status_code=404, detail="No patient record linked to this account")
    return patient_detail(db, patient)


@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    if user.role == "patient" and patient.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only view your own record")
    return patient_detail(db, patient)


@router.patch("/{patient_id}")
def update_patient(
    patient_id: int, data: PatientUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))
):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    log_action(db, user.id, "update_patient", patient.patient_no)
    return patient_detail(db, patient)


@router.post("/{patient_id}/guardians", status_code=201)
def add_guardian(
    patient_id: int, data: GuardianIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))
):
    if db.get(Patient, patient_id) is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    guardian = Guardian(patient_id=patient_id, **data.model_dump())
    db.add(guardian)
    db.commit()
    return to_dict(guardian)
