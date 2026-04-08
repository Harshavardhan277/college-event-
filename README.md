# 🎓 CEAM — College Event & Activity Management System

> A full-stack web application for managing college events, club activities, student registrations, payments, attendance, and certificate distribution.

Built with **Flask** · **SQLAlchemy** · **PostgreSQL** · **Tailwind CSS**

---

## 📌 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Event Workflow](#event-workflow)
- [Portals & Features](#portals--features)
- [Demo Login Credentials](#demo-login-credentials)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)

---

## Overview

CEAM is a role-based event management platform designed for Kalasalingam Academy of Research and Education. It supports four distinct user roles — **Student**, **Club Head (Coordinator)**, **HOD/Dean**, and **Admin** — each with their own dedicated portal and feature set.

---

## Tech Stack

| Layer        | Technology                           |
|--------------|--------------------------------------|
| Backend      | Python 3.x, Flask                    |
| Database     | PostgreSQL (via SQLAlchemy ORM)      |
| Auth         | Flask-Login, Flask-Bcrypt            |
| Email        | Flask-Mail (Gmail SMTP)              |
| Frontend     | Jinja2, Tailwind CSS, Font Awesome   |
| QR Codes     | `qrd` / Pillow (PIL)                 |
| File Uploads | Werkzeug                             |

---

## Project Structure

```
SE Project/
├── app.py                  # Flask app factory & blueprint registration
├── extensions.py           # Shared extensions (db, bcrypt, login_manager, mail)
├── models.py               # All SQLAlchemy models
├── auth_routes.py          # Shared auth: forgot/reset password (OTP)
├── email_utils.py          # Email OTP sending utility
├── utils.py                # QR code generation
├── seed_db.py              # Database seeder (creates default users)
├── .env                    # Environment variables
│
├── stu/                    # Student Portal
│   ├── routes.py
│   └── templates/
│
├── clu/                    # Club Head / Coordinator Portal
│   ├── routes.py
│   └── templates/
│
├── ho/                     # HOD / Dean Portal
│   ├── routes.py
│   └── templates/
│
├── adm/                    # Admin Portal
│   ├── routes.py
│   └── templates/
│
├── hod/                    # (Legacy HOD module - retained for compatibility)
│
├── static/                 # CSS, JS, images, uploads
└── templates/              # Shared templates (index.html, navbar)
```

---

## Event Workflow

```
[Club Head] Creates Event
        ↓
  Status: Pending Approval
        ↓
[HOD / Dean] Reviews Event
        ↓
  Approves ────────────── Rejects
        ↓
[Student] Sees Event on Dashboard
        ↓
[Student] Registers for Event
        ↓
[Student] Completes Payment (submits Transaction ID)
        ↓
[Club Head] Scans Student QR for Attendance
        ↓
[Club Head] Uploads Certificates
        ↓
[Student] Downloads Certificate
```

---

## Portals & Features

### 🎓 Student Portal (`/stu`)
- Register & Login with Register Number
- Browse approved events
- Register for events & pay via simulated gateway
- View registration history, payment status
- Download earned certificates
- View attendance records

### 👥 Club Head Portal (`/clu`)
- Login & manage club profile
- Create events with poster upload
- Post recruitment & helper requirement notices
- View registered participants
- Scan QR codes for attendance marking
- Upload participation certificates

### 🛡 HOD / Dean Portal (`/ho`)
- Review pending event proposals
- Approve or Reject events with remarks
- View all events (Pending / Approved / Rejected)

### ⚙️ Admin Portal (`/adm`)
- System-wide user management (Students, HODs, Deans, Club Heads)
- Create / Edit / Delete Clubs
- Create Coordinator and HOD/Dean accounts
- View and manage system users
- Change passwords and deactivate accounts

---

## Demo Login Credentials

> ⚠️ After running `python seed_db.py`, the following test accounts are available:

### 🎓 Student
| Field           | Value              |
|-----------------|--------------------|
| URL             | http://127.0.0.1:5000/stu/login |
| Register Number | `student`          |
| Password        | `studentpassword`  |

### 👥 Club Head (Coordinator)
| Field    | Value                  |
|----------|------------------------|
| URL      | http://127.0.0.1:5000/clu/login |
| Username | `coordinator`          |
| Password | `coordinatorpassword`  |
| Club     | Tech Innovations       |

### 🛡 HOD / Dean
| Field    | Value            |
|----------|------------------|
| URL      | http://127.0.0.1:5000/ho/login |
| Username | `hod`            |
| Password | `password123`    |
| Name     | Dr. Pavan Kumar  |
| Dept     | CSE              |

### ⚙️ Admin
| Field    | Value            |
|----------|------------------|
| URL      | http://127.0.0.1:5000/adm/login |
| Username | `admin`          |
| Password | `adminpassword`  |

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "SE Project"
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install flask flask-sqlalchemy flask-login flask-bcrypt flask-mail psycopg2-binary python-dotenv werkzeug pillow
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Flask Secret Key
SECRET_KEY=college_secret_key_2026

# PostgreSQL Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/college_event

# Gmail SMTP Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
```

> 💡 Use a Gmail **App Password** (not your real Gmail password). Generate one at: https://myaccount.google.com/apppasswords

---

## Database Setup

### 1. Create the PostgreSQL database

```sql
-- In psql or pgAdmin
CREATE DATABASE college_event;
```

### 2. Update `app.py` with your credentials

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/college_event"
```

### 3. Seed the database (creates tables + demo users)

```bash
python seed_db.py
```

> ⚠️ **Warning**: `seed_db.py` drops and recreates all tables. Only run this on a fresh setup or when you intentionally want to reset data.

---

## Running the Application

```bash
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000/**

You'll see the main landing page where you can choose your portal.

---

## 🔔 Notification System

The system includes an automated email notification feature using **Flask-Mail** and **Gmail SMTP**.

### 1. Acceptance Notifications
When an **HOD or Dean** approves or rejects an event, an email is automatically sent to the **Coordinator** who created the event, notifying them of the status change.

### 2. Event Reminders
The system can send reminders to all students registered for an event that occurs the next day.

To send reminders, run the following script:
```bash
python remind_events.py
```
*Tip: In a production environment, this script should be scheduled as a daily **cron job**.*

---

## Notes

- All uploaded files (posters, certificates, QR codes) are stored in `static/uploads/`.
- OTP-based password recovery is supported for student accounts via Gmail SMTP.
- The Coordinator login uses its own `coordinators` table (separate from the `users` table).
- The Admin account must be created via `seed_db.py` — there is no public admin registration.

---

## License

This project was built as a Software Engineering academic project at **Kalasalingam Academy of Research and Education**.

© 2026 CEAM — All rights reserved.
