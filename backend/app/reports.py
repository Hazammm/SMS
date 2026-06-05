"""
reports.py — PDF/HTML Report Generator for SMS

Generates structured academic reports as formatted text and HTML snippets,
suitable for printing or embedding in the frontend.

Modules:
  - ``SemesterReport``   : Full end-of-semester academic report
  - ``WeeklyDigest``     : Concise weekly performance digest email
  - ``TaskSummaryReport``: Outstanding task breakdown with urgency colour coding
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.analytics import (
    compute_weighted_gpa,
    grade_distribution,
    gpa_trend,
    study_efficiency_score,
    burnout_risk,
    weekly_report,
)
from app.notifications import deadline_alerts, daily_quote, study_streak


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hr(char: str = "─", width: int = 60) -> str:
    return char * width


def _pad_right(text: str, width: int) -> str:
    return text[:width].ljust(width)


def _table_row(*cols: tuple[str, int]) -> str:
    return "│ " + " │ ".join(_pad_right(str(v), w) for v, w in cols) + " │"


# ---------------------------------------------------------------------------
# Semester Report
# ---------------------------------------------------------------------------

class SemesterReport:
    """
    Generates a plain-text semester academic report for a student.

    Usage::

        report = SemesterReport(
            student_name="Chandler Bing",
            semester="Fall 2025",
            courses=[...],
            routine_logs=[...],
            tasks=[...],
        )
        print(report.render_text())
    """

    def __init__(
        self,
        student_name: str,
        semester: str,
        courses: list[dict[str, Any]],
        routine_logs: list[dict[str, Any]],
        tasks: list[dict[str, Any]],
    ) -> None:
        self.student_name = student_name
        self.semester = semester
        self.courses = courses
        self.routine_logs = routine_logs
        self.tasks = tasks
        self._generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── Private helpers ──────────────────────────────────────────────────

    def _course_table(self) -> list[str]:
        lines = [
            _hr(),
            "  COURSE PERFORMANCE",
            _hr(),
            _table_row(("Code", 8), ("Course Name", 35), ("Credits", 7), ("Grade", 5), ("GPA", 4)),
            "├" + "─" * 9 + "┼" + "─" * 37 + "┼" + "─" * 9 + "┼" + "─" * 7 + "┼" + "─" * 6 + "┤",
        ]
        for c in self.courses:
            lines.append(
                _table_row(
                    (c.get("code", "?"), 8),
                    (c.get("name", "Unknown"), 35),
                    (str(c.get("credits", 0)), 7),
                    (c.get("grade", "?"), 5),
                    (str(c.get("gpa", 0.0)), 4),
                )
            )
        lines.append(_hr())
        return lines

    def _summary_block(self) -> list[str]:
        gpa = compute_weighted_gpa(self.courses)
        dist = grade_distribution(self.courses)
        efficiency = study_efficiency_score(self.routine_logs)
        burnout = burnout_risk(self.routine_logs)
        streak = study_streak(self.routine_logs)

        total_credits = sum(int(c.get("credits", 0)) for c in self.courses)
        completed_tasks = sum(1 for t in self.tasks if str(t.get("status", "")).lower() == "completed")
        completion_rate = (completed_tasks / len(self.tasks) * 100) if self.tasks else 0

        grade_str = "  ".join(f"{g}:{n}" for g, n in sorted(dist.items()))

        return [
            _hr(),
            "  SEMESTER SUMMARY",
            _hr(),
            f"  Cumulative GPA        : {gpa:.2f} / 4.00",
            f"  Total Credits         : {total_credits}",
            f"  Grade Distribution    : {grade_str}",
            f"  Study Efficiency Score: {efficiency['overall']:.1f} / 100",
            f"  Weekly Study Hours    : {burnout['weekly_hours']:.1f}h",
            f"  Burnout Risk Level    : {burnout['risk_level']}",
            f"  Current Study Streak  : {streak['current_streak']} day(s)",
            f"  Task Completion Rate  : {completion_rate:.1f}%",
            _hr(),
        ]

    def _recommendations(self) -> list[str]:
        burnout = burnout_risk(self.routine_logs)
        alerts = deadline_alerts(self.tasks)
        critical = [a for a in alerts if a["urgency"] in ("OVERDUE", "CRITICAL")]

        lines = [
            _hr(),
            "  RECOMMENDATIONS",
            _hr(),
        ]
        lines.append(f"  ➤  Sleep & Burnout : {burnout['advice']}")
        if critical:
            lines.append(f"  ➤  Urgent Deadlines: {len(critical)} task(s) need immediate attention!")
            for a in critical[:3]:
                lines.append(f"      • {a['icon']} {a['title']} — {a['message']}")
        else:
            lines.append("  ➤  Deadlines       : No critical deadlines. Stay proactive!")

        lines.append(f"\n   Quote of the Day: \"{daily_quote(chandler_mode=True)}\"")
        lines.append(_hr())
        return lines

    # ── Public API ───────────────────────────────────────────────────────

    def render_text(self) -> str:
        """Render the full report as a plain-text string."""
        header = [
            _hr("═"),
            f"  STUDENT MANAGEMENT SYSTEM — SEMESTER REPORT",
            f"  Student : {self.student_name}",
            f"  Semester: {self.semester}",
            f"  Date    : {self._generated_at}",
            _hr("═"),
        ]
        sections = (
            header
            + self._course_table()
            + self._summary_block()
            + self._recommendations()
        )
        return "\n".join(sections)

    def render_html(self) -> str:
        """Render the report as a minimal HTML snippet for embedding."""
        text = self.render_text()
        return (
            "<pre style=\"font-family:monospace;background:#0a0a1a;"
            "color:#e0e0ff;padding:1.5rem;border-radius:12px;"
            "overflow-x:auto;font-size:0.85rem;\">"
            + text
            + "</pre>"
        )


# ---------------------------------------------------------------------------
# Weekly Digest
# ---------------------------------------------------------------------------

class WeeklyDigest:
    """
    Generates a concise weekly digest for the student dashboard.
    Suitable for a notification panel or email snippet.
    """

    def __init__(
        self,
        courses: list[dict[str, Any]],
        routine_logs: list[dict[str, Any]],
        tasks: list[dict[str, Any]],
        student_name: str = "Chandler Bing",
    ) -> None:
        self.report_data = weekly_report(courses, routine_logs, tasks, student_name)
        self.alerts = deadline_alerts(tasks)
        self.streak_data = study_streak(routine_logs)
        self.quote = daily_quote(chandler_mode=True)

    def render(self) -> dict[str, Any]:
        """Return a structured dict ready for JSON serialisation."""
        r = self.report_data
        return {
            "week_ending": date.today().isoformat(),
            "student": r["student"],
            "gpa": r["gpa"]["current"],
            "study_hours_this_week": r["study"]["weekly_hours"],
            "efficiency_score": r["study"]["efficiency_score"],
            "task_completion_pct": r["tasks"]["completion_rate_pct"],
            "burnout_risk": r["burnout"]["risk_level"],
            "current_streak_days": self.streak_data["current_streak"],
            "critical_alerts": [
                a for a in self.alerts if a["urgency"] in ("OVERDUE", "CRITICAL")
            ],
            "chandler_quote": self.quote,
        }


# ---------------------------------------------------------------------------
# Task Summary Report
# ---------------------------------------------------------------------------

def task_summary_report(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Generate a categorised task breakdown:
      - By status  (todo / in_progress / completed)
      - By priority (high / medium / low)
      - By category (assignment / project / exam / study)
      - Upcoming deadline list (next 7 days)
    """
    by_status: dict[str, list] = {"todo": [], "in_progress": [], "completed": []}
    by_priority: dict[str, list] = {"high": [], "medium": [], "low": []}
    by_category: dict[str, list] = {}

    today = date.today()
    upcoming: list[dict] = []

    for task in tasks:
        status = str(task.get("status", "todo")).lower()
        priority = str(task.get("priority", "low")).lower()
        category = str(task.get("category", "other")).lower()

        by_status.setdefault(status, []).append(task)
        by_priority.setdefault(priority, []).append(task)
        by_category.setdefault(category, []).append(task)

        raw_due = task.get("due_date", "")
        if raw_due and status != "completed":
            try:
                due = date.fromisoformat(str(raw_due))
                if 0 <= (due - today).days <= 7:
                    upcoming.append(task)
            except ValueError:
                pass

    upcoming.sort(key=lambda t: t.get("due_date", "9999-99-99"))

    return {
        "total": len(tasks),
        "by_status": {k: len(v) for k, v in by_status.items()},
        "by_priority": {k: len(v) for k, v in by_priority.items()},
        "by_category": {k: len(v) for k, v in by_category.items()},
        "upcoming_7_days": upcoming,
        "deadline_alerts": deadline_alerts(tasks),
    }
