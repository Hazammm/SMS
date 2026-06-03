"""
analytics.py — Academic Analytics Engine for the Student Management System (SMS)

Provides advanced statistical analysis for student performance data including:
  - GPA trend analysis and moving averages
  - Grade distribution and histogram computation
  - Study efficiency scoring and percentile ranking
  - Burnout risk detection using productivity variance
  - Weekly performance reporting
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np


# ---------------------------------------------------------------------------
# Grade → GPA point mapping (standard 4.0 scale)
# ---------------------------------------------------------------------------
GRADE_TO_GPA: dict[str, float] = {
    "A+": 4.0,
    "A":  4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B":  3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C":  2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D":  1.0,
    "F":  0.0,
    "IP": 4.0,   # In-Progress — treated optimistically
}


def letter_to_gpa(letter: str) -> float:
    """Convert a letter grade to its GPA equivalent."""
    return GRADE_TO_GPA.get(letter.strip().upper(), 0.0)


# ---------------------------------------------------------------------------
# GPA Calculations
# ---------------------------------------------------------------------------

def compute_weighted_gpa(courses: list[dict[str, Any]]) -> float:
    """
    Compute cumulative weighted GPA from a list of course dicts.

    Each course dict must contain:
      - ``credits`` (int)
      - ``gpa``     (float) OR ``grade`` (str)

    Returns the weighted GPA rounded to 2 decimal places.
    """
    total_credits = 0
    total_points = 0.0

    for course in courses:
        credits = int(course.get("credits", 0))
        gpa = float(course.get("gpa") or letter_to_gpa(course.get("grade", "F")))
        total_credits += credits
        total_points += gpa * credits

    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)


def gpa_trend(semester_gpas: list[float]) -> dict[str, Any]:
    """
    Analyse GPA over multiple semesters.

    Args:
        semester_gpas: Ordered list of GPA values per semester (oldest → newest).

    Returns a dict with:
      - ``trend``       : 'improving', 'declining', or 'stable'
      - ``slope``       : Linear regression slope
      - ``moving_avg``  : 3-point moving average series
      - ``std_dev``     : Standard deviation across semesters
    """
    if len(semester_gpas) < 2:
        return {
            "trend": "stable",
            "slope": 0.0,
            "moving_avg": semester_gpas[:],
            "std_dev": 0.0,
        }

    n = len(semester_gpas)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(semester_gpas) / n

    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, semester_gpas))
    denominator = sum((xi - x_mean) ** 2 for xi in x)
    slope = numerator / denominator if denominator != 0 else 0.0

    if slope > 0.05:
        trend = "improving"
    elif slope < -0.05:
        trend = "declining"
    else:
        trend = "stable"

    # 3-point moving average
    moving_avg: list[float] = []
    for i in range(n):
        start = max(0, i - 1)
        end = min(n, i + 2)
        window = semester_gpas[start:end]
        moving_avg.append(round(sum(window) / len(window), 3))

    std_dev = statistics.stdev(semester_gpas) if n > 1 else 0.0

    return {
        "trend": trend,
        "slope": round(slope, 4),
        "moving_avg": moving_avg,
        "std_dev": round(std_dev, 4),
    }


# ---------------------------------------------------------------------------
# Grade Distribution
# ---------------------------------------------------------------------------

def grade_distribution(courses: list[dict[str, Any]]) -> dict[str, int]:
    """
    Count how many courses fall into each letter-grade bucket.

    Returns a dict mapping grade letter → count, e.g.
    ``{"A": 3, "B+": 1, "A-": 2}``.
    """
    distribution: dict[str, int] = defaultdict(int)
    for course in courses:
        grade = str(course.get("grade", "?")).strip().upper()
        distribution[grade] += 1
    return dict(distribution)


def gpa_histogram(courses: list[dict[str, Any]], bins: int = 5) -> list[dict[str, Any]]:
    """
    Create a histogram of GPA points across courses.

    Returns a list of bin dicts:
      ``[{"range": "2.0–2.6", "count": 1}, ...]``
    """
    gpas = [float(c.get("gpa") or letter_to_gpa(c.get("grade", "F"))) for c in courses]
    if not gpas:
        return []

    lo, hi = 0.0, 4.0
    step = (hi - lo) / bins
    histogram: list[dict[str, Any]] = []

    for i in range(bins):
        bin_lo = lo + i * step
        bin_hi = bin_lo + step
        count = sum(1 for g in gpas if bin_lo <= g < bin_hi)
        histogram.append({
            "range": f"{bin_lo:.1f}–{bin_hi:.1f}",
            "count": count,
        })

    return histogram


# ---------------------------------------------------------------------------
# Study Efficiency
# ---------------------------------------------------------------------------

def study_efficiency_score(routine_logs: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Compute a study-efficiency score (0–100) for each session and overall.

    Formula:
      efficiency = (productivity / 10) * log2(duration_hours + 1) * 20

    Capped at 100 per session.

    Args:
        routine_logs: List of dicts with ``duration`` (minutes) and
                      ``productivity`` (1–10).

    Returns:
      - ``per_session``   : list of per-session efficiency scores
      - ``overall``       : aggregate weighted average
      - ``best_session``  : index of the highest-scoring session
      - ``worst_session`` : index of the lowest-scoring session
    """
    per_session: list[float] = []

    for log in routine_logs:
        duration_hrs = float(log.get("duration", 60)) / 60.0
        productivity = float(log.get("productivity", 5))
        raw = (productivity / 10.0) * math.log2(duration_hrs + 1) * 20.0
        per_session.append(min(round(raw, 2), 100.0))

    if not per_session:
        return {"per_session": [], "overall": 0.0, "best_session": -1, "worst_session": -1}

    overall = round(sum(per_session) / len(per_session), 2)
    best = int(np.argmax(per_session))
    worst = int(np.argmin(per_session))

    return {
        "per_session": per_session,
        "overall": overall,
        "best_session": best,
        "worst_session": worst,
    }


def percentile_rank(score: float, population: list[float]) -> float:
    """
    Return the percentile rank of *score* within *population*.

    e.g. ``percentile_rank(3.5, [3.0, 3.2, 3.5, 3.8, 4.0])`` → 60.0
    """
    if not population:
        return 0.0
    below = sum(1 for p in population if p < score)
    return round((below / len(population)) * 100, 1)


# ---------------------------------------------------------------------------
# Burnout Risk Detection
# ---------------------------------------------------------------------------

def burnout_risk(routine_logs: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Detect burnout risk by analysing productivity variance and total weekly hours.

    Risk levels:
      - ``"Low"``    : variance < 2.5 and hours < 35
      - ``"Medium"`` : variance < 4.0 or hours between 35–50
      - ``"High"``   : variance >= 4.0 or hours > 50

    Returns:
      - ``risk_level``    : 'Low', 'Medium', or 'High'
      - ``weekly_hours``  : Approximate total hours this week
      - ``prod_variance`` : Variance in productivity ratings
      - ``advice``        : Short actionable string
    """
    # Filter to the current ISO week
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    weekly_logs = [
        log for log in routine_logs
        if week_start.isoformat() <= str(log.get("date", "")) <= week_end.isoformat()
    ]

    weekly_minutes = sum(int(log.get("duration", 0)) for log in weekly_logs)
    weekly_hours = round(weekly_minutes / 60.0, 2)

    productivities = [float(log.get("productivity", 5)) for log in weekly_logs]
    prod_variance = round(statistics.variance(productivities), 4) if len(productivities) > 1 else 0.0

    if prod_variance >= 4.0 or weekly_hours > 50:
        risk_level = "High"
        advice = (
            "Immediate rest recommended. Schedule at least one full rest day, "
            "reduce daily study to 4h max, and prioritise sleep."
        )
    elif prod_variance >= 2.5 or weekly_hours > 35:
        risk_level = "Medium"
        advice = (
            "You are approaching your limits. Incorporate 20-min breaks every 90 mins, "
            "limit evening screen time, and ensure 7–8h sleep."
        )
    else:
        risk_level = "Low"
        advice = (
            "Great work-life balance! Keep consistent study sessions "
            "and maintain your sleep schedule to stay sharp."
        )

    return {
        "risk_level": risk_level,
        "weekly_hours": weekly_hours,
        "prod_variance": prod_variance,
        "advice": advice,
    }


# ---------------------------------------------------------------------------
# Weekly Performance Report
# ---------------------------------------------------------------------------

def weekly_report(
    courses: list[dict[str, Any]],
    routine_logs: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    student_name: str = "Chandler Bing",
) -> dict[str, Any]:
    """
    Generate a comprehensive weekly performance report for the student.

    Aggregates GPA, study efficiency, burnout risk, and task completion
    into a single human-readable summary dict.
    """
    current_gpa = compute_weighted_gpa(courses)
    grade_dist = grade_distribution(courses)
    efficiency = study_efficiency_score(routine_logs)
    burnout = burnout_risk(routine_logs)

    completed_tasks = [t for t in tasks if str(t.get("status", "")).lower() == "completed"]
    total_tasks = len(tasks)
    completion_rate = round((len(completed_tasks) / total_tasks * 100) if total_tasks else 0, 1)

    high_priority_pending = [
        t for t in tasks
        if str(t.get("priority", "")).lower() == "high"
        and str(t.get("status", "")).lower() != "completed"
    ]

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    return {
        "student": student_name,
        "generated_at": generated_at,
        "gpa": {
            "current": current_gpa,
            "grade_distribution": grade_dist,
        },
        "study": {
            "efficiency_score": efficiency["overall"],
            "weekly_hours": burnout["weekly_hours"],
        },
        "tasks": {
            "total": total_tasks,
            "completed": len(completed_tasks),
            "completion_rate_pct": completion_rate,
            "high_priority_pending": len(high_priority_pending),
        },
        "burnout": {
            "risk_level": burnout["risk_level"],
            "advice": burnout["advice"],
        },
    }
