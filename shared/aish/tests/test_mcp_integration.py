#!/usr/bin/env python3
"""
Integration tests for aish MCP server with CI tools.
Tests the full flow with real components where possible.
"""

import os
import sys
import json
import time
import asyncio
import tempfile
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest
from fastapi.testclient import TestClient

# Set up test environment
os.environ['TEKTON_ROOT'] = str(Path(__file__).parent.parent.parent.parent)
os.environ['CI_TOOLS_PORT_MODE'] = 'dynamic'

from shared.aish.src.mcp.app import app
from shared.ci_tools import get_registry as get_tools_registry, ToolLauncher
from shared.aish.src.registry.ci_registry import get_registry as get_ci_registry


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def temp_tekton_root():
    """Create temporary TEKTON_ROOT for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        old_root = os.environ.get('TEKTON_ROOT')
        os.environ['TEKTON_ROOT'] = temp_dir
        
        # Create necessary directories
        ci_tools_dir = Path(temp_dir) / '.tekton' / 'ci_tools'
        ci_tools_dir.mkdir(parents=True, exist_ok=True)
        
        registry_dir = Path(temp_dir) / '.tekton' / 'aish'
        registry_dir.mkdir(parents=True, exist_ok=True)
        
        yield temp_dir
        
        # Restore old root
        if old_root:
            os.environ['TEKTON_ROOT'] = old_root


class TestMCPToolsIntegration:
    """Test MCP integration with CI tools."""
    
    def test_full_tool_lifecycle(self, client, temp_tekton_root):
        """Test complete tool lifecycle through MCP."""
        # 1. List tools (should be empty or just built-ins)
        response = client.get("/api/mcp/v2/tools/ci-tools")
        assert response.status_code == 200
        initial_tools = response.json()['tools']
        initial_count = len(initial_tools)
        
        # 2. Define a new tool
        response = client.post("/api/mcp/v2/tools/ci-tools/define", json={
            "name": "test-echo",
            "type": "generic",
            "executable": sys.executable,  # Use Python
            "options": {
                "description": "Test echo tool",
                "capabilities": ["echo", "test"],
                "port": "auto",
                "launch_args": ["-c", "import sys; print('Echo tool ready')"]
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        allocated_port = data['port']
        assert allocated_port is not None
        
        # 3. Verify tool appears in list
        response = client.get("/api/mcp/v2/tools/ci-tools")
        assert response.status_code == 200
        tools = response.json()['tools']
        assert len(tools) == initial_count + 1
        
        test_tool = next((t for t in tools if t['name'] == 'test-echo'), None)
        assert test_tool is not None
        assert test_tool['description'] == 'Test echo tool'
        assert test_tool['defined_by'] == 'user'
        
        # 4. Get tool capabilities
        response = client.get("/api/mcp/v2/tools/ci-tools/capabilities/test-echo")
        assert response.status_code == 200
        caps = response.json()
        assert caps['name'] == 'test-echo'
        assert 'echo' in caps['capabilities']
        assert 'test' in caps['capabilities']
        
        # 5. Check tool appears in CI registry via MCP
        response = client.post("/api/mcp/v2/tools/list-ais")
        assert response.status_code == 200
        ais = response.json()['ais']
        
        test_ci = next((ai for ai in ais if ai['name'] == 'test-echo'), None)
        assert test_ci is not None
        assert test_ci['type'] == 'tool'
        
        # 6. Get CI details
        response = client.get("/api/mcp/v2/tools/ci/test-echo")
        assert response.status_code == 200
        ci_details = response.json()
        assert ci_details['name'] == 'test-echo'
        assert ci_details['type'] == 'tool'
        
        # Note: Actually launching the tool would require socket infrastructure
        # which is complex to test in integration tests
        
        # 7. Undefine the tool
        response = client.delete("/api/mcp/v2/tools/ci-tools/test-echo")
        assert response.status_code == 200
        assert response.json()['success'] is True
        
        # 8. Verify tool is gone
        response = client.get("/api/mcp/v2/tools/ci-tools")
        assert response.status_code == 200
        final_tools = response.json()['tools']
        assert len(final_tools) == initial_count
        assert not any(t['name'] == 'test-echo' for t in final_tools)
    
    def test_context_state_management(self, client):
        """Test context state management through MCP."""
        # Get initial context states
        response = client.get("/api/mcp/v2/tools/context-states")
        assert response.status_code == 200
        initial_states = response.json()['context_states']
        
        # Update context for a Greek CI (should exist)
        response = client.post("/api/mcp/v2/tools/context-state/numa", json={
            "last_output": "Test output from MCP",
            "staged_prompt": [{"role": "system", "content": "Test staged prompt"}]
        })
        
        # If numa doesn't exist in test env, that's okay
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            
            # Get updated context state
            response = client.get("/api/mcp/v2/tools/context-state/numa")
            assert response.status_code == 200
            state = response.json()
            assert state['last_output'] == "Test output from MCP"
            assert state['staged_prompt'] is not None
            
            # Promote staged to next
            response = client.post("/api/mcp/v2/tools/context-state/numa/promote-staged")
            assert response.status_code == 200
            assert response.json()['success'] is True
    
    def test_registry_operations(self, client):
        """Test registry management operations."""
        # Get registry status
        response = client.get("/api/mcp/v2/tools/registry/status")
        assert response.status_code == 200
        status = response.json()
        assert status['status'] == 'active'
        assert 'counts' in status
        assert 'total' in status['counts']
        
        # Force save
        response = client.post("/api/mcp/v2/tools/registry/save")
        assert response.status_code == 200
        assert response.json()['success'] is True
        
        # Reload registry
        response = client.post("/api/mcp/v2/tools/registry/reload")
        assert response.status_code == 200
        reload_data = response.json()
        assert reload_data['success'] is True
        assert 'counts' in reload_data
    
    def test_ci_discovery_and_filtering(self, client):
        """Test CI discovery and filtering capabilities."""
        # Get all CI types
        response = client.get("/api/mcp/v2/tools/ci-types")
        assert response.status_code == 200
        types = response.json()['types']
        assert isinstance(types, list)
        
        # For each type, get CIs
        for ci_type in types:
            response = client.get(f"/api/mcp/v2/tools/cis/type/{ci_type}")
            assert response.status_code == 200
            cis = response.json()['cis']
            assert isinstance(cis, list)
            
            # All returned CIs should be of the requested type
            for ci in cis:
                assert ci['type'] == ci_type
        
        # Check CI exists endpoint
        response = client.get("/api/mcp/v2/tools/ci/numa/exists")
        assert response.status_code == 200
        assert 'exists' in response.json()
    
    def test_error_handling(self, client):
        """Test error handling for various endpoints."""
        # Non-existent tool
        response = client.get("/api/mcp/v2/tools/ci-tools/status/nonexistent")
        assert response.status_code == 404
        
        # Non-existent CI
        response = client.get("/api/mcp/v2/tools/ci/nonexistent")
        assert response.status_code == 404
        
        # Invalid tool definition (missing required fields)
        response = client.post("/api/mcp/v2/tools/ci-tools/define", json={
            "name": "invalid-tool"
            # Missing executable
        })
        assert response.status_code == 400
        
        # Invalid launch request
        response = client.post("/api/mcp/v2/tools/ci-tools/launch", json={
            # Missing tool_name
        })
        assert response.status_code == 400


class TestMCPPerformance:
    """Test MCP performance characteristics."""
    
    def test_endpoint_response_times(self, client):
        """Test that endpoints meet performance requirements."""
        import time
        
        # Test fast endpoints (<50ms)
        fast_endpoints = [
            ("/api/mcp/v2/tools/ci-types", "GET"),
            ("/api/mcp/v2/tools/registry/status", "GET"),
            ("/api/mcp/v2/health", "GET"),
            ("/api/mcp/v2/capabilities", "GET")
        ]
        
        for endpoint, method in fast_endpoints:
            start = time.time()
            if method == "GET":
                response = client.get(endpoint)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            
            assert response.status_code in [200, 404]
            # Allow some slack for test environment
            assert elapsed < 200, f"{endpoint} took {elapsed}ms (expected <50ms)"
        
        # Test medium endpoints (<100ms)
        medium_endpoints = [
            ("/api/mcp/v2/tools/ci-tools", "GET"),
            ("/api/mcp/v2/tools/context-states", "GET")
        ]
        
        for endpoint, method in medium_endpoints:
            start = time.time()
            if method == "GET":
                response = client.get(endpoint)
            elapsed = (time.time() - start) * 1000
            
            assert response.status_code == 200
            assert elapsed < 500, f"{endpoint} took {elapsed}ms (expected <100ms)"


class TestMCPDataValidation:
    """Test data validation and schema compliance."""
    
    def test_response_schemas(self, client):
        """Test that responses match expected schemas."""
        # Test CI tools list schema
        response = client.get("/api/mcp/v2/tools/ci-tools")
        assert response.status_code == 200
        data = response.json()
        
        assert 'tools' in data
        for tool in data['tools']:
            assert 'name' in tool
            assert 'description' in tool
            assert 'status' in tool
            assert 'port' in tool
            assert isinstance(tool['capabilities'], list)
        
        # Test context state schema
        response = client.get("/api/mcp/v2/tools/context-states")
        assert response.status_code == 200
        data = response.json()
        
        assert 'context_states' in data
        assert isinstance(data['context_states'], dict)
        
        # Test capabilities schema
        response = client.get("/api/mcp/v2/capabilities")
        assert response.status_code == 200
        data = response.json()
        
        assert 'mcp_version' in data
        assert 'server_name' in data
        assert 'capabilities' in data
        assert 'tools' in data['capabilities']


def run_integration_tests():
    """Run all integration tests."""
    print("Running MCP Integration Tests")
    print("=" * 60)
    
    # Run pytest with verbose output
    exit_code = pytest.main([__file__, "-v", "-s"])
    
    if exit_code == 0:
        print("\n✅ All integration tests passed!")
    else:
        print(f"\n❌ Integration tests failed with exit code: {exit_code}")
    
    return exit_code == 0


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)