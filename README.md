<div align="center">

<img src="https://img.shields.io/badge/AuraSMS-Student%20Management%20System-6C63FF?style=for-the-badge&logo=graduation-cap&logoColor=white" alt="AuraSMS Banner"/>

# 🎓 AuraSMS — Premium Student Management System

**A full-stack, AI-powered academic companion built with FastAPI & Vanilla JS**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML%20Engine-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Chart.js](https://img.shields.io/badge/Chart.js-Analytics-FF6384?style=flat-square&logo=chart.js&logoColor=white)](https://www.chartjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](./LICENSE)

> *Track courses. Manage tasks. Log routines. Let AI optimize your schedule and recommend the skills that matter most for your career.*

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [ML Architecture](#-ml-architecture)
- [Database Schema](#-database-schema)
- [License](#-license)

---

## 🌟 Overview

**AuraSMS** (Aura Student Management System) is a sleek, full-stack web application that helps students take control of their academic life. Beyond the standard features of a planner, it integrates a **Machine Learning engine** that learns from your study habits to generate a personalized daily schedule and recommends the most relevant skill paths aligned to your career goals.

The system runs as a single unified server — the FastAPI backend serves both the REST API and the Single-Page Application (SPA) frontend, making deployment effortless with a single command.

---

## ✨ Features

### 📊 Overview Dashboard
- Real-time academic metrics: **GPA, task completion rate, and active skills** at a glance
- **GPA Progression Chart** visualizing grade trends over time
- **Daily Productivity & Study Patterns** bar chart powered by Chart.js
- Quick-access widgets for upcoming tasks and today's schedule

### 📚 Course Manager
- Full **CRUD management** for enrolled courses
- Track course **code, name, credits, grade, and GPA contribution**
- Duplicate course-code detection with graceful error handling

### ✅ Kanban Task Board
- Three-column board: **To Do → In Progress → Completed**
- Categorize tasks as *assignment*, *project*, *exam*, or *study*
- Set **priority levels** (low / medium / high) and due dates
- Real-time status drag-and-update flow

### 📅 Smart Routine Planner
- Log study sessions with **activity, duration, productivity score (1–10), and category**
- **AI-Generated Daily Schedule** button triggers the ML optimizer on demand
- The schedule adapts automatically to your sleep debt, workload, and peak focus periods

### 🤖 Skill AI Recommender
- Enter your career objective (e.g., *"become an AI Engineer"*)
- The **TF-IDF + Cosine Similarity engine** matches your goal against a curated corpus of 10 high-value tech learning tracks
- Returns ranked recommendations with a **similarity score**, category, and required skills

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | FastAPI | REST API with async support & auto-generated Swagger docs |
| **ORM** | SQLAlchemy | Database abstraction layer |
| **Database** | SQLite | Lightweight, zero-config local persistence |
| **ML Engine** | scikit-learn, NumPy | TF-IDF vectorization, cosine similarity, schedule optimization heuristic |
| **Data Validation** | Pydantic v2 | Request/response schema enforcement |
| **Frontend** | Vanilla HTML/CSS/JS | Zero-dependency SPA with dark-mode glassmorphism UI |
| **Charts** | Chart.js | GPA progression & productivity visualizations |
| **Icons** | Font Awesome 6 | Consistent, premium iconography |
| **Fonts** | Google Fonts (Outfit, Space Grotesk) | Clean, modern typography |

---

## 📁 Project Structure

```
SMS/
├── backend/
│   ├── app/
│   │   ├── __init__.py        # App package entry point
│   │   ├── main.py            # FastAPI app, routes, and Pydantic schemas
│   │   ├── db.py              # SQLAlchemy models, DB init, and seed data
│   │   └── ml.py              # TF-IDF recommender & schedule optimizer
│   ├── requirements.txt       # Python dependencies
│   └── sms.db                 # SQLite database (auto-created on first run)
│
├── frontend/
│   ├── index.html             # SPA shell with all tab sections
│   ├── css/
│   │   └── style.css          # Glassmorphism dark theme + responsive layout
│   └── js/
│       └── app.js             # All frontend logic — API calls, charts, UI state
│
├── run.py                     # One-command launcher (manages venv + uvicorn)
├── hello.py                   # Quick connectivity test script
└── LICENSE
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+**
- `pip` package manager
- A terminal (PowerShell, bash, zsh)

### 1. Clone the Repository

```bash
git clone https://github.com/Hazammm/SMS.git
cd SMS
```

### 2. Create and Activate a Virtual Environment

```bash
# Navigate into the backend directory
cd backend

# Create the virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Go back to the project root and use the launcher:

```bash
cd ..
python run.py
```

Or run uvicorn directly from the backend directory:

```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. Open the App

| URL | Description |
|---|---|
| `http://127.0.0.1:8000` | 🎓 AuraSMS Web Application |

> **Note:** On first startup, the database is automatically created and seeded with sample courses, tasks, skill goals, and routine logs so you can explore all features immediately.

---

## 🧠 ML Architecture

AuraSMS features two purpose-built ML components, both implemented without heavy model infrastructure — fast, explainable, and lightweight.

### 1. Content-Based Skill Recommender

**Module:** `backend/app/ml.py → recommend_skills()`

```
Student Career Objective (text)
         │
         ▼
  TF-IDF Vectorizer
  (fits on 10-item corpus of tech learning tracks)
         │
         ▼
  Cosine Similarity
  (objective vector vs. all corpus vectors)
         │
         ▼
  Top-N matches ranked by similarity score
```

**How it works:**
1. A corpus of 10 curated tech learning tracks (ML, Web Dev, Cloud, Cybersecurity, etc.) is vectorized using `TfidfVectorizer` from scikit-learn.
2. The student's free-text career objective is transformed into the same TF-IDF vector space.
3. **Cosine similarity** is computed between the objective vector and all corpus vectors.
4. The top-N closest matches are returned with their similarity scores, making recommendations fully transparent and explainable.

---

### 2. Routine Schedule Optimizer

**Module:** `backend/app/ml.py → optimize_schedule()`

```
Routine Logs (past sessions)  +  Active Tasks
           │                          │
           ▼                          ▼
  Sleep Debt Analysis         Workload Score Calculation
  (avg study hours →          (per-task priority weighting:
   estimated sleep hours →     high=2.5, med=1.5, low=0.75)
   optimal vs. actual)
           │                          │
           └──────────┬───────────────┘
                      ▼
           Sleep Status Classification
           ┌──────────────────────────────────────┐
           │  Healthy Sleep   → Deep Work (90min) │
           │  Mild Sleep Debt → Pomodoro (50/10)  │
           │  Sleep Deprived  → Light Mode (40/20)│
           └──────────────────────────────────────┘
                      │
                      ▼
           Hour-by-Hour Schedule Generation
           (adjusted study blocks, nap slots,
            and peak-focus period alignment)
```

**Key behaviors:**
- Recommended study hours are **capped between 2 and 8 hours** to prevent burnout
- Sleep-deprived students receive a mandatory **power nap slot** and reduced study load
- High-priority tasks inflate the workload score, dynamically extending study blocks
- Peak focus periods are derived from each student's own historical productivity data

---

## 📄 License

This project is licensed under the **MIT License** 

---

<div align="center">

Built with 💜 by **Hazam Liaqat**

*AuraSMS — Because every student deserves a smarter semester.*

</div>
