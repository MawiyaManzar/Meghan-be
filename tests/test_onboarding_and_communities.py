"""
Tests for:
- Task 3: Onboarding endpoints (UF-1.1)
- Task 4: Communities standardization (UF-4.0)

Assumptions:
- FastAPI TestClient fixture is provided as `client` in tests/conftest.py
- An authenticated user header is provided as `auth_headers`
"""

import json
import pytest
from fastapi import status


class TestOnboardingEndpoints:
    """Tests for Task 3: onboarding profile/privacy + first check-in + community auto-assign."""

    def test_onboarding_profile_saves_fields(self, client, auth_headers):
        """PUT /api/onboarding/profile saves age_range, life_stage, struggles."""
        payload = {
            "age_range": "18-21",
            "life_stage": "college",
            "struggles": ["career", "anxiety"],
        }
        resp = client.put("/api/onboarding/profile", headers=auth_headers, json=payload)

        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["age_range"] == "18-21"
        assert data["life_stage"] == "college"

        # struggles are stored as JSON string in DB
        # we just verify it contains our tags
        stored_struggles = data["struggles"]
        assert isinstance(stored_struggles, str)
        decoded = json.loads(stored_struggles)
        assert "career" in decoded
        assert "anxiety" in decoded

    def test_onboarding_privacy_sets_privacy_level(self, client, auth_headers):
        """PUT /api/onboarding/privacy sets privacy_level."""
        payload = {"privacy_level": "full"}
        resp = client.put("/api/onboarding/privacy", headers=auth_headers, json=payload)

        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["privacy_level"] == "full"

    def test_first_checkin_updates_user_state(self, client, auth_headers):
        """POST /api/checkins/first stores first emotional check-in."""
        payload = {
            "mood": "Pulse",
            "risk_tier": "Yellow",
            "stress_source": "Career/Academics",
        }
        resp = client.post("/api/checkins/first", headers=auth_headers, json=payload)
        assert resp.status_code == status.HTTP_201_CREATED

        # Verify user state
        state_resp = client.get("/api/users/me/state", headers=auth_headers)
        assert state_resp.status_code == status.HTTP_200_OK
        state = state_resp.json()
        assert state["mood"] == "Pulse"
        assert state["risk_tier"] == "Yellow"
        assert state["stress_source"] == "Career/Academics"

    def test_onboarding_auto_assigns_communities_from_struggles(self, client, auth_headers):
        """
        After saving struggles in onboarding/profile, user should be auto-assigned
        to at least one relevant community (based on internal mapping).
        """
        # Save struggles that map to Career/Academics and Relationship stress sources
        payload = {
            "age_range": "18-21",
            "life_stage": "college",
            "struggles": ["career", "relationship"],
        }
        resp = client.put("/api/onboarding/profile", headers=auth_headers, json=payload)
        assert resp.status_code == status.HTTP_200_OK

        # Fetch communities; ensure some are joined
        comm_resp = client.get("/api/communities", headers=auth_headers)
        assert comm_resp.status_code == status.HTTP_200_OK
        data = comm_resp.json()

        # user_communities should contain at least one community id
        user_communities = data["user_communities"]
        assert isinstance(user_communities, list)
        assert len(user_communities) >= 1


class TestCommunitiesEndpoints:
    """Tests for Task 4: communities endpoints and anonymity support."""

    def test_list_communities_returns_defaults(self, client, auth_headers):
        """GET /api/communities returns at least one active community."""
        resp = client.get("/api/communities", headers=auth_headers)
        assert resp.status_code == status.HTTP_200_OK

        data = resp.json()
        communities = data["communities"]
        assert isinstance(communities, list)
        assert len(communities) >= 1

        # Pick first and inspect fields
        c = communities[0]
        assert "id" in c
        assert "name" in c
        assert "description" in c
        assert "stress_source" in c
        assert "is_active" in c

    def test_list_communities_can_filter_by_stress_source(self, client, auth_headers):
        """GET /api/communities?stress_source=Relationship filters communities."""
        resp = client.get(
            "/api/communities?stress_source=Relationship",
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        communities = data["communities"]

        # Either zero or all returned must match the filter
        for c in communities:
            assert c["stress_source"] == "Relationship"

    def test_join_community_creates_membership_with_anonymity(self, client, auth_headers):
        """POST /api/communities/{id}/join sets is_anonymous and updates user_communities."""
        # Get communities to join one
        list_resp = client.get("/api/communities", headers=auth_headers)
        assert list_resp.status_code == status.HTTP_200_OK
        communities = list_resp.json()["communities"]
        assert communities
        comm_id = communities[0]["id"]

        # Join with is_anonymous = True
        join_resp = client.post(
            f"/api/communities/{comm_id}/join",
            headers=auth_headers,
            json={"is_anonymous": True},
        )
        assert join_resp.status_code == status.HTTP_201_CREATED

        # Verify membership is reflected in user_communities
        list_resp2 = client.get("/api/communities", headers=auth_headers)
        assert list_resp2.status_code == status.HTTP_200_OK
        data2 = list_resp2.json()
        assert comm_id in data2["user_communities"]

    def test_communities_endpoints_require_auth(self, client):
        """Communities endpoints must be protected."""
        resp = client.get("/api/communities")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

        resp = client.post("/api/communities/1/join", json={"is_anonymous": True})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

