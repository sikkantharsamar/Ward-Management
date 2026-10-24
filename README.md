# Ward Management System with Emergency Button (IDH/NIID) - Group 09

Starter code for the website and server. Python (FastAPI) backend, plain HTML/CSS/JavaScript frontend,
SQLite database (switchable to PostgreSQL). It is a working skeleton for the team to improve, not a finished product.

## What is included

| Area | What it does |
|---|---|
| Login and roles | Admin, doctor, nurse and patient accounts. Patients can self-register; staff are created by an admin. JWT login, role-based access on every endpoint. |
| Emergency alerts | Bed device sends an alert with its device key, the server saves it and pushes it live to the nurse station (WebSocket). Acknowledge, resolve, repeat-press handling, overdue list for escalation. Patients can also call for help from the website (the alternative trigger). |
| Nurse station page | Live alert cards with sound, ward bed map with colours, admit/discharge, low stock, dispense prescriptions. Falls back to polling every 10 s if the live connection drops. |
| Ward administration | Buildings, wards, beds, patients, guardians, admissions, bed transfers, doctor appointments (with clash check). |
| Prescriptions and inventory | Doctors issue prescriptions, nurses dispense them and stock is deducted automatically. Medicine and supply stock with reorder levels, stock movement history. |
| Reports | Summary numbers, alert history with response times, CSV download, audit log of every important action. |
| Device simulator | `device_simulator/simulate_button.py` pretends to be a bed button, including the retry-until-ACK rule. |

## Folder structure

```
ward-management/
  backend/
    app/
      main.py            app start, routers, serves the website
      config.py          settings from .env
      database.py        database connection
      models.py          ALL database tables
      schemas.py         request bodies
      security.py        password hashing, JWT
      deps.py            login check and role check
      utils.py           shared helpers
      websocket_manager.py   live push to nurse stations
      seed.py            demo data
      routers/           auth, users, patients, wards, admissions, appointments,
                         prescriptions, inventory, alerts, reports
    tests/test_api.py
    requirements.txt  .env.example
  frontend/              index, nurse, doctor, patient, admin, inventory pages
    js/  css/
  device_simulator/      fake bed button
  docs/                  DEVICE_API.md (for hardware team), TEAM_TASKS.md
  docker-compose.yml     optional PostgreSQL
```

## Run it (first time)

You need Python 3.10+ and VS Code. Open the `ward-management` folder in VS Code, then open a terminal:

```bash
cd backend
python -m venv .venv
# Windows:        .venv\Scripts\activate
# Mac / Linux:    source .venv/bin/activate
pip install -r requirements.txt
# Windows: copy .env.example .env      Mac / Linux: cp .env.example .env
python -m app.seed
uvicorn app.main:app --reload --host 0.0.0.0
```

- Website: http://127.0.0.1:8000
- API documentation (try every endpoint): http://127.0.0.1:8000/docs  (log in with `POST /api/auth/login`, copy the token, press Authorize)
- Other computers on the same Wi-Fi can open `http://<your-PC-IP>:8000`

Demo accounts (password `Password@123`): `admin@ward.local`, `doctor@ward.local`, `nurse@ward.local`, `patient@ward.local`.
Demo bed device keys: `demo-key-bed-1` to `demo-key-bed-6` (bed A1 has the demo patient).

### Try the emergency flow

1. Log in as `nurse@ward.local` in one browser window (nurse station).
2. In another terminal: `python device_simulator/simulate_button.py --key demo-key-bed-1`
3. The alert appears on the nurse station instantly. Acknowledge it, then resolve it.
4. Log in as admin and open the alert report.

## Database: what you need

You do NOT need AWS to start. Use it in three stages:

1. **Now (development):** SQLite. It is one file (`ward.db`), nothing to install. This is already the default.
2. **Local database for the ward PC:** PostgreSQL on the local PC (`docker compose up -d`, then set `DATABASE_URL` in `.env`). Sir asked for local logging on a local PC, so this is that part.
3. **Remote database (for multi-user remote login and backup):** a hosted PostgreSQL. AWS RDS is one option; there are also free-tier hosted options (for example Supabase, Neon, Render). Free-tier limits change, so check them before choosing. Ask sir whether the university provides any cloud account.

The code already uses SQLAlchemy, so changing from SQLite to PostgreSQL is just changing `DATABASE_URL`. The local-to-remote sync (a scheduled job that copies new records to the cloud, and works offline) is not built yet; see `docs/TEAM_TASKS.md`.

## Working together on GitHub

1. Leader creates the repo (private) and pushes this folder: `git init`, `git add .`, `git commit -m "Initial starter code"`, `git branch -M main`, `git remote add origin <repo-url>`, `git push -u origin main`.
2. Add the five teammates as collaborators.
3. Nobody commits directly to `main`. Each person works on a branch: `git checkout -b feature/ayodya-nurse-dashboard`.
4. Commit small and often, push the branch, open a Pull Request, the leader reviews and merges.
5. Pull before you start work each day: `git pull origin main`.
6. Never commit `.env` or `ward.db` (already in `.gitignore`).

Who works on which files is in `docs/TEAM_TASKS.md`.

## Important notes

- Change `SECRET_KEY` in `.env` before any real use. Use HTTPS when it leaves the lab.
- CORS is wide open for development; restrict it before deployment.
- This is a student proof of concept. Real patient data needs proper security and privacy review.
- The code was written without being run in the environment it was generated in (no internet to install packages). The syntax was checked, but expect to fix small bugs on first run. Fix them on a branch and tell the team.
