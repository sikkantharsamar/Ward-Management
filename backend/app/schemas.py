"""Input (request body) models. Output is returned as plain dicts built in the routers."""
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

Role = Literal["admin", "doctor", "nurse", "patient"]


class LoginIn(BaseModel):
    email: str
    password: str


class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1)
    role: Role
    specialization: Optional[str] = None
    phone: Optional[str] = None
    ward_id: Optional[int] = None


class ActiveIn(BaseModel):
    is_active: bool


class PatientIn(BaseModel):
    full_name: str = Field(min_length=1)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    allergies: Optional[str] = None
    medical_condition: Optional[str] = None
    isolation_status: bool = False
    special_needs: Optional[str] = None


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    allergies: Optional[str] = None
    medical_condition: Optional[str] = None
    isolation_status: Optional[bool] = None
    special_needs: Optional[str] = None


class GuardianIn(BaseModel):
    full_name: str = Field(min_length=1)
    relationship_type: Optional[str] = None
    phone: Optional[str] = None


class BuildingIn(BaseModel):
    name: str = Field(min_length=1)


class WardIn(BaseModel):
    building_id: int
    name: str = Field(min_length=1)
    ward_type: str = "general"


class BedIn(BaseModel):
    ward_id: int
    bed_number: str = Field(min_length=1)
    device_key: Optional[str] = None


class BedStatusIn(BaseModel):
    status: Literal["available", "occupied", "maintenance"]


class AdmissionIn(BaseModel):
    patient_id: int
    bed_id: int
    doctor_id: Optional[int] = None
    nurse_id: Optional[int] = None
    diagnosis: Optional[str] = None


class TransferIn(BaseModel):
    new_bed_id: int


class AppointmentIn(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: int
    scheduled_at: datetime
    reason: Optional[str] = None


class AppointmentStatusIn(BaseModel):
    status: Literal["scheduled", "completed", "cancelled"]


class PrescriptionIn(BaseModel):
    patient_id: int
    medicine_name: str = Field(min_length=1)
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    item_id: Optional[int] = None
    admission_id: Optional[int] = None


class DispenseIn(BaseModel):
    quantity: int = Field(1, ge=1)


class InventoryIn(BaseModel):
    name: str = Field(min_length=1)
    category: Literal["medicine", "supply"] = "medicine"
    unit: str = "unit"
    quantity: int = Field(0, ge=0)
    reorder_level: int = Field(10, ge=0)
    ward_id: Optional[int] = None
    expiry_date: Optional[date] = None


class AdjustIn(BaseModel):
    change: int
    reason: str = Field(min_length=1)


class DeviceAlertIn(BaseModel):
    source: Literal["bedside_button", "wearable"] = "bedside_button"


class ManualAlertIn(BaseModel):
    bed_id: int
    notes: Optional[str] = None


class ResolveIn(BaseModel):
    notes: Optional[str] = None
