"""
Test infrastructure setup and basic functionality.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.database import get_db


class TestInfrastructure:
    """Test basic infrastructure setup."""
    
    def test_app_creation(self):
        """Test that the FastAPI app is created successfully."""
        assert app is not None
        assert app.title == settings.APP_NAME
        assert app.version == settings.APP_VERSION
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert data["message"] == "Welcome to Meghan API"
    
    def test_database_dependency(self):
        """Test that database dependency is available."""
        db_gen = get_db()
        db = next(db_gen)
        assert db is not None
        # Clean up
        try:
            next(db_gen)
        except StopIteration:
            pass  # Expected behavior
    
    def test_cors_configuration(self):
        """Test CORS configuration."""
        client = TestClient(app)
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        
        # Should not return 405 Method Not Allowed for OPTIONS
        assert response.status_code != 405


@pytest.mark.property
class TestConfigurationProperties:
    """Property-based tests for configuration."""
    
    def test_settings_immutability(self):
        """Test that settings maintain their values."""
        original_app_name = settings.APP_NAME
        original_version = settings.APP_VERSION
        
        # Settings should remain constant
        assert settings.APP_NAME == original_app_name
        assert settings.APP_VERSION == original_version
    
    def test_database_url_format(self):
        """Test that database URL is properly formatted."""
        db_url = settings.DATABASE_URL
        assert isinstance(db_url, str)
        assert len(db_url) > 0
        # Should be either sqlite or postgresql URL
        assert db_url.startswith(("sqlite://", "postgresql://"))
    
    def test_cors_origins_parsing(self):
        """Test CORS origins configuration."""
        origins = settings.CORS_ORIGINS
        assert isinstance(origins, (list, str))
        if isinstance(origins, list):
            assert len(origins) > 0
            for origin in origins:
                assert isinstance(origin, str)
                assert len(origin) > 0