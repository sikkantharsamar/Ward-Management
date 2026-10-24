from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import admissions, alerts, appointments, auth, inventory, patients, prescriptions, reports, users, wards

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ward Management System (IDH/NIID)", version="0.1.0")

# Open CORS is for development only. Restrict allow_origins before real use.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

for module in (auth, users, patients, wards, admissions, appointments, prescriptions, inventory, alerts, reports):
    app.include_router(module.router, prefix="/api")


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok"}


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/app/")
