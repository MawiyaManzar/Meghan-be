"""
Integration tests for Task 6: Micro Expressions Feature
Tests all endpoints for micro expressions and empathy responses.
"""
import pytest
from fastapi import status
from app.models.user import ProblemCommunity, MicroExpression, EmpathyResponse, HeartsTransaction


@pytest.fixture
def test_community(db_session):
    """Create a test community for expressions."""
    community = ProblemCommunity(
        name="Test Community",
        description="A test community for expressions",
        stress_source="Career/Academics",
        is_active=True
    )
    db_session.add(community)
    db_session.commit()
    db_session.refresh(community)
    return community


class TestMicroExpressions:
    """Test micro expressions endpoints (Task 6)."""
    
    def test_create_expression_success(self, client, auth_headers, test_community):
        """Test POST /api/expressions creates expression successfully."""
        response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={
                "content": "Feeling overwhelmed with exams this week",
                "community_id": test_community.id,
                "is_anonymous": True
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "Feeling overwhelmed with exams this week"
        assert data["community_id"] == test_community.id
        assert data["is_anonymous"] is True
        assert data["hearts_awarded"] == 5  # HEARTS_FOR_EXPRESSION
        assert "id" in data
        assert "created_at" in data
    
    def test_create_expression_without_community(self, client, auth_headers):
        """Test POST /api/expressions works without community_id."""
        response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={
                "content": "Just need to vent about my day",
                "is_anonymous": False
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "Just need to vent about my day"
        assert data["community_id"] is None
        assert data["is_anonymous"] is False
    
    def test_create_expression_280_char_limit(self, client, auth_headers):
        """Test POST /api/expressions enforces 280 character limit."""
        # Create content exactly 280 characters
        content_280 = "a" * 280
        
        response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={"content": content_280}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Try with 281 characters
        content_281 = "a" * 281
        
        response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={"content": content_281}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Pydantic validation error
    
    def test_create_expression_invalid_community(self, client, auth_headers):
        """Test POST /api/expressions returns 404 for invalid community_id."""
        response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={
                "content": "Test expression",
                "community_id": 99999  # Non-existent community
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Community not found" in response.json()["detail"]
    
    def test_create_expression_safety_gate_blocks(self, client, auth_headers):
        """Test POST /api/expressions blocks high-risk content via safety gate."""
        response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={
                "content": "I want to kill myself",
                "is_anonymous": True
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "high-risk content" in response.json()["detail"].lower()
    
    def test_create_expression_awards_hearts(self, client, auth_headers, db_session):
        """Test POST /api/expressions awards hearts to author."""
        # Get initial hearts balance
        hearts_response = client.get("/api/hearts/balance", headers=auth_headers)
        initial_balance = hearts_response.json()["total_earned"]
        
        # Create expression
        response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={"content": "Feeling grateful today"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check hearts increased
        hearts_response = client.get("/api/hearts/balance", headers=auth_headers)
        new_balance = hearts_response.json()["total_earned"]
        assert new_balance == initial_balance + 5  # HEARTS_FOR_EXPRESSION
    
    def test_list_expressions_empty(self, client, auth_headers):
        """Test GET /api/expressions returns empty list when no expressions exist."""
        response = client.get("/api/expressions", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["limit"] == 20
        assert data["offset"] == 0
    
    def test_list_expressions_with_data(self, client, auth_headers, test_community):
        """Test GET /api/expressions returns expressions."""
        # Create multiple expressions
        client.post(
            "/api/expressions",
            headers=auth_headers,
            json={"content": "First expression"}
        )
        client.post(
            "/api/expressions",
            headers=auth_headers,
            json={"content": "Second expression", "community_id": test_community.id}
        )
        
        response = client.get("/api/expressions", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2
        # Should be ordered by most recent first
        assert data["items"][0]["content"] == "Second expression"
        assert data["items"][1]["content"] == "First expression"
    
    def test_list_expressions_pagination(self, client, auth_headers):
        """Test GET /api/expressions supports pagination."""
        # Create 5 expressions
        for i in range(5):
            client.post(
                "/api/expressions",
                headers=auth_headers,
                json={"content": f"Expression {i}"}
            )
        
        # Get first page (limit=2)
        response = client.get("/api/expressions?limit=2&offset=0", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 0
        
        # Get second page
        response = client.get("/api/expressions?limit=2&offset=2", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["offset"] == 2
    
    def test_list_expressions_filter_by_community(self, client, auth_headers, test_community, db_session):
        """Test GET /api/expressions filters by community_id."""
        # Create another community
        community2 = ProblemCommunity(
            name="Another Community",
            description="Another test community",
            stress_source="Family",
            is_active=True
        )
        db_session.add(community2)
        db_session.commit()
        db_session.refresh(community2)
        
        # Create expressions in different communities
        client.post(
            "/api/expressions",
            headers=auth_headers,
            json={"content": "Expression in community 1", "community_id": test_community.id}
        )
        client.post(
            "/api/expressions",
            headers=auth_headers,
            json={"content": "Expression in community 2", "community_id": community2.id}
        )
        client.post(
            "/api/expressions",
            headers=auth_headers,
            json={"content": "Expression without community"}
        )
        
        # Filter by first community
        response = client.get(
            f"/api/expressions?community_id={test_community.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["content"] == "Expression in community 1"
        assert data["items"][0]["community_id"] == test_community.id


class TestEmpathyResponses:
    """Test empathy response endpoints (Task 6)."""
    
    @pytest.fixture
    def test_expression(self, client, auth_headers):
        """Create a test expression for empathy responses."""
        response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={"content": "Feeling stressed about finals"}
        )
        return response.json()
    
    def test_add_empathy_response_success(self, client, auth_headers, test_expression):
        """Test POST /api/expressions/{id}/empathy creates empathy response."""
        response = client.post(
            f"/api/expressions/{test_expression['id']}/empathy",
            headers=auth_headers,
            json={
                "content": "You're not alone! We've all been there.",
                "is_anonymous": True
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["expression_id"] == test_expression["id"]
        assert data["content"] == "You're not alone! We've all been there."
        assert data["is_anonymous"] is True
        assert "id" in data
        assert "created_at" in data
    
    def test_add_empathy_response_not_found(self, client, auth_headers):
        """Test POST /api/expressions/{id}/empathy returns 404 for invalid expression."""
        response = client.post(
            "/api/expressions/99999/empathy",
            headers=auth_headers,
            json={"content": "Test response"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Expression not found" in response.json()["detail"]
    
    def test_add_empathy_response_280_char_limit(self, client, auth_headers, test_expression):
        """Test POST /api/expressions/{id}/empathy enforces 280 character limit."""
        # Try with 281 characters
        content_281 = "a" * 281
        
        response = client.post(
            f"/api/expressions/{test_expression['id']}/empathy",
            headers=auth_headers,
            json={"content": content_281}
        )
        
        # Pydantic validation happens before endpoint code, so we get 422 (Unprocessable Entity)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_add_empathy_response_safety_gate_blocks(self, client, auth_headers, test_expression):
        """Test POST /api/expressions/{id}/empathy blocks high-risk content."""
        response = client.post(
            f"/api/expressions/{test_expression['id']}/empathy",
            headers=auth_headers,
            json={"content": "I want to end my life"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "high-risk content" in response.json()["detail"].lower()
    
    def test_add_empathy_response_awards_hearts(self, client, auth_headers, test_expression, db_session):
        """Test POST /api/expressions/{id}/empathy awards hearts to responder."""
        # Get initial hearts balance
        hearts_response = client.get("/api/hearts/balance", headers=auth_headers)
        initial_balance = hearts_response.json()["total_earned"]
        
        # Add empathy response
        response = client.post(
            f"/api/expressions/{test_expression['id']}/empathy",
            headers=auth_headers,
            json={"content": "Sending you support!"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check hearts increased
        hearts_response = client.get("/api/hearts/balance", headers=auth_headers)
        new_balance = hearts_response.json()["total_earned"]
        assert new_balance == initial_balance + 3  # HEARTS_FOR_EMPATHY
    
    def test_multiple_empathy_responses(self, client, auth_headers, test_expression):
        """Test multiple empathy responses can be added to same expression."""
        # Add first response
        response1 = client.post(
            f"/api/expressions/{test_expression['id']}/empathy",
            headers=auth_headers,
            json={"content": "First response"}
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Add second response
        response2 = client.post(
            f"/api/expressions/{test_expression['id']}/empathy",
            headers=auth_headers,
            json={"content": "Second response"}
        )
        assert response2.status_code == status.HTTP_201_CREATED
        
        # Both should have different IDs
        assert response1.json()["id"] != response2.json()["id"]


class TestExpressionsAuthentication:
    """Test authentication requirements for expressions endpoints."""
    
    def test_create_expression_requires_auth(self, client):
        """Test POST /api/expressions requires authentication."""
        response = client.post(
            "/api/expressions",
            json={"content": "Test expression"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_expressions_requires_auth(self, client):
        """Test GET /api/expressions requires authentication."""
        response = client.get("/api/expressions")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_add_empathy_response_requires_auth(self, client):
        """Test POST /api/expressions/{id}/empathy requires authentication."""
        response = client.post(
            "/api/expressions/1/empathy",
            json={"content": "Test response"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestExpressionsIntegration:
    """Integration tests for expressions feature."""
    
    def test_full_flow(self, client, auth_headers, test_community):
        """Test complete flow: create expression, list, add empathy."""
        # 1. Create expression
        create_response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={
                "content": "Having a tough day",
                "community_id": test_community.id,
                "is_anonymous": True
            }
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        expression_id = create_response.json()["id"]
        
        # 2. List expressions (should include the one we just created)
        list_response = client.get("/api/expressions", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        assert list_response.json()["total"] >= 1
        
        # 3. Add empathy response
        empathy_response = client.post(
            f"/api/expressions/{expression_id}/empathy",
            headers=auth_headers,
            json={"content": "Hang in there! You've got this."}
        )
        assert empathy_response.status_code == status.HTTP_201_CREATED
        
        # 4. Verify hearts were awarded for both actions
        hearts_response = client.get("/api/hearts/balance", headers=auth_headers)
        hearts_data = hearts_response.json()
        # Should have earned at least 8 hearts (5 for expression + 3 for empathy)
        assert hearts_data["total_earned"] >= 8
    
    def test_expressions_respect_anonymity(self, client, auth_headers):
        """Test that expressions respect is_anonymous flag."""
        # Create anonymous expression
        response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={
                "content": "Anonymous expression",
                "is_anonymous": True
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["is_anonymous"] is True
        
        # Create non-anonymous expression
        response = client.post(
            "/api/expressions",
            headers=auth_headers,
            json={
                "content": "Identified expression",
                "is_anonymous": False
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["is_anonymous"] is False
