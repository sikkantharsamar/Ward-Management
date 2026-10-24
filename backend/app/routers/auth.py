from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Patient, User
from ..schemas import LoginIn, RegisterIn
from ..security import create_access_token, hash_password, verify_password
from ..utils import log_action, new_patient_no

router = APIRouter(prefix="/auth", tags=["auth"])


def user_out(user: User) -> dict:
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role}


@router.post("/register", status_code=201)
def register_patient(data: RegisterIn, db: Session = Depends(get_db)):
    """Public self-registration. Always creates a PATIENT account (staff are created by an admin)."""
    email = data.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Enter a valid email address")
    if db.scalars(select(User).where(User.email == email)).first():
        raise HTTPException(status_code=409, detail="This email is already registered")
    user = User(
        email=email,
        full_name=data.full_name.strip(),
        hashed_password=hash_password(data.password),
        role="patient",
    )
    db.add(user)
    db.flush()
    db.add(
        Patient(
            user_id=user.id,
            patient_no=new_patient_no(),
            full_name=user.full_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            phone=data.phone,
        )
    )
    db.commit()
    log_action(db, user.id, "register", email)
    return user_out(user)


@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalars(select(User).where(User.email == data.email.strip().lower())).first()
    if user is None or not user.is_active or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id, user.role)
    log_action(db, user.id, "login", user.email)
    return {"access_token": token, "token_type": "bearer", "user": user_out(user)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user_out(user)
