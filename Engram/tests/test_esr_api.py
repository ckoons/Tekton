#!/usr/bin/env python3
"""
Test ESR HTTP API.

Tests the ESR HTTP API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestESRAPI:
    """Test ESR HTTP API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        # Import here to avoid import errors
        from engram.api.server import app
        return TestClient(app)
    
    @pytest.fixture
    def mock_esr_tools(self):
        """Mock ESR tools."""
        with patch('engram.api.controllers.esr.esr_store_thought') as mock_store:
            with patch('engram.api.controllers.esr.esr_recall_thought') as mock_recall:
                with patch('engram.api.controllers.esr.esr_search_similar') as mock_search:
                    with patch('engram.api.controllers.esr.esr_build_context') as mock_context:
                        with patch('engram.api.controllers.esr.esr_create_association') as mock_assoc:
                            with patch('engram.api.controllers.esr.esr_get_metabolism_status') as mock_metab:
                                with patch('engram.api.controllers.esr.esr_trigger_reflection') as mock_reflect:
                                    with patch('engram.api.controllers.esr.esr_get_namespaces') as mock_ns:
                                        yield {
                                            'store': mock_store,
                                            'recall': mock_recall,
                                            'search': mock_search,
                                            'context': mock_context,
                                            'associate': mock_assoc,
                                            'metabolism': mock_metab,
                                            'reflect': mock_reflect,
                                            'namespaces': mock_ns
                                        }
    
    def test_esr_status(self, client):
        """Test ESR status endpoint."""
        response = client.get("/api/esr/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["available", "unavailable"]
        assert "timestamp" in data
        assert "endpoints" in data
        assert len(data["endpoints"]) == 8
    
    @pytest.mark.asyncio
    async def test_store_thought(self, client, mock_esr_tools):
        """Test storing a thought."""
        # Mock the tool response
        mock_esr_tools['store'].return_value = {
            "status": "success",
            "memory_id": "test_memory_123",
            "timestamp": datetime.now().isoformat()
        }
        
        # Make request
        response = client.post("/api/esr/store", json={
            "content": "Test thought",
            "thought_type": "IDEA",
            "context": {"test": True},
            "confidence": 0.95,
            "ci_id": "apollo"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["memory_id"] == "test_memory_123"
    
    @pytest.mark.asyncio
    async def test_recall_thought(self, client, mock_esr_tools):
        """Test recalling a thought."""
        # Mock the tool response
        mock_esr_tools['recall'].return_value = {
            "status": "success",
            "memory": {
                "content": "Recalled thought",
                "type": "MEMORY",
                "confidence": 0.8
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Make request
        response = client.get("/api/esr/recall/memory_123?ci_id=apollo")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["memory"]["content"] == "Recalled thought"
    
    @pytest.mark.asyncio
    async def test_recall_not_found(self, client, mock_esr_tools):
        """Test recalling non-existent thought."""
        # Mock the tool response
        mock_esr_tools['recall'].return_value = {
            "status": "not_found",
            "memory_id": "nonexistent"
        }
        
        # Make request
        response = client.get("/api/esr/recall/nonexistent?ci_id=apollo")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_search_similar(self, client, mock_esr_tools):
        """Test searching for similar thoughts."""
        # Mock the tool response
        mock_esr_tools['search'].return_value = {
            "status": "success",
            "results": [
                {"content": "Result 1", "confidence": 0.9},
                {"content": "Result 2", "confidence": 0.8}
            ],
            "count": 2,
            "timestamp": datetime.now().isoformat()
        }
        
        # Make request
        response = client.post("/api/esr/search", json={
            "query": "test query",
            "limit": 10,
            "thought_type": "MEMORY",
            "min_confidence": 0.7,
            "ci_id": "apollo"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["count"] == 2
        assert len(data["results"]) == 2
    
    @pytest.mark.asyncio
    async def test_build_context(self, client, mock_esr_tools):
        """Test building context."""
        # Mock the tool response
        mock_esr_tools['context'].return_value = {
            "status": "success",
            "context": {
                "primary": ["thought1", "thought2"],
                "associated": ["related1"]
            },
            "topic": "test topic",
            "depth": 3,
            "timestamp": datetime.now().isoformat()
        }
        
        # Make request
        response = client.post("/api/esr/context", json={
            "topic": "test topic",
            "depth": 3,
            "max_items": 20,
            "ci_id": "apollo"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "primary" in data["context"]
        assert len(data["context"]["primary"]) == 2
    
    @pytest.mark.asyncio
    async def test_create_association(self, client, mock_esr_tools):
        """Test creating association."""
        # Mock the tool response
        mock_esr_tools['associate'].return_value = {
            "status": "success",
            "from_memory": "memory1",
            "to_memory": "memory2",
            "association_type": "related",
            "timestamp": datetime.now().isoformat()
        }
        
        # Make request
        response = client.post("/api/esr/associate", json={
            "from_memory": "memory1",
            "to_memory": "memory2",
            "association_type": "related",
            "strength": 0.8,
            "ci_id": "apollo"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["from_memory"] == "memory1"
        assert data["to_memory"] == "memory2"
    
    @pytest.mark.asyncio
    async def test_get_metabolism_status(self, client, mock_esr_tools):
        """Test getting metabolism status."""
        # Mock the tool response
        mock_esr_tools['metabolism'].return_value = {
            "status": "success",
            "metabolism": {
                "total_memories": 100,
                "promoted": 20,
                "forgotten": 5
            },
            "ci_id": "apollo",
            "timestamp": datetime.now().isoformat()
        }
        
        # Make request
        response = client.get("/api/esr/metabolism/status?ci_id=apollo")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["metabolism"]["total_memories"] == 100
    
    @pytest.mark.asyncio
    async def test_trigger_reflection(self, client, mock_esr_tools):
        """Test triggering reflection."""
        # Mock the tool response
        mock_esr_tools['reflect'].return_value = {
            "status": "success",
            "action": "reflection_triggered",
            "ci_id": "apollo",
            "reason": "test",
            "timestamp": datetime.now().isoformat()
        }
        
        # Make request
        response = client.post("/api/esr/reflect", json={
            "ci_id": "apollo",
            "reason": "test"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["action"] == "reflection_triggered"
    
    @pytest.mark.asyncio
    async def test_get_namespaces(self, client, mock_esr_tools):
        """Test getting namespaces."""
        # Mock the tool response
        mock_esr_tools['namespaces'].return_value = {
            "status": "success",
            "namespaces": ["apollo", "athena", "rhetor"],
            "count": 3,
            "timestamp": datetime.now().isoformat()
        }
        
        # Make request
        response = client.get("/api/esr/namespaces")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["count"] == 3
        assert "apollo" in data["namespaces"]
    
    def test_error_handling(self, client, mock_esr_tools):
        """Test API error handling."""
        # Mock an error
        mock_esr_tools['store'].return_value = {
            "status": "error",
            "error": "Test error message"
        }
        
        # Make request
        response = client.post("/api/esr/store", json={
            "content": "Test",
            "ci_id": "apollo"
        })
        
        assert response.status_code == 500
        assert "Test error" in response.json()["detail"]
    
    def test_validation_error(self, client):
        """Test request validation."""
        # Missing required field
        response = client.post("/api/esr/store", json={
            "thought_type": "IDEA"
            # Missing 'content' field
        })
        
        assert response.status_code == 422  # Validation error
        errors = response.json()["detail"]
        assert any("content" in str(error) for error in errors)
    
    def test_esr_unavailable(self, client):
        """Test when ESR is not available."""
        with patch('engram.api.controllers.esr.ESR_AVAILABLE', False):
            response = client.post("/api/esr/store", json={
                "content": "Test",
                "ci_id": "apollo"
            })
            
            assert response.status_code == 503
            assert "not available" in response.json()["detail"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])