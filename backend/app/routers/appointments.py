from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Appointment, Doctor, Patient, User
from ..schemas import AppointmentIn, AppointmentStatusIn
from ..utils import doctor_for_user, log_action, patient_for_user, to_dict

router = APIRouter(prefix="/appointments", tags=["appointments"])


def appointment_out(db: Session, appt: Appointment) -> dict:
    data = to_dict(appt)
    patient = db.get(Patient, appt.patient_id)
    doctor = db.get(Doctor, appt.doctor_id)
    doctor_user = db.get(User, doctor.user_id) if doctor else None
    data["patient_name"] = patient.full_name if patient else None
    data["doctor_name"] = doctor_user.full_name if doctor_user else None
    data["specialization"] = doctor.specialization if doctor else None
    return data


@router.post("", status_code=201)
def create_appointment(data: AppointmentIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "patient":
        patient = patient_for_user(db, user)
        if patient is None:
            raise HTTPException(status_code=404, detail="No patient record linked to this account")
        patient_id = patient.id
    else:
        if data.patient_id is None:
            raise HTTPException(status_code=400, detail="patient_id is required")
        patient_id = data.patient_id
        if db.get(Patient, patient_id) is None:
            raise HTTPException(status_code=404, detail="Patient not found")
    if db.get(Doctor, data.doctor_id) is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    when = data.scheduled_at.replace(tzinfo=None)
    clash = db.scalars(
        select(Appointment).where(
            Appointment.doctor_id == data.doctor_id,
            Appointment.scheduled_at == when,
            Appointment.status == "scheduled",
        )
    ).first()
    if clash:
        raise HTTPException(status_code=409, detail="The doctor already has an appointment at that time")
    appt = Appointment(patient_id=patient_id, doctor_id=data.doctor_id, scheduled_at=when, reason=data.reason)
    db.add(appt)
    db.commit()
    log_action(db, user.id, "create_appointment", f"appointment {appt.id}")
    return appointment_out(db, appt)


@router.get("")
def list_appointments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Appointment).order_by(Appointment.scheduled_at)
    if user.role == "patient":
        patient = patient_for_user(db, user)
        if patient is None:
            return []
        stmt = stmt.where(Appointment.patient_id == patient.id)
    elif user.role == "doctor":
        doctor = doctor_for_user(db, user)
        if doctor is None:
            return []
        stmt = stmt.where(Appointment.doctor_id == doctor.id)
    return [appointment_out(db, a) for a in db.scalars(stmt.limit(300)).all()]


@router.patch("/{appointment_id}/status")
def update_status(
    appointment_id: int, data: AppointmentStatusIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    appt = db.get(Appointment, appointment_id)
    if appt is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if user.role == "patient":
        patient = patient_for_user(db, user)
        if patient is None or appt.patient_id != patient.id or data.status != "cancelled":
            raise HTTPException(status_code=403, detail="Patients can only cancel their own appointments")
    elif user.role == "doctor":
        doctor = doctor_for_user(db, user)
        if doctor is None or appt.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="This is not your appointment")
    appt.status = data.status
    db.commit()
    log_action(db, user.id, "appointment_status", f"appointment {appt.id} -> {data.status}")
    return appointment_out(db, appt)
