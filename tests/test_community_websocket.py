"""
Tests for the community WebSocket server (app/routers/community_ws.py).

Verifies:
- WebSocket connection with valid JWT and community membership
- Sending messages and receiving broadcast
- Error handling (no token, invalid JSON, empty content)
"""

import json
import pytest

from app.routers import community_ws
from app.services.communities import ensure_default_communities
from app.models.user import ProblemCommunity, CommunityMembership


class TestCommunityWebSocket:
    """Tests for /api/communities/ws/{community_id} WebSocket endpoint."""

    def test_websocket_connects_and_echoes_message(
        self, client, db_session, test_user, auth_token
    ):
        """
        Connect with valid JWT, send a message, receive broadcast.
        Success: Server accepts connection and broadcasts the message back.
        """
        # Setup: ensure communities exist and user is a member
        ensure_default_communities(db_session)
        db_session.commit()
        community = db_session.query(ProblemCommunity).first()
        assert community is not None

        membership = CommunityMembership(
            user_id=test_user.id,
            community_id=community.id,
            is_anonymous=True,
        )
        db_session.add(membership)
        db_session.commit()

        # Patch SessionLocal so WebSocket uses our test database
        original_session_local = community_ws.SessionLocal
        community_ws.SessionLocal = lambda: db_session

        try:
            with client.websocket_connect(
                f"/api/communities/ws/{community.id}?token={auth_token}"
            ) as websocket:
                # Send a valid message
                websocket.send_json({
                    "type": "message",
                    "content": "Hello from test",
                    "is_anonymous": True,
                })
                # Receive the broadcast (server echoes to all, including sender)
                data = websocket.receive_json()
                assert data["type"] == "message"
                assert "message" in data
                msg = data["message"]
                assert msg["content"] == "Hello from test"
                assert msg["community_id"] == community.id
                assert msg["is_anonymous"] is True
        finally:
            community_ws.SessionLocal = original_session_local

    def test_websocket_rejects_without_token(self, client, db_session):
        """
        Connection without token should be rejected.
        Success: WebSocket closes with policy violation.
        """
        ensure_default_communities(db_session)
        db_session.commit()
        community = db_session.query(ProblemCommunity).first()
        assert community is not None

        # Patch SessionLocal for ensure_default_communities (not used in WS path)
        original_session_local = community_ws.SessionLocal
        community_ws.SessionLocal = lambda: db_session

        try:
            with pytest.raises(Exception):  # Connection closes abnormally
                with client.websocket_connect(
                    f"/api/communities/ws/{community.id}"
                ) as websocket:
                    websocket.receive_json()
        finally:
            community_ws.SessionLocal = original_session_local

    def test_websocket_rejects_non_member(self, client, db_session, test_user, auth_token):
        """
        User who is not a community member should be rejected.
        Success: WebSocket accepts then sends error and closes.
        """
        ensure_default_communities(db_session)
        db_session.commit()
        community = db_session.query(ProblemCommunity).first()
        assert community is not None
        # Do NOT add membership - user is not a member

        original_session_local = community_ws.SessionLocal
        community_ws.SessionLocal = lambda: db_session

        try:
            with client.websocket_connect(
                f"/api/communities/ws/{community.id}?token={auth_token}"
            ) as websocket:
                # Server accepts then sends error JSON and closes
                data = websocket.receive_json()
                assert data["type"] == "error"
                assert "not a member" in data.get("detail", "").lower()
        finally:
            community_ws.SessionLocal = original_session_local

    def test_websocket_rejects_empty_content(
        self, client, db_session, test_user, auth_token
    ):
        """
        Sending message with empty content returns error.
        Success: Server sends error JSON, does not broadcast.
        """
        ensure_default_communities(db_session)
        db_session.commit()
        community = db_session.query(ProblemCommunity).first()
        membership = CommunityMembership(
            user_id=test_user.id,
            community_id=community.id,
            is_anonymous=True,
        )
        db_session.add(membership)
        db_session.commit()

        original_session_local = community_ws.SessionLocal
        community_ws.SessionLocal = lambda: db_session

        try:
            with client.websocket_connect(
                f"/api/communities/ws/{community.id}?token={auth_token}"
            ) as websocket:
                websocket.send_json({
                    "type": "message",
                    "content": "   ",
                    "is_anonymous": True,
                })
                data = websocket.receive_json()
                assert data["type"] == "error"
                assert "empty" in data.get("detail", "").lower()
        finally:
            community_ws.SessionLocal = original_session_local
