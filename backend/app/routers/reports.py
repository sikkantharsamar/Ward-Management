import csv
import io
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import STAFF, require_roles
from ..models import Admission, Alert, Appointment, AuditLog, Bed, InventoryItem, Patient, User
from ..timeutil import utcnow
from ..utils import alert_to_dict, to_dict

router = APIRouter(prefix="/reports", tags=["reports"])


def _seconds(start: Optional[datetime], end: Optional[datetime]) -> Optional[int]:
    return int((end - start).total_seconds()) if start and end else None


def _alert_rows(db: Session, start: Optional[datetime], end: Optional[datetime]) -> list:
    stmt = select(Alert).order_by(Alert.created_at.desc())
    if start:
        stmt = stmt.where(Alert.created_at >= start.replace(tzinfo=None))
    if end:
        stmt = stmt.where(Alert.created_at <= end.replace(tzinfo=None))
    rows = []
    for alert in db.scalars(stmt.limit(2000)).all():
        row = alert_to_dict(db, alert)
        row["response_seconds"] = _seconds(alert.created_at, alert.acknowledged_at)
        row["resolution_seconds"] = _seconds(alert.created_at, alert.resolved_at)
        rows.append(row)
    return rows


@router.get("/summary")
def summary(db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    def count(stmt):
        return db.scalar(stmt) or 0

    today_start = utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return {
        "patients_total": count(select(func.count()).select_from(Patient)),
        "patients_admitted": count(select(func.count()).select_from(Admission).where(Admission.status == "admitted")),
        "beds_total": count(select(func.count()).select_from(Bed)),
        "beds_occupied": count(select(func.count()).select_from(Bed).where(Bed.status == "occupied")),
        "beds_available": count(select(func.count()).select_from(Bed).where(Bed.status == "available")),
        "alerts_active": count(select(func.count()).select_from(Alert).where(Alert.status == "active")),
        "alerts_today": count(select(func.count()).select_from(Alert).where(Alert.created_at >= today_start)),
        "low_stock_items": count(
            select(func.count()).select_from(InventoryItem).where(InventoryItem.quantity <= InventoryItem.reorder_level)
        ),
        "appointments_today": count(
            select(func.count()).select_from(Appointment).where(
                Appointment.scheduled_at >= today_start,
                Appointment.scheduled_at < today_start + timedelta(days=1),
                Appointment.status == "scheduled",
            )
        ),
    }


@router.get("/alerts")
def alerts_report(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*STAFF)),
):
    """Alert history with response times. Use for incident investigation."""
    rows = _alert_rows(db, start, end)
    responses = [r["response_seconds"] for r in rows if r["response_seconds"] is not None]
    stats = {
        "total": len(rows),
        "avg_response_seconds": round(sum(responses) / len(responses), 1) if responses else None,
        "max_response_seconds": max(responses) if responses else None,
    }
    return {"stats": stats, "alerts": rows}


@router.get("/alerts.csv")
def alerts_csv(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*STAFF)),
):
    rows = _alert_rows(db, start, end)
    columns = [
        "id", "created_at", "building_name", "ward_name", "bed_number", "patient_name", "source",
        "status", "acknowledged_at", "response_seconds", "resolved_at", "resolution_seconds", "notes",
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=alerts_report.csv"},
    )


@router.get("/audit")
def audit_log(db: Session = Depends(get_db), user: User = Depends(require_roles("admin"))):
    rows = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)).all()
    return [to_dict(r) for r in rows]
