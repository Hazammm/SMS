"""
notifications.py — Smart Notification & Alert Engine for SMS

Generates intelligent, context-aware alerts for:
  - Upcoming assignment/exam deadlines (urgency tiers)
  - Low productivity nudges based on session logs
  - Study streak detection and celebration messages
  - Daily motivational quote rotation (Chandler Bing themed)
"""
from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta
from typing import Any


# ---------------------------------------------------------------------------
# Deadline Alert Tiers
# ---------------------------------------------------------------------------
URGENCY_TIERS: list[dict[str, Any]] = [
    {"label": "CRITICAL",  "days": 1,  "color": "#ff4d6d", "icon": "🚨"},
    {"label": "HIGH",      "days": 3,  "color": "#ff9f43", "icon": "⚠️"},
    {"label": "MEDIUM",    "days": 7,  "color": "#ffd166", "icon": "📅"},
    {"label": "LOW",       "days": 14, "color": "#06d6a0", "icon": "🗓️"},
]

CHANDLER_QUOTES: list[str] = [
    "Could this assignment BE any more overdue?",
    "I'm not great at the advice. Can I interest you in a sarcastic comment?",
    "Hi, I'm Chandler. I make jokes when I'm uncomfortable. Like right now — because exams.",
    "Oh. My. God. You actually submitted on time!",
    "I tend to make fun of myself to avoid actual work. Anyway, back to studying.",
    "It's like all my life everyone has always told me 'You're a great student, Chandler.' And I believed them.",
    "Welcome to the real world. It sucks. You're gonna love it. Now open your textbook.",
    "The definition of insanity is doing the same problem set over and over and expecting different results.",
    "Could I BE wearing any more notebooks?",
    "I'm hopeless and awkward and desperate for knowledge!",
]

MOTIVATIONAL_QUOTES: list[str] = [
    "Success is not final; failure is not fatal — it is the courage to continue that counts.",
    "The expert in anything was once a beginner.",
    "Don't watch the clock; do what it does. Keep going.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Dream bigger. Do bigger.",
    "Study hard, for the well is deep and our brains are shallow.",
    "You don't have to be great to start, but you have to start to be great.",
]


def _daily_index(pool_size: int) -> int:
    """Return a deterministic daily index into a list, rotating each day."""
    day_str = date.today().isoformat()
    digest = int(hashlib.md5(day_str.encode()).hexdigest(), 16)  # noqa: S324
    return digest % pool_size


def daily_quote(chandler_mode: bool = True) -> str:
    """Return today's motivational (or Chandler) quote."""
    pool = CHANDLER_QUOTES if chandler_mode else MOTIVATIONAL_QUOTES
    return pool[_daily_index(len(pool))]


# ---------------------------------------------------------------------------
# Deadline Alerts
# ---------------------------------------------------------------------------

def deadline_alerts(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Generate deadline alerts for non-completed tasks.

    Args:
        tasks: List of task dicts with at minimum ``title``, ``due_date``
               (ISO-format string), and ``status``.

    Returns:
        Sorted list of alert dicts ordered by urgency (most urgent first).
        Each alert contains:
          - ``task_id``    : Task ID (if present)
          - ``title``      : Task title
          - ``due_date``   : ISO date string
          - ``days_left``  : Integer days until due (negative = overdue)
          - ``urgency``    : 'OVERDUE', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'FUTURE'
          - ``color``      : Hex colour for UI
          - ``icon``       : Emoji icon
          - ``message``    : Human-readable alert message
    """
    today = date.today()
    alerts: list[dict[str, Any]] = []

    for task in tasks:
        status = str(task.get("status", "todo")).lower()
        if status == "completed":
            continue

        raw_due = task.get("due_date", "")
        if not raw_due:
            continue

        try:
            due = date.fromisoformat(str(raw_due))
        except ValueError:
            continue

        days_left = (due - today).days
        title = task.get("title", "Unnamed Task")
        task_id = task.get("id")

        if days_left < 0:
            urgency = "OVERDUE"
            color = "#c0392b"
            icon = "🔥"
            message = (
                f'"{title}" was due {abs(days_left)} day(s) ago! '
                "Submit immediately or contact your instructor."
            )
        else:
            tier_matched = False
            for tier in URGENCY_TIERS:
                if days_left <= tier["days"]:
                    urgency = tier["label"]
                    color = tier["color"]
                    icon = tier["icon"]
                    message = (
                        f'"{title}" is due in {days_left} day(s) '
                        f'({due.strftime("%b %d")}). Priority: {urgency}.'
                    )
                    tier_matched = True
                    break
            if not tier_matched:
                urgency = "FUTURE"
                color = "#a8d8ea"
                icon = "📌"
                message = f'"{title}" is due on {due.strftime("%b %d, %Y")} — plan ahead.'

        alerts.append({
            "task_id": task_id,
            "title": title,
            "due_date": raw_due,
            "days_left": days_left,
            "urgency": urgency,
            "color": color,
            "icon": icon,
            "message": message,
        })

    # Sort: overdue first, then closest deadline
    urgency_order = {"OVERDUE": -1, "CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "FUTURE": 4}
    alerts.sort(key=lambda a: (urgency_order.get(a["urgency"], 5), a["days_left"]))
    return alerts


# ---------------------------------------------------------------------------
# Productivity Nudges
# ---------------------------------------------------------------------------

def productivity_nudges(routine_logs: list[dict[str, Any]]) -> list[str]:
    """
    Analyse recent session logs and return context-aware nudge messages.

    Checks for:
      - Consecutive low-productivity days (< 6/10) → fatigue warning
      - Very long sessions (> 3h) without a break log → fragmentation advice
      - No logs today → gentle reminder to log a session
      - High-streak productivity days → celebration message
    """
    nudges: list[str] = []
    today = date.today()

    if not routine_logs:
        nudges.append(
            "👋 No study sessions logged yet today. "
            "Start a 25-minute Pomodoro to build momentum!"
        )
        return nudges

    # Group logs by date (last 7 days only)
    daily: dict[str, list[dict]] = {}
    for log in routine_logs:
        log_date = str(log.get("date", ""))
        if not log_date:
            continue
        try:
            d = date.fromisoformat(log_date)
        except ValueError:
            continue
        if (today - d).days > 7:
            continue
        daily.setdefault(log_date, []).append(log)

    # Check if logged today
    today_str = today.isoformat()
    if today_str not in daily:
        nudges.append(
            "📝 You haven't logged a session today. "
            "Even a 30-minute review counts — get started!"
        )

    # Detect low-productivity streak (3+ consecutive days avg < 6)
    sorted_dates = sorted(daily.keys())
    low_streak: list[str] = []
    for d_str in sorted_dates:
        prods = [float(l.get("productivity", 5)) for l in daily[d_str]]
        avg_prod = sum(prods) / len(prods) if prods else 5.0
        if avg_prod < 6.0:
            low_streak.append(d_str)
        else:
            low_streak = []

    if len(low_streak) >= 3:
        nudges.append(
            "😴 Your productivity has been below 6/10 for 3+ days. "
            "This is a sign of burnout. Take a full rest day and sleep 8+ hours tonight."
        )

    # High-productivity streak (3+ days avg >= 8)
    high_streak: list[str] = []
    for d_str in sorted_dates:
        prods = [float(l.get("productivity", 5)) for l in daily[d_str]]
        avg_prod = sum(prods) / len(prods) if prods else 5.0
        if avg_prod >= 8.0:
            high_streak.append(d_str)
        else:
            high_streak = []

    if len(high_streak) >= 3:
        nudges.append(
            f"🔥 {len(high_streak)}-day high-productivity streak! "
            "You're in the zone — keep it up, Chandler!"
        )

    # Very long individual sessions (> 180 min) without breaks
    for log in routine_logs:
        if int(log.get("duration", 0)) > 180:
            nudges.append(
                f"⏱️ Session \"{log.get('activity', 'Study')}\" ran for "
                f"{log.get('duration')} minutes. "
                "Sessions over 90 mins reduce retention — try shorter, focused blocks!"
            )
            break  # One warning is enough

    if not nudges:
        nudges.append(
            "✅ Everything looks balanced. "
            "Keep logging your sessions to get smarter insights!"
        )

    return nudges


# ---------------------------------------------------------------------------
# Study Streak Tracker
# ---------------------------------------------------------------------------

def study_streak(routine_logs: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Compute the current and longest consecutive study-day streaks.

    A day counts as a 'study day' if at least one routine log exists for it.

    Returns:
      - ``current_streak`` : Number of consecutive days up to today with logs
      - ``longest_streak`` : All-time longest consecutive study streak
      - ``streak_start``   : ISO date when current streak began
      - ``total_days``     : Total distinct days with at least one log
    """
    logged_dates: set[date] = set()
    for log in routine_logs:
        raw = str(log.get("date", ""))
        try:
            logged_dates.add(date.fromisoformat(raw))
        except ValueError:
            continue

    if not logged_dates:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "streak_start": None,
            "total_days": 0,
        }

    sorted_days = sorted(logged_dates)
    today = date.today()

    # Compute current streak (working backwards from today)
    current_streak = 0
    check_day = today
    while check_day in logged_dates:
        current_streak += 1
        check_day -= timedelta(days=1)

    streak_start = (today - timedelta(days=current_streak - 1)).isoformat() if current_streak > 0 else None

    # Compute longest streak
    longest_streak = 1
    run = 1
    for i in range(1, len(sorted_days)):
        if (sorted_days[i] - sorted_days[i - 1]).days == 1:
            run += 1
            longest_streak = max(longest_streak, run)
        else:
            run = 1

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "streak_start": streak_start,
        "total_days": len(logged_dates),
    }
