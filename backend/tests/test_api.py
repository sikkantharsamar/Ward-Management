"""Starter tests. Run from the backend folder:  pytest
Needs: pip install pytest httpx
"""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_ward.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.security import hash_password  # noqa: E402

client = TestClient(app)


def setup_function(_):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def make_staff(email, role):
    db = SessionLocal()
    db.add(models.User(email=email, full_name=role.title(), hashed_password=hash_password("Password@123"), role=role))
    db.commit()
    db.close()


def login(email):
    res = client.post("/api/auth/login", json={"email": email, "password": "Password@123"})
    assert res.status_code == 200
    return {"Authorization": "Bearer " + res.json()["access_token"]}


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_patient_register_and_login():
    res = client.post("/api/auth/register", json={"email": "p@x.com", "password": "Password@123", "full_name": "Pat"})
    assert res.status_code == 201
    headers = login("p@x.com")
    assert client.get("/api/patients/me", headers=headers).status_code == 200


def test_patient_cannot_use_staff_endpoints():
    client.post("/api/auth/register", json={"email": "p@x.com", "password": "Password@123", "full_name": "Pat"})
    headers = login("p@x.com")
    assert client.get("/api/patients", headers=headers).status_code == 403
    assert client.get("/api/alerts", headers=headers).status_code == 403


def test_device_alert_flow():
    make_staff("admin@x.com", "admin")
    make_staff("nurse@x.com", "nurse")
    admin = login("admin@x.com")
    building = client.post("/api/buildings", json={"name": "B1"}, headers=admin).json()
    ward = client.post("/api/wards", json={"building_id": building["id"], "name": "W1"}, headers=admin).json()
    bed = client.post("/api/beds", json={"ward_id": ward["id"], "bed_number": "1", "device_key": "k1"}, headers=admin).json()
    assert bed["device_key"] == "k1"

    assert client.post("/api/alerts/device", json={}, headers={"X-Device-Key": "wrong"}).status_code == 401
    res = client.post("/api/alerts/device", json={"source": "bedside_button"}, headers={"X-Device-Key": "k1"})
    assert res.status_code == 200 and res.json()["status"] == "received"
    alert_id = res.json()["alert_id"]

    nurse = login("nurse@x.com")
    assert len(client.get("/api/alerts", headers=nurse).json()) == 1
    assert client.post(f"/api/alerts/{alert_id}/acknowledge", headers=nurse).status_code == 200
    assert client.post(f"/api/alerts/{alert_id}/resolve", json={}, headers=nurse).status_code == 200
