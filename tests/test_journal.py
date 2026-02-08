"""
Integration tests for Task 7: Journaling Endpoints
Tests all endpoints for journal prompts, entries, and voice uploads.
"""
import pytest
from fastapi import status
from app.models.user import JournalEntry, CrisisEvent


class TestJournalPrompts:
    """Test journal prompts endpoint (Task 7)."""
    
    def test_get_journal_prompts(self, client, auth_headers):
        """Test GET /api/journal/prompts returns available prompts."""
        response = client.get("/api/journal/prompts", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "prompts" in data
        assert len(data["prompts"]) > 0
        
        # Check structure of first prompt
        prompt = data["prompts"][0]
        assert "id" in prompt
        assert "title" in prompt
        assert "description" in prompt
        assert "prompt_text" in prompt
    
    def test_get_journal_prompts_has_expected_prompts(self, client, auth_headers):
        """Test GET /api/journal/prompts includes expected prompt types."""
        response = client.get("/api/journal/prompts", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        prompt_ids = [p["id"] for p in data["prompts"]]
        
        # Check for expected prompts
        expected_prompts = ["gratitude", "stress_relief", "daily_reflection", "future_self", "emotions", "achievements"]
        for expected_id in expected_prompts:
            assert expected_id in prompt_ids, f"Expected prompt '{expected_id}' not found"
    
    def test_get_journal_prompts_requires_auth(self, client):
        """Test GET /api/journal/prompts requires authentication."""
        response = client.get("/api/journal/prompts")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestJournalEntries:
    """Test journal entry endpoints (Task 7)."""
    
    def test_create_journal_entry_success(self, client, auth_headers):
        """Test POST /api/journal/entries creates entry successfully."""
        response = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={
                "content": "Today I'm feeling grateful for my friends and family."
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "Today I'm feeling grateful for my friends and family."
        assert data["mood_at_time"] is None  # Not provided
        assert data["tier_at_time"] is None  # Not provided
        assert data["xp_gained"] == 10  # HEARTS_FOR_JOURNAL
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
    
    def test_create_journal_entry_with_mood_and_tier(self, client, auth_headers):
        """Test POST /api/journal/entries with explicit mood and tier."""
        response = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={
                "content": "Feeling a bit overwhelmed today.",
                "mood_at_time": "Heavy",
                "tier_at_time": "Yellow"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["mood_at_time"] == "Heavy"
        assert data["tier_at_time"] == "Yellow"
    
    def test_create_journal_entry_safety_gate_blocks(self, client, auth_headers):
        """Test POST /api/journal/entries blocks high-risk content via safety gate."""
        response = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={
                "content": "I want to kill myself"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "high-risk content" in response.json()["detail"].lower()
    
    def test_create_journal_entry_awards_hearts(self, client, auth_headers, db_session):
        """Test POST /api/journal/entries awards hearts to user."""
        # Get initial hearts balance
        hearts_response = client.get("/api/hearts/balance", headers=auth_headers)
        initial_balance = hearts_response.json()["total_earned"]
        
        # Create journal entry
        response = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={"content": "Reflecting on my day"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check hearts increased
        hearts_response = client.get("/api/hearts/balance", headers=auth_headers)
        new_balance = hearts_response.json()["total_earned"]
        assert new_balance == initial_balance + 10  # HEARTS_FOR_JOURNAL
    
    def test_list_journal_entries_empty(self, client, auth_headers):
        """Test GET /api/journal/entries returns empty list when no entries exist."""
        response = client.get("/api/journal/entries", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["entries"] == []
        assert data["total"] == 0
    
    def test_list_journal_entries_with_data(self, client, auth_headers):
        """Test GET /api/journal/entries returns user's entries."""
        # Create multiple entries
        client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={"content": "First journal entry"}
        )
        client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={"content": "Second journal entry"}
        )
        
        response = client.get("/api/journal/entries", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["entries"]) == 2
        assert data["total"] == 2
        # Should be ordered by most recent first
        assert data["entries"][0]["content"] == "Second journal entry"
        assert data["entries"][1]["content"] == "First journal entry"
    
    def test_list_journal_entries_pagination(self, client, auth_headers):
        """Test GET /api/journal/entries supports pagination."""
        # Create 5 entries
        for i in range(5):
            client.post(
                "/api/journal/entries",
                headers=auth_headers,
                json={"content": f"Journal entry {i}"}
            )
        
        # Get first page (limit=2)
        response = client.get("/api/journal/entries?limit=2&offset=0", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["entries"]) == 2
        assert data["total"] == 5
        
        # Get second page
        response = client.get("/api/journal/entries?limit=2&offset=2", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["entries"]) == 2
        assert data["offset"] == 2 if "offset" in data else True  # Some implementations don't return offset
    
    def test_list_journal_entries_only_user_entries(self, client, auth_headers, db_session):
        """Test GET /api/journal/entries only returns current user's entries."""
        # Create entry for current user
        response1 = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={"content": "My entry"}
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Create another user and their entry (directly in DB)
        from app.models.user import User
        from app.core.security import get_password_hash
        
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password123")
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        other_entry = JournalEntry(
            user_id=other_user.id,
            content="Other user's entry"
        )
        db_session.add(other_entry)
        db_session.commit()
        
        # List entries - should only see current user's
        response = client.get("/api/journal/entries", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["entries"][0]["content"] == "My entry"
    
    def test_create_journal_entry_requires_auth(self, client):
        """Test POST /api/journal/entries requires authentication."""
        response = client.post(
            "/api/journal/entries",
            json={"content": "Test entry"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_journal_entries_requires_auth(self, client):
        """Test GET /api/journal/entries requires authentication."""
        response = client.get("/api/journal/entries")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestVoiceUpload:
    """Test voice note upload endpoint (Task 7 - stub)."""
    
    @pytest.fixture
    def test_journal_entry(self, client, auth_headers):
        """Create a test journal entry for voice upload."""
        response = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={"content": "Test entry for voice upload"}
        )
        return response.json()
    
    def test_upload_voice_note_success(self, client, auth_headers, test_journal_entry):
        """Test POST /api/journal/entries/{id}/voice accepts audio file."""
        # Create a mock audio file
        audio_content = b"fake audio content"
        
        response = client.post(
            f"/api/journal/entries/{test_journal_entry['id']}/voice",
            headers=auth_headers,
            files={"file": ("test_audio.mp3", audio_content, "audio/mpeg")}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["entry_id"] == test_journal_entry["id"]
        assert "filename" in data
        assert "stub" in data["message"].lower() or "not yet implemented" in data.get("note", "").lower()
    
    def test_upload_voice_note_invalid_file_type(self, client, auth_headers, test_journal_entry):
        """Test POST /api/journal/entries/{id}/voice rejects non-audio files."""
        # Try uploading a text file
        text_content = b"this is not audio"
        
        response = client.post(
            f"/api/journal/entries/{test_journal_entry['id']}/voice",
            headers=auth_headers,
            files={"file": ("test.txt", text_content, "text/plain")}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "audio" in response.json()["detail"].lower()
    
    def test_upload_voice_note_entry_not_found(self, client, auth_headers):
        """Test POST /api/journal/entries/{id}/voice returns 404 for invalid entry."""
        audio_content = b"fake audio"
        
        response = client.post(
            "/api/journal/entries/99999/voice",
            headers=auth_headers,
            files={"file": ("test.mp3", audio_content, "audio/mpeg")}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_upload_voice_note_requires_auth(self, client, auth_headers):
        """Test POST /api/journal/entries/{id}/voice requires authentication."""
        # First create an entry (with auth)
        entry_response = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={"content": "Test entry"}
        )
        entry_id = entry_response.json()["id"]
        
        # Try to upload voice without auth
        audio_content = b"fake audio"
        response = client.post(
            f"/api/journal/entries/{entry_id}/voice",
            files={"file": ("test.mp3", audio_content, "audio/mpeg")}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestJournalIntegration:
    """Integration tests for journal feature."""
    
    def test_full_journal_flow(self, client, auth_headers):
        """Test complete flow: get prompts, create entry, list entries."""
        # 1. Get prompts
        prompts_response = client.get("/api/journal/prompts", headers=auth_headers)
        assert prompts_response.status_code == status.HTTP_200_OK
        prompts = prompts_response.json()["prompts"]
        assert len(prompts) > 0
        
        # 2. Create entry using a prompt
        selected_prompt = prompts[0]
        entry_response = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={
                "content": f"Reflecting on: {selected_prompt['prompt_text']}"
            }
        )
        assert entry_response.status_code == status.HTTP_201_CREATED
        entry_id = entry_response.json()["id"]
        
        # 3. List entries (should include the one we just created)
        list_response = client.get("/api/journal/entries", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        assert list_response.json()["total"] >= 1
        
        # 4. Verify hearts were awarded
        hearts_response = client.get("/api/hearts/balance", headers=auth_headers)
        hearts_data = hearts_response.json()
        assert hearts_data["total_earned"] >= 10  # At least one journal entry worth
    
    def test_journal_entries_optional_fields(self, client, auth_headers):
        """Test that mood_at_time and tier_at_time are truly optional."""
        # Create entry without mood/tier
        response1 = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={"content": "Entry without mood or tier"}
        )
        assert response1.status_code == status.HTTP_201_CREATED
        assert response1.json()["mood_at_time"] is None
        assert response1.json()["tier_at_time"] is None
        
        # Create entry with mood only
        response2 = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={
                "content": "Entry with mood only",
                "mood_at_time": "Grounded"
            }
        )
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.json()["mood_at_time"] == "Grounded"
        assert response2.json()["tier_at_time"] is None
        
        # Create entry with both
        response3 = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={
                "content": "Entry with both",
                "mood_at_time": "Pulse",
                "tier_at_time": "Yellow"
            }
        )
        assert response3.status_code == status.HTTP_201_CREATED
        assert response3.json()["mood_at_time"] == "Pulse"
        assert response3.json()["tier_at_time"] == "Yellow"
    
    def test_journal_safety_gate_logs_crisis_event(self, client, auth_headers, db_session):
        """Test that high-risk journal content logs a crisis event."""
        # Create entry with high-risk content
        response = client.post(
            "/api/journal/entries",
            headers=auth_headers,
            json={"content": "I want to kill myself"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check that crisis event was logged
        crisis_events = db_session.query(CrisisEvent).filter(
            CrisisEvent.source == "journal"
        ).all()
        
        # Should have at least one crisis event (may have multiple from other tests)
        assert len(crisis_events) >= 1
        
        # Check the most recent one
        latest_event = max(crisis_events, key=lambda e: e.created_at)
        assert latest_event.source == "journal"
        assert "kill myself" in latest_event.message_excerpt.lower()
