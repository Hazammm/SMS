# 🎓 Student Management System (SMS)
### AI-Powered Academic Platform · Built with Python & FastAPI

> *"Could this SMS platform BE any more feature-complete?"*  — Chandler Bing

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
│   │   ├── main.py          # FastAPI app + all API endpoints
│   │   ├── db.py            # SQLAlchemy models & database seeder
│   │   ├── ml.py            # TF-IDF skill recommender & schedule optimiser
│   │   ├── analytics.py     # GPA trend, efficiency scoring, burnout detection
│   │   ├── notifications.py # Deadline alerts, nudges, study streaks
│   │   ├── reports.py       # Semester & weekly report generators
│   │   └── config.py        # Centralised app configuration
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Premium glassmorphism SPA
│   ├── css/style.css
│   └── js/app.js
├── tests/
│   ├── test_analytics.py    # Unit tests — GPA, efficiency, burnout
│   └── test_notifications.py # Unit tests — alerts, nudges, streaks
├── scripts/
│   ├── seed_demo_data.py    # Database seeder script
│   └── check_health.py      # API health check script
├── hello.py                 # CLI launcher
├── run.py                   # Server launcher
└── .gitattributes           # Forces GitHub to detect Python
```

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Launch the platform
python hello.py

# 3. Open in browser
#    http://127.0.0.1:8000
```

---

## 🔑 API Endpoints

| Method | Endpoint                        | Description                        |
|--------|---------------------------------|------------------------------------|
| GET    | `/api/health`                   | Health check                       |
| GET    | `/api/courses`                  | List all courses                   |
| POST   | `/api/courses`                  | Add a course                       |
| GET    | `/api/tasks`                    | List all tasks                     |
| POST   | `/api/tasks`                    | Create a task                      |
| GET    | `/api/analytics/gpa`            | GPA analytics & distribution       |
| GET    | `/api/analytics/burnout`        | Burnout risk assessment            |
| GET    | `/api/analytics/efficiency`     | Study efficiency scores            |
| GET    | `/api/notifications/alerts`     | Deadline alerts (urgency-sorted)   |
| GET    | `/api/notifications/nudges`     | Personalised productivity nudges   |
| GET    | `/api/notifications/quote`      | Daily Chandler Bing quote          |
| GET    | `/api/report/weekly`            | Weekly performance report          |
| GET    | `/api/streak`                   | Study streak tracker               |
| GET    | `/api/student/profile`          | Student profile (Chandler Bing)    |
| POST   | `/api/recommend-skills`         | ML skill recommendations           |
| GET    | `/api/schedule/daily`           | Optimised daily schedule           |

---

## 🧪 Running Tests

```bash
cd backend
python -m pytest ../tests/ -v
```

---

## 👤 Student Profile

**Name:** Chandler Bing  
**Role:** Computer Science Student  
**GPA:** 3.85 / 4.00  

---

*Built with ❤️ and a healthy dose of sarcasm.*
