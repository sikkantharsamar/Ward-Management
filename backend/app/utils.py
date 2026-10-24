import secrets
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


def to_dict(obj, exclude=()) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns if c.name not in exclude}


def log_action(db: Session, user_id: Optional[int], action: str, detail: str = "") -> None:
    db.add(models.AuditLog(user_id=user_id, action=action, detail=detail))
    db.commit()


def new_patient_no() -> str:
    return "P" + secrets.token_hex(4).upper()


def bed_location(db: Session, bed_id: int) -> dict:
    bed = db.get(models.Bed, bed_id)
    if bed is None:
        return {}
    ward = db.get(models.Ward, bed.ward_id)
    building = db.get(models.Building, ward.building_id) if ward else None
    return {
        "bed_id": bed.id,
        "bed_number": bed.bed_number,
        "ward_id": ward.id if ward else None,
        "ward_name": ward.name if ward else None,
        "building_name": building.name if building else None,
    }


def current_admission(db: Session, patient_id: int) -> Optional[models.Admission]:
    return db.scalars(
        select(models.Admission).where(
            models.Admission.patient_id == patient_id, models.Admission.status == "admitted"
        )
    ).first()


def patient_for_user(db: Session, user: models.User) -> Optional[models.Patient]:
    return db.scalars(select(models.Patient).where(models.Patient.user_id == user.id)).first()


def doctor_for_user(db: Session, user: models.User) -> Optional[models.Doctor]:
    return db.scalars(select(models.Doctor).where(models.Doctor.user_id == user.id)).first()


def patient_detail(db: Session, patient: models.Patient) -> dict:
    data = to_dict(patient)
    guardians = db.scalars(select(models.Guardian).where(models.Guardian.patient_id == patient.id)).all()
    data["guardians"] = [to_dict(g) for g in guardians]
    adm = current_admission(db, patient.id)
    if adm:
        info = bed_location(db, adm.bed_id)
        info.update({"admission_id": adm.id, "admitted_at": adm.admitted_at, "diagnosis": adm.diagnosis})
        data["current_admission"] = info
    else:
        data["current_admission"] = None
    return data


def alert_to_dict(db: Session, alert: models.Alert) -> dict:
    data = to_dict(alert)
    data.update(bed_location(db, alert.bed_id))
    patient = db.get(models.Patient, alert.patient_id) if alert.patient_id else None
    data["patient_name"] = patient.full_name if patient else None
    data["allergies"] = patient.allergies if patient else None
    data["medical_condition"] = patient.medical_condition if patient else None
    data["isolation_status"] = patient.isolation_status if patient else False
    data["special_needs"] = patient.special_needs if patient else None
    return data
