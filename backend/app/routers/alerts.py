"""Emergency alerts: the most critical part of the system.

Flow: bed device -> POST /api/alerts/device (with X-Device-Key) -> saved in DB -> pushed over
WebSocket to every logged-in nurse station -> nurse acknowledges -> attends -> resolves.
The device treats an HTTP 200 reply as the ACK. If it gets no ACK it must retry.
"""
from datetime import timedelta

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import ESCALATION_SECONDS
from ..database import SessionLocal, get_db
from ..deps import STAFF, require_roles
from ..models import Admission, Alert, Bed, User
from ..schemas import DeviceAlertIn, ManualAlertIn, ResolveIn
from ..security import decode_token
from ..timeutil import utcnow
from ..utils import alert_to_dict, current_admission, log_action, patient_for_user
from ..websocket_manager import manager

router = APIRouter(prefix="/alerts", tags=["alerts"])


async def create_alert(db: Session, bed: Bed, source: str, notes: str = None, patient_id: int = None):
    """Creates an alert (or re-sounds the existing open one) and pushes it to the nurse stations."""
    existing = db.scalars(select(Alert).where(Alert.bed_id == bed.id, Alert.status == "active")).first()
    if existing:
        await manager.broadcast({"event": "alert_repeat", "alert": alert_to_dict(db, existing)})
        return existing, True
    adm = db.scalars(select(Admission).where(Admission.bed_id == bed.id, Admission.status == "admitted")).first()
    alert = Alert(
        bed_id=bed.id,
        patient_id=adm.patient_id if adm else patient_id,
        source=source,
        status="active",
        notes=notes,
    )
    db.add(alert)
    db.commit()
    await manager.broadcast({"event": "alert_created", "alert": alert_to_dict(db, alert)})
    return alert, False


@router.post("/device")
async def device_alert(
    data: DeviceAlertIn,
    x_device_key: str = Header(..., description="Secret key of the bed device"),
    db: Session = Depends(get_db),
):
    """Called by the bedside button / wearable. No user login; the device key identifies the bed."""
    bed = db.scalars(select(Bed).where(Bed.device_key == x_device_key)).first()
    if bed is None:
        raise HTTPException(status_code=401, detail="Unknown device key")
    alert, duplicate = await create_alert(db, bed, data.source)
    return {"status": "received", "alert_id": alert.id, "duplicate": duplicate}


@router.post("/patient")
async def patient_alert(db: Session = Depends(get_db), user: User = Depends(require_roles("patient"))):
    """Alternative way to call for help from the website, for patients logged in on a phone or tablet."""
    patient = patient_for_user(db, user)
    adm = current_admission(db, patient.id) if patient else None
    if adm is None:
        raise HTTPException(status_code=400, detail="You are not currently admitted to a bed")
    bed = db.get(Bed, adm.bed_id)
    alert, duplicate = await create_alert(db, bed, "patient_web", patient_id=patient.id)
    return {"status": "received", "alert_id": alert.id, "duplicate": duplicate}


@router.post("/manual")
async def manual_alert(
    data: ManualAlertIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))
):
    bed = db.get(Bed, data.bed_id)
    if bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    alert, duplicate = await create_alert(db, bed, "manual", notes=data.notes)
    return {"status": "received", "alert_id": alert.id, "duplicate": duplicate}


@router.get("")
def list_alerts(
    status: str = Query("open", description="open | active | acknowledged | resolved | all"),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*STAFF)),
):
    stmt = select(Alert).order_by(Alert.created_at.desc())
    if status == "open":
        stmt = stmt.where(Alert.status.in_(("active", "acknowledged")))
    elif status != "all":
        stmt = stmt.where(Alert.status == status)
    return [alert_to_dict(db, a) for a in db.scalars(stmt.limit(200)).all()]


@router.get("/overdue")
def overdue_alerts(
    seconds: int = ESCALATION_SECONDS,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*STAFF)),
):
    """Active alerts nobody has acknowledged yet. Use this to build the escalation feature."""
    cutoff = utcnow() - timedelta(seconds=seconds)
    stmt = select(Alert).where(Alert.status == "active", Alert.created_at <= cutoff)
    return [alert_to_dict(db, a) for a in db.scalars(stmt).all()]


@router.post("/{alert_id}/acknowledge")
async def acknowledge(alert_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.status != "active":
        raise HTTPException(status_code=409, detail=f"Alert is already {alert.status}")
    alert.status = "acknowledged"
    alert.acknowledged_at = utcnow()
    alert.acknowledged_by = user.id
    db.commit()
    log_action(db, user.id, "alert_acknowledged", f"alert {alert.id}")
    out = alert_to_dict(db, alert)
    await manager.broadcast({"event": "alert_updated", "alert": out})
    return out


@router.post("/{alert_id}/resolve")
async def resolve(
    alert_id: int, data: ResolveIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))
):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.status == "resolved":
        raise HTTPException(status_code=409, detail="Alert is already resolved")
    now = utcnow()
    if alert.status == "active":
        alert.acknowledged_at = now
        alert.acknowledged_by = user.id
    alert.status = "resolved"
    alert.resolved_at = now
    alert.resolved_by = user.id
    if data.notes:
        alert.notes = data.notes
    db.commit()
    log_action(db, user.id, "alert_resolved", f"alert {alert.id}")
    out = alert_to_dict(db, alert)
    await manager.broadcast({"event": "alert_updated", "alert": out})
    return out


@router.websocket("/ws")
async def alerts_socket(websocket: WebSocket, token: str = Query(...)):
    """Nurse-station live feed. Connect to /api/alerts/ws?token=<JWT>."""
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        await websocket.close(code=4401)
        return
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
    finally:
        db.close()
    if user is None or not user.is_active or user.role not in STAFF:
        await websocket.close(code=4403)
        return
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
