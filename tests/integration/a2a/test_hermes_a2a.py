"""
Integration tests for Hermes A2A JSON-RPC endpoint
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, MagicMock
try:
    from fastapi.testclient import TestClient
except ImportError:
    from starlette.testclient import TestClient
from fastapi import FastAPI, Request

from tekton.a2a import AgentCard, AgentRegistry, TaskManager, DiscoveryService
from hermes.api.a2a_endpoints import a2a_router, get_a2a_service
from hermes.core.a2a_service import A2AService
from hermes.core.service_discovery import ServiceRegistry
from hermes.core.message_bus import MessageBus


@pytest.fixture
def mock_a2a_service():
    """Create a mock A2A service with real components"""
    # Create real components
    service_registry = ServiceRegistry()
    message_bus = MessageBus()
    
    # Create A2A service
    a2a_service = A2AService(
        service_registry=service_registry,
        message_bus=message_bus,
        registration_manager=None  # Optional parameter
    )
    
    return a2a_service


@pytest.fixture
def test_app(mock_a2a_service):
    """Create test FastAPI app with A2A endpoints"""
    app = FastAPI()
    
    # Add the A2A service to app state
    app.state.a2a_service = mock_a2a_service
    
    # Override the dependency
    app.dependency_overrides[get_a2a_service] = lambda: mock_a2a_service
    
    # Include the router
    app.include_router(a2a_router, prefix="/api")
    
    return app


@pytest.fixture
def client(test_app):
    """Create test client"""
    return TestClient(test_app)


class TestJSONRPCEndpoint:
    """Test the main JSON-RPC endpoint"""
    
    def test_valid_request(self, client):
        """Test a valid JSON-RPC request"""
        request = {
            "jsonrpc": "2.0",
            "method": "agent.list",
            "id": "test-123"
        }
        
        response = client.post("/api/a2a/v1/", json=request)
        
        assert response.status_code == 200
        result = response.json()
        assert result["jsonrpc"] == "2.0"
        assert result["id"] == "test-123"
        assert "result" in result
        # agent.list returns {"agents": []}
        assert isinstance(result["result"], dict)
        assert "agents" in result["result"]
        assert isinstance(result["result"]["agents"], list)
    
    def test_invalid_json(self, client):
        """Test invalid JSON request"""
        response = client.post(
            "/api/a2a/v1/",
            content="{invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == -32700  # Parse error
    
    def test_missing_method(self, client):
        """Test request missing method field"""
        request = {
            "jsonrpc": "2.0",
            "id": "test-123"
        }
        
        response = client.post("/api/a2a/v1/", json=request)
        
        assert response.status_code == 200
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == -32600  # Invalid request
    
    def test_method_not_found(self, client):
        """Test calling non-existent method"""
        request = {
            "jsonrpc": "2.0",
            "method": "nonexistent.method",
            "id": "test-123"
        }
        
        response = client.post("/api/a2a/v1/", json=request)
        
        assert response.status_code == 200
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == -32601  # Method not found
    
    def test_notification_request(self, client):
        """Test notification request (no id)"""
        request = {
            "jsonrpc": "2.0",
            "method": "agent.heartbeat",
            "params": {"agent_id": "test-agent"}
        }
        
        response = client.post("/api/a2a/v1/", json=request)
        
        # Notification should return 204 No Content
        assert response.status_code == 204
        assert response.text == ""
    
    def test_batch_request(self, client):
        """Test batch request"""
        requests = [
            {
                "jsonrpc": "2.0",
                "method": "agent.list",
                "id": 1
            },
            {
                "jsonrpc": "2.0",
                "method": "task.list",
                "id": 2
            }
        ]
        
        response = client.post("/api/a2a/v1/", json=requests)
        
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[1]["id"] == 2


class TestAgentMethods:
    """Test agent-related JSON-RPC methods"""
    
    def test_agent_register(self, client):
        """Test agent registration"""
        request = {
            "jsonrpc": "2.0",
            "method": "agent.register",
            "params": {
                "agent_card": {
                    "id": "test-agent-123",
                    "name": "Test Agent",
                    "description": "A test agent",
                    "version": "1.0.0",
                    "capabilities": ["test", "example"],
                    "supported_methods": ["test.method"],
                    "endpoint": "http://localhost:9000"
                }
            },
            "id": "reg-123"
        }
        
        response = client.post("/api/a2a/v1/", json=request)
        
        assert response.status_code == 200
        result = response.json()
        assert result["result"]["success"] is True
        assert result["result"]["agent_id"] == "test-agent-123"
    
    def test_agent_list(self, client):
        """Test listing agents"""
        # First register an agent
        register_request = {
            "jsonrpc": "2.0",
            "method": "agent.register",
            "params": {
                "agent_card": {
                    "id": "test-agent-456",
                    "name": "Test Agent",
                    "description": "A test agent",
                    "version": "1.0.0",
                    "capabilities": ["test"],
                    "supported_methods": ["test.method"]
                }
            },
            "id": 1
        }
        
        client.post("/api/a2a/v1/", json=register_request)
        
        # Now list agents
        list_request = {
            "jsonrpc": "2.0",
            "method": "agent.list",
            "id": 2
        }
        
        response = client.post("/api/a2a/v1/", json=list_request)
        
        assert response.status_code == 200
        result = response.json()
        # agent.list returns {"agents": [...]}
        agents_response = result["result"]
        assert isinstance(agents_response, dict)
        assert "agents" in agents_response
        agents = agents_response["agents"]
        assert isinstance(agents, list)
        assert len(agents) >= 1
        assert any(agent["id"] == "test-agent-456" for agent in agents)
    
    def test_agent_heartbeat(self, client):
        """Test agent heartbeat"""
        # Register an agent first
        register_request = {
            "jsonrpc": "2.0",
            "method": "agent.register",
            "params": {
                "agent_card": {
                    "id": "heartbeat-agent",
                    "name": "Heartbeat Agent",
                    "description": "Test heartbeat",
                    "version": "1.0.0",
                    "capabilities": ["test"],
                    "supported_methods": []
                }
            },
            "id": 1
        }
        
        client.post("/api/a2a/v1/", json=register_request)
        
        # Send heartbeat
        heartbeat_request = {
            "jsonrpc": "2.0",
            "method": "agent.heartbeat",
            "params": {"agent_id": "heartbeat-agent"},
            "id": 2
        }
        
        response = client.post("/api/a2a/v1/", json=heartbeat_request)
        
        assert response.status_code == 200
        result = response.json()
        assert result["result"]["success"] is True


class TestTaskMethods:
    """Test task-related JSON-RPC methods"""
    
    def test_task_create(self, client):
        """Test creating a task"""
        request = {
            "jsonrpc": "2.0",
            "method": "task.create",
            "params": {
                "name": "Test Task",
                "created_by": "test-agent",
                "description": "A test task",
                "input_data": {"key": "value"},
                "priority": "high"
            },
            "id": "task-create-123"
        }
        
        response = client.post("/api/a2a/v1/", json=request)
        
        assert response.status_code == 200
        result = response.json()
        # task.create returns {"task_id": "...", "task": {...}}
        task_response = result["result"]
        assert "task_id" in task_response
        assert "task" in task_response
        task = task_response["task"]
        assert task["name"] == "Test Task"
        assert task["created_by"] == "test-agent"
        assert task["state"] == "pending"
        assert "id" in task
    
    def test_task_lifecycle(self, client):
        """Test complete task lifecycle"""
        # Create task
        create_request = {
            "jsonrpc": "2.0",
            "method": "task.create",
            "params": {
                "name": "Lifecycle Task",
                "created_by": "test-agent"
            },
            "id": 1
        }
        
        response = client.post("/api/a2a/v1/", json=create_request)
        # Extract task_id from the response
        task_response = response.json()["result"]
        task_id = task_response["task"]["id"]
        
        # Update state to running
        update_request = {
            "jsonrpc": "2.0",
            "method": "task.update_state",
            "params": {
                "task_id": task_id,
                "state": "running",
                "message": "Starting task"
            },
            "id": 2
        }
        
        response = client.post("/api/a2a/v1/", json=update_request)
        assert response.json()["result"]["state"] == "running"
        
        # Update progress
        progress_request = {
            "jsonrpc": "2.0",
            "method": "task.update_progress",
            "params": {
                "task_id": task_id,
                "progress": 0.5,
                "message": "Halfway done"
            },
            "id": 3
        }
        
        response = client.post("/api/a2a/v1/", json=progress_request)
        assert response.json()["result"]["progress"] == 0.5
        
        # Complete task
        complete_request = {
            "jsonrpc": "2.0",
            "method": "task.complete",
            "params": {
                "task_id": task_id,
                "output_data": {"result": "success"},
                "message": "Task completed"
            },
            "id": 4
        }
        
        response = client.post("/api/a2a/v1/", json=complete_request)
        result = response.json()["result"]
        assert result["state"] == "completed"
        assert result["progress"] == 1.0
        assert result["output_data"] == {"result": "success"}


class TestDiscoveryMethods:
    """Test discovery-related JSON-RPC methods"""
    
    def test_discovery_query(self, client):
        """Test agent discovery query"""
        # Register some agents
        for i in range(3):
            request = {
                "jsonrpc": "2.0",
                "method": "agent.register",
                "params": {
                    "agent_card": {
                        "id": f"discovery-agent-{i}",
                        "name": f"Discovery Agent {i}",
                        "description": "Test agent",
                        "version": "1.0.0",
                        "capabilities": ["test", f"cap{i}"],
                        "supported_methods": ["test.method"],
                        "tags": ["test", f"tag{i}"]
                    }
                },
                "id": i
            }
            client.post("/api/a2a/v1/", json=request)
        
        # Query with filters
        query_request = {
            "jsonrpc": "2.0",
            "method": "discovery.query",
            "params": {
                "query": {
                    "capabilities": ["test"],
                    "limit": 10
                }
            },
            "id": "query-123"
        }
        
        response = client.post("/api/a2a/v1/", json=query_request)
        
        assert response.status_code == 200
        result = response.json()["result"]
        assert "agents" in result
        assert "total_count" in result
        assert len(result["agents"]) >= 3
    
    def test_discovery_capability_map(self, client):
        """Test getting capability map"""
        # Register agents with capabilities
        request = {
            "jsonrpc": "2.0",
            "method": "agent.register",
            "params": {
                "agent_card": {
                    "id": "cap-map-agent",
                    "name": "Capability Map Agent",
                    "description": "Test agent",
                    "version": "1.0.0",
                    "capabilities": ["cap1", "cap2", "cap3"],
                    "supported_methods": []
                }
            },
            "id": 1
        }
        client.post("/api/a2a/v1/", json=request)
        
        # Get capability map
        map_request = {
            "jsonrpc": "2.0",
            "method": "discovery.capability_map",
            "id": 2
        }
        
        response = client.post("/api/a2a/v1/", json=map_request)
        
        assert response.status_code == 200
        result = response.json()["result"]
        assert isinstance(result, dict)
        assert "cap1" in result
        assert "cap-map-agent" in result["cap1"]


class TestWellKnownEndpoint:
    """Test the well-known agent card endpoint"""
    
    def test_agent_card_endpoint(self, client):
        """Test getting Hermes's agent card"""
        response = client.get("/api/a2a/v1/.well-known/agent.json")
        
        assert response.status_code == 200
        agent_card = response.json()
        
        assert agent_card["name"] == "Hermes"
        assert agent_card["protocol_version"] == "0.2.1"
        assert "capabilities" in agent_card
        assert "supported_methods" in agent_card
        assert len(agent_card["supported_methods"]) > 0


class TestLegacyEndpoints:
    """Test legacy compatibility endpoints"""
    
    def test_legacy_register(self, client):
        """Test legacy registration endpoint"""
        agent_data = {
            "id": "legacy-agent",
            "name": "Legacy Agent",
            "description": "Test legacy registration",
            "version": "1.0.0",
            "capabilities": ["test"],
            "supported_methods": []
        }
        
        response = client.post("/api/a2a/v1/register", json=agent_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["agent_id"] == "legacy-agent"
    
    def test_legacy_list_agents(self, client):
        """Test legacy agent list endpoint"""
        response = client.get("/api/a2a/v1/agents")
        
        assert response.status_code == 200
        result = response.json()
        # Legacy endpoint might return different format
        if isinstance(result, dict) and "agents" in result:
            agents = result["agents"]
        else:
            agents = result
        assert isinstance(agents, list)