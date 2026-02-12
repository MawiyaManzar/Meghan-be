"""
Integration tests for Task 9: Crisis Detection Enhancement.

Covers:
- POST /api/crisis/detect (low / high, and medium via LLM monkeypatch)
- GET /api/crisis/resources (default + country-specific)
"""

import pytest
from fastapi import status

from app.services.safety import safety_service


class TestCrisisDetect:
    """Tests for /api/crisis/detect."""

    def test_detect_low_risk(self, client, auth_headers):
        """Neutral text → low risk, allowed=True."""
        response = client.post(
            "/api/crisis/detect",
            headers=auth_headers,
            json={"text": "Today was a normal day, I went to class and studied."},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["risk_level"] in ["low", "medium", "high"]
        # For neutral text we expect low risk in current implementation
        assert data["risk_level"] == "low"
        assert data["allowed"] is True
        assert isinstance(data["matched_phrases"], list)

    def test_detect_high_risk_keyword(self, client, auth_headers):
        """High-risk phrase should trigger high risk and allowed=False."""
        response = client.post(
            "/api/crisis/detect",
            headers=auth_headers,
            json={"text": "I want to kill myself"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["risk_level"] == "high"
        assert data["allowed"] is False
        assert len(data["matched_phrases"]) >= 1
        assert "kill myself" in data["matched_phrases"][0]
        assert isinstance(data.get("safe_reply"), str) and data["safe_reply"]

    def test_detect_medium_risk_with_llm(self, client, auth_headers, monkeypatch):
        """
        Medium-risk text with LLM assessment should return medium and allowed=False.

        We monkeypatch SafetyService._assess_with_llm to avoid relying on real LLM calls.
        """

        def fake_assess_with_llm(text: str):
            return {
                "risk_level": "medium",
                "reasoning": "Contains hopelessness language but no explicit self-harm intent.",
                "safe_reply": "I'm concerned about how you're feeling. Would you like to talk more about it?",
            }

        # Ensure medium-risk patterns match and LLM path is used
        safety_service.llm_service = object()  # any truthy value
        monkeypatch.setattr(safety_service, "_assess_with_llm", fake_assess_with_llm)

        response = client.post(
            "/api/crisis/detect",
            headers=auth_headers,
            json={"text": "I feel hopeless and worthless lately."},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["risk_level"] == "medium"
        assert data["allowed"] is False
        assert len(data["matched_phrases"]) >= 1  # medium patterns matched
        assert isinstance(data.get("safe_reply"), str) and data["safe_reply"]


class TestCrisisResources:
    """Tests for /api/crisis/resources."""

    def test_resources_default_international(self, client):
        """GET /api/crisis/resources without country returns international resources."""
        response = client.get("/api/crisis/resources")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["country"] == "International"
        assert isinstance(data["resources"], list)
        assert len(data["resources"]) >= 2

        names = [r["name"] for r in data["resources"]]
        assert "International Crisis Text Line" in names

    def test_resources_us(self, client):
        """GET /api/crisis/resources?country=US returns US-specific + default resources."""
        response = client.get("/api/crisis/resources?country=US")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["country"] == "US"
        names = [r["name"] for r in data["resources"]]

        assert "National Suicide Prevention Lifeline" in names
        assert "Crisis Text Line" in names

    def test_resources_india(self, client):
        """GET /api/crisis/resources?country=IN returns India-specific + default resources."""
        response = client.get("/api/crisis/resources?country=IN")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["country"] == "IN"
        names = [r["name"] for r in data["resources"]]

        assert "Kiran Mental Health Rehabilitation Helpline (Govt. of India)" in names
        assert "AASRA" in names

    def test_resources_unknown_country_falls_back(self, client):
        """Unknown country code should fall back to default international resources."""
        response = client.get("/api/crisis/resources?country=ZZ")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["country"] == "International"
        names = [r["name"] for r in data["resources"]]
        assert "International Crisis Text Line" in names

