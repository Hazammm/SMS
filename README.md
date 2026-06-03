# 🎓 Student Management System (SMS)
### AI-Powered Academic Platform · Built with Python & FastAPI

> *"Could this SMS platform BE any more feature-complete?"*  — Chandler Bing (2026)

---

## 🚀 Overview

A **premium, AI-powered Student Management System** designed for Chandler Bing, featuring:

- 📊 **GPA Analytics** — Weighted GPA, grade distribution, trend analysis
- 🤖 **ML Skill Recommender** — TF-IDF + Cosine Similarity course recommendations
- 📅 **Adaptive Schedule Optimizer** — Burnout-aware daily routine generation
- 🔔 **Smart Notifications** — Deadline alerts, productivity nudges, study streaks
- 📈 **Weekly Reports** — Comprehensive academic performance summaries
- 🎨 **Glassmorphism UI** — Premium dark-mode dashboard with Chart.js visualisations

---

## 🛠️ Tech Stack

| Layer       | Technology                              |
|-------------|----------------------------------------|
| Backend     | Python 3.10+, FastAPI, SQLAlchemy      |
| ML Engine   | scikit-learn (TF-IDF, Cosine Similarity), NumPy |
| Database    | SQLite (via SQLAlchemy ORM)            |
| Frontend    | Vanilla HTML5, CSS3 (Glassmorphism), JS, Chart.js |
| Testing     | Python `unittest`                      |

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
