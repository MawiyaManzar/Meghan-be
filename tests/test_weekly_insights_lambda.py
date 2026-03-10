"""
TDD tests for A5: weekly wellbeing insights Lambda orchestration.

These tests are intentionally introduced before implementation so we can lock
the expected behavior of the Lambda handler.
"""

from datetime import date

from app.core.security import get_password_hash
from app.models.user import User, WeeklyWellbeingInsight


def test_lambda_handler_persists_weekly_insight(monkeypatch):
    """
    Lambda should:
    - collect target user IDs
    - generate insight summary per user
    - persist a weekly insight row
    - return counters for observability
    """
    from app.lambda_functions.weekly_insights import run_weekly_insights_job

    calls = {
        "target_users": 0,
        "summary": 0,
        "persist": 0,
    }

    class StubRepo:
        def get_target_user_ids(self):
            calls["target_users"] += 1
            return [101]

        def upsert_weekly_insight(self, user_id, week_start, week_end, summary_text, risk_tier):
            calls["persist"] += 1
            assert user_id == 101
            assert week_start == date(2026, 3, 2)
            assert week_end == date(2026, 3, 8)
            assert "stress around exams" in summary_text
            assert risk_tier == "Yellow"

    class StubSummaryService:
        def build_weekly_summary(self, user_id, week_start, week_end):
            calls["summary"] += 1
            assert user_id == 101
            return "The user had recurring stress around exams and sleep routines.", "Yellow"

    result = run_weekly_insights_job(
        week_start=date(2026, 3, 2),
        repo=StubRepo(),
        summary_service=StubSummaryService(),
    )

    assert result["processed_users"] == 1
    assert result["failed_users"] == 0
    assert calls["target_users"] == 1
    assert calls["summary"] == 1
    assert calls["persist"] == 1


def test_lambda_handler_counts_user_level_failure_and_continues():
    """
    If one user fails, lambda should continue processing the rest and expose
    failure counters in output for debugging and alarms.
    """
    from app.lambda_functions.weekly_insights import run_weekly_insights_job

    class StubRepo:
        def __init__(self):
            self.persisted = []

        def get_target_user_ids(self):
            return [101, 202]

        def upsert_weekly_insight(self, user_id, week_start, week_end, summary_text, risk_tier):
            self.persisted.append((user_id, summary_text, risk_tier))

    class FlakySummaryService:
        def build_weekly_summary(self, user_id, week_start, week_end):
            if user_id == 101:
                raise RuntimeError("bedrock timeout")
            return "Stable week with steady routines.", "Green"

    repo = StubRepo()
    result = run_weekly_insights_job(
        week_start=date(2026, 3, 2),
        repo=repo,
        summary_service=FlakySummaryService(),
    )

    assert result["processed_users"] == 1
    assert result["failed_users"] == 1
    assert result["total_users"] == 2
    assert repo.persisted == [(202, "Stable week with steady routines.", "Green")]


def test_aws_lambda_handler_parses_week_start_and_returns_200():
    """AWS-style handler should parse week_start from event and return JSON body."""
    from app.lambda_functions.weekly_insights import lambda_handler

    class StubRepo:
        def get_target_user_ids(self):
            return []

        def upsert_weekly_insight(self, user_id, week_start, week_end, summary_text, risk_tier):
            raise AssertionError("Should not persist when there are no users")

    class StubSummaryService:
        def build_weekly_summary(self, user_id, week_start, week_end):
            return "unused", "Green"

    response = lambda_handler(
        {"week_start": "2026-03-02"},
        None,
        repo=StubRepo(),
        summary_service=StubSummaryService(),
    )

    assert response["statusCode"] == 200
    assert response["body"]["week_start"] == "2026-03-02"
    assert response["body"]["week_end"] == "2026-03-08"
    assert response["body"]["total_users"] == 0


def test_aws_lambda_handler_invalid_week_start_returns_400():
    """Invalid week_start should return HTTP-like 400 response for observability."""
    from app.lambda_functions.weekly_insights import lambda_handler

    response = lambda_handler({"week_start": "not-a-date"}, None, repo=object(), summary_service=object())

    assert response["statusCode"] == 400
    assert response["body"]["error"] == "invalid_week_start"


def test_sqlalchemy_repo_upsert_persists_and_updates(db_session):
    """A5.4: real SQLAlchemy repo should insert then update the same weekly row."""
    from app.lambda_functions.weekly_insights import SQLAlchemyWeeklyInsightsRepo

    user = User(email="a54_repo@example.com", password_hash=get_password_hash("pass1234"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    repo = SQLAlchemyWeeklyInsightsRepo(db_session)
    week_start = date(2026, 3, 2)
    week_end = date(2026, 3, 8)

    repo.upsert_weekly_insight(
        user_id=user.id,
        week_start=week_start,
        week_end=week_end,
        summary_text="First summary",
        risk_tier="Yellow",
    )
    repo.upsert_weekly_insight(
        user_id=user.id,
        week_start=week_start,
        week_end=week_end,
        summary_text="Updated summary",
        risk_tier="Green",
    )

    rows = (
        db_session.query(WeeklyWellbeingInsight)
        .filter(
            WeeklyWellbeingInsight.user_id == user.id,
            WeeklyWellbeingInsight.week_start == week_start,
            WeeklyWellbeingInsight.week_end == week_end,
        )
        .all()
    )
    assert len(rows) == 1
    assert rows[0].summary_text == "Updated summary"
    assert rows[0].risk_tier == "Green"


def test_lambda_handler_uses_default_sqlalchemy_wiring(db_session, monkeypatch):
    """A5.4: lambda_handler should wire SessionLocal repo/service when deps omitted."""
    from app import lambda_functions as lambda_pkg
    from app.lambda_functions.weekly_insights import lambda_handler

    user = User(email="a54_lambda@example.com", password_hash=get_password_hash("pass1234"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user_id = user.id

    monkeypatch.setattr(
        lambda_pkg.weekly_insights,
        "SessionLocal",
        lambda: db_session,
    )

    response = lambda_handler({"week_start": "2026-03-02"}, None)

    assert response["statusCode"] == 200
    assert response["body"]["total_users"] == 1
    assert response["body"]["processed_users"] == 1

    persisted = (
        db_session.query(WeeklyWellbeingInsight)
        .filter(WeeklyWellbeingInsight.user_id == user_id)
        .all()
    )
    assert len(persisted) == 1
    assert persisted[0].week_start.isoformat() == "2026-03-02"
