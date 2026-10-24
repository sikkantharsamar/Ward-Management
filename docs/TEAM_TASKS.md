# Team tasks (suggested split, adjust with the team)

Each person works on their own branch and opens a Pull Request.

## Samar (leader): core backend and database
- Files: `backend/app/main.py, models.py, security.py, deps.py, routers/alerts.py, routers/auth.py, routers/users.py`
- Review all Pull Requests, keep `main` working.
- Local-to-cloud sync with offline queue (new: `backend/app/sync.py`), PostgreSQL switch, Alembic migrations.
- Alert escalation (use `GET /api/alerts/overdue`): repeat alarm and notify other nurses automatically.
- Device heartbeat and offline/low-battery detection endpoint.

## Ayodya: nurse station
- Files: `frontend/nurse.html`, `frontend/js/nurse.js`
- Better bed map layout, louder and clearer alarm, nurse assignment to beds, filter by ward.
- Show device offline / low-battery state.

## Dulanga: doctor, patient, admissions, inventory
- Files: `frontend/doctor.html, patient.html, inventory.html` and their JS; `routers/admissions.py, appointments.py, prescriptions.py, inventory.py`
- Bed transfer screen (API exists, no screen yet), edit patient and guardian screens, expiry-date warnings, patient history.

## Kavisha: UI design and styling
- Files: `frontend/css/style.css`, all HTML pages (look and feel only)
- Responsive layout for tablets, accessible colours and large text, logo and assets, print layout for reports.
- 3D casing design (separate folder, e.g. `hardware/3d/`).

## Harsha and Binura: hardware
- Folder: `hardware/` (create it): schematics, PCB, firmware.
- Read `docs/DEVICE_API.md`. Firmware must follow the retry-until-ACK rules.
- SD card logging and battery backup behaviour; test with the simulator first.

## Everyone
- Charts and incident-report screens (Ayodya, Dulanga), user documentation with QR codes to video guides, technical documentation.
- Tests for latency, packet loss, power failure and many devices at once (use `tests/` and the simulator).
