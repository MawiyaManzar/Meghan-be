"""
Weekly wellbeing insights Lambda orchestration.

This module keeps the scheduling/looping logic lightweight and dependency-
injectable so we can test behavior without real AWS or database calls.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Optional, Protocol

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User, WeeklyWellbeingInsight
from app.services.wellbeing import wellbeing_analyzer

logger = logging.getLogger(__name__)


class WeeklyInsightsRepo(Protocol):
    """Persistence contract for weekly insight jobs."""

    def get_target_user_ids(self) -> list[int]:
        """Return user IDs that should be processed by this weekly run."""

    def upsert_weekly_insight(
        self,
        user_id: int,
        week_start: date,
        week_end: date,
        summary_text: str,
        risk_tier: Optional[str],
    ) -> None:
        """Persist one user's weekly insight summary."""


class WeeklySummaryService(Protocol):
    """Summary generation contract (Bedrock-backed in production)."""

    def build_weekly_summary(
        self,
        user_id: int,
        week_start: date,
        week_end: date,
    ) -> tuple[str, Optional[str]]:
        """Return summary text and optional risk tier."""


class SQLAlchemyWeeklyInsightsRepo:
    """SQLAlchemy-backed repository for weekly insight persistence."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_target_user_ids(self) -> list[int]:
        rows = self.db.query(User.id).order_by(User.id.asc()).all()
        return [row[0] for row in rows]

    def upsert_weekly_insight(
        self,
        user_id: int,
        week_start: date,
        week_end: date,
        summary_text: str,
        risk_tier: Optional[str],
    ) -> None:
        existing = (
            self.db.query(WeeklyWellbeingInsight)
            .filter(
                WeeklyWellbeingInsight.user_id == user_id,
                WeeklyWellbeingInsight.week_start == week_start,
                WeeklyWellbeingInsight.week_end == week_end,
            )
            .first()
        )
        if existing is None:
            self.db.add(
                WeeklyWellbeingInsight(
                    user_id=user_id,
                    week_start=week_start,
                    week_end=week_end,
                    summary_text=summary_text,
                    risk_tier=risk_tier,
                )
            )
        else:
            existing.summary_text = summary_text
            existing.risk_tier = risk_tier

        self.db.commit()


class WellbeingAnalyzerSummaryService:
    """Build concise weekly summary text from existing wellbeing analyzer output."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def build_weekly_summary(
        self,
        user_id: int,
        week_start: date,
        week_end: date,
    ) -> tuple[str, Optional[str]]:
        _ = week_end  # Analyzer derives week_end from week_start internally.
        insights = wellbeing_analyzer.generate_weekly_insights(
            db=self.db,
            user_id=user_id,
            week_start=week_start,
        )
        summary_text = insights.encouragement_message or (
            "Weekly wellbeing summary generated."
        )
        return summary_text, insights.most_common_tier


def _default_week_start(today: Optional[date] = None) -> date:
    today = today or date.today()
    return today - timedelta(days=today.weekday())


def run_weekly_insights_job(
    *,
    week_start: Optional[date],
    repo: WeeklyInsightsRepo,
    summary_service: WeeklySummaryService,
) -> dict:
    """
    Run one weekly insight generation pass.

    Returns counters that are easy to surface in logs/alarms and tests.
    """
    effective_week_start = week_start or _default_week_start()
    week_end = effective_week_start + timedelta(days=6)

    user_ids = repo.get_target_user_ids()
    processed_users = 0
    failed_users = 0

    logger.info(
        "weekly_insights_job_started week_start=%s week_end=%s total_users=%d",
        effective_week_start,
        week_end,
        len(user_ids),
    )

    for user_id in user_ids:
        try:
            summary_text, risk_tier = summary_service.build_weekly_summary(
                user_id=user_id,
                week_start=effective_week_start,
                week_end=week_end,
            )
            repo.upsert_weekly_insight(
                user_id=user_id,
                week_start=effective_week_start,
                week_end=week_end,
                summary_text=summary_text,
                risk_tier=risk_tier,
            )
            processed_users += 1
        except Exception as exc:
            failed_users += 1
            logger.exception(
                "weekly_insights_user_failed user_id=%s week_start=%s reason=%s",
                user_id,
                effective_week_start,
                exc,
            )

    result = {
        "week_start": effective_week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "total_users": len(user_ids),
        "processed_users": processed_users,
        "failed_users": failed_users,
    }
    logger.info("weekly_insights_job_finished result=%s", result)
    return result


def _extract_week_start(event: Optional[dict[str, Any]]) -> Optional[date]:
    """
    Parse optional week_start from common Lambda event shapes.

    Supported:
    - {"week_start": "YYYY-MM-DD"}
    - {"queryStringParameters": {"week_start": "YYYY-MM-DD"}}
    """
    if not event:
        return None

    week_start_raw = event.get("week_start")
    if not week_start_raw:
        query_params = event.get("queryStringParameters") or {}
        week_start_raw = query_params.get("week_start")

    if not week_start_raw:
        return None

    return date.fromisoformat(str(week_start_raw))


def lambda_handler(
    event: Optional[dict[str, Any]],
    context: Any,
    *,
    repo: Optional[WeeklyInsightsRepo] = None,
    summary_service: Optional[WeeklySummaryService] = None,
) -> dict[str, Any]:
    """
    AWS Lambda handler wrapper for weekly insights job.

    Returns HTTP-like payload shape with statusCode/body for easy operational
    debugging in CloudWatch and test assertions.
    """
    _ = context  # context is currently unused but kept for AWS compatibility.
    try:
        week_start = _extract_week_start(event)
    except ValueError:
        return {
            "statusCode": 400,
            "body": {
                "error": "invalid_week_start",
                "message": "week_start must be ISO date format YYYY-MM-DD.",
            },
        }

    if (repo is None) != (summary_service is None):
        logger.error("weekly_insights_lambda_missing_dependencies")
        return {
            "statusCode": 500,
            "body": {
                "error": "missing_dependencies",
                "message": "repo and summary_service must be provided.",
            },
        }

    owned_db = None
    try:
        if repo is None and summary_service is None:
            owned_db = SessionLocal()
            repo = SQLAlchemyWeeklyInsightsRepo(owned_db)
            summary_service = WellbeingAnalyzerSummaryService(owned_db)

        result = run_weekly_insights_job(
            week_start=week_start,
            repo=repo,
            summary_service=summary_service,
        )
        return {"statusCode": 200, "body": result}
    finally:
        if owned_db is not None:
            owned_db.close()

