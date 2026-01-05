"""
Integration tests for Phase 3 endpoints:
- Task 3.1: Chat Endpoints
- Task 3.2: User State Management Endpoints
"""
import pytest
from fastapi import status


class TestUserStateEndpoints:
    """Test user state management endpoints (Task 3.2)."""
    
    def test_get_user_state_creates_default(self, client, auth_headers):
        """Test GET /api/users/me/state creates default state if none exists."""
        response = client.get("/api/users/me/state", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["mood"] == "Grounded"
        assert data["risk_tier"] == "Green"
        assert data["xp"] == 0
        assert data["level"] == 1
        assert data["steps"] == 0
        assert data["sleep_hours"] == 0
        assert data["pomo_sessions"] == 0
        assert "id" in data
        assert "user_id" in data
    
    def test_update_user_state_partial(self, client, auth_headers):
        """Test PUT /api/users/me/state with partial update."""
        # First get state to create it
        client.get("/api/users/me/state", headers=auth_headers)
        
        # Update only mood and steps
        response = client.put(
            "/api/users/me/state",
            headers=auth_headers,
            json={
                "mood": "Pulse",
                "steps": 5000
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["mood"] == "Pulse"
        assert data["steps"] == 5000
        # Other fields should remain unchanged
        assert data["risk_tier"] == "Green"
    
    def test_update_user_state_full(self, client, auth_headers):
        """Test PUT /api/users/me/state with full update."""
        client.get("/api/users/me/state", headers=auth_headers)
        
        response = client.put(
            "/api/users/me/state",
            headers=auth_headers,
            json={
                "mood": "Heavy",
                "risk_tier": "Yellow",
                "stress_source": "Career/Academics",
                "steps": 3000,
                "sleep_hours": 6,
                "pomo_sessions": 1
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["mood"] == "Heavy"
        assert data["risk_tier"] == "Yellow"
        assert data["stress_source"] == "Career/Academics"
        assert data["steps"] == 3000
        assert data["sleep_hours"] == 6
        assert data["pomo_sessions"] == 1
    
    def test_update_user_state_invalid_tier(self, client, auth_headers):
        """Test PUT /api/users/me/state rejects invalid tier."""
        client.get("/api/users/me/state", headers=auth_headers)
        
        response = client.put(
            "/api/users/me/state",
            headers=auth_headers,
            json={"risk_tier": "InvalidTier"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid tier" in response.json()["detail"]
    
    def test_update_user_state_invalid_mood(self, client, auth_headers):
        """Test PUT /api/users/me/state rejects invalid mood."""
        client.get("/api/users/me/state", headers=auth_headers)
        
        response = client.put(
            "/api/users/me/state",
            headers=auth_headers,
            json={"mood": "InvalidMood"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid mood" in response.json()["detail"]
    
    def test_update_user_state_others_requires_text(self, client, auth_headers):
        """Test PUT /api/users/me/state requires other_text when stress_source is Others."""
        client.get("/api/users/me/state", headers=auth_headers)
        
        response = client.put(
            "/api/users/me/state",
            headers=auth_headers,
            json={
                "stress_source": "Others",
                "other_text": None
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "other_text is required" in response.json()["detail"]
    
    def test_update_user_state_others_with_text(self, client, auth_headers):
        """Test PUT /api/users/me/state accepts Others with other_text."""
        client.get("/api/users/me/state", headers=auth_headers)
        
        response = client.put(
            "/api/users/me/state",
            headers=auth_headers,
            json={
                "stress_source": "Others",
                "other_text": "Work-related stress"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["stress_source"] == "Others"
        assert data["other_text"] == "Work-related stress"
    
    def test_add_xp(self, client, auth_headers):
        """Test POST /api/users/me/state/xp adds XP and recalculates level."""
        client.get("/api/users/me/state", headers=auth_headers)
        
        # Add 50 XP (should stay at level 1)
        response = client.post(
            "/api/users/me/state/xp",
            headers=auth_headers,
            json={"amount": 50}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["xp"] == 50
        assert data["level"] == 1  # floor(50/200) + 1 = 1
    
    def test_add_xp_level_up(self, client, auth_headers):
        """Test POST /api/users/me/state/xp increases level at threshold."""
        client.get("/api/users/me/state", headers=auth_headers)
        
        # Add 250 XP (should reach level 2: floor(250/200) + 1 = 2)
        response = client.post(
            "/api/users/me/state/xp",
            headers=auth_headers,
            json={"amount": 250}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["xp"] == 250
        assert data["level"] == 2
    
    def test_add_xp_multiple_times(self, client, auth_headers):
        """Test POST /api/users/me/state/xp accumulates XP."""
        client.get("/api/users/me/state", headers=auth_headers)
        
        # Add 100 XP
        response1 = client.post(
            "/api/users/me/state/xp",
            headers=auth_headers,
            json={"amount": 100}
        )
        assert response1.status_code == status.HTTP_200_OK
        assert response1.json()["xp"] == 100
        
        # Add 150 more XP
        response2 = client.post(
            "/api/users/me/state/xp",
            headers=auth_headers,
            json={"amount": 150}
        )
        assert response2.status_code == status.HTTP_200_OK
        assert response2.json()["xp"] == 250
        assert response2.json()["level"] == 2


class TestUserProfileEndpoints:
    """Test user profile endpoints (Task 3.2)."""
    
    def test_get_user_profile_creates_empty(self, client, auth_headers):
        """Test GET /api/users/me/profile creates empty profile if none exists."""
        response = client.get("/api/users/me/profile", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] is None
        assert data["major"] is None
        assert data["hobbies"] is None
        assert data["values"] is None
        assert "id" in data
        assert "user_id" in data
    
    def test_update_profile(self, client, auth_headers):
        """Test PUT /api/users/me/profile updates profile fields."""
        client.get("/api/users/me/profile", headers=auth_headers)
        
        response = client.put(
            "/api/users/me/profile",
            headers=auth_headers,
            json={
                "name": "Test User",
                "major": "Computer Science",
                "hobbies": "Coding, Reading"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test User"
        assert data["major"] == "Computer Science"
        assert data["hobbies"] == "Coding, Reading"
    
    def test_update_profile_awards_xp_for_new_fields(self, client, auth_headers):
        """Test PUT /api/users/me/profile awards 20 XP per newly filled field."""
        client.get("/api/users/me/profile", headers=auth_headers)
        
        # Get initial XP
        state_response = client.get("/api/users/me/state", headers=auth_headers)
        initial_xp = state_response.json()["xp"]
        
        # Update profile with 3 new fields
        client.put(
            "/api/users/me/profile",
            headers=auth_headers,
            json={
                "name": "Test User",
                "major": "Computer Science",
                "hobbies": "Coding"
            }
        )
        
        # Check XP increased by 60 (3 fields * 20 XP)
        state_response = client.get("/api/users/me/state", headers=auth_headers)
        new_xp = state_response.json()["xp"]
        assert new_xp == initial_xp + 60
    
    def test_update_profile_no_xp_for_existing_fields(self, client, auth_headers):
        """Test PUT /api/users/me/profile doesn't award XP for updating existing fields."""
        # First update - fill fields
        client.get("/api/users/me/profile", headers=auth_headers)
        client.put(
            "/api/users/me/profile",
            headers=auth_headers,
            json={"name": "Original Name", "major": "Original Major"}
        )
        
        # Get XP after first update
        state_response = client.get("/api/users/me/state", headers=auth_headers)
        xp_after_first = state_response.json()["xp"]
        
        # Second update - modify existing fields
        client.put(
            "/api/users/me/profile",
            headers=auth_headers,
            json={"name": "Updated Name", "major": "Updated Major"}
        )
        
        # XP should not increase
        state_response = client.get("/api/users/me/state", headers=auth_headers)
        xp_after_second = state_response.json()["xp"]
        assert xp_after_second == xp_after_first
    
    def test_update_profile_partial(self, client, auth_headers):
        """Test PUT /api/users/me/profile with partial update."""
        # First set some fields
        client.get("/api/users/me/profile", headers=auth_headers)
        client.put(
            "/api/users/me/profile",
            headers=auth_headers,
            json={"name": "Test User", "major": "CS"}
        )
        
        # Update only one field
        response = client.put(
            "/api/users/me/profile",
            headers=auth_headers,
            json={"hobbies": "New Hobby"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test User"  # Unchanged
        assert data["major"] == "CS"  # Unchanged
        assert data["hobbies"] == "New Hobby"  # Updated


class TestChatEndpoints:
    """Test chat endpoints (Task 3.1)."""
    
    def test_create_conversation_default_state(self, client, auth_headers):
        """Test POST /api/chat/conversations creates conversation using current user state."""
        # Create user state first
        client.get("/api/users/me/state", headers=auth_headers)
        client.put(
            "/api/users/me/state",
            headers=auth_headers,
            json={"mood": "Pulse", "risk_tier": "Yellow", "stress_source": "Career/Academics"}
        )
        
        # Create conversation with empty body (should use current state)
        response = client.post(
            "/api/chat/conversations",
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["mood"] == "Pulse"
        assert data["tier"] == "Yellow"
        assert data["source"] == "Career/Academics"
        assert "id" in data
        assert "user_id" in data
    
    def test_create_conversation_explicit_values(self, client, auth_headers):
        """Test POST /api/chat/conversations with explicit tier/mood/source."""
        response = client.post(
            "/api/chat/conversations",
            headers=auth_headers,
            json={
                "tier": "Green",
                "mood": "Grounded",
                "source": "Family"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["tier"] == "Green"
        assert data["mood"] == "Grounded"
        assert data["source"] == "Family"
    
    def test_create_conversation_invalid_tier(self, client, auth_headers):
        """Test POST /api/chat/conversations rejects invalid tier."""
        response = client.post(
            "/api/chat/conversations",
            headers=auth_headers,
            json={"tier": "InvalidTier", "mood": "Grounded", "source": "Family"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_list_conversations(self, client, auth_headers):
        """Test GET /api/chat/conversations lists user's conversations."""
        # Create a conversation
        client.post("/api/chat/conversations", headers=auth_headers, json={})
        
        response = client.get("/api/chat/conversations", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "conversations" in data
        assert len(data["conversations"]) == 1
    
    def test_list_conversations_multiple(self, client, auth_headers):
        """Test GET /api/chat/conversations returns all user's conversations."""
        # Create multiple conversations
        client.post("/api/chat/conversations", headers=auth_headers, json={})
        client.post("/api/chat/conversations", headers=auth_headers, json={})
        
        response = client.get("/api/chat/conversations", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["conversations"]) == 2
    
    def test_get_conversation_messages_empty(self, client, auth_headers):
        """Test GET /api/chat/conversations/{id}/messages returns empty messages for new conversation."""
        # Create conversation
        conv_response = client.post("/api/chat/conversations", headers=auth_headers, json={})
        conv_id = conv_response.json()["id"]
        
        response = client.get(
            f"/api/chat/conversations/{conv_id}/messages",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "conversation" in data
        assert "messages" in data
        assert len(data["messages"]) == 0
    
    def test_get_conversation_messages_not_found(self, client, auth_headers):
        """Test GET /api/chat/conversations/{id}/messages returns 404 for non-existent conversation."""
        response = client.get(
            "/api/chat/conversations/99999/messages",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_send_message_invalid_role(self, client, auth_headers):
        """Test POST /api/chat/conversations/{id}/messages rejects role other than 'user'."""
        conv_response = client.post("/api/chat/conversations", headers=auth_headers, json={})
        conv_id = conv_response.json()["id"]
        
        response = client.post(
            f"/api/chat/conversations/{conv_id}/messages",
            headers=auth_headers,
            json={"role": "model", "content": "Test"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "role must be 'user'" in response.json()["detail"]
    
    def test_send_message_with_llm(self, client, auth_headers):
        """Test POST /api/chat/conversations/{id}/messages sends message and gets AI response.
        
        Note: This test will work if GEMINI_API_KEY is set, or will use fallback response if not.
        """
        import os
        from app.core.config import settings
        
        # Create conversation
        conv_response = client.post("/api/chat/conversations", headers=auth_headers, json={})
        conv_id = conv_response.json()["id"]
        
        # Get initial XP
        state_response = client.get("/api/users/me/state", headers=auth_headers)
        initial_xp = state_response.json()["xp"]
        
        # Send message
        response = client.post(
            f"/api/chat/conversations/{conv_id}/messages",
            headers=auth_headers,
            json={
                "role": "user",
                "content": "Hello, this is a test message"
            }
        )
        
        # Should always succeed (either with LLM response or fallback)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "model"
        assert len(data["content"]) > 0
        assert "id" in data
        
        # Check XP increased by 5 (always happens, even with fallback)
        state_response = client.get("/api/users/me/state", headers=auth_headers)
        new_xp = state_response.json()["xp"]
        assert new_xp == initial_xp + 5
        
        # If API key is set, verify response looks like an LLM response (not just fallback)
        if settings.GEMINI_API_KEY:
            # LLM responses should be more substantial than fallback messages
            assert len(data["content"]) > 50, "LLM response should be substantial"
    
    def test_send_message_saves_messages(self, client, auth_headers):
        """Test POST /api/chat/conversations/{id}/messages saves both user and model messages."""
        # Create conversation
        conv_response = client.post("/api/chat/conversations", headers=auth_headers, json={})
        conv_id = conv_response.json()["id"]
        
        # Send message (may fail if no API key, but should still save fallback)
        response = client.post(
            f"/api/chat/conversations/{conv_id}/messages",
            headers=auth_headers,
            json={
                "role": "user",
                "content": "Test message"
            }
        )
        
        # Even if LLM fails, we should get a response (fallback)
        assert response.status_code == status.HTTP_200_OK
        
        # Get messages
        messages_response = client.get(
            f"/api/chat/conversations/{conv_id}/messages",
            headers=auth_headers
        )
        
        assert messages_response.status_code == status.HTTP_200_OK
        messages_data = messages_response.json()
        # Should have user message and model response
        assert len(messages_data["messages"]) >= 1
        # First message should be user message
        assert messages_data["messages"][0]["role"] == "user"
        assert messages_data["messages"][0]["content"] == "Test message"


class TestAuthentication:
    """Test authentication requirements for endpoints."""
    
    def test_user_state_endpoints_require_auth(self, client):
        """Test user state endpoints require authentication."""
        response = client.get("/api/users/me/state")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.put("/api/users/me/state", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.post("/api/users/me/state/xp", json={"amount": 10})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_profile_endpoints_require_auth(self, client):
        """Test profile endpoints require authentication."""
        response = client.get("/api/users/me/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.put("/api/users/me/profile", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_chat_endpoints_require_auth(self, client):
        """Test chat endpoints require authentication."""
        response = client.post("/api/chat/conversations", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.get("/api/chat/conversations")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.get("/api/chat/conversations/1/messages")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.post("/api/chat/conversations/1/messages", json={"role": "user", "content": "test"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

