#!/usr/bin/env python3
"""
Simple workflow tests using TektonEnviron and tekton_url patterns.
No environment manipulation, just functional tests.
"""

import pytest
import json
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from shared.env import TektonEnviron
from shared.urls import tekton_url
from shared.workflow.workflow_handler import WorkflowHandler, WorkflowMessage


class TestTektonPatterns:
    """Test that workflow handler uses TektonEnviron and tekton_url correctly."""
    
    def test_tekton_environ_usage(self):
        """Test that we can read from TektonEnviron."""
        # Simply test that we can get values
        tekton_root = TektonEnviron.get('TEKTON_ROOT')
        assert tekton_root is not None
        
        # Test with default
        some_value = TektonEnviron.get('NONEXISTENT_KEY', 'default_value')
        assert some_value == 'default_value'
    
    def test_tekton_url_usage(self):
        """Test that we can construct URLs with tekton_url."""
        # Test basic URL construction
        url = tekton_url('telos', '/workflow')
        assert url.startswith('http://')
        assert '/workflow' in url
        
        # Test with different components
        hermes_url = tekton_url('hermes', '/api/v1/test')
        assert '/api/v1/test' in hermes_url
        
        # Test with explicit host
        custom_url = tekton_url('metis', '/test', host='custom.host')
        assert 'custom.host' in custom_url


class TestWorkflowHandler:
    """Simple functional tests for WorkflowHandler."""
    
    def test_workflow_message_creation(self):
        """Test creating a workflow message."""
        msg = WorkflowMessage(
            purpose={"telos": "create proposal"},
            dest="telos",
            payload={"action": "create", "name": "test"}
        )
        
        assert msg.purpose["telos"] == "create proposal"
        assert msg.dest == "telos"
        assert msg.payload["action"] == "create"
    
    def test_workflow_id_generation(self):
        """Test workflow ID generation."""
        handler = WorkflowHandler('test_component')
        
        # Test basic ID generation
        workflow_id = handler.generate_workflow_id("Test_Sprint")
        assert workflow_id.startswith("test_")  # Sprint suffix removed, lowercase
        assert len(workflow_id.split('_')) >= 5  # Has timestamp parts
    
    def test_prepare_data_payload(self):
        """Test data payload preparation."""
        handler = WorkflowHandler('test_component')
        
        # Test small data (embedded)
        small_data = {"test": "data", "count": 123}
        payload = handler.prepare_data_payload(small_data)
        assert payload["type"] == "embedded"
        assert payload["content"] == small_data
        
        # Test large data (reference)
        large_data = {"items": ["x" * 1000 for _ in range(20)]}
        payload = handler.prepare_data_payload(large_data)
        assert payload["type"] == "reference"
        assert "size_bytes" in payload
    
    def test_port_configuration(self):
        """Test that ports are loaded from TektonEnviron."""
        handler = WorkflowHandler('test_component')
        
        # Check that ports exist
        assert 'telos' in handler.ports
        assert 'hermes' in handler.ports
        
        # Verify they're integers
        assert isinstance(handler.ports['telos'], int)
        assert isinstance(handler.ports['hermes'], int)


class TestWorkflowIntegration:
    """Simple integration test for workflow system."""
    
    @pytest.mark.asyncio
    async def test_workflow_message_handling(self):
        """Test handling a complete workflow message."""
        # Create a simple handler
        class TestHandler(WorkflowHandler):
            async def look_for_work(self):
                return {"status": "success", "found": 2}
            
            async def process_sprint(self, payload):
                return {"status": "success", "processed": payload.get("sprint_name")}
        
        handler = TestHandler('test_component')
        
        # Test look_for_work
        message = WorkflowMessage(
            purpose={"test_component": "check for work"},
            dest="test_component",
            payload={"action": "look_for_work"}
        )
        
        result = await handler.handle_workflow(message)
        assert result["status"] == "success"
        assert result["found"] == 2
        
        # Test process_sprint
        message2 = WorkflowMessage(
            purpose={"test_component": "process sprint"},
            dest="test_component",
            payload={"action": "process_sprint", "sprint_name": "Test_Sprint"}
        )
        
        result2 = await handler.handle_workflow(message2)
        assert result2["status"] == "success"
        assert result2["processed"] == "Test_Sprint"
    
    @pytest.mark.asyncio
    async def test_workflow_with_temp_storage(self):
        """Test workflow with temporary file storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a handler that stores in temp directory
            class TempHandler(WorkflowHandler):
                def __init__(self, component_name):
                    super().__init__(component_name)
                    self.temp_dir = temp_dir
                
                def _get_workflow_dir(self):
                    # Override to use temp directory
                    return str(Path(temp_dir) / '.tekton' / 'workflows' / 'data')
                
                async def process_sprint(self, payload):
                    return {"status": "success"}
            
            handler = TempHandler('test_component')
            
            # Save some workflow data
            workflow_id = handler.generate_workflow_id("Test")
            data = {"test": "data", "value": 123}
            
            # Save and verify
            path = handler.save_workflow_data(workflow_id, data)
            assert Path(path).exists()
            
            # Load and verify
            loaded = handler.load_workflow_data(workflow_id)
            assert loaded["test"] == "data"
            assert loaded["value"] == 123
            assert "metadata" in loaded


def test_tekton_patterns_in_workflow():
    """Verify workflow handler uses TektonEnviron correctly."""
    # This test verifies the actual implementation
    handler = WorkflowHandler('test')
    
    # The handler should use TektonEnviron for ports
    # We can verify by checking the source
    import inspect
    source = inspect.getsource(handler._load_port_config)
    
    # Should use TektonEnviron.get, not os.getenv
    assert "TektonEnviron.get" in source
    assert "os.getenv" not in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])