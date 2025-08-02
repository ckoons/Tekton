#!/usr/bin/env python3
"""
Test aish MCP server CI tools endpoints.
"""

import os
import sys
import json
import asyncio
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
# Add path for registry imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    # Import app inside fixture to avoid module path conflicts
    from shared.aish.src.mcp.app import app
    return TestClient(app)


@pytest.fixture
def mock_tools_registry():
    """Mock CI tools registry."""
    mock_registry = Mock()
    mock_registry.get_tools.return_value = {
        'claude-code': {
            'display_name': 'Claude Code',
            'type': 'tool',
            'base_type': 'claude-code',
            'port': 8400,
            'description': 'Claude AI coding assistant',
            'executable': 'claude-code',
            'capabilities': {'code_generation': True, 'debugging': True},
            'defined_by': 'system'
        },
        'test-tool': {
            'display_name': 'Test Tool',
            'type': 'tool',
            'base_type': 'generic',
            'port': 8401,
            'description': 'User-defined test tool',
            'executable': '/usr/bin/test',
            'capabilities': {'testing': True},
            'defined_by': 'user'
        }
    }
    
    mock_registry.get_tool.side_effect = lambda name: mock_registry.get_tools().get(name)
    
    mock_registry.get_tool_status.side_effect = lambda name: {
        'name': name,
        'config': mock_registry.get_tools().get(name, {}),
        'running': name == 'claude-code',
        'pid': 12345 if name == 'claude-code' else None,
        'uptime': 3600.0 if name == 'claude-code' else 0
    }
    
    mock_registry.find_available_port.return_value = 8402
    mock_registry.register_tool.return_value = True
    mock_registry.unregister_tool.return_value = True
    
    return mock_registry


@pytest.fixture
def mock_tool_launcher():
    """Mock tool launcher."""
    mock_launcher = Mock()
    mock_launcher.launch_tool.return_value = True
    mock_launcher.terminate_tool.return_value = True
    
    # Mock adapter with status
    mock_adapter = Mock()
    mock_adapter.get_status.return_value = {
        'running': True,
        'pid': 12345,
        'session': 'test-session',
        'uptime': 3600.0
    }
    mock_adapter.tool_name = 'claude-code'
    
    mock_launcher.tools = {
        'claude-code': {
            'adapter': mock_adapter,
            'config': {
                'display_name': 'Claude Code',
                'base_type': 'claude-code'
            }
        }
    }
    
    mock_launcher.get_instance.return_value = mock_launcher
    
    return mock_launcher


class TestCIToolsEndpoints:
    """Test CI tools management endpoints."""
    
    def test_list_ci_tools(self, client, mock_tools_registry):
        """Test listing CI tools."""
        with patch('shared.ci_tools.get_registry') as mock_get:
            mock_get.return_value = mock_tools_registry
            
            response = client.get("/api/mcp/v2/tools/ci-tools")
            assert response.status_code == 200
            
            data = response.json()
            assert 'tools' in data
            assert len(data['tools']) == 2
            
            # Check first tool
            tool = data['tools'][0]
            assert tool['name'] == 'claude-code'
            assert tool['description'] == 'Claude AI coding assistant'
            assert tool['status'] == 'running'
            assert tool['port'] == 8400
            assert 'code_generation' in tool['capabilities']
    
    def test_launch_ci_tool(self, client, mock_tools_registry, mock_tool_launcher):
        """Test launching a CI tool."""
        with patch('shared.ci_tools.get_registry') as mock_get_reg:
            with patch('shared.ci_tools.ToolLauncher') as mock_launcher_cls:
                mock_get_reg.return_value = mock_tools_registry
                mock_launcher_cls.get_instance.return_value = mock_tool_launcher
                
                response = client.post("/api/mcp/v2/tools/ci-tools/launch", json={
                    "tool_name": "claude-code",
                    "session_id": "test-session",
                    "instance_name": "test-instance"
                })
                
                assert response.status_code == 200
                data = response.json()
                assert data['success'] is True
                assert 'Successfully launched' in data['message']
                assert data['port'] == 8400
                
                # Verify launcher was called
                mock_tool_launcher.launch_tool.assert_called_once_with(
                    'claude-code', 'test-session', 'test-instance'
                )
    
    def test_terminate_ci_tool(self, client, mock_tool_launcher):
        """Test terminating a CI tool."""
        with patch('shared.ci_tools.ToolLauncher') as mock_launcher_cls:
            mock_launcher_cls.get_instance.return_value = mock_tool_launcher
            
            response = client.post("/api/mcp/v2/tools/ci-tools/terminate", json={
                "tool_name": "claude-code"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'Successfully terminated' in data['message']
            
            mock_tool_launcher.terminate_tool.assert_called_once_with('claude-code')
    
    def test_get_ci_tool_status(self, client, mock_tools_registry):
        """Test getting CI tool status."""
        with patch('shared.ci_tools.get_registry') as mock_get:
            mock_get.return_value = mock_tools_registry
            
            response = client.get("/api/mcp/v2/tools/ci-tools/status/claude-code")
            assert response.status_code == 200
            
            data = response.json()
            assert data['name'] == 'claude-code'
            assert data['running'] is True
            assert data['pid'] == 12345
            assert data['uptime'] == 3600.0
    
    def test_list_ci_tool_instances(self, client, mock_tool_launcher):
        """Test listing CI tool instances."""
        with patch('shared.ci_tools.ToolLauncher') as mock_launcher_cls:
            mock_launcher_cls.get_instance.return_value = mock_tool_launcher
            
            response = client.get("/api/mcp/v2/tools/ci-tools/instances")
            assert response.status_code == 200
            
            data = response.json()
            assert 'instances' in data
            assert len(data['instances']) == 1
            
            instance = data['instances'][0]
            assert instance['name'] == 'claude-code'
            assert instance['tool_type'] == 'claude-code'
            assert instance['pid'] == 12345
            assert instance['running'] is True
    
    def test_define_ci_tool(self, client, mock_tools_registry):
        """Test defining a new CI tool."""
        with patch('shared.ci_tools.get_registry') as mock_get:
            mock_get.return_value = mock_tools_registry
            
            response = client.post("/api/mcp/v2/tools/ci-tools/define", json={
                "name": "new-tool",
                "type": "generic",
                "executable": "/usr/bin/newtool",
                "options": {
                    "description": "A new tool",
                    "capabilities": ["analysis", "generation"],
                    "port": "auto",
                    "health_check": "ping"
                }
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'Successfully defined' in data['message']
            assert data['port'] == 8402  # From mock
            
            # Verify register was called
            mock_tools_registry.register_tool.assert_called_once()
            call_args = mock_tools_registry.register_tool.call_args
            assert call_args[0][0] == 'new-tool'
            config = call_args[0][1]
            assert config['executable'] == '/usr/bin/newtool'
            assert config['base_type'] == 'generic'
    
    def test_undefine_ci_tool(self, client, mock_tools_registry):
        """Test undefining a CI tool."""
        with patch('shared.ci_tools.get_registry') as mock_get:
            mock_get.return_value = mock_tools_registry
            
            response = client.delete("/api/mcp/v2/tools/ci-tools/test-tool")
            assert response.status_code == 200
            
            data = response.json()
            assert data['success'] is True
            assert 'Successfully undefined' in data['message']
            
            mock_tools_registry.unregister_tool.assert_called_once_with('test-tool')
    
    def test_get_ci_tool_capabilities(self, client, mock_tools_registry):
        """Test getting CI tool capabilities."""
        with patch('shared.ci_tools.get_registry') as mock_get:
            mock_get.return_value = mock_tools_registry
            
            response = client.get("/api/mcp/v2/tools/ci-tools/capabilities/claude-code")
            assert response.status_code == 200
            
            data = response.json()
            assert data['name'] == 'claude-code'
            assert data['capabilities'] == {'code_generation': True, 'debugging': True}
            assert data['executable'] == 'claude-code'
            assert data['port'] == 8400


class TestContextStateEndpoints:
    """Test context state management endpoints."""
    
    @pytest.fixture
    def mock_ci_registry(self):
        """Mock CI registry with context state methods."""
        mock_registry = Mock()
        
        # Mock CIs
        mock_registry.exists.side_effect = lambda name: name in ['numa', 'apollo', 'claude-code']
        
        # Mock context state
        mock_registry.get_ci_context_state.side_effect = lambda name: {
            'last_output': f"Last output from {name}",
            'staged_prompt': [{"role": "system", "content": "Staged"}] if name == 'apollo' else None,
            'next_prompt': [{"role": "user", "content": "Next"}] if name == 'numa' else None
        } if name in ['numa', 'apollo'] else None
        
        mock_registry.get_all_context_states.return_value = {
            'numa': {
                'last_output': "Last output from numa",
                'next_prompt': [{"role": "user", "content": "Next"}]
            },
            'apollo': {
                'last_output': "Last output from apollo",
                'staged_prompt': [{"role": "system", "content": "Staged"}]
            }
        }
        
        mock_registry.update_ci_last_output.return_value = True
        mock_registry.set_ci_staged_context_prompt.return_value = True
        mock_registry.set_ci_next_context_prompt.return_value = True
        mock_registry.set_ci_next_from_staged.return_value = True
        
        return mock_registry
    
    def test_get_ci_context_state(self, client, mock_ci_registry):
        """Test getting context state for a CI."""
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            # Test CI with context
            response = client.get("/api/mcp/v2/tools/context-state/numa")
            assert response.status_code == 200
            
            data = response.json()
            assert data['ci_name'] == 'numa'
            assert data['last_output'] == "Last output from numa"
            assert data['next_prompt'] is not None
            assert data['staged_prompt'] is None
            
            # Test CI without context
            response = client.get("/api/mcp/v2/tools/context-state/claude-code")
            assert response.status_code == 200
            
            data = response.json()
            assert data['ci_name'] == 'claude-code'
            assert data['last_output'] is None
            
            # Test non-existent CI
            response = client.get("/api/mcp/v2/tools/context-state/unknown")
            assert response.status_code == 404
    
    def test_update_ci_context_state(self, client, mock_ci_registry):
        """Test updating context state for a CI."""
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            response = client.post("/api/mcp/v2/tools/context-state/numa", json={
                "last_output": "New output",
                "staged_prompt": [{"role": "system", "content": "New staged"}],
                "next_prompt": [{"role": "user", "content": "New next"}]
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'last_output' in data['message']
            assert 'staged_prompt' in data['message']
            assert 'next_prompt' in data['message']
            
            # Verify methods were called
            mock_ci_registry.update_ci_last_output.assert_called_with('numa', 'New output')
            mock_ci_registry.set_ci_staged_context_prompt.assert_called()
            mock_ci_registry.set_ci_next_context_prompt.assert_called()
    
    def test_get_all_context_states(self, client, mock_ci_registry):
        """Test getting all context states."""
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            response = client.get("/api/mcp/v2/tools/context-states")
            assert response.status_code == 200
            
            data = response.json()
            assert 'context_states' in data
            states = data['context_states']
            
            assert 'numa' in states
            assert 'apollo' in states
            assert states['numa']['last_output'] == "Last output from numa"
            assert states['apollo']['staged_prompt'] is not None
    
    def test_promote_staged_context(self, client, mock_ci_registry):
        """Test promoting staged context to next prompt."""
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            response = client.post("/api/mcp/v2/tools/context-state/apollo/promote-staged")
            assert response.status_code == 200
            
            data = response.json()
            assert data['success'] is True
            assert 'Promoted staged context' in data['message']
            
            mock_ci_registry.set_ci_next_from_staged.assert_called_once_with('apollo')


class TestCIInformationEndpoints:
    """Test detailed CI information endpoints."""
    
    @pytest.fixture
    def mock_ci_registry(self):
        """Mock CI registry with CI information."""
        mock_registry = Mock()
        
        mock_registry.get_by_name.side_effect = lambda name: {
            'name': name,
            'type': 'greek' if name in ['numa', 'apollo'] else 'tool',
            'endpoint': f'http://localhost:8{200 + hash(name) % 100}',
            'description': f'{name} CI',
            'message_format': 'rhetor_socket' if name in ['numa', 'apollo'] else 'json_simple'
        } if name in ['numa', 'apollo', 'claude-code'] else None
        
        mock_registry.get_types.return_value = ['greek', 'terminal', 'project', 'tool']
        
        mock_registry.get_by_type.side_effect = lambda t: [
            {'name': 'numa', 'type': 'greek'},
            {'name': 'apollo', 'type': 'greek'}
        ] if t == 'greek' else [
            {'name': 'claude-code', 'type': 'tool'}
        ] if t == 'tool' else []
        
        mock_registry.exists.side_effect = lambda name: name in ['numa', 'apollo', 'claude-code']
        
        return mock_registry
    
    def test_get_ci_details(self, client, mock_ci_registry):
        """Test getting CI details."""
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            response = client.get("/api/mcp/v2/tools/ci/numa")
            assert response.status_code == 200
            
            data = response.json()
            assert data['name'] == 'numa'
            assert data['type'] == 'greek'
            assert data['message_format'] == 'rhetor_socket'
            
            # Test non-existent CI
            response = client.get("/api/mcp/v2/tools/ci/unknown")
            assert response.status_code == 404
    
    def test_get_ci_types(self, client, mock_ci_registry):
        """Test getting CI types."""
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            response = client.get("/api/mcp/v2/tools/ci-types")
            assert response.status_code == 200
            
            data = response.json()
            assert 'types' in data
            assert set(data['types']) == {'greek', 'terminal', 'project', 'tool'}
    
    def test_get_cis_by_type(self, client, mock_ci_registry):
        """Test getting CIs by type."""
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            # Get Greek CIs
            response = client.get("/api/mcp/v2/tools/cis/type/greek")
            assert response.status_code == 200
            
            data = response.json()
            assert 'cis' in data
            assert len(data['cis']) == 2
            assert all(ci['type'] == 'greek' for ci in data['cis'])
            
            # Get tool CIs
            response = client.get("/api/mcp/v2/tools/cis/type/tool")
            assert response.status_code == 200
            
            data = response.json()
            assert len(data['cis']) == 1
            assert data['cis'][0]['name'] == 'claude-code'
    
    def test_check_ci_exists(self, client, mock_ci_registry):
        """Test checking if CI exists."""
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            # Existing CI
            response = client.get("/api/mcp/v2/tools/ci/numa/exists")
            assert response.status_code == 200
            assert response.json()['exists'] is True
            
            # Non-existent CI
            response = client.get("/api/mcp/v2/tools/ci/unknown/exists")
            assert response.status_code == 200
            assert response.json()['exists'] is False


class TestRegistryManagementEndpoints:
    """Test registry management endpoints."""
    
    @pytest.fixture
    def mock_ci_registry(self):
        """Mock CI registry with management methods."""
        mock_registry = Mock()
        
        # Mock get_all for counting (returns dict, not list)
        # Need to provide enough values for all calls in the reload endpoint
        mock_registry.get_all.side_effect = [
            # First call - before reload (for count)
            {
                'numa': {'name': 'numa', 'type': 'greek'},
                'apollo': {'name': 'apollo', 'type': 'greek'}
            },
            # Second call - after reload (for count)
            {
                'numa': {'name': 'numa', 'type': 'greek'},
                'apollo': {'name': 'apollo', 'type': 'greek'},
                'claude-code': {'name': 'claude-code', 'type': 'tool'},
                'alice': {'name': 'alice', 'type': 'terminal'}
            },
            # Third call - after reload (for getting all CIs)
            {
                'numa': {'name': 'numa', 'type': 'greek'},
                'apollo': {'name': 'apollo', 'type': 'greek'},
                'claude-code': {'name': 'claude-code', 'type': 'tool'},
                'alice': {'name': 'alice', 'type': 'terminal'}
            }
        ]
        
        # Mock reload behavior
        mock_registry.reload = Mock()
        mock_registry._save_context_state = Mock()
        
        # Mock registry file
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_registry._registry_file = mock_file
        
        return mock_registry
    
    def test_reload_registry(self, client, mock_ci_registry):
        """Test reloading CI registry."""
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            response = client.post("/api/mcp/v2/tools/registry/reload")
            assert response.status_code == 200
            
            data = response.json()
            assert data['success'] is True
            assert '2 → 4' in data['message']
            assert data['counts']['total'] == 4
            assert data['counts']['before'] == 2
            assert data['counts']['by_type']['greek'] == 2
            assert data['counts']['by_type']['tool'] == 1
            assert data['counts']['by_type']['terminal'] == 1
    
    def test_get_registry_status(self, client, mock_ci_registry):
        """Test getting registry status."""
        # Reset get_all side effect for this test
        mock_ci_registry.get_all.side_effect = None
        mock_ci_registry.get_all.return_value = {
            'numa': {'name': 'numa', 'type': 'greek'},
            'apollo': {'name': 'apollo', 'type': 'greek'},
            'claude-code': {'name': 'claude-code', 'type': 'tool'}
        }
        
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            response = client.get("/api/mcp/v2/tools/registry/status")
            assert response.status_code == 200
            
            data = response.json()
            assert data['status'] == 'active'
            assert data['counts']['total'] == 3
            assert data['counts']['by_type']['greek'] == 2
            assert data['counts']['by_type']['tool'] == 1
            # File exists check depends on mock setup, just verify it's a boolean
            assert isinstance(data['file_exists'], bool)
    
    def test_save_registry_state(self, client, mock_ci_registry):
        """Test saving registry state."""
        with patch('mcp.server.get_registry') as mock_get:
            mock_get.return_value = mock_ci_registry
            
            response = client.post("/api/mcp/v2/tools/registry/save")
            assert response.status_code == 200
            
            data = response.json()
            assert data['success'] is True
            assert 'successfully' in data['message']
            
            mock_ci_registry._save_context_state.assert_called_once()


class TestMCPCapabilities:
    """Test MCP capabilities endpoint reflects all functionality."""
    
    def test_capabilities_endpoint(self, client):
        """Test capabilities endpoint includes all tools."""
        response = client.get("/api/mcp/v2/capabilities")
        assert response.status_code == 200
        
        data = response.json()
        assert data['mcp_version'] == '1.0'
        assert data['server_name'] == 'aish'
        
        tools = data['capabilities']['tools']
        
        # Check CI tools are included
        assert 'list-ci-tools' in tools
        assert 'launch-ci-tool' in tools
        assert 'terminate-ci-tool' in tools
        assert 'define-ci-tool' in tools
        assert 'get-ci-tool-status' in tools
        
        # Check context state tools
        assert 'get-context-state' in tools
        assert 'update-context-state' in tools
        assert 'get-all-context-states' in tools
        assert 'promote-staged-context' in tools
        
        # Check CI information tools
        assert 'get-ci' in tools
        assert 'get-ci-types' in tools
        assert 'get-cis-by-type' in tools
        assert 'check-ci-exists' in tools
        
        # Check registry management
        assert 'reload-registry' in tools
        assert 'get-registry-status' in tools
        assert 'save-registry' in tools


if __name__ == "__main__":
    pytest.main([__file__, "-v"])