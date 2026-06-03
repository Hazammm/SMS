"""
tests/test_analytics.py — Unit tests for the SMS analytics engine

Tests cover:
  - Weighted GPA computation
  - GPA trend detection (improving, declining, stable)
  - Grade distribution counting
  - Study efficiency scoring
  - Burnout risk detection
  - Weekly report generation
"""
from __future__ import annotations

import unittest
from datetime import date, timedelta

from app.analytics import (
    compute_weighted_gpa,
    gpa_trend,
    grade_distribution,
    gpa_histogram,
    study_efficiency_score,
    percentile_rank,
    burnout_risk,
    weekly_report,
    letter_to_gpa,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────

SAMPLE_COURSES = [
    {"code": "CS-401", "name": "AI & Neural Networks",   "credits": 3, "grade": "A",  "gpa": 4.00},
    {"code": "CS-302", "name": "Data Structures",        "credits": 4, "grade": "A-", "gpa": 3.70},
    {"code": "CS-305", "name": "Database Systems",       "credits": 3, "grade": "B+", "gpa": 3.30},
    {"code": "MAT-201", "name": "Linear Algebra",        "credits": 3, "grade": "A",  "gpa": 4.00},
]

TODAY = date.today().isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
TWO_DAYS_AGO = (date.today() - timedelta(days=2)).isoformat()

SAMPLE_LOGS = [
    {"activity": "Deep Work: AI coding",          "duration": 120, "productivity": 9, "date": TODAY,        "category": "study"},
    {"activity": "Database Systems revision",      "duration": 90,  "productivity": 7, "date": YESTERDAY,    "category": "study"},
    {"activity": "Linear Algebra problem sets",    "duration": 60,  "productivity": 8, "date": TWO_DAYS_AGO, "category": "study"},
]

SAMPLE_TASKS = [
    {"id": 1, "title": "Neural Net assignment",  "priority": "high",   "category": "assignment", "due_date": (date.today() + timedelta(days=1)).isoformat(), "status": "in_progress"},
    {"id": 2, "title": "DB Schema design",       "priority": "medium", "category": "project",    "due_date": (date.today() + timedelta(days=3)).isoformat(), "status": "todo"},
    {"id": 3, "title": "LeetCode problems",      "priority": "low",    "category": "study",      "due_date": (date.today() - timedelta(days=1)).isoformat(), "status": "completed"},
]


# ─── Test Cases ──────────────────────────────────────────────────────────────

class TestLetterToGpa(unittest.TestCase):
    def test_a_plus(self):
        self.assertEqual(letter_to_gpa("A+"), 4.0)

    def test_b_minus(self):
        self.assertAlmostEqual(letter_to_gpa("B-"), 2.7)

    def test_f(self):
        self.assertEqual(letter_to_gpa("F"), 0.0)

    def test_unknown(self):
        self.assertEqual(letter_to_gpa("Z"), 0.0)

    def test_case_insensitive(self):
        self.assertEqual(letter_to_gpa("a"), 4.0)


class TestComputeWeightedGpa(unittest.TestCase):
    def test_weighted_average(self):
        gpa = compute_weighted_gpa(SAMPLE_COURSES)
        # Manual: (4.00*3 + 3.70*4 + 3.30*3 + 4.00*3) / 13
        expected = round((12.0 + 14.8 + 9.9 + 12.0) / 13, 2)
        self.assertAlmostEqual(gpa, expected, places=2)

    def test_empty_courses(self):
        self.assertEqual(compute_weighted_gpa([]), 0.0)

    def test_single_course(self):
        courses = [{"credits": 3, "grade": "A", "gpa": 4.0}]
        self.assertEqual(compute_weighted_gpa(courses), 4.0)


class TestGpaTrend(unittest.TestCase):
    def test_improving(self):
        result = gpa_trend([2.5, 2.8, 3.1, 3.4, 3.7])
        self.assertEqual(result["trend"], "improving")
        self.assertGreater(result["slope"], 0)

    def test_declining(self):
        result = gpa_trend([3.9, 3.6, 3.2, 2.9, 2.5])
        self.assertEqual(result["trend"], "declining")
        self.assertLess(result["slope"], 0)

    def test_stable(self):
        result = gpa_trend([3.5, 3.5, 3.5, 3.5])
        self.assertEqual(result["trend"], "stable")

    def test_single_value(self):
        result = gpa_trend([3.5])
        self.assertEqual(result["trend"], "stable")

    def test_moving_average_length(self):
        gpas = [3.0, 3.2, 3.5, 3.7, 3.9]
        result = gpa_trend(gpas)
        self.assertEqual(len(result["moving_avg"]), len(gpas))


class TestGradeDistribution(unittest.TestCase):
    def test_counts(self):
        dist = grade_distribution(SAMPLE_COURSES)
        self.assertEqual(dist.get("A"), 2)
        self.assertEqual(dist.get("A-"), 1)
        self.assertEqual(dist.get("B+"), 1)

    def test_empty(self):
        self.assertEqual(grade_distribution([]), {})


class TestGpaHistogram(unittest.TestCase):
    def test_returns_bins(self):
        hist = gpa_histogram(SAMPLE_COURSES, bins=4)
        self.assertEqual(len(hist), 4)

    def test_bin_format(self):
        hist = gpa_histogram(SAMPLE_COURSES)
        for bin_item in hist:
            self.assertIn("range", bin_item)
            self.assertIn("count", bin_item)

    def test_empty_courses(self):
        self.assertEqual(gpa_histogram([]), [])


class TestStudyEfficiencyScore(unittest.TestCase):
    def test_overall_in_range(self):
        result = study_efficiency_score(SAMPLE_LOGS)
        self.assertGreaterEqual(result["overall"], 0)
        self.assertLessEqual(result["overall"], 100)

    def test_best_worst_indices(self):
        result = study_efficiency_score(SAMPLE_LOGS)
        self.assertIn(result["best_session"], range(len(SAMPLE_LOGS)))
        self.assertIn(result["worst_session"], range(len(SAMPLE_LOGS)))

    def test_empty_logs(self):
        result = study_efficiency_score([])
        self.assertEqual(result["overall"], 0.0)
        self.assertEqual(result["best_session"], -1)


class TestPercentileRank(unittest.TestCase):
    def test_median(self):
        pop = [3.0, 3.2, 3.5, 3.8, 4.0]
        rank = percentile_rank(3.5, pop)
        self.assertEqual(rank, 40.0)   # 2 values below 3.5

    def test_lowest(self):
        pop = [3.0, 3.5, 4.0]
        self.assertEqual(percentile_rank(3.0, pop), 0.0)

    def test_empty_population(self):
        self.assertEqual(percentile_rank(3.5, []), 0.0)


class TestBurnoutRisk(unittest.TestCase):
    def test_low_risk_with_few_logs(self):
        result = burnout_risk(SAMPLE_LOGS)
        self.assertIn(result["risk_level"], ("Low", "Medium", "High"))
        self.assertIsInstance(result["advice"], str)

    def test_high_risk_detection(self):
        # Logs with very high variance in productivity this week
        today = date.today()
        logs = [
            {"duration": 600, "productivity": 2, "date": today.isoformat()},
            {"duration": 600, "productivity": 9, "date": today.isoformat()},
            {"duration": 600, "productivity": 1, "date": today.isoformat()},
        ]
        result = burnout_risk(logs)
        # High duration (30h) + high variance should trigger Medium or High
        self.assertIn(result["risk_level"], ("Medium", "High"))


class TestWeeklyReport(unittest.TestCase):
    def test_structure(self):
        report = weekly_report(SAMPLE_COURSES, SAMPLE_LOGS, SAMPLE_TASKS, "Chandler Bing")
        self.assertEqual(report["student"], "Chandler Bing")
        self.assertIn("gpa", report)
        self.assertIn("study", report)
        self.assertIn("tasks", report)
        self.assertIn("burnout", report)

    def test_task_counts(self):
        report = weekly_report(SAMPLE_COURSES, SAMPLE_LOGS, SAMPLE_TASKS, "Chandler Bing")
        self.assertEqual(report["tasks"]["total"], len(SAMPLE_TASKS))
        self.assertEqual(report["tasks"]["completed"], 1)


if __name__ == "__main__":
    unittest.main()
