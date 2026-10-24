from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import ADMIN, STAFF, get_current_user, require_roles
from ..models import Doctor, Nurse, Patient, User
from ..schemas import ActiveIn, UserCreate
from ..security import hash_password
from ..utils import log_action, new_patient_no, to_dict

router = APIRouter(tags=["users"])


@router.post("/users", status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), admin: User = Depends(require_roles(*ADMIN))):
    """Admin creates staff (doctor / nurse / admin) or patient accounts."""
    email = data.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Enter a valid email address")
    if db.scalars(select(User).where(User.email == email)).first():
        raise HTTPException(status_code=409, detail="This email is already registered")
    user = User(
        email=email,
        full_name=data.full_name.strip(),
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.flush()
    if data.role == "doctor":
        db.add(Doctor(user_id=user.id, specialization=data.specialization, phone=data.phone))
    elif data.role == "nurse":
        db.add(Nurse(user_id=user.id, ward_id=data.ward_id, phone=data.phone))
    elif data.role == "patient":
        db.add(Patient(user_id=user.id, patient_no=new_patient_no(), full_name=user.full_name, phone=data.phone))
    db.commit()
    log_action(db, admin.id, "create_user", f"{email} ({data.role})")
    return to_dict(user, exclude=("hashed_password",))


@router.get("/users")
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_roles(*ADMIN))):
    users = db.scalars(select(User).order_by(User.id)).all()
    return [to_dict(u, exclude=("hashed_password",)) for u in users]


@router.patch("/users/{user_id}/active")
def set_user_active(
    user_id: int, data: ActiveIn, db: Session = Depends(get_db), admin: User = Depends(require_roles(*ADMIN))
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id and not data.is_active:
        raise HTTPException(status_code=400, detail="You cannot disable your own account")
    user.is_active = data.is_active
    db.commit()
    log_action(db, admin.id, "set_user_active", f"user {user_id} -> {data.is_active}")
    return to_dict(user, exclude=("hashed_password",))


@router.get("/doctors")
def list_doctors(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.execute(select(Doctor, User).join(User, Doctor.user_id == User.id).where(User.is_active == True)).all()  # noqa: E712
    return [
        {"id": d.id, "full_name": u.full_name, "specialization": d.specialization, "phone": d.phone}
        for d, u in rows
    ]


@router.get("/nurses")
def list_nurses(db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    rows = db.execute(select(Nurse, User).join(User, Nurse.user_id == User.id).where(User.is_active == True)).all()  # noqa: E712
    return [{"id": n.id, "full_name": u.full_name, "ward_id": n.ward_id, "phone": n.phone} for n, u in rows]
