"""
Simple integration tests for Hermes A2A JSON-RPC endpoint

This version uses httpx directly to avoid TestClient compatibility issues.
"""

import pytest
import httpx
import json
import asyncio
from typing import Dict, Any

# Base URL for tests
BASE_URL = "http://localhost:8001"


def test_hermes_running():
    """Check if Hermes is running"""
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=2.0)
        assert response.status_code in [200, 404]  # 404 if no health endpoint
        print("✓ Hermes is reachable")
    except httpx.ConnectError:
        pytest.skip("Hermes is not running on port 8001")


def test_a2a_endpoint_exists():
    """Test that A2A endpoint exists"""
    response = httpx.post(f"{BASE_URL}/api/a2a/v1/", json={})
    # Should get JSON-RPC error, not 404
    assert response.status_code != 404
    print("✓ A2A endpoint exists")


def test_jsonrpc_agent_list():
    """Test agent.list method"""
    request = {
        "jsonrpc": "2.0",
        "method": "agent.list",
        "id": 1
    }
    
    response = httpx.post(f"{BASE_URL}/api/a2a/v1/", json=request)
    assert response.status_code == 200
    
    result = response.json()
    assert result["jsonrpc"] == "2.0"
    assert result["id"] == 1
    assert "result" in result
    assert isinstance(result["result"], dict)
    assert "agents" in result["result"]
    print(f"✓ agent.list works - found {len(result['result']['agents'])} agents")


def test_jsonrpc_error_handling():
    """Test JSON-RPC error handling"""
    request = {
        "jsonrpc": "2.0",
        "method": "invalid.method",
        "id": 2
    }
    
    response = httpx.post(f"{BASE_URL}/api/a2a/v1/", json=request)
    assert response.status_code == 200
    
    result = response.json()
    assert "error" in result
    assert result["error"]["code"] == -32601  # Method not found
    print("✓ Error handling works correctly")


def test_agent_registration():
    """Test agent registration"""
    # Register an agent
    request = {
        "jsonrpc": "2.0",
        "method": "agent.register",
        "params": {
            "agent_card": {
                "name": "Integration Test Agent",
                "description": "Test agent for integration tests",
                "version": "1.0.0",
                "capabilities": ["test", "integration"],
                "supported_methods": ["test.echo"]
            }
        },
        "id": 3
    }
    
    response = httpx.post(f"{BASE_URL}/api/a2a/v1/", json=request)
    assert response.status_code == 200
    
    result = response.json()
    assert "result" in result
    assert result["result"]["success"] is True
    agent_id = result["result"]["agent_id"]
    print(f"✓ Agent registered with ID: {agent_id}")
    
    # List agents to verify
    list_request = {
        "jsonrpc": "2.0",
        "method": "agent.list",
        "id": 4
    }
    
    response = httpx.post(f"{BASE_URL}/api/a2a/v1/", json=list_request)
    result = response.json()
    agents = result["result"]["agents"]
    assert any(agent["id"] == agent_id for agent in agents)
    print("✓ Agent appears in list")


def test_task_creation():
    """Test task creation"""
    request = {
        "jsonrpc": "2.0",
        "method": "task.create",
        "params": {
            "name": "Integration Test Task",
            "description": "Test task creation",
            "input_data": {"test": True}
        },
        "id": 5
    }
    
    response = httpx.post(f"{BASE_URL}/api/a2a/v1/", json=request)
    assert response.status_code == 200
    
    result = response.json()
    assert "result" in result
    assert "task_id" in result["result"]
    assert "task" in result["result"]
    
    task = result["result"]["task"]
    assert task["name"] == "Integration Test Task"
    assert task["state"] == "pending"
    print(f"✓ Task created with ID: {task['id']}")


def test_batch_request():
    """Test batch JSON-RPC request"""
    requests = [
        {
            "jsonrpc": "2.0",
            "method": "agent.list",
            "id": 6
        },
        {
            "jsonrpc": "2.0",
            "method": "discovery.capability_map",
            "id": 7
        }
    ]
    
    response = httpx.post(f"{BASE_URL}/api/a2a/v1/", json=requests)
    assert response.status_code == 200
    
    results = response.json()
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["id"] == 6
    assert results[1]["id"] == 7
    print("✓ Batch requests work correctly")


if __name__ == "__main__":
    # Run tests
    print("Running A2A Integration Tests...")
    print("=" * 50)
    
    try:
        test_hermes_running()
        test_a2a_endpoint_exists()
        test_jsonrpc_agent_list()
        test_jsonrpc_error_handling()
        test_agent_registration()
        test_task_creation()
        test_batch_request()
        
        print("\n✅ All integration tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise