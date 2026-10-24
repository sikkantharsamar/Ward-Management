<h1 align="center">🚨 Ward Management System with Emergency Button 🏥</h1>

<p align="center">
  <b>IDH Ward Care</b> — one smart system to manage the ward and call for help in seconds.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Proof%20of%20Concept-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Alerts-Real--Time-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Made%20for-Hospitals-2ea44f?style=for-the-badge" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

---

## 💡 About the Project

In an infectious disease ward, a patient who needs help fast may not be able to reach a nurse. On top of that, hospital records are often spread across paper and different systems.

This project fixes both problems:

- 🔴 **A physical emergency button on every bed.** One press and the nurse knows right away.
- 🖥️ **A web-based ward management system.** Patients, beds, doctors, medicines and appointments, all in one place.

Built for the **Infectious Diseases Hospital (IDH), Sri Lanka**. 🇱🇰

---

## 🔗 How the Emergency Button and Nurse Station Connect

The nurse station website is **directly integrated with the emergency button**.

1. 🛏️ A patient presses the button on their bed (or uses an easier alternative if they can't press it).
2. 📡 The button sends the alert to the system over Wi-Fi.
3. 🖥️ The nurse station website **pops up an alert with a sound alarm** instantly.
4. 📍 The alert shows the **bed, ward and patient details**, so the nurse knows exactly where to go.
5. ✅ The nurse acknowledges the alert, attends the patient, and marks it resolved.

No shouting. No waiting. No missed calls. 🔔

---

## 🌟 How It Helps Everyone

### 👩‍⚕️ Nurses
- 🚨 Get instant alerts with sound and a pop-up on the nurse station screen
- 🗺️ See a live bed map with colour-coded status
- 💊 Dispense medicines, and the stock updates automatically

### 👨‍⚕️ Doctors
- 📋 See patient records and admissions in one place
- 📅 Manage appointments easily
- 📝 Write prescriptions digitally

### 🧑‍🤝‍🧑 Patients
- 🔘 Call for help at any time with the bedside button
- ♿ Use an easier alternative if they can't press the normal button
- 🔐 Check their own information through their own login

### 🛠️ Admins
- 🏢 Manage buildings, wards, beds and users
- 📦 Track medical supplies, with low-stock warnings
- 📊 View alert reports and response times

---

## ✨ Key Features

| | Feature |
|---|---|
| 🔴 | Bedside emergency button on every bed |
| ♿ | Wearable / alternative trigger for patients who can't press the button |
| 🖥️ | Live nurse station dashboard with sound alarm |
| 🛏️ | Bed allocation, transfers and ward occupancy |
| 💊 | Prescriptions and automatic inventory tracking |
| 🔋 | Battery backup so it keeps working during power cuts |
| 💾 | Offline logging and cloud backup so no alert is ever lost |
| 🔐 | Secure login with different roles (admin, doctor, nurse, patient) |
| 📈 | Incident reports with CSV export |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| 🐍 **Server** | Python, FastAPI, Uvicorn |
| 🗄️ **Database** | SQLAlchemy, SQLite (development), PostgreSQL (local and remote) |
| ⚡ **Live Alerts** | WebSocket with polling fallback |
| 🔑 **Security** | JWT, PBKDF2 password hashing, role-based access |
| 🎨 **Frontend** | HTML, CSS, JavaScript |
| 🔌 **Hardware** | Microcontroller with Wi-Fi, SD card, battery backup, custom PCB, 3D-printed casing |
| 🧪 **Tools** | VS Code, Git, GitHub, Docker |

---

## 🚀 Getting Started

You need **Python 3.10+** and **Git**.

```bash
git clone <repository-url>
cd ward-management/backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
python -m app.seed               # creates demo data
uvicorn app.main:app --reload --host 0.0.0.0
```

🌐 Website: http://127.0.0.1:8000
📖 API docs: http://127.0.0.1:8000/docs

**Demo logins** (password: `Password@123`)
`admin@ward.local` · `doctor@ward.local` · `nurse@ward.local` · `patient@ward.local`

**Try the emergency flow** 🚨
Log in as the nurse, then in a second terminal run:

```bash
python device_simulator/simulate_button.py --key demo-key-bed-1
```

The alert shows up on the nurse station right away.

---
