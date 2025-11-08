import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestHealthEndpoints:
    def test_root_endpoint_returns_app_info(self):
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "InMind"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "docs_url" in data
    
    def test_health_endpoint_returns_healthy(self):
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "backend"
        assert "timestamp" in data
    
    def test_health_endpoint_includes_timestamp(self):
        response = client.get("/health")
        
        data = response.json()
        assert "timestamp" in data
        timestamp = data["timestamp"]
        assert isinstance(timestamp, str)
        assert len(timestamp) > 0
    
    def test_nonexistent_endpoint_returns_404(self):
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_invalid_method_returns_405(self):
        response = client.put("/health")
        
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data


class TestOllamaHealthEndpoints:
    def test_ollama_health_endpoint_structure(self):
        response = client.get("/health/ollama")
        
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "ollama_host" in data
        assert "timestamp" in data
    
    def test_ollama_health_includes_models_when_available(self):
        response = client.get("/health/ollama")
        
        data = response.json()
        if response.status_code == 200:
            assert data["status"] == "healthy"
            assert "available_models" in data
            assert isinstance(data["available_models"], list)
        else:
            assert data["status"] == "unhealthy"
            assert "error" in data