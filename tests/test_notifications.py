"""
tests/test_notifications.py — Unit tests for the SMS notifications engine

Tests cover:
  - Deadline alert urgency tiers (OVERDUE, CRITICAL, HIGH, MEDIUM, LOW, FUTURE)
  - Deadline alert sorting
  - Productivity nudge generation
  - Study streak calculation
  - Daily quote rotation
"""
from __future__ import annotations

import unittest
from datetime import date, timedelta

from app.notifications import (
    deadline_alerts,
    productivity_nudges,
    study_streak,
    daily_quote,
    CHANDLER_QUOTES,
    MOTIVATIONAL_QUOTES,
)

# ─── Fixtures ────────────────────────────────────────────────────────────────

TODAY = date.today()


def _task(title: str, due_offset: int, status: str = "todo", priority: str = "medium") -> dict:
    return {
        "id": hash(title) % 1000,
        "title": title,
        "due_date": (TODAY + timedelta(days=due_offset)).isoformat(),
        "status": status,
        "priority": priority,
        "category": "assignment",
    }


def _log(duration: int, productivity: int, day_offset: int = 0) -> dict:
    return {
        "activity": "Study session",
        "duration": duration,
        "productivity": productivity,
        "date": (TODAY - timedelta(days=day_offset)).isoformat(),
        "category": "study",
    }


# ─── Deadline Alert Tests ─────────────────────────────────────────────────────

class TestDeadlineAlerts(unittest.TestCase):

    def test_overdue_task(self):
        tasks = [_task("Overdue essay", due_offset=-3)]
        alerts = deadline_alerts(tasks)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["urgency"], "OVERDUE")
        self.assertLess(alerts[0]["days_left"], 0)

    def test_critical_task(self):
        tasks = [_task("Neural Net assignment", due_offset=1)]
        alerts = deadline_alerts(tasks)
        self.assertEqual(alerts[0]["urgency"], "CRITICAL")

    def test_high_urgency(self):
        tasks = [_task("Database project", due_offset=3)]
        alerts = deadline_alerts(tasks)
        self.assertEqual(alerts[0]["urgency"], "HIGH")

    def test_medium_urgency(self):
        tasks = [_task("Study chapter 5", due_offset=6)]
        alerts = deadline_alerts(tasks)
        self.assertEqual(alerts[0]["urgency"], "MEDIUM")

    def test_low_urgency(self):
        tasks = [_task("Prepare slides", due_offset=12)]
        alerts = deadline_alerts(tasks)
        self.assertEqual(alerts[0]["urgency"], "LOW")

    def test_future_task(self):
        tasks = [_task("End of semester project", due_offset=30)]
        alerts = deadline_alerts(tasks)
        self.assertEqual(alerts[0]["urgency"], "FUTURE")

    def test_completed_tasks_excluded(self):
        tasks = [_task("Done task", due_offset=-1, status="completed")]
        alerts = deadline_alerts(tasks)
        self.assertEqual(len(alerts), 0)

    def test_sorting_overdue_first(self):
        tasks = [
            _task("Future task", due_offset=20),
            _task("Critical task", due_offset=1),
            _task("Overdue task", due_offset=-2),
        ]
        alerts = deadline_alerts(tasks)
        self.assertEqual(alerts[0]["urgency"], "OVERDUE")
        self.assertEqual(alerts[1]["urgency"], "CRITICAL")

    def test_alert_has_required_fields(self):
        tasks = [_task("Test task", due_offset=2)]
        alert = deadline_alerts(tasks)[0]
        for field in ("title", "due_date", "days_left", "urgency", "color", "icon", "message"):
            self.assertIn(field, alert)

    def test_missing_due_date_skipped(self):
        tasks = [{"id": 1, "title": "No date", "status": "todo"}]
        alerts = deadline_alerts(tasks)
        self.assertEqual(len(alerts), 0)


# ─── Productivity Nudge Tests ─────────────────────────────────────────────────

class TestProductivityNudges(unittest.TestCase):

    def test_empty_logs_returns_nudge(self):
        nudges = productivity_nudges([])
        self.assertTrue(len(nudges) > 0)
        self.assertTrue(any("No study" in n or "haven't" in n for n in nudges))

    def test_no_log_today(self):
        logs = [_log(60, 8, day_offset=1)]  # logged yesterday only
        nudges = productivity_nudges(logs)
        self.assertTrue(any("today" in n.lower() for n in nudges))

    def test_low_productivity_streak_detected(self):
        logs = [
            _log(60, 4, day_offset=0),
            _log(60, 4, day_offset=1),
            _log(60, 4, day_offset=2),
        ]
        nudges = productivity_nudges(logs)
        self.assertTrue(any("burnout" in n.lower() or "productivity" in n.lower() for n in nudges))

    def test_high_productivity_streak(self):
        logs = [
            _log(90, 9, day_offset=0),
            _log(90, 9, day_offset=1),
            _log(90, 9, day_offset=2),
        ]
        nudges = productivity_nudges(logs)
        self.assertTrue(any("streak" in n.lower() or "" in n for n in nudges))

    def test_long_session_nudge(self):
        logs = [_log(200, 8, day_offset=0)]
        nudges = productivity_nudges(logs)
        self.assertTrue(any("180" in n or "90" in n or "minute" in n.lower() for n in nudges))


# ─── Study Streak Tests ───────────────────────────────────────────────────────

class TestStudyStreak(unittest.TestCase):

    def test_no_logs_returns_zero(self):
        result = study_streak([])
        self.assertEqual(result["current_streak"], 0)
        self.assertEqual(result["longest_streak"], 0)
        self.assertIsNone(result["streak_start"])

    def test_current_streak_consecutive(self):
        logs = [
            _log(60, 8, day_offset=0),
            _log(60, 8, day_offset=1),
            _log(60, 8, day_offset=2),
        ]
        result = study_streak(logs)
        self.assertEqual(result["current_streak"], 3)

    def test_streak_breaks_on_missing_day(self):
        logs = [
            _log(60, 8, day_offset=0),
            # day 1 missing
            _log(60, 8, day_offset=2),
        ]
        result = study_streak(logs)
        self.assertEqual(result["current_streak"], 1)  # Only today counts

    def test_longest_streak(self):
        logs = [
            # Old streak of 4
            _log(60, 8, day_offset=10),
            _log(60, 8, day_offset=11),
            _log(60, 8, day_offset=12),
            _log(60, 8, day_offset=13),
            # Gap
            # Current streak of 2
            _log(60, 8, day_offset=0),
            _log(60, 8, day_offset=1),
        ]
        result = study_streak(logs)
        self.assertEqual(result["longest_streak"], 4)
        self.assertEqual(result["current_streak"], 2)

    def test_total_days_count(self):
        logs = [
            _log(60, 8, day_offset=0),
            _log(60, 8, day_offset=0),  # Same day — should count as 1
            _log(60, 8, day_offset=3),
        ]
        result = study_streak(logs)
        self.assertEqual(result["total_days"], 2)


# ─── Daily Quote Tests ────────────────────────────────────────────────────────

class TestDailyQuote(unittest.TestCase):

    def test_chandler_quote_is_string(self):
        quote = daily_quote(chandler_mode=True)
        self.assertIsInstance(quote, str)
        self.assertTrue(len(quote) > 5)

    def test_motivational_quote_is_string(self):
        quote = daily_quote(chandler_mode=False)
        self.assertIsInstance(quote, str)
        self.assertTrue(len(quote) > 5)

    def test_chandler_quote_in_pool(self):
        quote = daily_quote(chandler_mode=True)
        self.assertIn(quote, CHANDLER_QUOTES)

    def test_motivational_quote_in_pool(self):
        quote = daily_quote(chandler_mode=False)
        self.assertIn(quote, MOTIVATIONAL_QUOTES)

    def test_consistent_within_day(self):
        # Same day should always return same quote
        q1 = daily_quote(chandler_mode=True)
        q2 = daily_quote(chandler_mode=True)
        self.assertEqual(q1, q2)


if __name__ == "__main__":
    unittest.main()
