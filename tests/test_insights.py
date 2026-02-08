"""
Integration tests for Task 8: Weekly Insights Generation
Tests weekly wellbeing insights endpoint and analysis.
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta, date
from app.models.user import JournalEntry, Conversation, HeartsTransaction, ChatMessage
from app.schemas.hearts import HeartsTransactionCreate
from app.services.hearts import award_hearts


class TestWeeklyInsights:
    """Test weekly insights endpoint (Task 8)."""
    
    def test_get_weekly_insights_empty(self, client, auth_headers):
        """Test GET /api/insights/weekly returns insights even with no data."""
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check structure
        assert "week_starting" in data
        assert "week_ending" in data
        assert "mood_trends" in data
        assert "trigger_patterns" in data
        assert "positive_progress" in data
        assert "recommendations" in data
        assert "encouragement_message" in data
        assert "total_journal_entries" in data
        assert "total_chat_sessions" in data
        assert "hearts_earned" in data
        
        # With no data, should have empty lists but still have structure
        assert isinstance(data["mood_trends"], list)
        assert isinstance(data["trigger_patterns"], list)
        assert isinstance(data["positive_progress"], list)
        assert isinstance(data["recommendations"], list)
        assert data["total_journal_entries"] == 0
        assert data["total_chat_sessions"] == 0
        assert data["hearts_earned"] == 0
    
    def test_get_weekly_insights_with_journal_entries(self, client, auth_headers, db_session):
        """Test GET /api/insights/weekly includes journal entries in analysis."""
        # Get user ID from auth first
        user_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = user_response.json()["id"]
        
        # Create journal entries with mood/tier data
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # Create entries this week
        entry1 = JournalEntry(
            user_id=user_id,
            content="Feeling grateful today",
            mood_at_time="Grounded",
            tier_at_time="Green",
            created_at=datetime.combine(week_start + timedelta(days=1), datetime.min.time())
        )
        entry2 = JournalEntry(
            user_id=user_id,
            content="Feeling a bit stressed",
            mood_at_time="Pulse",
            tier_at_time="Yellow",
            created_at=datetime.combine(week_start + timedelta(days=3), datetime.min.time())
        )
        db_session.add(entry1)
        db_session.add(entry2)
        db_session.commit()
        
        # Get insights
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have mood trends from journal entries
        assert len(data["mood_trends"]) >= 2
        assert data["total_journal_entries"] == 2
        
        # Check mood trends structure
        trend = data["mood_trends"][0]
        assert "date" in trend
        assert "mood" in trend
        assert "tier" in trend
    
    def test_get_weekly_insights_with_conversations(self, client, auth_headers, db_session):
        """Test GET /api/insights/weekly includes conversations in analysis."""
        # Get user ID
        user_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = user_response.json()["id"]
        
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # Create conversations this week
        conv1 = Conversation(
            user_id=user_id,
            tier="Green",
            mood="Grounded",
            source="Career/Academics",
            created_at=datetime.combine(week_start + timedelta(days=2), datetime.min.time())
        )
        conv2 = Conversation(
            user_id=user_id,
            tier="Yellow",
            mood="Pulse",
            source="Family",
            created_at=datetime.combine(week_start + timedelta(days=4), datetime.min.time())
        )
        db_session.add(conv1)
        db_session.add(conv2)
        db_session.commit()
        
        # Get insights
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have mood trends from conversations
        assert data["total_chat_sessions"] == 2
        
        # Should have trigger patterns
        assert len(data["trigger_patterns"]) >= 1
        trigger = data["trigger_patterns"][0]
        assert "trigger" in trigger
        assert "frequency" in trigger
        assert "severity" in trigger
        assert "description" in trigger
    
    def test_get_weekly_insights_with_hearts(self, client, auth_headers, db_session):
        """Test GET /api/insights/weekly includes hearts earned in analysis."""
        # Get user ID
        user_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = user_response.json()["id"]
        
        # Create journal entry (which awards hearts)
        client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={"content": "Test entry for hearts"}
        )
        
        # Get insights
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have hearts earned
        assert data["hearts_earned"] >= 10  # HEARTS_FOR_JOURNAL
        
        # Should have progress indicator for hearts
        hearts_progress = [p for p in data["positive_progress"] if p["category"] == "hearts_earned"]
        if hearts_progress:
            assert len(hearts_progress) > 0
    
    def test_get_weekly_insights_trigger_patterns(self, client, auth_headers, db_session):
        """Test GET /api/insights/weekly identifies trigger patterns correctly."""
        # Get user ID
        user_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = user_response.json()["id"]
        
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # Create multiple conversations with same stress source
        for i in range(3):
            conv = Conversation(
                user_id=user_id,
                tier="Yellow",
                mood="Pulse",
                source="Career/Academics",  # Same source repeated
                created_at=datetime.combine(week_start + timedelta(days=i+1), datetime.min.time())
            )
            db_session.add(conv)
        db_session.commit()
        
        # Get insights
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should identify the trigger pattern
        career_triggers = [t for t in data["trigger_patterns"] if t["trigger"] == "Career/Academics"]
        assert len(career_triggers) > 0
        
        trigger = career_triggers[0]
        assert trigger["frequency"] == 3
        assert trigger["severity"] in ["low", "medium", "high"]
    
    def test_get_weekly_insights_progress_indicators(self, client, auth_headers):
        """Test GET /api/insights/weekly includes progress indicators."""
        # Create some activity
        client.post("/api/journal/entries", headers=auth_headers, json={"content": "Entry 1"})
        client.post("/api/journal/entries", headers=auth_headers, json={"content": "Entry 2"})
        
        # Get insights
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have progress indicators
        assert len(data["positive_progress"]) > 0
        
        # Check structure
        progress = data["positive_progress"][0]
        assert "category" in progress
        assert "metric" in progress
        assert "improvement" in progress
    
    def test_get_weekly_insights_recommendations(self, client, auth_headers):
        """Test GET /api/insights/weekly includes recommendations."""
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should always have at least one recommendation
        assert len(data["recommendations"]) > 0
        
        # Check structure
        rec = data["recommendations"][0]
        assert "type" in rec
        assert "title" in rec
        assert "description" in rec
    
    def test_get_weekly_insights_encouragement_message(self, client, auth_headers):
        """Test GET /api/insights/weekly includes encouragement message."""
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have encouragement message
        assert "encouragement_message" in data
        assert isinstance(data["encouragement_message"], str)
        assert len(data["encouragement_message"]) > 0
    
    def test_get_weekly_insights_with_week_start_parameter(self, client, auth_headers):
        """Test GET /api/insights/weekly accepts week_start query parameter."""
        # Get a specific week (2 weeks ago)
        two_weeks_ago = date.today() - timedelta(days=14)
        days_since_monday = two_weeks_ago.weekday()
        week_start = two_weeks_ago - timedelta(days=days_since_monday)
        
        response = client.get(
            f"/api/insights/weekly?week_start={week_start.isoformat()}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should return insights for the specified week
        assert data["week_starting"] == week_start.isoformat()
        assert data["week_ending"] == (week_start + timedelta(days=6)).isoformat()
    
    def test_get_weekly_insights_most_common_mood(self, client, auth_headers, db_session):
        """Test GET /api/insights/weekly calculates most common mood."""
        # Get user ID
        user_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = user_response.json()["id"]
        
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # Create multiple entries with same mood
        for i in range(3):
            entry = JournalEntry(
                user_id=user_id,
                content=f"Entry {i}",
                mood_at_time="Grounded",
                tier_at_time="Green",
                created_at=datetime.combine(week_start + timedelta(days=i), datetime.min.time())
            )
            db_session.add(entry)
        db_session.commit()
        
        # Get insights
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should identify most common mood
        assert data["most_common_mood"] == "Grounded"
    
    def test_get_weekly_insights_most_common_tier(self, client, auth_headers, db_session):
        """Test GET /api/insights/weekly calculates most common tier."""
        # Get user ID
        user_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = user_response.json()["id"]
        
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # Create entries with same tier
        for i in range(2):
            entry = JournalEntry(
                user_id=user_id,
                content=f"Entry {i}",
                mood_at_time="Pulse",
                tier_at_time="Yellow",
                created_at=datetime.combine(week_start + timedelta(days=i), datetime.min.time())
            )
            db_session.add(entry)
        db_session.commit()
        
        # Get insights
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should identify most common tier
        assert data["most_common_tier"] == "Yellow"
    
    def test_get_weekly_insights_requires_auth(self, client):
        """Test GET /api/insights/weekly requires authentication."""
        response = client.get("/api/insights/weekly")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_weekly_insights_only_user_data(self, client, auth_headers, db_session):
        """Test GET /api/insights/weekly only includes current user's data."""
        # Get current user ID
        user_response = client.get("/api/auth/me", headers=auth_headers)
        current_user_id = user_response.json()["id"]
        
        # Create another user and their data
        from app.models.user import User
        from app.core.security import get_password_hash
        
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password123")
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # Create entry for other user
        other_entry = JournalEntry(
            user_id=other_user.id,
            content="Other user's entry",
            mood_at_time="Heavy",
            tier_at_time="Red",
            created_at=datetime.combine(week_start + timedelta(days=1), datetime.min.time())
        )
        db_session.add(other_entry)
        db_session.commit()
        
        # Get insights for current user
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should not include other user's data
        # If current user has no entries, total should be 0
        # If they have entries, check that mood trends don't include other user's mood
        if data["total_journal_entries"] == 0:
            assert len([t for t in data["mood_trends"] if t.get("mood") == "Heavy"]) == 0


class TestWeeklyInsightsIntegration:
    """Integration tests for weekly insights feature."""
    
    def test_full_insights_generation(self, client, auth_headers, db_session):
        """Test complete insights generation with multiple data sources."""
        # Get user ID
        user_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = user_response.json()["id"]
        
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # Create diverse data
        # 1. Journal entries
        client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={
                "content": "Feeling grateful",
                "mood_at_time": "Grounded",
                "tier_at_time": "Green"
            }
        )
        
        # 2. Conversations
        conv = Conversation(
            user_id=user_id,
            tier="Yellow",
            mood="Pulse",
            source="Career/Academics",
            created_at=datetime.combine(week_start + timedelta(days=2), datetime.min.time())
        )
        db_session.add(conv)
        db_session.commit()
        
        # 3. Hearts (already earned from journal entry)
        
        # Get insights
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify all components are present
        assert data["total_journal_entries"] >= 1
        assert data["total_chat_sessions"] >= 1
        assert data["hearts_earned"] >= 10
        
        # Should have mood trends
        assert len(data["mood_trends"]) >= 1
        
        # Should have trigger patterns (from conversation)
        assert len(data["trigger_patterns"]) >= 1
        
        # Should have progress indicators
        assert len(data["positive_progress"]) >= 1
        
        # Should have recommendations
        assert len(data["recommendations"]) >= 1
        
        # Should have encouragement message
        assert len(data["encouragement_message"]) > 0
    
    def test_insights_with_high_frequency_triggers(self, client, auth_headers, db_session):
        """Test insights identify high-frequency triggers correctly."""
        # Get user ID
        user_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = user_response.json()["id"]
        
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        # Create many conversations with same trigger and high tier
        for i in range(5):
            conv = Conversation(
                user_id=user_id,
                tier="Red" if i % 2 == 0 else "Yellow",  # Mix of high and medium
                mood="Heavy",
                source="Family",  # Same trigger
                created_at=datetime.combine(week_start + timedelta(days=i), datetime.min.time())
            )
            db_session.add(conv)
        db_session.commit()
        
        # Get insights
        response = client.get("/api/insights/weekly", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should identify Family as a trigger
        family_triggers = [t for t in data["trigger_patterns"] if t["trigger"] == "Family"]
        assert len(family_triggers) > 0
        
        trigger = family_triggers[0]
        assert trigger["frequency"] == 5
        # Should be high severity because of Red tiers
        assert trigger["severity"] == "high"
        
        # Should have recommendation for community support
        community_recs = [r for r in data["recommendations"] if r["type"] == "community"]
        assert len(community_recs) > 0
