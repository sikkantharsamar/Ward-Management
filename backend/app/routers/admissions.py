from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import STAFF, require_roles
from ..models import Admission, Bed, BedTransfer, Doctor, Nurse, Patient, User
from ..schemas import AdmissionIn, TransferIn
from ..timeutil import utcnow
from ..utils import bed_location, current_admission, log_action, to_dict

router = APIRouter(prefix="/admissions", tags=["admissions"])


def admission_out(db: Session, adm: Admission) -> dict:
    data = to_dict(adm)
    data.update(bed_location(db, adm.bed_id))
    patient = db.get(Patient, adm.patient_id)
    data["patient_name"] = patient.full_name if patient else None
    data["patient_no"] = patient.patient_no if patient else None
    return data


@router.post("", status_code=201)
def admit_patient(data: AdmissionIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    patient = db.get(Patient, data.patient_id)
    bed = db.get(Bed, data.bed_id)
    if patient is None or bed is None:
        raise HTTPException(status_code=404, detail="Patient or bed not found")
    if bed.status != "available":
        raise HTTPException(status_code=409, detail=f"Bed is {bed.status}, not available")
    if current_admission(db, patient.id):
        raise HTTPException(status_code=409, detail="Patient is already admitted")
    if data.doctor_id and db.get(Doctor, data.doctor_id) is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if data.nurse_id and db.get(Nurse, data.nurse_id) is None:
        raise HTTPException(status_code=404, detail="Nurse not found")
    adm = Admission(**data.model_dump())
    bed.status = "occupied"
    db.add(adm)
    db.commit()
    log_action(db, user.id, "admit_patient", f"patient {patient.id} -> bed {bed.id}")
    return admission_out(db, adm)


@router.get("")
def list_admissions(status: str = "admitted", db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    stmt = select(Admission).order_by(Admission.admitted_at.desc())
    if status != "all":
        stmt = stmt.where(Admission.status == status)
    return [admission_out(db, a) for a in db.scalars(stmt.limit(200)).all()]


@router.post("/{admission_id}/transfer")
def transfer_bed(
    admission_id: int, data: TransferIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))
):
    adm = db.get(Admission, admission_id)
    if adm is None:
        raise HTTPException(status_code=404, detail="Admission not found")
    if adm.status != "admitted":
        raise HTTPException(status_code=409, detail="Patient is no longer admitted")
    new_bed = db.get(Bed, data.new_bed_id)
    if new_bed is None:
        raise HTTPException(status_code=404, detail="New bed not found")
    if new_bed.status != "available":
        raise HTTPException(status_code=409, detail=f"New bed is {new_bed.status}")
    old_bed = db.get(Bed, adm.bed_id)
    db.add(BedTransfer(admission_id=adm.id, from_bed_id=adm.bed_id, to_bed_id=new_bed.id, transferred_by=user.id))
    if old_bed:
        old_bed.status = "available"
    new_bed.status = "occupied"
    adm.bed_id = new_bed.id
    db.commit()
    log_action(db, user.id, "transfer_bed", f"admission {adm.id} -> bed {new_bed.id}")
    return admission_out(db, adm)


@router.post("/{admission_id}/discharge")
def discharge(admission_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    adm = db.get(Admission, admission_id)
    if adm is None:
        raise HTTPException(status_code=404, detail="Admission not found")
    if adm.status != "admitted":
        raise HTTPException(status_code=409, detail="Already discharged")
    adm.status = "discharged"
    adm.discharged_at = utcnow()
    bed = db.get(Bed, adm.bed_id)
    if bed:
        bed.status = "available"
    db.commit()
    log_action(db, user.id, "discharge", f"admission {adm.id}")
    return admission_out(db, adm)
