import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import ADMIN, STAFF, require_roles
from ..models import Admission, Alert, Bed, Building, Patient, User, Ward
from ..schemas import BedIn, BedStatusIn, BuildingIn, WardIn
from ..utils import log_action, to_dict

router = APIRouter(tags=["wards"])


@router.get("/buildings")
def list_buildings(db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    return [to_dict(b) for b in db.scalars(select(Building).order_by(Building.name)).all()]


@router.post("/buildings", status_code=201)
def create_building(data: BuildingIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*ADMIN))):
    if db.scalars(select(Building).where(Building.name == data.name)).first():
        raise HTTPException(status_code=409, detail="Building already exists")
    building = Building(name=data.name)
    db.add(building)
    db.commit()
    log_action(db, user.id, "create_building", data.name)
    return to_dict(building)


@router.get("/wards")
def list_wards(db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    result = []
    for ward in db.scalars(select(Ward).order_by(Ward.id)).all():
        building = db.get(Building, ward.building_id)
        total = db.scalar(select(func.count()).select_from(Bed).where(Bed.ward_id == ward.id))
        occupied = db.scalar(
            select(func.count()).select_from(Bed).where(Bed.ward_id == ward.id, Bed.status == "occupied")
        )
        item = to_dict(ward)
        item.update({"building_name": building.name if building else None, "bed_count": total, "occupied_count": occupied})
        result.append(item)
    return result


@router.post("/wards", status_code=201)
def create_ward(data: WardIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*ADMIN))):
    if db.get(Building, data.building_id) is None:
        raise HTTPException(status_code=404, detail="Building not found")
    ward = Ward(**data.model_dump())
    db.add(ward)
    db.commit()
    log_action(db, user.id, "create_ward", data.name)
    return to_dict(ward)


@router.post("/beds", status_code=201)
def create_bed(data: BedIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*ADMIN))):
    """Creates a bed and its device key. Give the device key to the hardware team to flash into the button unit."""
    if db.get(Ward, data.ward_id) is None:
        raise HTTPException(status_code=404, detail="Ward not found")
    device_key = data.device_key or secrets.token_urlsafe(16)
    if db.scalars(select(Bed).where(Bed.device_key == device_key)).first():
        raise HTTPException(status_code=409, detail="This device key is already used")
    bed = Bed(ward_id=data.ward_id, bed_number=data.bed_number, device_key=device_key)
    db.add(bed)
    db.commit()
    log_action(db, user.id, "create_bed", f"ward {data.ward_id} bed {data.bed_number}")
    return to_dict(bed)


@router.get("/wards/{ward_id}/beds")
def list_beds(ward_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    """Live bed map data: status, current patient and alert state for every bed in a ward."""
    if db.get(Ward, ward_id) is None:
        raise HTTPException(status_code=404, detail="Ward not found")
    beds = db.scalars(select(Bed).where(Bed.ward_id == ward_id).order_by(Bed.id)).all()
    result = []
    for bed in beds:
        item = to_dict(bed, exclude=() if user.role == "admin" else ("device_key",))
        adm = db.scalars(select(Admission).where(Admission.bed_id == bed.id, Admission.status == "admitted")).first()
        patient = db.get(Patient, adm.patient_id) if adm else None
        item["admission_id"] = adm.id if adm else None
        item["patient_id"] = patient.id if patient else None
        item["patient_name"] = patient.full_name if patient else None
        item["isolation_status"] = patient.isolation_status if patient else False
        open_alert = db.scalars(
            select(Alert).where(Alert.bed_id == bed.id, Alert.status.in_(("active", "acknowledged")))
            .order_by(Alert.created_at.desc())
        ).first()
        item["alert_status"] = open_alert.status if open_alert else None
        result.append(item)
    return result


@router.patch("/beds/{bed_id}/status")
def set_bed_status(
    bed_id: int, data: BedStatusIn, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "nurse"))
):
    bed = db.get(Bed, bed_id)
    if bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    bed.status = data.status
    db.commit()
    log_action(db, user.id, "set_bed_status", f"bed {bed_id} -> {data.status}")
    return to_dict(bed, exclude=("device_key",))
