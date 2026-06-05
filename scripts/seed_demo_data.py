"""
scripts/seed_demo_data.py — Demo Data Seeder for the SMS Platform

Standalone script to wipe and re-seed the SQLite database with fresh
demonstration data for Chandler Bing, suitable for demos and screenshots.

Usage:
    python scripts/seed_demo_data.py
    python scripts/seed_demo_data.py --reset   # drops all tables first
"""
from __future__ import annotations

import argparse
import sys
import os
from datetime import date, timedelta

# Configure stdout to use UTF-8 (fixes UnicodeEncodeError on Windows terminals)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Ensure the backend package is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from backend.app.db import (
    Base,
    Course,
    Task,
    RoutineLog,
    SkillGoal,
    engine,
    SessionLocal,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed the SMS database with fresh demo data."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all tables before re-seeding (destructive!).",
    )
    return parser.parse_args()


def future(days: int) -> str:
    """Return an ISO date string offset from today by *days*."""
    return (date.today() + timedelta(days=days)).isoformat()


def seed_courses(db) -> None:
    print("  Seeding courses …")
    courses = [
        Course(code="CS-401", name="Artificial Intelligence & Neural Networks", credits=3, grade="A",  gpa=4.00),
        Course(code="CS-302", name="Data Structures and Algorithms",            credits=4, grade="A-", gpa=3.70),
        Course(code="CS-305", name="Database Management Systems",               credits=3, grade="B+", gpa=3.30),
        Course(code="MAT-201", name="Linear Algebra & Applications",            credits=3, grade="A",  gpa=4.00),
        Course(code="CS-499", name="Capstone Project Phase I",                  credits=3, grade="IP", gpa=4.00),
        Course(code="CS-210", name="Operating Systems Design",                  credits=3, grade="B",  gpa=3.00),
        Course(code="CS-350", name="Computer Networks & Security",              credits=3, grade="A-", gpa=3.70),
    ]
    db.add_all(courses)
    print(f"    ✓ {len(courses)} courses added.")


def seed_tasks(db) -> None:
    print("  Seeding tasks …")
    tasks = [
        Task(
            title="Implement backpropagation neural network in NumPy",
            description="Write feedforward, cost computation and gradient updates for a 3-layer net.",
            priority="high", category="assignment",
            due_date=future(1), status="in_progress",
        ),
        Task(
            title="Design database schema for Capstone eCommerce project",
            description="Draw ER diagrams and prepare SQL DDL schemas for PostgreSQL.",
            priority="medium", category="project",
            due_date=future(3), status="todo",
        ),
        Task(
            title="Review Linear Algebra — eigenvalues & eigenvectors",
            description="Prepare notes on PCA applications.",
            priority="medium", category="study",
            due_date=future(5), status="todo",
        ),
        Task(
            title="Midterm Exam Prep — graph algorithms",
            description="Revise BFS, DFS, Dijkstra, Bellman-Ford, and MSTs.",
            priority="high", category="exam",
            due_date=future(2), status="todo",
        ),
        Task(
            title="LeetCode 3 Sum and sliding window problems",
            description="Complete at least 5 medium-difficulty arrays/string questions.",
            priority="low", category="study",
            due_date=future(-1), status="completed",
        ),
        Task(
            title="OS Lab — Shell Script Automation",
            description="Write Bash scripts to automate file backup and process monitoring.",
            priority="medium", category="assignment",
            due_date=future(7), status="todo",
        ),
        Task(
            title="Network Security — TLS Handshake report",
            description="Document the TLS 1.3 handshake process with Wireshark traces.",
            priority="low", category="assignment",
            due_date=future(10), status="todo",
        ),
    ]
    db.add_all(tasks)
    print(f"    ✓ {len(tasks)} tasks added.")


def seed_skill_goals(db) -> None:
    print("  Seeding skill goals …")
    skills = [
        SkillGoal(name="Deep Learning (PyTorch)",       progress=65, goal="AI Engineer"),
        SkillGoal(name="Relational DB Normalization",   progress=85, goal="Database Systems"),
        SkillGoal(name="Docker Containerization",       progress=30, goal="DevOps Architect"),
        SkillGoal(name="React & Modern Frontend",       progress=55, goal="Full-Stack Developer"),
        SkillGoal(name="AWS Cloud Practitioner",        progress=20, goal="Cloud Engineer"),
        SkillGoal(name="Competitive Programming",       progress=70, goal="Software Engineer"),
    ]
    db.add_all(skills)
    print(f"    ✓ {len(skills)} skill goals added.")


def seed_routine_logs(db) -> None:
    print("  Seeding routine logs …")
    logs = [
        RoutineLog(activity="Deep Work: Backpropagation Neural Net Coding", duration=120, productivity=9, date=future(0),  category="project"),
        RoutineLog(activity="Lecture: Database Systems normalisation",       duration=90,  productivity=8, date=future(0),  category="study"),
        RoutineLog(activity="Midterm Revision: Practice Exam Session",       duration=150, productivity=7, date=future(-1), category="revision"),
        RoutineLog(activity="Linear Algebra: Eigenvector problem sets",      duration=60,  productivity=9, date=future(-2), category="study"),
        RoutineLog(activity="Capstone Team Standup & Backlog Grooming",      duration=45,  productivity=6, date=future(-2), category="class"),
        RoutineLog(activity="LeetCode Practice: Arrays & Strings",           duration=75,  productivity=8, date=future(-3), category="study"),
        RoutineLog(activity="OS Lab: Bash Scripting Exercise",               duration=90,  productivity=7, date=future(-3), category="project"),
    ]
    db.add_all(logs)
    print(f"    ✓ {len(logs)} routine logs added.")


def run(reset: bool = False) -> None:
    print("=" * 55)
    print("  SMS — Demo Data Seeder")
    print(f"  Student: Chandler Bing")
    print(f"  Date   : {date.today().isoformat()}")
    print("=" * 55)

    if reset:
        print("\n  --reset flag detected. Dropping all tables …")
        Base.metadata.drop_all(bind=engine)
        print("  Tables dropped.\n")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Only seed if empty
        if reset or db.query(Course).first() is None:
            print("\nSeeding tables:")
            seed_courses(db)
            seed_tasks(db)
            seed_skill_goals(db)
            seed_routine_logs(db)
            db.commit()
            print("\n  Seeding complete!")
        else:
            print("\n  Database already contains data. Use --reset to re-seed.")
    except Exception as exc:
        db.rollback()
        print(f"\n  Error during seeding: {exc}")
        raise
    finally:
        db.close()

    print("=" * 55)


if __name__ == "__main__":
    args = parse_args()
    run(reset=args.reset)
