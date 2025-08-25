#!/usr/bin/env python3
"""
Test suite for aish MCP Server

Tests all MCP endpoints to ensure they work correctly.
"""

import json
import time
import pytest
import requests
from pathlib import Path
import sys
import os

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.env import TektonEnviron

# MCP server configuration
MCP_PORT = int(TektonEnviron.get('AISH_MCP_PORT', '8118'))
MCP_BASE_URL = f'http://localhost:{MCP_PORT}/api/mcp/v2'


class TestMCPServer:
    """Test suite for aish MCP server endpoints"""
    
    @classmethod
    def setup_class(cls):
        """Ensure MCP server is running"""
        try:
            response = requests.get(f'{MCP_BASE_URL}/health', timeout=2)
            if response.status_code != 200:
                pytest.skip("MCP server not running - start with 'aish'")
        except requests.exceptions.ConnectionError:
            pytest.skip("MCP server not running - start with 'aish'")
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = requests.get(f'{MCP_BASE_URL}/health')
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'aish-mcp'
        assert 'version' in data
        assert 'capabilities' in data
    
    def test_capabilities_endpoint(self):
        """Test the MCP discovery endpoint"""
        response = requests.get(f'{MCP_BASE_URL}/capabilities')
        assert response.status_code == 200
        
        data = response.json()
        assert data['mcp_version'] == '1.0'
        assert data['server_name'] == 'aish'
        assert 'capabilities' in data
        assert 'tools' in data['capabilities']
        
        # Check required tools are present
        tools = data['capabilities']['tools']
        required_tools = [
            'send-message', 'team-chat', 'forward', 
            'project-forward', 'list-ais', 'purpose',
            'terma-send', 'terma-broadcast', 'terma-inbox'
        ]
        for tool in required_tools:
            assert tool in tools, f"Missing tool: {tool}"
    
    def test_list_ais_endpoint(self):
        """Test listing available CIs"""
        response = requests.post(
            f'{MCP_BASE_URL}/tools/list-ais',
            json={}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'ais' in data
        assert isinstance(data['ais'], list)
        assert len(data['ais']) > 0
        
        # Check some expected CIs
        ai_names = [ai['name'] for ai in data['ais']]
        expected_ais = ['numa', 'apollo', 'athena', 'hermes']
        for ai in expected_ais:
            assert ai in ai_names, f"Missing AI: {ai}"
    
    def test_send_message_endpoint(self):
        """Test sending message to AI"""
        # Test with numa (should work)
        response = requests.post(
            f'{MCP_BASE_URL}/tools/send-message',
            json={
                'ai_name': 'numa',
                'message': 'Test message from MCP test suite'
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'response' in data
        assert isinstance(data['response'], str)
        assert len(data['response']) > 0
    
    def test_send_message_invalid_ai(self):
        """Test sending message to invalid AI"""
        response = requests.post(
            f'{MCP_BASE_URL}/tools/send-message',
            json={
                'ai_name': 'invalid-ai-name',
                'message': 'Test message'
            }
        )
        assert response.status_code == 500
        assert 'Unknown AI' in response.json()['detail']
    
    def test_send_message_missing_params(self):
        """Test send-message with missing parameters"""
        # Missing ai_name
        response = requests.post(
            f'{MCP_BASE_URL}/tools/send-message',
            json={'message': 'Test'}
        )
        assert response.status_code == 400
        
        # Missing message
        response = requests.post(
            f'{MCP_BASE_URL}/tools/send-message',
            json={'ai_name': 'numa'}
        )
        assert response.status_code == 400
    
    def test_team_chat_endpoint(self):
        """Test team chat broadcast"""
        response = requests.post(
            f'{MCP_BASE_URL}/tools/team-chat',
            json={'message': 'Test team chat from MCP test suite'}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'responses' in data
        assert isinstance(data['responses'], list)
        
        # Should have responses from multiple CIs
        if len(data['responses']) > 0:
            # Check response format
            for resp in data['responses']:
                assert 'specialist_id' in resp
                assert 'content' in resp
                assert 'socket_id' in resp
    
    def test_forward_list(self):
        """Test listing forwards"""
        response = requests.post(
            f'{MCP_BASE_URL}/tools/forward',
            json={'action': 'list'}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'forwards' in data
        assert isinstance(data['forwards'], dict)
    
    def test_forward_add_remove(self):
        """Test adding and removing a forward"""
        # Add forward
        response = requests.post(
            f'{MCP_BASE_URL}/tools/forward',
            json={
                'action': 'add',
                'ai_name': 'test-ai',
                'terminal': 'test-terminal'
            }
        )
        assert response.status_code == 200
        assert 'success' in response.json()['status']
        
        # Verify it was added
        response = requests.post(
            f'{MCP_BASE_URL}/tools/forward',
            json={'action': 'list'}
        )
        forwards = response.json()['forwards']
        assert 'test-ai' in forwards
        assert forwards['test-ai'] == 'test-terminal'
        
        # Remove forward
        response = requests.post(
            f'{MCP_BASE_URL}/tools/forward',
            json={
                'action': 'remove',
                'ai_name': 'test-ai'
            }
        )
        assert response.status_code == 200
        assert 'success' in response.json()['status']
        
        # Verify it was removed
        response = requests.post(
            f'{MCP_BASE_URL}/tools/forward',
            json={'action': 'list'}
        )
        forwards = response.json()['forwards']
        assert 'test-ai' not in forwards
    
    def test_project_forward_list(self):
        """Test project forward list"""
        response = requests.post(
            f'{MCP_BASE_URL}/tools/project-forward',
            json={'action': 'list'}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'projects' in data
        assert isinstance(data['projects'], list)
    
    def test_purpose_get(self):
        """Test getting terminal purpose"""
        response = requests.post(
            f'{MCP_BASE_URL}/tools/purpose',
            json={}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'terminal' in data
        assert 'purpose' in data
    
    def test_terma_inbox(self):
        """Test terminal inbox"""
        response = requests.get(f'{MCP_BASE_URL}/tools/terma-inbox')
        assert response.status_code == 200
        
        data = response.json()
        assert 'prompt' in data
        assert 'new' in data
        assert 'keep' in data
        assert isinstance(data['prompt'], list)
        assert isinstance(data['new'], list)
        assert isinstance(data['keep'], list)
    
    def test_streaming_response(self):
        """Test streaming response support"""
        response = requests.post(
            f'{MCP_BASE_URL}/tools/send-message',
            json={
                'ai_name': 'numa',
                'message': 'Test streaming',
                'stream': True
            },
            stream=True
        )
        assert response.status_code == 200
        assert response.headers.get('content-type').startswith('text/event-stream')
        
        # Read at least one chunk
        chunks_received = 0
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    chunks_received += 1
                    data = json.loads(line_str[6:])
                    assert 'done' in data
                    if data['done']:
                        break
        
        assert chunks_received > 0


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])