"""
config.py — Application Configuration for the Student Management System (SMS)

Centralised configuration using environment variables with sensible defaults.
Includes:
  - Database settings
  - CORS origins
  - ML engine parameters
  - Notification thresholds
  - Student profile defaults
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DatabaseConfig:
    """SQLite / SQLAlchemy database configuration."""
    url: str = field(
        default_factory=lambda: os.environ.get(
            "SMS_DB_URL", "sqlite:///./sms.db"
        )
    )
    echo_sql: bool = field(
        default_factory=lambda: os.environ.get("SMS_DB_ECHO", "false").lower() == "true"
    )
    pool_recycle_secs: int = field(
        default_factory=lambda: int(os.environ.get("SMS_DB_POOL_RECYCLE", "300"))
    )


@dataclass(frozen=True)
class CORSConfig:
    """Cross-Origin Resource Sharing settings."""
    allow_origins: list[str] = field(
        default_factory=lambda: os.environ.get("SMS_CORS_ORIGINS", "*").split(",")
    )
    allow_methods: list[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    )
    allow_headers: list[str] = field(
        default_factory=lambda: ["*"]
    )
    allow_credentials: bool = False


@dataclass(frozen=True)
class MLConfig:
    """Machine Learning engine parameters."""
    # TF-IDF
    tfidf_max_features: int = field(
        default_factory=lambda: int(os.environ.get("SMS_TFIDF_MAX_FEATURES", "5000"))
    )
    tfidf_ngram_min: int = 1
    tfidf_ngram_max: int = 2

    # Recommendation defaults
    default_num_recommendations: int = 3
    max_num_recommendations: int = 10

    # Schedule optimisation
    min_daily_study_hours: float = 2.0
    max_daily_study_hours: float = 8.0
    workload_high_priority_weight: float = 2.5
    workload_medium_priority_weight: float = 1.5
    workload_low_priority_weight: float = 0.75


@dataclass(frozen=True)
class NotificationConfig:
    """Thresholds for notification and alert logic."""
    burnout_high_variance_threshold: float = 4.0
    burnout_medium_variance_threshold: float = 2.5
    burnout_high_weekly_hours: float = 50.0
    burnout_medium_weekly_hours: float = 35.0

    deadline_critical_days: int = 1
    deadline_high_days: int = 3
    deadline_medium_days: int = 7
    deadline_low_days: int = 14

    low_productivity_threshold: float = 6.0
    high_productivity_threshold: float = 8.0
    long_session_threshold_mins: int = 180

    streak_alert_minimum: int = 3


@dataclass(frozen=True)
class StudentConfig:
    """Default student profile values shown in the UI."""
    default_name: str = "Chandler Bing"
    default_role: str = "Student"
    avatar_path: str = "/chandler_pfp.png"
    chandler_mode_quotes: bool = True


@dataclass(frozen=True)
class AppConfig:
    """Root application configuration aggregating all sub-configs."""
    app_title: str = "Student Management System"
    app_version: str = "2.0.0"
    app_description: str = (
        "Premium AI-powered Student Management System with ML-driven "
        "skill recommendations and adaptive schedule optimisation."
    )
    debug: bool = field(
        default_factory=lambda: os.environ.get("SMS_DEBUG", "false").lower() == "true"
    )
    host: str = field(
        default_factory=lambda: os.environ.get("SMS_HOST", "127.0.0.1")
    )
    port: int = field(
        default_factory=lambda: int(os.environ.get("SMS_PORT", "8000"))
    )

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cors: CORSConfig = field(default_factory=CORSConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    student: StudentConfig = field(default_factory=StudentConfig)


# Singleton config instance — import this everywhere
settings = AppConfig()
